# -*- coding: utf-8 -*-
"""
更精确的 USC 分析：基于 AST 的合约级/函数级匹配。

- 按合约（ContractDefinition）粒度检测，避免多合约文件中误判。
- 在函数体（FunctionDefinition）内检测 delegatecall，避免注释或未使用代码干扰。
- 检测实现槽（0x3608...）是否出现在常量/字面量中，并与 delegatecall 同属一合约时提高置信度。
"""

from typing import Dict, Any, List, Optional, Set, Tuple

from . import patterns as P

# 实现槽 hex（用于精确匹配）
_IMPL_SLOT_NORM = P.EIP1967_IMPLEMENTATION_SLOT.lower().replace("0x", "")


def _norm_hex(val: str) -> str:
    v = (val or "").strip().lower()
    if v.startswith("0x"):
        v = v[2:]
    return v[:64]


def _is_implementation_slot(hex_val: str) -> bool:
    n = _norm_hex(hex_val)
    return n == _IMPL_SLOT_NORM or _IMPL_SLOT_NORM.endswith(n) or n.endswith(_IMPL_SLOT_NORM)


def _walk_contains_delegatecall(node: Dict) -> bool:
    """递归检查以 node 为根的子树是否包含 delegatecall（MemberAccess 或 assembly 内 Identifier）。"""
    if not isinstance(node, dict):
        return False
    node_type = node.get("nodeType")
    if node_type == "MemberAccess":
        if node.get("memberName") == "delegatecall":
            return True
    if node_type == "Identifier":
        if node.get("name") == "delegatecall":
            return True
    if node_type == "InlineAssembly":
        # Yul AST 可能在 "ast" 或 "operations"
        for key in ("ast", "operations"):
            if key in node and isinstance(node[key], dict):
                if _walk_contains_delegatecall(node[key]):
                    return True
            if key in node and isinstance(node[key], list):
                for item in node[key]:
                    if isinstance(item, dict) and _walk_contains_delegatecall(item):
                        return True
    for key, val in node.items():
        if key == "nodeType":
            continue
        if isinstance(val, dict) and _walk_contains_delegatecall(val):
            return True
        if isinstance(val, list):
            for item in val:
                if isinstance(item, dict) and _walk_contains_delegatecall(item):
                    return True
    return False


def _walk_collect_hex_literals(node: Dict, out: Set[str]) -> None:
    """递归收集 64 字符 hex 字面量（0x 开头）。"""
    if not isinstance(node, dict):
        return
    node_type = node.get("nodeType")
    if node_type == "Literal":
        val = node.get("value") or ""
        if isinstance(val, str) and val.strip().startswith("0x") and len(val.strip()) >= 66:
            out.add(val.strip()[:66])
        return
    for key, val in node.items():
        if key == "nodeType":
            continue
        if isinstance(val, dict):
            _walk_collect_hex_literals(val, out)
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    _walk_collect_hex_literals(item, out)


def _is_upgrade_function(name: str) -> bool:
    n = (name or "").strip().lower()
    return n in ("upgradeto", "upgradetoandcall", "_upgradeto", "_upgradetoandcall")


def _is_fallback_function(name: str) -> bool:
    n = (name or "").strip().lower()
    return n in ("_fallback", "_delegate", "fallback", "receive")


def _analyze_contract_node(contract: Dict) -> Dict[str, Any]:
    """
    分析一个 ContractDefinition 节点。
    返回: name, has_delegatecall, has_implementation_slot, has_upgrade_to, has_fallback, functions_with_delegatecall.
    """
    name = contract.get("name") or "Unknown"
    nodes = contract.get("nodes") or []
    hex_literals: Set[str] = set()
    functions_with_dc: List[str] = []
    has_upgrade_to = False
    has_fallback = False

    for member in nodes:
        if not isinstance(member, dict):
            continue
        node_type = member.get("nodeType")
        if node_type == "FunctionDefinition":
            fname = member.get("name") or ""
            if _is_upgrade_function(fname):
                has_upgrade_to = True
            if _is_fallback_function(fname):
                has_fallback = True
            body = member.get("body")
            if body and _walk_contains_delegatecall(body):
                functions_with_dc.append(fname)
            _walk_collect_hex_literals(member, hex_literals)
        elif node_type == "VariableDeclaration":
            _walk_collect_hex_literals(member, hex_literals)
        else:
            _walk_collect_hex_literals(member, hex_literals)

    has_impl_slot = any(_is_implementation_slot(h) for h in hex_literals)
    has_delegatecall = len(functions_with_dc) > 0

    return {
        "name": name,
        "has_delegatecall": has_delegatecall,
        "has_implementation_slot": has_impl_slot,
        "has_upgrade_to": has_upgrade_to,
        "has_fallback": has_fallback,
        "functions_with_delegatecall": functions_with_dc,
        "hex_literals_count": len(hex_literals),
    }


def _find_contract_definitions(node: Dict, out: List[Dict]) -> None:
    """递归收集所有 ContractDefinition 节点。"""
    if not isinstance(node, dict):
        return
    if node.get("nodeType") == "ContractDefinition":
        out.append(node)
    for key, val in node.items():
        if key == "nodeType":
            continue
        if isinstance(val, dict):
            _find_contract_definitions(val, out)
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    _find_contract_definitions(item, out)


def precise_ast_analysis(ast_dict: Dict) -> Dict[str, Any]:
    """
    对单文件 AST 做精确分析：按合约粒度提取特征。

    返回:
      contracts: 每个合约的 has_delegatecall, has_implementation_slot, has_upgrade_to, has_fallback, functions_with_delegatecall
      best_proxy: 最像代理的合约（用于分类）
      key_instruction_delegatecall, storage_implementation_slot, function_upgrade_to, function_fallback（聚合/最佳）
    """
    contracts_raw: List[Dict] = []
    _find_contract_definitions(ast_dict, contracts_raw)
    contracts = [_analyze_contract_node(c) for c in contracts_raw]

    # 聚合：任一合约具备即视为具备
    key_instruction_delegatecall = any(c["has_delegatecall"] for c in contracts)
    storage_implementation_slot = any(c["has_implementation_slot"] for c in contracts)
    function_upgrade_to = any(c["has_upgrade_to"] for c in contracts)
    function_fallback = any(c["has_fallback"] for c in contracts)

    # 选“最佳代理”合约：delegatecall + 实现槽 的合约；若有多个则选同时有 fallback 的
    best = None
    for c in contracts:
        if c["has_delegatecall"] and c["has_implementation_slot"]:
            if best is None:
                best = c
            elif c["has_fallback"] and not best.get("has_fallback"):
                best = c

    if best is None and contracts:
        # 退化为任一有 delegatecall 的合约
        for c in contracts:
            if c["has_delegatecall"]:
                best = c
                break

    return {
        "contracts": contracts,
        "best_proxy": best,
        "key_instruction_delegatecall": key_instruction_delegatecall,
        "storage_implementation_slot": storage_implementation_slot,
        "function_upgrade_to": function_upgrade_to,
        "function_fallback": function_fallback,
        "precision": "ast_contract_scoped",
    }

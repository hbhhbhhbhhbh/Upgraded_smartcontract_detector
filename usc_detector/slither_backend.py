# -*- coding: utf-8 -*-
"""
可选：基于 Slither 的深度分析，用于更高精度。

- 通过 CFG/IR 识别 delegatecall 调用点。
- 识别对 EIP-1967 实现槽的引用（常量/状态变量）。
需安装: pip install slither-analyzer，且系统 PATH 中有 solc。
"""

from typing import Dict, Any, List
from pathlib import Path

from . import patterns as P

_SLITHER_AVAILABLE = False
try:
    from slither import Slither
    _SLITHER_AVAILABLE = True
except Exception:
    pass


def is_available() -> bool:
    return _SLITHER_AVAILABLE


def analyze_file(file_path: str) -> Dict[str, Any]:
    """
    对单个 Solidity 文件运行 Slither，提取 delegatecall、存储槽相关特征。
    失败或未安装时返回 {}。
    """
    if not _SLITHER_AVAILABLE:
        return {}
    path = Path(file_path)
    if not path.is_file():
        return {}
    try:
        slither = Slither(str(path))
    except Exception:
        return {}

    out = {
        "precision": "slither",
        "key_instruction_delegatecall": False,
        "storage_implementation_slot": False,
        "function_upgrade_to": False,
        "function_fallback": False,
        "contracts": [],
        "delegatecall_in_functions": [],
    }
    impl_slot = P.EIP1967_IMPLEMENTATION_SLOT.lower().replace("0x", "")

    try:
        for contract in slither.contracts:
            c_info = {
                "name": getattr(contract, "name", "?"),
                "has_delegatecall": False,
                "has_implementation_slot_ref": False,
                "functions_with_delegatecall": [],
            }
            for func in getattr(contract, "functions", []):
                name = getattr(func, "name", "") or ""
                if name in ("upgradeTo", "upgradeToAndCall", "_upgradeTo", "_upgradeToAndCall"):
                    out["function_upgrade_to"] = True
                if name in ("_fallback", "_delegate", "fallback", "receive"):
                    out["function_fallback"] = True
                for node in getattr(func, "nodes", []):
                    for ir in getattr(node, "irs", []):
                        ir_type = getattr(ir, "type", None)
                        if ir_type and "DELEGATECALL" in str(ir_type).upper():
                            out["key_instruction_delegatecall"] = True
                            c_info["has_delegatecall"] = True
                            if name and name not in c_info["functions_with_delegatecall"]:
                                c_info["functions_with_delegatecall"].append(name)
                            break
                    if getattr(node, "low_level_calls", None):
                        for ll in node.low_level_calls:
                            if getattr(ll, "function_name", None) == "delegatecall":
                                out["key_instruction_delegatecall"] = True
                                c_info["has_delegatecall"] = True
                                if name and name not in c_info["functions_with_delegatecall"]:
                                    c_info["functions_with_delegatecall"].append(name)
                if c_info["functions_with_delegatecall"]:
                    out["delegatecall_in_functions"] = list(set(out["delegatecall_in_functions"] + c_info["functions_with_delegatecall"]))
            for var in list(getattr(contract, "state_variables", [])) + list(getattr(contract, "constants", [])):
                init = getattr(var, "initial_value", None)
                if init and impl_slot in str(init).lower():
                    out["storage_implementation_slot"] = True
                    c_info["has_implementation_slot_ref"] = True
            out["contracts"].append(c_info)
    except Exception:
        pass
    return out

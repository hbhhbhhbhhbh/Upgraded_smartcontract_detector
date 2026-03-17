# -*- coding: utf-8 -*-
"""
Rule-based classification for Upgradeable Smart Contracts (USC).

USC 分为四类：简单代理、透明代理、UUPS、插件/钻石模式 (Diamond/Beacon)。
依据三项代码特征：关键指令(delegatecall)、存储特征(0x3608...)、函数特征(upgradeTo/_fallback)。
"""

from typing import Dict, Any, Tuple, Optional

from . import patterns as P


def _confidence(strong: bool, mid: bool, weak: bool) -> float:
    if strong:
        return 0.92
    if mid:
        return 0.78
    if weak:
        return 0.58
    return 0.35


def classify(
    regex_result: Dict[str, Any],
    ast_result: Optional[Dict[str, Any]] = None,
) -> Tuple[str, float]:
    """
    将合约分类为四类 USC 之一，并返回置信度 [0, 1]。
    若 ast_result 含 precise（合约级 AST 分析），优先采用其特征并提高置信度。

    分类优先级：Diamond/Beacon > Transparent > UUPS > Simple Proxy > unknown。
    """
    ast_result = ast_result or {}
    precise = ast_result.get("precise") or {}
    ext = regex_result.get("pattern_extraction", {})

    # 优先使用精确分析（合约/函数级），否则回退到 regex + 简单 AST
    use_precise = bool(precise.get("precision") == "ast_contract_scoped")
    if use_precise:
        has_dc = precise.get("key_instruction_delegatecall", False)
        has_slot = precise.get("storage_implementation_slot", False)
        has_upgrade_to = precise.get("function_upgrade_to", False)
        has_fallback = precise.get("function_fallback", False)
    else:
        has_dc = regex_result.get("has_delegatecall", False) or ast_result.get("has_delegatecall_ast", False)
        has_slot = (
            regex_result.get("has_implementation_slot", False)
            or regex_result.get("has_eip1967", False)
            or ast_result.get("has_eip1967_slot_ast", False)
        )
        has_upgrade_to = ext.get("function_upgrade_to", False) or regex_result.get("has_upgrade_to", False)
        has_fallback = ext.get("function_fallback", False) or regex_result.get("has_fallback", False)

    transparent_hits = regex_result.get("transparent_hits", 0)
    uups_hits = regex_result.get("uups_hits", 0)
    beacon_hits = regex_result.get("beacon_hits", 0)
    diamond_hits = regex_result.get("diamond_hits", 0)

    # 1) 插件/钻石模式 (Diamond/Beacon)
    if diamond_hits > 0:
        return P.USC_DIAMOND_BEACON, _confidence(diamond_hits >= 2, diamond_hits >= 1, True)
    if beacon_hits > 0 and (has_dc or has_slot):
        return P.USC_DIAMOND_BEACON, _confidence(beacon_hits >= 2, True, True)

    # 2) 透明代理 (Transparent)：admin 槽或 TransparentUpgradeableProxy/ProxyAdmin
    if transparent_hits > 0 and has_dc:
        return P.USC_TRANSPARENT, _confidence(has_slot and transparent_hits >= 2, transparent_hits >= 1, True)

    # 3) UUPS：delegatecall + 实现槽 + upgradeTo/upgradeToAndCall 或 UUPSUpgradeable
    if (has_upgrade_to or uups_hits > 0) and has_dc:
        return P.USC_UUPS, _confidence(has_slot and (has_upgrade_to or uups_hits >= 2), has_slot or uups_hits >= 1, True)

    # 4) 简单代理 (Simple Proxy)：delegatecall + 实现槽(0x3608...)，无强 UUPS/Transparent/Diamond 标记
    if has_dc and has_slot:
        conf = _confidence(has_fallback, True, True)
        if use_precise and precise.get("best_proxy"):
            conf = min(0.96, conf + 0.04)  # 精确分析时略提高置信度
        return P.USC_SIMPLE_PROXY, conf

    # 仅有 delegatecall
    if has_dc:
        return P.PATTERN_TYPE_DELEGATECALL_ONLY, 0.48 if has_fallback else 0.4
    # 仅有实现槽
    if has_slot:
        return P.PATTERN_TYPE_EIP1967_SLOT_ONLY, 0.5
    if regex_result.get("proxy_naming_hits", 0) >= 2:
        return P.PATTERN_TYPE_GENERIC_UPGRADEABLE, 0.45

    return "unknown", 0.0

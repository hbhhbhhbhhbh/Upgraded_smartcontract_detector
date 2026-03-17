# -*- coding: utf-8 -*-
"""
Regex-based USC pattern detector.

Scans raw Solidity source for delegatecall, EIP-1967 slots, and proxy naming.
"""

import re
from typing import List, Tuple, Dict, Any

from . import patterns as P


def _compile_patterns() -> Dict[str, List[re.Pattern]]:
    out = {}
    out["delegatecall"] = [re.compile(pat, re.MULTILINE | re.DOTALL) for pat in P.DELEGATECALL_PATTERNS]
    out["eip1967_slot"] = [re.compile(P.REGEX_EIP1967_SLOT)]
    out["implementation_slot"] = [re.compile(P.REGEX_IMPLEMENTATION_SLOT)]  # 0x3608... 存放逻辑合约地址
    out["eip1967_naming"] = [re.compile(pat) for pat in P.EIP1967_NAMING_PATTERNS]
    out["proxy_naming"] = [re.compile(pat) for pat in P.PROXY_NAMING_PATTERNS]
    out["uups"] = [re.compile(pat) for pat in P.UUPS_PATTERNS]
    out["transparent"] = [re.compile(pat) for pat in P.TRANSPARENT_PATTERNS]
    out["beacon"] = [re.compile(pat) for pat in P.BEACON_PATTERNS]
    out["upgrade_to"] = [re.compile(pat) for pat in P.FUNCTION_UPGRADE_TO_PATTERNS]
    out["fallback"] = [re.compile(pat) for pat in P.FUNCTION_FALLBACK_PATTERNS]
    out["diamond"] = [re.compile(pat) for pat in P.DIAMOND_PATTERNS]
    return out


_COMPILED = _compile_patterns()


def has_delegatecall(source: str) -> bool:
    for pat in _COMPILED["delegatecall"]:
        if pat.search(source):
            return True
    return False


def has_eip1967_slot(source: str) -> bool:
    for pat in _COMPILED["eip1967_slot"]:
        if pat.search(source):
            return True
    return False


def has_eip1967_naming(source: str) -> bool:
    for pat in _COMPILED["eip1967_naming"]:
        if pat.search(source):
            return True
    return False


def has_eip1967(source: str) -> bool:
    """True if source contains EIP-1967 slot hex or standard naming."""
    return has_eip1967_slot(source) or has_eip1967_naming(source)


def get_proxy_naming_hits(source: str) -> int:
    n = 0
    for pat in _COMPILED["proxy_naming"]:
        n += len(pat.findall(source))
    return n


def get_uups_hits(source: str) -> int:
    n = 0
    for pat in _COMPILED["uups"]:
        n += len(pat.findall(source))
    return n


def get_transparent_hits(source: str) -> int:
    n = 0
    for pat in _COMPILED["transparent"]:
        n += len(pat.findall(source))
    return n


def get_beacon_hits(source: str) -> int:
    n = 0
    for pat in _COMPILED["beacon"]:
        n += len(pat.findall(source))
    return n


def has_implementation_slot(source: str) -> bool:
    """存储特征：是否使用 0x3608... 存放逻辑合约地址。"""
    for pat in _COMPILED["implementation_slot"]:
        if pat.search(source):
            return True
    return False


def has_upgrade_to(source: str) -> bool:
    """函数特征：是否存在 upgradeTo() / _upgradeTo() 等。"""
    for pat in _COMPILED["upgrade_to"]:
        if pat.search(source):
            return True
    return False


def has_fallback(source: str) -> bool:
    """函数特征：是否存在 _fallback() / _delegate() / fallback() external 等。"""
    for pat in _COMPILED["fallback"]:
        if pat.search(source):
            return True
    return False


def get_diamond_hits(source: str) -> int:
    n = 0
    for pat in _COMPILED["diamond"]:
        n += len(pat.findall(source))
    return n


def regex_scan(source: str) -> Dict[str, Any]:
    """
    Run all regex checks on Solidity source.
    Returns dict of flags, hit counts, and pattern_extraction (代码特征).
    """
    has_dc = has_delegatecall(source)
    has_slot = has_implementation_slot(source)
    has_eip = has_eip1967(source)
    has_up = has_upgrade_to(source)
    has_fb = has_fallback(source)
    return {
        "has_delegatecall": has_dc,
        "has_eip1967_slot": has_eip1967_slot(source),
        "has_implementation_slot": has_slot,
        "has_eip1967_naming": has_eip1967_naming(source),
        "has_eip1967": has_eip,
        "has_upgrade_to": has_up,
        "has_fallback": has_fb,
        "proxy_naming_hits": get_proxy_naming_hits(source),
        "uups_hits": get_uups_hits(source),
        "transparent_hits": get_transparent_hits(source),
        "beacon_hits": get_beacon_hits(source),
        "diamond_hits": get_diamond_hits(source),
        "pattern_extraction": {
            "key_instruction_delegatecall": has_dc,
            "storage_implementation_slot": has_slot,
            "function_upgrade_to": has_up,
            "function_fallback": has_fb,
        },
    }

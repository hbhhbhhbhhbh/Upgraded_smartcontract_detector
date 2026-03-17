# -*- coding: utf-8 -*-
"""
USC (Upgradeable Smart Contract) Code Patterns & EIP-1967 Constants.

Taxonomy / Pattern definitions for:
- EIP-1967 standard proxy storage slots
- delegatecall usage
- Proxy/Upgradeable naming and code signatures
"""

# ---------------------------------------------------------------------------
# EIP-1967 Standard Proxy Storage Slots (bytes32 hex)
# https://eips.ethereum.org/EIPS/eip-1967
# ---------------------------------------------------------------------------
EIP1967_IMPLEMENTATION_SLOT = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
EIP1967_ADMIN_SLOT = "0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103"
EIP1967_BEACON_SLOT = "0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50"
EIP1967_ROLLBACK_SLOT = "0x4910fdfa16fed3260ed0e7147f7cc6da11a60208b5b9406d12a635614ffd9143"

EIP1967_SLOTS = frozenset({
    EIP1967_IMPLEMENTATION_SLOT,
    EIP1967_ADMIN_SLOT,
    EIP1967_BEACON_SLOT,
    EIP1967_ROLLBACK_SLOT,
})

# Normalized (lowercase, no 0x prefix) for flexible matching
EIP1967_SLOTS_NORMALIZED = frozenset(
    s.lower().replace("0x", "") for s in EIP1967_SLOTS
)

# ---------------------------------------------------------------------------
# Regex patterns for source-level matching
# ---------------------------------------------------------------------------

# delegatecall in Solidity: .delegatecall( or delegatecall(
DELEGATECALL_PATTERNS = [
    r"\.delegatecall\s*\(",
    r"\bdelegatecall\s*\(",
    # Inline assembly
    r"delegatecall\s*\(\s*gas\s*",
    r"delegatecall\s*\(\s*[^)]+\)",
]

# EIP-1967 slot constants in source (hex literal, 64 hex chars)
EIP1967_SLOT_HEXES = [
    "360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc",
    "b53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103",
    "a3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50",
    "4910fdfa16fed3260ed0e7147f7cc6da11a60208b5b9406d12a635614ffd9143",
]
REGEX_EIP1967_SLOT = r"0x(" + "|".join(EIP1967_SLOT_HEXES) + ")"

# EIP-1967 naming in source (common constant names)
EIP1967_NAMING_PATTERNS = [
    r"_IMPLEMENTATION_SLOT\s*=",
    r"_ADMIN_SLOT\s*=",
    r"_BEACON_SLOT\s*=",
    r"_ROLLBACK_SLOT\s*=",
    r"IMPLEMENTATION_SLOT\s*=",
    r"eip1967\.proxy\.implementation",
    r"eip1967\.proxy\.admin",
    r"eip1967\.proxy\.beacon",
]

# Proxy/Upgradeable contract naming (for confidence boosting)
PROXY_NAMING_PATTERNS = [
    r"contract\s+\w*Proxy\w*\s*\{",
    r"contract\s+\w*Upgradeable\w*\s*\{",
    r"contract\s+ERC1967Proxy\s*\{",
    r"contract\s+ERC1967Upgrade\s*",
    r"abstract\s+contract\s+\w*Proxy\s*",
    r"_implementation\s*\(\s*\)\s*internal",
    r"_delegate\s*\(\s*address",
    r"function\s+_upgradeTo\s*\(",
    r"function\s+_upgradeToAndCall\s*\(",
    r"Upgraded\s*\(\s*address",
]

# UUPS: upgrade logic in implementation
UUPS_PATTERNS = [
    r"upgradeTo\s*\(",
    r"upgradeToAndCall\s*\(",
    r"UUPSUpgradeable",
    r"proxiableUUID",
]

# Transparent proxy (admin + implementation)
TRANSPARENT_PATTERNS = [
    r"TransparentUpgradeableProxy",
    r"ProxyAdmin",
    r"admin\s*\(\s*\)\s*.*returns\s*\(\s*address",
]

# Beacon proxy
BEACON_PATTERNS = [
    r"BeaconProxy",
    r"UpgradeableBeacon",
    r"_BEACON_SLOT",
    r"BeaconUpgraded\s*\(",
]

# ---------------------------------------------------------------------------
# 函数特征 (Function features): upgradeTo(), _fallback()
# ---------------------------------------------------------------------------
FUNCTION_UPGRADE_TO_PATTERNS = [
    r"function\s+upgradeTo\s*\(",
    r"function\s+upgradeToAndCall\s*\(",
    r"\bupgradeTo\s*\(",
    r"\bupgradeToAndCall\s*\(",
    r"_upgradeTo\s*\(",
    r"_upgradeToAndCall\s*\(",
]
FUNCTION_FALLBACK_PATTERNS = [
    r"function\s+_fallback\s*\(",
    r"function\s+_delegate\s*\(",
    r"fallback\s*\(\s*\)\s*external",
    r"receive\s*\(\s*\)\s*external",
    r"_fallback\s*\(",
    r"_delegate\s*\(",
]

# Diamond (EIP-2535) / 插件·钻石模式
DIAMOND_PATTERNS = [
    r"diamondCut\s*\(",
    r"facets\s*\(\s*\)",
    r"getFacet\s*\(",
    r"EIP2535",
    r"DiamondLoupe",
    r"IDiamondLoupe",
    r"LibDiamond",
    r"selector\s*=>\s*facet",
]

# Implementation slot only (0x3608... 存放逻辑合约地址)
IMPLEMENTATION_SLOT_HEX = "360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
REGEX_IMPLEMENTATION_SLOT = r"0x" + IMPLEMENTATION_SLOT_HEX

# ---------------------------------------------------------------------------
# USC 分类标签 (4 类)
# ---------------------------------------------------------------------------
USC_SIMPLE_PROXY = "simple_proxy"           # 简单代理
USC_TRANSPARENT = "transparent_proxy"        # 透明代理
USC_UUPS = "uups"                            # 通用可升级代理 (UUPS)
USC_DIAMOND_BEACON = "diamond_beacon"        # 插件/钻石模式 (Diamond/Beacon)

# 兼容旧输出的别名
PATTERN_TYPE_STANDARD_PROXY = "standard_proxy_eip1967"
PATTERN_TYPE_DELEGATECALL_ONLY = "delegatecall_only"
PATTERN_TYPE_EIP1967_SLOT_ONLY = "eip1967_slot_only"
PATTERN_TYPE_UUPS = USC_UUPS
PATTERN_TYPE_TRANSPARENT_PROXY = USC_TRANSPARENT
PATTERN_TYPE_BEACON_PROXY = "beacon_proxy"
PATTERN_TYPE_GENERIC_UPGRADEABLE = "generic_upgradeable"

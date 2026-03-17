# -*- coding: utf-8 -*-
"""
AST-based USC pattern detector.

Uses solc (via py-solc-x) + py-solc-ast (solcast) to parse Solidity to AST
and match delegatecall usage and EIP-1967 storage slot constants.
When solc is not available or parsing fails, returns empty findings (regex still runs).
"""

from typing import Dict, Any, List, Optional, Set
import json

from . import patterns as P

# Optional dependencies
try:
    import solcx
    HAS_SOLCX = True
except ImportError:
    HAS_SOLCX = False

try:
    import solcast
    HAS_SOLCAST = True
except ImportError:
    HAS_SOLCAST = False


def _ast_walk_visit(node, delegatecall_found: Set[str], eip1967_slot_found: Set[str], hex_literals: Set[str]) -> None:
    """Recursively walk AST (dict from solc JSON) to find delegatecall and EIP-1967 slots."""
    if not isinstance(node, dict):
        return
    node_type = node.get("nodeType")
    if node_type == "MemberAccess":
        member = node.get("memberName")
        if member == "delegatecall":
            delegatecall_found.add("MemberAccess.delegatecall")
        return
    if node_type == "Identifier":
        name = node.get("name")
        if name == "delegatecall":
            delegatecall_found.add("Identifier.delegatecall")
        return
    if node_type == "Literal":
        kind = node.get("kind", "")
        value = (node.get("value") or "").strip()
        if kind == "number" and value.startswith("0x") and len(value) >= 66:
            hex_literals.add(value[:66])
        elif isinstance(value, str) and value.startswith("0x") and len(value) >= 66:
            hex_literals.add(value[:66])
        return
    for key, val in node.items():
        if key == "nodeType":
            continue
        if isinstance(val, dict):
            _ast_walk_visit(val, delegatecall_found, eip1967_slot_found, hex_literals)
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    _ast_walk_visit(item, delegatecall_found, eip1967_slot_found, hex_literals)


def _ast_contains_eip1967(hex_literals: Set[str]) -> bool:
    normalized = {h.lower().replace("0x", "")[:64] for h in hex_literals}
    for slot in P.EIP1967_SLOTS:
        s = slot.lower().replace("0x", "")
        if s in normalized or any(n.endswith(s) or s.endswith(n) for n in normalized):
            return True
    for h in hex_literals:
        if h[2:].lower() in [s.replace("0x", "").lower() for s in P.EIP1967_SLOTS]:
            return True
    return False


def ast_scan_from_json(ast_dict: dict) -> Dict[str, Any]:
    """
    Scan a single source AST (solc output for one file) for delegatecall and EIP-1967.
    ast_dict: the "ast" object from solc standard output sources[path]["ast"].
    """
    delegatecall_found = set()
    eip1967_slot_found = set()
    hex_literals = set()
    _ast_walk_visit(ast_dict, delegatecall_found, eip1967_slot_found, hex_literals)
    has_eip1967 = _ast_contains_eip1967(hex_literals)
    return {
        "has_delegatecall_ast": len(delegatecall_found) > 0,
        "delegatecall_sources": list(delegatecall_found),
        "has_eip1967_slot_ast": has_eip1967,
        "hex_literals_count": len(hex_literals),
    }


def _get_precise_analysis(ast_dict: dict) -> Dict[str, Any]:
    """Run contract-scoped precise analysis on same AST. Requires precise_analyzer."""
    try:
        from .precise_analyzer import precise_ast_analysis
        return precise_ast_analysis(ast_dict)
    except Exception:
        return {}


def compile_and_ast_scan(
    source_path: str,
    source_code: Optional[str] = None,
    solc_version: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compile Solidity file with solc (via solcx) and run AST scan.
    Returns combined AST findings or empty dict on failure.
    """
    if not HAS_SOLCX or not HAS_SOLCAST:
        return {}
    try:
        if solc_version:
            solcx.install_solc(solc_version)
        if source_code is None:
            with open(source_path, "r", encoding="utf-8", errors="replace") as f:
                source_code = f.read()
        input_json = {
            "language": "Solidity",
            "sources": {source_path: {"content": source_code}},
            "settings": {
                "outputSelection": {"*": {"*": ["ast"]}},
                "optimizer": {"enabled": False},
            },
        }
        out = solcx.compile_standard(input_json, allow_paths=[".", source_path])
        if not out or "sources" not in out:
            return {}
        src = out["sources"].get(source_path)
        if not src or "ast" not in src:
            return {}
        ast_dict = src["ast"]
        simple = ast_scan_from_json(ast_dict)
        precise = _get_precise_analysis(ast_dict)
        if precise:
            simple["precise"] = precise
        return simple
    except Exception:
        return {}


def ast_scan_source(source_code: str, source_path: str = "inline.sol") -> Dict[str, Any]:
    """
    Run AST scan on source string (simple + precise contract-scoped when available).
    Returns {} when solc/solcx not available or compile fails.
    """
    return compile_and_ast_scan(source_path, source_code=source_code)

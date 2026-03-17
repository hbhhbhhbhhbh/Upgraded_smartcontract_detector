# -*- coding: utf-8 -*-
"""
Single-entry scanner: regex + optional AST, rule classification, output shape.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

from . import regex_detector
from . import ast_detector
from . import rules


def scan_file(
    file_path: str,
    contract_address: Optional[str] = None,
    source_code: Optional[str] = None,
    use_ast: bool = True,
) -> Dict[str, Any]:
    """
    Scan one Solidity file. Returns one result dict for the file (or per-contract if needed).

    Output shape: contract_address, pattern_type, confidence, details.
    """
    path = Path(file_path)
    if source_code is None:
        try:
            source_code = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return {
                "contract_address": contract_address or str(path),
                "file": str(path),
                "pattern_type": "error",
                "confidence": 0.0,
                "details": {"error": "Could not read file"},
            }

    regex_result = regex_detector.regex_scan(source_code)
    ast_result: Dict[str, Any] = {}
    if use_ast:
        ast_result = ast_detector.ast_scan_source(source_code, source_path=str(path))

    pattern_type, confidence = rules.classify(regex_result, ast_result)
    # 优先采用精确分析（合约级 AST）的特征输出
    precise = (ast_result or {}).get("precise", {})
    if precise.get("precision") == "ast_contract_scoped":
        extraction = {
            "key_instruction_delegatecall": precise.get("key_instruction_delegatecall", False),
            "storage_implementation_slot": precise.get("storage_implementation_slot", False),
            "function_upgrade_to": precise.get("function_upgrade_to", False),
            "function_fallback": precise.get("function_fallback", False),
            "precision": "ast_contract_scoped",
            "best_proxy_contract": precise.get("best_proxy", {}).get("name") if precise.get("best_proxy") else None,
        }
    else:
        ext = regex_result.get("pattern_extraction", {})
        extraction = {
            "key_instruction_delegatecall": ext.get("key_instruction_delegatecall", False),
            "storage_implementation_slot": ext.get("storage_implementation_slot", False),
            "function_upgrade_to": ext.get("function_upgrade_to", False),
            "function_fallback": ext.get("function_fallback", False),
        }

    return {
        "contract_address": contract_address or str(path.absolute()),
        "file": str(path),
        "pattern_type": pattern_type,
        "confidence": round(confidence, 4),
        "pattern_extraction": extraction,
        "details": {
            "regex": regex_result,
            "ast": ast_result if ast_result else None,
        },
    }


def scan_directory(
    directory: str,
    extensions: tuple = (".sol",),
    contract_address_map: Optional[Dict[str, str]] = None,
    use_ast: bool = True,
    exclude_dirs: Optional[tuple] = None,
) -> List[Dict[str, Any]]:
    """
    Scan all Solidity files under directory.
    contract_address_map: file_path -> address.
    exclude_dirs: directory names to skip (e.g. ("node_modules",)).
    """
    directory = Path(directory)
    address_map = contract_address_map or {}
    exclude = exclude_dirs or ()
    results = []
    for path in directory.rglob("*"):
        if path.is_file() and path.suffix.lower() in extensions:
            if any(part in exclude for part in path.parts):
                continue
            addr = address_map.get(str(path))
            results.append(scan_file(str(path), contract_address=addr, use_ast=use_ast))
    return results

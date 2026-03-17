# -*- coding: utf-8 -*-
"""Unit tests for precise_analyzer (contract/function-scoped AST)."""

import pytest
from usc_detector.precise_analyzer import precise_ast_analysis
from usc_detector import patterns as P


def _make_contract_ast(name, nodes):
    """Build a minimal ContractDefinition AST node."""
    return {"nodeType": "ContractDefinition", "name": name, "nodes": nodes}


def _make_function_ast(name, body_has_delegatecall, body_has_slot_hex=False):
    """Build FunctionDefinition with optional delegatecall and slot in body."""
    body = {"nodeType": "Block", "statements": []}
    if body_has_delegatecall:
        body["statements"].append({"nodeType": "ExpressionStatement", "expression": {"nodeType": "MemberAccess", "memberName": "delegatecall"}})
    if body_has_slot_hex:
        body["statements"].append({"nodeType": "VariableDeclaration", "initialValue": {"nodeType": "Literal", "value": P.EIP1967_IMPLEMENTATION_SLOT}})
    return {"nodeType": "FunctionDefinition", "name": name, "body": body}


def test_precise_analysis_simple_proxy():
    """Contract with delegatecall in _delegate and implementation slot constant."""
    func_delegate = _make_function_ast("_delegate", body_has_delegatecall=True)
    func_fallback = _make_function_ast("_fallback", body_has_delegatecall=False)
    slot_var = {"nodeType": "VariableDeclaration", "name": "_IMPLEMENTATION_SLOT", "initialValue": {"nodeType": "Literal", "value": P.EIP1967_IMPLEMENTATION_SLOT}}
    contract = _make_contract_ast("Proxy", [func_delegate, func_fallback, slot_var])
    ast = {"nodeType": "SourceUnit", "nodes": [contract]}
    result = precise_ast_analysis(ast)
    assert result["key_instruction_delegatecall"] is True
    assert result["storage_implementation_slot"] is True
    assert result["function_fallback"] is True
    assert result["best_proxy"] is not None
    assert result["best_proxy"]["name"] == "Proxy"
    assert "_delegate" in result["best_proxy"]["functions_with_delegatecall"]


def test_precise_analysis_no_delegatecall():
    """Contract with slot but no delegatecall -> best_proxy stays None."""
    slot_var = {"nodeType": "VariableDeclaration", "initialValue": {"nodeType": "Literal", "value": P.EIP1967_IMPLEMENTATION_SLOT}}
    contract = _make_contract_ast("Impl", [slot_var])
    ast = {"nodeType": "SourceUnit", "nodes": [contract]}
    result = precise_ast_analysis(ast)
    assert result["storage_implementation_slot"] is True
    assert result["key_instruction_delegatecall"] is False
    assert result.get("best_proxy") is None

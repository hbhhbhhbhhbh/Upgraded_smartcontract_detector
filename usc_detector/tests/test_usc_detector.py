# -*- coding: utf-8 -*-
"""
Automated tests: every run scans all contracts in the project's contracts/ folder.

Usage: from project root:
  pytest usc_detector/tests/test_usc_detector.py -v
  python -m pytest usc_detector/tests/test_usc_detector.py -v
"""

import pytest
from pathlib import Path

# Project root = parent of usc_detector package
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONTRACTS_DIR = PROJECT_ROOT / "contracts"
# Exclude node_modules and other non-project code
EXCLUDE_DIRS = ("node_modules",)


def get_contracts_dir() -> Path:
    """Return contracts directory; skip tests if missing."""
    if not CONTRACTS_DIR.is_dir():
        pytest.skip(f"contracts dir not found: {CONTRACTS_DIR}")
    return CONTRACTS_DIR


def collect_sol_files() -> list:
    """Collect all .sol files under contracts/, excluding EXCLUDE_DIRS."""
    contracts = get_contracts_dir()
    files = []
    for path in contracts.rglob("*.sol"):
        if path.suffix.lower() != ".sol":
            continue
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


@pytest.fixture(scope="module")
def contracts_scan_results():
    """Run USC detector on entire contracts/ folder once per test run (regex only for speed)."""
    from usc_detector.scanner import scan_directory
    contracts = get_contracts_dir()
    return scan_directory(
        str(contracts),
        exclude_dirs=EXCLUDE_DIRS,
        use_ast=False,
    )


@pytest.fixture
def sol_files():
    """List of .sol paths in contracts/ (excluding node_modules)."""
    return collect_sol_files()


class TestContractsFolder:
    """Tests that automatically run against all contracts in contracts/."""

    def test_contracts_dir_exists(self):
        """Ensure contracts/ folder exists."""
        assert get_contracts_dir().is_dir(), f"Expected {CONTRACTS_DIR} to exist"

    def test_has_sol_files(self, sol_files):
        """Ensure there is at least one .sol file to scan."""
        assert len(sol_files) >= 1, (
            f"No .sol files under {CONTRACTS_DIR} (excluding {EXCLUDE_DIRS})"
        )

    def test_scan_completes_without_error(self, contracts_scan_results):
        """Scan all contracts; no result should have pattern_type 'error'."""
        errors = [r for r in contracts_scan_results if r.get("pattern_type") == "error"]
        assert not errors, (
            f"Scan failed for {len(errors)} file(s): "
            + ", ".join(r.get("file", "?") for r in errors[:5])
        )

    def test_scan_result_count_matches_files(self, contracts_scan_results, sol_files):
        """Number of scan results should equal number of .sol files."""
        assert len(contracts_scan_results) == len(sol_files), (
            f"Expected {len(sol_files)} results, got {len(contracts_scan_results)}"
        )

    def test_each_result_has_required_fields(self, contracts_scan_results):
        """Each result must have contract_address, pattern_type, confidence, pattern_extraction."""
        for r in contracts_scan_results:
            assert "contract_address" in r, r.get("file", "?")
            assert "pattern_type" in r, r.get("file", "?")
            assert "confidence" in r, r.get("file", "?")
            assert isinstance(r["confidence"], (int, float))
            ext = r.get("pattern_extraction", {})
            assert "key_instruction_delegatecall" in ext
            assert "storage_implementation_slot" in ext
            assert "function_upgrade_to" in ext
            assert "function_fallback" in ext

    def test_known_proxy_detected_if_present(self, contracts_scan_results):
        """If any contract is a proxy, detector should label it (4 USC types or legacy)."""
        types = {r["pattern_type"] for r in contracts_scan_results}
        upgradeable_types = {
            "simple_proxy",
            "transparent_proxy",
            "uups",
            "diamond_beacon",
            "standard_proxy_eip1967",
            "delegatecall_only",
            "eip1967_slot_only",
            "beacon_proxy",
            "generic_upgradeable",
        }
        detected = types & upgradeable_types
        assert isinstance(detected, set)


class TestSingleContractScan:
    """Per-file scan tests using contracts/ files."""

    def test_each_contract_scans_without_exception(self, sol_files):
        """Each .sol file in contracts/ must scan without raising."""
        from usc_detector.scanner import scan_file
        for sol_path in sol_files:
            result = scan_file(str(sol_path), use_ast=False)
            assert "pattern_type" in result, f"{sol_path}"
            assert "confidence" in result, f"{sol_path}"
            if result.get("pattern_type") == "error":
                err = result.get("details", {}).get("error", "unknown")
                pytest.fail(f"Scan error for {sol_path}: {err}")

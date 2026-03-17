# -*- coding: utf-8 -*-
"""
CLI entry: scan Solidity files/dirs and output JSON or CSV.

Usage:
  python -m usc_detector.main --input path/to/contract.sol [--output results.json] [--format json|csv] [--no-ast]
  python -m usc_detector.main --input path/to/contracts/ --output out.csv --format csv
"""

import argparse
import json
import csv
import re
import sys
from pathlib import Path

from .scanner import scan_file, scan_directory

DEFAULT_EXCLUDE_DIRS = ("node_modules",)


def _sanitize_filename(name: str) -> str:
    """Safe filename from path or name."""
    s = re.sub(r'[<>:"/\\|?*]', "_", name)
    return s[:200].strip() or "contract"


def _to_csv_rows(results: list) -> list:
    if not results:
        return [["contract_address", "file", "pattern_type", "confidence", "details"]]
    rows = [["contract_address", "file", "pattern_type", "confidence", "details"]]
    for r in results:
        details = r.get("details", {})
        details_str = json.dumps(details, ensure_ascii=False) if details else ""
        rows.append([
            r.get("contract_address", ""),
            r.get("file", ""),
            r.get("pattern_type", ""),
            str(r.get("confidence", 0)),
            details_str,
        ])
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect Upgradeable Smart Contracts (USC) via regex + AST rules.")
    parser.add_argument("--input", "-i", default=None, help="Solidity file or directory")
    parser.add_argument("input_path", nargs="?", default=None, help="Solidity file or directory (if --input not set)")
    parser.add_argument("--output", "-o", default=None, help="Output file for combined results (default: stdout)")
    parser.add_argument("--output-dir", "-d", default=None, help="Write one JSON per contract into this directory + summary.json")
    parser.add_argument("--format", "-f", choices=["json", "csv"], default="json", help="Output format (for -o or stdout)")
    parser.add_argument("--no-ast", action="store_true", help="Disable AST scan (regex only)")
    parser.add_argument("--exclude-dirs", nargs="*", default=None, help="Dir names to skip (default: node_modules)")
    args = parser.parse_args()

    inp = args.input or args.input_path
    if not inp:
        parser.error("Provide --input/-i or a positional path.")
    inp = Path(inp)
    if not inp.exists():
        print("Error: input path does not exist.", file=sys.stderr)
        return 1

    use_ast = not args.no_ast
    exclude_dirs = tuple(args.exclude_dirs) if args.exclude_dirs is not None else DEFAULT_EXCLUDE_DIRS

    if inp.is_file():
        results = [scan_file(str(inp), use_ast=use_ast)]
    else:
        results = scan_directory(
            str(inp), use_ast=use_ast, exclude_dirs=exclude_dirs
        )

    out_path = Path(args.output) if args.output else None
    output_dir = Path(args.output_dir) if args.output_dir else None

    # Per-contract output: one JSON file per contract + summary.json
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        scan_root = inp if inp.is_dir() else inp.parent
        seen = {}
        for r in results:
            p = Path(r["file"])
            try:
                rel = p.resolve().relative_to(Path(scan_root).resolve())
            except ValueError:
                rel = p
            base_name = _sanitize_filename(str(rel).replace("\\", "_").replace("/", "_"))
            if not base_name.endswith(".sol"):
                base_name = base_name.replace(".sol", "")
            key = base_name
            seen[key] = seen.get(key, 0) + 1
            if seen[key] > 1:
                base_name = f"{base_name}_{seen[key]}"
            single_path = output_dir / f"{base_name}.json"
            single_path.write_text(
                json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        summary_path = output_dir / "summary.json"
        summary_path.write_text(
            json.dumps({"results": results, "count": len(results)}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        if not out_path:
            print(f"Wrote {len(results)} contract result(s) to {output_dir}/ and summary.json", file=sys.stderr)

    # Combined output: file or stdout
    if args.format == "csv":
        rows = _to_csv_rows(results)
        if out_path:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(rows)
        else:
            writer = csv.writer(sys.stdout)
            writer.writerows(rows)
    else:
        payload = {"results": results, "count": len(results)}
        text = json.dumps(payload, indent=2, ensure_ascii=False)
        if out_path:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(text, encoding="utf-8")
        else:
            if not output_dir:
                print(text)
            else:
                # When using -d, still print a short per-contract summary to stdout
                for r in results:
                    print(
                        r.get("file", "?"),
                        "|",
                        r.get("pattern_type", "?"),
                        "|",
                        r.get("confidence", 0),
                    )

    return 0


if __name__ == "__main__":
    sys.exit(main())

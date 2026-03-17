# -*- coding: utf-8 -*-
"""
Convenience runner for USC detector from project root.

Usage:
  python run_usc_detector.py <file_or_dir> [--output out.json] [--format json|csv] [--no-ast]

Example:
  python run_usc_detector.py ./contracts --output results.json --format json
  python run_usc_detector.py ./contracts/sample.sol -o out.csv -f csv
"""

import sys
import os

# Ensure package is on path when run from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from usc_detector.main import main

if __name__ == "__main__":
    sys.exit(main())

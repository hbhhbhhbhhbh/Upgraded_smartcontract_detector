# -*- coding: utf-8 -*-
"""USC Detector: rule-based Upgradeable Smart Contract detection."""

from .scanner import scan_file, scan_directory
from . import patterns

__all__ = ["scan_file", "scan_directory", "patterns"]

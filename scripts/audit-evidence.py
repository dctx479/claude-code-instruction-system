#!/usr/bin/env python3
"""Compatibility entry for the evidence audit interface."""
import argparse
import json
from pathlib import Path
import sys

from taiyi.common import warning
from taiyi.evidence import EvidenceQuery

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--memory", type=Path, default=Path(__file__).resolve().parents[1] / "memory")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        report = EvidenceQuery(args.memory, args.root).audit()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        sys.exit(int(bool(report["invalid"] or (args.strict and
                          (report["legacy"] or report["low_confidence"] or report["review_required"])))))
    except (OSError, ValueError) as exc:
        warning(f"evidence audit failed: {exc}")
        sys.exit(1)

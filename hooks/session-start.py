#!/usr/bin/env python3
"""Inject only the short flow card."""
from pathlib import Path
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
try:
    print((Path(__file__).resolve().parents[1] / "config/flow-card.md").read_text(encoding="utf-8"))
except OSError as exc:
    print(f"WARNING: flow card unavailable: {exc}", file=sys.stderr)

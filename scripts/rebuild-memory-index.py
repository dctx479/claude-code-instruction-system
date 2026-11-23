#!/usr/bin/env python3
"""Explicit memory index rebuild; main interface is taiyi-tool.py rebuild."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys

from taiyi.common import warning
from taiyi.search import MemoryIndex

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--memory", type=Path, default=Path(__file__).resolve().parents[1] / "memory")
    args = parser.parse_args()
    try:
        print(json.dumps(MemoryIndex(args.memory).sync(force=True)))
    except (OSError, ValueError, sqlite3.Error) as exc:
        warning(f"memory rebuild failed: {exc}")
        sys.exit(1)

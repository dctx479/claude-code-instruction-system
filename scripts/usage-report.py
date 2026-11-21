#!/usr/bin/env python3
"""Summarize the opt-in local history over a chosen observation window."""
import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=Path.home() / ".claude/taiyi/usage.jsonl")
    parser.add_argument("--days", type=int, default=28)
    args = parser.parse_args()
    counts = Counter()
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    try:
        for line in args.file.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if datetime.fromisoformat(row["ts"]) >= cutoff:
                counts[(row["tool"], row["name"])] += 1
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"WARNING: usage report unavailable: {exc}", file=sys.stderr)
        return 1
    print(json.dumps([dict(tool=t, name=n, calls=c) for (t, n), c in counts.most_common()], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Report supplied token measurements separately from output byte reduction."""
import argparse
import json
import math
from pathlib import Path
import sys

from taiyi.common import warning


def measure(rows):
    if not rows:
        raise ValueError("measurement rows required; no fabricated default token counts")
    result = dict(samples=len(rows))
    for unit in ("tokens", "bytes"):
        selected = [r for r in rows if "raw_" + unit in r and "actual_" + unit in r]
        raw = actual = 0
        for row in selected:
            values = [row["raw_" + unit], row["actual_" + unit]]
            if any(isinstance(v, bool) or not isinstance(v, (float, int)) or
                   not math.isfinite(v) or v < 0 for v in values):
                raise ValueError("measurement counts must be finite nonnegative numbers")
            raw += values[0]
            actual += values[1]
        result[unit] = dict(samples=len(selected), raw=raw, actual=actual,
                            reduction=1 - actual / raw if raw else None)
    result["note"] = "Byte reduction is not token savings; input tokens should include instruction/script overhead and the same task outcome."
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="JSONL rows with raw_tokens/actual_tokens or raw_bytes/actual_bytes")
    args = parser.parse_args()
    try:
        result = measure([json.loads(line) for line in args.file.read_text(encoding="utf-8").splitlines() if line.strip()])
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, TypeError) as exc:
        warning(f"measurement failed: {exc}")
        sys.exit(1)

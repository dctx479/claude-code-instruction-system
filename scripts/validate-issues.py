#!/usr/bin/env python3
"""Validate local issue dependencies; never execute commands from CSV."""
import argparse
import csv
from pathlib import Path
import sys


def validate(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"id", "title", "acceptance_criteria", "blocked_by", "dev_state"}
        if not required <= set(reader.fieldnames or []):
            raise ValueError("missing columns: " + ", ".join(sorted(required - set(reader.fieldnames or []))))
        rows = list(reader)
    if not rows:
        raise ValueError("empty issue set")
    by_id = {}
    for row in rows:
        if not row["id"] or row["id"] in by_id:
            raise ValueError("missing or duplicate issue id")
        if not row["title"].strip() or not row["acceptance_criteria"].strip():
            raise ValueError("title and executable acceptance criteria required")
        if row["dev_state"] not in {"TODO", "DOING", "BLOCKED", "DONE"}:
            raise ValueError("invalid dev_state")
        by_id[row["id"]] = row
    active, visited = set(), set()

    def visit(key):
        if key not in by_id:
            raise ValueError("unknown blocker: " + key)
        if key in active:
            raise ValueError("dependency cycle: " + key)
        if key in visited:
            return
        active.add(key)
        row = by_id[key]
        for dependency in filter(None, (x.strip() for x in row["blocked_by"].split("|"))):
            visit(dependency)
            if row["dev_state"] in {"DOING", "DONE"} and by_id[dependency]["dev_state"] != "DONE":
                raise ValueError(key + " started/completed before blocker " + dependency)
        active.remove(key)
        visited.add(key)

    for key in by_id:
        visit(key)
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    args = parser.parse_args()
    try:
        print(f"PASS: {validate(args.csv)} local issues")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"WARNING: issues invalid: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

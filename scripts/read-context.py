#!/usr/bin/env python3
"""Read archived context - index or specific resolution"""
import json
import sys
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

CONTEXT_DIR = Path(".claude/context")
RESOLUTIONS_DIR = CONTEXT_DIR / "resolutions"

def read_index():
    index_file = CONTEXT_DIR / "index.json"
    if not index_file.exists():
        print("❌ No index found. Run /save-context first.", file=sys.stderr)
        sys.exit(1)

    with open(index_file, encoding="utf-8") as f:
        index = json.load(f)

    print(json.dumps(index, indent=2, ensure_ascii=False))

def read_resolution(res_id):
    if not RESOLUTIONS_DIR.exists():
        print("❌ No resolutions found.", file=sys.stderr)
        sys.exit(1)

    for ndjson_file in sorted(RESOLUTIONS_DIR.glob("*.ndjson"), reverse=True):
        with open(ndjson_file, encoding="utf-8") as f:
            for line in f:
                res = json.loads(line.strip())
                if res.get("id") == res_id:
                    print(json.dumps(res, indent=2, ensure_ascii=False))
                    return

    print(f"❌ Resolution {res_id} not found.", file=sys.stderr)
    sys.exit(1)

def list_resolutions():
    if not RESOLUTIONS_DIR.exists():
        print("No resolutions yet.")
        return

    resolutions = []
    for ndjson_file in sorted(RESOLUTIONS_DIR.glob("*.ndjson"), reverse=True):
        with open(ndjson_file, encoding="utf-8") as f:
            for line in f:
                res = json.loads(line.strip())
                resolutions.append({
                    "id": res.get("id"),
                    "signature": res.get("problem_signature"),
                    "summary": res.get("problem", "")[:60]
                })

    print(f"📋 Found {len(resolutions)} resolutions:\n")
    for res in resolutions:
        print(f"  {res['id']}: {res['signature']}")
        print(f"    {res['summary']}")
        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python read-context.py <index|resolution|list> [res_id]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "index":
        read_index()
    elif cmd == "resolution":
        if len(sys.argv) < 3:
            print("Usage: python read-context.py resolution <res_id>")
            sys.exit(1)
        read_resolution(sys.argv[2])
    elif cmd == "list":
        list_resolutions()
    else:
        print(f"❌ Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)

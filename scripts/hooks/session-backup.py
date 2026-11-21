#!/usr/bin/env python3
"""Opt-in bounded diff backup; operates only on its own patch files."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import uuid

LIMIT = 50 * 1024 * 1024


def prune(directory, now=None, limit=LIMIT):
    now = time.time() if now is None else now
    files = sorted((p for p in directory.glob("taiyi-*.patch") if p.is_file() and not p.is_symlink()),
                   key=lambda p: p.stat().st_mtime)
    total = sum(p.stat().st_size for p in files)
    for path in files:
        if now - path.stat().st_mtime > 14 * 86400 or total > limit:
            size = path.stat().st_size
            path.unlink()
            total -= size


def main():
    try:
        event = json.load(sys.stdin)
        root = Path(event["cwd"]).resolve()
        result = subprocess.run(["git", "-C", str(root), "diff", "HEAD", "--no-ext-diff", "--no-textconv"],
                                capture_output=True, timeout=8)
        if result.returncode:
            raise ValueError("git diff failed (not a repository or missing HEAD)")
        directory = Path.home() / ".claude/taiyi/session-backups"
        directory.mkdir(parents=True, exist_ok=True)
        prune(directory)
        if len(result.stdout) > LIMIT:
            raise ValueError("diff exceeds backup limit; skipped")
        if result.stdout:
            key = hashlib.sha256(str(root).encode()).hexdigest()[:12]
            path = directory / f"taiyi-{key}-{uuid.uuid4().hex}.patch"
            with path.open("xb") as stream:
                stream.write(result.stdout)
            if sys.platform != "win32":
                path.chmod(0o600)
            prune(directory)
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        print(f"WARNING: session backup unavailable: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())

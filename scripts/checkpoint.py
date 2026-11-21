#!/usr/bin/env python3
"""Save/verify a per-worktree handoff. Exit 0 valid, 2 absent, 1 damaged/stale."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def location(root):
    root = Path(root).resolve()
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "--git-path", "taiyi/checkpoint.json"],
                            capture_output=True, text=True, encoding="utf-8", check=True)
    path = Path(result.stdout.strip())
    return path if path.is_absolute() else root / path


def digest(root, name):
    # Windows TEMP may use an 8.3 alias; normalize both sides before containment.
    root = Path(root).resolve()
    if not isinstance(name, str) or Path(name).is_absolute():
        raise ValueError("checkpoint paths must be repository relative")
    path = (root / name).resolve()
    if not path.is_relative_to(root) or ".git" in path.relative_to(root).parts:
        raise ValueError("checkpoint path outside permitted worktree")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(data):
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("unsupported checkpoint schema")
    if not isinstance(data.get("goal"), str) or not data["goal"].strip():
        raise ValueError("goal is required")
    for key in ("done", "next", "evidence"):
        if not isinstance(data.get(key), list) or any(not isinstance(x, str) for x in data[key]):
            raise ValueError(key + " must be an array of strings")
    if not isinstance(data.get("files_sha256"), dict):
        raise ValueError("files_sha256 must be a mapping")


def save(root, data):
    data = dict(data, version=1, created_at=datetime.now(timezone.utc).isoformat())
    files = data.pop("files", [])
    if not isinstance(files, list):
        raise ValueError("files must be an array")
    data["files_sha256"] = {name: digest(root, name) for name in files}
    validate(data)
    path = location(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    return path


def verify(root):
    path = location(root)
    if not path.exists():
        return 2
    data = json.loads(path.read_text(encoding="utf-8"))
    validate(data)
    for name, expected in data["files_sha256"].items():
        if digest(root, name) != expected:
            raise ValueError("checkpoint file changed: " + name)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("save", "verify", "show"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.mode == "save":
            print(save(root, json.load(sys.stdin)))
            return 0
        code = verify(root)
        if code == 2:
            print("WARNING: no checkpoint", file=sys.stderr)
        elif args.mode == "show":
            print(location(root).read_text(encoding="utf-8"))
        return code
    except (OSError, ValueError, TypeError, subprocess.CalledProcessError) as exc:
        print(f"WARNING: checkpoint invalid: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())

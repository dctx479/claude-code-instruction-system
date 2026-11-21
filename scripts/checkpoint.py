#!/usr/bin/env python3
"""Save/verify a per-worktree handoff. Exit 0 valid, 2 absent, 1 damaged/stale."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import shutil
import subprocess
import sys
import tempfile


def git_environment():
    # Hook-local GIT_DIR/GIT_WORK_TREE must not redirect state to another repository.
    return {key: value for key, value in os.environ.items() if key not in {
        "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM"}}


def git(root, *arguments):
    executable = shutil.which("git")
    if not executable:
        raise ValueError("git executable unavailable")
    return subprocess.run([executable, "-C", str(root), *arguments], env=git_environment(),
                          capture_output=True, text=True, encoding="utf-8", check=True)


def worktree_root(root):
    result = git(Path(root).resolve(), "rev-parse", "--show-toplevel")
    return Path(result.stdout.strip()).resolve()


def location(root):
    root = worktree_root(root)
    result = git(root, "rev-parse", "--git-path", "taiyi/checkpoint.json")
    path = Path(result.stdout.strip())
    return path if path.is_absolute() else root / path


def digest(root, name):
    # Windows TEMP may use an 8.3 alias; normalize both sides before containment.
    root = Path(root).resolve()
    if not isinstance(name, str) or not name or Path(name).is_absolute() or PureWindowsPath(name).drive:
        raise ValueError("checkpoint paths must be repository relative")
    if any(re.fullmatch(r"(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", part, re.I)
           for part in PureWindowsPath(name).parts):
        raise ValueError("checkpoint path is a reserved device name")
    path = (root / name).resolve()
    if not path.is_relative_to(root) or ".git" in path.relative_to(root).parts:
        raise ValueError("checkpoint path outside permitted worktree")
    if not path.is_file():
        raise ValueError("checkpoint artifact must be a regular file")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(data):
    if not isinstance(data, dict) or type(data.get("version")) is not int or data["version"] != 1:
        raise ValueError("unsupported checkpoint schema")
    if not isinstance(data.get("goal"), str) or not data["goal"].strip():
        raise ValueError("goal is required")
    for key in ("done", "next", "evidence"):
        if not isinstance(data.get(key), list) or any(not isinstance(x, str) for x in data[key]):
            raise ValueError(key + " must be an array of strings")
    if not isinstance(data.get("files_sha256"), dict):
        raise ValueError("files_sha256 must be a mapping")
    for name, value in data["files_sha256"].items():
        if not isinstance(name, str) or not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("files_sha256 needs relative names and SHA-256 hex values")


def save(root, data):
    root = worktree_root(root)
    if not isinstance(data, dict):
        raise ValueError("checkpoint input must be an object")
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
    root = worktree_root(root)
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
    except (OSError, ValueError, TypeError, RecursionError, subprocess.CalledProcessError) as exc:
        print(f"WARNING: checkpoint invalid: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())

#!/usr/bin/env python3
"""Opt-in local lint feedback, without auto-fix, npm scripts or package downloads."""
import json
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    try:
        event = json.load(sys.stdin)
        root = Path(event["cwd"]).resolve()
        path = Path(event["tool_input"]["file_path"])
        path = (root / path).resolve() if not path.is_absolute() else path.resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError("edited file is not inside the project")
        command = None
        if path.suffix == ".py" and shutil.which("ruff"):
            command = [shutil.which("ruff"), "check", "--no-fix", "--", str(path)]
        elif path.suffix in {".js", ".jsx", ".ts", ".tsx"}:
            # Execute the local JS entry with node; do not invoke .cmd through a shell.
            eslint = root / "node_modules/eslint/bin/eslint.js"
            if eslint.is_file() and shutil.which("node"):
                command = [shutil.which("node"), str(eslint), "--no-fix", "--", str(path)]
        if not command:
            print("WARNING: lint feedback skipped: no applicable local linter", file=sys.stderr)
            return 0
        result = subprocess.run(command, cwd=root, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=20)
        if result.returncode:
            print("WARNING: local lint reported problems", file=sys.stderr)
            print((result.stdout + result.stderr)[-8000:], file=sys.stderr)
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        print(f"WARNING: lint feedback unavailable: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())

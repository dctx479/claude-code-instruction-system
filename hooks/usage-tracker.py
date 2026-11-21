#!/usr/bin/env python3
"""Opt-in local invocation history. Never store prompts, arguments, paths or responses."""
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time


def record(event, directory):
    tool = event.get("tool_name")
    if event.get("hook_event_name") == "UserPromptSubmit":
        prompt = event.get("prompt")
        if not isinstance(prompt, str):
            raise ValueError("prompt must be a string")
        explicit = re.match(r"^/([a-z][a-z0-9-]*)(?=\s|$)", prompt.strip())
        if not explicit:
            return
        name = explicit[1]
        config = directory.parent
        # Slash expansion is not a Skill tool call. Only count registered personal capabilities,
        # not arbitrary slash text, prompt arguments, or built-in CLI commands.
        if not ((config / "skills" / name / "SKILL.md").is_file() or (config / "commands" / (name + ".md")).is_file()):
            return
        tool = "Skill" if (config / "skills" / name / "SKILL.md").is_file() else "Command"
        args = {}
    else:
        args = event.get("tool_input", {})
        name = args.get("skill") if tool == "Skill" else args.get("subagent_type")
    if tool not in {"Skill", "Agent", "Task", "Command"}:
        return
    if not isinstance(name, str) or not re.fullmatch(r"[\w.:-]{1,128}", name):
        raise ValueError("missing/invalid invocation name")
    directory.mkdir(parents=True, exist_ok=True)
    # Exclusive short critical section, fail visibly rather than corrupt concurrent writes.
    lock = directory / "usage.lock"
    deadline = time.monotonic() + 0.5
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise
            time.sleep(0.01)
    try:
        os.close(fd)
        now = datetime.now(timezone.utc)
        path = directory / "usage.jsonl"
        rows = []
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                item = json.loads(line)
                if datetime.fromisoformat(item["ts"]) >= now - timedelta(days=90):
                    rows.append(item)
        rows.append(dict(ts=now.isoformat(), tool=tool, name=name))
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory,
                                             prefix="usage-", suffix=".tmp", delete=False) as stream:
                temporary = Path(stream.name)
                for row in rows:
                    stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            os.replace(temporary, path)
            if os.name != "nt":
                path.chmod(0o600)
        finally:
            if temporary and temporary.exists():
                temporary.unlink()
    finally:
        lock.unlink()


def main():
    try:
        record(json.load(sys.stdin), Path.home() / ".claude/taiyi")
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        print(f"WARNING: usage event not recorded: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())

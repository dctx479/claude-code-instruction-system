#!/usr/bin/env python3
"""Parse hook JSON and publish advisory context; never execute prompt content."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile


def routing_text(prompt):
    """Ignore explicit quotations. Ambiguous large pastes route conservatively."""
    lines = []
    fence = None
    for line in prompt.splitlines():
        stripped = line.lstrip()
        marker = re.match(r"(`{3,}|~{3,})", stripped)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None and not stripped.startswith(">"):
            lines.append(line)
    text = "\n".join(lines).strip()
    if len(text) > 2000:
        # First-line manual selection is explicit even when followed by an article.
        manual = re.match(r"^@([a-z][a-z0-9-]*)\b", text)
        if manual:
            return manual.group(0)
        tail = re.split(r"\n\s*\n", text)[-1].strip()
        return tail if len(tail) <= 500 else ""
    return text


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=path.name + ".", suffix=".tmp", delete=False) as f:
            name = f.name
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(name, path)
    finally:
        if name and Path(name).exists():
            Path(name).unlink()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("select", "publish", "route"))
    parser.add_argument("--state-dir", type=Path)
    parser.add_argument("--intent", default="general")
    parser.add_argument("--agent", default="orchestrator")
    parser.add_argument("--skill", default="")
    parser.add_argument("--tool", default="")
    args = parser.parse_args()
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict) or not isinstance(event.get("prompt"), str):
            raise ValueError("expected a JSON object with string prompt")
        if any(not isinstance(event.get(key, ""), str) for key in ("session_id", "cwd")):
            raise ValueError("session_id/cwd must be strings")
    except (ValueError, OSError) as exc:
        print(f"WARNING: intent input invalid: {exc}", file=sys.stderr)
        return 1
    if args.mode == "select":
        print(routing_text(event["prompt"]))
        return 0

    if args.mode == "route":
        # Only the actual first line is eligible, never a tail extracted from a paste.
        text = event["prompt"].strip()
        manual = re.match(r"^@([a-z][a-z0-9-]*)(?=\s|$)", text)
        command = re.match(r"^/([a-z][a-z0-9-]*)(?=\s|$)", text)
        args.intent = "manual" if manual else "command" if command else "none"
        args.agent = manual[1] if manual else ""
        args.skill = command[1] if command else ""

    tool = None
    if args.tool:
        try:
            tool = json.loads(args.tool)
            if tool is not None and not isinstance(tool, dict):
                raise ValueError("tool recommendation must be an object")
        except ValueError as exc:
            print(f"WARNING: invalid tool recommendation: {exc}", file=sys.stderr)
            tool = None
    data = {"intent": args.intent, "agent": args.agent, "skill": args.skill,
            "tool_recommendation": tool, "session_id": event.get("session_id", ""),
            "cwd": event.get("cwd", "")}
    # Context comes from this invocation, independent of disk/HUD failures.
    if args.intent != "none":
        print("Advisory routing (verify against the current request): " +
              json.dumps(data, ensure_ascii=False))
    if args.state_dir:
        if data["session_id"]:
            key = hashlib.sha256((data["cwd"] + "\0" + data["session_id"]).encode()).hexdigest()
            try:
                atomic_json(args.state_dir / "intent-sessions" / (key + ".json"), data)
            except OSError as exc:
                print(f"WARNING: session routing state unavailable: {exc}", file=sys.stderr)
        # Backward-compatible, last-writer-wins snapshot for the old HUD only.
        try:
            atomic_json(args.state_dir / "intent-state.json", data)
        except OSError as exc:
            print(f"WARNING: HUD snapshot unavailable: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())

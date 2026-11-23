#!/usr/bin/env python3
"""Opt-in advisory Hook. Never grants permissions or substitutes tool output."""
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from taiyi.common import warning
from taiyi.context import post_tool, pre_tool
from taiyi.state import SessionStore


def handle(event):
    if not isinstance(event, dict):
        raise ValueError("Hook payload must be an object")
    cwd = Path(event.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or cwd).resolve()
    store = SessionStore(root, event.get("session_id"))
    kind = event.get("hook_event_name")
    tool = event.get("tool_name")
    inputs = event.get("tool_input", {})
    if not isinstance(inputs, dict):
        raise ValueError("tool_input must be an object")
    advice = None
    if kind == "PreToolUse":
        advice = pre_tool(store, tool, inputs, cwd, event.get("tool_use_id"))
    elif kind in {"PostToolUse", "PostToolUseFailure"}:
        response = event.get("error") if kind == "PostToolUseFailure" else event.get("tool_response")
        advice = post_tool(store, tool, inputs, response, kind == "PostToolUseFailure", event.get("tool_use_id"), cwd)
    elif kind == "PreCompact":
        if store.path.exists():
            store.snapshot()
        # PreCompact stdout is not a context injection channel.
        return None
    elif kind == "SessionStart" and event.get("source") in {"compact", "resume"}:
        events = store.recall(limit=4)
        if events:
            advice = "会话事件摘要（参考；文件和测试状态需复核）：\n" + "\n".join(
                f"{e['kind']}: {e['summary']}" for e in events)
    elif kind == "UserPromptSubmit":
        # No prompt history is retained. Explicit commands own task routing.
        return None
    if advice:
        return dict(hookSpecificOutput=dict(hookEventName=kind, additionalContext=advice[:2200]))
    return None


def main():
    try:
        output = handle(json.load(sys.stdin))
        if output:
            print(json.dumps(output, ensure_ascii=False))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RecursionError) as exc:
        warning(f"context optimization skipped: {exc}")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    sys.exit(main())

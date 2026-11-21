#!/usr/bin/env python3
"""HUD-only agent state, parsed as JSON and atomically replaced."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import tempfile


def main():
    temporary = None
    try:
        event = json.load(sys.stdin)
        if event.get("tool_name") not in {"Agent", "Task"}:
            return 0
        name = event.get("tool_input", {}).get("subagent_type")
        if not isinstance(name, str) or not re.fullmatch(r"[\w:-]{1,128}", name):
            raise ValueError("missing/invalid agent type")
        root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or event["cwd"]).resolve()
        directory = root / ".claude"
        if not directory.is_dir():
            return 0  # A project without HUD state does not need a new directory.
        data = dict(current_agent=name, last_updated=datetime.now(timezone.utc).isoformat(), agent_history=[])
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory, suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, ensure_ascii=False)
        os.replace(temporary, directory / "agent-state.json")
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f"WARNING: agent HUD state unavailable: {exc}", file=sys.stderr)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())

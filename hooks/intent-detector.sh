#!/bin/bash
# Explicit routing only. Never execute or infer commands from prompt content.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if ! command -v python >/dev/null 2>&1; then
    echo "WARNING: intent routing skipped: python unavailable" >&2
    exit 0
fi
if ! python "$SCRIPT_DIR/intent-context.py" route --state-dir "$HOME/.claude"; then
    echo "WARNING: intent routing unavailable" >&2
fi
exit 0

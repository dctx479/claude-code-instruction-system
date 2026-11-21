#!/bin/bash
# Ralph Stop protocol: exit 2 only after persisted next/resume transitions.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [[ ! -f "$SCRIPT_DIR/ralph-state.py" ]]; then
    echo "WARNING: Ralph state helper is missing; allowing stop" >&2
    exit 0
fi
PYTHON_BIN="${PYTHON_CMD:-}"
if [[ -z "$PYTHON_BIN" ]]; then
    for candidate in python3 python py; do
        if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c "import sys; assert sys.version_info >= (3, 10)" >/dev/null 2>&1; then
            PYTHON_BIN="$candidate"
            break
        fi
    done
fi
if [[ -z "$PYTHON_BIN" ]]; then
    echo "WARNING: Ralph requires Python 3.10+; allowing stop" >&2
    exit 0
fi
args=(--home "$HOME" --project-root "${CLAUDE_PROJECT_DIR:-$PWD}" --max-iterations "${RALPH_MAX_ITERATIONS:-10}")
[[ -z "${RALPH_STATE_FILE:-}" ]] || args+=(--state-file "$RALPH_STATE_FILE")
[[ -z "${RALPH_LOG_FILE:-}" ]] || args+=(--log-file "$RALPH_LOG_FILE")
"$PYTHON_BIN" "$SCRIPT_DIR/ralph-state.py" "${args[@]}"
code=$?
if [[ "$code" != 0 && "$code" != 2 ]]; then
    echo "WARNING: Ralph helper failed (exit $code); allowing stop" >&2
    exit 0
fi
exit "$code"

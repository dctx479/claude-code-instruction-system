#!/usr/bin/env bash
# Stable installed entry; JSON and rendering run in one standard-library process.
set -euo pipefail

SCRIPT_PATH="${BASH_SOURCE[0]//\\//}"
case "$SCRIPT_PATH" in
    */*) SCRIPT_DIR="${SCRIPT_PATH%/*}" ;;
    *) SCRIPT_DIR="." ;;
esac
if [[ ! -f "$SCRIPT_DIR/hud.py" ]]; then
    printf '%s\n' 'WARNING: HUD renderer file is missing' >&2
    printf '%s\n' 'HUD unavailable'
    exit 1
fi
if command -v python >/dev/null 2>&1; then
    exec python -S "$SCRIPT_DIR/hud.py" "$@"
elif command -v python3 >/dev/null 2>&1; then
    exec python3 -S "$SCRIPT_DIR/hud.py" "$@"
else
    printf '%s\n' 'WARNING: HUD requires Python 3.10+' >&2
    printf '%s\n' 'HUD unavailable'
    exit 1
fi

#!/bin/bash
# Verify actual installed files and run the installed Hook with an isolated HOME.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python "$ROOT/scripts/verify-global-install.py" --repo "$ROOT" --smoke-hook "$@"

#!/bin/bash
# Compatibility entry point; uses the same isolated routing regression suite.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec bash "$ROOT/scripts/test-all-intents.sh"

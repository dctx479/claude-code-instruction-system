#!/bin/bash
# Test the repository hook in temporary HOME directories; no global install needed.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python -m unittest discover -s tests -p 'test_intent_routing.py' -v

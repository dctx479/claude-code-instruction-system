#!/usr/bin/env python3
"""Offline description overlap hints, not model routing accuracy."""
import itertools
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def main():
    import importlib.util
    spec = importlib.util.spec_from_file_location("facts", ROOT / "scripts/check-doc-facts.py")
    facts = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(facts)
    descriptions = {}
    for path in (ROOT / ".claude/skills").glob("*/SKILL.md"):
        data = facts.header(path)
        if data.get("disable-model-invocation"):
            continue
        text = data["description"].lower()
        tokens = set(re.findall(r"[a-z]{3,}", text))
        chinese = re.findall(r"[\u4e00-\u9fff]+", text)
        tokens.update(word[i:i+2] for word in chinese for i in range(len(word)-1))
        descriptions[path.parent.name] = tokens
    warnings = 0
    for (a, one), (b, two) in itertools.combinations(descriptions.items(), 2):
        score = len(one & two) / max(1, len(one | two))
        if score >= 0.75:
            print(f"WARNING: description overlap {a} / {b}: {score:.2f}; human review required")
            warnings += 1
    print(f"Checked {len(descriptions)} automatic descriptions; {warnings} overlap hints; model routing NOT_RUN")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

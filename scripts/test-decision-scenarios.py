#!/usr/bin/env python3
"""Run labelled local route scenarios; these are fixtures, not live Agent tasks."""
import json
from pathlib import Path

from taiyi.decision import DecisionRouter


def evaluate(root):
    scenarios = json.loads((root / "evals/fixtures/decision-scenarios.json").read_text(encoding="utf-8"))
    if not scenarios:
        raise ValueError("empty scenario set")
    router = DecisionRouter(root / "memory")
    results = []
    for item in scenarios:
        actual = router.route(item["task"])["decision"]
        results.append(dict(**item, actual=actual, passed=actual == item["expected"]))
    return dict(dataset="local labelled fixtures", total=len(results),
                accuracy=sum(item["passed"] for item in results) / len(results), results=results)


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    result = evaluate(Path(__file__).resolve().parents[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if all(item["passed"] for item in result["results"]) else 1)

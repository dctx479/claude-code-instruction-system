#!/usr/bin/env python3
"""Reproducible local runtime latency and synthetic output reduction baseline."""
import argparse
import json
from pathlib import Path
import statistics
import sqlite3
import sys
import tempfile
import time

from taiyi.common import atomic_json, warning
from taiyi.context import aggregate, summarize
from taiyi.decision import DecisionRouter
from taiyi.evidence import EvidenceQuery
from taiyi.search import MemoryIndex


def timing(operation, repeats):
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        operation()
        samples.append((time.perf_counter() - start) * 1000)
    ordered = sorted(samples)
    return dict(samples=repeats, median_ms=round(statistics.median(samples), 3),
                p95_ms=round(ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))], 3))


def benchmark(root, repeats=1000):
    router = DecisionRouter(root / "memory")
    evidence = EvidenceQuery(root / "memory/curated", root)
    with tempfile.TemporaryDirectory() as temp:
        temporary = Path(temp)
        index = MemoryIndex(root / "memory", temporary / "index.db")
        started = time.perf_counter()
        metadata = index.sync()
        cold_ms = (time.perf_counter() - started) * 1000
        result = dict(dataset="local repository plus synthetic aggregation fixtures",
            route=timing(lambda: router.route("统计目录文件行数"), repeats),
            playbook=timing(lambda: router.route("全局安装"), min(repeats, 100)),
            evidence=timing(lambda: evidence.verify_evidence("fix-backup-collision"), min(repeats, 100)),
            search=timing(lambda: index.search("backup collision"), min(repeats, 100)),
            cold_index_ms=round(cold_ms, 3), indexed_documents=metadata["documents"])
        log = ["INFO request completed with status 200 and normal latency\n"] * 500
        summary = summarize(iter(log))
        summary_bytes = len(json.dumps(summary, ensure_ascii=False).encode("utf-8"))
        for i in range(50):
            (temporary / f"source-{i}.py").write_text("value = 1\n" * 100, encoding="utf-8")
        aggregated = aggregate(temporary)
        aggregate_bytes = len(json.dumps(aggregated, ensure_ascii=False).encode("utf-8"))
        result["synthetic_bytes"] = dict(log_raw=summary["raw_bytes"], log_actual=summary_bytes,
            log_reduction=round(1 - summary_bytes / summary["raw_bytes"], 4),
            files_raw=aggregated["raw_bytes"], files_actual=aggregate_bytes,
            files_reduction=round(1 - aggregate_bytes / aggregated["raw_bytes"], 4))
        result["tokens"] = None
        result["unverified"] = ["live token savings", "session duration improvement", "repeat-task time improvement", "three external projects"]
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=1000)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.repeats <= 10000:
        parser.error("--repeats must be 1..10000")
    try:
        result = benchmark(Path(__file__).resolve().parents[1], args.repeats)
        if args.output:
            atomic_json(args.output, result)
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, sqlite3.Error) as exc:
        warning(f"benchmark failed: {exc}")
        sys.exit(1)

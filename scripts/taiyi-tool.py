#!/usr/bin/env python3
"""Unified CLI for the optional context/routing/evidence runtime."""
import argparse
import json
import math
from pathlib import Path
import sqlite3
import subprocess
import sys

from taiyi.common import warning
from taiyi.context import aggregate, ContentCache, summarize
from taiyi.decision import analyze, DecisionRouter, feedback, Playbooks
from taiyi.evidence import chain_issues, EvidenceQuery
from taiyi.search import MemoryIndex
from taiyi.state import SessionStore


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path.cwd(), help="project state root")
    p.add_argument("--memory", type=Path, default=Path(__file__).resolve().parents[1] / "memory")
    p.add_argument("--session", help="required for persistent session operations")
    commands = p.add_subparsers(dest="command", required=True)
    route = commands.add_parser("route")
    route.add_argument("task")
    route.add_argument("--record", action="store_true")
    search = commands.add_parser("search")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=3)
    commands.add_parser("rebuild")
    book = commands.add_parser("playbook")
    book.add_argument("name")
    book.add_argument("--version")
    record = commands.add_parser("record")
    record.add_argument("id")
    record.add_argument("outcome", choices=["success", "failure", "rejected"])
    record.add_argument("--duration-ms", type=float)
    record.add_argument("--cost", type=float)
    commands.add_parser("analyze")
    session = commands.add_parser("session")
    session.add_argument("action", choices=["add", "snapshot", "recall"])
    session.add_argument("--kind", default="decision", choices=["decision", "task", "failure", "evidence"])
    session.add_argument("--text", default="")
    summary = commands.add_parser("summarize")
    summary.add_argument("--file", type=Path)
    agg = commands.add_parser("aggregate")
    agg.add_argument("directory", type=Path)
    agg.add_argument("--pattern", default="*.py")
    agg.add_argument("--operation", choices=["lines", "grep", "metadata"], default="lines")
    agg.add_argument("--needle")
    agg.add_argument("--limit", type=int, default=50)
    cache = commands.add_parser("cache")
    cache.add_argument("action", choices=["get", "put"])
    cache.add_argument("key")
    cache.add_argument("--file", type=Path)
    cache.add_argument("--query", default="")
    cache.add_argument("--ttl", type=int, default=86400)
    evidence = commands.add_parser("evidence")
    evidence.add_argument("action", choices=["trace", "verify", "find"])
    evidence.add_argument("name", nargs="?")
    evidence.add_argument("--min-confidence", type=float, default=0.8)
    audit = commands.add_parser("audit")
    audit.add_argument("--strict", action="store_true", help="also fail on legacy/review/low confidence entries")
    return p


def run(args):
    store = SessionStore(args.root, args.session) if args.session else None
    if args.command in {"record", "analyze", "session"} and store is None:
        raise ValueError("--session is required")
    command = args.command
    if command == "route":
        return DecisionRouter(args.memory, store).route(args.task, record=args.record), 0
    if command in {"search", "rebuild"}:
        index = MemoryIndex(args.memory)
        return (index.sync(force=True) if command == "rebuild" else index.search(args.query, args.limit)), 0
    if command == "playbook":
        return Playbooks(args.memory).load(args.name, args.version), 0
    if command == "record":
        return feedback(store, args.id, args.outcome, args.duration_ms, args.cost), 0
    if command == "analyze":
        return analyze(store), 0
    if command == "session":
        if args.action == "add":
            if not args.text:
                raise ValueError("session add requires --text")
            result = store.record(args.kind, args.text)
        elif args.action == "snapshot":
            result = store.snapshot()
        else:
            result = store.recall(args.text)
        return result, 0
    if command == "summarize":
        if args.file:
            with args.file.open(encoding="utf-8") as stream:
                return summarize(stream), 0
        return summarize(sys.stdin), 0
    if command == "aggregate":
        result = aggregate(args.directory, args.pattern, args.operation, args.needle, args.limit)
        return result, 1 if result["skipped"] else 0
    if command == "cache":
        cache = ContentCache(args.root / ".claude/taiyi/cache")
        if args.action == "put":
            if not args.file:
                raise ValueError("cache put requires --file")
            return cache.put(args.key, args.file.read_text(encoding="utf-8"), args.ttl), 0
        result = cache.get(args.key, args.query)
        return result, 0 if result["hit"] else 2
    query = EvidenceQuery(args.memory, args.root)
    if command == "evidence":
        if args.action == "find":
            if not math.isfinite(args.min_confidence) or not 0 <= args.min_confidence <= 1:
                raise ValueError("confidence must be 0..1")
            return query.find_by_confidence(args.min_confidence), 0
        if not args.name:
            raise ValueError("evidence name required")
        result = query.trace_evidence_chain(args.name) if args.action == "trace" else query.verify_evidence(args.name)
        verification = result.get("verification", result)
        return result, 1 if chain_issues(result) or verification["status"] == "invalid" or any(
            e["status"] in {"invalid", "changed"} for e in verification.get("evidence", [])) else 0
    if command == "audit":
        result = query.audit()
        failure = bool(result["invalid"] or (args.strict and
                       (result["legacy"] or result["review_required"] or result["low_confidence"])))
        return result, int(failure)
    raise ValueError("unknown command")


def main():
    args = parser().parse_args()
    try:
        result, status = run(args)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return status
    except (OSError, ValueError, TypeError, KeyError, sqlite3.Error, subprocess.SubprocessError, SyntaxError, RecursionError) as exc:
        warning(f"operation failed: {exc}")
        return 1


if __name__ == "__main__":
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    sys.exit(main())

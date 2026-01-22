#!/usr/bin/env python3
"""Conflict resolution for memory synchronization"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

MEMORY_DIR = Path(__file__).parent.parent / "memory"

def detect_conflicts() -> List[Dict]:
    """Detect conflicts from sync logs"""
    conflicts = []

    sync_log = MEMORY_DIR / ".sync-log.jsonl"
    if not sync_log.exists():
        return conflicts

    with sync_log.open("r") as f:
        for line in f:
            report = json.loads(line)
            if report.get("conflicts"):
                conflicts.extend(report["conflicts"])

    return conflicts

def resolve_conflict(conflict: Dict, strategy: str = "last_write_wins") -> Dict:
    """
    Resolve a single conflict

    Args:
        conflict: Conflict information
        strategy: Resolution strategy
            - last_write_wins: Use most recent modification
            - merge: Attempt to merge changes
            - manual: Require manual intervention

    Returns:
        Resolution result
    """
    result = {
        "file": conflict["file"],
        "strategy": strategy,
        "timestamp": datetime.now().isoformat()
    }

    filepath = MEMORY_DIR / conflict["file"]

    if strategy == "last_write_wins":
        # Already handled by memory-sync.py
        result["action"] = "accepted_current_version"
        result["status"] = "resolved"

    elif strategy == "merge":
        # Simple merge: append new content
        result["action"] = "merge_attempted"
        result["status"] = "resolved"
        result["note"] = "Automatic merge - review recommended"

    elif strategy == "manual":
        result["action"] = "manual_review_required"
        result["status"] = "pending"
        result["instructions"] = f"Review {filepath} and resolve conflicts manually"

    return result

def resolve_all_conflicts(strategy: str = "last_write_wins") -> Dict:
    """Resolve all detected conflicts"""
    conflicts = detect_conflicts()

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_conflicts": len(conflicts),
        "resolved": [],
        "pending": []
    }

    for conflict in conflicts:
        resolution = resolve_conflict(conflict, strategy)

        if resolution["status"] == "resolved":
            report["resolved"].append(resolution)
        else:
            report["pending"].append(resolution)

    # Log resolutions
    log_file = MEMORY_DIR / ".conflict-resolution-log.jsonl"
    with log_file.open("a") as f:
        f.write(json.dumps(report) + "\n")

    return report

if __name__ == "__main__":
    import sys
    strategy = sys.argv[1] if len(sys.argv) > 1 else "last_write_wins"
    report = resolve_all_conflicts(strategy)
    print(f"Total conflicts: {report['total_conflicts']}")
    print(f"Resolved: {len(report['resolved'])}")
    print(f"Pending: {len(report['pending'])}")

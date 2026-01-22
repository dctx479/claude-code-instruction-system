#!/usr/bin/env python3
"""Memory file synchronization - syncs memory/*.md files with timestamps and conflict detection"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

MEMORY_DIR = Path(__file__).parent.parent / "memory"
SYNC_STATE_FILE = MEMORY_DIR / ".sync-state.json"

def get_file_hash(filepath: Path) -> str:
    """Calculate MD5 hash of file content"""
    return hashlib.md5(filepath.read_bytes()).hexdigest()

def load_sync_state() -> Dict:
    """Load last sync state"""
    if SYNC_STATE_FILE.exists():
        return json.loads(SYNC_STATE_FILE.read_text())
    return {}

def save_sync_state(state: Dict):
    """Save current sync state"""
    SYNC_STATE_FILE.write_text(json.dumps(state, indent=2))

def detect_conflicts(filepath: Path, state: Dict) -> Optional[str]:
    """Detect if file has conflicts (modified by multiple sources)"""
    key = str(filepath.relative_to(MEMORY_DIR))
    current_hash = get_file_hash(filepath)

    if key not in state:
        return None

    if state[key]["hash"] != current_hash:
        return "modified"

    return None

def sync_memory_files(strategy: str = "last_write_wins") -> Dict:
    """
    Sync all memory/*.md files

    Args:
        strategy: Conflict resolution strategy
            - last_write_wins: Use most recent modification
            - manual: Report conflicts for manual resolution

    Returns:
        Sync report with statistics
    """
    state = load_sync_state()
    report = {
        "timestamp": datetime.now().isoformat(),
        "synced": [],
        "conflicts": [],
        "errors": []
    }

    # Scan all .md files in memory/
    for md_file in MEMORY_DIR.rglob("*.md"):
        if md_file.name.startswith("."):
            continue

        try:
            key = str(md_file.relative_to(MEMORY_DIR))
            current_hash = get_file_hash(md_file)
            mtime = md_file.stat().st_mtime

            conflict = detect_conflicts(md_file, state)

            if conflict and strategy == "manual":
                report["conflicts"].append({
                    "file": key,
                    "type": conflict,
                    "action": "manual_review_required"
                })
            else:
                # Update state
                state[key] = {
                    "hash": current_hash,
                    "mtime": mtime,
                    "last_sync": datetime.now().isoformat()
                }
                report["synced"].append(key)

        except Exception as e:
            report["errors"].append({"file": str(md_file), "error": str(e)})

    save_sync_state(state)

    # Log sync
    log_file = MEMORY_DIR / ".sync-log.jsonl"
    with log_file.open("a") as f:
        f.write(json.dumps(report) + "\n")

    return report

if __name__ == "__main__":
    import sys
    strategy = sys.argv[1] if len(sys.argv) > 1 else "last_write_wins"
    report = sync_memory_files(strategy)
    print(f"Synced: {len(report['synced'])} files")
    print(f"Conflicts: {len(report['conflicts'])} files")
    print(f"Errors: {len(report['errors'])} files")

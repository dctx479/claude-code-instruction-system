#!/usr/bin/env python3
"""Graphiti knowledge graph synchronization - syncs memory data to Graphiti (placeholder)"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

MEMORY_DIR = Path(__file__).parent.parent / "memory"
GRAPHITI_ENABLED = False  # Set to True when Graphiti is configured

def parse_lesson_learned(content: str) -> List[Dict]:
    """Parse lessons-learned.md into structured entities"""
    entities = []
    lines = content.split("\n")

    current_entry = None
    current_section = None

    for line in lines:
        if line.startswith("## [") and "] " in line:
            # New entry
            if current_entry:
                entities.append(current_entry)

            title = line.split("] ", 1)[1] if "] " in line else "Unknown"
            date = line.split("[")[1].split("]")[0] if "[" in line else "Unknown"

            current_entry = {
                "type": "lesson",
                "title": title,
                "date": date,
                "sections": {}
            }
        elif line.startswith("### ") and current_entry:
            current_section = line[4:].strip()
            current_entry["sections"][current_section] = []
        elif line.strip() and current_entry and current_section:
            current_entry["sections"][current_section].append(line.strip())

    if current_entry:
        entities.append(current_entry)

    return entities

def parse_agent_performance(content: str) -> List[Dict]:
    """Parse agent-performance.md into structured metrics"""
    entities = []
    lines = content.split("\n")

    current_agent = None

    for line in lines:
        if line.startswith("### ") and not line.startswith("### 周趋势"):
            agent_name = line[4:].strip()
            current_agent = {
                "type": "agent_baseline",
                "name": agent_name,
                "metrics": {}
            }
            entities.append(current_agent)
        elif "|" in line and current_agent and "指标" not in line and "---" not in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                metric_name = parts[0]
                current_value = parts[1] if len(parts) > 1 else "-"
                current_agent["metrics"][metric_name] = current_value

    return entities

def sync_to_graphiti(dry_run: bool = True) -> Dict:
    """
    Sync memory files to Graphiti knowledge graph

    Args:
        dry_run: If True, only simulate sync without actual API calls

    Returns:
        Sync report
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "graphiti_enabled": GRAPHITI_ENABLED,
        "entities_extracted": 0,
        "entities_synced": 0,
        "errors": []
    }

    if not GRAPHITI_ENABLED:
        report["status"] = "placeholder"
        report["message"] = "Graphiti not configured. Install and configure Graphiti to enable sync."
        return report

    try:
        # Parse lessons-learned.md
        lessons_file = MEMORY_DIR / "lessons-learned.md"
        if lessons_file.exists():
            content = lessons_file.read_text(encoding="utf-8")
            lessons = parse_lesson_learned(content)
            report["entities_extracted"] += len(lessons)

            if not dry_run:
                # TODO: Call Graphiti API to store entities
                # graphiti_client.add_entities(lessons)
                pass

        # Parse agent-performance.md
        perf_file = MEMORY_DIR / "agent-performance.md"
        if perf_file.exists():
            content = perf_file.read_text(encoding="utf-8")
            agents = parse_agent_performance(content)
            report["entities_extracted"] += len(agents)

            if not dry_run:
                # TODO: Call Graphiti API to store entities
                # graphiti_client.add_entities(agents)
                pass

        report["status"] = "success" if not dry_run else "dry_run"
        report["entities_synced"] = report["entities_extracted"] if not dry_run else 0

    except Exception as e:
        report["status"] = "error"
        report["errors"].append(str(e))

    # Log sync
    log_file = MEMORY_DIR / ".graphiti-sync-log.jsonl"
    with log_file.open("a") as f:
        f.write(json.dumps(report) + "\n")

    return report

if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv or not GRAPHITI_ENABLED
    report = sync_to_graphiti(dry_run)
    print(f"Status: {report['status']}")
    print(f"Entities extracted: {report['entities_extracted']}")
    print(f"Entities synced: {report['entities_synced']}")
    if report.get("message"):
        print(f"Message: {report['message']}")

"""Sync engine for context archives to memory/*.md and Graphiti"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

CONTEXT_DIR = Path(".claude/context")
MEMORY_DIR = Path("memory")
LESSONS_FILE = MEMORY_DIR / "lessons-learned.md"

def sync_to_memory(resolution: Dict[str, Any]):
    """Sync resolution to memory/lessons-learned.md"""
    MEMORY_DIR.mkdir(exist_ok=True)

    entry = f"""
## [{datetime.now().strftime('%Y-%m-%d')}] {resolution['id']}

### 问题描述
{resolution['problem']}

### 根本原因
{resolution['root_cause']}

### 解决方案
{resolution['final_fix'][0] if resolution['final_fix'] else 'N/A'}

### 验证方法
{resolution['verification'][0] if resolution['verification'] else 'N/A'}

---
"""

    with open(LESSONS_FILE, 'a', encoding='utf-8') as f:
        f.write(entry)

def sync_to_graphiti(resolution: Dict[str, Any]):
    """Sync resolution to Graphiti (placeholder)"""
    # TODO: Implement Graphiti integration
    pass

def sync_all():
    """Sync all resolutions"""
    res_dir = CONTEXT_DIR / "resolutions"
    if not res_dir.exists():
        return

    for ndjson_file in res_dir.glob("*.ndjson"):
        with open(ndjson_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    res = json.loads(line)
                    sync_to_memory(res)
                    sync_to_graphiti(res)

if __name__ == "__main__":
    sync_all()
    print("✓ Sync complete")

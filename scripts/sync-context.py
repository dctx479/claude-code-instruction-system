#!/usr/bin/env python3
"""Sync context archives to memory/*.md"""
import json
import sys
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

CONTEXT_DIR = Path(".claude/context")
RESOLUTIONS_DIR = CONTEXT_DIR / "resolutions"
MEMORY_DIR = Path("memory")
LESSONS_FILE = MEMORY_DIR / "lessons-learned.md"
ERROR_PATTERNS_FILE = MEMORY_DIR / "error-patterns.md"

def sync_to_lessons_learned():
    """Sync resolutions to lessons-learned.md"""
    if not RESOLUTIONS_DIR.exists():
        print("No resolutions to sync")
        return

    MEMORY_DIR.mkdir(exist_ok=True)

    # Read existing content
    existing = LESSONS_FILE.read_text(encoding="utf-8") if LESSONS_FILE.exists() else "# 经验教训库\n\n"

    # Collect new resolutions
    new_entries = []
    for ndjson_file in sorted(RESOLUTIONS_DIR.glob("*.ndjson")):
        with open(ndjson_file, encoding="utf-8") as f:
            for line in f:
                res = json.loads(line.strip())
                res_id = res.get("id")

                # Skip if already in file
                if res_id in existing:
                    continue

                entry = f"""## [{datetime.now().strftime('%Y-%m-%d')}] {res.get('problem_signature', 'Unknown')} #{res_id}

### 问题描述
{res.get('problem', 'N/A')}

### 根因分析
{res.get('root_cause', 'N/A')}

### 解决方案
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(res.get('final_fix', [])))}

### 为什么有效
{res.get('why_it_works', 'N/A')}

### 验证方法
{chr(10).join(f"- {check}" for check in res.get('verification', []))}

---

"""
                new_entries.append(entry)

    if new_entries:
        with open(LESSONS_FILE, "a", encoding="utf-8") as f:
            f.write("\n".join(new_entries))
        print(f"✅ Synced {len(new_entries)} resolutions to {LESSONS_FILE}")
    else:
        print("No new resolutions to sync")

def sync_to_error_patterns():
    """Sync anti-patterns to error-patterns.md"""
    if not RESOLUTIONS_DIR.exists():
        return

    MEMORY_DIR.mkdir(exist_ok=True)

    existing = ERROR_PATTERNS_FILE.read_text(encoding="utf-8") if ERROR_PATTERNS_FILE.exists() else "# 错误模式库\n\n"

    new_patterns = []
    for ndjson_file in sorted(RESOLUTIONS_DIR.glob("*.ndjson")):
        with open(ndjson_file, encoding="utf-8") as f:
            for line in f:
                res = json.loads(line.strip())
                res_id = res.get("id")

                if res_id in existing:
                    continue

                anti_patterns = res.get('anti_patterns', [])
                if anti_patterns:
                    entry = f"""## {res.get('problem_signature', 'Unknown')} (#{res_id})

**反模式**:
{chr(10).join(f"- ❌ {pattern}" for pattern in anti_patterns)}

---

"""
                    new_patterns.append(entry)

    if new_patterns:
        with open(ERROR_PATTERNS_FILE, "a", encoding="utf-8") as f:
            f.write("\n".join(new_patterns))
        print(f"✅ Synced {len(new_patterns)} anti-patterns to {ERROR_PATTERNS_FILE}")

if __name__ == "__main__":
    print("🔄 Syncing context to memory...")
    sync_to_lessons_learned()
    sync_to_error_patterns()
    print("✅ Sync complete")

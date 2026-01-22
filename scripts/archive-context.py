#!/usr/bin/env python3
"""Context archival script - extracts key information before context compression"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    import anthropic
except ImportError:
    print("❌ Error: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
    sys.exit(1)

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

CONTEXT_DIR = Path(".claude/context")
RESOLUTIONS_DIR = CONTEXT_DIR / "resolutions"

ARCHIVAL_PROMPT = """你是对话归档器，将长对话提炼为可复用的工程上下文。输出两个文件块：

===FILE:index.json===
{
  "context_version": "v2",
  "project": "<项目名>",
  "current_state": "<当前状态>",
  "goals": ["<目标>"],
  "constraints": ["<约束>"],
  "environment": {"os": "<系统>", "runtime": "<运行时>", "tools": ["<工具>"], "paths": ["<路径>"]},
  "verified_facts": ["<已验证事实>"],
  "next_actions": ["<下一步>"],
  "detail_index": {
    "resolutions": [{"id": "res-001", "problem_signature": "<错误关键词>", "summary": "<方案摘要>", "tags": ["<标签>"], "artifacts_touched": ["<文件>"]}]
  }
}
===END_FILE===
===FILE:resolutions.ndjson===
{"id":"res-001","type":"resolution","problem_signature":"<错误关键词>","problem":"<问题描述>","root_cause":"<根本原因>","final_fix":["<步骤>"],"why_it_works":"<原理>","verification":["<验证>"],"anti_patterns":["<反模式>"],"artifacts_touched":["<文件>"],"evidence":{"signals":["<证据>"],"when":"<时间>"}}
===END_FILE===

要求：
1. 提炼试错后的正确路径，不要全量对话
2. problem_signature 用稳定的错误关键词
3. anti_patterns 记录 1-3 条无效尝试
4. artifacts_touched 只写文件路径，不贴代码
5. verified_facts 只记录已确认的事实，不猜测"""

def get_api_key():
    settings_path = Path.home() / ".claude" / "settings.json"
    if settings_path.exists():
        with open(settings_path) as f:
            return json.load(f).get("apiKey")
    return os.getenv("ANTHROPIC_API_KEY")

def archive_conversation(conversation_text: str):
    api_key = get_api_key()
    if not api_key:
        print("❌ Error: No API key found", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    print("🧠 Analyzing conversation...")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        messages=[{"role": "user", "content": f"{ARCHIVAL_PROMPT}\n\n对话内容：\n{conversation_text}"}]
    )

    content = response.content[0].text

    try:
        idx_start = content.find("===FILE:index.json===")
        idx_end = content.find("===END_FILE===", idx_start)
        res_start = content.find("===FILE:resolutions.ndjson===", idx_end)
        res_end = content.find("===END_FILE===", res_start)

        index_json = content[idx_start + 21:idx_end].strip()
        resolutions_ndjson = content[res_start + 29:res_end].strip()

        index_data = json.loads(index_json)

        CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
        RESOLUTIONS_DIR.mkdir(exist_ok=True)

        with open(CONTEXT_DIR / "index.json", "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        resolution_file = RESOLUTIONS_DIR / f"{timestamp}.ndjson"
        with open(resolution_file, "w", encoding="utf-8") as f:
            f.write(resolutions_ndjson)

        print(f"✅ Context archived")
        print(f"   📄 {CONTEXT_DIR / 'index.json'}")
        print(f"   📋 {resolution_file}")
        print(f"\n📊 Project: {index_data.get('project', 'N/A')}")
        print(f"   State: {index_data.get('current_state', 'N/A')}")
        print(f"   Facts: {len(index_data.get('verified_facts', []))}")
        print(f"   Resolutions: {len(index_data.get('detail_index', {}).get('resolutions', []))}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python archive-context.py <conversation_file>")
        sys.exit(1)

    conv_file = Path(sys.argv[1])
    if not conv_file.exists():
        print(f"❌ Error: File not found: {conv_file}", file=sys.stderr)
        sys.exit(1)

    conversation = conv_file.read_text(encoding="utf-8")
    archive_conversation(conversation)

#!/usr/bin/env python3
"""Generate the short agent entry from frontmatter; --check detects drift."""
import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def render(root):
    rows = ["# Agent 路由索引", "", "由 `python scripts/build-agent-index.py` 生成；按任务选择一项，再读取对应文件。", "",
            "| Agent | 用途 | 定义 |", "|---|---|---|"]
    for path in sorted((root / "agents").rglob("*.md")):
        text = path.read_text(encoding="utf-8-sig")
        header = re.match(r"^---\n(.*?)\n---", text, re.S)
        if not header:
            continue
        fields = dict(re.findall(r"^(name|description):\s*(.+)$", header[1], re.M))
        name = fields.get("name", path.stem).strip('\"\'')
        description = fields.get("description", "读取定义确认适用范围").strip('\"\'').replace("|", "\\|")
        # Summary only; complete descriptions remain in the agent file.
        if len(description) > 85:
            description = description[:85] + "…"
        rel = path.relative_to(root / "agents").as_posix()
        rows.append(f"| {name} | {description} | [{rel}]({rel}) |")
    return "\n".join(rows) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path, content = ROOT / "agents/INDEX.md", render(ROOT)
    if args.check:
        if path.read_text(encoding="utf-8") != content:
            print("WARNING: agents/INDEX.md is stale", file=sys.stderr)
            return 1
    else:
        path.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

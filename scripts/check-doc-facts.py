#!/usr/bin/env python3
"""Validate profile/command inventory and generate its single factual summary."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def header(path):
    import yaml
    text = path.read_text(encoding="utf-8-sig")
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not match:
        raise ValueError(f"frontmatter missing: {path}")
    data = yaml.safe_load(match[1])
    if not isinstance(data, dict):
        raise ValueError(f"frontmatter not a mapping: {path}")
    return data


def inspect(root):
    profiles = json.loads((root / "config/profiles.json").read_text(encoding="utf-8"))["profiles"]
    skills = {p.parent.name: header(p) for p in (root / ".claude/skills").glob("*/SKILL.md")}
    agents = {p.relative_to(root / "agents").as_posix() for p in (root / "agents").rglob("*.md")
              if p.read_text(encoding="utf-8-sig").startswith("---\n")}
    commands = [p for p in (root / "commands").rglob("*.md") if p.name != "INDEX.md"]
    for path in commands:
        data = header(path)
        if not isinstance(data.get("description"), str) or not data["description"].strip():
            raise ValueError(f"command description missing: {path}")
        if data.get("disable-model-invocation") is not True:
            raise ValueError(f"command must be explicitly invoked: {path}")
    for kind, inventory in (("skills", set(skills)), ("agents", agents)):
        members = [item for profile in profiles.values() for item in profile[kind]]
        counts = Counter(members)
        if set(members) != inventory or any(n != 1 for n in counts.values()):
            raise ValueError(f"{kind} profile coverage mismatch: missing={sorted(inventory-set(members))}, "
                             f"unknown={sorted(set(members)-inventory)}, duplicates={[x for x,n in counts.items() if n>1]}")
    rows = ["# 能力安装清单", "", "由 `python scripts/check-doc-facts.py --write` 生成。profile 唯一来源为 `config/profiles.json`。", "",
            "| Profile | Skills | Agents | 自动 Skill 描述字符 |", "|---|---:|---:|---:|"]
    for name, profile in profiles.items():
        chars = sum(len(skills[s]["description"]) for s in profile["skills"] if not skills[s].get("disable-model-invocation", False))
        rows.append(f"| {name} | {len(profile['skills'])} | {len(profile['agents'])} | {chars} |")
    rows.extend(["", f"总计：{len(skills)} 个顶层 Skill、{len(agents)} 个 Agent、{len(commands)} 个命令。", "",
                 "字符数来自描述静态统计，不等于 token 数或真实会话 /context 实测。",
                 "新目标默认 core。切换 profile 不删除旧目标文件；旧全量安装需先审阅多余文件。",
                 "Java/PHP 顶层 Skill 通过路径读取嵌套参考，嵌套文件不计为独立注册 Skill。"])
    return "\n".join(rows) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        content = inspect(ROOT)
        destination = ROOT / "docs/CAPABILITY-SUMMARY.md"
        if args.write:
            destination.write_text(content, encoding="utf-8")
        elif not destination.is_file() or destination.read_text(encoding="utf-8") != content:
            raise ValueError("capability summary stale; run --write")
    except (OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        print(f"WARNING: document facts check failed: {exc}", file=sys.stderr)
        return 1
    print("Profile coverage, command metadata and capability facts: PASS")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

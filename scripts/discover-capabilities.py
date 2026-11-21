#!/usr/bin/env python3
"""Read installed metadata and report discovery volume without loading Skill bodies."""
import argparse
import json
from pathlib import Path
import re
import sys


def discover(target):
    import yaml
    skills, agents, warnings = [], [], []
    for kind, paths in (("skills", (target / "skills").glob("*/SKILL.md")), ("agents", (target / "agents").rglob("*.md"))):
        for path in sorted(paths):
            text = path.read_text(encoding="utf-8-sig")
            match = re.match(r"^---\n(.*?)\n---", text, re.S)
            if not match:
                continue
            try:
                data = yaml.safe_load(match[1])
            except yaml.YAMLError:
                warnings.append(dict(path=path.relative_to(target).as_posix(), reason="invalid YAML frontmatter"))
                continue
            if not isinstance(data, dict) or not isinstance(data.get("description"), str):
                continue
            record = dict(name=data.get("name", path.stem), path=path.relative_to(target).as_posix(),
                          description_chars=len(data["description"]), automatic=not data.get("disable-model-invocation", False))
            (skills if kind == "skills" else agents).append(record)
    return dict(skills=skills, agents=agents, warnings=warnings, skill_count=len(skills), agent_count=len(agents),
                automatic_description_chars=sum(row["description_chars"] for row in skills if row["automatic"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=Path.home() / ".claude")
    args = parser.parse_args()
    try:
        result = discover(args.target.resolve())
        print(json.dumps(result, ensure_ascii=False, indent=2))
        for item in result["warnings"]:
            print(f"WARNING: {item['path']}: {item['reason']}", file=sys.stderr)
        return 0
    except (OSError, ValueError, ImportError) as exc:
        print(f"WARNING: capability discovery failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

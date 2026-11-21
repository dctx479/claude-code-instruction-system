#!/usr/bin/env python3
"""Validate repository Agent Skills frontmatter without running skill instructions."""
import argparse
import json
from pathlib import Path
import re
import sys


def audit(root):
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML unavailable; install scripts/requirements-validation.txt in a validation venv") from exc
    records, problems, names = [], [], {}
    warnings = []
    allowed = {"name", "description", "license", "compatibility", "metadata", "allowed-tools",
               "disable-model-invocation", "user-invocable", "argument-hint", "model", "context", "agent", "hooks"}
    for directory in sorted((Path(root) / ".claude/skills").glob("*")):
        if directory.is_dir() and not directory.name.startswith(".") and not (directory / "SKILL.md").is_file():
            problems.append(dict(path=directory.relative_to(root).as_posix(), detail="missing top-level SKILL.md; nested skills are not discoverable"))
    for path in sorted((Path(root) / ".claude/skills").glob("*/SKILL.md")):
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8-sig")
            match = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.S)
            if not match:
                raise ValueError("YAML frontmatter missing")
            data = yaml.safe_load(match[1])
            if not isinstance(data, dict):
                raise ValueError("frontmatter must be a mapping")
            if set(data) - allowed:
                raise ValueError("unsupported fields: " + ", ".join(sorted(set(data) - allowed)))
            for field in ("disable-model-invocation", "user-invocable"):
                if field in data and not isinstance(data[field], bool):
                    raise ValueError(field + " must be a boolean")
                if isinstance(data.get("metadata"), dict) and field in data["metadata"]:
                    raise ValueError(field + " belongs at top level, not metadata")
            name, description = data.get("name"), data.get("description")
            if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
                raise ValueError("name must be a nonempty kebab-case string of at most 64 characters")
            if name != path.parent.name:
                raise ValueError("name does not match the skill directory")
            if name in names:
                raise ValueError("duplicate name: " + names[name])
            names[name] = rel
            if not isinstance(description, str) or not description.strip() or len(description) > 1024 or re.search(r"[<>]", description):
                raise ValueError("description must be nonempty, <=1024 characters, without angle brackets")
            if "metadata" in data and not isinstance(data["metadata"], dict):
                raise ValueError("metadata must be a mapping")
            if "compatibility" in data and not isinstance(data["compatibility"], str):
                raise ValueError("compatibility must be a string")
            if not text[match.end():].strip():
                raise ValueError("skill instructions are empty")
            records.append(dict(path=rel, name=name, description_chars=len(description),
                                automatic=not data.get("disable-model-invocation", False),
                                lines=len(text.splitlines()), body_lines=len(text[match.end():].splitlines())))
            if len(text.splitlines()) > 500:
                warnings.append(dict(path=rel, detail="SKILL.md exceeds 500 lines; move conditional detail into references/"))
        except (OSError, ValueError, yaml.YAMLError) as exc:
            problems.append(dict(path=rel, detail=str(exc)))
    if not records and not problems:
        problems.append(dict(path=".claude/skills", detail="no SKILL.md files found"))
    return dict(skills_checked=len(records) + len(problems), valid=len(records), skills=records,
                problems=problems, warnings=warnings, passed=not problems)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = audit(args.root.resolve())
    except RuntimeError as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Skills: {result['valid']}/{result['skills_checked']} valid")
        for problem in result["problems"]:
            print(f"ERROR: {problem['path']}: {problem['detail']}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning['path']}: {warning['detail']}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

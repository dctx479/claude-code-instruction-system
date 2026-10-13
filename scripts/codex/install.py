#!/usr/bin/env python3
"""Install Taiyi instructions and resource snapshots for Codex (stdlib only)."""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path("taiyi-system/install-manifest.json")
RESOURCE_DIRS = (
    "commands", "agents", "workflows", "docs", "scripts",
    "memory", "templates", "config", ".claude/skills", "specs",
    "tools", "graph", "sync", "recommend", "mcp", "examples", "integrations", "themes",
)
IGNORED = {"__pycache__", ".pytest_cache", "node_modules", ".git", "target"}
GLOBAL_START = b"<!-- taiyi-codex-global:start -->"
GLOBAL_END = b"<!-- taiyi-codex-global:end -->"


def global_entry(codex_home, base):
    """Prepare a managed global block, preserving all other instruction bytes."""
    override = checked_target(codex_home, Path("AGENTS.override.md"))
    name = "AGENTS.override.md" if override.exists() else "AGENTS.md"
    target = checked_target(codex_home, Path(name))
    if target.exists() and not target.is_file():
        raise ValueError(f"Global instruction target is not a file: {target}")
    previous = target.read_bytes() if target.exists() else b""
    block = (GLOBAL_START + b"\n" + (
        "## 太一元系统：全局 Codex 支持\n\n"
        f"在各项目执行任务前，读取 `{base / 'taiyi-system/codex/runtime.md'}`，"
        "并按任务需要加载命令、专家角色与领域资料。\n"
        "目标项目及其更具体的指令优先；修改作用于当前目标项目。\n"
        "可通过 `$taiyi-core` 选择工作流，或直接使用 `$taiyi-review` 等入口。\n"
        "角色资料不自动创建子智能体；Claude Hook、HUD 和后台状态机不生效。\n"
    ).encode("utf-8") + GLOBAL_END)
    if GLOBAL_START in previous or GLOBAL_END in previous:
        if previous.count(GLOBAL_START) != 1 or previous.count(GLOBAL_END) != 1:
            raise ValueError("Malformed Taiyi global instruction markers")
        start = previous.index(GLOBAL_START)
        end = previous.index(GLOBAL_END) + len(GLOBAL_END)
        if end < start:
            raise ValueError("Malformed Taiyi global instruction marker order")
        content = previous[:start] + block + previous[end:]
    else:
        separator = b"" if not previous else (b"\n" if previous.endswith(b"\n") else b"\n\n")
        content = previous + separator + block + b"\n"
    return target, previous, content


def write_global_entry(target, previous, content):
    if previous == content:
        return None
    backup = None
    if target.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        relative = Path("taiyi-backups") / stamp / target.name
        backup = checked_target(target.parent, relative)
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, backup)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    return backup


def skill_entry(name, description, body):
    # JSON strings are also valid YAML scalars; no YAML dependency is needed.
    if not re.fullmatch(r"[a-z0-9-]{1,63}", name):
        raise ValueError(f"Invalid Codex skill name: {name}")
    return (
        f"---\nname: {name}\ndescription: "
        f"{json.dumps(description, ensure_ascii=False)}\n---\n\n{body}\n"
    ).encode("utf-8")


def wrapper(name, description, source):
    resource = f"../../taiyi-system/{source.as_posix()}"
    return skill_entry(name, description, (
        f"# {name}\n\n"
        "先读取相对于本 Skill 目录的 `../../taiyi-system/codex/runtime.md`。\n"
        f"再读取 `{resource}`，按 Codex 运行适配协议执行用户请求。\n\n"
        "原始资料内的相对路径以该资料所在目录为基准；`$ARGUMENTS` 是用户随本 Skill 提供的文本。"
        "Claude 的模型、工具权限、Hook 和斜杠命令不是 Codex 配置。"
        "对用户的目标项目执行工作；资料不自动授予额外的安装、提交、推送或发布权限。"
    ))


def command_descriptions(root):
    descriptions = {}
    for line in (root / "commands/INDEX.md").read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.split("|")]
        if len(cells) >= 6 and cells[1].startswith("`/"):
            descriptions[cells[1].strip("`").lstrip("/")] = cells[3]
    return descriptions


def description_from_source(path):
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
    if match:
        value = match.group(1).strip().strip("\"'")
        if value not in {">", "|", "|-", ">-"}:
            return value[:400]
    return f"使用 {path.parent.name} 领域知识处理相关任务"


def build_plan(root, with_agents=False, with_skills=False, selected_skills=()):
    """Return destination-relative paths and bytes before any filesystem writes."""
    plan = {}

    def add(path, content):
        if path in plan:
            raise ValueError(f"Duplicate installation path: {path}")
        plan[path] = content

    # Preserve script/reference/template paths rather than copying SKILL.md alone.
    for directory in RESOURCE_DIRS:
        for source in sorted((root / directory).rglob("*")):
            if any(part in IGNORED for part in source.relative_to(root).parts):
                continue
            if source.is_symlink():
                raise ValueError(f"Resource symlinks are not supported: {source}")
            if source.is_file() and source.suffix not in {".pyc", ".log"}:
                add(Path("taiyi-system") / source.relative_to(root), source.read_bytes())
    add(Path("taiyi-system/codex/runtime.md"), (root / "codex/runtime.md").read_bytes())
    add(Path("skills/taiyi-core/SKILL.md"), (root / "codex/skills/taiyi-core/SKILL.md").read_bytes())

    descriptions = command_descriptions(root)
    for source in sorted((root / "commands").rglob("*.md")):
        if source.name == "INDEX.md":
            continue
        name = f"taiyi-{source.stem}"
        description = descriptions.get(source.stem, source.stem)
        add(Path("skills") / name / "SKILL.md", wrapper(
            name, f"太一 {source.stem} 工作流：{description}。用于用户请求此工作流时。",
            source.relative_to(root),
        ))

    if with_agents:
        for source in sorted((root / "agents").rglob("*.md")):
            if source.name == "INDEX.md":
                continue
            name = f"taiyi-agent-{source.stem}"
            add(Path("skills") / name / "SKILL.md", wrapper(
                name, f"太一 {source.stem} 专家角色：{description_from_source(source)}",
                source.relative_to(root),
            ))

    sources = list(sorted((root / ".claude/skills").rglob("SKILL.md")))
    available = {source.parent.name for source in sources}
    unknown = set(selected_skills) - available
    if unknown:
        raise ValueError(f"Unknown skills: {', '.join(sorted(unknown))}")
    for source in sources:
        if not with_skills and source.parent.name not in selected_skills:
            continue
        name = f"taiyi-skill-{source.parent.name}"
        add(Path("skills") / name / "SKILL.md", wrapper(
            name, f"太一领域 Skill：{description_from_source(source)}", source.relative_to(root),
        ))
    return plan


def checked_target(base, relative):
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Unsafe installation path: {relative}")
    target = base / relative
    for ancestor in (target, *target.parents):
        if ancestor.is_symlink():
            raise ValueError(f"Refusing to write through symlink: {ancestor}")
        if ancestor != target and ancestor.exists() and not ancestor.is_dir():
            raise ValueError(f"Parent is not a directory: {ancestor}")
    return target


def install(plan, base, force=False, dry_run=False):
    manifest_target = checked_target(base, MANIFEST)
    previous = []
    if manifest_target.exists():
        previous = json.loads(manifest_target.read_text(encoding="utf-8")).get("files", [])
    # Keep earlier optional skills and their resources managed on partial updates.
    managed = sorted(set(previous) | {path.as_posix() for path in plan})
    plan = dict(plan)
    plan[MANIFEST] = (json.dumps({"version": 1, "files": managed},
                                 ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    changes = []
    conflicts = []
    for relative, content in sorted(plan.items()):
        target = checked_target(base, relative)
        if target.exists():
            if not target.is_file():
                raise ValueError(f"Destination is not a file: {target}")
            if target.read_bytes() == content:
                continue
            conflicts.append(relative)
        changes.append((relative, content))
    if conflicts and not force:
        sample = "\n".join(str(base / path) for path in conflicts[:8])
        raise ValueError(f"Existing files differ ({len(conflicts)}); no files changed:\n{sample}\n"
                         "Review them, then use --force to back up and replace.")
    if dry_run:
        return len(changes), None
    backup = None
    if conflicts:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = base / "taiyi-backups" / stamp
        for relative in conflicts:
            target = checked_target(base, relative)
            copy = checked_target(backup, relative)
            copy.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, copy)
    for relative, content in changes:
        target = checked_target(base, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    return len(changes), backup


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--project", type=Path, help="Target project (default: this repository)")
    scope.add_argument("--user", action="store_true", help="Install into ~/.agents for all projects")
    scope.add_argument("--global", dest="global_install", action="store_true",
                       help="Install user skills and enable global instructions (preserve and back up existing rules)")
    parser.add_argument("--with-agents", action="store_true", help="Expose expert roles as skills")
    parser.add_argument("--with-skills", action="store_true", help="Expose all bundled domain skills")
    parser.add_argument("--skill", action="append", default=[], help="Expose a domain skill by folder name (repeatable)")
    parser.add_argument("--force", action="store_true", help="Back up differing files before replacing")
    parser.add_argument("--dry-run", action="store_true", help="Validate and report without writing")
    args = parser.parse_args(argv)
    # Do not resolve symlinks: preflight must detect and reject them.
    project = Path(os.path.abspath(args.project or REPO_ROOT))
    base = (Path.home() if args.user or args.global_install else project) / ".agents"
    try:
        plan = build_plan(REPO_ROOT, args.with_agents, args.with_skills, args.skill)
        entry = None
        if args.global_install:
            codex_home = Path(os.path.abspath(os.environ.get("CODEX_HOME") or Path.home() / ".codex"))
            entry = global_entry(codex_home, base)
        # Validate both destinations before either is modified.
        install(plan, base, args.force, dry_run=True)
        count, backup = install(plan, base, args.force, args.dry_run)
        global_backup = write_global_entry(*entry) if entry and not args.dry_run else None
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Installation failed: {error}", file=sys.stderr)
        return 1
    skill_count = sum(path.parts[0] == "skills" for path in plan)
    print(f"{'Dry run' if args.dry_run else 'Installed'}: {base}")
    print(f"Skills: {skill_count}; {'planned' if args.dry_run else 'changed'} files: {count}")
    if backup:
        print(f"Backup: {backup}")
    if entry:
        print(f"Global instructions{' (planned)' if args.dry_run else ''}: {entry[0]}")
    if global_backup:
        print(f"Global instructions backup: {global_backup}")
    print("Use $taiyi-core or $taiyi-review in Codex. No config.toml, credentials or hooks changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

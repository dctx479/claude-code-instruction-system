#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太一元系统全局安装脚本
版本: 1.0.0
规范: specs/SPEC-global-install.md

把本仓库同步到 ~/.claude/ 并把 hooks/hooks.json 合并进 ~/.claude/settings.json。
可重复执行；覆盖前自动备份；不删除目标目录中的任何文件。

用法:
    python scripts/install-global.py --dry-run          # 只看计划
    python scripts/install-global.py                    # 安装到 ~/.claude
    python scripts/install-global.py --components hooks,commands
    python scripts/install-global.py --target /tmp/sandbox/.claude
"""

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Windows 上输出被管道/重定向时默认用 GBK 编码，遇到 ✓ ⚠ 等字符会直接抛 UnicodeEncodeError
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure") and not _stream.isatty():
        _stream.reconfigure(encoding="utf-8", errors="replace")

OVERWRITE = "overwrite"   # 目标不同则备份后覆盖
KEEP = "keep"             # 目标已存在则不动（有状态文件）
FLATTEN = "flatten"       # 覆盖，且去掉子目录层级
GLOBAL_RULES = "global-rules"  # 仅迁移已知旧版或托管入口，保护个人指令
MANAGED_GLOBAL = "<!-- taiyi:managed-global -->"
# 2026-11-19 的项目 CLAUDE.md；统一换行后匹配，避免误覆盖用户编辑。
LEGACY_CORE_SHA256 = "ecc8147313b4132581f4cb20f908305f29b705687217c00ed24feb61582684e0"

# 组件 → [(源, 目标, 策略)]
COMPONENTS = {
    "core": [("config/claude-global.md", "CLAUDE.md", GLOBAL_RULES)],
    "agents": [("agents", "agents", OVERWRITE)],
    # 拍平安装：commands/general/ralph.md → commands/ralph.md。
    # 保留子目录的话 Claude Code 会把命令注册成 /general:ralph，而文档和 CLAUDE.md 用的是 /ralph
    "commands": [("commands", "commands", FLATTEN)],
    "hooks": [
        ("hooks", "hooks", OVERWRITE),
        ("scripts", "scripts", OVERWRITE),
        ("config", "config", OVERWRITE),
    ],
    "skills": [(".claude/skills", "skills", OVERWRITE)],
    "statusline": [
        (".claude/statusline", "statusline", OVERWRITE),
        (".claude/hud-config.json", "hud-config.json", KEEP),
    ],
    "knowledge": [
        ("workflows", "workflows", OVERWRITE),
        ("docs", "docs", OVERWRITE),
        ("specs", "specs", OVERWRITE),
        ("memory", "memory", KEEP),
        (".claude/reference", "reference", OVERWRITE),
        (".claude/prompts", "prompts", OVERWRITE),
    ],
}

# 任何位置都排除
EXCLUDE_NAMES = ["__pycache__", "*.pyc", "*.pyo", "*.log", "*.tmp", ".DS_Store", "Thumbs.db"]
# 按「目标相对路径」排除
EXCLUDE_DEST = [
    "commands/INDEX.md",          # 否则会被注册成 /INDEX 命令
    "memory/ralph-state.json",    # 项目级运行态
    "memory/.*",                  # 同步引擎的本地状态
]
# 即使所在目录是覆盖策略，这些有状态文件也只在缺失时复制
KEEP_DEST = ["config/port-registry.json"]

# settings.json 中属于本系统的 hook 条目标记
OWN_HOOK_MARKERS = ("/.claude/hooks/", "/.claude/scripts/")
STATUSLINE_COMMAND = 'bash "$HOME/.claude/statusline/hud.sh" render'
STATUSLINE_MARKER = "/.claude/statusline/hud.sh"


def excluded(rel_dest: str, name: str) -> bool:
    if any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE_NAMES):
        return True
    return any(fnmatch.fnmatch(rel_dest, pat) for pat in EXCLUDE_DEST)


def iter_files(src: Path, dest_rel: str):
    """产出 (源文件, 目标相对路径)。"""
    if src.is_file():
        yield src, dest_rel
        return
    for root, dirs, files in os.walk(src):
        dirs[:] = sorted(d for d in dirs if not any(fnmatch.fnmatch(d, p) for p in EXCLUDE_NAMES))
        for name in sorted(files):
            path = Path(root) / name
            rel = (Path(dest_rel) / path.relative_to(src)).as_posix()
            if not excluded(rel, name):
                yield path, rel


def same_content(a: Path, b: Path) -> bool:
    try:
        return a.stat().st_size == b.stat().st_size and a.read_bytes() == b.read_bytes()
    except OSError:
        return False


class Installer:
    def __init__(self, target: Path, dry_run: bool, replace_global_rules: bool = False):
        self.target = target
        self.dry_run = dry_run
        self.replace_global_rules = replace_global_rules
        self.backup_dir = target / "backups" / ("taiyi-install-" + time.strftime("%Y%m%d-%H%M%S"))
        self.stats = {"copied": 0, "updated": 0, "unchanged": 0, "kept": 0, "failed": 0}
        self.problems = []

    def backup(self, dest: Path, rel: str) -> None:
        if self.dry_run:
            return
        bak = self.backup_dir / rel
        bak.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dest, bak)

    def copy_file(self, src: Path, rel: str, policy: str) -> None:
        dest = self.target / rel
        if any(fnmatch.fnmatch(rel, pat) for pat in KEEP_DEST):
            policy = KEEP
        if dest.exists():
            if same_content(src, dest):
                self.stats["unchanged"] += 1
                return
            if policy == GLOBAL_RULES and not self.replace_global_rules:
                content = dest.read_bytes().replace(b"\r\n", b"\n")
                known_legacy = hashlib.sha256(content).hexdigest() == LEGACY_CORE_SHA256
                managed = content.startswith(MANAGED_GLOBAL.encode("utf-8"))
                if not known_legacy and not managed:
                    self.stats["kept"] += 1
                    print("WARNING: 保留自定义 CLAUDE.md；先审阅差异，明确要替换时使用 --replace-global-rules。")
                    return
            if policy == KEEP:
                self.stats["kept"] += 1
                return
            action = "updated"
        else:
            action = "copied"

        if self.dry_run:
            print(f"  [{action}] {rel}")
            self.stats[action] += 1
            return
        try:
            if action == "updated":
                self.backup(dest, rel)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            self.stats[action] += 1
        except OSError as exc:
            # 不静默吞错：单个文件失败（例如被杀毒软件拦截）要报告，但不中断其余文件
            self.stats["failed"] += 1
            self.problems.append(f"复制失败 {rel}: {exc}")
            print(f"⚠️ WARNING: 复制失败 {rel}: {exc}", file=sys.stderr)

    def install_files(self, components) -> None:
        for comp in components:
            for src_rel, dest_rel, policy in COMPONENTS[comp]:
                src = REPO / src_rel
                if not src.exists():
                    self.problems.append(f"源不存在: {src_rel}")
                    print(f"⚠️ WARNING: 源不存在，跳过: {src_rel}", file=sys.stderr)
                    continue
                seen = {}
                for path, rel in iter_files(src, dest_rel):
                    if policy == FLATTEN:
                        rel = f"{dest_rel}/{path.name}"
                        if rel in seen:
                            self.problems.append(f"拍平后重名: {path} 与 {seen[rel]}")
                            continue
                        seen[rel] = path
                    self.copy_file(path, rel, OVERWRITE if policy == FLATTEN else policy)

    # ── settings.json ────────────────────────────────────────────────────

    def load_settings(self) -> dict:
        path = self.target / "settings.json"
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            sys.exit(f"❌ 现有 {path} 无法解析（{exc}），已中止，未做任何修改。")
        if not isinstance(data, dict):
            sys.exit(f"❌ 现有 {path} 顶层不是 JSON 对象，已中止，未做任何修改。")
        return data

    @staticmethod
    def is_own_group(group) -> bool:
        handlers = group.get("hooks", []) if isinstance(group, dict) else []
        return any(
            isinstance(h, dict) and any(m in str(h.get("command", "")) for m in OWN_HOOK_MARKERS)
            for h in handlers
        )

    def merge_settings(self, settings: dict, components) -> dict:
        merged = json.loads(json.dumps(settings))  # 深拷贝

        if "hooks" in components:
            ours = json.loads((REPO / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
            hooks = merged.get("hooks")
            if not isinstance(hooks, dict):
                hooks = {}
            # 先移除所有事件里本系统的旧条目（事件迁移时不留残余），再写入当前版本
            for event in list(hooks):
                groups = hooks[event] if isinstance(hooks[event], list) else []
                remaining = [g for g in groups if not self.is_own_group(g)]
                if remaining:
                    hooks[event] = remaining
                else:
                    del hooks[event]
            for event, groups in ours.items():
                hooks.setdefault(event, []).extend(groups)
            merged["hooks"] = hooks

        if "statusline" in components:
            current = merged.get("statusLine")
            current_cmd = current.get("command", "") if isinstance(current, dict) else ""
            if not current or STATUSLINE_MARKER in current_cmd:
                merged["statusLine"] = {"type": "command", "command": STATUSLINE_COMMAND}
            else:
                print(f"  [保留] 已有自定义 statusLine，未改动: {current_cmd}")

        return merged

    def write_settings(self, old: dict, new: dict) -> None:
        path = self.target / "settings.json"
        if old == new:
            print("  settings.json: 无变化")
            return
        changed = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
        print(f"  settings.json: 更新键 {changed}")
        if self.dry_run:
            return
        if path.exists():
            self.backup(path, "settings.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".taiyi-new")
        tmp.write_text(json.dumps(new, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(tmp, path)

    # ── 自检 ─────────────────────────────────────────────────────────────

    def verify(self, settings: dict) -> None:
        for event, groups in (settings.get("hooks") or {}).items():
            for group in groups:
                for handler in group.get("hooks", []):
                    cmd = str(handler.get("command", ""))
                    if not any(m in cmd for m in OWN_HOOK_MARKERS):
                        continue
                    match = re.search(r'\$HOME/\.claude/([^"\s]+)', cmd)
                    if match and not (self.target / match.group(1)).is_file():
                        self.problems.append(f"{event}: hook 脚本缺失 {match.group(1)}")
                    timeout = handler.get("timeout")
                    if isinstance(timeout, (int, float)) and timeout > 600:
                        self.problems.append(f"{event}: timeout={timeout} 看起来是毫秒，单位应为秒")
        status_cmd = (settings.get("statusLine") or {}).get("command", "")
        if STATUSLINE_MARKER in status_cmd and not (self.target / "statusline" / "hud.sh").is_file():
            self.problems.append("statusLine 指向的 statusline/hud.sh 缺失")


def main() -> int:
    parser = argparse.ArgumentParser(description="把太一元系统安装/同步到全局 ~/.claude")
    parser.add_argument("--target", default=str(Path.home() / ".claude"), help="目标目录（默认 ~/.claude）")
    parser.add_argument("--components", default=",".join(COMPONENTS),
                        help="逗号分隔: " + ",".join(COMPONENTS))
    parser.add_argument("--dry-run", action="store_true", help="只打印计划，不写入")
    parser.add_argument("--replace-global-rules", action="store_true",
                        help="显式授权备份并替换自定义全局 CLAUDE.md（仅 core 组件）")
    args = parser.parse_args()

    components = [c.strip() for c in args.components.split(",") if c.strip()]
    unknown = [c for c in components if c not in COMPONENTS]
    if unknown:
        parser.error(f"未知组件: {unknown}")

    target = Path(args.target).expanduser().resolve()
    installer = Installer(target, args.dry_run, args.replace_global_rules)

    print(f"源:   {REPO}")
    print(f"目标: {target}" + ("   (dry-run，不写入)" if args.dry_run else ""))
    print(f"组件: {', '.join(components)}")
    if target != (Path.home() / ".claude").resolve():
        print("注意: hook 命令固定指向 $HOME/.claude，非默认目标仅用于沙箱测试（需同时设置 HOME）。")
    if shutil.which("bash") is None:
        print("⚠️ WARNING: PATH 中找不到 bash，hooks 无法运行（Windows 需要安装 Git Bash）。", file=sys.stderr)

    old_settings = installer.load_settings()   # 先校验，非法则在任何写入之前中止

    print("\n[1/3] 复制文件")
    installer.install_files(components)
    s = installer.stats
    print(f"  新增 {s['copied']}，更新 {s['updated']}，未变 {s['unchanged']}，"
          f"保留已有 {s['kept']}，失败 {s['failed']}")

    print("\n[2/3] 合并 settings.json")
    new_settings = installer.merge_settings(old_settings, components)
    installer.write_settings(old_settings, new_settings)

    print("\n[3/3] 自检")
    if not args.dry_run:
        installer.verify(installer.load_settings())
    if installer.problems:
        for problem in installer.problems:
            print(f"  ❌ {problem}")
    else:
        print("  ✓ 通过" if not args.dry_run else "  (dry-run 跳过)")

    if not args.dry_run and installer.backup_dir.exists():
        print(f"\n被覆盖文件的备份: {installer.backup_dir}")
    if not args.dry_run:
        print("\n提示: 已运行的 Claude Code 会话不会热加载新 hooks，重启会话后生效（/hooks 可查看已加载项）。")
    return 1 if installer.problems else 0


if __name__ == "__main__":
    sys.exit(main())

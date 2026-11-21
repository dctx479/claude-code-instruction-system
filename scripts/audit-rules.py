#!/usr/bin/env python3
"""Read-only, standard-library rule checks. Semantic advice requires human review."""
import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

NAMES = {"AGENTS.md", "AGENTS.override.md", "CLAUDE.md", "CLAUDE.local.md"}
SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", "target", "backups"}
IMPORT = re.compile(r"(?:^|\s)@((?:\.?\.?/)?[\w./-]+\.md)\b")
INLINE = re.compile(r"`([^`\n]+)`")
STALE_SECTION = re.compile(r"CLAUDE\.md[`\s]*(?:§\s*[\d一二三四五六七八九十百零〇IVXivx]+|第\s*[\d一二三四五六七八九十百零〇IVXivx]+\s*[节章])")


def candidates(root):
    try:
        result = subprocess.run(["git", "-C", str(root), "ls-files", "--cached", "--others",
                                 "--exclude-standard", "-z"], capture_output=True, check=True)
        # Git paths use UTF-8 independently of the terminal locale.
        return [root / p for p in result.stdout.decode("utf-8").split("\0") if p]
    except (OSError, subprocess.CalledProcessError):
        return [p for p in root.rglob("*") if not SKIP.intersection(p.relative_to(root).parts)]


def is_rule(path, root):
    rel = path.relative_to(root).as_posix()
    return path.name in NAMES or (".claude/rules/" in rel and path.suffix == ".md") or rel == "config/claude-global.md"


def audit(root, global_file=None):
    root = Path(root).resolve()
    findings, inventory, texts, visiting = [], [], {}, set()

    def label(path):
        return path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)

    def add(level, code, path, line, detail):
        findings.append(dict(level=level, code=code, path=label(path), line=line, detail=detail))

    def resolve(path, ref):
        # Markdown links resolve from the file. Root-relative rule prose also occurs;
        # accept either when one exists, without declaring contextual paths obsolete.
        choices = [(path.parent / ref).resolve(), (root / ref).resolve()]
        return next((p for p in choices if p.exists()), choices[0])

    def read(path, imported=False):
        path = path.resolve()
        if path in visiting:
            add("error", "import-cycle", path, 1, "cyclic @ import")
            return
        if path in texts:
            return
        if not path.is_relative_to(root):
            add("review", "external-import", path, 1, "outside repository; not read (human confirmation required)")
            return
        try:
            raw = path.read_bytes()
            content = raw.decode("utf-8-sig")
        except (OSError, UnicodeError) as exc:
            add("error", "read", path, 1, str(exc))
            return
        texts[path] = content
        lines = content.splitlines()
        inventory.append(dict(path=label(path), lines=len(lines), bytes=len(raw), imported=imported))
        limit = 60 if label(path) == "config/claude-global.md" else 200
        if len(lines) > limit:
            add("warning", "line-budget", path, 1, f"{len(lines)} lines > local budget {limit}")
        if len(raw) >= 29491:
            add("warning", "byte-budget", path, 1, f"{len(raw)} bytes; near/exceeds 32 KiB")
        visiting.add(path)
        fenced = False
        for number, line in enumerate(lines, 1):
            if re.match(r"\s*(```|~~~)", line):
                fenced = not fenced
                continue
            if not fenced:
                for ref in IMPORT.findall(line):
                    target = (path.parent / ref).resolve()
                    if not target.exists():
                        add("error", "missing-import", path, number, ref)
                    else:
                        read(target, True)
                for token in INLINE.findall(line) + re.findall(r"\]\(([^)\s]+)\)", line):
                    if (("/" not in token and not re.search(r"\.(md|py|sh|json|toml|ya?ml)$", token)) or
                            " " in token or "://" in token or
                            token.startswith(("/", "~", "$", "@")) or
                            re.search(r"[{}<>*|]", token)):
                        continue
                    target = resolve(path, token.split("#")[0])
                    if not target.exists():
                        add("review", "path-unresolved", path, number,
                            f"{token}: no file/root-relative match; confirm context before deletion")
                    elif target.name == "INDEX.md":
                        count = len(target.read_text(encoding="utf-8-sig").splitlines())
                        if count > 150:
                            add("warning", "linked-entry-budget", path, number,
                                f"{token}: {count} lines > on-demand entry budget 150")
            # Check only explicit invocations, never execute commands from instructions.
            commands = INLINE.findall(line) if not fenced else [line.strip()]
            for command in commands:
                check_command(command, path, number)
        visiting.remove(path)

    def check_command(command, path, number):
        try:
            parts = shlex.split(command, posix=True)
        except ValueError:
            return
        if not parts:
            return
        if parts[0] in {"npm", "pnpm", "yarn"}:
            # Resolve nearest package.json; do not mistake a subproject's scripts
            # for commands available in the root.
            scope = path.parent
            while scope != root and not (scope / "package.json").is_file():
                scope = scope.parent
            manifest = scope / "package.json"
            if not manifest.is_file():
                add("review", "command-unresolved", path, number,
                    f"{command}: no package.json in instruction scope; confirm target project")
                return
            script = parts[2] if len(parts) > 2 and parts[1] == "run" else (
                parts[1] if len(parts) > 1 and parts[1] in {"test", "build", "lint", "typecheck"} else None)
            if script:
                try:
                    data = json.loads(manifest.read_text(encoding="utf-8-sig"))
                    if script not in data.get("scripts", {}):
                        add("error", "missing-script", path, number, f"{manifest.name}: scripts.{script} absent")
                except (ValueError, AttributeError) as exc:
                    add("error", "manifest", path, number, str(exc))
        elif parts[0] in {"python", "python3", "bash"} and len(parts) > 1:
            script = parts[1]
            if script.endswith((".py", ".sh")) and not re.search(r"[$~{}<>*]", script):
                if not resolve(path, script).is_file():
                    add("error", "missing-command-file", path, number, script)

    for path in sorted(set(candidates(root))):
        if path.is_file() and is_rule(path, root):
            read(path)
        if path.is_file() and path.suffix == ".md" and not {"reports", "archive", "hud"}.intersection(path.relative_to(root).parts) and (
                is_rule(path, root) or path.relative_to(root).parts[0] in {"docs", "agents", "commands", "workflows"}):
            for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
                if STALE_SECTION.search(line):
                    add("error", "stale-section", path, number, "obsolete CLAUDE.md section reference; link to the current source")
    # Budget only root -> directory chains, not the sum of unrelated subtrees.
    agent_dirs = {p.parent for p in texts if p.name in {"AGENTS.md", "AGENTS.override.md"}}
    for directory in sorted(agent_dirs):
        chain, scope = [], directory
        while scope.is_relative_to(root):
            chosen = next((p for p in (scope / "AGENTS.override.md", scope / "AGENTS.md") if p in texts), None)
            if chosen:
                chain.append(chosen)
            if scope == root:
                break
            scope = scope.parent
        size = sum(len(p.read_bytes()) for p in chain)
        if size >= 29491:
            add("warning", "agent-chain-budget", directory, 1, f"{size} bytes in effective repository chain (default budget 32768)")
    if global_file is not None:
        global_file = Path(global_file).expanduser().resolve()
        try:
            global_text = global_file.read_text(encoding="utf-8-sig").strip()
            for path, content in texts.items():
                if path.name in NAMES and content.strip() == global_text:
                    add("warning", "global-duplicate", path, 1, "identical to explicitly supplied global rules")
        except (OSError, UnicodeError) as exc:
            add("error", "global-read", global_file, 1, str(exc))
    return {"files": inventory, "findings": findings,
            "limitations": ["Read-only; no commands executed or files modified.",
                            "No semantic deletion advice; review findings require human context.",
                            "Budgets cover repository rules only; external/global instructions may add context.",
                            "Command checks support explicit npm/pnpm/yarn scripts and local python/bash files only."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--global-file", type=Path, help="opt-in comparison; never scans HOME implicitly")
    parser.add_argument("--strict", action="store_true", help="fail on budget warnings as well as errors")
    parser.add_argument("--json", action="store_true", help="structured report on stdout")
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error("--root must be an existing directory")
    result = audit(args.root, args.global_file)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Lines  Bytes  Rule file")
        for entry in result["files"]:
            print(f"{entry['lines']:5} {entry['bytes']:6}  {entry['path']}")
        for item in result["findings"]:
            print(f"{item['level'].upper()}: {item['path']}:{item['line']} [{item['code']}] {item['detail']}")
        print(f"{len(result['files'])} files; {len(result['findings'])} findings")
        print("\n".join(result["limitations"]))
    return int(any(f["level"] == "error" or (args.strict and f["level"] == "warning") for f in result["findings"]))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

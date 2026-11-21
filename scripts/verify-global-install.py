#!/usr/bin/env python3
"""Compare managed install files without writing to the real target or running a model."""
import argparse
import fnmatch
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

DEFAULT_COMPONENTS = "core,agents,commands,hooks,skills,knowledge"


def load_installer(repo):
    spec = importlib.util.spec_from_file_location("taiyi_verify_installer", repo / "scripts/install-global.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(repo, target, components, smoke_hook=False, bash=None):
    repo, target = Path(repo).resolve(), Path(target).resolve()
    installer = load_installer(repo)
    problems, seen, skipped = [], {}, 0
    for component in components:
        if component not in installer.COMPONENTS:
            raise ValueError(f"unknown component: {component}")
        for source, destination, policy in installer.COMPONENTS[component]:
            if policy == installer.KEEP:
                skipped += 1
                continue  # never assume the user's evolving knowledge must equal the source
            src = repo / source
            if not src.exists():
                problems.append(f"source missing: {source}")
                continue
            for path, rel in installer.iter_files(src, destination):
                if policy == installer.FLATTEN:
                    rel = f"{destination}/{path.name}"
                if any(fnmatch.fnmatch(rel, pattern) for pattern in installer.KEEP_DEST):
                    skipped += 1
                    continue
                if rel in seen and seen[rel] != path:
                    problems.append(f"destination collision: {rel}")
                    continue
                seen[rel] = path
                dest = target / rel
                if not dest.is_file():
                    problems.append(f"installed file missing: {rel}")
                elif not installer.same_content(path, dest):
                    problems.append(f"content differs: {rel} (review customization before replacing)")
    settings_file = target / "settings.json"
    try:
        settings = json.loads(settings_file.read_text(encoding="utf-8-sig")) if settings_file.exists() else {}
        if not isinstance(settings, dict):
            raise ValueError("settings must be an object")
        expected = installer.Installer(target, True).merge_settings(settings, components)
        if expected != settings:
            problems.append("managed settings are not synchronized")
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        problems.append(f"cannot verify settings: {exc}")

    smoke = "not requested"
    if smoke_hook:
        bash = bash or os.environ.get("TAIYI_TEST_BASH")
        if not bash:
            git_bash = Path("C:/Program Files/Git/bin/bash.exe")
            bash = str(git_bash) if os.name == "nt" and git_bash.is_file() else shutil.which("bash")
        if not bash:
            smoke = "FAIL: Bash unavailable"
        else:
            try:
                with tempfile.TemporaryDirectory(prefix="taiyi-installed-smoke-") as directory:
                    env = dict(os.environ, HOME=Path(directory).as_posix(),
                               KEYWORDS_FILE=str(target / "config/keywords.json"), PYTHONIOENCODING="cp1252")
                    event = dict(prompt="Please debug this bug", session_id="installed-smoke", cwd=str(repo))
                    process = subprocess.run([bash, str(target / "hooks/intent-detector.sh")],
                                             input=json.dumps(event), env=env, cwd=repo, capture_output=True,
                                             text=True, encoding="utf-8", timeout=20)
                    if process.returncode or process.stderr:
                        raise ValueError(f"exit={process.returncode}; {process.stderr.strip()}")
                    data = json.loads(process.stdout.split(": ", 1)[1])
                    state = Path(directory) / ".claude/intent-state.json"
                    session_files = list((Path(directory) / ".claude/intent-sessions").glob("*.json"))
                    if data.get("agent") != "debugger" or not state.is_file() or len(session_files) != 1:
                        raise ValueError("unexpected routing context or isolated state")
                    if json.loads(state.read_text(encoding="utf-8")) != data:
                        raise ValueError("stdout and state disagree")
                smoke = "PASS (temporary HOME; real user state untouched)"
            except (OSError, ValueError, IndexError, subprocess.TimeoutExpired) as exc:
                smoke = f"FAIL: {exc}"
        if smoke.startswith("FAIL"):
            problems.append("installed Hook smoke: " + smoke)
    return dict(files_checked=len(seen), stateful_sources_skipped=skipped,
                hook_smoke=smoke, problems=problems, passed=not problems)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--target", type=Path, default=Path.home() / ".claude")
    parser.add_argument("--components", default=DEFAULT_COMPONENTS)
    parser.add_argument("--smoke-hook", action="store_true", help="run installed Hook with temporary HOME")
    args = parser.parse_args()
    if not (args.repo / "AGENTS.md").is_file():
        parser.error("--repo must identify the source repository, not an installed copy")
    components = [c.strip() for c in args.components.split(",") if c.strip()]
    if not components:
        parser.error("select at least one component")
    try:
        result = verify(args.repo, args.target, components, args.smoke_hook)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

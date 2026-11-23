#!/usr/bin/env python3
"""Save/verify a per-worktree handoff. Exit 0 valid, 2 absent, 1 damaged/stale."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import shutil
import subprocess
import sys
import tempfile


def git_environment():
    # Hook-local GIT_DIR/GIT_WORK_TREE must not redirect state to another repository.
    return {key: value for key, value in os.environ.items() if key not in {
        "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM"}}


def git(root, *arguments):
    executable = shutil.which("git")
    if not executable:
        raise ValueError("git executable unavailable")
    return subprocess.run([executable, "-C", str(root), *arguments], env=git_environment(),
                          capture_output=True, text=True, encoding="utf-8", check=True)


def worktree_root(root):
    result = git(Path(root).resolve(), "rev-parse", "--show-toplevel")
    return Path(result.stdout.strip()).resolve()


def location(root):
    root = worktree_root(root)
    result = git(root, "rev-parse", "--git-path", "taiyi/checkpoint.json")
    path = Path(result.stdout.strip())
    return path if path.is_absolute() else root / path


def digest(root, name):
    # Windows TEMP may use an 8.3 alias; normalize both sides before containment.
    root = Path(root).resolve()
    if not isinstance(name, str) or not name or Path(name).is_absolute() or PureWindowsPath(name).drive:
        raise ValueError("checkpoint paths must be repository relative")
    if any(re.fullmatch(r"(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", part, re.I)
           for part in PureWindowsPath(name).parts):
        raise ValueError("checkpoint path is a reserved device name")
    path = (root / name).resolve()
    if not path.is_relative_to(root) or ".git" in path.relative_to(root).parts:
        raise ValueError("checkpoint path outside permitted worktree")
    if not path.is_file():
        raise ValueError("checkpoint artifact must be a regular file")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(data):
    if not isinstance(data, dict) or type(data.get("version")) is not int or data["version"] != 1:
        raise ValueError("unsupported checkpoint schema")
    if not isinstance(data.get("goal"), str) or not data["goal"].strip():
        raise ValueError("goal is required")
    for key in ("done", "next", "evidence"):
        if not isinstance(data.get(key), list) or any(not isinstance(x, str) for x in data[key]):
            raise ValueError(key + " must be an array of strings")
    if not isinstance(data.get("files_sha256"), dict):
        raise ValueError("files_sha256 must be a mapping")
    for name, value in data["files_sha256"].items():
        if not isinstance(name, str) or not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("files_sha256 needs relative names and SHA-256 hex values")


def save(root, data):
    root = worktree_root(root)
    if not isinstance(data, dict):
        raise ValueError("checkpoint input must be an object")
    data = dict(data, version=1, created_at=datetime.now(timezone.utc).isoformat())
    files = data.pop("files", [])
    if not isinstance(files, list):
        raise ValueError("files must be an array")
    data["files_sha256"] = {name: digest(root, name) for name in files}
    validate(data)
    path = location(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    return path


def verify(root):
    root = worktree_root(root)
    path = location(root)
    if not path.exists():
        return 2
    data = json.loads(path.read_text(encoding="utf-8"))
    validate(data)
    for name, expected in data["files_sha256"].items():
        if digest(root, name) != expected:
            raise ValueError("checkpoint file changed: " + name)
    return 0


def review(root, checkpoint_path=None):
    """
    交互式审查检查点状态

    返回四种状态的文件列表:
    - verified: 验证通过 (✅)
    - missing: 文件缺失 (⚠️)
    - modified: hash 不匹配 (⛔)
    - new: 新文件未在检查点中 (🆕)
    """
    root = worktree_root(root)
    path = checkpoint_path or location(root)

    if not path.exists():
        print("ERROR: No checkpoint found", file=sys.stderr)
        return 1

    data = json.loads(path.read_text(encoding="utf-8"))
    validate(data)

    # 收集状态
    verified = []
    missing = []
    modified = []

    for name, expected_hash in data["files_sha256"].items():
        file_path = root / name

        if not file_path.exists():
            missing.append(name)
        else:
            try:
                actual_hash = digest(root, name)
                if actual_hash == expected_hash:
                    verified.append(name)
                else:
                    modified.append((name, expected_hash, actual_hash))
            except Exception as e:
                missing.append(name)

    # 查找新文件（git status 中的新文件）
    new_files = []
    try:
        result = git(root, "status", "--porcelain=v1", "--untracked-files=all")
        for line in result.stdout.splitlines():
            if line.startswith("??"):
                file_name = line[3:].strip()
                if file_name not in data["files_sha256"]:
                    new_files.append(file_name)
    except:
        pass

    # 输出报告
    print(f"Checkpoint Review: {path.name}")
    print(f"Created: {data.get('created_at', 'unknown')}")
    print(f"Goal: {data.get('goal', 'N/A')}")
    print()
    print("Files Status:")

    for name in verified:
        print(f"  ✅ {name} (verified)")

    for name in missing:
        print(f"  ⚠️  {name} (missing)")

    for name, expected, actual in modified:
        print(f"  ⛔ {name} (modified)")
        if os.getenv("CHECKPOINT_VERBOSE"):
            print(f"     Expected: {expected}")
            print(f"     Actual:   {actual}")

    for name in new_files[:10]:  # 限制显示数量
        print(f"  🆕 {name} (new, not in checkpoint)")

    if len(new_files) > 10:
        print(f"  ... and {len(new_files) - 10} more new files")

    # 摘要
    print()
    print("Summary:")
    print(f"  Total tracked: {len(data['files_sha256'])} files")
    print(f"  Verified: {len(verified)}")
    print(f"  Missing: {len(missing)}")
    print(f"  Modified: {len(modified)}")
    print(f"  New (untracked): {len(new_files)}")

    if missing or modified:
        print()
        print("⚠️  Actions:")
        if modified:
            print("  - Review modified files before continuing")
            print("  - Consider updating checkpoint if changes are intentional")
        if missing:
            print("  - Restore missing files or update checkpoint")

    return 0 if not missing and not modified else 1


def diff_checkpoints(root, checkpoint1_path, checkpoint2_path):
    """
    比较两个检查点的差异
    """
    root = worktree_root(root)

    if not checkpoint1_path.exists() or not checkpoint2_path.exists():
        print("ERROR: One or both checkpoints not found", file=sys.stderr)
        return 1

    data1 = json.loads(checkpoint1_path.read_text(encoding="utf-8"))
    data2 = json.loads(checkpoint2_path.read_text(encoding="utf-8"))

    files1 = set(data1["files_sha256"].keys())
    files2 = set(data2["files_sha256"].keys())

    added = files2 - files1
    removed = files1 - files2
    common = files1 & files2
    modified = [f for f in common if data1["files_sha256"][f] != data2["files_sha256"][f]]
    unchanged = [f for f in common if data1["files_sha256"][f] == data2["files_sha256"][f]]

    print(f"Checkpoint Diff:")
    print(f"  From: {checkpoint1_path.name} ({data1.get('created_at', 'unknown')})")
    print(f"  To:   {checkpoint2_path.name} ({data2.get('created_at', 'unknown')})")
    print()

    if added:
        print(f"Added files ({len(added)}):")
        for name in sorted(added):
            print(f"  + {name}")
        print()

    if removed:
        print(f"Removed files ({len(removed)}):")
        for name in sorted(removed):
            print(f"  - {name}")
        print()

    if modified:
        print(f"Modified files ({len(modified)}):")
        for name in sorted(modified):
            print(f"  M {name}")
        print()

    print(f"Unchanged: {len(unchanged)} files")

    # 比较元数据
    print()
    print("Metadata changes:")
    if data1.get("goal") != data2.get("goal"):
        print(f"  Goal:")
        print(f"    - {data1.get('goal', 'N/A')}")
        print(f"    + {data2.get('goal', 'N/A')}")

    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("save", "verify", "show", "review", "diff"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--checkpoint", type=Path, help="Checkpoint file (for review)")
    parser.add_argument("--from", dest="checkpoint1", type=Path, help="First checkpoint (for diff)")
    parser.add_argument("--to", dest="checkpoint2", type=Path, help="Second checkpoint (for diff)")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.mode == "save":
            print(save(root, json.load(sys.stdin)))
            return 0
        elif args.mode == "review":
            return review(root, args.checkpoint)
        elif args.mode == "diff":
            if not args.checkpoint1 or not args.checkpoint2:
                print("ERROR: diff requires --from and --to arguments", file=sys.stderr)
                return 1
            return diff_checkpoints(root, args.checkpoint1, args.checkpoint2)

        code = verify(root)
        if code == 2:
            print("WARNING: no checkpoint", file=sys.stderr)
        elif args.mode == "show":
            print(location(root).read_text(encoding="utf-8"))
        return code
    except (OSError, ValueError, TypeError, RecursionError, subprocess.CalledProcessError) as exc:
        print(f"WARNING: checkpoint invalid: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())

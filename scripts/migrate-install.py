#!/usr/bin/env python3
"""Reversibly archive unselected managed capabilities, preserving custom or unknown files."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("migration_installer", ROOT / "scripts/install-global.py")
INSTALL = importlib.util.module_from_spec(spec)
spec.loader.exec_module(INSTALL)


def linked(path):
    return path.is_symlink() or getattr(path, "is_junction", lambda: False)()


def inventory(path):
    if linked(path):
        raise ValueError("linked capability cannot be migrated")
    files = [path] if path.is_file() else sorted(INSTALL.safe_files(path))
    if any(linked(p) for p in files):
        raise ValueError("linked content cannot be migrated")
    return {p.relative_to(path).as_posix() if path.is_dir() else ".": hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files if p.is_file()}


def canonical(data):
    return data.replace(b"\r\n", b"\n")


def historical_files(baseline):
    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", baseline):
        raise ValueError("baseline must be a commit hash")
    try:
        result = subprocess.run(["git", "-C", str(ROOT), "archive", baseline, ".claude/skills", "agents"],
                                capture_output=True, check=True)
    except subprocess.CalledProcessError as exc:
        raise ValueError("historical baseline unavailable; retain unmatched files or fetch the explicit baseline") from exc
    with tarfile.open(fileobj=io.BytesIO(result.stdout)) as archive:
        return {item.name: archive.extractfile(item).read() for item in archive.getmembers() if item.isfile()}


def plan(target, profiles, baseline):
    selected, all_names = INSTALL.profile_names(profiles), INSTALL.profile_names("all")
    historic = None
    moves, retained = [], []
    for kind in ("skills", "agents"):
        for name in sorted(all_names[kind] - selected[kind]):
            rel = kind + "/" + name
            path = target / rel
            if not path.exists():
                continue
            if not path.resolve().is_relative_to(target):
                retained.append(dict(path=rel, reason="path escapes target"))
                continue
            try:
                digests = inventory(path)
                if not digests:
                    raise ValueError("empty or unknown capability")
                for child in digests:
                    dest_file = path if child == "." else path / child
                    source_name = ((".claude/skills/" if kind == "skills" else "agents/") + name +
                                   ("/" + child if child != "." else ""))
                    source = ROOT / source_name
                    data = canonical(dest_file.read_bytes())
                    matches_current = source.is_file() and data == canonical(source.read_bytes())
                    matches_history = False
                    if not matches_current:
                        if historic is None:
                            historic = historical_files(baseline)
                        matches_history = source_name in historic and data == canonical(historic[source_name])
                    if not matches_current and not matches_history:
                        raise ValueError("customized/unknown file: " + child)
                moves.append(dict(path=rel, files=digests))
            except (OSError, ValueError) as exc:
                retained.append(dict(path=rel, reason=str(exc)))
    return dict(version=1, target=str(target), profiles=profiles, baseline=baseline, moves=moves, retained=retained)


def apply(target, proposed):
    # Preflight every path before any move. Never overwrite or discard target content.
    if Path(proposed["target"]).resolve() != target:
        raise ValueError("migration target mismatch")
    for item in proposed["moves"]:
        if Path(item["path"]).is_absolute() or ".." in Path(item["path"]).parts or Path(item["path"]).parts[0] not in {"skills", "agents"}:
            raise ValueError("invalid capability path")
        path = target / item["path"]
        if not path.resolve().is_relative_to(target) or inventory(path) != item["files"]:
            raise ValueError("migration source changed after planning")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + f"-{time.time_ns()}"
    store = target / ".taiyi-migrations"
    if linked(store) or not store.resolve().is_relative_to(target):
        raise ValueError("migration store escapes target")
    archive = store / stamp
    archive.mkdir(parents=True)
    manifest = dict(proposed, completed=[])
    manifest_path = archive / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for item in proposed["moves"]:
        destination = archive / item["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(target / item["path"]), str(destination))
        manifest["completed"].append(item)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def restore(target, manifest_path):
    manifest_path = manifest_path.resolve()
    if not manifest_path.is_relative_to(target / ".taiyi-migrations") or linked(manifest_path):
        raise ValueError("restore manifest is outside the migration store")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if Path(manifest["target"]).resolve() != target:
        raise ValueError("restore target mismatch")
    items = manifest.get("completed", [])
    for item in items:
        if Path(item["path"]).is_absolute() or ".." in Path(item["path"]).parts or Path(item["path"]).parts[0] not in {"skills", "agents"}:
            raise ValueError("invalid restore path")
        source, destination = manifest_path.parent / item["path"], target / item["path"]
        if not source.resolve().is_relative_to(manifest_path.parent) or not destination.resolve().is_relative_to(target):
            raise ValueError("restore path escapes its store")
        if destination.exists() or inventory(source) != item["files"]:
            raise ValueError("restore collision or archived content changed")
    for item in reversed(items):
        destination = target / item["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(manifest_path.parent / item["path"]), str(destination))
    manifest["completed"] = []
    manifest["restored"] = True
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=Path.home() / ".claude")
    parser.add_argument("--profile", default="core")
    parser.add_argument("--baseline", default="c9473b8")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--restore", type=Path)
    args = parser.parse_args()
    target = args.target.resolve()
    try:
        if args.restore:
            restore(target, args.restore)
            print("Migration restored without overwriting active files")
            return 0
        proposed = plan(target, args.profile, args.baseline)
        if args.apply and proposed["moves"]:
            proposed["manifest"] = str(apply(target, proposed))
        print(json.dumps(proposed, ensure_ascii=False, indent=2))
        for item in proposed["retained"]:
            print(f"WARNING: retained {item['path']}: {item['reason']}", file=sys.stderr)
        return 1 if proposed["retained"] else 0
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"WARNING: migration stopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

"""Small shared storage primitives; never silently recover corrupted state."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time


def warning(message):
    print(f"WARNING: {message}", file=sys.stderr)


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def bounded(value, limit=1200):
    text = re.sub(r"(?i)(api[_-]?key|token|password|secret|authorization)(\s*[=:]\s*|\s+)[^\s,;]+",
                  r"\1=[REDACTED]", str(value))
    text = re.sub(r"\b(?:sk-[\w-]+|gh[pousr]_[\w]+)\b", "[REDACTED]", text)
    return text[:limit]


def read_json(path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
        os.replace(temporary, path)
        if os.name != "nt":
            path.chmod(0o600)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


@contextmanager
def locked(path, timeout=0.5):
    """Exclusive bounded lock. Stale locks require inspection, never guessed removal."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + ".lock")
    deadline = time.monotonic() + timeout
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            break
        except (FileExistsError, PermissionError) as exc:
            # Windows may report access denied while another process deletes
            # its just-closed lock. Persistent permission errors still fail.
            if isinstance(exc, PermissionError) and os.name != "nt":
                raise
            if time.monotonic() >= deadline:
                raise TimeoutError(f"state lock unavailable ({type(exc).__name__})") from exc
            time.sleep(0.01)
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def confined(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("path outside knowledge root")
    return path


def markdown_files(root):
    for path in sorted(root.rglob("*.md")):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            warning("skipped linked memory source")
            continue
        yield path

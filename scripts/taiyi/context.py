"""Compute before printing: bounded summaries, aggregation and explicit local cache."""
import json
from pathlib import Path
import re
import time

from .common import atomic_json, bounded, digest, locked, read_json, utcnow, warning


def summarize(lines, sample_limit=5):
    count = size = errors = warnings = 0
    head, tail, error_samples = [], [], []
    for line in lines:
        count += 1
        size += len(line.encode("utf-8"))
        sample = bounded(line.rstrip(), 200)
        if len(head) < sample_limit:
            head.append(sample)
        tail = (tail + [sample])[-sample_limit:]
        if re.search(r"\b(?:ERROR|FAILED|FAILURE|Traceback|Exception)\b", line, re.I):
            errors += 1
            if len(error_samples) < sample_limit:
                error_samples.append(sample)
        if re.search(r"\bWARN(?:ING)?\b", line, re.I):
            warnings += 1
    result = dict(lines=count, raw_bytes=size, error_lines=errors, warning_lines=warnings,
                  head=head, tail=tail, error_samples=error_samples, lossy=True)
    # Iterate because the digit count of this field is part of its own size.
    result["summary_bytes"] = 0
    for _ in range(5):
        size = len(json.dumps(result, ensure_ascii=False).encode("utf-8"))
        if result["summary_bytes"] == size:
            break
        result["summary_bytes"] = size
    return result


def aggregate(root, pattern="*.py", operation="lines", needle=None, limit=50):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError("aggregation directory missing")
    if operation not in {"lines", "grep", "metadata"}:
        raise ValueError("unknown aggregation operation")
    if operation == "grep" and not needle:
        raise ValueError("grep requires --needle (literal substring)")
    results, total_files, total_lines, total_bytes, matched_files = [], 0, 0, 0, 0
    skipped = 0
    for path in sorted(root.rglob(pattern)):
        if not path.is_file() or any(p in {".git", "node_modules", ".claude-tmp", "__pycache__"}
                                     for p in path.relative_to(root).parts):
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            warning("aggregation skipped linked source")
            skipped += 1
            continue
        total_files += 1
        size = path.stat().st_size
        total_bytes += size
        matches, line_count = [], 0
        if operation != "metadata":
            try:
                with path.open(encoding="utf-8") as stream:
                    for line_count, line in enumerate(stream, 1):
                        if needle and needle in line and len(matches) < 3:
                            matches.append(dict(line=line_count, text=bounded(line.rstrip(), 180)))
            except UnicodeError:
                warning("aggregation skipped non-UTF8 source")
                skipped += 1
                continue
        total_lines += line_count
        if matches:
            matched_files += 1
        if len(results) < max(1, min(limit, 200)) and (operation != "grep" or matches):
            results.append(dict(path=path.relative_to(root).as_posix(), bytes=size,
                                lines=line_count, matches=matches))
    return dict(files=total_files, lines=total_lines, raw_bytes=total_bytes, skipped=skipped,
                matched_files=matched_files if operation == "grep" else None,
                results=results, truncated=(matched_files if operation == "grep" else total_files) > len(results))


class ContentCache:
    """Explicitly populated cache; no network requests or guessed URL validity."""
    def __init__(self, directory):
        self.root = Path(directory)

    def path(self, key):
        return self.root / (digest(key) + ".json")

    def put(self, key, content, ttl=86400, now=None):
        if not 0 < ttl <= 7 * 86400:
            raise ValueError("TTL must be 1..604800 seconds")
        if len(content.encode("utf-8")) > 2 * 1024 * 1024:
            raise ValueError("cache entry exceeds 2 MiB")
        path = self.path(key)
        entry = dict(created=time.time() if now is None else now, ttl=ttl,
                     content=content, sha256=digest(content))
        # A cache-wide lock makes capacity checks and entry writes one operation.
        with locked(self.root / "cache-capacity"):
            entries = list(self.root.glob("*.json"))
            if len(entries) >= 200 and not path.exists():
                raise ValueError("cache capacity reached (200 entries); inspect local cache")
            used = sum(p.stat().st_size for p in entries if p != path)
            if used + len(json.dumps(entry, ensure_ascii=False).encode("utf-8")) > 50 * 1024 * 1024:
                raise ValueError("cache capacity reached (50 MiB); inspect local cache")
            atomic_json(path, entry)
        return dict(cached=True, key_hash=digest(key), bytes=len(content.encode("utf-8")))

    def get(self, key, query="", now=None):
        data = read_json(self.path(key))
        if data is None:
            return dict(hit=False, reason="missing")
        if not isinstance(data, dict) or digest(data["content"]) != data["sha256"]:
            raise ValueError("cache integrity invalid")
        if (time.time() if now is None else now) >= data["created"] + data["ttl"]:
            return dict(hit=False, reason="expired")
        from .search import excerpt, tokens
        return dict(hit=True, snippet=excerpt(data["content"], tokens(query), 900),
                    original_bytes=len(data["content"].encode("utf-8")))


def pre_tool(store, tool, inputs, cwd, tool_use_id=None):
    limit = inputs.get("limit")
    bounded_read = tool == "Read" and isinstance(limit, int) and not isinstance(limit, bool) and limit > 0
    if tool not in {"Read", "Grep"} or bounded_read:
        if store.path.exists():
            store.update(lambda data: data.update(streak={}))
        return None

    def update(data):
        path = inputs.get("file_path", "") if tool == "Read" else inputs.get("path", ".")
        if not isinstance(path, str):
            raise ValueError("tool path must be a string")
        target = (Path(cwd) / path).resolve()
        key = digest(str(target.parent if tool == "Read" else target))
        target_key = digest(str(target))
        previous = data["streak"]
        count = previous.get("count", 0) + 1 if previous.get("tool") == tool and previous.get("key") == key else 1
        data["streak"] = dict(tool=tool, key=key, count=count, target=target_key)
        reason = None
        if tool == "Read" and target_key != previous.get("target") and target.is_file() and target.stat().st_size > 100000:
            reason = "大文件：使用 offset/limit 或脚本流式聚合，只输出所需结果。"
        elif count == 3:
            reason = "连续同目录读取，建议批量聚合。" if tool == "Read" else "连续搜索，建议批量 rg 或脚本。"
        elif count == 6:
            reason = "建议批量处理连续读取/搜索。"
        elif count >= 9 and count % 9 == 0:
            reason = "建议改用批量接口。"
        if reason:
            data["decisions"].append(dict(id=tool_use_id or digest(str(time.time_ns())),
                tool_use_id=tool_use_id, ts=utcnow(),
                task=tool + " output strategy", decision="use_script", reason=reason,
                confidence=0.8, outcome="pending", duration_ms=None, cost=None))
        return reason
    return store.update(update)


def post_tool(store, tool, inputs, response, failed=False, tool_use_id=None, cwd=None):
    is_error = failed or (isinstance(response, dict) and
                         (response.get("is_error") is True or response.get("isError") is True or
                          (isinstance(response.get("exit_code"), int) and response["exit_code"] != 0)))
    events = []
    if tool in {"Edit", "Write", "MultiEdit"} and not is_error:
        path = inputs.get("file_path")
        if isinstance(path, str):
            target = (Path(cwd or store.root) / path).resolve()
            summary = target.relative_to(store.root).as_posix() if target.is_relative_to(store.root) else "external file edited"
        else:
            summary = "multiple files"
        events.append(dict(ts=utcnow(), kind="file_edit", summary=bounded(summary, 300)))
    elif tool == "Bash":
        command = inputs.get("command", "")
        if isinstance(command, str) and re.search(r"\bgit\b", command):
            # Only the verb; no command arguments or stdout are persisted.
            match = re.search(r"\bgit\s+(status|diff|add|commit|checkout|switch|merge|rebase|log|push|pull)\b", command)
            events.append(dict(ts=utcnow(), kind="git", summary="git " + (match[1] if match else "operation")))
    elif tool in {"TaskCreate", "TaskUpdate"}:
        events.append(dict(ts=utcnow(), kind="task", summary="task status " + bounded(inputs.get("status", "updated"), 80)))
    if is_error:
        raw = str(response)
        categories = [kind for kind in ("PermissionError", "FileExistsError", "UnicodeEncodeError",
                      "not been read", "FAILED", "timeout") if kind.lower() in raw.lower()]
        events.append(dict(ts=utcnow(), kind="failure", tool=tool,
                           summary=", ".join(categories) or "tool failed; inspect original tool result"))
    if events or (tool_use_id and store.path.exists()):
        def complete(data):
            data["events"].extend(events)
            for item in data["decisions"]:
                if tool_use_id and item.get("tool_use_id") == tool_use_id and item["outcome"] == "pending":
                    item.update(outcome="failure" if is_error else "success")
        store.update(complete)
    return "工具失败：检查原始错误，修复后再验证。" if is_error else None

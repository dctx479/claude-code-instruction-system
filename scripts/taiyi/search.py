"""Transactional Markdown index with bounded, source-carrying search results."""
import re
import sqlite3
from pathlib import Path

from .common import confined, digest, markdown_files, warning

VERSION = 1


def levenshtein(left, right):
    previous = list(range(len(right) + 1))
    for row, character in enumerate(left, 1):
        current = [row]
        for column, other in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[column] + 1,
                               previous[column - 1] + (character != other)))
        previous = current
    return previous[-1]


def tokens(text, limit=32):
    # Include Han characters so SQLite's unicode tokenizer can be supplemented.
    return re.findall(r"[a-z0-9_-]+|[\u3400-\u9fff]+", text.lower())[:limit]


def excerpt(content, terms, size=700):
    offset = next((content.lower().find(term) for term in terms if term in content.lower()), 0)
    start = max(0, offset - size // 4)
    return ("…" if start else "") + content[start:start + size] + ("…" if start + size < len(content) else "")


class MemoryIndex:
    def __init__(self, memory_dir, db=None, use_fts=True):
        self.root = Path(memory_dir).resolve()
        self.db = Path(db) if db else confined(self.root, ".cache/index.db")
        self.use_fts = use_fts

    def sources(self):
        if not self.root.is_dir():
            raise ValueError("memory directory missing")
        return [(p.relative_to(self.root).as_posix(), p.read_text(encoding="utf-8"))
                for p in markdown_files(self.root)]

    def connect(self):
        self.db.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.db, timeout=0.2)
        connection.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
        connection.execute("CREATE TABLE IF NOT EXISTS documents (path TEXT PRIMARY KEY, content TEXT)")
        return connection

    def sync(self, force=False):
        sources = self.sources()
        fingerprint = digest(str(VERSION) + str(self.use_fts) + repr(sources))
        connection = self.connect()
        try:
            with connection:
                old = dict(connection.execute("SELECT key, value FROM meta"))
                if not force and old.get("fingerprint") == fingerprint and old.get("version") == str(VERSION):
                    return dict(documents=len(sources), rebuilt=False, fts=old.get("fts") == "1")
                connection.execute("BEGIN IMMEDIATE")
                fts = False
                connection.execute("DROP TABLE IF EXISTS memory_fts")
                if self.use_fts:
                    try:
                        connection.execute("CREATE VIRTUAL TABLE memory_fts USING fts5(path UNINDEXED, content, tokenize='porter unicode61')")
                        fts = True
                    except sqlite3.OperationalError as exc:
                        if "no such module" not in str(exc):
                            raise
                        warning("FTS5 unavailable; using substring search")
                else:
                    warning("FTS5 disabled; using substring search")
                connection.execute("DELETE FROM documents")
                connection.executemany("INSERT INTO documents VALUES (?, ?)", sources)
                if fts:
                    connection.executemany("INSERT INTO memory_fts VALUES (?, ?)", sources)
                connection.executemany("INSERT OR REPLACE INTO meta VALUES (?, ?)",
                                       [("fingerprint", fingerprint), ("fts", str(int(fts))), ("version", str(VERSION))])
            return dict(documents=len(sources), rebuilt=True, fts=fts)
        finally:
            connection.close()

    def search(self, query, limit=3):
        terms = tokens(query)
        if not terms:
            return []
        limit = max(1, min(limit, 10))
        metadata = self.sync()
        connection = self.connect()
        try:
            docs = dict(connection.execute("SELECT path, content FROM documents"))
            ranks = {}
            if metadata["fts"]:
                expression = " OR ".join('"' + t.replace('"', '""') + '"' for t in terms)
                for rank, (path,) in enumerate(connection.execute(
                        "SELECT path FROM memory_fts WHERE memory_fts MATCH ? ORDER BY bm25(memory_fts), path LIMIT 30",
                        (expression,))):
                    ranks[path] = 1 / (60 + rank + 1)
            substring = sorted(((sum(term in content.lower() for term in terms), path)
                                for path, content in docs.items()), reverse=True)
            for rank, (score, path) in enumerate(substring):
                if score:
                    ranks[path] = ranks.get(path, 0) + 1 / (60 + rank + 1)
            corrected = []
            if not ranks:
                vocabulary = sorted(set(t for content in docs.values() for t in tokens(content, 100000)))
                for term in terms:
                    if len(term) > 64:
                        continue
                    candidates = [(levenshtein(term, word), word) for word in vocabulary
                                  if abs(len(term) - len(word)) <= 2 and len(word) <= 64]
                    if candidates:
                        distance, word = min(candidates)
                        if distance <= min(2, max(1, len(term) // 4)):
                            corrected.append(word)
                for path, content in docs.items():
                    if any(t in content.lower() for t in corrected):
                        ranks[path] = 1 / 61
            def proximity(path):
                positions = [docs[path].lower().find(t) for t in terms]
                found = [p for p in positions if p >= 0]
                return len(found) / (1 + (max(found) - min(found) if found else 0))
            ordered = sorted(ranks, key=lambda p: (-ranks[p], -proximity(p), p))[:limit]
            return [dict(path=path, score=round(ranks[path], 6),
                         snippet=excerpt(docs[path], corrected or terms), corrected=corrected) for path in ordered]
        finally:
            connection.close()

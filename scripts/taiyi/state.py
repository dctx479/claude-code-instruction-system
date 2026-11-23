"""Project/session isolated records, bounded under one atomic lock."""
from copy import deepcopy
from pathlib import Path

from .common import atomic_json, bounded, digest, locked, read_json, utcnow

VERSION = 1


class SessionStore:
    def __init__(self, root, session_id):
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id required; event not recorded")
        self.root = Path(root).resolve()
        self.key = digest(str(self.root))[:16] + "-" + digest(session_id)[:20]
        self.path = self.root / ".claude/taiyi/sessions" / (self.key + ".json")
        if not self.path.resolve().is_relative_to(self.root):
            raise ValueError("session state outside project")

    def load(self):
        data = read_json(self.path, dict(version=VERSION, events=[], decisions=[], streak={}))
        if not isinstance(data, dict) or data.get("version") != VERSION:
            raise ValueError("session state version invalid")
        if not isinstance(data.get("events"), list) or not isinstance(data.get("decisions"), list):
            raise ValueError("session state collections invalid")
        if not isinstance(data.get("streak"), dict):
            raise ValueError("session streak invalid")
        return data

    def update(self, operation):
        with locked(self.path):
            data = self.load()
            before = deepcopy(data)
            result = operation(data)
            data["events"] = data["events"][-200:]
            data["decisions"] = data["decisions"][-200:]
            if data != before:
                atomic_json(self.path, data)
            return result

    def record(self, kind, summary, **fields):
        item = dict(ts=utcnow(), kind=kind, summary=bounded(summary), **fields)
        self.update(lambda data: data["events"].append(item))
        return item

    def snapshot(self):
        def save(data):
            snapshot = dict(ts=utcnow(), events=data["events"][-30:],
                            pending=[d for d in data["decisions"] if d.get("outcome") == "pending"][-5:])
            data["snapshot"] = snapshot
            return snapshot
        return self.update(save)

    def recall(self, query="", limit=5):
        data = self.load()
        events = data.get("snapshot", {}).get("events", []) + data["events"]
        unique = {str(item): item for item in events}
        terms = query.lower().split()
        ranked = sorted(enumerate(unique.values()),
                        key=lambda row: (sum(t in row[1]["summary"].lower() for t in terms), row[0]),
                        reverse=True)
        return [item for _, item in ranked[:max(1, min(limit, 10))]]

"""Advisory routing and versioned workflows. No task commands are executed."""
import difflib
import math
import re
import time
import uuid
from collections import Counter
from pathlib import Path

from .common import bounded, confined, read_json, utcnow

OUTCOMES = {"pending", "success", "failure", "rejected"}


class Playbooks:
    def __init__(self, memory_dir):
        self.root = Path(memory_dir).resolve()
        self.registry = read_json(confined(self.root, "playbooks/REGISTRY.json"), {})
        if not isinstance(self.registry, dict):
            raise ValueError("invalid playbook registry")

    def load(self, name, version=None):
        item = self.registry[name]
        selected = version or item["latest"]
        if selected not in item["versions"]:
            raise ValueError("unregistered playbook version")
        path = confined(self.root, item["versions"][selected])
        return dict(name=name, version=selected, path=str(path), content=path.read_text(encoding="utf-8"))

    def match(self, task):
        candidates = []
        for name, entry in self.registry.items():
            score = sum(str(word).lower() in task.lower() for word in entry["keywords"])
            if score >= entry.get("min_matches", 2):
                candidates.append((score, name))
        if not candidates:
            return None
        ordered = sorted(candidates, reverse=True)
        if len(ordered) > 1 and ordered[0][0] == ordered[1][0]:
            return None
        result = self.load(ordered[0][1])
        result.pop("content")
        return result


class DecisionRouter:
    def __init__(self, memory_dir, store=None):
        self.playbooks = Playbooks(memory_dir)
        self.failures = read_json(confined(Path(memory_dir).resolve(), "failures/REGISTRY.json"), [])
        self.store = store

    def route(self, task, context=None, record=False):
        if not isinstance(task, str) or not task.strip():
            raise ValueError("nonempty task required")
        started = time.perf_counter()
        task = bounded(task, 2000)
        decision = dict(decision="delegate_to_llm", reason="需要进一步判断", confidence=0.0)
        for failure in self.failures:
            if re.search(failure["pattern"], task, re.IGNORECASE):
                decision = dict(decision="avoid_known_failure", reason=failure["name"],
                                alternative=failure["solution"], confidence=0.8)
                break
        else:
            # Narrow compound/destructive requests never enter the mechanical route.
            compound = re.search(r"然后|并且|部署|删除|覆盖|安装|\b(?:then|deploy|delete|install|and)\b", task, re.I)
            simple = [
                (r"统计.*(?:文件|目录).*行数|\bcount (?:file |source )?lines\b", "aggregate-lines"),
                (r"查找.*包含.*文件|\bfind files containing\b", "rg"),
                (r"(?:解析|检查|格式化).*JSON|\b(?:parse|validate|format) json\b", "json-tool"),
                (r"列出.*最近修改|\blist recently modified files\b", "file-metadata"),
            ]
            match = next((name for pattern, name in simple if re.search(pattern, task, re.I)), None)
            playbook = self.playbooks.match(task)
            if match and not compound:
                decision = dict(decision="use_script", operation=match, reason="机械操作可由工具聚合", confidence=0.9)
            elif playbook:
                decision = dict(decision="use_playbook", playbook=playbook, reason="匹配版本化流程", confidence=0.85)
            elif self.store:
                candidates = [d for d in self.store.load()["decisions"] if d.get("outcome") == "success"]
                similar = [(difflib.SequenceMatcher(None, task, d["task"], autojunk=False).ratio(), d)
                           for d in candidates[-20:]]
                if similar:
                    score, previous = max(similar, key=lambda pair: pair[0])
                    if score >= 0.85 and not compound:
                        decision = dict(decision="repeat_previous", reference=previous["id"],
                                        reason="参考已成功任务；重新检查当前环境", confidence=round(score, 3))
        decision.update(id=uuid.uuid4().hex, task=task, ts=utcnow(), outcome="pending",
                        duration_ms=round((time.perf_counter() - started) * 1000, 3), cost=None)
        if record:
            if self.store is None:
                raise ValueError("recording requires session store")
            self.store.update(lambda data: data["decisions"].append(decision))
        return decision


def feedback(store, decision_id, outcome, duration_ms=None, cost=None):
    if outcome not in OUTCOMES - {"pending"}:
        raise ValueError("invalid outcome")
    for value in (duration_ms, cost):
        if value is not None and (not isinstance(value, (float, int)) or not math.isfinite(value) or value < 0):
            raise ValueError("invalid measured duration/cost")
    def change(data):
        item = next((d for d in data["decisions"] if d["id"] == decision_id), None)
        if item is None:
            raise ValueError("decision not found")
        item.update(outcome=outcome, completed_at=utcnow(), execution_ms=duration_ms, cost=cost)
        return item
    return store.update(change)


def analyze(store):
    decisions = store.load()["decisions"]
    measured = [d for d in decisions if d["outcome"] in {"success", "failure"}]
    successful = sum(d["outcome"] == "success" for d in measured)
    playbooks = {}
    for item in measured:
        if item["decision"] == "use_playbook":
            book = item["playbook"]
            key = book["name"] + "@" + book["version"]
            stats = playbooks.setdefault(key, dict(successes=0, attempts=0))
            stats["attempts"] += 1
            stats["successes"] += item["outcome"] == "success"
    for stats in playbooks.values():
        stats["success_rate"] = stats["successes"] / stats["attempts"]
    return dict(total=len(decisions), measured=len(measured),
                success_rate=successful / len(measured) if measured else None,
                routing_accuracy=None, routes=dict(Counter(d["decision"] for d in decisions)),
                frequent_tasks=dict(Counter(d["task"] for d in decisions).most_common(10)),
                playbooks=playbooks, retrospective=[dict(task=d["task"], reason=d["outcome"],
                    proposal="检查失败证据后提出最小 diff，不自动晋升规则")
                    for d in decisions if d["outcome"] == "failure" or
                    (d.get("execution_ms") is not None and d["execution_ms"] > 60000)])

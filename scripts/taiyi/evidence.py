"""Evidence validation and bounded tracing, separate from running tests."""
import ast
from datetime import date
import json
import math
from pathlib import Path
import re
import subprocess

from .common import confined, digest, markdown_files, read_json, warning

TYPES = {"test", "commit", "measurement", "observation", "documentation"}


def chain_issues(chain):
    issues = []
    if chain.get("status") in {"invalid", "cycle", "depth_limit", "node_limit"}:
        issues.append(dict(name=chain.get("name"), status=chain["status"]))
    verification = chain.get("verification", {})
    if verification.get("status") == "invalid" or any(item.get("status") in {"invalid", "changed"}
                                                      for item in verification.get("evidence", [])):
        issues.append(dict(name=chain.get("name"), status="invalid_evidence"))
    for child in chain.get("related", []):
        issues.extend(chain_issues(child))
    return issues


def probability(value):
    return (not isinstance(value, bool) and isinstance(value, (float, int)) and
            math.isfinite(value) and 0 <= value <= 1)


def validate(metadata):
    errors = []
    if not isinstance(metadata, dict):
        return ["metadata must be an object"]
    if not probability(metadata.get("confidence")):
        errors.append("confidence must be in [0, 1]")
    evidence = metadata.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        return errors + ["nonempty evidence array required"]
    seen = set()
    for item in evidence:
        if not isinstance(item, dict):
            errors.append("evidence must be an object")
            continue
        for key in ("id", "source", "method", "date", "verified_by"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                errors.append(f"evidence {key} required")
        if not isinstance(item.get("type"), str) or item["type"] not in TYPES:
            errors.append("unknown evidence type")
        if not probability(item.get("confidence")):
            errors.append("evidence confidence must be in [0, 1]")
        identifier = item.get("id")
        if isinstance(identifier, str):
            if identifier in seen:
                errors.append("duplicate evidence id")
            seen.add(identifier)
        if "metrics" in item and not isinstance(item["metrics"], dict):
            errors.append("metrics must be an object")
        if "sha256" in item and (not isinstance(item["sha256"], str) or
                                   not re.fullmatch(r"[a-f0-9]{64}", item["sha256"])):
            errors.append("sha256 must be a 64-character lowercase hex digest")
        try:
            date.fromisoformat(item.get("date", ""))
        except (ValueError, TypeError):
            errors.append("evidence date must be YYYY-MM-DD")
    related = metadata.get("related", [])
    if not isinstance(related, list) or not all(isinstance(r, str) for r in related):
        errors.append("related must be a list of memory names")
    elif len(related) > 20:
        errors.append("related exceeds 20 entries per memory")
    return errors


class EvidenceQuery:
    def __init__(self, memory_dir, repo=None):
        self.root = Path(memory_dir).resolve()
        self.repo = Path(repo).resolve() if repo else self.root.parent

    def load_memory(self, name):
        relative = name if name.endswith(".md") else name + ".md"
        path = confined(self.root, relative)
        content = path.read_text(encoding="utf-8")
        sidecar = confined(self.root, path.with_suffix(".evidence.json").relative_to(self.root))
        data = read_json(sidecar)
        body = content
        if data is None and content.startswith("---\n"):
            parts = content.split("\n---", 1)
            if len(parts) != 2:
                raise ValueError("unterminated frontmatter")
            header = parts[0][4:]
            if header.lstrip().startswith("{"):
                data = json.loads(header)
                body = parts[1].lstrip("\r\n")
            else:
                # Existing free-form YAML memories remain readable unchanged.
                # Structured evidence in YAML requires an adjacent JSON ledger.
                if re.search(r"^\s*(?:evidence|confidence):", header, re.M):
                    raise ValueError("structured YAML evidence requires JSON sidecar")
        if data is None:
            data = dict(name=path.stem, description=content.splitlines()[0] if content else path.stem,
                        metadata=None)
        if not isinstance(data, dict):
            raise ValueError("memory metadata must be an object")
        return dict(name=data.get("name", path.stem), description=data.get("description", path.stem),
                    metadata=data.get("metadata"), path=path.relative_to(self.root).as_posix(), content=body)

    def verify_source(self, item):
        source = item["source"]
        result = dict(id=item["id"], source=source, status="unverifiable")
        if item["type"] == "commit":
            match = re.fullmatch(r"commit:([a-fA-F0-9]{7,40})", source)
            if not match:
                return dict(result, status="invalid", reason="invalid commit reference")
            command = subprocess.run(["git", "-C", str(self.repo), "cat-file", "-t", match[1]],
                                     capture_output=True, text=True, timeout=2)
            return dict(result, status="reference_valid" if command.returncode == 0 and
                        command.stdout.strip() == "commit" else "invalid", reason="git object existence only")
        if re.match(r"https?://", source):
            return dict(result, reason="external URL not fetched")
        match = re.fullmatch(r"(.+?)(?::(\d+)(?:-(\d+))?|:([\w.]+))?", source)
        if not match:
            return dict(result, status="invalid", reason="invalid source")
        try:
            path = confined(self.repo, match[1])
        except ValueError:
            return dict(result, status="invalid", reason="source outside repository")
        if not path.is_file():
            return dict(result, status="invalid", reason="source missing")
        content = path.read_text(encoding="utf-8")
        if match[2]:
            start, end = int(match[2]), int(match[3] or match[2])
            if not 1 <= start <= end <= len(content.splitlines()):
                return dict(result, status="invalid", reason="source line range missing")
        if match[4]:
            symbols = {node.name for node in ast.walk(ast.parse(content))
                       if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))} if path.suffix == ".py" else set()
            if match[4].split(".")[-1] not in symbols:
                return dict(result, status="invalid", reason="source symbol missing")
        if item.get("sha256") and digest(content) != item["sha256"]:
            return dict(result, status="changed", reason="source hash changed; review required")
        if item["type"] in {"measurement", "observation"}:
            return dict(result, reason="source exists; observation/measurement requires review")
        return dict(result, status="reference_valid", reason="source exists; test execution not verified")

    def verify_evidence(self, name):
        memory = self.load_memory(name)
        metadata = memory["metadata"]
        if metadata is None:
            return dict(status="legacy", errors=[], evidence=[])
        errors = validate(metadata)
        if errors:
            return dict(status="invalid", errors=errors, evidence=[])
        checked = [self.verify_source(item) for item in metadata["evidence"]]
        return dict(status="review_required" if any(e["status"] != "reference_valid" for e in checked)
                    else "references_valid", errors=[], evidence=checked)

    def trace_evidence_chain(self, name, seen=None, depth=0, remaining=None):
        seen = set() if seen is None else seen
        remaining = [100] if remaining is None else remaining
        if remaining[0] <= 0:
            return dict(name=name, status="node_limit")
        remaining[0] -= 1
        canonical = name.removesuffix(".md")
        if canonical in seen:
            return dict(name=name, status="cycle")
        if depth >= 12:
            return dict(name=name, status="depth_limit")
        memory = self.load_memory(name)
        metadata = memory["metadata"] if isinstance(memory["metadata"], dict) else {}
        result = dict(name=memory["name"], conclusion=memory["description"],
                      confidence=metadata.get("confidence"), verification=self.verify_evidence(name))
        related = metadata.get("related", [])
        if isinstance(related, list) and all(isinstance(r, str) for r in related):
            result["related"] = []
            for item in related[:20]:
                try:
                    result["related"].append(self.trace_evidence_chain(item, seen | {canonical}, depth + 1, remaining))
                except (OSError, ValueError) as exc:
                    result["related"].append(dict(name=item, status="invalid", reason=str(exc)))
        return result

    def find_by_confidence(self, minimum=0.8):
        results = []
        for path in markdown_files(self.root):
            name = path.relative_to(self.root).as_posix()
            metadata = self.load_memory(name)["metadata"]
            if metadata is not None:
                errors = validate(metadata)
                if errors:
                    raise ValueError(f"invalid evidence metadata in {name}: {errors}")
                if metadata["confidence"] >= minimum:
                    results.append(name)
        return results

    def audit(self):
        report = dict(total=0, structured=0, legacy=[], low_confidence=[], invalid=[], review_required=[])
        for path in markdown_files(self.root):
            name = path.relative_to(self.root).as_posix()
            report["total"] += 1
            try:
                memory = self.load_memory(name)
                result = self.verify_evidence(name)
                if result["status"] == "legacy":
                    report["legacy"].append(name)
                    continue
                report["structured"] += 1
                if probability((memory["metadata"] or {}).get("confidence")) and memory["metadata"]["confidence"] < 0.6:
                    report["low_confidence"].append(name)
                if result["errors"] or any(e["status"] in {"invalid", "changed"} for e in result["evidence"]):
                    report["invalid"].append(dict(path=name, verification=result))
                elif result["status"] == "review_required":
                    report["review_required"].append(name)
                issues = chain_issues(self.trace_evidence_chain(name))
                if issues:
                    report["invalid"].append(dict(path=name, chain_issues=issues))
            except (OSError, ValueError, TypeError, KeyError, SyntaxError, subprocess.SubprocessError) as exc:
                warning(f"evidence record could not be validated: {name}: {exc}")
                report["invalid"].append(dict(path=name, reason=str(exc)))
        return report

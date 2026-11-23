"""Observable regression tests for optional optimization, routing and evidence."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from taiyi.common import atomic_json, digest, locked
from taiyi.context import aggregate, ContentCache, post_tool, pre_tool, summarize
from taiyi.decision import analyze, DecisionRouter, feedback, Playbooks
from taiyi.evidence import EvidenceQuery, validate
from taiyi.search import MemoryIndex
from taiyi.state import SessionStore


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


INSTALL = module("scripts/install-global.py", "runtime_installer")
VERIFY = module("scripts/verify-global-install.py", "runtime_verifier")


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.memory = self.root / "memory"
        self.memory.mkdir()
        self.store = SessionStore(self.root, "session/../../一")

    def tearDown(self):
        self.temporary.cleanup()

    def cli(self, *args, data=None):
        return subprocess.run([sys.executable, str(ROOT / "scripts/taiyi-tool.py"),
                               "--root", str(self.root), "--memory", str(self.memory), *args],
                              input=data, capture_output=True, text=True, encoding="utf-8")

    def hook(self, event, raw=None):
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(self.root))
        return subprocess.run([sys.executable, str(ROOT / "hooks/context-optimizer.py")],
                              input=raw if raw is not None else json.dumps(event), capture_output=True,
                              text=True, encoding="utf-8", env=env)

    def event(self, kind, **extra):
        return dict(session_id="one", cwd=str(self.root), hook_event_name=kind, **extra)

    def entry(self, name="claim", related=None, source="source.py:check"):
        (self.root / "source.py").write_text("def check():\n    return True\n", encoding="utf-8")
        metadata = dict(confidence=0.8, related=related or [], evidence=[dict(id="e1", type="test",
                        source=source, method="reference check", confidence=0.8, date="2026-11-23", verified_by="tool")])
        path = self.memory / (name + ".md")
        path.write_text("---\n" + json.dumps(dict(name=name, description="claim", metadata=metadata)) +
                        "\n---\nbody", encoding="utf-8")
        return path, metadata

    def test_state_isolated_by_project_and_session_and_traversal_safe(self):
        self.store.record("decision", "selected workflow")
        other_session = SessionStore(self.root, "different")
        other_project = SessionStore(self.root / "project", "session/../../一")
        self.assertNotEqual(other_session.path, self.store.path)
        self.assertNotEqual(other_project.path, self.store.path)
        self.assertTrue(self.store.path.resolve().is_relative_to(self.root))
        self.assertEqual([], other_session.load()["events"])
        with self.assertRaises(ValueError):
            SessionStore(self.root, None)

    def test_concurrent_records_remain_valid_and_bounded(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda i: self.store.record("task", str(i)), range(30)))
        self.assertEqual(30, len(self.store.load()["events"]))
        self.store.update(lambda data: data["events"].extend([dict(summary="x")] * 300))
        self.assertEqual(200, len(self.store.load()["events"]))

    def test_corruption_and_lock_contention_fail_without_overwriting(self):
        self.store.path.parent.mkdir(parents=True)
        self.store.path.write_text("{bad", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.store.record("task", "x")
        self.assertEqual("{bad", self.store.path.read_text(encoding="utf-8"))
        with locked(self.store.path):
            with self.assertRaises(TimeoutError):
                self.store.record("task", "x")

    @unittest.skipUnless(os.name == "nt", "Windows delete-pending lock behavior")
    def test_windows_delete_pending_lock_retries_but_persistent_access_error_fails(self):
        self.store.path.parent.mkdir(parents=True)
        actual_open = os.open
        attempts = [PermissionError("delete pending"), None]
        def opening(path, flags, mode):
            failure = attempts.pop(0) if attempts else None
            if failure:
                raise failure
            return actual_open(path, flags, mode)
        with patch("taiyi.common.os.open", side_effect=opening):
            with locked(self.store.path):
                pass
        with patch("taiyi.common.os.open", side_effect=PermissionError("access denied")):
            with self.assertRaisesRegex(TimeoutError, "PermissionError"):
                with locked(self.store.path, timeout=0.01):
                    self.fail("persistent permission failure acquired lock")

    def test_state_redacts_credentials_and_snapshot_recall_is_relevant(self):
        self.store.record("decision", "token=secret-value kubernetes selected")
        self.store.record("file_edit", "other.py")
        self.store.snapshot()
        result = self.store.recall("kubernetes", 1)
        self.assertIn("kubernetes", result[0]["summary"])
        self.assertNotIn("secret-value", self.store.path.read_text(encoding="utf-8"))

    def test_read_grep_thresholds_reset_and_edits_are_allowed(self):
        inputs = dict(file_path="src/a.py")
        self.assertIsNone(pre_tool(self.store, "Read", inputs, self.root))
        self.assertIsNone(pre_tool(self.store, "Read", inputs, self.root))
        self.assertIn("批量", pre_tool(self.store, "Read", inputs, self.root))
        self.assertIsNone(pre_tool(self.store, "Edit", inputs, self.root))
        self.assertIsNone(pre_tool(self.store, "Read", inputs, self.root))
        for _ in range(2):
            self.assertIsNone(pre_tool(self.store, "Grep", dict(path="src"), self.root))
        self.assertIn("批量", pre_tool(self.store, "Grep", dict(path="src"), self.root))
        self.assertIsNone(pre_tool(self.store, "Read", dict(file_path="other/a.py"), self.root))

    def test_large_read_with_limit_is_not_rerouted(self):
        path = self.root / "big.txt"
        path.write_text("x" * 100001)
        self.assertIsNone(pre_tool(self.store, "Read", dict(file_path=str(path), limit=20), self.root))
        self.assertIn("大文件", pre_tool(self.store, "Read", dict(file_path=str(path)), self.root))

    def test_hook_protocol_error_branches_and_missing_session(self):
        for raw in ("{bad", "[]", '{"cwd":"x"}', '{"session_id":"x","tool_input":[]}'):
            result = self.hook({}, raw)
            self.assertEqual(0, result.returncode)
            self.assertEqual("", result.stdout)
            self.assertIn("WARNING", result.stderr)
        path = self.root / "大文件.txt"
        path.write_text("x" * 100001, encoding="utf-8")
        result = self.hook(self.event("PreToolUse", tool_name="Read", tool_input=dict(file_path=str(path))))
        output = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual("PreToolUse", output["hookEventName"])
        self.assertIn("大文件", output["additionalContext"])
        self.assertNotIn("permissionDecision", output)

    def test_failure_record_compact_and_resume_without_stdout_replacement(self):
        raw = "PermissionError password=private"
        result = self.hook(self.event("PostToolUseFailure", tool_name="Bash", error=raw,
                                      tool_input=dict(command="echo password=private")))
        self.assertNotIn("private", result.stdout)
        store = SessionStore(self.root, "one")
        self.assertEqual("PermissionError", store.load()["events"][-1]["summary"])
        self.assertNotIn("private", store.path.read_text(encoding="utf-8"))
        self.assertEqual("", self.hook(self.event("PreCompact")).stdout)
        result = self.hook(self.event("SessionStart", source="compact"))
        self.assertIn("PermissionError", json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"])
        self.assertEqual("", self.hook(self.event("UserPromptSubmit", prompt="password=private")).stdout)

    def test_auto_decision_feedback_correlates_tool_id_and_keeps_cost_unknown(self):
        path = self.root / "large.txt"
        path.write_text("x" * 100001)
        pre_tool(self.store, "Read", dict(file_path=str(path)), self.root, "call-1")
        post_tool(self.store, "Read", {}, {}, tool_use_id="call-1")
        decision = self.store.load()["decisions"][-1]
        self.assertEqual("success", decision["outcome"])
        self.assertIsNone(decision["cost"])
        self.assertIsNone(analyze(self.store)["routing_accuracy"])

    def test_search_recursive_updates_deletes_chinese_and_typos(self):
        nested = self.memory / "nested"
        nested.mkdir()
        path = nested / "record.md"
        path.write_text("# Kubernetes\n" + "padding " * 100 + "部署备份日志", encoding="utf-8")
        index = MemoryIndex(self.memory)
        self.assertEqual("nested/record.md", index.search("kuberntes")[0]["path"])
        self.assertEqual("nested/record.md", index.search("备份")[0]["path"])
        self.assertFalse(index.sync()["rebuilt"])
        path.write_text("new unique content", encoding="utf-8")
        self.assertEqual([], index.search("kubernetes"))
        self.assertEqual(1, len(index.search("unique")))
        path.unlink()
        self.assertEqual([], index.search("unique"))

    def test_search_version_change_fts_fallback_and_malformed_queries(self):
        (self.memory / "a.md").write_text("alpha evidence", encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()) as errors:
            index = MemoryIndex(self.memory, use_fts=False)
            self.assertEqual(1, len(index.search('alpha OR "*')))
        self.assertIn("WARNING", errors.getvalue())
        connection = sqlite3.connect(index.db)
        connection.execute("UPDATE meta SET value='wrong' WHERE key='fingerprint'")
        connection.commit()
        connection.close()
        self.assertTrue(index.sync()["rebuilt"])
        self.assertEqual([], index.search("'"))

    def test_corrupt_index_reports_failure_and_keeps_source(self):
        path = self.memory / "a.md"
        path.write_text("alpha")
        db = self.memory / ".cache/index.db"
        db.parent.mkdir()
        db.write_text("corrupt")
        result = self.cli("search", "alpha")
        self.assertEqual(1, result.returncode)
        self.assertIn("WARNING", result.stderr)
        self.assertEqual("alpha", path.read_text())

    def test_routing_simple_playbook_failure_history_and_ambiguous_fallback(self):
        router = DecisionRouter(ROOT / "memory", self.store)
        cases = [("统计目录文件行数", "use_script"), ("全局安装", "use_playbook"),
                 ("PermissionError 安装", "avoid_known_failure"),
                 ("统计文件行数然后部署", "delegate_to_llm"), ("设计下一代系统", "delegate_to_llm")]
        for task, expected in cases:
            self.assertEqual(expected, router.route(task)["decision"])
        original = router.route("分析非常具体的服务故障", record=True)
        self.assertEqual("delegate_to_llm", router.route(original["task"])["decision"])
        feedback(self.store, original["id"], "success", 42, 0.01)
        self.assertEqual("repeat_previous", router.route(original["task"])["decision"])
        self.assertEqual(1.0, analyze(self.store)["success_rate"])

    def test_playbook_version_selection_confined_and_measured_success_rates(self):
        books = Playbooks(ROOT / "memory")
        self.assertEqual("v1.0", books.load("install-global")["version"])
        self.assertEqual("v1.0", books.load("install-global", "v1.0")["version"])
        with self.assertRaises(ValueError):
            books.load("install-global", "../../evil")
        router = DecisionRouter(ROOT / "memory", self.store)
        first = router.route("全局安装", record=True)
        second = router.route("全局安装", record=True)
        feedback(self.store, first["id"], "success")
        feedback(self.store, second["id"], "failure")
        self.assertEqual(0.5, analyze(self.store)["playbooks"]["install-global@v1.0"]["success_rate"])
        self.assertEqual(1, len(analyze(self.store)["retrospective"]))

    def test_feedback_rejects_unknown_id_and_nonfinite_metrics(self):
        with self.assertRaises(ValueError):
            feedback(self.store, "missing", "success")
        with self.assertRaises(ValueError):
            feedback(self.store, "missing", "success", float("nan"))
        self.assertEqual(1, self.cli("route", "统计文件行数", "--record").returncode)

    def test_summary_stream_preserves_error_samples_and_bounds_context(self):
        result = summarize(iter(["INFO ok\n"] * 1000 + ["ERROR token=private\n", "FAILED suite\n"]))
        self.assertEqual(1002, result["lines"])
        self.assertEqual(2, result["error_lines"])
        self.assertNotIn("private", json.dumps(result))
        self.assertLess(result["summary_bytes"], result["raw_bytes"] * 0.3)

    def test_aggregate_line_counts_literal_search_and_unicode_paths(self):
        nested = self.root / "源码 空格"
        nested.mkdir()
        (nested / "a.py").write_text("a\nb\nneedle\n", encoding="utf-8")
        (nested / "b.py").write_text("last line without newline", encoding="utf-8")
        result = aggregate(nested)
        self.assertEqual(4, result["lines"])
        self.assertEqual(2, result["files"])
        result = aggregate(nested, operation="grep", needle="needle")
        self.assertEqual("a.py", result["results"][0]["path"])
        self.assertEqual(3, result["results"][0]["matches"][0]["line"])

    def test_cache_ttl_integrity_bounded_snippet_and_path_hash(self):
        cache = ContentCache(self.root / "cache")
        cache.put("https://example.test/../../one", "alpha " * 2000, ttl=10, now=100)
        self.assertTrue(cache.get("https://example.test/../../one", "alpha", now=109)["hit"])
        self.assertFalse(cache.get("https://example.test/../../one", now=110)["hit"])
        self.assertEqual(2, self.cli("cache", "get", "absent").returncode)
        path = cache.path("https://example.test/../../one")
        data = json.loads(path.read_text(encoding="utf-8"))
        data["content"] = "tampered"
        atomic_json(path, data)
        with self.assertRaises(ValueError):
            cache.get("https://example.test/../../one", now=101)

    def test_evidence_validation_distinguishes_reference_from_execution(self):
        self.entry()
        query = EvidenceQuery(self.memory, self.root)
        result = query.verify_evidence("claim")
        self.assertEqual("references_valid", result["status"])
        self.assertIn("not verified", result["evidence"][0]["reason"])
        self.assertEqual(["claim.md"], query.find_by_confidence())
        _, metadata = self.entry("bad")
        metadata["evidence"].append(dict(metadata["evidence"][0]))
        metadata["confidence"] = float("nan")
        self.assertTrue(validate(metadata))

    def test_evidence_missing_lines_symbols_traversal_and_source_changes(self):
        query = EvidenceQuery(self.memory, self.root)
        for source in ("missing.py", "source.py:9", "source.py:missing", "../outside.py"):
            self.entry(source=source)
            self.assertEqual("invalid", query.verify_evidence("claim")["evidence"][0]["status"])
        path, metadata = self.entry()
        metadata["evidence"][0]["sha256"] = "0" * 64
        atomic_json(path.with_suffix(".evidence.json"), dict(metadata=metadata))
        self.assertEqual("changed", query.verify_evidence("claim")["evidence"][0]["status"])

    def test_evidence_cycles_related_missing_and_legacy_never_rewritten(self):
        self.entry("a", ["b"])
        self.entry("b", ["a", "missing"])
        query = EvidenceQuery(self.memory, self.root)
        trace = query.trace_evidence_chain("a")
        self.assertEqual("cycle", trace["related"][0]["related"][0]["status"])
        self.assertEqual("invalid", trace["related"][0]["related"][1]["status"])
        legacy = self.memory / "old.md"
        original = "# Historical case\nkeep the facts"
        legacy.write_text(original)
        self.assertIn("old.md", query.audit()["legacy"])
        self.assertEqual(original, legacy.read_text())
        self.assertEqual(1, self.cli("audit", "--strict").returncode)

    def test_evidence_bad_schema_and_missing_reference_make_audit_nonzero(self):
        self.entry(source="missing.py")
        self.assertEqual(1, self.cli("audit").returncode)
        self.assertEqual(1, self.cli("evidence", "verify", "claim").returncode)
        self.assertEqual(1, self.cli("evidence", "trace", "../outside").returncode)

    def test_measurements_keep_bytes_separate_and_reject_empty_or_fake_counts(self):
        measurement = module("scripts/measure-token-savings.py", "runtime_measurement")
        result = measurement.measure([dict(raw_bytes=1000, actual_bytes=200)])
        self.assertEqual(0.8, result["bytes"]["reduction"])
        self.assertIsNone(result["tokens"]["reduction"])
        with self.assertRaises(ValueError):
            measurement.measure([])
        with self.assertRaises(ValueError):
            measurement.measure([dict(raw_tokens=float("nan"), actual_tokens=1)])

    def test_throttle_never_denies_and_reduces_repeated_advice(self):
        emitted = []
        for _ in range(27):
            emitted.append(pre_tool(self.store, "Grep", dict(path="."), self.root))
        self.assertEqual([3, 6, 9, 18, 27], [i for i, advice in enumerate(emitted, 1) if advice])
        self.assertLess(len(emitted[8]), len(emitted[2]))

    def test_irrelevant_tools_and_empty_compact_do_not_create_state(self):
        for tool in ("Bash", "Glob", "Agent", "TaskList"):
            pre_tool(self.store, tool, {}, self.root)
            post_tool(self.store, tool, {}, {}, tool_use_id="untracked")
        self.assertFalse(self.store.path.exists())
        # A separate fresh session exercises no-op protocol events.
        for event in (self.event("PreToolUse", tool_name="Glob"),
                      self.event("PostToolUse", tool_name="Read", tool_use_id="untracked"),
                      self.event("PreCompact")):
            result = self.hook(event)
            self.assertEqual("", result.stdout)
            self.assertEqual("", result.stderr)
        self.assertFalse(SessionStore(self.root, "one").path.exists())

    def test_limited_read_resets_streak_without_repeated_warning(self):
        pre_tool(self.store, "Read", dict(file_path="src/a.py"), self.root)
        pre_tool(self.store, "Read", dict(file_path="src/b.py"), self.root)
        for offset in range(5):
            self.assertIsNone(pre_tool(self.store, "Read", dict(file_path="src/large.py", limit=20, offset=offset * 20), self.root))
        self.assertEqual({}, self.store.load()["streak"])
        self.assertIsNone(pre_tool(self.store, "Read", dict(file_path="src/c.py"), self.root))

    def test_same_large_file_streaming_advice_is_not_repeated(self):
        path = self.root / "large.txt"
        path.write_text("x" * 100001)
        first = pre_tool(self.store, "Read", dict(file_path=str(path)), self.root)
        second = pre_tool(self.store, "Read", dict(file_path=str(path)), self.root)
        third = pre_tool(self.store, "Read", dict(file_path=str(path)), self.root)
        self.assertIn("大文件", first)
        self.assertIsNone(second)
        self.assertIn("批量", third)

    def test_post_event_and_feedback_use_one_write_and_unmatched_feedback_uses_none(self):
        path = self.root / "large.txt"
        path.write_text("x" * 100001)
        pre_tool(self.store, "Read", dict(file_path=str(path)), self.root, "call")
        original = atomic_json
        with patch("taiyi.state.atomic_json", wraps=original) as writes:
            post_tool(self.store, "Read", {}, "PermissionError", failed=True, tool_use_id="call")
            self.assertEqual(1, writes.call_count)
            post_tool(self.store, "Read", {}, {}, tool_use_id="unmatched")
            self.assertEqual(1, writes.call_count)
        self.assertEqual("failure", self.store.load()["decisions"][-1]["outcome"])

    def test_edit_paths_are_relative_to_event_cwd_and_external_paths_are_omitted(self):
        post_tool(self.store, "Edit", dict(file_path="nested.py"), {}, cwd=self.root / "src")
        post_tool(self.store, "Edit", dict(file_path=str(self.root.parent / "external.txt")), {})
        events = self.store.load()["events"]
        self.assertEqual("src/nested.py", events[0]["summary"])
        self.assertEqual("external file edited", events[1]["summary"])
        pre_tool(self.store, "Read", dict(file_path="src/nested.py"), self.root)
        self.assertNotIn(str(self.root), self.store.path.read_text(encoding="utf-8"))

    def test_deep_hook_json_warns_without_traceback(self):
        result = self.hook({}, "[" * 2000 + "0" + "]" * 2000)
        self.assertEqual(0, result.returncode)
        self.assertIn("WARNING", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_non_utf8_aggregation_returns_partial_failure_and_preserves_files(self):
        bad = self.root / "binary.py"
        bad.write_bytes(b"\xff\xfe")
        result = self.cli("aggregate", str(self.root))
        self.assertEqual(1, result.returncode)
        self.assertEqual(1, json.loads(result.stdout)["skipped"])
        self.assertIn("WARNING", result.stderr)
        self.assertEqual(b"\xff\xfe", bad.read_bytes())

    def test_legacy_structured_yaml_needs_sidecar_with_visible_failure(self):
        old = self.memory / "yaml.md"
        original = "---\nname: old\nmetadata:\n  confidence: 0.8\n---\ncase"
        old.write_text(original)
        result = self.cli("audit")
        self.assertEqual(1, result.returncode)
        self.assertIn("sidecar", result.stdout)
        self.assertEqual(original, old.read_text())

    def test_curated_records_have_current_repository_sources(self):
        query = EvidenceQuery(ROOT / "memory/curated", ROOT)
        report = query.audit()
        self.assertEqual(10, report["structured"])
        self.assertEqual([], report["invalid"])
        self.assertEqual([], report["legacy"])

    def test_optional_installer_preserves_personal_settings_and_is_idempotent(self):
        target = self.root / "installed"
        personal = dict(type="command", command="echo personal", timeout=5)
        original = dict(permissions=dict(allow=["Read"]), hooks=dict(PreToolUse=[dict(hooks=[personal])]))
        installer = INSTALL.Installer(target, False)
        components = ["hooks", "context-optimization"]
        merged = installer.merge_settings(original, components)
        self.assertEqual(merged, installer.merge_settings(merged, components))
        self.assertEqual(original["permissions"], merged["permissions"])
        with contextlib.redirect_stdout(io.StringIO()):
            installer.install_files(components)
            installer.write_settings(original, merged)
        result = VERIFY.verify(ROOT, target, components)
        self.assertTrue(result["passed"], result)
        self.assertEqual(5, sum("context-optimizer.py" in h["command"] for groups in merged["hooks"].values()
                                for group in groups for h in group["hooks"]))
        reverted = installer.merge_settings(merged, ["hooks"])
        self.assertFalse(any("context-optimizer.py" in h["command"] for groups in reverted["hooks"].values()
                             for group in groups for h in group["hooks"]))
        self.assertIn(personal, reverted["hooks"]["PreToolUse"][0]["hooks"])
        installed_cli = target / "scripts/taiyi-tool.py"
        proc = subprocess.run([sys.executable, str(installed_cli), "route", "全局安装"],
                              capture_output=True, text=True, encoding="utf-8", cwd=self.root)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual("use_playbook", json.loads(proc.stdout)["decision"])


if __name__ == "__main__":
    unittest.main()

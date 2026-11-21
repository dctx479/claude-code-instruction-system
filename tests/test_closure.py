import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


INSTALL = module("closure_install", "scripts/install-global.py")
MIGRATE = module("closure_migrate", "scripts/migrate-install.py")
USAGE = module("closure_usage", "hooks/usage-tracker.py")
CHECKPOINT = module("closure_checkpoint", "scripts/checkpoint.py")
FACTS = module("closure_facts", "scripts/check-doc-facts.py")
sys.path.insert(0, str(ROOT / "scripts"))
from eval_support import parse_events
from unittest.mock import patch


class ClosureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.target = Path(self.tmp.name).resolve() / "target"
        self.target.mkdir()

    def backup(self, text):
        path = self.target / "settings.json"
        path.write_text(text, encoding="utf-8")
        installer = INSTALL.Installer(self.target, False, backup_retention=2)
        installer.backup(path, "settings.json")
        installer.write_backup_manifest(True)
        return installer

    def test_retention_only_expires_completed_verified_owned_snapshots(self):
        legacy = self.target / "backups/taiyi-install-legacy"
        legacy.mkdir(parents=True)
        (legacy / "personal.txt").write_text("keep")
        snapshots = [self.backup(str(i)) for i in range(4)]
        expired = snapshots[-1].prune_backups()
        self.assertEqual(2, len(expired))
        self.assertTrue((legacy / "personal.txt").exists())
        self.assertTrue(snapshots[-1].backup_dir.is_dir())
        self.assertTrue(snapshots[-2].backup_dir.is_dir())
        self.assertEqual("3", (self.target / "settings.json").read_text())

    def test_retention_preserves_unexpected_modified_and_incomplete_content(self):
        old = self.backup("original")
        (old.backup_dir / "personal.txt").write_text("unknown")
        changed = self.backup("backup")
        (changed.backup_dir / "settings.json").write_text("changed")
        incomplete = self.backup("incomplete")
        incomplete.write_backup_manifest(False)
        newest = self.backup("newest")
        with contextlib.redirect_stderr(io.StringIO()) as err:
            newest.prune_backups()
        self.assertIn("WARNING", err.getvalue())
        for item in (old, changed, incomplete, newest):
            self.assertTrue(item.backup_dir.exists())

    def test_optional_component_only_replacement_preserves_other_managed_hooks(self):
        installer = INSTALL.Installer(self.target, True)
        initial = installer.merge_settings({}, ["hooks", "usage", "lint-feedback"])
        # A stale timeout must be updated, not duplicate the handler on partial installs.
        usage = next(g for g in initial["hooks"]["PostToolUse"] if g["matcher"] == "Skill|Agent|Task")
        usage["hooks"][0]["timeout"] = 1
        merged = installer.merge_settings(initial, ["usage"])
        self.assertEqual(merged, installer.merge_settings(merged, ["usage"]))
        self.assertIn("SessionStart", merged["hooks"])
        self.assertEqual(2, len(merged["hooks"]["PostToolUse"]))
        self.assertEqual(2, len(merged["hooks"]["UserPromptSubmit"]))

    def seed_domain(self):
        folder = self.target / "skills/seedance-prompt"
        folder.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(ROOT / ".claude/skills/seedance-prompt", folder)
        return folder

    def test_migration_is_reversible_and_does_not_delete_project_sources(self):
        folder = self.seed_domain()
        proposed = MIGRATE.plan(self.target, "core", "c9473b8")
        self.assertEqual([], proposed["retained"])
        self.assertEqual(1, len(proposed["moves"]))
        before = MIGRATE.inventory(folder)
        manifest = MIGRATE.apply(self.target, proposed)
        self.assertFalse(folder.exists())
        self.assertTrue((ROOT / ".claude/skills/seedance-prompt/SKILL.md").exists())
        MIGRATE.restore(self.target, manifest)
        self.assertEqual(before, MIGRATE.inventory(folder))

    def test_migration_retains_custom_files_and_restore_refuses_collision(self):
        folder = self.seed_domain()
        (folder / "personal.md").write_text("user notes")
        proposed = MIGRATE.plan(self.target, "core", "c9473b8")
        self.assertEqual([], proposed["moves"])
        self.assertEqual(1, len(proposed["retained"]))
        (folder / "personal.md").unlink()  # Generated fixture file only.
        proposed = MIGRATE.plan(self.target, "core", "c9473b8")
        manifest = MIGRATE.apply(self.target, proposed)
        folder.mkdir()
        with self.assertRaises(ValueError):
            MIGRATE.restore(self.target, manifest)

    def test_migration_refuses_source_changes_after_plan(self):
        folder = self.seed_domain()
        proposed = MIGRATE.plan(self.target, "core", "c9473b8")
        (folder / "SKILL.md").write_text("changed by user")
        with self.assertRaises(ValueError):
            MIGRATE.apply(self.target, proposed)
        self.assertTrue(folder.exists())

    def test_evaluation_pairs_actual_tool_results_instead_of_model_claims(self):
        raw = "\n".join(json.dumps(x) for x in [
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "all checks pass"},
                {"type": "tool_use", "id": "call1", "name": "Bash", "input": {"command": "python -m unittest"}}]}},
            {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "call1", "is_error": True, "content": "test failed"}]}},
            {"type": "result", "is_error": False, "subtype": "success"}])
        events, calls, final = parse_events(raw)
        self.assertEqual(1, len(calls))
        self.assertTrue(calls[0]["result"]["error"])
        self.assertEqual("test failed", calls[0]["result"]["content"])
        self.assertFalse(final["is_error"])
        _, calls, final = parse_events('{bad\n{"type":"assistant","message":{"content":[]}}')
        self.assertEqual([], calls)
        self.assertEqual({}, final)

    def test_migration_rejects_tampered_plan_traversal_before_move(self):
        proposed = dict(target=str(self.target), moves=[dict(path="../outside", files={})])
        with self.assertRaises(ValueError):
            MIGRATE.apply(self.target, proposed)

    def test_usage_counts_explicit_registered_slash_without_recording_arguments(self):
        skill = self.target / "skills/debug/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("registered")
        directory = self.target / "taiyi"
        USAGE.record(dict(hook_event_name="UserPromptSubmit", prompt="/debug secret-prompt-text"), directory)
        USAGE.record(dict(hook_event_name="UserPromptSubmit", prompt="/context private"), directory)
        USAGE.record(dict(hook_event_name="UserPromptSubmit", prompt="ordinary text /debug private"), directory)
        rows = [json.loads(line) for line in (directory / "usage.jsonl").read_text().splitlines()]
        self.assertEqual(1, len(rows))
        self.assertEqual({"ts", "tool", "name"}, set(rows[0]))
        self.assertEqual("debug", rows[0]["name"])
        self.assertEqual("Skill", rows[0]["tool"])

    def test_checkpoint_from_subdirectory_uses_repo_relative_files(self):
        subprocess.run(["git", "init", "-q", str(self.target)], check=True)
        sub = self.target / "sub"
        sub.mkdir()
        (self.target / "artifact.txt").write_text("data")
        CHECKPOINT.save(self.target, dict(goal="test", done=[], next=[], evidence=[], files=["artifact.txt"]))
        self.assertEqual(0, CHECKPOINT.verify(sub))
        CHECKPOINT.save(sub, dict(goal="test", done=[], next=[], evidence=[], files=["artifact.txt"]))
        self.assertEqual(0, CHECKPOINT.verify(self.target))

    def test_checkpoint_rejects_loose_schema_and_device_paths(self):
        for version in (True, 1.0):
            with self.assertRaises(ValueError):
                CHECKPOINT.validate(dict(version=version, goal="x", done=[], next=[], evidence=[], files_sha256={}))
        for name in ("NUL", "CON", "COM9", "C:artifact.txt"):
            with self.assertRaises(ValueError):
                CHECKPOINT.digest(self.target, name)

    def test_checkpoint_deep_json_returns_warning_without_traceback(self):
        subprocess.run(["git", "init", "-q", str(self.target)], check=True)
        path = CHECKPOINT.location(self.target)
        path.parent.mkdir(parents=True)
        path.write_text("[" * 10000 + "]" * 10000)
        proc = subprocess.run([sys.executable, str(ROOT / "scripts/checkpoint.py"), "verify", "--root", str(self.target)],
                              capture_output=True, text=True)
        self.assertEqual(1, proc.returncode)
        self.assertIn("WARNING", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)

    def test_agent_metadata_bad_yaml_is_an_explicit_validation_failure(self):
        path = self.target / "agent.md"
        path.write_text("---\nname: example\ndescription: Example: broken YAML\n---\nBody\n")
        with self.assertRaisesRegex(ValueError, "invalid YAML frontmatter"):
            FACTS.header(path)
        path.write_text('---\nname: example\ndescription: "Example: valid YAML"\n---\nBody\n')
        self.assertEqual("Example: valid YAML", FACTS.header(path)["description"])

    def test_migration_current_files_need_no_historical_git_objects(self):
        self.seed_domain()
        with patch.object(MIGRATE, "historical_files", side_effect=AssertionError("must not read missing shallow history")):
            proposed = MIGRATE.plan(self.target, "core", "c9473b8")
        self.assertEqual(1, len(proposed["moves"]))
        self.assertEqual([], proposed["retained"])


if __name__ == "__main__":
    unittest.main()

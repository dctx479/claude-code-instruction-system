import contextlib
from datetime import datetime, timedelta, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


GUARD = module("guard", "scripts/validate/command_guard.py")
USAGE = module("usage", "hooks/usage-tracker.py")
BACKUP = module("backup", "scripts/hooks/session-backup.py")
CHECKPOINT = module("checkpoint", "scripts/checkpoint.py")
INSTALL = module("install_vnext", "scripts/install-global.py")
VERIFY = module("verify_vnext", "scripts/verify-global-install.py")
LINT = module("lint_feedback", "scripts/hooks/lint-feedback.py")
ISSUES = module("issues", "scripts/validate-issues.py")


class VNextTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_guard_parameter_variants_and_no_command_disclosure(self):
        for command in ("rm -fr /", "rm -r -f ~", "rm --force --recursive /tmp/secret",
                        "echo ok && rm -rf /", "echo ok;rm -fr /", "echo ok\nrm -r -f ~",
                        "sudo mkfs.ext4 /dev/sda", "git -C x push -f"):
            with self.subTest(command=command):
                self.assertTrue(GUARD.blocked(command))
        for command in ("git status", "python scripts/audit-rules.py", "rm file.txt", "grep fdisk docs/file",
                        "echo rm -rf /", "rm -rf build && cat /tmp/report"):
            self.assertEqual("", GUARD.blocked(command))
        event = json.dumps({"tool_input": {"command": "rm -fr /super-secret-token"}})
        process = subprocess.run([sys.executable, str(ROOT / "scripts/validate/command_guard.py")],
                                 input=event, capture_output=True, text=True)
        self.assertEqual(2, process.returncode)
        self.assertIn("WARNING", process.stderr)
        self.assertNotIn("super-secret-token", process.stderr)

    def test_port_helper_runs_only_for_container_commands(self):
        for command, expected in (("git status", 0), ("docker run -p 8080:80 image", 1)):
            event = io.StringIO(json.dumps(dict(tool_input=dict(command=command))))
            with patch.object(sys, "stdin", event), patch.object(GUARD.subprocess, "run") as run:
                run.return_value = subprocess.CompletedProcess([], 0)
                self.assertEqual(0, GUARD.main())
                self.assertEqual(expected, run.call_count)

    def test_usage_privacy_retention_and_contention(self):
        self.root.joinpath("usage.jsonl").write_text(json.dumps(dict(
            ts=(datetime.now(timezone.utc) - timedelta(days=91)).isoformat(), tool="Skill", name="old")) + "\n")
        USAGE.record({"tool_name": "Skill", "tool_input": {"skill": "debug", "args": "secret-prompt"},
                      "cwd": "private-project", "tool_response": "secret-response"}, self.root)
        row = json.loads(self.root.joinpath("usage.jsonl").read_text())
        self.assertEqual({"ts", "tool", "name"}, set(row))
        self.assertEqual("debug", row["name"])
        self.root.joinpath("usage.lock").touch()
        with self.assertRaises(FileExistsError):
            USAGE.record({"tool_name": "Skill", "tool_input": {"skill": "debug"}}, self.root)

    def test_backup_only_prunes_owned_files_and_enforces_limits(self):
        old, first, last, personal = [self.root / n for n in
                                      ("taiyi-old.patch", "taiyi-first.patch", "taiyi-last.patch", "personal.patch")]
        for path in (old, first, last, personal):
            path.write_bytes(b"x" * 8)
        now = time.time()
        os.utime(old, (now - 15 * 86400, now - 15 * 86400))
        os.utime(first, (now - 100, now - 100))
        BACKUP.prune(self.root, now=now, limit=8)
        self.assertFalse(old.exists())
        self.assertFalse(first.exists())
        self.assertTrue(last.exists())
        self.assertTrue(personal.exists())

    def test_checkpoint_absent_valid_changed_and_corrupt(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.assertEqual(2, CHECKPOINT.verify(self.root))
        path = self.root / "artifact.txt"
        path.write_text("before")
        checkpoint = CHECKPOINT.save(self.root, dict(goal="test", done=[], next=["verify"], evidence=[], files=["artifact.txt"]))
        self.assertEqual(0, CHECKPOINT.verify(self.root))
        path.write_text("after")
        with self.assertRaises(ValueError):
            CHECKPOINT.verify(self.root)
        checkpoint.write_text("{broken")
        with self.assertRaises(ValueError):
            CHECKPOINT.verify(self.root)
        with self.assertRaises(ValueError):
            CHECKPOINT.save(self.root, dict(goal="test", done=[], next=[], evidence=[], files=["../secret"]))

    def test_checkpoint_normalizes_root_before_boundary_check(self):
        (self.root / "nested").mkdir()
        (self.root / "artifact.txt").write_bytes(b"artifact")
        expected = CHECKPOINT.digest(self.root.resolve(), "artifact.txt")
        self.assertEqual(expected, CHECKPOINT.digest(self.root / "nested" / "..", "artifact.txt"))

    def test_checkpoint_worktrees_have_distinct_state_and_cli_exit_codes(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        command = [sys.executable, str(ROOT / "scripts/checkpoint.py"), "verify", "--root", str(self.root)]
        absent = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(2, absent.returncode)
        self.assertIn("WARNING", absent.stderr)
        no_hooks = self.root / "no-hooks"
        no_hooks.mkdir()
        subprocess.run(["git", "-C", str(self.root), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "-c", "commit.gpgsign=false", "-c", f"core.hooksPath={no_hooks}",
                        "commit", "--allow-empty", "-qm", "fixture"], check=True)
        linked = self.root / "linked"
        subprocess.run(["git", "-C", str(self.root), "-c", f"core.hooksPath={no_hooks}",
                        "worktree", "add", "-q", "--detach", str(linked)], check=True)
        CHECKPOINT.save(self.root, dict(goal="main", done=[], next=[], evidence=[], files=[]))
        CHECKPOINT.save(linked, dict(goal="linked", done=[], next=[], evidence=[], files=[]))
        self.assertNotEqual(CHECKPOINT.location(self.root).resolve(), CHECKPOINT.location(linked).resolve())
        self.assertEqual(0, CHECKPOINT.verify(self.root))
        self.assertEqual(0, CHECKPOINT.verify(linked))

    def test_guardrails_merge_preserves_custom_rules_and_is_idempotent(self):
        installer = INSTALL.Installer(self.root, True, with_guardrails=True)
        original = dict(permissions={"allow": ["Read"], "ask": ["Bash(custom *)"]}, env={"example": "value"})
        merged = installer.merge_settings(original, ["hooks", "usage"])
        self.assertEqual(["Read"], merged["permissions"]["allow"])
        self.assertIn("Bash(custom *)", merged["permissions"]["ask"])
        self.assertEqual("disable", merged["permissions"]["disableBypassPermissionsMode"])
        self.assertEqual(merged, installer.merge_settings(merged, ["hooks", "usage"]))
        self.assertNotIn("disableBypassPermissionsMode", original["permissions"])
        personal = {"type": "command", "command": 'bash "$HOME/.claude/scripts/personal.sh"'}
        shared = {"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [personal,
            {"type": "command", "command": 'bash "$HOME/.claude/scripts/validate/validate-command.sh"'}]}]}}
        result = installer.merge_settings(shared, ["hooks"])
        self.assertEqual(personal, result["hooks"]["PreToolUse"][0]["hooks"][0])
        with self.assertRaises(ValueError):
            installer.merge_settings({"permissions": {"disableBypassPermissionsMode": "allow"}}, [])

    def test_core_and_optional_profiles_install_and_verify(self):
        for profiles in ("core", "core,ctf,data"):
            target = self.root / profiles.replace(",", "-")
            components = ["hooks", "skills", "agents", "lint-feedback", "usage", "session-backup"]
            installer = INSTALL.Installer(target, False, profiles=profiles, with_guardrails=True)
            with contextlib.redirect_stdout(io.StringIO()):
                settings = installer.merge_settings({}, components)
                installer.install_files(components)
                installer.write_settings({}, settings)
                installer.verify(settings)
            self.assertFalse(installer.problems, installer.problems)
            result = VERIFY.verify(ROOT, target, components, profiles=profiles, with_guardrails=True)
            self.assertTrue(result["passed"], result)
            self.assertTrue((target / "skills/debug/SKILL.md").is_file())
            self.assertEqual("ctf" in profiles, (target / "skills/java-audit/SKILL.md").is_file())
            self.assertFalse((target / "scripts/research").exists())
            self.assertNotIn("PreCompact", settings["hooks"])
        defaults = INSTALL.Installer(self.root, True).merge_settings({}, ["hooks"])
        self.assertNotIn("PostToolUse", defaults["hooks"])
        self.assertNotIn("SessionEnd", defaults["hooks"])

    def test_lint_passes_no_fix_and_preserves_file(self):
        path = self.root / "example.py"
        path.write_bytes(b"x=1\n")
        event = io.StringIO(json.dumps(dict(cwd=str(self.root), tool_input=dict(file_path=str(path)))))
        with patch.object(sys, "stdin", event), patch.object(LINT.shutil, "which", return_value="ruff"), \
                patch.object(LINT.subprocess, "run") as run:
            run.return_value = subprocess.CompletedProcess([], 0, "", "")
            self.assertEqual(0, LINT.main())
            self.assertIn("--no-fix", run.call_args.args[0])
        self.assertEqual(b"x=1\n", path.read_bytes())

    def test_issue_dependencies_reject_cycles_unknown_ids_and_early_start(self):
        import csv
        path = self.root / "issues.csv"
        def write(rows):
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=["id", "title", "acceptance_criteria", "blocked_by", "dev_state"])
                writer.writeheader()
                writer.writerows(rows)
        a = dict(id="A", title="first", acceptance_criteria="python -m unittest", blocked_by="", dev_state="TODO")
        b = dict(id="B", title="second", acceptance_criteria="python -m unittest", blocked_by="A", dev_state="TODO")
        write([a, b])
        self.assertEqual(2, ISSUES.validate(path))
        for changes in ({"blocked_by": "unknown"}, {"dev_state": "DOING"}):
            write([a, dict(b, **changes)])
            with self.assertRaises(ValueError):
                ISSUES.validate(path)
        write([dict(a, blocked_by="B"), b])
        with self.assertRaises(ValueError):
            ISSUES.validate(path)

    def test_agent_tracker_parses_json_escapes_and_warns_on_malformed_input(self):
        (self.root / ".claude").mkdir()
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
        event = json.dumps(dict(tool_name="Agent", cwd=str(self.root), tool_input=dict(subagent_type="debugger")))
        event = event.replace("debugger", "\\u0064ebugger")
        command = [sys.executable, str(ROOT / "hooks/agent-state.py")]
        proc = subprocess.run(command, input=event, env=env, capture_output=True, text=True)
        self.assertEqual(0, proc.returncode)
        self.assertEqual("", proc.stderr)
        self.assertEqual("debugger", json.loads((self.root / ".claude/agent-state.json").read_text())["current_agent"])
        proc = subprocess.run(command, input="{bad", env=env, capture_output=True, text=True)
        self.assertEqual(0, proc.returncode)
        self.assertIn("WARNING", proc.stderr)


if __name__ == "__main__":
    unittest.main()

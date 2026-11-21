import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ralph_state", ROOT / "hooks/ralph-state.py")
RALPH = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RALPH)
BASH = os.environ.get("TAIYI_TEST_BASH") or (
    "C:/Program Files/Git/bin/bash.exe" if os.name == "nt" and
    Path("C:/Program Files/Git/bin/bash.exe").is_file() else shutil.which("bash"))


class RalphTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.project = self.home / "project"
        self.project.mkdir()
        self.path = self.project / "memory/ralph-state.json"
        self.path.parent.mkdir()
        self.state = dict(active=True, iteration=0, max_iterations=2, completed=False,
                          fatal_error=False, needs_confirmation=False, round_complete=False,
                          project_dir=str(self.project), session_id="session-a", metrics={})

    def invoke(self, state=None, raw_input=None, global_state=False, explicit=False):
        if not BASH:
            self.fail("Bash is required")
        path = self.home / ".claude/ralph-state.json" if global_state else self.path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.state if state is None else state), encoding="utf-8")
        env = dict(os.environ, HOME=self.home.as_posix(), CLAUDE_PROJECT_DIR=str(self.project),
                   PYTHONIOENCODING="cp1252")
        env.pop("RALPH_STATE_FILE", None)
        env.pop("RALPH_LOG_FILE", None)
        env.pop("PYTHON_CMD", None)
        if explicit:
            env["RALPH_STATE_FILE"] = str(path)
        proc = subprocess.run([BASH, str(ROOT / "hooks/ralph-stop-interceptor.sh")],
                              input=raw_input if raw_input is not None else '{"session_id":"session-a"}',
                              env=env, capture_output=True, text=True, encoding="utf-8", timeout=20)
        return proc, json.loads(path.read_text(encoding="utf-8"))

    def test_round_then_completion_lifecycle(self):
        self.state["round_complete"] = True
        first, state = self.invoke()
        self.assertEqual(2, first.returncode, first.stderr)
        self.assertEqual(1, state["iteration"])
        self.assertFalse(state["round_complete"])
        self.assertEqual(1, state["metrics"]["total_iterations"])
        state.update(completed=True, round_complete=True)
        second, finished = self.invoke(state)
        self.assertEqual(0, second.returncode, second.stderr)
        self.assertFalse(finished["active"])
        self.assertEqual("COMPLETED", finished["status"])
        third, again = self.invoke(finished)
        self.assertEqual(0, third.returncode)
        self.assertEqual(1, again["metrics"]["successful_runs"])

    def test_mid_round_does_not_increment(self):
        proc, state = self.invoke()
        self.assertEqual(2, proc.returncode)
        self.assertEqual(0, state["iteration"])

    def test_max_iterations_stops(self):
        self.state.update(iteration=2, round_complete=True)
        proc, state = self.invoke()
        self.assertEqual(0, proc.returncode)
        self.assertEqual("FAILED", state["status"])
        self.assertTrue(state["max_iterations_reached"])

    def test_final_round_does_not_start_one_more_round(self):
        self.state.update(iteration=1, max_iterations=2, round_complete=True)
        proc, state = self.invoke()
        self.assertEqual(0, proc.returncode, "two completed rounds must not start a third")
        self.assertFalse(state["active"])
        self.assertTrue(state["max_iterations_reached"])

    def test_confirmation_pauses(self):
        self.state["needs_confirmation"] = True
        proc, state = self.invoke()
        self.assertEqual(0, proc.returncode)
        self.assertEqual("PAUSED", state["status"])
        self.assertTrue(state["active"])

    def test_fatal_stops(self):
        self.state["fatal_error"] = True
        proc, state = self.invoke()
        self.assertEqual(0, proc.returncode)
        self.assertEqual("FAILED", state["status"])
        self.assertFalse(state["active"])

    def test_global_other_project_ignored(self):
        self.state["project_dir"] = str(self.home / "other")
        proc, state = self.invoke(global_state=True)
        self.assertEqual(0, proc.returncode)
        self.assertEqual(self.state, state)

    def test_unscoped_global_ignored_even_with_explicit_path(self):
        self.state.pop("project_dir")
        proc, state = self.invoke(global_state=True, explicit=True)
        self.assertEqual(0, proc.returncode)
        self.assertIn("WARNING", proc.stderr)
        self.assertEqual(self.state, state)

    def test_other_session_ignored(self):
        proc, state = self.invoke(raw_input='{"session_id":"session-b"}')
        self.assertEqual(0, proc.returncode)
        self.assertEqual(self.state, state)

    def test_invalid_input_warns_without_claiming_completion(self):
        proc, state = self.invoke(raw_input="{bad")
        self.assertEqual(0, proc.returncode)
        self.assertIn("WARNING", proc.stderr)
        self.assertEqual(self.state, state)
        self.assertNotIn("COMPLETED", proc.stdout)

    def test_invalid_state_is_not_treated_as_completed(self):
        self.state.update(completed=True, iteration="bad")
        proc, state = self.invoke()
        self.assertEqual(0, proc.returncode)
        self.assertIn("WARNING", proc.stderr)
        self.assertNotIn("COMPLETED", proc.stdout)
        self.assertEqual(self.state, state)

    def test_write_failure_warns_and_never_blocks_or_claims_completion(self):
        self.state["completed"] = True
        self.path.write_text(json.dumps(self.state), encoding="utf-8")
        stderr, stdout = io.StringIO(), io.StringIO()
        with mock.patch.object(RALPH.os, "replace", side_effect=PermissionError("locked")):
            with contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(stdout):
                code = RALPH.run(self.home, self.project, {"session_id": "session-a"})
        self.assertEqual(0, code)
        self.assertIn("WARNING", stderr.getvalue())
        self.assertNotIn("COMPLETED", stdout.getvalue())
        self.assertEqual(self.state, json.loads(self.path.read_text(encoding="utf-8")))
        self.assertEqual([], list(self.path.parent.glob("*.tmp")))

    def test_missing_helper_does_not_masquerade_as_continue_exit_two(self):
        fixture = self.home / "broken-install"
        fixture.mkdir()
        script = fixture / "ralph-stop-interceptor.sh"
        script.write_bytes((ROOT / "hooks/ralph-stop-interceptor.sh").read_bytes())
        proc = subprocess.run([BASH, str(script)], input="{}", capture_output=True,
                              text=True, encoding="utf-8", timeout=20)
        self.assertEqual(0, proc.returncode)
        self.assertIn("WARNING", proc.stderr)

    def test_argument_error_exit_two_is_not_a_continue_signal(self):
        stderr = io.StringIO()
        with mock.patch.object(RALPH.sys, "argv", ["ralph-state", "--unknown"]):
            with contextlib.redirect_stderr(stderr):
                code = RALPH.main()
        self.assertEqual(0, code)
        self.assertIn("WARNING", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()

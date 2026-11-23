"""Exercise the installed HUD interface with real JSON, isolated state and Git."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("taiyi_hud", ROOT / ".claude/statusline/hud.py")
HUD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(HUD)


class StatuslineTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="taiyi-hud-test-")
        self.root = Path(self.temporary.name)
        self.home = self.root / "home"
        self.project = self.root / "项目 空格"
        self.project.mkdir()
        self.env = dict(os.environ, HOME=str(self.home), CLAUDE_PROJECT_DIR=str(self.project),
                        HUD_CONFIG_FILE=str(self.home / ".claude/hud-config.json"),
                        HUD_CACHE_DIR=str(self.home / ".claude/cache"), COLUMNS="240")
        for key in ("HUD_THEME", "HUD_WIDTH", "HUD_SESSION_JSON", "CLAUDE_AGENT", "CLAUDE_MODEL", "CLAUDE_TASK", "CLAUDE_PROGRESS", "NO_COLOR"):
            self.env.pop(key, None)
        self.config = dict(colors=dict(enabled=False), modules=dict(git=dict(enabled=False)), width=220)
        self.data = dict(session_id="one", cwd=str(self.project), model=dict(id="claude-sonnet-4-6", display_name="Sonnet 4.6"),
                         context_window=dict(used_percentage=85, total_input_tokens=12000, total_output_tokens=500),
                         cost=dict(total_cost_usd=0.125))

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def cli(self, raw=None, action="render", wrapper=False, env=None):
        self.write(Path(self.env["HUD_CONFIG_FILE"]), self.config)
        if wrapper:
            bash = "C:/Program Files/Git/bin/bash.exe" if os.name == "nt" else shutil.which("bash")
            if not bash:
                self.skipTest("Bash unavailable")
            command = [bash, str(ROOT / ".claude/statusline/hud.sh"), action]
        else:
            command = [sys.executable, str(ROOT / ".claude/statusline/hud.py"), action]
        return subprocess.run(command, input=json.dumps(self.data, ensure_ascii=False) if raw is None else raw,
                              text=True, encoding="utf-8", capture_output=True, env=env or self.env,
                              cwd=self.project, timeout=15)

    def renderer(self, data=None, config=None, env=None):
        return HUD.Renderer(self.data if data is None else data, self.config if config is None else config,
                            self.env if env is None else env, self.project)

    def init_git(self, directory, branch="main"):
        directory.mkdir(parents=True, exist_ok=True)
        for args in (["init", "-q", "-b", branch], ["config", "user.name", "HUD fixture"],
                     ["config", "user.email", "hud@example.invalid"]):
            subprocess.run(["git", "-C", str(directory), *args], check=True, capture_output=True)
        (directory / "tracked.txt").write_text("original\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(directory), "add", "tracked.txt"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(directory), "commit", "-qm", "fixture"], check=True, capture_output=True)

    def test_pretty_and_compact_json_display_same_metrics(self):
        for raw in (json.dumps(self.data, indent=2), json.dumps(self.data, separators=(",", ":"))):
            result = self.cli(raw)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("CTX:85%", result.stdout)
            self.assertIn("12.0Ki/500o", result.stdout)
            self.assertIn("$0.125", result.stdout)
            self.assertIn("项目 空格", result.stdout)
            self.assertEqual("", result.stderr)

    def test_zero_missing_and_unknown_cost_never_gate_valid_payload(self):
        self.data["cost"]["total_cost_usd"] = 0
        self.assertIn("$0.000", self.cli().stdout)
        self.data.pop("cost")
        self.assertIn("$?", self.cli().stdout)
        self.data.pop("context_window")
        output = self.cli().stdout
        self.assertIn("CTX:?", output)
        self.assertIn("?i/?o", output)
        self.assertNotIn("@orchestrator", output)

    def test_explicit_legacy_gate_remains_available(self):
        self.config["display"] = dict(hide_zero_cost=True)
        self.data["cost"]["total_cost_usd"] = 0
        self.assertEqual("", self.cli().stdout)
        self.data["cost"]["total_cost_usd"] = 0.2
        self.assertIn("Sonnet", self.cli().stdout)

    def test_context_uses_reported_window_and_cache_input_counts(self):
        self.data["context_window"] = dict(context_window_size=1000000,
            current_usage=dict(input_tokens=100000, cache_read_input_tokens=300000, cache_creation_input_tokens=50000, output_tokens=150))
        result = self.cli()
        self.assertIn("CTX:45%", result.stdout)
        self.assertIn("450.0Ki/150o", result.stdout)

    def test_all_module_false_flags_and_git_suboptions_are_respected(self):
        self.config["modules"] = {name: dict(enabled=False) for name in HUD.NAMES}
        with patch.object(HUD.Renderer, "git", side_effect=AssertionError("Git should be lazy")):
            self.assertEqual("", self.renderer().render())
        self.config["modules"]["git"] = dict(enabled=True, show_branch=False, show_status=False, show_ahead_behind=False)
        with patch.object(HUD.Renderer, "git", side_effect=AssertionError("hidden Git should not run")):
            self.assertEqual("", self.renderer().render())

    def test_colors_and_themes_apply_without_forcing_ansi(self):
        self.config["theme"] = "nerd"
        self.assertIn("┃", self.cli().stdout)
        self.assertNotIn("\x1b", self.cli().stdout)
        self.config["colors"] = dict(enabled=True, context_warn="red")
        self.assertIn("\x1b[31mCTX:85%", self.cli().stdout)
        self.assertNotIn("\x1b", self.cli(env=dict(self.env, NO_COLOR="1")).stdout)
        renderer = HUD.Renderer(self.data, self.config, self.env, theme="minimal")
        self.assertIn(" | ", renderer.render())

    def test_model_blue_uses_bright_bold_color_on_dark_background(self):
        self.config["colors"] = dict(enabled=True, model_sonnet="blue")
        result = self.cli()
        self.assertIn("\x1b[1;97mSonnet 4.6\x1b[0m", result.stdout)
        self.config["modules"]["model"] = dict(high_contrast=False)
        self.assertIn("\x1b[34mSonnet 4.6\x1b[0m", self.cli().stdout)
        self.assertNotIn("\x1b", self.cli(env=dict(self.env, NO_COLOR="1")).stdout)

    def test_blank_model_name_falls_back_to_reported_id(self):
        self.data["model"] = dict(display_name=" \t\x1b[34m\x1b[0m ", id="provider-model-5")
        self.assertIn("provider-model-5", self.cli().stdout)
        self.data["model"]["id"] = "claude-sonnet-4-6"
        self.assertIn("Sonnet 4.6", self.cli().stdout)

    def test_narrow_statusline_preserves_model_before_project_and_git_labels(self):
        self.data["context_window"]["used_percentage"] = 50
        renderer = self.renderer(env=dict(self.env, COLUMNS="26", HUD_WIDTH="auto"))
        output = renderer.render()
        self.assertIn("Sonnet 4.6", output)
        self.assertIn("CTX:50%", output)
        self.assertLessEqual(HUD.cells(output), 22)

    def test_cjk_width_reserves_host_padding_and_keeps_context(self):
        self.config["modules"]["project"] = dict(max_length=30)
        self.data["cwd"] = str(self.root / ("中文" * 30))
        output = self.renderer(env=dict(self.env, COLUMNS="35", HUD_WIDTH="auto")).render()
        self.assertLessEqual(HUD.cells(output), 31)
        self.assertIn("CTX:85%", output)
        self.assertIn("…", output)

    def test_priority_excludes_performance_before_reading_it(self):
        self.config["display"] = dict(priority_threshold=1)
        self.config["modules"]["performance"] = dict(enabled=True, priority=3)
        renderer = self.renderer(env=dict(self.env, COLUMNS="90", HUD_WIDTH="auto"))
        original = renderer.segment
        def segment(name):
            if name == "performance":
                self.fail("hidden performance segment evaluated")
            return original(name)
        with patch.object(renderer, "segment", side_effect=segment):
            renderer.render()

    def test_control_characters_in_model_and_task_cannot_escape_statusline(self):
        self.data["model"]["display_name"] = "Sonnet\x1b]52;secret\x07\nnext"
        result = self.cli(env=dict(self.env, CLAUDE_TASK="task\r\n\x1b[31mcolored"))
        self.assertEqual(0, result.returncode)
        self.assertNotIn("\x1b", result.stdout)
        self.assertEqual(1, len(result.stdout.splitlines()))

    def test_progress_is_clamped_and_uses_configured_bar(self):
        self.config["modules"]["progress"] = dict(enabled=True, bar_width=4, show_percentage=False)
        self.assertIn("[####]", self.cli(env=dict(self.env, CLAUDE_PROGRESS="150")).stdout)
        result = self.cli(env=dict(self.env, CLAUDE_PROGRESS="wrong"))
        self.assertIn("WARNING", result.stderr)
        self.assertNotIn("wrong", result.stdout)

    def test_agent_and_slash_command_are_session_scoped(self):
        key = hashlib.sha256((self.data["cwd"] + "\0one").encode()).hexdigest()
        state = self.home / ".claude/intent-sessions" / (key + ".json")
        self.write(state, dict(cwd=self.data["cwd"], session_id="other", agent="wrong"))
        self.write(self.home / ".claude/intent-state.json", dict(agent="wrong-global"))
        self.assertNotIn("@wrong", self.cli().stdout)
        self.write(state, dict(cwd=self.data["cwd"], session_id="one", agent="debugger"))
        self.assertIn("@debugger", self.cli().stdout)
        self.write(state, dict(cwd=self.data["cwd"], session_id="one", agent="", skill="route"))
        self.assertIn("/route", self.cli().stdout)

    def test_agent_hook_records_provenance_and_hud_reads_it(self):
        (self.project / ".claude").mkdir()
        event = dict(cwd=str(self.project), session_id="one", tool_name="Agent", tool_input=dict(subagent_type="debugger"))
        result = subprocess.run([sys.executable, str(ROOT / "hooks/agent-state.py")], input=json.dumps(event),
                                capture_output=True, text=True, env=self.env, encoding="utf-8")
        self.assertEqual(0, result.returncode)
        self.assertIn("@debugger", self.cli().stdout)
        self.data["session_id"] = "two"
        self.assertNotIn("@debugger", self.cli().stdout)

    def test_ralph_global_other_project_and_other_session_are_ignored(self):
        path = self.home / ".claude/ralph-state.json"
        self.write(path, dict(active=True, iteration=2, max_iterations=5, project_dir=str(self.root / "elsewhere")))
        self.assertNotIn("R:", self.cli().stdout)
        self.write(path, dict(active=True, iteration=2, max_iterations=5, project_dir=str(self.project), session_id="two"))
        self.assertNotIn("R:", self.cli().stdout)
        self.write(self.project / "memory/ralph-state.json", dict(active=True, iteration=1, max_iterations=3, session_id="one"))
        self.assertIn("R:1/3", self.cli().stdout)

    def test_invalid_json_never_leaks_input(self):
        for raw in ("{secret", "[]", "[" * 2000 + "0" + "]" * 2000):
            result = self.cli(raw)
            self.assertEqual(1, result.returncode)
            self.assertIn("WARNING", result.stderr)
            self.assertNotIn("secret", result.stderr + result.stdout)
            self.assertEqual("HUD unavailable\n", result.stdout)

    def test_malformed_config_warns_and_falls_back(self):
        path = Path(self.env["HUD_CONFIG_FILE"])
        path.parent.mkdir(parents=True)
        path.write_text("{broken", encoding="utf-8")
        with patch("sys.stderr") as errors:
            renderer = HUD.Renderer(self.data, env=self.env)
            output = renderer.render()
        self.assertIn("Sonnet", output)
        self.assertTrue(errors.write.called)

    def test_git_cache_isolated_by_cwd_and_respects_disable_and_ttl(self):
        first, second = self.root / "one", self.root / "two"
        self.init_git(first, "first")
        self.init_git(second, "second")
        config = dict(self.config, cache=dict(enabled=True, git_ttl=60), performance=dict(max_execution_time=3000))
        config["modules"] = dict(git=dict(enabled=True))
        data = dict(self.data, cwd=str(first))
        renderer = self.renderer(data, config)
        self.assertIn("first", renderer.git())
        with patch("subprocess.run", side_effect=AssertionError("warm cache ran Git")):
            self.assertIn("first", self.renderer(data, config).git())
        self.assertIn("second", self.renderer(dict(data, cwd=str(second)), config).git())
        self.assertEqual(2, len(list(Path(self.env["HUD_CACHE_DIR"]).glob("taiyi-hud-git-*.json"))))
        config["cache"]["enabled"] = False
        with patch("subprocess.run", wraps=subprocess.run) as calls:
            self.renderer(data, config).git()
            self.assertEqual(1, calls.call_count)
        config["cache"] = dict(enabled=True, git_ttl=0)
        with patch("subprocess.run", wraps=subprocess.run) as calls:
            self.renderer(data, config).git()
            self.assertEqual(1, calls.call_count)

    def test_git_clean_dirty_detached_and_no_upstream(self):
        self.init_git(self.project)
        config = dict(self.config, cache=dict(enabled=False), performance=dict(max_execution_time=3000))
        renderer = self.renderer(config=config)
        self.assertEqual("main ✓", renderer.git())
        (self.project / "new.txt").write_text("new\n")
        self.assertIn("main *", self.renderer(config=config).git())
        subprocess.run(["git", "-C", str(self.project), "checkout", "--detach", "-q"], check=True)
        self.assertIn("(detached)", self.renderer(config=config).git())

    def test_non_git_directory_is_normal_and_timeout_is_unknown(self):
        self.assertEqual("", self.renderer().git())
        renderer = self.renderer()
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("git", 0.1)), patch("sys.stderr") as errors:
            self.assertEqual("GIT:?", renderer.git())
            self.assertTrue(errors.write.called)

    def test_malformed_cache_is_refreshed_instead_of_claiming_clean(self):
        self.init_git(self.project)
        config = dict(self.config, performance=dict(max_execution_time=3000))
        self.renderer(config=config).git()
        cache = next(Path(self.env["HUD_CACHE_DIR"]).glob("taiyi-hud-git-*.json"))
        cache.write_text(json.dumps(dict(version=1, cwd=HUD.normalized(self.project), ts=time.time(), git={})))
        with patch("sys.stderr") as errors:
            self.assertEqual("main ✓", self.renderer(config=config).git())
            self.assertTrue(errors.write.called)

    def test_cache_clear_preserves_unowned_files(self):
        directory = Path(self.env["HUD_CACHE_DIR"])
        directory.mkdir(parents=True)
        other = directory / "project-name.cache"
        other.write_text("other renderer")
        unknown = directory / ("taiyi-hud-git-" + "a" * 64 + ".json")
        unknown.write_text("{}")
        owned = directory / ("taiyi-hud-git-" + "b" * 64 + ".json")
        self.write(owned, dict(owner="taiyi-hud", version=1))
        result = self.cli(action="cache-clear")
        self.assertEqual(0, result.returncode)
        self.assertTrue(other.exists())
        self.assertTrue(unknown.exists())
        self.assertFalse(owned.exists())
        self.assertIn("WARNING", result.stderr)

    def test_shell_entry_and_nonrender_commands_handle_unicode_and_empty_input(self):
        result = self.cli(wrapper=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("CTX:85%", result.stdout)
        for action in ("version", "config", "help", "full"):
            result = self.cli(raw="", action=action, wrapper=True)
            self.assertEqual(0, result.returncode, result.stderr)

    def test_installer_upgrades_managed_entry_and_preserves_custom_command(self):
        spec = importlib.util.spec_from_file_location("hud_installer", ROOT / "scripts/install-global.py")
        installer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(installer_module)
        installer = installer_module.Installer(self.root / "install", True)
        legacy = dict(type="command", command='bash "$HOME/.claude/statusline/hud.sh" render')
        result = installer.merge_settings(dict(statusLine=legacy, permissions=dict(allow=["Read"])), ["statusline"])
        self.assertEqual(installer_module.STATUSLINE_COMMAND, result["statusLine"]["command"])
        self.assertEqual(["Read"], result["permissions"]["allow"])
        custom = dict(type="command", command="custom-statusline")
        self.assertEqual(custom, installer.merge_settings(dict(statusLine=custom), ["statusline"])["statusLine"])
        self.assertEqual(result, installer.merge_settings(result, ["statusline"]))

    def test_statusline_install_includes_python_and_preserves_hud_config(self):
        spec = importlib.util.spec_from_file_location("hud_install_files", ROOT / "scripts/install-global.py")
        installer_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(installer_module)
        target = self.root / "installed/.claude"
        self.write(target / "hud-config.json", self.config)
        installer = installer_module.Installer(target, False)
        installer.install_files(["statusline"])
        self.assertEqual(self.config, json.loads((target / "hud-config.json").read_text(encoding="utf-8")))
        self.assertTrue((target / "statusline/hud.py").is_file())
        self.assertTrue((target / "statusline/hud.sh").is_file())
        result = subprocess.run([sys.executable, "-S", str(target / "statusline/hud.py"), "render"],
                  input=json.dumps(self.data), text=True, encoding="utf-8", capture_output=True,
                  env=dict(self.env, HUD_CONFIG_FILE=str(target / "hud-config.json")), cwd=self.project)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("CTX:85%", result.stdout)

    @unittest.skipUnless(os.name == "nt", "MSYS Windows path mapping")
    def test_msys_home_and_project_paths_map_to_native_windows(self):
        home = "/" + self.home.drive[0].lower() + self.home.as_posix()[2:]
        project = "/" + self.project.drive[0].lower() + self.project.as_posix()[2:]
        data = dict(self.data, cwd=project, workspace=dict(current_dir=project, project_dir=project))
        renderer = self.renderer(data, env=dict(self.env, HOME=home))
        self.assertEqual(self.home, renderer.home)
        self.assertEqual(self.project, renderer.cwd)


if __name__ == "__main__":
    unittest.main()

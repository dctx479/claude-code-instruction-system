"""Behavioral checks for the Codex installer, with isolated destinations."""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("taiyi_install", ROOT / "scripts/codex/install.py")
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = installer.build_plan(ROOT)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name) / ".agents"

    def test_default_commands_and_resource_paths(self):
        installer.install(self.plan, self.base)
        commands = [p for p in (ROOT / "commands").rglob("*.md") if p.name != "INDEX.md"]
        skills = list((self.base / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(skills), len(commands) + 1)
        for command in commands:
            skill = self.base / "skills" / f"taiyi-{command.stem}" / "SKILL.md"
            self.assertTrue(skill.is_file())
            relative = Path("../../taiyi-system") / command.relative_to(ROOT)
            self.assertEqual((skill.parent / relative).read_bytes(), command.read_bytes())
        self.assertTrue((self.base / "taiyi-system/codex/runtime.md").is_file())
        self.assertFalse((self.base.parent / ".codex").exists())
        self.assertFalse((self.base.parent / "AGENTS.md").exists())

    def test_dry_run_writes_nothing(self):
        count, backup = installer.install(self.plan, self.base, dry_run=True)
        self.assertGreater(count, 0)
        self.assertIsNone(backup)
        self.assertFalse(self.base.exists())

    def test_reinstall_is_idempotent_and_preserves_unrelated_files(self):
        installer.install(self.plan, self.base)
        unrelated = self.base / "skills/custom/SKILL.md"
        unrelated.parent.mkdir()
        unrelated.write_text("user skill", encoding="utf-8")
        count, backup = installer.install(self.plan, self.base)
        self.assertEqual(count, 0)
        self.assertIsNone(backup)
        self.assertEqual(unrelated.read_text(), "user skill")

    def test_conflict_preflight_does_not_partially_install(self):
        target = self.base / "skills/taiyi-review/SKILL.md"
        target.parent.mkdir(parents=True)
        target.write_text("user instructions", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "no files changed"):
            installer.install(self.plan, self.base)
        self.assertEqual(target.read_text(), "user instructions")
        self.assertFalse((self.base / "taiyi-system").exists())

    def test_force_backs_up_exact_old_content(self):
        installer.install(self.plan, self.base)
        relative = Path("skills/taiyi-review/SKILL.md")
        (self.base / relative).write_bytes(b"user instructions\n")
        count, backup = installer.install(self.plan, self.base, force=True)
        self.assertEqual(count, 1)
        self.assertEqual((backup / relative).read_bytes(), b"user instructions\n")
        self.assertEqual((self.base / relative).read_bytes(), self.plan[relative])

    def test_nested_skills_include_scripts_and_references(self):
        plan = installer.build_plan(ROOT, selected_skills=["php-sql-audit", "debug"])
        installer.install(plan, self.base)
        nested = Path(".claude/skills/php-audit/php-sql-audit/SKILL.md")
        self.assertEqual((self.base / "taiyi-system" / nested).read_bytes(), (ROOT / nested).read_bytes())
        for source in (ROOT / ".claude/skills").rglob("*.py"):
            self.assertEqual((self.base / "taiyi-system" / source.relative_to(ROOT)).read_bytes(), source.read_bytes())
        self.assertTrue((self.base / "skills/taiyi-skill-php-sql-audit/SKILL.md").is_file())

    def test_unknown_skill_fails_before_writes(self):
        with self.assertRaisesRegex(ValueError, "Unknown skills"):
            installer.build_plan(ROOT, selected_skills=["does-not-exist"])
        self.assertFalse(self.base.exists())

    def test_all_agents_and_skills_have_unique_valid_names(self):
        plan = installer.build_plan(ROOT, with_agents=True, with_skills=True)
        for path in plan:
            if path.parts[0] == "skills":
                self.assertRegex(path.parts[1], r"^[a-z0-9-]{1,63}$")
        self.assertGreater(sum(p.parts[0] == "skills" for p in plan), 100)

    def test_manifest_retains_earlier_optional_installs(self):
        plan = installer.build_plan(ROOT, selected_skills=["debug"])
        installer.install(plan, self.base)
        count, _ = installer.install(self.plan, self.base)
        self.assertEqual(count, 0)
        manifest = json.loads((self.base / installer.MANIFEST).read_text())
        self.assertIn("skills/taiyi-skill-debug/SKILL.md", manifest["files"])

    def test_refuses_symlink_and_file_parents(self):
        elsewhere = Path(self.temp.name) / "elsewhere"
        elsewhere.mkdir()
        self.base.symlink_to(elsewhere, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            installer.install(self.plan, self.base, force=True)
        self.assertEqual(list(elsewhere.iterdir()), [])
        self.base.unlink()
        self.base.mkdir()
        (self.base / "skills").write_text("not a directory")
        with self.assertRaisesRegex(ValueError, "not a directory"):
            installer.install(self.plan, self.base, force=True)

    def test_rejects_path_traversal(self):
        with self.assertRaisesRegex(ValueError, "Unsafe installation path"):
            installer.install({Path("../outside"): b"bad"}, self.base)
        self.assertFalse(self.base.exists())

    def test_force_dry_run_leaves_conflicts_and_backups_untouched(self):
        target = self.base / "skills/taiyi-review/SKILL.md"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"custom instructions")
        count, backup = installer.install(self.plan, self.base, force=True, dry_run=True)
        self.assertGreater(count, 0)
        self.assertIsNone(backup)
        self.assertEqual(target.read_bytes(), b"custom instructions")
        self.assertFalse((self.base / "taiyi-backups").exists())

    def test_cli_user_install_keeps_codex_home_untouched(self):
        home = Path(self.temp.name) / "home with spaces"
        home.mkdir()
        codex_home = home / "custom-codex-profile"
        env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), CODEX_HOME=str(codex_home))
        command = [sys.executable, str(ROOT / "scripts/codex/install.py"), "--user", "--skill", "debug"]
        preview = subprocess.run(command + ["--dry-run"], env=env, capture_output=True, text=True)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertFalse((home / ".agents").exists())
        result = subprocess.run(command, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((home / ".agents/skills/taiyi-skill-debug/SKILL.md").is_file())
        self.assertFalse(codex_home.exists())
        self.assertFalse((home / ".codex").exists())

    def test_cli_project_path_with_spaces(self):
        project = Path(self.temp.name) / "project with spaces"
        result = subprocess.run([sys.executable, str(ROOT / "scripts/codex/install.py"),
                                 "--project", str(project)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((project / ".agents/skills/taiyi-review/SKILL.md").is_file())

    def test_global_entry_preserves_existing_rules_and_backs_up(self):
        profile = Path(self.temp.name) / "codex"
        profile.mkdir()
        target = profile / "AGENTS.md"
        original = b"# Existing rules\nKeep my settings.\n"
        target.write_bytes(original)
        entry = installer.global_entry(profile, self.base)
        backup = installer.write_global_entry(*entry)
        self.assertEqual(backup.read_bytes(), original)
        self.assertTrue(target.read_bytes().startswith(original))
        self.assertIn(str(self.base / "taiyi-system/codex/runtime.md").encode(), target.read_bytes())
        before = target.read_bytes()
        self.assertIsNone(installer.write_global_entry(*installer.global_entry(profile, self.base)))
        self.assertEqual(target.read_bytes(), before)

    def test_global_uses_override_without_changing_base_rules(self):
        profile = Path(self.temp.name) / "codex"
        profile.mkdir()
        (profile / "AGENTS.md").write_bytes(b"base rules")
        override = profile / "AGENTS.override.md"
        override.write_bytes(b"override rules")
        entry = installer.global_entry(profile, self.base)
        self.assertEqual(entry[0], override)
        installer.write_global_entry(*entry)
        self.assertEqual((profile / "AGENTS.md").read_bytes(), b"base rules")
        self.assertTrue(override.read_bytes().startswith(b"override rules"))

    def test_global_cli_respects_custom_profile_and_dry_run(self):
        home = Path(self.temp.name) / "user"
        profile = home / "custom profile"
        env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), CODEX_HOME=str(profile))
        command = [sys.executable, str(ROOT / "scripts/codex/install.py"), "--global"]
        preview = subprocess.run(command + ["--dry-run"], env=env, capture_output=True, text=True)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertFalse(home.exists())
        result = subprocess.run(command, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((profile / "AGENTS.md").is_file())
        self.assertTrue((home / ".agents/skills/taiyi-core/SKILL.md").is_file())
        self.assertFalse((profile / "config.toml").exists())

    def test_global_invalid_markers_prevent_installation(self):
        home = Path(self.temp.name) / "user"
        profile = home / ".codex"
        profile.mkdir(parents=True)
        (profile / "AGENTS.md").write_bytes(installer.GLOBAL_START)
        env = dict(os.environ, HOME=str(home), USERPROFILE=str(home), CODEX_HOME=str(profile))
        result = subprocess.run([sys.executable, str(ROOT / "scripts/codex/install.py"), "--global"],
                                env=env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((home / ".agents").exists())


if __name__ == "__main__":
    unittest.main()

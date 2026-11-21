import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


AUDIT = module("audit_rules", "scripts/audit-rules.py")
VERIFY = module("verify_install", "scripts/verify-global-install.py")


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def codes(self):
        return {f["code"] for f in AUDIT.audit(self.root)["findings"]}

    def test_valid_import_is_read_only(self):
        self.write("CLAUDE.md", "@AGENTS.md\n")
        path = self.write("AGENTS.md", "Use `scripts/run.py`.\n")
        self.write("scripts/run.py", "raise RuntimeError('never execute this')\n")
        before = path.read_bytes()
        result = AUDIT.audit(self.root)
        self.assertEqual([], result["findings"])
        self.assertEqual(2, len(result["files"]))
        self.assertEqual(before, path.read_bytes())

    def test_missing_and_cyclic_imports(self):
        self.write("CLAUDE.md", "@missing.md\n@AGENTS.md\n")
        self.write("AGENTS.md", "@CLAUDE.md\n")
        self.assertTrue({"missing-import", "import-cycle"} <= self.codes())

    def test_external_import_not_read(self):
        self.write("CLAUDE.md", "@../outside.md\n")
        # Even when outside exists, the audit must not read its contents.
        with tempfile.TemporaryDirectory(dir=self.root) as nested:
            nested = Path(nested)
            self.write("outside.md", "secret\n")
            (nested / "CLAUDE.md").write_text("@../outside.md\n", encoding="utf-8")
            report = AUDIT.audit(nested)
            self.assertEqual(["external-import"], [f["code"] for f in report["findings"]])
            self.assertEqual(1, len(report["files"]))

    def test_contextual_path_is_review_not_deletion(self):
        self.write("AGENTS.md", "See `generics/legacy/`.\n")
        findings = AUDIT.audit(self.root)["findings"]
        self.assertEqual("review", findings[0]["level"])

    def test_missing_bare_filename_is_reported(self):
        self.write("AGENTS.md", "Read `missing.md`.\n")
        self.assertIn("path-unresolved", self.codes())

    def test_local_and_root_paths(self):
        self.write("sub/AGENTS.md", "See `local.md` and `docs/root.md`.\n")
        self.write("sub/local.md", "ok")
        self.write("docs/root.md", "ok")
        self.assertEqual(set(), self.codes())

    def test_command_checks_and_manifest_scope(self):
        self.write("AGENTS.md", "```bash\npython scripts/missing.py\nnpm run test\n```\n")
        self.write("child/package.json", '{"scripts":{"test":"true"}}')
        self.assertTrue({"missing-command-file", "command-unresolved"} <= self.codes())
        self.write("package.json", '{"scripts":{}}')
        self.assertIn("missing-script", self.codes())

    def test_chain_budget_does_not_sum_siblings(self):
        self.write("AGENTS.md", "a" * 10000)
        self.write("one/AGENTS.md", "b" * 10000)
        self.write("two/AGENTS.md", "c" * 10000)
        self.assertNotIn("agent-chain-budget", self.codes())
        self.write("one/deep/AGENTS.md", "d" * 10000)
        self.assertIn("agent-chain-budget", self.codes())

    def test_override_has_precedence_in_budget(self):
        self.write("AGENTS.md", "a" * 20000)
        self.write("AGENTS.override.md", "override\n")
        self.write("child/AGENTS.md", "b" * 15000)
        self.assertNotIn("agent-chain-budget", self.codes())

    def test_strict_exit_and_inventory(self):
        self.write("AGENTS.md", "rule\n" * 201)
        proc = subprocess.run([sys.executable, str(ROOT / "scripts/audit-rules.py"),
                               "--root", str(self.root), "--strict", "--json"],
                              capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(1, proc.returncode)
        report = json.loads(proc.stdout)
        self.assertEqual(201, report["files"][0]["lines"])

    def test_global_comparison_opt_in(self):
        self.write("AGENTS.md", "same\n")
        global_file = self.write("global.txt", "same\n")
        result = AUDIT.audit(self.root, global_file)
        self.assertEqual("global-duplicate", result["findings"][0]["code"])


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.target = Path(self.tmp.name) / "claude"

    def run_install(self, *extra):
        proc = subprocess.run([sys.executable, str(ROOT / "scripts/install-global.py"),
                               "--target", str(self.target), "--components", "core", *extra],
                              capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        return proc

    def test_dry_run_writes_nothing(self):
        self.run_install("--dry-run")
        self.assertFalse(self.target.exists())

    def test_core_is_global_only_and_idempotent(self):
        self.run_install()
        dest = self.target / "CLAUDE.md"
        content, mtime = dest.read_bytes(), dest.stat().st_mtime_ns
        self.assertEqual((ROOT / "config/claude-global.md").read_bytes(), content)
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.run_install()
        self.assertEqual(mtime, dest.stat().st_mtime_ns)
        self.assertFalse((self.target / "backups").exists())
        self.assertTrue(VERIFY.verify(ROOT, self.target, ["core"])["passed"])

    def test_full_install_preserves_settings_and_is_idempotent(self):
        self.target.mkdir()
        original = {"env": {"TEST_KEY": "value"}, "permissions": {"allow": ["Read"]}}
        (self.target / "settings.json").write_text(json.dumps(original), encoding="utf-8")
        command = [sys.executable, str(ROOT / "scripts/install-global.py"), "--target", str(self.target)]
        snapshots = []
        files_before_repeat = None
        for _ in range(2):
            proc = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            snapshots.append(json.loads((self.target / "settings.json").read_text(encoding="utf-8")))
            files = {p.relative_to(self.target).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                     for p in self.target.rglob("*") if p.is_file()}
            if files_before_repeat is None:
                files_before_repeat = files
            else:
                self.assertEqual(files_before_repeat, files)
        self.assertEqual(snapshots[0], snapshots[1])
        self.assertEqual(original["env"], snapshots[0]["env"])
        self.assertEqual(original["permissions"], snapshots[0]["permissions"])
        self.assertTrue((self.target / "hooks/intent-context.py").is_file())
        self.assertTrue((self.target / "commands/rule-audit.md").is_file())
        self.assertEqual((ROOT / "config/claude-global.md").read_bytes(),
                         (self.target / "CLAUDE.md").read_bytes())
        verification = VERIFY.verify(ROOT, self.target, VERIFY.DEFAULT_COMPONENTS.split(","))
        self.assertTrue(verification["passed"], verification)

    def test_verifier_reports_missing_and_changed_files_without_writing(self):
        self.run_install()
        dest = self.target / "CLAUDE.md"
        dest.write_text("customized", encoding="utf-8")
        result = VERIFY.verify(ROOT, self.target, ["core"])
        self.assertFalse(result["passed"])
        self.assertIn("content differs", result["problems"][0])
        self.assertEqual("customized", dest.read_text(encoding="utf-8"))
        dest.unlink()
        result = VERIFY.verify(ROOT, self.target, ["core"])
        self.assertFalse(result["passed"])
        self.assertFalse(dest.exists())

    def test_verifier_rejects_invalid_settings(self):
        self.run_install()
        path = self.target / "settings.json"
        path.write_text("{bad", encoding="utf-8")
        result = VERIFY.verify(ROOT, self.target, ["core"])
        self.assertFalse(result["passed"])
        self.assertEqual("{bad", path.read_text(encoding="utf-8"))

    def test_verifier_smoke_failure_is_not_success(self):
        self.run_install()  # core only; installed Hook intentionally absent
        result = VERIFY.verify(ROOT, self.target, ["core"], smoke_hook=True)
        self.assertFalse(result["passed"])
        self.assertTrue(result["hook_smoke"].startswith("FAIL"))

    def test_custom_rules_preserved_and_explicit_replacement_backed_up(self):
        self.target.mkdir()
        dest = self.target / "CLAUDE.md"
        dest.write_text("custom personal rules\n", encoding="utf-8")
        settings = {"env": {"TEST_KEY": "value"}, "permissions": {"allow": ["Read"]}}
        (self.target / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
        self.run_install()
        self.assertEqual("custom personal rules\n", dest.read_text(encoding="utf-8"))
        self.run_install("--replace-global-rules")
        backups = list((self.target / "backups").rglob("CLAUDE.md"))
        self.assertEqual(1, len(backups))
        self.assertEqual("custom personal rules\n", backups[0].read_text(encoding="utf-8"))
        self.assertEqual(settings, json.loads((self.target / "settings.json").read_text(encoding="utf-8")))

    def test_known_legacy_migration_is_backed_up(self):
        # Synthetic legacy signature exercises the same guarded migration branch.
        installer = module("installer_test", "scripts/install-global.py")
        self.target.mkdir()
        legacy = b"legacy project rules\n"
        installer.LEGACY_CORE_SHA256 = hashlib.sha256(legacy).hexdigest()
        (self.target / "CLAUDE.md").write_bytes(legacy)
        obj = installer.Installer(self.target, False)
        with contextlib.redirect_stdout(io.StringIO()):
            obj.copy_file(ROOT / "config/claude-global.md", "CLAUDE.md", installer.GLOBAL_RULES)
        self.assertEqual(legacy, (obj.backup_dir / "CLAUDE.md").read_bytes())
        self.assertEqual(1, obj.stats["updated"])


if __name__ == "__main__":
    unittest.main()

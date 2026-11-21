import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("skill_audit", ROOT / "scripts/audit-skills.py")
AUDIT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AUDIT)


@unittest.skipUnless(importlib.util.find_spec("yaml"), "Skill audit requires the validation venv (PyYAML)")
class SkillAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def write(self, name, text):
        path = self.root / ".claude/skills" / name / "SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_portable_metadata_and_compatibility(self):
        self.write("example", "---\nname: example\ndescription: A focused workflow\ncompatibility: Python 3.10+\nmetadata:\n  version: 1.0.0\n  trigger: [example]\n---\n# Instructions\nDo the task.\n")
        result = AUDIT.audit(self.root)
        self.assertTrue(result["passed"], result)

    def test_unknown_top_level_field_is_rejected(self):
        self.write("example", "---\nname: example\ndescription: Example\ntrigger: [example]\n---\nInstructions\n")
        self.assertFalse(AUDIT.audit(self.root)["passed"])

    def test_claude_fields_and_boolean_types(self):
        path = self.write("example", "---\nname: example\ndescription: Example\ndisable-model-invocation: true\nuser-invocable: true\nargument-hint: '[task]'\n---\nInstructions\n")
        self.assertTrue(AUDIT.audit(self.root)["passed"])
        path.write_text(path.read_text().replace("invocation: true", "invocation: 'false'"))
        self.assertFalse(AUDIT.audit(self.root)["passed"])

    def test_nested_skill_requires_discoverable_entry(self):
        self.write("bundle/child", "---\nname: child\ndescription: Example\n---\nInstructions\n")
        self.assertFalse(AUDIT.audit(self.root)["passed"])

    def test_missing_header_and_bad_yaml_are_reported_without_writing(self):
        one = self.write("one", "# Missing header\n")
        two = self.write("two", "---\nname: [\n---\nInstructions\n")
        before = {p: p.read_bytes() for p in (one, two)}
        result = AUDIT.audit(self.root)
        self.assertEqual(2, len(result["problems"]))
        self.assertEqual(before, {p: p.read_bytes() for p in (one, two)})

    def test_directory_name_and_description_checked(self):
        self.write("example", "---\nname: mismatch\ndescription: ''\n---\nInstructions\n")
        self.assertFalse(AUDIT.audit(self.root)["passed"])

    def test_empty_inventory_is_not_success(self):
        self.assertFalse(AUDIT.audit(self.root)["passed"])


if __name__ == "__main__":
    unittest.main()

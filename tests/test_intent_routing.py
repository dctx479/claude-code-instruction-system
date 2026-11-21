"""Exercise the repository hook with isolated HOME; no global installation required."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASH = os.environ.get("TAIYI_TEST_BASH") or (
    "C:/Program Files/Git/bin/bash.exe" if os.name == "nt" and
    Path("C:/Program Files/Git/bin/bash.exe").is_file() else shutil.which("bash"))


class RoutingTests(unittest.TestCase):
    def setUp(self):
        if not BASH:
            self.fail("Bash is required; install Git Bash or set TAIYI_TEST_BASH")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.env = dict(os.environ, HOME=self.home.as_posix(), PYTHONIOENCODING="utf-8")

    def invoke(self, prompt=None, raw=None, session="session-a", **kwargs):
        data = raw if raw is not None else json.dumps(
            dict(prompt=prompt, session_id=session, cwd=str(ROOT)), ensure_ascii=False)
        env = dict(self.env, **kwargs)
        proc = subprocess.run([BASH, str(ROOT / "hooks/intent-detector.sh")],
                              input=data, capture_output=True, text=True, encoding="utf-8",
                              env=env, timeout=20)
        self.assertEqual(0, proc.returncode, proc.stderr)
        if raw is not None:
            return proc
        if proc.stdout:
            self.assertTrue(proc.stdout.startswith("Advisory routing"), proc.stdout + proc.stderr)
            context = json.loads(proc.stdout.split(": ", 1)[1])
        else:
            context = json.loads((self.home / ".claude/intent-state.json").read_text(encoding="utf-8"))
            self.assertEqual("none", context["intent"])
            self.assertEqual("", context["agent"])
        return context, proc

    def test_all_roles(self):
        cases = [
            ("帮我调试这个错误", "debugger"), ("请审查这段代码的质量", "code-reviewer"),
            ("生成单元测试覆盖率", "automated-testing"), ("重构这段代码让它更清晰", "code-reviewer"),
            ("设计一个微服务架构", "architect"), ("检查XSS注入漏洞", "security-analyst"),
            ("依赖扫描CVE安全审计", "security-audit"), ("查询数据库SQL优化", "data-scientist"),
            ("统计分析用户行为数据", "data-analyst"), ("绘制数据可视化图表", "data-visualization"),
            ("训练PyTorch深度学习模型", "deep-learning"), ("用PPO强化学习训练策略", "reinforcement-learning"),
            ("用ARIMA时间序列预测趋势", "time-series-analysis"), ("SHAP解释模型可解释性", "model-interpretability"),
            ("文献综述调研论文", "literature-manager"), ("帮我撰写论文综述", "paper-writing-assistant"),
            ("记录实验配置和结果", "experiment-logger"), ("编写功能规范文档", "spec-writer"),
            ("质量审查验收检查", "qa-reviewer"), ("autofix自动修复P2问题", "qa-fixer"),
            ("性能监控报告生成", "performance-monitor"), ("系统配置优化token优化", "auto-optimizer"),
            ("全自主autopilot执行", "autopilot-orchestrator"), ("保存上下文归档", "context-archivist"),
            ("用vitest写mock用例", "vitest-tester"), ("按sdd-riper流程开发这个需求", "sdd-riper-orchestrator"),
            ("请资深架构师看看这个框架", "senior-code-architect"), ("技术导师带我入门这个领域", "tech-mentor"),
            ("做一下需求拆解和用户故事", "requirements-analyst"), ("数仓多维分析查询", "data-warehouse-analyst"),
            ("生成代码地图方便导航", "codemap-builder"), ("对这个模块做qa修复", "qa-fixer"),
            ('他说 "你好"\n然后帮我调试这个报错', "debugger"), ("继续推进任务", "orchestrator")]
        for prompt, expected in cases:
            with self.subTest(prompt=prompt):
                data, proc = self.invoke(prompt)
                self.assertEqual("", data["agent"])
                self.assertEqual("", proc.stdout)
                data, proc = self.invoke("@" + expected + " " + prompt)
                self.assertEqual(expected, data["agent"])
                self.assertEqual("", proc.stderr)

    def test_pasted_article_and_quoted_commands_do_not_route(self):
        article = "旧文章讲 QA 验收 npm test /autopilot 的例子。" * 100
        for prompt in [article + "\n\n参照上述内容对当前项目进行改进优化",
                       article, "> /autopilot 质量审查验收\n\n继续推进任务",
                       "```text\n/autopilot 质量审查验收\n```\n继续推进任务"]:
            with self.subTest(prompt=prompt[-50:]):
                data, _ = self.invoke(prompt)
                self.assertEqual("", data["agent"])

    def test_explicit_override_and_empty_input(self):
        data, _ = self.invoke("@architect\n" + "qa /autopilot " * 300)
        self.assertEqual("architect", data["agent"])
        data, _ = self.invoke("")
        self.assertEqual("", data["agent"])

    def test_invalid_input_warns_without_stale_context(self):
        for raw in ["{bad", "[]", '{"prompt": 42}', '{"prompt":"hi","cwd":{}}']:
            proc = self.invoke(raw=raw)
            self.assertIn("WARNING", proc.stderr)
            self.assertEqual("", proc.stdout)
        self.assertFalse((self.home / ".claude/intent-state.json").exists())

    def test_session_paths_are_isolated_and_traversal_safe(self):
        for session, prompt in [("session-a", "帮我调试错误"), ("../../evil", "设计微服务架构")]:
            self.invoke("@debugger " + prompt, session=session)
        base = self.home / ".claude/intent-sessions"
        self.assertEqual(2, len(list(base.glob("*.json"))))
        key = hashlib.sha256((str(ROOT) + "\0session-a").encode()).hexdigest()
        saved = json.loads((base / (key + ".json")).read_text(encoding="utf-8"))
        self.assertEqual("debugger", saved["agent"])
        self.assertFalse((self.home / "evil").exists())

    def test_explicit_command_and_utf8_protocol(self):
        data, proc = self.invoke("/spec-flow 中文需求", PYTHONIOENCODING="cp1252")
        self.assertEqual("command", data["intent"])
        self.assertEqual("spec-flow", data["skill"])
        self.assertEqual("", data["agent"])
        self.assertIsNone(data["tool_recommendation"])
        self.assertEqual("", proc.stderr)

    def test_ordinary_turn_clears_previous_advice(self):
        self.invoke("@debugger debug")
        data, proc = self.invoke("continue")
        self.assertEqual("", proc.stdout)
        self.assertEqual("none", data["intent"])

    def test_real_governance_requests_are_not_data_analysis(self):
        fixture = json.loads((ROOT / "tests/fixtures/governance-intents.json").read_text(encoding="utf-8"))
        for case in fixture["cases"]:
            with self.subTest(prompt=case["prompt"]):
                data, proc = self.invoke(case["prompt"])
                self.assertEqual(case["agent"], data["agent"])
                self.assertEqual("", proc.stderr)


if __name__ == "__main__":
    unittest.main()

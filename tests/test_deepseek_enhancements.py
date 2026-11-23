#!/usr/bin/env python3
"""
集成测试: DeepSeek 启发的上下文管理增强

测试分层笔记系统、标注系统和检查点审查功能的集成
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# 添加 scripts 目录到 path
scripts_dir = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

# 导入前确保模块名正确（使用下划线）
import importlib.util

def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

note_manager = load_module('note_manager', scripts_dir / 'note-manager.py')
annotation_manager = load_module('annotation_manager', scripts_dir / 'annotation-manager.py')

SessionNotesManager = note_manager.SessionNotesManager
AnnotationManager = annotation_manager.AnnotationManager


class TestSessionNotes(unittest.TestCase):
    """测试分层笔记系统"""

    def setUp(self):
        """创建临时项目目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

        # 初始化 git 仓库
        subprocess.run(['git', 'init'], cwd=self.project_root, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=self.project_root, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=self.project_root, capture_output=True)

        # 创建初始提交
        (self.project_root / 'README.md').write_text('# Test Project')
        subprocess.run(['git', 'add', '.'], cwd=self.project_root, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=self.project_root, capture_output=True)

        self.manager = SessionNotesManager(self.project_root)

    def tearDown(self):
        """清理临时目录"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_add_session_note(self):
        """测试添加 session 级笔记"""
        note_file = self.manager.add_note('session', 'Test session note', 'idea')

        self.assertTrue(note_file.exists())
        content = note_file.read_text()
        self.assertIn('Test session note', content)
        self.assertIn('idea', content)

    def test_add_workspace_note(self):
        """测试添加 workspace 级笔记"""
        note_file = self.manager.add_note('workspace', 'Test workspace note', 'decision')

        self.assertTrue(note_file.exists())
        content = note_file.read_text()
        self.assertIn('Test workspace note', content)
        self.assertIn('decision', content)

    def test_show_notes(self):
        """测试显示笔记"""
        self.manager.add_note('session', 'Session note 1', 'idea')
        self.manager.add_note('workspace', 'Workspace note 1', 'todo')

        output = self.manager.show_notes()

        self.assertIn('Session note 1', output)
        self.assertIn('Workspace note 1', output)

    def test_archive_session_notes(self):
        """测试归档 session 笔记"""
        self.manager.add_note('session', 'Test note', 'idea')

        archive_file = self.manager.archive_session_notes()

        self.assertIsNotNone(archive_file)
        self.assertTrue(archive_file.exists())
        self.assertIn('archive', str(archive_file))

    def test_session_id_generation(self):
        """测试 session ID 生成"""
        session_id = SessionNotesManager.get_session_id()

        self.assertIsNotNone(session_id)
        self.assertIn('-', session_id)
        # 应该包含 git hash 和时间戳


class TestAnnotations(unittest.TestCase):
    """测试标注系统"""

    def setUp(self):
        """创建临时项目目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

        # 初始化 git 仓库
        subprocess.run(['git', 'init'], cwd=self.project_root, capture_output=True)

        self.manager = AnnotationManager(self.project_root)

    def tearDown(self):
        """清理临时目录"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_add_annotation(self):
        """测试添加标注"""
        annotation = self.manager.add_annotation(
            text='Test annotation',
            tag='key-insight',
            role='assistant',
            turn=1
        )

        self.assertEqual(annotation['text'], 'Test annotation')
        self.assertEqual(annotation['tag'], 'key-insight')
        self.assertEqual(annotation['turn'], 1)
        self.assertIn('timestamp', annotation)

    def test_invalid_tag(self):
        """测试无效标签"""
        with self.assertRaises(ValueError):
            self.manager.add_annotation(
                text='Test',
                tag='invalid-tag',
                role='assistant'
            )

    def test_get_annotations(self):
        """测试查询标注"""
        self.manager.add_annotation('Insight 1', 'key-insight', turn=1)
        self.manager.add_annotation('Todo 1', 'todo', turn=2)
        self.manager.add_annotation('Insight 2', 'key-insight', turn=3)

        # 查询所有
        all_annotations = self.manager.get_annotations()
        self.assertEqual(len(all_annotations), 3)

        # 按标签过滤
        insights = self.manager.get_annotations(tag='key-insight')
        self.assertEqual(len(insights), 2)

        # 限制数量
        limited = self.manager.get_annotations(limit=2)
        self.assertEqual(len(limited), 2)

    def test_get_summary(self):
        """测试获取摘要"""
        self.manager.add_annotation('Insight 1', 'key-insight')
        self.manager.add_annotation('Todo 1', 'todo')
        self.manager.add_annotation('Insight 2', 'key-insight')

        summary = self.manager.get_summary()

        self.assertEqual(summary['total'], 3)
        self.assertEqual(summary['by_tag']['key-insight'], 2)
        self.assertEqual(summary['by_tag']['todo'], 1)

    def test_export_to_markdown(self):
        """测试导出到 Markdown"""
        self.manager.add_annotation('Test insight', 'key-insight', turn=1)
        self.manager.add_annotation('Test todo', 'todo', turn=2)

        output_file = self.project_root / 'annotations.md'
        self.manager.export_to_markdown(output_file)

        self.assertTrue(output_file.exists())
        content = output_file.read_text()
        self.assertIn('Test insight', content)
        self.assertIn('Test todo', content)


class TestCheckpointReview(unittest.TestCase):
    """测试检查点审查功能"""

    def setUp(self):
        """创建临时项目目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

        # 初始化 git 仓库
        subprocess.run(['git', 'init'], cwd=self.project_root, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=self.project_root, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=self.project_root, capture_output=True)

        # 创建测试文件
        (self.project_root / 'test.txt').write_text('Hello World')
        subprocess.run(['git', 'add', '.'], cwd=self.project_root, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial'], cwd=self.project_root, capture_output=True)

    def tearDown(self):
        """清理临时目录"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_checkpoint_save_and_review(self):
        """测试保存和审查检查点"""
        # 创建检查点
        checkpoint_data = {
            "goal": "Test checkpoint",
            "done": ["Created test file"],
            "next": ["Continue testing"],
            "evidence": ["test.txt exists"],
            "files": ["test.txt"]
        }

        # 保存检查点
        result = subprocess.run(
            ['python', 'scripts/checkpoint.py', 'save', '--root', str(self.project_root)],
            input=json.dumps(checkpoint_data),
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        self.assertEqual(result.returncode, 0)

        # 审查检查点
        result = subprocess.run(
            ['python', 'scripts/checkpoint.py', 'review', '--root', str(self.project_root)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn('verified', result.stdout.lower())
        self.assertIn('test.txt', result.stdout)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        """创建临时项目目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

        # 初始化 git 仓库
        subprocess.run(['git', 'init'], cwd=self.project_root, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=self.project_root, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=self.project_root, capture_output=True)
        subprocess.run(['git', 'commit', '--allow-empty', '-m', 'Initial'], cwd=self.project_root, capture_output=True)

        self.notes_manager = SessionNotesManager(self.project_root)
        self.annotation_manager = AnnotationManager(self.project_root)

    def tearDown(self):
        """清理临时目录"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_workflow_simulation(self):
        """模拟完整工作流程"""
        # 1. 添加 session 笔记
        self.notes_manager.add_note('session', 'Start debugging', 'idea')

        # 2. 添加标注
        self.annotation_manager.add_annotation(
            'Found the root cause',
            'key-insight',
            turn=5
        )

        # 3. 添加更多笔记
        self.notes_manager.add_note('session', 'Need to verify fix', 'todo')

        # 4. 查看笔记
        notes_output = self.notes_manager.show_notes('session')
        self.assertIn('Start debugging', notes_output)
        self.assertIn('Need to verify fix', notes_output)

        # 5. 查看标注摘要
        summary = self.annotation_manager.get_summary()
        self.assertEqual(summary['total'], 1)
        self.assertEqual(summary['by_tag']['key-insight'], 1)

        # 6. 归档 session 笔记
        archive_file = self.notes_manager.archive_session_notes()
        self.assertIsNotNone(archive_file)
        self.assertTrue(archive_file.exists())


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestSessionNotes))
    suite.addTests(loader.loadTestsFromTestCase(TestAnnotations))
    suite.addTests(loader.loadTestsFromTestCase(TestCheckpointReview))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())

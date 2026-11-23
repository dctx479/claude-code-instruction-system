#!/usr/bin/env python3
"""
快速验证脚本 - 验证 DeepSeek 增强功能是否正常工作
"""

import sys
import json
from pathlib import Path

# 添加 scripts 到路径
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

def test_note_manager():
    """测试笔记管理器"""
    print("Testing SessionNotesManager...")

    import importlib.util
    spec = importlib.util.spec_from_file_location("note_manager", Path(__file__).parent / 'scripts' / 'note-manager.py')
    note_manager = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(note_manager)

    manager = note_manager.SessionNotesManager()

    # 测试添加笔记
    note_file = manager.add_note('workspace', 'Test workspace note', 'idea')
    print(f"✓ Created workspace note: {note_file}")

    # 测试显示笔记
    output = manager.show_notes('workspace')
    assert 'Test workspace note' in output
    print("✓ Show notes works")

    # 测试 session ID
    session_id = note_manager.SessionNotesManager.get_session_id()
    print(f"✓ Generated session ID: {session_id}")

    print("✓ SessionNotesManager: ALL PASSED\n")
    return True


def test_annotation_manager():
    """测试标注管理器"""
    print("Testing AnnotationManager...")

    import importlib.util
    spec = importlib.util.spec_from_file_location("annotation_manager", Path(__file__).parent / 'scripts' / 'annotation-manager.py')
    annotation_manager = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(annotation_manager)

    manager = annotation_manager.AnnotationManager()

    # 测试添加标注
    annotation = manager.add_annotation(
        text='Test annotation',
        tag='key-insight',
        role='assistant',
        turn=1
    )
    print(f"✓ Created annotation: {annotation['tag']}")

    # 测试查询
    annotations = manager.get_annotations(limit=5)
    print(f"✓ Found {len(annotations)} annotation(s)")

    # 测试摘要
    summary = manager.get_summary()
    print(f"✓ Summary: {summary['total']} total")

    print("✓ AnnotationManager: ALL PASSED\n")
    return True


def test_checkpoint_review():
    """测试检查点审查"""
    print("Testing checkpoint review...")

    import subprocess

    # 检查 checkpoint.py 是否有 review 命令
    result = subprocess.run(
        ['python', 'scripts/checkpoint.py', '--help'],
        capture_output=True,
        text=True
    )

    if 'review' in result.stdout:
        print("✓ checkpoint.py has review command")
    else:
        print("✗ checkpoint.py missing review command")
        return False

    if 'diff' in result.stdout:
        print("✓ checkpoint.py has diff command")
    else:
        print("✗ checkpoint.py missing diff command")
        return False

    print("✓ Checkpoint review: ALL PASSED\n")
    return True


def test_skill_definition():
    """测试 Skill 定义"""
    print("Testing session-notes skill...")

    skill_file = Path(__file__).parent / '.claude' / 'skills' / 'session-notes' / 'SKILL.md'

    if not skill_file.exists():
        print(f"✗ Skill file not found: {skill_file}")
        return False

    content = skill_file.read_text(encoding='utf-8')

    # 检查关键部分
    checks = [
        ('name: session-notes', 'Skill name'),
        ('/note session', 'Session command'),
        ('/note workspace', 'Workspace command'),
        ('/note global', 'Global command'),
        ('integration:', 'Integration section'),
    ]

    for check_str, description in checks:
        if check_str in content:
            print(f"✓ {description} present")
        else:
            print(f"✗ {description} missing")
            return False

    print("✓ Skill definition: ALL PASSED\n")
    return True


def test_index_updated():
    """测试 INDEX 是否更新"""
    print("Testing Skills INDEX update...")

    index_file = Path(__file__).parent / '.claude' / 'skills' / 'INDEX.md'
    content = index_file.read_text(encoding='utf-8')

    if 'session-notes' in content:
        print("✓ session-notes added to INDEX.md")
    else:
        print("✗ session-notes not in INDEX.md")
        return False

    print("✓ INDEX update: PASSED\n")
    return True


def test_gitignore():
    """测试 .gitignore 规则"""
    print("Testing .gitignore rules...")

    gitignore_file = Path(__file__).parent / '.gitignore'
    content = gitignore_file.read_text(encoding='utf-8')

    checks = [
        ('.claude/scratch/', 'Scratch directory'),
        ('annotations.jsonl', 'Annotations file'),
    ]

    for check_str, description in checks:
        if check_str in content:
            print(f"✓ {description} ignored")
        else:
            print(f"✗ {description} not ignored")
            return False

    print("✓ .gitignore: ALL PASSED\n")
    return True


def test_documentation():
    """测试文档是否创建"""
    print("Testing documentation...")

    docs = [
        ('specs/SPEC-deepseek-inspired-enhancements.md', 'Technical spec'),
        ('docs/SESSION-NOTES-GUIDE.md', 'User guide'),
        ('analysis/deepseek-notes-analysis.md', 'Analysis report'),
    ]

    for doc_path, description in docs:
        doc_file = Path(__file__).parent / doc_path
        if doc_file.exists():
            print(f"✓ {description} exists")
        else:
            print(f"✗ {description} missing")
            return False

    print("✓ Documentation: ALL PASSED\n")
    return True


def main():
    """运行所有验证"""
    print("=" * 60)
    print("DeepSeek Enhancements Verification")
    print("=" * 60)
    print()

    tests = [
        ("Note Manager", test_note_manager),
        ("Annotation Manager", test_annotation_manager),
        ("Checkpoint Review", test_checkpoint_review),
        ("Skill Definition", test_skill_definition),
        ("INDEX Update", test_index_updated),
        (".gitignore Rules", test_gitignore),
        ("Documentation", test_documentation),
    ]

    results = {}

    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"X {name} FAILED with exception: {e}\n")
            results[name] = False

    # 总结
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All validations PASSED!")
        return 0
    else:
        print(f"\n✗ {total - passed} validation(s) FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())

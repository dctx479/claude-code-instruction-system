#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速验证脚本 - 验证 DeepSeek 增强功能是否正常工作
"""

import sys
import os
from pathlib import Path

# 切换到项目根目录
project_root = Path(__file__).parent.parent
os.chdir(project_root)

def check_file_exists(path, description):
    """检查文件是否存在"""
    if Path(path).exists():
        print(f"[OK] {description}")
        return True
    else:
        print(f"[FAIL] {description} - file not found: {path}")
        return False

def check_content_in_file(path, content, description):
    """检查文件中是否包含特定内容"""
    try:
        file_content = Path(path).read_text(encoding='utf-8')
        if content in file_content:
            print(f"[OK] {description}")
            return True
        else:
            print(f"[FAIL] {description} - content not found")
            return False
    except Exception as e:
        print(f"[FAIL] {description} - error: {e}")
        return False

def main():
    print("=" * 60)
    print("DeepSeek Enhancements Verification")
    print("=" * 60)
    print()

    results = []

    # 1. 检查核心脚本
    print("1. Core Scripts")
    results.append(check_file_exists('scripts/note-manager.py', 'note-manager.py exists'))
    results.append(check_file_exists('scripts/annotation-manager.py', 'annotation-manager.py exists'))
    results.append(check_content_in_file('scripts/checkpoint.py', 'def review', 'checkpoint.py has review function'))
    results.append(check_content_in_file('scripts/checkpoint.py', 'def diff_checkpoints', 'checkpoint.py has diff function'))
    print()

    # 2. 检查 Skill 定义
    print("2. Skill Definition")
    results.append(check_file_exists('.claude/skills/session-notes/SKILL.md', 'session-notes SKILL.md exists'))
    results.append(check_content_in_file('.claude/skills/session-notes/SKILL.md', '/note session', 'SKILL.md has /note session command'))
    results.append(check_content_in_file('.claude/skills/session-notes/SKILL.md', '/note workspace', 'SKILL.md has /note workspace command'))
    results.append(check_content_in_file('.claude/skills/session-notes/SKILL.md', '/note global', 'SKILL.md has /note global command'))
    print()

    # 3. 检查 INDEX 更新
    print("3. Skills INDEX")
    results.append(check_content_in_file('.claude/skills/INDEX.md', 'session-notes', 'session-notes added to INDEX.md'))
    print()

    # 4. 检查文档
    print("4. Documentation")
    results.append(check_file_exists('specs/SPEC-deepseek-inspired-enhancements.md', 'Technical spec exists'))
    results.append(check_file_exists('docs/SESSION-NOTES-GUIDE.md', 'User guide exists'))
    results.append(check_file_exists('analysis/deepseek-notes-analysis.md', 'Analysis report exists'))
    print()

    # 5. 检查 .gitignore
    print("5. Git Configuration")
    results.append(check_content_in_file('.gitignore', '.claude/scratch/', '.gitignore has scratch directory'))
    results.append(check_content_in_file('.gitignore', 'annotations.jsonl', '.gitignore has annotations file'))
    print()

    # 6. 检查目录结构
    print("6. Directory Structure")
    results.append(check_file_exists('.claude/scratch/.gitkeep', '.claude/scratch/ directory exists'))
    print()

    # 7. 测试 Python 模块导入
    print("7. Module Import Test")
    try:
        import importlib.util

        # 测试 note-manager
        spec = importlib.util.spec_from_file_location("note_manager", "scripts/note-manager.py")
        note_manager = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(note_manager)
        print("[OK] note-manager.py can be imported")
        results.append(True)

        # 测试基本功能
        manager = note_manager.SessionNotesManager()
        session_id = note_manager.SessionNotesManager.get_session_id()
        print(f"[OK] SessionNotesManager works (session_id: {session_id})")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] Module import test failed: {e}")
        results.append(False)
        results.append(False)
    print()

    try:
        # 测试 annotation-manager
        spec = importlib.util.spec_from_file_location("annotation_manager", "scripts/annotation-manager.py")
        annotation_manager = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(annotation_manager)
        print("[OK] annotation-manager.py can be imported")
        results.append(True)

        # 测试基本功能
        ann_manager = annotation_manager.AnnotationManager()
        print("[OK] AnnotationManager works")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] Annotation module test failed: {e}")
        results.append(False)
        results.append(False)
    print()

    # 总结
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results if r)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n[SUCCESS] All validations passed!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} validation(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())

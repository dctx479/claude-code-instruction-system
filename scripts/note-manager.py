#!/usr/bin/env python3
"""
Session Notes Manager - 分层临时笔记管理工具

用途: 管理 session/workspace/global 三级作用域的临时笔记
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal

# 作用域类型
ScopeType = Literal["session", "workspace", "global"]

class SessionNotesManager:
    """分层笔记管理器"""

    def __init__(self, project_root: Optional[Path] = None):
        """
        初始化笔记管理器

        Args:
            project_root: 项目根目录，默认为当前 git 仓库根目录
        """
        self.project_root = project_root or self._find_git_root()
        self.scratch_dir = self.project_root / '.claude' / 'scratch'
        self.archive_dir = self.scratch_dir / 'archive'

        # 全局笔记目录
        home = Path.home()
        self.global_scratch_dir = home / '.claude' / 'scratch'

        # 确保目录存在
        self.scratch_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.global_scratch_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _find_git_root() -> Path:
        """查找 git 仓库根目录"""
        try:
            root = subprocess.check_output(
                ['git', 'rev-parse', '--show-toplevel'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            return Path(root)
        except:
            # 如果不在 git 仓库中，使用当前目录
            return Path.cwd()

    @staticmethod
    def get_session_id() -> str:
        """
        生成 session ID

        格式: {git-hash}-{timestamp}
        """
        try:
            commit = subprocess.check_output(
                ['git', 'rev-parse', '--short=7', 'HEAD'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            commit = 'unknown'

        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        return f"{commit}-{timestamp}"

    def get_project_name(self) -> str:
        """获取项目名称"""
        return self.project_root.name

    def _get_note_file(self, scope: ScopeType) -> Path:
        """
        获取指定作用域的笔记文件路径

        Args:
            scope: 作用域类型

        Returns:
            笔记文件路径
        """
        if scope == "session":
            session_id = self.get_session_id()
            return self.scratch_dir / f'session-{session_id}.md'
        elif scope == "workspace":
            return self.scratch_dir / 'workspace-notes.md'
        elif scope == "global":
            return self.global_scratch_dir / 'global-inbox.md'
        else:
            raise ValueError(f"Invalid scope: {scope}")

    def add_note(self, scope: ScopeType, content: str, tag: str = "note") -> Path:
        """
        添加笔记

        Args:
            scope: 作用域类型
            content: 笔记内容
            tag: 标签类型

        Returns:
            笔记文件路径
        """
        note_file = self._get_note_file(scope)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

        # 如果文件不存在，创建并写入头部
        if not note_file.exists():
            self._initialize_note_file(note_file, scope)

        # 追加笔记
        with open(note_file, 'a', encoding='utf-8') as f:
            f.write(f'\n## {timestamp} - {tag}\n')
            f.write(f'{content}\n')

        return note_file

    def _initialize_note_file(self, note_file: Path, scope: ScopeType):
        """初始化笔记文件头部"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if scope == "session":
            session_id = note_file.stem.replace('session-', '')
            header = f"""# Session Notes - {session_id}
Created: {timestamp}
Project: {self.get_project_name()}

---
"""
        elif scope == "workspace":
            header = f"""# Workspace Notes - {self.get_project_name()}
Last Updated: {timestamp}

---
"""
        elif scope == "global":
            header = f"""# Global Inbox
Last Updated: {timestamp}

---
"""
        else:
            header = ""

        with open(note_file, 'w', encoding='utf-8') as f:
            f.write(header)

    def show_notes(self, scope: Optional[ScopeType] = None) -> str:
        """
        显示笔记内容

        Args:
            scope: 作用域类型，None 表示显示所有

        Returns:
            笔记内容
        """
        output = []

        scopes = [scope] if scope else ["session", "workspace", "global"]

        for s in scopes:
            note_file = self._get_note_file(s)

            if note_file.exists():
                scope_name = s.capitalize()
                output.append(f"\n{'='*60}")
                output.append(f"=== {scope_name} Notes ===")
                output.append('='*60)

                with open(note_file, 'r', encoding='utf-8') as f:
                    output.append(f.read())
            else:
                scope_name = s.capitalize()
                output.append(f"\n[{scope_name}]: No notes found")

        return '\n'.join(output)

    def clear_notes(self, scope: ScopeType, confirm: bool = False) -> bool:
        """
        清空指定作用域的笔记

        Args:
            scope: 作用域类型
            confirm: 是否已确认（workspace 和 global 需要）

        Returns:
            是否成功
        """
        note_file = self._get_note_file(scope)

        if not note_file.exists():
            return False

        if scope == "session":
            # session 笔记移动到 archive
            return self.archive_session_notes() is not None
        else:
            # workspace 和 global 需要确认
            if not confirm:
                print(f"WARNING: This will delete {scope} notes. Use --confirm to proceed.")
                return False

            note_file.unlink()
            return True

    def archive_session_notes(self) -> Optional[Path]:
        """
        归档当前 session 笔记

        Returns:
            归档文件路径，如果没有笔记则返回 None
        """
        # 查找当前 session 笔记文件
        session_files = list(self.scratch_dir.glob('session-*.md'))

        if not session_files:
            return None

        # 归档最新的 session 文件
        session_file = max(session_files, key=lambda p: p.stat().st_mtime)

        archive_name = f"{session_file.stem}-archived-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        archive_file = self.archive_dir / archive_name

        session_file.rename(archive_file)

        return archive_file

    def list_archived_sessions(self, limit: int = 10) -> list[Path]:
        """
        列出归档的 session 笔记

        Args:
            limit: 最多返回数量

        Returns:
            归档文件列表（按时间倒序）
        """
        archived = sorted(
            self.archive_dir.glob('session-*.md'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        return archived[:limit]


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Session Notes Manager - 分层临时笔记管理工具'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # add 命令
    add_parser = subparsers.add_parser('add', help='Add a note')
    add_parser.add_argument('scope', choices=['session', 'workspace', 'global'])
    add_parser.add_argument('content', help='Note content')
    add_parser.add_argument('--tag', default='note', help='Note tag')

    # show 命令
    show_parser = subparsers.add_parser('show', help='Show notes')
    show_parser.add_argument('scope', nargs='?', choices=['session', 'workspace', 'global', 'all'])

    # clear 命令
    clear_parser = subparsers.add_parser('clear', help='Clear notes')
    clear_parser.add_argument('scope', choices=['session', 'workspace', 'global'])
    clear_parser.add_argument('--confirm', action='store_true', help='Confirm deletion')

    # archive 命令
    archive_parser = subparsers.add_parser('archive', help='Archive session notes')

    # list-archived 命令
    list_parser = subparsers.add_parser('list-archived', help='List archived sessions')
    list_parser.add_argument('--limit', type=int, default=10, help='Max results')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # 初始化管理器
    manager = SessionNotesManager()

    # 执行命令
    if args.command == 'add':
        note_file = manager.add_note(args.scope, args.content, args.tag)
        print(f"✓ Note added to {args.scope}: {note_file}")
        return 0

    elif args.command == 'show':
        scope = None if args.scope == 'all' or not args.scope else args.scope
        content = manager.show_notes(scope)
        print(content)
        return 0

    elif args.command == 'clear':
        success = manager.clear_notes(args.scope, args.confirm)
        if success:
            print(f"✓ {args.scope} notes cleared")
            return 0
        else:
            print(f"✗ Failed to clear {args.scope} notes")
            return 1

    elif args.command == 'archive':
        archive_file = manager.archive_session_notes()
        if archive_file:
            print(f"✓ Session notes archived: {archive_file}")
            return 0
        else:
            print("✗ No session notes to archive")
            return 1

    elif args.command == 'list-archived':
        archived = manager.list_archived_sessions(args.limit)
        if archived:
            print(f"Archived sessions (most recent {len(archived)}):")
            for i, path in enumerate(archived, 1):
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                print(f"  {i}. {path.name} ({mtime.strftime('%Y-%m-%d %H:%M')})")
            return 0
        else:
            print("No archived sessions found")
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())

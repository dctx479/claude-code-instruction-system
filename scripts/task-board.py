#!/usr/bin/env python3
"""
Task Board - 便利贴式任务管理工具

灵感来源: AI PPT Agent 的便利贴法
核心理念: 可视化任务，灵活调整
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Literal

StatusType = Literal["todo", "doing", "done", "dropped"]

class TaskBoard:
    """便利贴式任务管理"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or self._find_git_root()
        self.board_dir = self.project_root / '.claude' / 'taskboard'
        self.board_file = self.board_dir / 'tasks.json'

        # 确保目录存在
        self.board_dir.mkdir(parents=True, exist_ok=True)

        # 加载任务
        self.tasks = self._load_tasks()

    @staticmethod
    def _find_git_root() -> Path:
        """查找 git 仓库根目录"""
        import subprocess
        try:
            root = subprocess.check_output(
                ['git', 'rev-parse', '--show-toplevel'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            return Path(root)
        except:
            return Path.cwd()

    def _load_tasks(self) -> List[Dict]:
        """加载任务列表"""
        if self.board_file.exists():
            with open(self.board_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_tasks(self):
        """保存任务列表"""
        with open(self.board_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def add_card(self, title: str, status: StatusType = 'todo',
                 description: str = '') -> Dict:
        """
        添加一张任务卡片

        Args:
            title: 任务标题
            status: 状态 (todo/doing/done/dropped)
            description: 任务描述

        Returns:
            任务卡片
        """
        card = {
            "id": len(self.tasks) + 1,
            "title": title,
            "status": status,
            "description": description,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat()
        }

        self.tasks.append(card)
        self._save_tasks()

        return card

    def move_card(self, card_id: int, new_status: StatusType) -> bool:
        """
        移动卡片到新状态

        Args:
            card_id: 任务 ID
            new_status: 新状态

        Returns:
            是否成功
        """
        for task in self.tasks:
            if task['id'] == card_id:
                task['status'] = new_status
                task['updated'] = datetime.now().isoformat()
                self._save_tasks()
                return True
        return False

    def remove_card(self, card_id: int) -> bool:
        """
        删除卡片

        Args:
            card_id: 任务 ID

        Returns:
            是否成功
        """
        original_len = len(self.tasks)
        self.tasks = [t for t in self.tasks if t['id'] != card_id]

        if len(self.tasks) < original_len:
            self._save_tasks()
            return True
        return False

    def get_card(self, card_id: int) -> Optional[Dict]:
        """获取指定卡片"""
        for task in self.tasks:
            if task['id'] == card_id:
                return task
        return None

    def list_cards(self, status: Optional[StatusType] = None) -> List[Dict]:
        """
        列出卡片

        Args:
            status: 按状态过滤，None 表示全部

        Returns:
            任务列表
        """
        if status:
            return [t for t in self.tasks if t['status'] == status]
        return self.tasks

    def visualize(self, style: str = 'compact'):
        """
        可视化任务板

        Args:
            style: 显示风格 (compact/detailed)
        """
        # 按状态分组
        by_status = {
            'todo': [t for t in self.tasks if t['status'] == 'todo'],
            'doing': [t for t in self.tasks if t['status'] == 'doing'],
            'done': [t for t in self.tasks if t['status'] == 'done'],
            'dropped': [t for t in self.tasks if t['status'] == 'dropped']
        }

        if style == 'compact':
            self._visualize_compact(by_status)
        else:
            self._visualize_detailed(by_status)

    def _visualize_compact(self, by_status: Dict):
        """紧凑显示模式"""
        print()
        print("=" * 80)
        print(" " * 30 + "[BOARD] TASK BOARD")
        print("=" * 80)
        print()

        # 表头
        col_width = 18
        print(f"{'TODO':<{col_width}} | {'DOING':<{col_width}} | {'DONE':<{col_width}} | {'DROPPED':<{col_width}}")
        print("-" * 80)

        # 获取最大行数
        max_rows = max(len(tasks) for tasks in by_status.values())

        # 逐行打印
        for i in range(max_rows):
            row = []
            for status in ['todo', 'doing', 'done', 'dropped']:
                tasks = by_status[status]
                if i < len(tasks):
                    task = tasks[i]
                    # 截断标题
                    title = task['title']
                    if len(title) > col_width - 5:
                        title = title[:col_width-8] + '...'

                    # 添加图标
                    icon = {
                        'todo': '[ ]',
                        'doing': '[>]',
                        'done': '[OK]',
                        'dropped': '[FAIL]'
                    }[status]

                    cell = f"{icon} {task['id']}. {title}"
                    row.append(f"{cell:<{col_width}}")
                else:
                    row.append(' ' * col_width)

            print(' | '.join(row))

        print()
        print(f"Total: {len(self.tasks)} tasks")
        print(f"  TODO: {len(by_status['todo'])}")
        print(f"  DOING: {len(by_status['doing'])}")
        print(f"  DONE: {len(by_status['done'])}")
        print(f"  DROPPED: {len(by_status['dropped'])}")
        print()

    def _visualize_detailed(self, by_status: Dict):
        """详细显示模式"""
        print()
        print("=" * 80)
        print(" " * 30 + "[BOARD] TASK BOARD (Detailed)")
        print("=" * 80)
        print()

        for status_name, status_key in [
            ('[TODO] TODO', 'todo'),
            ('[DOING] DOING', 'doing'),
            ('[DONE] DONE', 'done'),
            ('[DROP] DROPPED', 'dropped')
        ]:
            tasks = by_status[status_key]
            print(f"\n{status_name} ({len(tasks)})")
            print("-" * 80)

            if not tasks:
                print("  (empty)")
                continue

            for task in tasks:
                print(f"\n  [{task['id']}] {task['title']}")
                if task.get('description'):
                    desc = task['description']
                    if len(desc) > 60:
                        desc = desc[:57] + '...'
                    print(f"      {desc}")

                created = datetime.fromisoformat(task['created']).strftime('%Y-%m-%d %H:%M')
                print(f"      Created: {created}")

        print()


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Task Board - 便利贴式任务管理'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # add 命令
    add_parser = subparsers.add_parser('add', help='Add a task card')
    add_parser.add_argument('title', help='Task title')
    add_parser.add_argument('--status', default='todo',
                           choices=['todo', 'doing', 'done', 'dropped'])
    add_parser.add_argument('--desc', default='', help='Task description')

    # move 命令
    move_parser = subparsers.add_parser('move', help='Move a task to new status')
    move_parser.add_argument('id', type=int, help='Task ID')
    move_parser.add_argument('status', choices=['todo', 'doing', 'done', 'dropped'])

    # remove 命令
    remove_parser = subparsers.add_parser('remove', help='Remove a task')
    remove_parser.add_argument('id', type=int, help='Task ID')

    # show 命令
    show_parser = subparsers.add_parser('show', help='Show task board')
    show_parser.add_argument('--style', default='compact',
                            choices=['compact', 'detailed'])
    show_parser.add_argument('--status', choices=['todo', 'doing', 'done', 'dropped'],
                            help='Filter by status')

    # list 命令
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('--status', choices=['todo', 'doing', 'done', 'dropped'])

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # 初始化任务板
    board = TaskBoard()

    # 执行命令
    if args.command == 'add':
        card = board.add_card(args.title, args.status, args.desc)
        print(f"[OK] Task added: [{card['id']}] {card['title']}")
        return 0

    elif args.command == 'move':
        success = board.move_card(args.id, args.status)
        if success:
            print(f"[OK] Task {args.id} moved to {args.status}")
            return 0
        else:
            print(f"[FAIL] Task {args.id} not found")
            return 1

    elif args.command == 'remove':
        success = board.remove_card(args.id)
        if success:
            print(f"[OK] Task {args.id} removed")
            return 0
        else:
            print(f"[FAIL] Task {args.id} not found")
            return 1

    elif args.command == 'show':
        if args.status:
            tasks = board.list_cards(args.status)
            print(f"\n{args.status.upper()} tasks ({len(tasks)}):")
            for task in tasks:
                print(f"  [{task['id']}] {task['title']}")
        else:
            board.visualize(args.style)
        return 0

    elif args.command == 'list':
        tasks = board.list_cards(args.status)
        for task in tasks:
            print(f"[{task['id']}] [{task['status']}] {task['title']}")
        return 0

    return 0


if __name__ == '__main__':
    sys.exit(main())

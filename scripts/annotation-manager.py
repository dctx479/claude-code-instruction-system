#!/usr/bin/env python3
"""
Annotation Manager - 对话标注管理工具

用途: 管理对话中的标注（!mark 命令），支持持久化和查询
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# 标注标签类型
VALID_TAGS = {
    'key-insight',   # 关键洞察
    'todo',          # 待办事项
    'assumption',    # 待验证假设
    'question',      # 未解决问题
    'decision',      # 重要决策
    'anti-pattern',  # 错误尝试
}


class AnnotationManager:
    """对话标注管理器"""

    def __init__(self, project_root: Optional[Path] = None):
        """
        初始化标注管理器

        Args:
            project_root: 项目根目录
        """
        self.project_root = project_root or self._find_git_root()
        self.context_dir = self.project_root / '.claude' / 'context'
        self.annotations_file = self.context_dir / 'annotations.jsonl'

        # 确保目录存在
        self.context_dir.mkdir(parents=True, exist_ok=True)

        # 如果文件不存在，创建并写入 schema 注释
        if not self.annotations_file.exists():
            self._initialize_annotations_file()

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

    def _initialize_annotations_file(self):
        """初始化标注文件，写入 schema 注释"""
        schema = {
            "_schema": "annotations-v1",
            "_description": "对话标注记录，每行一个 JSON 对象",
            "_fields": {
                "turn": "对话轮次（可选）",
                "role": "角色 (user|assistant)",
                "text": "标注文本",
                "tag": f"标签类型 ({' | '.join(VALID_TAGS)})",
                "timestamp": "ISO 8601 时间戳",
                "session_id": "会话 ID（可选）"
            }
        }

        with open(self.annotations_file, 'w', encoding='utf-8') as f:
            f.write('# Schema: ' + json.dumps(schema, ensure_ascii=False) + '\n')

    def add_annotation(
        self,
        text: str,
        tag: str,
        role: str = "assistant",
        turn: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        添加标注

        Args:
            text: 标注文本
            tag: 标签类型
            role: 角色 (user|assistant)
            turn: 对话轮次
            session_id: 会话 ID

        Returns:
            标注记录

        Raises:
            ValueError: 如果标签类型无效
        """
        if tag not in VALID_TAGS:
            raise ValueError(
                f"Invalid tag '{tag}'. Valid tags: {', '.join(VALID_TAGS)}"
            )

        annotation = {
            "text": text,
            "tag": tag,
            "role": role,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        if turn is not None:
            annotation["turn"] = turn

        if session_id:
            annotation["session_id"] = session_id

        # 追加到文件
        with open(self.annotations_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(annotation, ensure_ascii=False) + '\n')

        return annotation

    def get_annotations(
        self,
        tag: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        查询标注

        Args:
            tag: 按标签过滤
            session_id: 按会话 ID 过滤
            limit: 最多返回数量

        Returns:
            标注列表（按时间倒序）
        """
        if not self.annotations_file.exists():
            return []

        annotations = []

        with open(self.annotations_file, 'r', encoding='utf-8') as f:
            for line in f:
                # 跳过注释行
                if line.startswith('#'):
                    continue

                try:
                    annotation = json.loads(line)

                    # 过滤
                    if tag and annotation.get('tag') != tag:
                        continue

                    if session_id and annotation.get('session_id') != session_id:
                        continue

                    annotations.append(annotation)
                except json.JSONDecodeError:
                    continue

        # 按时间倒序
        annotations.sort(key=lambda x: x['timestamp'], reverse=True)

        # 限制数量
        if limit:
            annotations = annotations[:limit]

        return annotations

    def get_summary(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取标注摘要

        Args:
            session_id: 会话 ID，None 表示所有

        Returns:
            摘要信息
        """
        annotations = self.get_annotations(session_id=session_id)

        # 按标签分组
        by_tag = {}
        for annotation in annotations:
            tag = annotation['tag']
            if tag not in by_tag:
                by_tag[tag] = []
            by_tag[tag].append(annotation)

        return {
            "total": len(annotations),
            "by_tag": {tag: len(items) for tag, items in by_tag.items()},
            "latest": annotations[:5] if annotations else []
        }

    def export_to_markdown(
        self,
        output_file: Path,
        session_id: Optional[str] = None
    ):
        """
        导出标注到 Markdown 文件

        Args:
            output_file: 输出文件路径
            session_id: 会话 ID，None 表示所有
        """
        annotations = self.get_annotations(session_id=session_id)

        # 按标签分组
        by_tag = {}
        for annotation in annotations:
            tag = annotation['tag']
            if tag not in by_tag:
                by_tag[tag] = []
            by_tag[tag].append(annotation)

        # 生成 Markdown
        lines = [
            "# Conversation Annotations",
            "",
            f"**Total**: {len(annotations)} annotations",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]

        if session_id:
            lines.append(f"**Session**: {session_id}")
            lines.append("")

        # 按标签输出
        for tag in sorted(by_tag.keys()):
            items = by_tag[tag]
            lines.append(f"## {tag.replace('-', ' ').title()} ({len(items)})")
            lines.append("")

            for item in items:
                timestamp = item['timestamp'][:19]  # 去掉毫秒
                role = item['role']
                text = item['text']
                turn = item.get('turn', '?')

                lines.append(f"### Turn {turn} - {timestamp}")
                lines.append(f"**Role**: {role}")
                lines.append(f"**Text**: {text}")
                lines.append("")

        # 写入文件
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Annotation Manager - 对话标注管理工具'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # add 命令
    add_parser = subparsers.add_parser('add', help='Add annotation')
    add_parser.add_argument('text', help='Annotation text')
    add_parser.add_argument('--tag', required=True, choices=VALID_TAGS)
    add_parser.add_argument('--role', default='assistant', choices=['user', 'assistant'])
    add_parser.add_argument('--turn', type=int, help='Conversation turn')
    add_parser.add_argument('--session-id', help='Session ID')

    # list 命令
    list_parser = subparsers.add_parser('list', help='List annotations')
    list_parser.add_argument('--tag', choices=VALID_TAGS, help='Filter by tag')
    list_parser.add_argument('--session-id', help='Filter by session ID')
    list_parser.add_argument('--limit', type=int, default=20, help='Max results')

    # summary 命令
    summary_parser = subparsers.add_parser('summary', help='Show summary')
    summary_parser.add_argument('--session-id', help='Filter by session ID')

    # export 命令
    export_parser = subparsers.add_parser('export', help='Export to markdown')
    export_parser.add_argument('output', type=Path, help='Output file')
    export_parser.add_argument('--session-id', help='Filter by session ID')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # 初始化管理器
    manager = AnnotationManager()

    # 执行命令
    if args.command == 'add':
        annotation = manager.add_annotation(
            text=args.text,
            tag=args.tag,
            role=args.role,
            turn=args.turn,
            session_id=args.session_id
        )
        print(f"✓ Annotation added: {annotation['tag']}")
        return 0

    elif args.command == 'list':
        annotations = manager.get_annotations(
            tag=args.tag,
            session_id=args.session_id,
            limit=args.limit
        )

        if not annotations:
            print("No annotations found")
            return 0

        print(f"Found {len(annotations)} annotation(s):\n")
        for i, annotation in enumerate(annotations, 1):
            timestamp = annotation['timestamp'][:19]
            tag = annotation['tag']
            text = annotation['text']
            turn = annotation.get('turn', '?')

            print(f"{i}. [{tag}] Turn {turn} @ {timestamp}")
            print(f"   {text}")
            print()

        return 0

    elif args.command == 'summary':
        summary = manager.get_summary(session_id=args.session_id)

        print(f"Total annotations: {summary['total']}")
        print("\nBy tag:")
        for tag, count in sorted(summary['by_tag'].items()):
            print(f"  {tag}: {count}")

        if summary['latest']:
            print("\nLatest 5:")
            for i, annotation in enumerate(summary['latest'], 1):
                timestamp = annotation['timestamp'][:19]
                tag = annotation['tag']
                text = annotation['text'][:50]
                print(f"  {i}. [{tag}] {text}... @ {timestamp}")

        return 0

    elif args.command == 'export':
        manager.export_to_markdown(args.output, session_id=args.session_id)
        print(f"✓ Annotations exported to {args.output}")
        return 0

    return 0


if __name__ == '__main__':
    sys.exit(main())

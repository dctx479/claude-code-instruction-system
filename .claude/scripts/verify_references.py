#!/usr/bin/env python3
"""
验证 CLAUDE.md 中引用的所有文件是否存在
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Set

def extract_file_references(content: str) -> Set[str]:
    """从 Markdown 内容中提取所有文件路径引用"""
    references = set()

    # 匹配模式：
    # 1. `path/to/file.md` (反引号包裹)
    # 2. 详见: `path/to/file.md`
    # 3. 参见: `path/to/file.md`
    # 4. 详细文档: `path/to/file.md`

    patterns = [
        r'`([a-zA-Z0-9_\-./]+\.(?:md|sh|json|py))`',  # 反引号包裹的文件路径
        r'详见[：:]\s*`([^`]+)`',  # 详见: `path`
        r'参见[：:]\s*`([^`]+)`',  # 参见: `path`
        r'详细文档[：:]\s*`([^`]+)`',  # 详细文档: `path`
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # 清理路径
            path = match.strip()
            # 跳过 URL 和特殊路径
            if path.startswith('http') or path.startswith('~') or path.startswith('$'):
                continue
            # 跳过命令和变量
            if '<' in path or '>' in path or '{' in path:
                continue
            references.add(path)

    return references

def verify_file_exists(base_path: Path, file_path: str) -> bool:
    """验证文件是否存在"""
    full_path = base_path / file_path
    return full_path.exists()

def categorize_references(references: Set[str]) -> dict:
    """将引用按类型分类"""
    categories = {
        'agents': [],
        'skills': [],
        'commands': [],
        'docs': [],
        'workflows': [],
        'integrations': [],
        'examples': [],
        'memory': [],
        'specs': [],
        'config': [],
        'hooks': [],
        'scripts': [],
        'tools': [],
        'other': []
    }

    for ref in references:
        if ref.startswith('agents/'):
            categories['agents'].append(ref)
        elif ref.startswith('.claude/skills/') or ref.startswith('skills/'):
            categories['skills'].append(ref)
        elif ref.startswith('commands/'):
            categories['commands'].append(ref)
        elif ref.startswith('docs/'):
            categories['docs'].append(ref)
        elif ref.startswith('workflows/'):
            categories['workflows'].append(ref)
        elif ref.startswith('integrations/') or ref.startswith('.claude/integrations/'):
            categories['integrations'].append(ref)
        elif ref.startswith('examples/') or ref.startswith('.claude/examples/'):
            categories['examples'].append(ref)
        elif ref.startswith('memory/'):
            categories['memory'].append(ref)
        elif ref.startswith('specs/'):
            categories['specs'].append(ref)
        elif ref.startswith('config/'):
            categories['config'].append(ref)
        elif ref.startswith('hooks/'):
            categories['hooks'].append(ref)
        elif ref.startswith('scripts/'):
            categories['scripts'].append(ref)
        elif ref.startswith('tools/'):
            categories['tools'].append(ref)
        else:
            categories['other'].append(ref)

    return categories

def main():
    # 项目根目录
    base_path = Path(__file__).parent.parent.parent
    claude_md = base_path / 'CLAUDE.md'

    # 读取 CLAUDE.md
    with open(claude_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取所有文件引用
    references = extract_file_references(content)

    # 分类引用
    categorized = categorize_references(references)

    # 验证文件存在性
    existing_files = []
    missing_files = []

    for ref in sorted(references):
        if verify_file_exists(base_path, ref):
            existing_files.append(ref)
        else:
            missing_files.append(ref)

    # 生成报告
    report = []
    report.append("# 文件验证报告\n")
    report.append(f"生成时间: {os.popen('date').read().strip()}\n")
    report.append(f"总引用数: {len(references)}\n")
    report.append(f"存在文件: {len(existing_files)}\n")
    report.append(f"缺失文件: {len(missing_files)}\n")
    report.append("\n---\n")

    # 按类别显示存在的文件
    report.append("\n## 存在的文件（✅）\n")
    for category, files in categorized.items():
        if not files:
            continue
        existing_in_category = [f for f in files if f in existing_files]
        if existing_in_category:
            report.append(f"\n### {category.upper()}\n")
            for file in sorted(existing_in_category):
                report.append(f"- ✅ {file}\n")

    # 按类别显示缺失的文件
    report.append("\n## 缺失的文件（❌）\n")
    for category, files in categorized.items():
        if not files:
            continue
        missing_in_category = [f for f in files if f in missing_files]
        if missing_in_category:
            report.append(f"\n### {category.upper()}\n")
            for file in sorted(missing_in_category):
                report.append(f"- ❌ {file}\n")

    # 建议操作
    report.append("\n## 建议操作\n")
    if missing_files:
        report.append("\n### 优先级 P0（核心文档）\n")
        p0_files = [f for f in missing_files if any(x in f for x in ['INDEX.md', 'README.md', 'TEMPLATE.md'])]
        for file in sorted(p0_files):
            report.append(f"- [ ] 创建 {file}\n")

        report.append("\n### 优先级 P1（Agent 定义）\n")
        p1_files = [f for f in missing_files if f.startswith('agents/') and f not in p0_files]
        for file in sorted(p1_files):
            report.append(f"- [ ] 创建 {file}\n")

        report.append("\n### 优先级 P2（其他文档）\n")
        p2_files = [f for f in missing_files if f not in p0_files and f not in p1_files]
        for file in sorted(p2_files):
            report.append(f"- [ ] 创建 {file}\n")
    else:
        report.append("- ✅ 所有引用的文件都存在！\n")

    # 输出报告
    report_content = ''.join(report)
    print(report_content)

    # 保存报告
    report_file = base_path / '.claude' / 'reports' / 'file-verification-report.md'
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"\n报告已保存到: {report_file}")

if __name__ == '__main__':
    main()

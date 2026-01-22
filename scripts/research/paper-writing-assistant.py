#!/usr/bin/env python3
"""Paper Writing Assistant - 论文写作助手"""
import json
import sys
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

RESEARCH_DIR = Path(".research")
PAPERS_DIR = RESEARCH_DIR / "papers"

def create_paper(title):
    """创建论文项目"""
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)

    # 生成项目目录名
    safe_title = "".join(c if c.isalnum() or c in (' ', '-') else '_' for c in title)
    safe_title = safe_title.replace(' ', '-').lower()[:50]
    paper_dir = PAPERS_DIR / safe_title

    if paper_dir.exists():
        print(f"❌ 论文项目已存在: {paper_dir}")
        return

    paper_dir.mkdir(parents=True)
    (paper_dir / "figures").mkdir()

    # 创建元数据
    metadata = {
        "title": title,
        "created": datetime.now().isoformat(),
        "status": "draft",
        "word_count": 0,
        "references": []
    }

    with open(paper_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # 创建初始文件
    (paper_dir / "draft.md").write_text(f"# {title}\n\n", encoding="utf-8")
    (paper_dir / "references.bib").write_text("", encoding="utf-8")
    (paper_dir / "CLAUDE.md").write_text("# 写作指南\n\n待生成...\n", encoding="utf-8")
    (paper_dir / "IMPLEMENT.md").write_text("# 写作计划\n\n待生成...\n", encoding="utf-8")

    print(f"✅ 论文项目已创建: {paper_dir}")
    print(f"\n📁 项目结构:")
    print(f"  {paper_dir}/")
    print(f"  ├── draft.md          # 论文草稿")
    print(f"  ├── references.bib    # 引用文件")
    print(f"  ├── CLAUDE.md         # 写作指南")
    print(f"  ├── IMPLEMENT.md      # 写作计划")
    print(f"  ├── metadata.json     # 元数据")
    print(f"  └── figures/          # 图表目录")

def list_papers():
    """列出所有论文项目"""
    if not PAPERS_DIR.exists():
        print("📚 暂无论文项目")
        return

    papers = []
    for paper_dir in PAPERS_DIR.iterdir():
        if paper_dir.is_dir():
            metadata_file = paper_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, encoding="utf-8") as f:
                    metadata = json.load(f)
                papers.append((paper_dir.name, metadata))

    if not papers:
        print("📚 暂无论文项目")
        return

    print(f"\n📚 论文项目列表 (共 {len(papers)} 个):\n")
    for name, metadata in papers:
        print(f"📄 {metadata['title']}")
        print(f"   目录: {name}")
        print(f"   状态: {metadata['status']}")
        print(f"   字数: {metadata['word_count']}")
        print(f"   创建: {metadata['created'][:10]}")
        print()

def update_word_count(paper_name):
    """更新字数统计"""
    paper_dir = PAPERS_DIR / paper_name
    if not paper_dir.exists():
        print(f"❌ 论文项目不存在: {paper_name}")
        return

    draft_file = paper_dir / "draft.md"
    if not draft_file.exists():
        print(f"❌ 草稿文件不存在")
        return

    content = draft_file.read_text(encoding="utf-8")
    word_count = len(content.split())

    metadata_file = paper_dir / "metadata.json"
    with open(metadata_file, encoding="utf-8") as f:
        metadata = json.load(f)

    metadata["word_count"] = word_count

    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ 字数统计已更新: {word_count} 词")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python paper-writing-assistant.py create <title>")
        print("  python paper-writing-assistant.py list")
        print("  python paper-writing-assistant.py update-count <paper_name>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "create":
        if len(sys.argv) < 3:
            print("用法: create <title>")
            sys.exit(1)
        title = " ".join(sys.argv[2:])
        create_paper(title)
    elif cmd == "list":
        list_papers()
    elif cmd == "update-count":
        if len(sys.argv) < 3:
            print("用法: update-count <paper_name>")
            sys.exit(1)
        update_word_count(sys.argv[2])
    else:
        print(f"❌ 未知命令: {cmd}")
        sys.exit(1)

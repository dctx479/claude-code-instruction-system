#!/usr/bin/env python3
"""Literature Manager - 文献管理工具"""
import json
import sys
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

RESEARCH_DIR = Path(".research")
LITERATURE_DIR = RESEARCH_DIR / "literature"
INDEX_FILE = LITERATURE_DIR / "index.json"

def init_literature_db():
    """初始化文献数据库"""
    LITERATURE_DIR.mkdir(parents=True, exist_ok=True)

    if not INDEX_FILE.exists():
        index = {
            "papers": [],
            "collections": {},
            "tags": {},
            "metadata": {
                "created": datetime.now().isoformat(),
                "total_papers": 0
            }
        }
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        print(f"✅ 文献数据库已初始化: {INDEX_FILE}")
    else:
        print(f"📚 文献数据库已存在: {INDEX_FILE}")

def add_paper(title, authors, year, venue="", tags=None, summary=""):
    """添加文献"""
    with open(INDEX_FILE, encoding="utf-8") as f:
        index = json.load(f)

    paper_id = f"paper-{len(index['papers']) + 1:03d}"
    paper = {
        "id": paper_id,
        "title": title,
        "authors": authors if isinstance(authors, list) else [authors],
        "year": year,
        "venue": venue,
        "tags": tags or [],
        "summary": summary,
        "added_date": datetime.now().isoformat()
    }

    index["papers"].append(paper)
    index["metadata"]["total_papers"] = len(index["papers"])

    # 更新标签索引
    for tag in paper["tags"]:
        if tag not in index["tags"]:
            index["tags"][tag] = []
        index["tags"][tag].append(paper_id)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"✅ 已添加文献: {paper_id} - {title}")
    return paper_id

def list_papers(tag=None):
    """列出文献"""
    if not INDEX_FILE.exists():
        print("❌ 文献数据库不存在，请先运行 init")
        return

    with open(INDEX_FILE, encoding="utf-8") as f:
        index = json.load(f)

    papers = index["papers"]

    if tag:
        paper_ids = index["tags"].get(tag, [])
        papers = [p for p in papers if p["id"] in paper_ids]

    if not papers:
        print("📚 暂无文献")
        return

    print(f"\n📚 文献列表 (共 {len(papers)} 篇):\n")
    for paper in papers:
        print(f"[{paper['id']}] {paper['title']}")
        print(f"  作者: {', '.join(paper['authors'])}")
        print(f"  年份: {paper['year']} | 来源: {paper['venue']}")
        print(f"  标签: {', '.join(paper['tags'])}")
        print()

def search_papers(query):
    """搜索文献"""
    if not INDEX_FILE.exists():
        print("❌ 文献数据库不存在")
        return

    with open(INDEX_FILE, encoding="utf-8") as f:
        index = json.load(f)

    query_lower = query.lower()
    results = []

    for paper in index["papers"]:
        if (query_lower in paper["title"].lower() or
            query_lower in paper.get("summary", "").lower() or
            any(query_lower in tag.lower() for tag in paper["tags"])):
            results.append(paper)

    if not results:
        print(f"🔍 未找到匹配 '{query}' 的文献")
        return

    print(f"\n🔍 搜索结果 (共 {len(results)} 篇):\n")
    for paper in results:
        print(f"[{paper['id']}] {paper['title']}")
        print(f"  {', '.join(paper['authors'])} ({paper['year']})")
        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python literature-manager.py init")
        print("  python literature-manager.py add <title> <authors> <year> [venue] [tags]")
        print("  python literature-manager.py list [tag]")
        print("  python literature-manager.py search <query>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        init_literature_db()
    elif cmd == "add":
        if len(sys.argv) < 5:
            print("用法: add <title> <authors> <year> [venue] [tags]")
            sys.exit(1)
        title = sys.argv[2]
        authors = sys.argv[3].split(",")
        year = int(sys.argv[4])
        venue = sys.argv[5] if len(sys.argv) > 5 else ""
        tags = sys.argv[6].split(",") if len(sys.argv) > 6 else []
        add_paper(title, authors, year, venue, tags)
    elif cmd == "list":
        tag = sys.argv[2] if len(sys.argv) > 2 else None
        list_papers(tag)
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("用法: search <query>")
            sys.exit(1)
        search_papers(sys.argv[2])
    else:
        print(f"❌ 未知命令: {cmd}")
        sys.exit(1)

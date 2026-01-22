#!/usr/bin/env python3
"""Experiment Logger - 实验记录工具"""
import json
import sys
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

RESEARCH_DIR = Path(".research")
EXPERIMENTS_DIR = RESEARCH_DIR / "experiments"
INDEX_FILE = EXPERIMENTS_DIR / "index.json"

def init_experiments():
    """初始化实验目录"""
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)

    if not INDEX_FILE.exists():
        index = {
            "experiments": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "total_experiments": 0
            }
        }
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

def create_experiment(title):
    """创建实验记录"""
    init_experiments()

    with open(INDEX_FILE, encoding="utf-8") as f:
        index = json.load(f)

    exp_id = f"exp-{len(index['experiments']) + 1:03d}"
    exp_dir = EXPERIMENTS_DIR / exp_id
    exp_dir.mkdir(parents=True)
    (exp_dir / "results").mkdir()
    (exp_dir / "results" / "plots").mkdir()

    config = {
        "experiment_id": exp_id,
        "title": title,
        "date": datetime.now().isoformat(),
        "status": "running",
        "parameters": {},
        "results": {}
    }

    with open(exp_dir / "config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    log_content = f"""# Experiment Log: {exp_id}

## 实验信息
- **标题**: {title}
- **日期**: {datetime.now().strftime('%Y-%m-%d')}

## 假设
待填写...

## 方法
待填写...

## 实验过程

### {datetime.now().strftime('%Y-%m-%d %H:%M')} - 实验开始
实验创建

## 结果
待记录...

## 结论
待总结...
"""

    (exp_dir / "log.md").write_text(log_content, encoding="utf-8")
    (exp_dir / "reproduce.sh").write_text("#!/bin/bash\n# Reproduction script\n", encoding="utf-8")

    index["experiments"].append(exp_id)
    index["metadata"]["total_experiments"] = len(index["experiments"])

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"✅ 实验已创建: {exp_id}")
    print(f"📁 {exp_dir}/")
    print(f"   ├── config.json")
    print(f"   ├── log.md")
    print(f"   ├── reproduce.sh")
    print(f"   └── results/")

def list_experiments():
    """列出所有实验"""
    if not INDEX_FILE.exists():
        print("🔬 暂无实验记录")
        return

    with open(INDEX_FILE, encoding="utf-8") as f:
        index = json.load(f)

    if not index["experiments"]:
        print("🔬 暂无实验记录")
        return

    print(f"\n🔬 实验列表 (共 {len(index['experiments'])} 个):\n")

    for exp_id in index["experiments"]:
        exp_dir = EXPERIMENTS_DIR / exp_id
        config_file = exp_dir / "config.json"

        if config_file.exists():
            with open(config_file, encoding="utf-8") as f:
                config = json.load(f)

            print(f"[{exp_id}] {config['title']}")
            print(f"  状态: {config['status']}")
            print(f"  日期: {config['date'][:10]}")
            if config.get('results'):
                print(f"  结果: {config['results']}")
            print()

def update_result(exp_id, **metrics):
    """更新实验结果"""
    exp_dir = EXPERIMENTS_DIR / exp_id
    if not exp_dir.exists():
        print(f"❌ 实验不存在: {exp_id}")
        return

    config_file = exp_dir / "config.json"
    with open(config_file, encoding="utf-8") as f:
        config = json.load(f)

    config["results"].update(metrics)
    config["status"] = "completed"

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"✅ 实验结果已更新: {exp_id}")
    for key, value in metrics.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python experiment-logger.py create <title>")
        print("  python experiment-logger.py list")
        print("  python experiment-logger.py result <exp_id> <key=value> ...")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "create":
        if len(sys.argv) < 3:
            print("用法: create <title>")
            sys.exit(1)
        title = " ".join(sys.argv[2:])
        create_experiment(title)
    elif cmd == "list":
        list_experiments()
    elif cmd == "result":
        if len(sys.argv) < 4:
            print("用法: result <exp_id> <key=value> ...")
            sys.exit(1)
        exp_id = sys.argv[2]
        metrics = {}
        for arg in sys.argv[3:]:
            if '=' in arg:
                key, value = arg.split('=', 1)
                try:
                    metrics[key] = float(value)
                except ValueError:
                    metrics[key] = value
        update_result(exp_id, **metrics)
    else:
        print(f"❌ 未知命令: {cmd}")
        sys.exit(1)

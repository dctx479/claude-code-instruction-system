# 外部工具集成指南

**适用工具**: Codex, Gemini, DeepSeek, 其他 LLM/AI 工具  
**集成内容**: 分层笔记、对话标注、检查点审查  
**兼容性**: 100% 工具无关设计

---

## 🎯 设计原则

### 核心理念：工具无关 (Tool-Agnostic)

所有新功能都通过**标准接口**暴露，任何工具都可以使用：

1. **文件系统** - 笔记存储在标准文件中
2. **命令行工具** - Python 脚本提供 CLI 接口
3. **标准格式** - Markdown、JSONL、JSON
4. **无依赖** - 不需要特定 AI 工具

---

## 📦 可用功能

### 功能 1: 分层笔记系统

**工具无关性**: ✅ 完全工具无关

**任何工具都可以**:

```python
# 1. 读取笔记
import os
from pathlib import Path

# 读取 session 笔记
session_notes = Path('.claude/scratch').glob('session-*.md')
for note_file in session_notes:
    content = note_file.read_text(encoding='utf-8')
    print(f"Session note: {content}")

# 读取 workspace 笔记
workspace_notes = Path('.claude/scratch/workspace-notes.md')
if workspace_notes.exists():
    content = workspace_notes.read_text(encoding='utf-8')
    print(f"Workspace notes: {content}")

# 读取 global 笔记
global_notes = Path.home() / '.claude/scratch/global-inbox.md'
if global_notes.exists():
    content = global_notes.read_text(encoding='utf-8')
    print(f"Global notes: {content}")
```

```python
# 2. 写入笔记（通过 Python API）
import sys
sys.path.insert(0, 'scripts')

from note_manager import SessionNotesManager

manager = SessionNotesManager()
manager.add_note('session', 'My note from Codex', tag='idea')
manager.add_note('workspace', 'Project decision', tag='decision')
```

```bash
# 3. 写入笔记（通过命令行）
python scripts/note-manager.py add session "My note" --tag idea
python scripts/note-manager.py add workspace "Decision" --tag decision
python scripts/note-manager.py show
```

### 功能 2: 对话标注系统

**工具无关性**: ✅ 完全工具无关

**任何工具都可以**:

```python
# 1. 读取标注
import json
from pathlib import Path

annotations_file = Path('.claude/context/annotations.jsonl')
if annotations_file.exists():
    annotations = []
    with open(annotations_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                annotations.append(json.loads(line))
    
    print(f"Found {len(annotations)} annotations")
    for ann in annotations:
        print(f"[{ann['tag']}] {ann['text']}")
```

```python
# 2. 写入标注（通过 Python API）
import sys
sys.path.insert(0, 'scripts')

from annotation_manager import AnnotationManager

manager = AnnotationManager()
manager.add_annotation(
    text='Important finding from Gemini',
    tag='key-insight',
    role='assistant'
)
```

```bash
# 3. 写入标注（通过命令行）
python scripts/annotation-manager.py add "Finding" --tag key-insight
python scripts/annotation-manager.py list
python scripts/annotation-manager.py summary
```

### 功能 3: 检查点审查

**工具无关性**: ✅ 完全工具无关

**任何工具都可以**:

```bash
# 1. 审查检查点
python scripts/checkpoint.py review

# 2. 比较检查点
python scripts/checkpoint.py diff \
  --from .git/taiyi/checkpoint-old.json \
  --to .git/taiyi/checkpoint-new.json

# 3. 在任何工具中集成
import subprocess
result = subprocess.run(
    ['python', 'scripts/checkpoint.py', 'review'],
    capture_output=True, text=True
)
print(result.stdout)
```

---

## 🔧 集成示例

### 示例 1: Codex CLI 集成

**场景**: 使用 Codex CLI 时记录笔记和标注

```bash
# Codex CLI 工作流
codex "Analyze this code"  # Codex 分析代码

# 在 Codex 分析后，记录笔记
python scripts/note-manager.py add session "Codex identified bug in line 42"

# 标注关键发现
python scripts/annotation-manager.py add "Memory leak in loop" --tag key-insight

# 查看所有笔记和标注
python scripts/note-manager.py show
python scripts/annotation-manager.py summary
```

### 示例 2: Gemini 集成

**场景**: 使用 Gemini API 时使用笔记系统

```python
import google.generativeai as genai
import sys
sys.path.insert(0, 'scripts')
from note_manager import SessionNotesManager
from annotation_manager import AnnotationManager

# 初始化
note_mgr = SessionNotesManager()
ann_mgr = AnnotationManager()

# 使用 Gemini
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Explain quantum computing")

# 记录 Gemini 的回复
note_mgr.add_note('session', f"Gemini explanation: {response.text[:100]}...", tag='idea')

# 标注关键点
if "superposition" in response.text:
    ann_mgr.add_annotation(
        text="Gemini mentioned superposition",
        tag='key-insight',
        role='assistant'
    )

print("Notes and annotations saved!")
```

### 示例 3: DeepSeek Coder 集成

**场景**: 使用 DeepSeek Coder 时记录决策

```python
import requests
import sys
sys.path.insert(0, 'scripts')
from note_manager import SessionNotesManager

note_mgr = SessionNotesManager()

# 调用 DeepSeek API
response = requests.post(
    "https://api.deepseek.com/v1/chat/completions",
    headers={"Authorization": "Bearer YOUR_KEY"},
    json={"model": "deepseek-coder", "messages": [...]}
)

result = response.json()['choices'][0]['message']['content']

# 记录 DeepSeek 的建议
note_mgr.add_note('workspace', f"DeepSeek suggests: {result}", tag='decision')

print("DeepSeek suggestion saved to workspace notes")
```

### 示例 4: 多工具协作

**场景**: 同时使用 Claude + Codex + Gemini

```python
import sys
sys.path.insert(0, 'scripts')
from note_manager import SessionNotesManager
from annotation_manager import AnnotationManager

note_mgr = SessionNotesManager()
ann_mgr = AnnotationManager()

# Claude 分析
claude_result = "Use JWT for auth"
note_mgr.add_note('session', f"Claude: {claude_result}", tag='decision')

# Codex 实现
codex_code = "def authenticate(token): ..."
note_mgr.add_note('session', f"Codex implemented: {codex_code[:50]}", tag='idea')

# Gemini 审查
gemini_review = "Security looks good"
ann_mgr.add_annotation(f"Gemini review: {gemini_review}", tag='key-insight')

# 统一复盘
print("=== Multi-tool collaboration summary ===")
print(note_mgr.show_notes('session'))
print(ann_mgr.get_summary())
```

---

## 📋 通用集成模式

### 模式 1: 命令行集成 (推荐)

**适用**: 任何支持执行 shell 命令的工具

```bash
# 任何工具都可以调用
python scripts/note-manager.py add session "Content"
python scripts/annotation-manager.py add "Content" --tag key-insight
python scripts/checkpoint.py review
```

**优点**:
- ✅ 完全工具无关
- ✅ 无需 Python API 依赖
- ✅ 可在任何环境使用

### 模式 2: Python API 集成

**适用**: Python 环境或支持 Python 调用的工具

```python
import sys
sys.path.insert(0, 'path/to/scripts')

from note_manager import SessionNotesManager
from annotation_manager import AnnotationManager

# 使用 Python API
note_mgr = SessionNotesManager()
ann_mgr = AnnotationManager()
```

**优点**:
- ✅ 类型安全
- ✅ 更好的错误处理
- ✅ 更灵活的集成

### 模式 3: 文件系统直接访问

**适用**: 任何可以读写文件的工具

```python
# 直接读写文件
from pathlib import Path
import json

# 读取笔记
notes = Path('.claude/scratch/workspace-notes.md').read_text()

# 写入标注
with open('.claude/context/annotations.jsonl', 'a') as f:
    annotation = {
        "text": "My annotation",
        "tag": "key-insight",
        "timestamp": "2025-01-23T10:00:00Z"
    }
    f.write(json.dumps(annotation) + '\n')
```

**优点**:
- ✅ 最大灵活性
- ✅ 无需任何依赖
- ✅ 可在任何语言使用

---

## 🛠️ 工具专用集成指南

### Codex CLI

**更新 `.claude/skills/collaborating-with-codex/SKILL.md`**:

在技能说明中添加：

```markdown
## 使用分层笔记和标注

Codex CLI 可以完全使用分层笔记系统：

### 记录 Codex 输出
codex "task" > output.txt
python scripts/note-manager.py add session "Codex completed: $(cat output.txt | head -1)"

### 标注关键发现
python scripts/annotation-manager.py add "Codex identified optimization" --tag key-insight

### 查看所有笔记
python scripts/note-manager.py show session
```

### Gemini API

**更新 `.claude/skills/collaborating-with-gemini/SKILL.md`**:

在技能说明中添加：

```markdown
## 使用分层笔记和标注

Gemini 可以完全使用分层笔记系统：

### Python 集成
import sys
sys.path.insert(0, 'scripts')
from note_manager import SessionNotesManager

note_mgr = SessionNotesManager()
# Gemini 分析后
note_mgr.add_note('session', f"Gemini: {response.text}", tag='idea')

### 命令行集成
python scripts/note-manager.py add session "Gemini analysis result"
```

---

## 📖 通用使用指南

### 步骤 1: 初始化（一次性）

```bash
# 确保目录存在
mkdir -p .claude/scratch
mkdir -p .claude/context

# 验证工具可用
python scripts/note-manager.py --help
python scripts/annotation-manager.py --help
```

### 步骤 2: 在工作流中集成

```bash
# 任何工具工作流:
# 1. 执行任务
your-tool "task"

# 2. 记录结果
python scripts/note-manager.py add session "Result from your-tool"

# 3. 标注关键点
python scripts/annotation-manager.py add "Key finding" --tag key-insight

# 4. 查看汇总
python scripts/note-manager.py show
python scripts/annotation-manager.py summary
```

### 步骤 3: 跨工具协作

```bash
# 多工具协作模式:
# Claude 分析
claude-code "analyze code"
python scripts/note-manager.py add session "Claude: Use design pattern X"

# Codex 实现
codex "implement pattern X"
python scripts/note-manager.py add session "Codex: Implementation complete"

# Gemini 审查
gemini "review implementation"
python scripts/annotation-manager.py add "Gemini: Looks good" --tag key-insight

# 统一复盘
python scripts/note-manager.py show session
python scripts/annotation-manager.py export review.md
```

---

## ✅ 兼容性确认

### 工具无关性验证

| 工具 | 命令行 | Python API | 文件系统 | 状态 |
|------|--------|-----------|---------|------|
| **Claude Code** | ✅ | ✅ | ✅ | 完全支持 |
| **Codex CLI** | ✅ | ✅ | ✅ | 完全支持 |
| **Gemini API** | ✅ | ✅ | ✅ | 完全支持 |
| **DeepSeek Coder** | ✅ | ✅ | ✅ | 完全支持 |
| **GPT-4 API** | ✅ | ✅ | ✅ | 完全支持 |
| **任何其他工具** | ✅ | ✅ | ✅ | 完全支持 |

### 接口标准

所有工具都通过标准接口访问：

1. **文件格式**: Markdown (笔记), JSONL (标注), JSON (检查点)
2. **文件位置**: `.claude/scratch/`, `.claude/context/`, `~/.claude/scratch/`
3. **命令行**: Python 脚本提供统一 CLI
4. **无锁定**: 无需特定工具，任何工具都可以使用

---

## 🎯 最佳实践

### 1. 跨工具标注约定

使用统一的标注格式，包含工具来源：

```bash
# 格式: [工具名] 内容
python scripts/annotation-manager.py add "[Codex] Found optimization" --tag key-insight
python scripts/annotation-manager.py add "[Gemini] Security validated" --tag decision
python scripts/annotation-manager.py add "[Claude] Architecture review" --tag key-insight
```

### 2. 工具专用标签

为不同工具使用专用标签前缀：

```bash
# Codex 相关
--tag codex-suggestion
--tag codex-implementation

# Gemini 相关
--tag gemini-analysis
--tag gemini-review

# Claude 相关
--tag claude-decision
--tag claude-insight
```

### 3. 统一复盘流程

无论使用哪些工具，使用统一的复盘流程：

```bash
# 1. 查看所有笔记
python scripts/note-manager.py show

# 2. 查看所有标注
python scripts/annotation-manager.py summary

# 3. 导出完整报告
python scripts/annotation-manager.py export multi-tool-report.md

# 4. 检查点审查
python scripts/checkpoint.py review
```

---

## 📚 相关文档

- **主文档**: `docs/SESSION-NOTES-GUIDE.md`
- **技术规格**: `specs/SPEC-deepseek-inspired-enhancements.md`
- **Codex 集成**: `.claude/skills/collaborating-with-codex/SKILL.md`
- **Gemini 集成**: `.claude/skills/collaborating-with-gemini/SKILL.md`

---

## 🎉 总结

✅ **所有外部工具都可以使用分层笔记和标注系统**  
✅ **完全工具无关设计**  
✅ **三种集成模式：命令行、Python API、文件系统**  
✅ **支持多工具协作**  
✅ **统一的复盘流程**

**任何 AI 工具都可以无缝集成！**

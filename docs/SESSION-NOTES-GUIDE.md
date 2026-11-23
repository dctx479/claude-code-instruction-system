# Session Notes 使用指南

## 概述

Session Notes 是基于 DeepSeek 笔记生态启发的分层临时笔记系统，提供三级作用域的轻量化信息记录。

**核心理念**: 持久化是"分层衰减"而非"全有或全无"
- **session**: 临时想法，compact 后归档
- **workspace**: 项目相关，跨会话保留  
- **global**: 通用经验，跨项目复用

---

## 快速开始

### 命令概览

```bash
# 添加笔记
/note session <内容>      # 会话级笔记
/note workspace <内容>    # 工作区级笔记
/note global <内容>       # 全局笔记

# 查看笔记
/note show [scope]        # 显示指定作用域笔记

# 清空笔记
/note clear [scope]       # 清空指定作用域

# Python 命令行工具
python scripts/note-manager.py add session "Your note" --tag idea
python scripts/note-manager.py show
python scripts/note-manager.py archive
```

---

## 使用场景

### 场景 1: 长调试会话

**问题**: 调试过程中发现多个临时线索，容易忘记

```
尝试方法 A 失败 → /note session 方法 A 失败，报错 ECONNREFUSED
尝试方法 B 成功 → /note session Docker exec 绕过了网络路由问题
准备 compact → /note show session → 归档笔记
```

### 场景 2: 跨会话项目开发

**问题**: 昨天的技术决策今天忘记了

```
会话 1: /note workspace 使用 JWT 而非 session cookie，理由：支持跨域
会话 2: /note show workspace → 查看昨天的决策
会话 3: /note workspace token 有效期设为 7 天，刷新窗口 24 小时
```

### 场景 3: 通用经验积累

**问题**: 解决了一个问题，下次遇到又忘了

```
解决问题 → /note global PowerShell 2>&1 会导致 $? 误判，改用 try-catch
下次遇到 → /note show global → 快速定位解决方案
定期整理 → 将 global-inbox.md 迁移到 memory/lessons-learned.md
```

---

## 标签类型

| 标签 | 含义 | 适用场景 |
|------|------|---------|
| `idea` | 灵感想法 | 临时创意、探索方向 |
| `todo` | 待办事项 | 需要执行的任务 |
| `assumption` | 待验证假设 | 实验设计、理论推测 |
| `question` | 未解决问题 | 需要调查的疑问 |
| `insight` | 关键洞察 | 重要发现、经验教训 |
| `decision` | 重要决策 | 技术选型、架构决策 |
| `config` | 配置说明 | 重要配置项、环境设置 |

---

## 文件位置

### 项目级笔记
```
.claude/scratch/
  session-{session-id}.md        # 当前会话笔记
  workspace-notes.md             # 工作区笔记
  archive/
    session-{id}-archived-*.md   # 归档的会话笔记
```

### 全局笔记
```
~/.claude/scratch/
  global-inbox.md                # 全局收件箱
```

---

## 生命周期管理

### Session 笔记
- **创建**: 首次使用 `/note session` 时自动创建
- **归档**: `/compact` 或 `/handoff` 时自动归档到 `archive/`
- **清理**: 建议保留 30 天的归档文件

### Workspace 笔记
- **创建**: 首次使用 `/note workspace` 时自动创建
- **清理**: 任务完成后手动整理到 `memory/*.md`
- **归档**: 项目归档时一并归档

### Global 笔记
- **创建**: 首次使用 `/note global` 时自动创建
- **清理**: 每月整理一次，提取到 `memory/best-practices.md`
- **归档**: 用户决定

---

## 与现有系统集成

### 与 `/handoff` 集成

`/handoff` 执行时：
1. 检查未归档的 session 笔记
2. 在交接文档中包含笔记摘要
3. 提示用户决定是否归档

### 与 `/reflection` 集成

`/reflection` 执行时：
1. 自动读取当前 session 笔记
2. 优先提取已标注的关键信息
3. 将笔记内容纳入复盘分析

### 与 `context-archivist` 集成

生成 resolution 时：
1. 读取 session/workspace 笔记
2. 提取 `insight` 和 `decision` 到 resolution
3. 标记 `assumption` 为待验证项

---

## 对话标注系统

### 添加标注

```bash
# 在对话中使用 !mark 命令
!mark key-insight                    # 标记上一条助手回复
!mark todo 验证 token 刷新逻辑       # 标记指定文本

# 使用 Python 工具
python scripts/annotation-manager.py add "Important insight" --tag key-insight --turn 15
```

### 查询标注

```bash
# 列出所有标注
python scripts/annotation-manager.py list

# 按标签过滤
python scripts/annotation-manager.py list --tag key-insight

# 查看摘要
python scripts/annotation-manager.py summary

# 导出到 Markdown
python scripts/annotation-manager.py export annotations.md
```

### 标注标签

- `key-insight`: 关键洞察
- `todo`: 待办事项
- `assumption`: 待验证假设
- `question`: 未解决问题
- `decision`: 重要决策
- `anti-pattern`: 错误尝试

---

## 检查点审查

### 审查检查点状态

```bash
# 审查当前检查点
python scripts/checkpoint.py review

# 审查指定检查点
python scripts/checkpoint.py review --checkpoint path/to/checkpoint.json

# 详细模式（显示 hash）
CHECKPOINT_VERBOSE=1 python scripts/checkpoint.py review
```

### 输出说明

```
✅ file.txt (verified)        # 文件验证通过
⚠️  file.txt (missing)         # 文件缺失
⛔ file.txt (modified)        # 文件已修改
🆕 file.txt (new)             # 新文件，未在检查点中
```

### 比较检查点

```bash
python scripts/checkpoint.py diff \
  --from .git/taiyi/checkpoint-old.json \
  --to .git/taiyi/checkpoint-new.json
```

---

## 注意事项

### 隐私与安全

- ⚠️ 不要在笔记中记录敏感信息（密码、API key）
- ⚠️ `.claude/scratch/` 已添加到 `.gitignore`
- ⚠️ global 笔记跨项目可见，避免项目专属信息

### 整理策略

- **session**: 自动归档，定期清理 archive（建议 30 天）
- **workspace**: 任务完成后整理到 `memory/*.md`
- **global**: 每月整理一次，提取到 `best-practices.md`

### 与结构化记忆的关系

```
临时笔记 → 任务复盘 → 结构化记忆
(session-notes) → (reflection) → (memory/*.md)
  轻量、易失      提炼、验证      持久、溯源
```

session-notes 是"记录缓冲区"，不是最终存储。

---

## 故障排查

### 问题: session 笔记没有自动归档

**原因**: `/compact` 或 `/handoff` 没有触发归档逻辑

**解决方案**:
```bash
# 手动归档
python scripts/note-manager.py archive
```

### 问题: 标注文件损坏

**原因**: JSONL 文件部分行格式错误

**解决方案**:
```bash
# 验证 JSONL 格式
python -c "
import json
with open('.claude/context/annotations.jsonl') as f:
    for i, line in enumerate(f, 1):
        if line.startswith('#'): continue
        try:
            json.loads(line)
        except:
            print(f'Line {i} invalid')
"
```

### 问题: global 笔记看不到

**原因**: 路径错误或权限问题

**解决方案**:
```bash
# 检查路径
ls ~/.claude/scratch/global-inbox.md

# 手动创建（如果不存在）
mkdir -p ~/.claude/scratch
python scripts/note-manager.py add global "Test note"
```

---

## API 参考

### SessionNotesManager

```python
from scripts.note_manager import SessionNotesManager

manager = SessionNotesManager()

# 添加笔记
manager.add_note('session', 'Note content', tag='idea')

# 显示笔记
output = manager.show_notes(scope='session')

# 归档
archive_file = manager.archive_session_notes()
```

### AnnotationManager

```python
from scripts.annotation_manager import AnnotationManager

manager = AnnotationManager()

# 添加标注
manager.add_annotation(
    text='Important finding',
    tag='key-insight',
    turn=15
)

# 查询标注
annotations = manager.get_annotations(tag='key-insight', limit=10)

# 获取摘要
summary = manager.get_summary()
```

---

## 相关文档

- `specs/SPEC-deepseek-inspired-enhancements.md` - 完整技术规格
- `.claude/skills/session-notes/SKILL.md` - Skill 定义
- `docs/CONTEXT-ENGINEERING-GUIDE.md` - 上下文工程指南
- `analysis/deepseek-notes-analysis.md` - 原始分析报告

---

## 版本历史

- **v1.0.0** (2025-01-XX): 初始版本
  - 分层临时笔记系统 (session/workspace/global)
  - 对话标注系统 (6 种标签类型)
  - 检查点交互式审查 (review/diff)

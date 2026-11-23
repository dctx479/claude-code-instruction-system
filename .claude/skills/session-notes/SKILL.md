---
name: session-notes
description: 分层临时笔记系统 - 管理 session/workspace/global 三级作用域的临时笔记，降低"临时想法"丢失率
license: MIT
metadata:
  category: system
  tags:
  - notes
  - session-management
  - context-engineering
  - annotation
  integration:
  - handoff
  - reflection
  - context-archivist
  version: 1.0.0
  trigger:
  - /note
  - 记笔记
  - 记住这个
  - 临时记录
disable-model-invocation: false
---

# session-notes Skill

## 功能概述

分层临时笔记系统，提供三级作用域的轻量化信息记录，填补"对话中临时想法无处记录"的盲区。

**设计理念**: 持久化是"分层衰减"而非"全有或全无"
- **session**: 临时想法，compact 后归档
- **workspace**: 项目相关，跨会话保留
- **global**: 通用经验，跨项目复用

---

## 命令接口

### `/note session <内容>`
追加到会话级笔记（`.claude/scratch/session-{session-id}.md`）

**用途**: 
- 对话中的临时想法
- 待验证的假设
- 即将丢失的灵感

**生命周期**: `/compact` 或会话结束时自动归档到 `.claude/scratch/archive/`

**示例**:
```
/note session Docker exec 可能绕过网络路由问题
/note session 假设：token 存储在 httpOnly cookie 中
/note session 待办：验证 rate limiting 逻辑
```

### `/note workspace <内容>`
追加到工作区级笔记（`.claude/scratch/workspace-notes.md`）

**用途**:
- 项目级待办事项
- 跨会话的技术决策
- 重要配置说明

**生命周期**: 手动清理或项目归档时清空

**示例**:
```
/note workspace 数据库连接池大小设为 20
/note workspace 认证 token 有效期 7 天
/note workspace Redis 用于会话存储
```

### `/note global <内容>`
追加到全局笔记（`~/.claude/scratch/global-inbox.md`）

**用途**:
- 跨项目的通用经验
- 工具使用技巧
- 常见问题解决方案

**生命周期**: 用户手动整理

**示例**:
```
/note global PowerShell 中 2>&1 会导致 $? 误判
/note global git worktree 需要 --detach 避免分支冲突
/note global Claude Code 的 Read 工具有行数限制
```

### `/note show [scope]`
显示指定作用域的笔记

**参数**:
- `scope`: `session` | `workspace` | `global` | `all`（默认 `all`）

**输出格式**:
```markdown
=== Session Notes (session-abc123-20250120) ===
## 2025-01-20 10:30 - idea
Docker exec 可能绕过网络路由问题

## 2025-01-20 10:45 - assumption
假设：token 存储在 httpOnly cookie 中

=== Workspace Notes ===
## 2025-01-18 - decision
数据库连接池大小设为 20

=== Global Notes ===
## 2025-01-15 - insight
PowerShell 中 2>&1 会导致 $? 误判
```

### `/note clear [scope]`
清空指定作用域的笔记（需确认）

**参数**:
- `scope`: `session` | `workspace` | `global`

**行为**:
- session: 移动到 archive 而非删除
- workspace: 需要用户明确确认
- global: 需要用户明确确认

---

## 文件格式

### Session 笔记格式

```markdown
# Session Notes - {session-id}
Created: {timestamp}
Project: {project-name}

## {timestamp} - {tag}
{content}

## {timestamp} - {tag}
{content}
```

### Workspace 笔记格式

```markdown
# Workspace Notes - {project-name}
Last Updated: {timestamp}

## {timestamp} - {tag}
{content}
```

### Global 笔记格式

```markdown
# Global Inbox
Last Updated: {timestamp}

## {timestamp} - {tag} - {project-hint}
{content}
```

### 标签类型

| 标签 | 含义 | 适用场景 |
|------|------|---------|
| `idea` | 灵感想法 | 临时创意、探索方向 |
| `todo` | 待办事项 | 需要执行的任务 |
| `assumption` | 待验证假设 | 实验设计、理论推测 |
| `question` | 未解决问题 | 需要调查的疑问 |
| `insight` | 关键洞察 | 重要发现、经验教训 |
| `decision` | 重要决策 | 技术选型、架构决策 |
| `config` | 配置说明 | 重要配置项、环境设置 |

标签在内容中可选，默认为 `note`。

---

## Session ID 生成

使用 git commit hash (前 7 位) + 时间戳：

```python
import subprocess
from datetime import datetime

def get_session_id():
    try:
        commit = subprocess.check_output(
            ['git', 'rev-parse', '--short=7', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except:
        commit = 'unknown'
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    return f"{commit}-{timestamp}"
```

---

## 自动归档逻辑

### 触发时机

1. 检测到 `/compact` 命令
2. 检测到 `/handoff` 命令
3. 会话结束（如果可检测）

### 归档策略

```python
def archive_session_notes(session_id, project_root):
    """
    归档会话级笔记到 .claude/scratch/archive/
    """
    from pathlib import Path
    import shutil
    from datetime import datetime
    
    scratch_dir = Path(project_root) / '.claude' / 'scratch'
    archive_dir = scratch_dir / 'archive'
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    session_file = scratch_dir / f'session-{session_id}.md'
    if session_file.exists():
        archive_name = f'session-{session_id}-{datetime.now().strftime("%Y%m%d-%H%M%S")}.md'
        archive_file = archive_dir / archive_name
        shutil.move(str(session_file), str(archive_file))
        return archive_file
    return None
```

---

## 集成点

### 与 `/handoff` 集成

`/handoff` 执行时：
1. 检查是否有未归档的 session 笔记
2. 在交接文档中包含笔记摘要
3. 提示用户决定是否归档或清空

### 与 `/reflection` 集成

`/reflection` 执行时：
1. 自动读取当前 session 笔记
2. 优先提取已标注的关键信息
3. 将笔记内容纳入复盘分析

### 与 `context-archivist` 集成

`context-archivist` 生成 resolution 时：
1. 读取 session/workspace 笔记
2. 将笔记中的 `insight` 和 `decision` 提取到 resolution
3. 将 `assumption` 标记为待验证项

---

## 使用场景

### 场景 1: 长调试会话

**问题**: 调试过程中发现多个临时线索，容易忘记

**解决方案**:
```
尝试方法 A 失败 → /note session 方法 A 失败，报错 ECONNREFUSED
尝试方法 B 成功 → /note session Docker exec 绕过了网络路由问题
准备 compact → /note show session → 归档笔记
```

### 场景 2: 跨会话项目开发

**问题**: 昨天的技术决策今天忘记了

**解决方案**:
```
会话 1: /note workspace 使用 JWT 而非 session cookie，理由：支持跨域
会话 2: /note show workspace → 查看昨天的决策
会话 3: /note workspace token 有效期设为 7 天，刷新窗口 24 小时
```

### 场景 3: 通用经验积累

**问题**: 解决了一个问题，下次遇到又忘了

**解决方案**:
```
解决 PowerShell 问题 → /note global PowerShell 2>&1 会导致 $? 误判，改用 try-catch
下次在其他项目遇到 → /note show global → 快速定位解决方案
定期整理 → 将 global-inbox.md 中的条目迁移到 memory/lessons-learned.md
```

---

## 注意事项

### 1. 隐私与安全

- ⚠️ 不要在笔记中记录敏感信息（密码、API key、个人数据）
- ⚠️ `.claude/scratch/` 应添加到 `.gitignore`
- ⚠️ global 笔记跨项目可见，避免记录项目专属信息

### 2. 整理策略

- **session**: 自动归档，定期清理 archive（建议保留 30 天）
- **workspace**: 任务完成后整理到 memory/*.md
- **global**: 每月整理一次，提取到 best-practices.md

### 3. 与结构化记忆的关系

```
临时笔记（session-notes）→ 任务复盘（reflection）→ 结构化记忆（memory/*.md）
     ↓ 轻量、易失               ↓ 提炼、验证           ↓ 持久、溯源
```

session-notes 是"记录缓冲区"，不是最终存储。

---

## 实现细节

### 文件权限

- session/workspace 笔记：项目内可见
- global 笔记：所有项目可见
- archive：只读，用于审计

### 并发安全

- 使用追加模式（`a`）避免覆盖
- 文件锁（如果多个 Agent 并发写入）

### 性能考虑

- 笔记文件通常 <10KB，读取无性能问题
- archive 目录定期清理，避免堆积

---

## 相关文档

- `specs/SPEC-deepseek-inspired-enhancements.md` - 完整技术规格
- `docs/CONTEXT-ENGINEERING-GUIDE.md` - 上下文工程指南
- `.claude/skills/handoff/SKILL.md` - 交接 Skill
- `.claude/skills/reflection/SKILL.md` - 复盘 Skill

---

## 版本历史

- **v1.0.0** (2025-01-XX): 初始版本，实现三级作用域笔记系统

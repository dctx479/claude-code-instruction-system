# SPEC: DeepSeek 启发的上下文管理增强

**状态**: DRAFT  
**风险**: MEDIUM  
**作者**: Claude (Sonnet 4)  
**日期**: 2025-01-XX  
**参考**: analysis/deepseek-notes-analysis.md

---

## 1. 目标与动机

### 1.1 核心目标

基于 DeepSeek 笔记生态的设计理念，增强太一元系统的上下文管理能力，填补两个关键盲区：
1. **会话内临时标注缺失** - 对话中的临时想法无处记录
2. **对话→知识转换摩擦过大** - 从对话到记忆需要完整复盘

### 1.2 设计原则

- ✅ **向后兼容**: 现有 Agent/Skill 无需修改即可使用
- ✅ **渐进增强**: 新功能是可选的，不破坏现有工作流
- ✅ **轻量实现**: 优先使用文件系统，避免引入新依赖
- ✅ **证据溯源**: 保持太一的结构化验证机制

---

## 2. 功能规格

### 2.1 分层临时笔记系统

#### 2.1.1 目录结构

```
.claude/scratch/              # 临时笔记根目录
  session-{session-id}.md     # 会话级笔记（/compact 后清空）
  workspace-notes.md          # 工作区级笔记（跨会话持久）

~/.claude/scratch/            # 全局临时笔记
  global-inbox.md             # 全局收件箱（跨项目）
```

#### 2.1.2 命令接口

新增 Skill: `.claude/skills/session-notes/`

```bash
/note session <内容>      # 追加到会话级笔记
/note workspace <内容>    # 追加到工作区级笔记
/note global <内容>       # 追加到全局笔记
/note show [scope]        # 显示指定作用域的笔记
/note clear [scope]       # 清空指定作用域（需确认）
```

#### 2.1.3 文件格式

```markdown
# Session Notes - {session-id}

## {timestamp} - {tag}
{content}

## {timestamp} - {tag}
{content}
```

标签类型: `idea`, `todo`, `assumption`, `question`, `insight`

#### 2.1.4 生命周期管理

- **session**: 检测到 `/compact` 或会话结束时，自动归档到 `.claude/scratch/archive/session-{id}-{timestamp}.md`
- **workspace**: 手动清理或项目归档时清空
- **global**: 用户手动整理

### 2.2 对话标注系统

#### 2.2.1 存储格式

`.claude/context/annotations.jsonl` (流式追加)

```jsonl
{"turn": 15, "role": "assistant", "text": "Docker exec 绕过网络路由", "tag": "key-insight", "timestamp": "2025-01-XX T10:30:00Z", "session_id": "abc123"}
{"turn": 23, "role": "user", "text": "需要验证 token 刷新逻辑", "tag": "todo", "timestamp": "2025-01-XX T10:45:00Z", "session_id": "abc123"}
```

#### 2.2.2 触发机制

**方式 1: 显式标注**
```
用户输入: !mark <tag> [<text>]
系统行为: 记录上一条助手回复（或指定文本）到 annotations.jsonl
```

**方式 2: 自动检测** (可选，默认关闭)
```
检测关键词: "记住"、"待办"、"假设"、"问题"
自动标记: 追加到 annotations.jsonl，用户可审查
```

#### 2.2.3 标签类型

| 标签 | 含义 | 用途 |
|------|------|------|
| `key-insight` | 关键洞察 | 复盘时优先提取 |
| `todo` | 待办事项 | 生成任务清单 |
| `assumption` | 待验证假设 | 实验设计参考 |
| `question` | 未解决问题 | 后续调查线索 |
| `decision` | 重要决策 | ADR 生成素材 |
| `anti-pattern` | 错误尝试 | 经验教训记录 |

#### 2.2.4 集成点

- **`/reflection` Skill**: 优先读取已标注内容，降低复盘负担
- **`context-archivist` Agent**: 生成 resolution 时引用标注
- **`/handoff` Skill**: 交接文档自动包含标注摘要

### 2.3 检查点交互式审查

#### 2.3.1 新增命令

扩展 `scripts/checkpoint.py`:

```bash
python scripts/checkpoint.py review [--checkpoint <id>]
```

#### 2.3.2 输出格式

```
Checkpoint Review: checkpoint-20250120-103045

Files Status:
  ✅ src/app.ts (验证通过, hash 匹配)
  ✅ src/utils.ts (验证通过, hash 匹配)
  ⚠️  src/db.ts (文件缺失)
  ⛔ tests/api.test.ts (hash 不匹配, 已修改)
  🆕 src/new-feature.ts (新文件, 未在检查点中)

Summary:
  Total: 5 files
  Verified: 2
  Missing: 1
  Modified: 1
  New: 1

Actions:
  - Review modified files before continuing
  - Consider updating checkpoint if changes are intentional
```

#### 2.3.3 Diff 功能

```bash
python scripts/checkpoint.py diff <checkpoint1> <checkpoint2>
```

显示两个检查点之间的差异。

### 2.4 增量摘要流

#### 2.4.1 触发策略

在 `context-archivist` Agent 中新增 `--stream` 模式：

- **触发频率**: 每 10 轮对话
- **输出位置**: `.claude/context/session-summary.md`
- **内容结构**:

```markdown
# Session Summary - {session-id}

## Checkpoint 1 (Turns 1-10)
**Key Decisions**: ...
**Verified Facts**: ...
**Open Questions**: ...

## Checkpoint 2 (Turns 11-20)
**Key Decisions**: ...
**Verified Facts**: ...
**Open Questions**: ...
```

#### 2.4.2 `/compact` 集成

在 `/compact` 触发前：
1. 生成最终增量摘要
2. 合并所有 checkpoint 到 session-summary.md
3. `/compact` 指令中引用 session-summary.md
4. 压缩后保留 session-summary.md

---

## 3. 实施计划

### 3.1 Phase 1: 核心基础设施 (Day 1-3)

#### Task 1.1: 分层笔记系统
- [ ] 创建 `.claude/skills/session-notes/` Skill
- [ ] 实现 `/note` 命令族
- [ ] 实现三级作用域文件管理
- [ ] 添加自动归档逻辑

**交付物**: 
- `.claude/skills/session-notes/SKILL.md`
- `scripts/note-manager.py` (可选，处理归档)

**验收**:
- [ ] 三级作用域文件正确创建
- [ ] session 笔记在 `/compact` 后自动归档
- [ ] global 笔记跨项目可见

#### Task 1.2: 对话标注存储
- [ ] 创建 `.claude/context/annotations.jsonl` schema
- [ ] 实现 `!mark` 命令解析逻辑
- [ ] 实现标注追加功能

**交付物**:
- `scripts/annotation-manager.py`
- `.claude/context/annotations-schema.json`

**验收**:
- [ ] 标注持久化到 JSONL
- [ ] 支持 6 种标签类型
- [ ] 时间戳和 session_id 正确记录

#### Task 1.3: 检查点审查界面
- [ ] 扩展 `checkpoint.py` 添加 `review` 子命令
- [ ] 实现四状态检测逻辑
- [ ] 实现 `diff` 子命令

**交付物**:
- 更新后的 `scripts/checkpoint.py`

**验收**:
- [ ] 四种状态正确识别（✅⚠️⛔🆕）
- [ ] diff 输出清晰可读

### 3.2 Phase 2: 集成与增强 (Day 4-7)

#### Task 2.1: `/reflection` 集成标注
- [ ] 更新 `.claude/skills/reflection/SKILL.md`
- [ ] 添加"优先读取标注"逻辑
- [ ] 生成标注摘要

**交付物**:
- 更新后的 `reflection/SKILL.md`

**验收**:
- [ ] `/reflection` 输出中引用标注
- [ ] 标注按标签分类显示

#### Task 2.2: `context-archivist` 增量摘要
- [ ] 更新 `agents/ops/context-archivist.md`
- [ ] 实现 `--stream` 模式
- [ ] 实现 10 轮触发逻辑

**交付物**:
- 更新后的 `context-archivist.md`
- `scripts/incremental-summary.py` (可选)

**验收**:
- [ ] 摘要每 10 轮自动生成
- [ ] 摘要包含：关键决策、验证结果、待办事项
- [ ] `/compact` 正确引用摘要

#### Task 2.3: `/handoff` 集成
- [ ] 更新 `.claude/skills/handoff/SKILL.md`
- [ ] 添加标注摘要到交接文档
- [ ] 添加临时笔记检查

**交付物**:
- 更新后的 `handoff/SKILL.md`

**验收**:
- [ ] 交接文档包含标注摘要
- [ ] 提示未清理的临时笔记

### 3.3 Phase 3: 文档与测试 (Day 8-10)

#### Task 3.1: 文档更新
- [ ] 更新 `docs/CONTEXT-ENGINEERING-GUIDE.md`
- [ ] 新增 `docs/SESSION-NOTES-GUIDE.md`
- [ ] 更新 `docs/MEMORY-SYSTEM.md` 架构图
- [ ] 新增 `memory/best-practices.md` BP-058

**交付物**:
- 4 个更新后的文档

#### Task 3.2: 测试与验证
- [ ] 创建 `tests/test_session_notes.py`
- [ ] 创建 `tests/test_annotations.py`
- [ ] 创建 `tests/test_checkpoint_review.py`
- [ ] 在真实项目中集成测试

**交付物**:
- 3 个测试文件
- 集成测试报告

#### Task 3.3: 兼容性验证
- [ ] 验证所有现有 Agent 仍正常工作
- [ ] 验证所有现有 Skill 仍正常工作
- [ ] 验证 Hook 系统无冲突

**交付物**:
- 兼容性测试报告

---

## 4. 技术细节

### 4.1 Session ID 生成

使用 git commit hash 前 7 位 + 时间戳：
```python
import subprocess
from datetime import datetime

def get_session_id():
    try:
        commit = subprocess.check_output(['git', 'rev-parse', '--short=7', 'HEAD']).decode().strip()
    except:
        commit = 'unknown'
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    return f"{commit}-{timestamp}"
```

### 4.2 标注解析逻辑

```python
import re
from datetime import datetime

def parse_mark_command(user_input, previous_assistant_message):
    """
    解析 !mark 命令
    
    格式:
      !mark <tag>              # 标记上一条助手回复
      !mark <tag> <text>       # 标记指定文本
    """
    pattern = r'^!mark\s+(\w+)(?:\s+(.+))?$'
    match = re.match(pattern, user_input.strip())
    
    if not match:
        return None
    
    tag = match.group(1)
    text = match.group(2) if match.group(2) else previous_assistant_message
    
    return {
        "tag": tag,
        "text": text,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "role": "assistant" if not match.group(2) else "user"
    }
```

### 4.3 临时笔记归档策略

```python
import shutil
from pathlib import Path

def archive_session_notes(session_id, project_root):
    """
    归档会话级笔记
    """
    scratch_dir = Path(project_root) / '.claude' / 'scratch'
    archive_dir = scratch_dir / 'archive'
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    session_file = scratch_dir / f'session-{session_id}.md'
    if session_file.exists():
        archive_file = archive_dir / f'session-{session_id}-{datetime.now().strftime("%Y%m%d-%H%M%S")}.md'
        shutil.move(str(session_file), str(archive_file))
        return archive_file
    return None
```

### 4.4 增量摘要生成提示

```python
INCREMENTAL_SUMMARY_PROMPT = """
请生成本轮对话（Turn {start}-{end}）的增量摘要。

格式:
## Checkpoint {checkpoint_num} (Turns {start}-{end})

**Key Decisions**: 
- [决策 1]
- [决策 2]

**Verified Facts**:
- [事实 1]
- [事实 2]

**Open Questions**:
- [问题 1]
- [问题 2]

**Annotations**: {annotation_count} 条标注
- key-insight: {insight_count}
- todo: {todo_count}
- assumption: {assumption_count}

要求:
1. 只提取已验证的事实，不猜测
2. 决策需说明理由
3. 问题需说明为何未解决
4. 简洁，每项 1-2 句
"""
```

---

## 5. 兼容性保证

### 5.1 现有功能零影响

- ✅ 所有新文件在 `.claude/scratch/` 和 `.claude/context/`，不影响现有路径
- ✅ 所有新命令以 `/note` 和 `!mark` 为前缀，不与现有命令冲突
- ✅ `checkpoint.py` 新增子命令，原有 `save`/`show` 保持不变
- ✅ `context-archivist` 增量模式是可选的，不影响原有行为

### 5.2 Agent 透明使用

任何 Agent 都可以：
1. 读取 `.claude/scratch/` 下的临时笔记
2. 读取 `.claude/context/annotations.jsonl` 中的标注
3. 调用 `checkpoint.py review` 检查状态
4. 触发增量摘要生成

无需修改 Agent 定义文件。

### 5.3 Skill 自动集成

通过在 Skill frontmatter 中声明：

```yaml
integration:
  - session-notes      # 自动加载临时笔记
  - annotations        # 自动加载标注
  - incremental-summary # 自动生成摘要
```

---

## 6. 成功指标

### 6.1 功能指标

- [ ] 所有命令正常工作（`/note`, `!mark`, `checkpoint.py review`）
- [ ] 三级作用域隔离正确
- [ ] 标注持久化成功率 100%
- [ ] 增量摘要生成成功

### 6.2 质量指标

- [ ] 所有现有测试通过
- [ ] 新增测试覆盖率 >80%
- [ ] 兼容性测试 100% 通过
- [ ] 文档完整性检查通过

### 6.3 用户体验指标

- [ ] `/reflection` 耗时减少 >40%（通过标注定位）
- [ ] 信息丢失率降低 >50%（人工评测）
- [ ] compact 后关键信息保留率 >95%

---

## 7. 风险与缓解

### 7.1 风险矩阵

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| Session ID 冲突 | 中 | 低 | 使用 git hash + 时间戳组合 |
| 标注文件损坏 | 高 | 低 | JSONL 格式，单行损坏不影响其他 |
| 临时笔记泄露敏感信息 | 高 | 中 | 添加 `.gitignore` 规则，文档说明 |
| 增量摘要 token 消耗过高 | 中 | 中 | 可配置触发频率，默认每 10 轮 |
| 与现有 Agent 冲突 | 高 | 低 | 完整兼容性测试 |

### 7.2 回滚计划

如果出现严重问题：
1. 删除 `.claude/scratch/` 和 `.claude/context/annotations.jsonl`
2. 还原 `checkpoint.py` 到原版本
3. 还原 Agent/Skill 定义文件
4. 系统恢复到增强前状态

---

## 8. 后续迭代

### 8.1 Phase 4 候选 (未来 3 个月)

- [ ] 语义检索系统（FTS5 索引）
- [ ] 自动关键词检测标注
- [ ] 标注可视化界面
- [ ] 跨会话标注关联

### 8.2 Phase 5 候选 (未来 6 个月)

- [ ] 机器学习驱动的摘要质量评估
- [ ] 多模态标注（代码片段、图片）
- [ ] 团队协作标注共享

---

## 9. 参考文档

- `analysis/deepseek-notes-analysis.md` - 原始分析报告
- `docs/CONTEXT-ENGINEERING-GUIDE.md` - 上下文工程指南
- `docs/MEMORY-SYSTEM.md` - 记忆系统架构
- `.claude/skills/handoff/SKILL.md` - 交接 Skill
- `agents/ops/context-archivist.md` - 上下文归档 Agent

---

**下一步**: 开始 Phase 1 实施

<!-- Resource paths below are relative to the parent skill directory. -->

### 2. 日志类型定义

| 类型 | 用途 | 输出格式 |
|------|------|----------|
| `TaskStart` | 任务开始 | Context + Goals |
| `InnerThought` | 内心思考 | 自由文本推理 |
| `DecisionPoint` | 决策记录 | Options + Chosen + Reason + Tradeoffs |
| `Discovery` | 意外发现 | Finding + Implications |
| `Error` | 错误记录 | Error + Analysis + Recovery |
| `Recovery` | 恢复策略 | Strategy + Result |
| `Uncertainty` | 不确定性 | Question + Confidence + Mitigation |
| `Progress` | 进度更新 | Checklist + Next |
| `TaskComplete` | 任务完成 | Summary + Learnings |

### 3. 日志格式模板

#### TaskStart 模板
```markdown
## [timestamp] Task: {task_name}

### Context
- Request: {用户请求原文}
- Environment: {技术栈/环境信息}
- Constraints: {约束条件}
- Plan ID: {关联的计划 ID，如有}

### Goals
1. {目标 1}
2. {目标 2}

### Initial Assessment
{对任务的初步分析}
```

#### DecisionPoint 模板
```markdown
### Decision Point: {decision_title}

**Question**: {需要决策的问题}

**Considering**:
- [Option A] {选项名}
  - Pro: {优点}
  - Con: {缺点}
- [Option B] {选项名}
  - Pro: {优点}
  - Con: {缺点}

**Chosen**: {选择的选项}
**Reason**: {选择理由}
**Tradeoffs**: {权衡取舍}
**Confidence**: {置信度 0-100%}
```

#### Error 模板
```markdown
### Error Encountered

**Error**: {错误描述}
**Stack/Context**:
```
{错误详情}
```

**Analysis**:
- 可能原因 1: {原因}
- 可能原因 2: {原因}

**Recovery Strategy**: {恢复策略}
**Result**: {恢复结果}
```

#### Uncertainty 模板
```markdown
### Uncertainty Note

**What I'm unsure about**: {不确定的内容}
**Current assumption**: {当前假设}
**Confidence level**: {置信度}
**Mitigation**: {缓解措施}
**Needs clarification from user**: {是否需要用户确认} [Yes/No]
```

#### TaskComplete 模板
```markdown
## [timestamp] Task Complete: {task_name}

### Summary
{完成情况总结}

### Key Decisions Made
1. {决策 1}: {理由}
2. {决策 2}: {理由}

### Learnings
- {经验 1}
- {经验 2}

### Open Questions
- {遗留问题}

### Time Spent
- Elapsed: {耗时}
- Token used: {约估}
```

## 与太一系统集成

### 与 Context Archival 协同

```
Observability (实时)              Context Archival (归档)
     │                                    │
     ├─ logs/ai-thoughts.md               ├─ .claude/context/index.json
     │  (流水日志，轻量)                   │  (结构化索引)
     │                                    │
     ├─ 所有决策和思考过程                 ├─ 仅成功方案
     │                                    │
     └─────────┬─────────────────────────→│
               │                          └─ .claude/context/resolutions/
               │   任务完成时同步               (问题解决方案)
               │   提取关键 resolutions
               │
    触发: /save-context 或 PreCompact Hook
```

**分工**:
- **Observability**: 实时记录所有推理过程，包括失败尝试
- **Context Archival**: 提炼成功方案，结构化沉淀

**同步时机**:
- 任务完成时，从 ai-thoughts.md 提取关键决策
- PreCompact Hook 触发时
- 用户执行 `/save-context` 时

### 与 Ralph Loop 集成

Ralph 循环执行时自动激活 observability：

```markdown
## [timestamp] Ralph Loop: {task_description}

### Iteration 1
[TaskStart 记录]

### Iteration 2
[Progress 更新]
[DecisionPoint 记录]

### Iteration 3
[Error 记录]
[Recovery 策略]

...

### Loop Complete
[TaskComplete 记录]
[统计: 迭代次数、耗时、关键决策数]
```

状态同步到 `memory/ralph-state.json`:
```json
{
  "observability": {
    "thought_log": "logs/ai-thoughts.md",
    "decisions_made": 5,
    "errors_encountered": 2,
    "recoveries": 2
  }
}
```

### 与 Autopilot 集成

Autopilot 各阶段自动记录：

```
Phase 1: Planning
├─ [TaskStart] 任务分解
├─ [DecisionPoint] 策略选择
└─ [Progress] 计划确认

Phase 2: Specification
├─ [InnerThought] 分析需求
├─ [DecisionPoint] 架构决策
└─ [Uncertainty] 需求不明确点

Phase 3: Development
├─ [Ralph Loop 日志]
├─ [Error + Recovery] 如遇错误
└─ [Progress] 检查点

Phase 4: QA
├─ [Discovery] 发现问题
├─ [DecisionPoint] 修复策略
└─ [Progress] 修复状态

Phase 5: Delivery
├─ [TaskComplete] 总结
└─ [Learnings] 经验沉淀
```

### 与 Plan-Scoped Memory 集成

每个计划维护独立的思维日志：

```
.claude/context/plans/{plan_id}/
├─ thoughts.md          # 计划专属思维日志
├─ decisions.json       # 决策索引
└─ ...
```

全局日志保留所有记录，计划日志仅包含该计划相关内容。

## 日志文件管理

### 文件结构

```
logs/
├─ ai-thoughts.md           # 当前思维日志（最近 7 天）
├─ ai-thoughts-archive/     # 归档目录
│   ├─ 2026-01/
│   │   ├─ week-01.md
│   │   ├─ week-02.md
│   │   └─ ...
│   └─ 2026-02/
│       └─ ...
└─ .thoughts-config.json    # 配置文件
```

### 轮转策略

```json
// logs/.thoughts-config.json
{
  "rotation": {
    "strategy": "size+time",
    "max_size_mb": 5,
    "max_age_days": 7,
    "archive_format": "monthly/weekly"
  },
  "retention": {
    "active_days": 7,
    "archive_months": 3,
    "compress_after_days": 30
  },
  "filters": {
    "exclude_types": [],
    "min_confidence_log": 0
  }
}
```

### 自动轮转

当满足以下条件时触发轮转：
1. 文件大小超过 5MB
2. 时间超过 7 天
3. 每周日自动归档

轮转脚本: `scripts/rotate-thought-logs.sh`

```bash
#!/bin/bash
# 思维日志轮转脚本

LOG_DIR="logs"
ARCHIVE_DIR="logs/ai-thoughts-archive"
MAX_SIZE_MB=5
MAX_AGE_DAYS=7

# 检查文件大小
size_mb=$(du -m "$LOG_DIR/ai-thoughts.md" | cut -f1)

# 检查文件年龄
age_days=$(( ($(date +%s) - $(stat -c %Y "$LOG_DIR/ai-thoughts.md")) / 86400 ))

if [ "$size_mb" -ge "$MAX_SIZE_MB" ] || [ "$age_days" -ge "$MAX_AGE_DAYS" ]; then
    year=$(date +%Y)
    month=$(date +%m)
    week=$(date +%W)

    mkdir -p "$ARCHIVE_DIR/$year-$month"
    mv "$LOG_DIR/ai-thoughts.md" "$ARCHIVE_DIR/$year-$month/week-$week.md"
    touch "$LOG_DIR/ai-thoughts.md"

    echo "# AI Thoughts Log" > "$LOG_DIR/ai-thoughts.md"
    echo "Created: $(date -Iseconds)" >> "$LOG_DIR/ai-thoughts.md"
    echo "" >> "$LOG_DIR/ai-thoughts.md"
fi
```

## 使用指南

### 手动触发记录

```bash
# 记录决策点
/observe decision "选择数据库方案"

# 记录不确定性
/observe uncertainty "不确定性能影响"

# 记录发现
/observe discovery "发现循环依赖"

# 查看当前思维日志
/observe show

# 搜索历史决策
/observe search "JWT"
```

### 配置选项

在 `config/observability.json` 中配置：

```json
{
  "enabled": true,
  "log_path": "logs/ai-thoughts.md",
  "auto_trigger": {
    "on_task_start": true,
    "on_decision": true,
    "on_error": true,
    "on_task_complete": true
  },
  "verbosity": "normal",  // "minimal" | "normal" | "verbose"
  "sync_to_context": true,
  "confidence_threshold": 50,  // 低于此置信度时自动记录 Uncertainty
  "include_in_ralph": true,
  "include_in_autopilot": true
}
```

### 查询历史

```bash
# 按时间范围查询
/observe history --from 2026-02-01 --to 2026-02-04

# 按类型查询
/observe history --type DecisionPoint

# 按关键词查询
/observe search "认证"

# 生成决策报告
/observe report --format markdown > decisions-report.md
```

## 最佳实践

### 1. 透明性原则

**DO**:
- 记录真实的不确定性和疑虑
- 说明选择某方案的具体理由
- 记录失败尝试和教训

**DON'T**:
- 隐藏不确定性
- 只记录成功结果
- 过度美化决策过程

### 2. 实用性原则

**DO**:
- 使用结构化格式便于检索
- 保持简洁，突出关键信息
- 关联相关文件和代码位置

**DON'T**:
- 记录过多琐碎细节
- 重复记录相同信息
- 使用模糊的描述

### 3. 诚实性原则

**DO**:
- 表达真实的置信度
- 承认知识盲区
- 标注需要人工确认的点

**DON'T**:
- 假装确定实际不确定的事
- 隐瞒错误或失败
- 过度自信

### 4. 何时详细记录

| 场景 | 详细程度 | 理由 |
|------|----------|------|
| 关键架构决策 | 高 | 需要审计追溯 |
| 简单 bug 修复 | 低 | 通常不需回顾 |
| 涉及安全的变更 | 高 | 合规需求 |
| 实验性探索 | 中 | 记录尝试路径 |
| 常规开发任务 | 低 | 避免信息过载 |

## 与 memory/lessons-learned.md 的关系

| Observability | lessons-learned.md |
|---------------|-------------------|
| 实时记录 | 事后总结 |
| 所有思考过程 | 仅重要经验 |
| 包含失败尝试 | 仅成功方案 |
| 流水式日志 | 结构化条目 |
| 7 天轮转 | 永久保留 |

**同步流程**:
1. 任务完成时，从 ai-thoughts.md 提取关键决策
2. 符合"经验教训"标准的内容同步到 lessons-learned.md
3. 使用标准格式: `## [日期] 经验条目 #ID`

## 参考资源

- **Aha-Loop**: 可观测性灵感来源
- **Context Archivist Agent**: `agents/ops/context-archivist.md`
- **Ralph Loop**: `commands/general/ralph.md`
- **Autopilot**: `commands/general/autopilot.md`
- **Plan-Scoped Memory**: `workflows/research/plan-scoped-memory.md`

---

**注意**:
- 日志文件位于 `logs/ai-thoughts.md`
- 首次使用前需创建 logs 目录: `mkdir -p logs`
- 配置文件: `config/observability.json`

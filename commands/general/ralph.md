# /ralph - 自主循环执行命令

> **Ralph Loop**: 让 Claude 自主执行任务直到完成，无需持续人工干预

## 概述

`/ralph` 命令启动自主循环执行模式，Claude 会自动继续执行任务直到:
1. 任务完成
2. 遇到需要人工确认的决策
3. 达到最大迭代次数
4. 遇到致命错误

## 命名由来

"Ralph" 取自 **R**un **A**utonomously **L**oop **P**ersistently **H**ook 的首字母缩写，
也是对自主执行能力的友好称呼。

## 用法

### 基本用法

```bash
# 启动 Ralph 循环执行
/ralph <任务描述>

# 示例
/ralph "完成用户认证模块的所有待办事项"
/ralph "修复所有 lint 错误并提交代码"
/ralph "将项目迁移到 TypeScript"
```

### 高级选项

```bash
# 设置最大迭代次数
/ralph --max-iterations 20 <任务描述>

# 设置检查点（每N次迭代保存进度）
/ralph --checkpoint-interval 3 <任务描述>

# 安静模式（减少输出）
/ralph --quiet <任务描述>

# 强制重新开始（忽略之前的状态）
/ralph --restart <任务描述>
```

### 控制命令

```bash
# 查看当前状态
/ralph status

# 暂停执行
/ralph pause

# 恢复执行
/ralph resume

# 停止执行
/ralph stop

# 查看执行历史
/ralph history
```

## 工作原理

### 一轮 (Iteration) 的定义

**一轮 = 一个完整的工作周期**，包含以下阶段（不论执行了多少次 tool call）：

```
┌─────────────────────────────────────────┐
│           一轮 (One Iteration)           │
│                                         │
│  1. 状态评估  ── 全面了解当前进展        │
│  2. 计划制定  ── 规划本轮要完成的工作    │
│  3. 执行操作  ── 完成多个相关操作步骤    │
│  4. 结果验证  ── 确认本轮成果达标        │
│  5. 标记完成  ── round_complete = true   │
└─────────────────────────────────────────┘
```

> ⚠️ 单次文件读写、单条命令执行**不算**一轮。一轮是有意义的工作闭环。

### Claude 端每轮操作规范

**启动 `/ralph` 时（第 0 轮初始化）**，Claude 必须立即写入状态文件：

```json
{
  "active": true,
  "status": "RUNNING",
  "iteration": 0,
  "max_iterations": 10,
  "round_complete": false,
  "completed": false,
  "fatal_error": false,
  "needs_confirmation": false,
  "current_task": "唯一任务ID（kebab-case）",
  "task_description": "用户原始任务描述",
  "started_at": "2026-01-23T10:00:00Z",
  "last_updated": "2026-01-23T10:00:00Z",
  "paused_at": null,
  "paused_reason": null,
  "max_iterations_reached": false,
  "checkpoints": [],
  "errors": [],
  "metrics": { "total_runs": 1, "successful_runs": 0, "failed_runs": 0, "total_iterations": 0 }
}
```

**每轮结束时**，Claude 必须更新以下字段之一：

| 情形 | 写入字段 |
|------|----------|
| 本轮完成，任务未结束 | `round_complete: true` |
| 整个任务全部完成 | `completed: true` + `round_complete: true` |
| 遇到不可恢复错误 | `fatal_error: true` + `errors` 数组追加描述 |
| 需要人工确认 | `needs_confirmation: true` + `paused_reason: "说明"` |

> 🚨 **不得**在轮次中途（尚未完成计划步骤时）将 `round_complete` 设为 `true`。

```
用户: /ralph "完成待办事项"
        │
        ▼
┌─────────────────────────┐
│   初始化 Ralph State    │
│   - 设置任务描述        │
│   - 重置迭代计数        │
│   - 激活循环模式        │
└─────────────┬───────────┘
              │
              ▼
┌─────────────────────────┐
│     执行任务迭代        │◄────────────┐
│   - 分析当前状态        │             │
│   - 执行下一步操作      │             │
│   - 更新进度            │             │
└─────────────┬───────────┘             │
              │                         │
              ▼                         │
        ┌───────────┐                   │
        │ 任务完成? │                   │
        └─────┬─────┘                   │
              │                         │
         NO   │   YES                   │
              │                         │
    ┌─────────┴─────────┐               │
    │                   │               │
    ▼                   ▼               │
┌────────┐        ┌──────────┐          │
│ 需确认?│        │  完成!   │          │
└────┬───┘        └──────────┘          │
     │                                  │
 NO  │  YES                             │
     │                                  │
     │   ┌─────────────┐                │
     │   │ 请求人工确认 │                │
     │   └─────────────┘                │
     │                                  │
     └──────────────────────────────────┘
              │
              ▼
        ┌───────────┐
        │ Stop Hook │
        │ 拦截检查   │
        └─────┬─────┘
              │
              ▼
        ┌───────────┐
        │ 继续/停止 │
        └───────────┘
```

## 状态文件

Ralph 使用两层状态文件，HUD 按对应层级读取：

| 层级 | 路径 | 读取方 | 说明 |
|------|------|--------|------|
| **项目级** | `memory/ralph-state.json` | 项目 `hud.sh` | 项目内 ralph 执行状态 |
| **全局级** | `~/.claude/memory/ralph-state.json` | 全局 `hud.sh` | 跨项目 ralph 执行状态 |

Ralph 写入哪个路径取决于调用上下文：在项目内调用写项目路径，全局模式写全局路径。

```json
{
  "active": true,
  "status": "RUNNING",
  "iteration": 3,
  "max_iterations": 10,
  "round_complete": false,
  "completed": false,
  "fatal_error": false,
  "needs_confirmation": false,
  "current_task": "user-auth-todos",
  "task_description": "完成用户认证模块的所有待办事项",
  "started_at": "2026-01-23T10:00:00Z",
  "last_updated": "2026-01-23T10:15:00Z",
  "paused_at": null,
  "paused_reason": null,
  "max_iterations_reached": false,
  "checkpoints": [
    {
      "iteration": 1,
      "timestamp": "2026-01-23T10:05:00Z",
      "summary": "完成了登录功能"
    }
  ],
  "errors": [],
  "metrics": {
    "total_runs": 5,
    "successful_runs": 4,
    "failed_runs": 1,
    "total_iterations": 23
  }
}
```

### 状态字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `active` | bool | Ralph 是否正在运行 |
| `status` | string | INACTIVE / RUNNING / PAUSED / COMPLETED / FAILED |
| `iteration` | int | 当前已完成的轮次数（由 Stop Hook 递增） |
| `max_iterations` | int | 最大允许轮次数 |
| `round_complete` | bool | **Claude 写入**：本轮工作是否全部完成 |
| `completed` | bool | **Claude 写入**：整个任务是否完成 |
| `fatal_error` | bool | **Claude 写入**：是否遇到不可恢复错误 |
| `needs_confirmation` | bool | **Claude 写入**：是否需要人工确认 |
| `paused_reason` | string | 暂停原因说明 |
| `last_updated` | ISO8601 | Stop Hook 自动更新 |
| `metrics.total_iterations` | int | Stop Hook 每次递增迭代时累计 |

## 安全机制

### 1. 迭代限制
默认最多执行 10 次迭代，防止无限循环。

### 2. 致命错误检测
遇到以下情况会自动停止:
- 编译错误
- 运行时崩溃
- 安全警告
- 资源耗尽

### 3. 确认请求
以下操作需要人工确认:
- 删除文件或数据
- 修改生产配置
- 引入新依赖
- 数据库 Schema 变更

### 4. 检查点恢复
定期保存进度，允许从中断处恢复。

## 示例场景

### 场景 1: 代码迁移

```bash
/ralph "将所有 .js 文件迁移到 TypeScript"

# Ralph 会自动:
# 1. 扫描所有 .js 文件
# 2. 逐个转换为 .ts
# 3. 修复类型错误
# 4. 运行测试验证
# 5. 循环直到全部完成
```

### 场景 2: Bug 修复

```bash
/ralph "修复所有 GitHub issues 中标记为 bug 的问题"

# Ralph 会自动:
# 1. 获取 bug 列表
# 2. 分析每个 bug
# 3. 实现修复
# 4. 编写测试
# 5. 提交代码
# 6. 循环直到全部修复
```

### 场景 3: 测试覆盖

```bash
/ralph "为所有未覆盖的函数编写单元测试"

# Ralph 会自动:
# 1. 运行覆盖率分析
# 2. 识别未覆盖函数
# 3. 生成测试用例
# 4. 运行测试
# 5. 循环直到覆盖率达标
```

## 与其他功能集成

### 与 HUD 集成
Ralph 执行状态会显示在 HUD 状态栏中。

### 与 Intent Detector 集成
Ralph 使用意图检测来理解任务完成条件。

### 与 Plan-Scoped Memory 集成
Ralph 的每次执行会创建独立的计划记忆空间。

### 与持久化规划文件集成（批量任务模式）

**问题**: 批量处理 >50 个同质任务（如逐个分析 127 只股票）时，AI 上下文压缩导致后期任务质量下降——跳过分析阶段、格式漂移、遗忘约束条件。

**方案**: 用 3 个持久化 markdown 文件作为 Ralph 循环的"外部记忆"：

```
task_plan.md   ← 完整任务清单 + 约束条件（每轮开头重读）
findings.md    ← 累积发现（每完成一项追加）
progress.md    ← 当前进度（每轮更新）
```

**工作流**:

```bash
# Step 1: 创建规划文件
/ralph "创建 task_plan.md，列出所有待分析股票及分析标准"

# Step 2: 用规划文件驱动批量执行
/ralph "按 task_plan.md 逐个执行分析，每完成一项更新 progress.md 和 findings.md"
```

**Claude 每轮操作规范**:

```
轮次开始时:
  1. 读取 task_plan.md 的约束条件（防止漂移）
  2. 读取 progress.md 确定下一个待处理项
  3. 开始执行

轮次结束时:
  1. 将结果追加到 findings.md
  2. 在 progress.md 勾选已完成项
  3. 设置 round_complete: true
```

**与 `/issues-execute` 的选择**:

| 场景 | 推荐工具 |
|------|---------|
| 结构化任务，有明确 acceptance_criteria | `/plan-to-issues` + `/issues-execute` |
| 开放式批量分析（研究、调研、审查） | `/ralph` + 持久化规划文件 |
| 超大规模（>100项）结构化任务 | 先 task_plan.md 梳理 → 转 issues CSV |

详见: `docs/ORCHESTRATION-GUIDE.md` 示例4

## 最佳实践

1. **明确任务描述**: 越具体越好
2. **设置合理的迭代限制**: 复杂任务可增加
3. **使用检查点**: 长时间任务建议开启
4. **监控执行**: 通过 `/ralph status` 跟踪进度

## 故障排除

### Ralph 卡住
```bash
/ralph status  # 查看状态
/ralph stop    # 强制停止
```

### 意外停止
检查 `memory/ralph-state.json` 中的错误信息。

### 恢复执行
```bash
/ralph resume  # 从最后检查点恢复
```

## 相关文档

- `hooks/ralph-stop-interceptor.sh` - Stop Hook 实现
- `memory/ralph-state.json` - 状态文件
- `workflows/execution/ralph-manager.md` - 详细工作流

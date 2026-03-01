# Ralph Manager 工作流

> 自主循环执行系统的核心管理逻辑

## 概述

Ralph Manager 负责管理 Claude 的自主循环执行，确保任务能够持续执行直到完成，同时保持安全性和可控性。

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Ralph Manager                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Task Parser  │  │ State Engine │  │ Stop Handler │      │
│  │ 任务解析器   │  │ 状态引擎     │  │ 停止处理器   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           │                                 │
│                           ▼                                 │
│                  ┌─────────────────┐                        │
│                  │ Execution Loop  │                        │
│                  │ 执行循环        │                        │
│                  └─────────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. Task Parser (任务解析器)

解析用户输入的任务描述，提取:
- 任务目标
- 完成条件
- 约束条件
- 优先级

```markdown
输入: "完成用户认证模块的所有待办事项"

解析结果:
- 目标: 完成待办事项
- 范围: 用户认证模块
- 完成条件: 所有待办事项标记为完成
- 约束: 仅限用户认证模块
```

### 2. State Engine (状态引擎)

管理 Ralph 的执行状态:

```
状态转换图:

  INACTIVE ──start──► RUNNING
      ▲                  │
      │                  ├──complete──► COMPLETED
      │                  │
      │                  ├──error────► FAILED
      │                  │
      │                  ├──pause────► PAUSED
      │                  │
      └──stop/timeout────┘
```

状态定义:
- **INACTIVE**: 未激活，等待启动
- **RUNNING**: 正在执行任务
- **PAUSED**: 暂停，等待恢复或人工确认
- **COMPLETED**: 任务成功完成
- **FAILED**: 任务失败

### 3. Stop Handler (停止处理器)

处理停止事件，决定是否继续执行:

```bash
# 决策逻辑
if task_completed:
    allow_stop()
elif fatal_error:
    allow_stop()
elif max_iterations_reached:
    allow_stop()
elif needs_confirmation:
    pause_and_ask()
else:
    continue_execution()
```

### 4. Execution Loop (执行循环)

核心执行逻辑 — **一轮 (Iteration) = 一个完整工作周期**，包含评估→规划→执行→验证全过程：

```python
def execution_loop():
    while state.active and state.iteration < max_iterations:
        # ── 一轮开始 ──────────────────────────────────────────
        state.round_complete = False  # 标记轮次进行中
        save_state()

        # 1. 全面评估当前状态（非单步操作，而是整体进展）
        current_state = assess_full_state()

        # 2. 检查完成条件
        if is_task_completed(current_state):
            state.completed = True
            break

        # 3. 规划本轮完整工作计划（可包含多个步骤）
        work_plan = plan_iteration(current_state)

        # 4. 执行本轮所有步骤（多次 tool call 均属于同一轮）
        for step in work_plan.steps:
            if requires_confirmation(step):
                state.status = PAUSED
                yield step  # 请求人工确认，暂停当前轮
                continue

            result = execute_step(step)

            if result.is_fatal_error:
                state.fatal_error = True
                break
            elif result.is_error:
                handle_recoverable_error(result)

        # 5. 验证本轮成果
        verify_iteration_results()

        # 6. 本轮完成 — 递增计数并通知 Stop Hook
        state.iteration += 1
        state.round_complete = True  # ← Stop Hook 读取此标志才会递增计数
        save_checkpoint_if_needed()
        # ── 一轮结束 ──────────────────────────────────────────
```

**关键原则**：
- `round_complete = False` 期间，Stop Hook 只会"续跑"当前轮，**不**递增迭代计数
- `round_complete = True` 时，Stop Hook 递增计数并启动下一轮
- 一轮内执行多少 tool call、多少文件操作，都属于同一轮，不影响计数

## 完成条件检测

Ralph 使用多种策略检测任务是否完成:

### 1. 显式完成
```markdown
任务描述中包含明确的完成标志:
- "修复所有 lint 错误" → 检查 lint 输出为空
- "通过所有测试" → 检查测试结果为绿色
- "覆盖率达到 80%" → 检查覆盖率数值
```

### 2. 隐式完成
```markdown
通过上下文推断:
- 没有更多待办事项
- 没有更多错误
- 所有文件已处理
```

### 3. 用户确认
```markdown
需要用户确认的情况:
- 模糊的完成条件
- 主观判断的质量标准
- 业务逻辑验证
```

## 错误处理

### 可恢复错误
```markdown
- 网络超时 → 重试
- 并发冲突 → 回退重试
- 临时资源不可用 → 等待重试
```

### 致命错误
```markdown
- 编译错误且无法自动修复
- 安全漏洞检测到
- 数据损坏
- 用户明确要求停止
```

## 检查点机制

### 自动检查点
```json
{
  "checkpoint_id": "cp-001",
  "iteration": 5,
  "timestamp": "2026-01-23T10:30:00Z",
  "state_snapshot": {
    "completed_tasks": ["task-1", "task-2"],
    "pending_tasks": ["task-3", "task-4"],
    "current_file": "src/auth/login.ts"
  },
  "context_summary": "已完成登录和注册功能，正在处理密码重置"
}
```

### 恢复机制
```bash
/ralph resume --from-checkpoint cp-001
```

## 集成点

### 与 HUD 集成
```
HUD 状态栏显示:
[Ralph: 3/10] Running | Task: fix-lint-errors | ETA: 5m
```

### 与 Intent Detector 集成
```markdown
Intent Detector 帮助 Ralph:
1. 理解任务意图
2. 检测完成条件
3. 识别异常情况
```

### 与 Model Router 集成
```markdown
Model Router 为 Ralph 选择最优模型:
- 简单任务 → Haiku (快速)
- 复杂决策 → Sonnet (平衡)
- 关键决策 → Opus (高质量)
```

## 性能优化

### 1. 增量处理
不重新处理已完成的部分。

### 2. 并行执行
独立任务并行处理。

### 3. 智能跳过
跳过不需要处理的项目。

### 4. 缓存复用
复用已计算的结果。

## 监控与日志

### 日志级别
```
DEBUG: 详细执行步骤
INFO:  主要事件
WARN:  可恢复错误
ERROR: 致命错误
```

### 日志文件
```
~/.claude/ralph.log
memory/ralph-state.json
```

### 监控指标
```json
{
  "total_runs": 100,
  "successful_runs": 95,
  "failed_runs": 5,
  "average_iterations": 4.2,
  "average_duration": "8m30s"
}
```

## 安全考虑

### 1. 操作白名单
只允许安全的操作自动执行。

### 2. 敏感操作确认
删除、修改生产配置等需要确认。

### 3. 资源限制
限制最大迭代次数、执行时间。

### 4. 审计日志
记录所有操作以供审计。

## 相关文档

- `/ralph` 命令: `commands/general/ralph.md`
- Stop Hook: `hooks/ralph-stop-interceptor.sh`
- 状态文件: `memory/ralph-state.json`

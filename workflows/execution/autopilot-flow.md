# Autopilot 工作流

> 全自主执行的完整工作流定义

## 概述

Autopilot 工作流定义了从需求到交付的完整自动化流程，包括阶段转换、状态管理、错误处理和恢复机制。

## 状态机

```
┌─────────────────────────────────────────────────────────────┐
│                     Autopilot State Machine                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                        ┌─────────┐                          │
│                        │  IDLE   │                          │
│                        └────┬────┘                          │
│                             │ start                         │
│                             ▼                               │
│                        ┌─────────┐                          │
│            ┌──────────►│PLANNING │◄──────────┐              │
│            │           └────┬────┘           │              │
│            │                │                │              │
│            │           plan_complete         │              │
│            │                │                │              │
│            │                ▼                │              │
│         retry          ┌─────────┐        rollback          │
│            │           │SPEC_GEN │           │              │
│            │           └────┬────┘           │              │
│            │                │                │              │
│            │      spec_approved/skip         │              │
│            │                │                │              │
│            │                ▼                │              │
│            │           ┌─────────┐           │              │
│            └───────────│DEVELOP  │───────────┘              │
│                        └────┬────┘                          │
│                             │                               │
│                        dev_complete                         │
│                             │                               │
│                             ▼                               │
│                        ┌─────────┐                          │
│            ┌──────────►│   QA    │◄──────────┐              │
│            │           └────┬────┘           │              │
│            │                │                │              │
│         fix_and_retry  qa_passed        qa_failed           │
│            │                │                │              │
│            │                │      ┌─────────┴───┐          │
│            │                │      │   FIXING    │          │
│            │                │      └─────────────┘          │
│            │                │                               │
│            │                ▼                               │
│            │           ┌─────────┐                          │
│            └───────────│DELIVERY │                          │
│                        └────┬────┘                          │
│                             │                               │
│                        delivered                            │
│                             │                               │
│                             ▼                               │
│                        ┌─────────┐                          │
│                        │COMPLETE │                          │
│                        └─────────┘                          │
│                                                             │
│  Error States:                                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                     │
│  │ PAUSED  │  │ FAILED  │  │ ABORTED │                     │
│  └─────────┘  └─────────┘  └─────────┘                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 阶段详解

### Phase 1: Planning

**目标**: 分析任务，制定执行计划

**步骤**:
```yaml
1_intent_analysis:
  agent: intent-detector
  input: task_description
  output: intent, recommended_agents, recommended_skills

2_task_decomposition:
  agent: orchestrator
  input: task_description, intent
  output: subtasks[], dependencies[]

3_strategy_selection:
  agent: strategy-selector
  input: subtasks, dependencies
  output: strategy (PARALLEL|SEQUENTIAL|HIERARCHICAL)

4_resource_allocation:
  agent: orchestrator
  input: subtasks, strategy
  output:
    - agent_assignments[]
    - model_selections[]
    - time_estimates[]
    - cost_estimates
```

**输出**:
```json
{
  "plan_id": "plan-20260123-001",
  "intent": "feature_development",
  "subtasks": [
    {"id": "st-001", "name": "用户注册", "agent": "coder", "model": "sonnet"},
    {"id": "st-002", "name": "用户登录", "agent": "coder", "model": "sonnet"},
    {"id": "st-003", "name": "密码重置", "agent": "coder", "model": "sonnet"}
  ],
  "strategy": "SEQUENTIAL",
  "dependencies": [
    {"from": "st-001", "to": "st-002"},
    {"from": "st-002", "to": "st-003"}
  ],
  "estimates": {
    "time": "2h 30m",
    "cost": "$5.00"
  }
}
```

### Phase 2: Specification

**目标**: 生成详细的功能规范和技术设计

**步骤**:
```yaml
1_spec_generation:
  agent: spec-writer
  input: plan
  output: specs/SPEC-{feature}.md
  checkpoints:
    - draft_complete
    - sections_filled

2_architecture_design:
  agent: architect
  input: spec
  output:
    - architecture_diagram
    - data_models
    - api_contracts
    - technology_choices

3_review (if mode != full):
  type: human_checkpoint
  display: spec_summary
  options:
    - approve: continue
    - modify: edit_and_retry
    - reject: abort
```

**输出文件**:
- `specs/SPEC-{feature}.md`
- `specs/{feature}/architecture.md`
- `specs/{feature}/data-models.md`

### Phase 3: Development

**目标**: 实现代码

**步骤**:
```yaml
1_plan_memory_init:
  action: create_plan_scoped_memory
  output: .claude/context/plans/{plan_id}/

2_ralph_loop:
  agent: ralph
  config:
    max_iterations: 20
    checkpoint_interval: 3
  loop:
    - analyze_current_state
    - select_model (via model_router)
    - execute_subtask
    - verify_result
    - update_progress
    - check_completion

3_knowledge_capture:
  action: save_learnings
  output: .claude/context/plans/{plan_id}/learnings.json
```

**Ralph Loop 内部流程**:
```
while not complete and iteration < max:
    # 1. 分析当前状态
    state = analyze_progress()

    # 2. 选择下一个任务
    next_task = select_next_subtask(state)

    # 3. Model Router 选择模型
    model = model_router.select(next_task)

    # 4. 执行任务
    result = execute(next_task, model)

    # 5. 处理结果
    if result.needs_intervention:
        await request_intervention()
    elif result.is_error:
        handle_error(result)
    else:
        mark_complete(next_task)

    # 6. 保存检查点
    if iteration % checkpoint_interval == 0:
        save_checkpoint()

    iteration += 1
```

### Phase 4: QA

**目标**: 验证代码质量

**步骤**:
```yaml
1_code_review:
  agent: qa-reviewer
  input: code_changes
  output: qa-report.md
  scoring:
    - functionality: 40
    - code_quality: 30
    - test_coverage: 20
    - performance: 5
    - security: 5
  pass_threshold: 80

2_automated_testing:
  agent: automated-testing
  input: code_changes
  output:
    - test_results
    - coverage_report

3_auto_fix (if score < 80 and has_p2_issues):
  agent: qa-fixer
  input: qa_report.p2_issues
  output: fix-report.md
  max_retries: 3
  loop:
    - fix_issues
    - verify_fixes
    - re_review

4_human_fix (if has_p0_p1_issues):
  type: human_checkpoint
  display: critical_issues
  options:
    - fix_manually
    - accept_risks
    - abort
```

### Phase 5: Delivery

**目标**: 完成交付准备

**步骤**:
```yaml
1_documentation:
  agent: spec-writer
  tasks:
    - update_readme
    - generate_api_docs
    - update_changelog

2_experience_capture:
  action: extract_lessons
  input: plan_memory
  output:
    - memory/lessons-learned.md (append)
    - memory/best-practices.md (update)

3_cleanup:
  action: archive_plan
  tasks:
    - move_to_archive
    - compress_logs
    - update_metrics

4_notification:
  action: notify_completion
  output: delivery_report.md
```

## 错误处理

### 错误分类

| 错误类型 | 处理方式 | 示例 |
|----------|----------|------|
| Recoverable | 自动重试 | 网络超时、临时文件锁 |
| Fixable | QA-Fixer | P2 代码问题 |
| Requires Attention | 暂停请求确认 | P0/P1 问题、敏感操作 |
| Fatal | 终止执行 | 资源不可用、权限不足 |

### 重试策略

```yaml
retry_policy:
  max_retries: 3
  backoff:
    initial: 1s
    multiplier: 2
    max: 30s
  retryable_errors:
    - network_timeout
    - rate_limit
    - temporary_failure
```

### 回滚策略

```yaml
rollback_policy:
  checkpoints:
    - planning_complete
    - spec_approved
    - each_subtask_complete
    - qa_passed
  on_failure:
    - save_current_state
    - identify_rollback_point
    - restore_files
    - update_status
```

## 配置参考

### 完整配置

```json
{
  "autopilot": {
    "default_mode": "supervised",
    "phases": {
      "planning": {
        "enabled": true,
        "timeout": "5m",
        "agents": ["orchestrator", "strategy-selector"]
      },
      "specification": {
        "enabled": true,
        "timeout": "15m",
        "review_required": true,
        "agents": ["spec-writer", "architect"]
      },
      "development": {
        "enabled": true,
        "timeout": "4h",
        "ralph_config": {
          "max_iterations": 20,
          "checkpoint_interval": 3
        },
        "agents": ["coder", "debugger"]
      },
      "qa": {
        "enabled": true,
        "timeout": "30m",
        "pass_threshold": 80,
        "max_fix_attempts": 3,
        "agents": ["qa-reviewer", "qa-fixer", "automated-testing"]
      },
      "delivery": {
        "enabled": true,
        "timeout": "10m",
        "agents": ["spec-writer"]
      }
    },
    "checkpoints": {
      "enabled": true,
      "interval": 3,
      "max_stored": 10
    },
    "limits": {
      "max_cost": 20,
      "max_duration": "8h",
      "max_iterations": 50
    },
    "notifications": {
      "on_phase_complete": true,
      "on_intervention": true,
      "on_error": true,
      "on_complete": true
    }
  }
}
```

## 监控指标

### 实时指标

```yaml
metrics:
  - current_phase
  - current_subtask
  - progress_percentage
  - elapsed_time
  - estimated_remaining
  - tokens_used
  - cost_so_far
  - model_distribution
  - error_count
  - retry_count
```

### 完成报告

```yaml
completion_report:
  summary:
    - total_time
    - total_cost
    - subtasks_completed
    - qa_score
    - files_changed
  phases:
    planning:
      - duration
      - subtasks_identified
    specification:
      - duration
      - spec_length
    development:
      - duration
      - iterations
      - model_usage
    qa:
      - duration
      - initial_score
      - final_score
      - issues_fixed
    delivery:
      - duration
      - docs_generated
  lessons:
    - key_learnings
    - improvements_suggested
```

## 相关文档

- 命令文档: `commands/general/autopilot.md`
- Agent 定义: `agents/ops/autopilot-orchestrator.md`
- Ralph Loop: `workflows/execution/ralph-manager.md`
- QA 系统: `workflows/quality/self-healing.md`
- 编排模式: `workflows/orchestration/orchestration-patterns.md`

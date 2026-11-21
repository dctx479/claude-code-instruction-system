---
name: task-decompose
description: 将需求拆为本地纵向行为切片，每票包含测试、可执行验收和 blocked_by 依赖；不创建第二份任务清单或 GitHub issue。
license: MIT
metadata:
  category: planning
  tags:
  - task
  - decompose
  - planning
  - atomic
  - dependency
  - parallel
  - agile
  requires: []
  optional:
  - sdd-riper
  - spec-first
  version: 1.0.0
  trigger:
  - /task-decompose
  - 任务拆解
  - 需求分解
  - 拆分任务
  - 原子任务
  - 任务依赖图
disable-model-invocation: true
---

# Local vertical slices

Read the user's desired behavior, existing spec and constraints. Follow `docs/VNEXT-WORKFLOW.md`; do not create a second task authority.

Each ticket delivers a small observable behavior together with its tests, with a clear input/output boundary and an executable acceptance command. Split by user-visible behavior, not separate database/backend/test phases or an arbitrary four-hour limit.

Use the existing local issues CSV format (/plan-to-issues). New rows include id, title, acceptance_criteria, blocked_by and dev_state; dependency IDs are pipe-separated, empty when independent. Keep implementation evidence in refs/notes. Do not bind the requirement to today's implementation file path.

Check unknown dependencies, cycles and prerequisites before execution. Use `scripts/validate-issues.py` (global install: `$HOME/.claude/scripts/validate-issues.py`) when available; otherwise explicitly report the missing checker. A TODO dependency prevents a dependent ticket from starting.

Ask only for material unknowns not already answered. Do not create GitHub issues, install dependencies, start agents, implement code or publish merely because a decomposition was requested.

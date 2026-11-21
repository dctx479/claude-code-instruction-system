---
name: handoff
description: 上下文交接仪式 - /compact 之前写交接文档（compact模式），或生成可复制的续接 prompt 用于开新对话窗口（new-window模式）
license: MIT
metadata:
  category: system
  tags:
  - handoff
  - context-engineering
  - compact
  - session-management
  - continuity
  integration:
  - prime
  - neat
  - reflection
  - context-engineering
  version: 1.1.0
  trigger:
  - /handoff
  - 准备 compact
  - 上下文快满了
  - 交接一下
  - 记录当前进度
  - 开新窗口继续
  - 生成续接 prompt
  - context is getting full
disable-model-invocation: true
---

# Verified handoff

Use `scripts/checkpoint.py` as described in `docs/VNEXT-WORKFLOW.md`.
For a global install, use `$HOME/.claude/scripts/checkpoint.py` with the target project as cwd (requires the commands component). Do not assume this repository's scripts exist in every project.
Save one worktree-local checkpoint before compacting or moving to a new session. Include goal, completed work, next actions, evidence commands/paths and the repository-relative changed files.
Feed JSON to `python scripts/checkpoint.py save`; the script computes hashes. Never fabricate test results or hashes.
On continuation run `python scripts/checkpoint.py show`: 0 valid, 2 absent, 1 corrupted/stale. If stale, inspect the changes and preserve the original evidence before updating.
For a new-window handoff, produce a short continuation prompt pointing to the same checkpoint; do not duplicate the full state in memory/handoff.md.
Legacy memory/handoff.md may be read as historical context only, with a WARNING that it lacks integrity verification.

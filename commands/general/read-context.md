---
description: read context via verified handoff
disable-model-invocation: true
---

# /read-context

Use the handoff Skill and `python scripts/checkpoint.py show` per `docs/VNEXT-WORKFLOW.md`.
Keep one worktree-local checkpoint, not another copy in memory. Exit codes: 0 valid, 2 absent, 1 corrupt/stale. Reconcile stale evidence before continuing.
For explicitly requested historical context, the old context scripts remain available; their output is unverified historical reference, not current checkpoint state.

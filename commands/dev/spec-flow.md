---
description: spec flow
disable-model-invocation: true
---

# /spec-flow

Use `docs/VNEXT-WORKFLOW.md` as the workflow contract.

- `start <feature>`: determine risk, reuse or create `specs/SPEC-<feature>.md`. Clarify only missing behavior; /grill has an eight-question ceiling.
- `next`: validate the current stage against its acceptance evidence, then advance to the next necessary stage. Reuse existing approval; do not ask again for an already authorized action.
- `status`: report the spec status and local issue states, with failed/unrun checks explicit.

Approved specs remain unchanged; append a delta spec for new requirements. Use /plan-to-issues and /issues-execute, not a second state machine or a fabricated .spec-flow-state.json.
No task-wide score can override a failed required acceptance condition.

---
name: sdd-riper
description: Spec-Driven Development + RIPER 五阶段流程，确保大模型编程质量可控
metadata:
  type: Heavy（重量级）
  version: 1.1.0
  trigger:
  - /riper
  - /sdd-riper
  - 中大型需求开发
  - 需要写规范文档
  - 复杂功能实现
disable-model-invocation: true
---

# Spec-driven RIPER

Use the risk-based contract in `docs/VNEXT-WORKFLOW.md`. Explicit selection chooses this planning method, not extra permissions or a second document hierarchy.

## Research and innovate
Read the actual implementation, relevant tests and existing decisions. Clarify only material unknowns; reuse answers and authorization already supplied. Compare alternatives only where the decision has a real tradeoff.

## Plan
Reuse the local approved `specs/SPEC-<feature>.md` and its acceptance criteria. Do not copy it into mydocs or require a fixed chapter count. LOW work needs no new spec. MEDIUM uses local vertical slices and `blocked_by`; HIGH adds rollback and boundary evidence. Classify by blast radius, not file/line count.
An approved spec is immutable. Changed requirements use a delta spec; unchanged requirements do not need approval again.

## Execute and review
Carry out the authorized slice. For bugs capture a failing command before changing implementation. Run the same command after the change and the relevant regression checks. Preserve raw failures and unresolved blockers.
Review against the artifact and acceptance criteria, without supplying the implementer's conclusion to an independent reviewer. Stop after three repair/review rounds with unresolved blockers recorded. Use another agent or external CLI only under existing authorization.

## Delivery
Report behavior, diff, real commands/results and remaining limitations. Reuse a single checkpoint for continuation. Do not add a wiki, mandatory knowledge archive, duplicate spec, automatic commit/push, arbitrary score or time allocation threshold.

---
name: spec-first
description: 完整 QA 工作流编排器 - 串联 spec-writer → qa-reviewer → qa-fixer 三步流程，确保功能从规范到验收的质量闭环
license: MIT
metadata:
  category: development
  tags:
  - qa
  - spec
  - quality
  - workflow
  - automation
  - spec-first
  integration:
  - spec-writer
  - qa-reviewer
  - qa-fixer
  - sdd-riper
  version: 1.0.0
  trigger:
  - /spec-first
  - 完整 QA 流程
  - 先写规范再开发
  - 需要质量保障
  - spec first
disable-model-invocation: true
---

# Spec-first

Follow `docs/VNEXT-WORKFLOW.md` for risk selection and the seven-stage workflow.
Reuse an existing spec where it already defines the required behavior. LOW tasks do not need a new spec.
Approved specs are immutable: create a delta spec for changed requirements.
Use /plan-to-issues and /issues-execute for local vertical slices. Ask only for missing decisions that materially affect behavior.
Verification is evidence per acceptance item; use qa-reviewer with artifacts and criteria, without the implementer's conclusion. Limit repair/review to three rounds and report remaining blockers.
No automatic commit, push, external CLI, delegation or permissions escalation is implied by this skill.

---
name: sdd-riper-light
description: SDD-RIPER 轻量版 - 适用于熟练用户和简单任务的快速开发流程
metadata:
  type: Light（轻量级）
  version: 1.1.0
  trigger:
  - /riper-light
  - /sdd-light
  - 简单 bug 修复
  - 小功能开发
  - 快速迭代
disable-model-invocation: true
---

# Lightweight spec-driven work

Follow `docs/VNEXT-WORKFLOW.md` and the project's own acceptance commands. Select risk by behavior and blast radius, not a fixed number of files or lines.

- LOW: inspect the relevant files, make the requested change, run relevant checks, deliver diff/results. Do not manufacture a micro-spec for a one-line correction.
- MEDIUM: reuse the existing spec/plan, or write the smallest behavior contract that resolves a real uncertainty. Use local vertical slices where dependencies justify them.
- HIGH: include rollback and boundary evidence; use existing authorization, and ask only before a newly unauthorized external or irreversible action.
- Bug: first reproduce with a stable failing command; after fixing, execute that same command and related regressions.

An already approved spec is sufficient authorization for the implementation in scope. Do not ask for approval again or silently auto-approve a new scope. Keep approved specs unchanged; new requirements go in a delta spec.
No mydocs hierarchy, fixed chapter count, extra change-log copy, automatic knowledge archive, dependency installation or publication is implied. Report failed/unrun acceptance explicitly.

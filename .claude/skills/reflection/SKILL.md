---
name: reflection
description: 根据真实任务证据复盘，区分机械检查与判断规则；保留历史案例，不凑经验数量或自动扩张流程。
license: MIT
metadata:
  category: system
  tags:
  - reflection
  - lessons-learned
  - knowledge-compounding
  - ingest
  - self-evolution
  integration:
  - neat
  - skill-creator
  - knowledge-compounding
  version: 1.0.0
  trigger:
  - /reflection
  - 复盘一下
  - 总结经验
  - 提炼教训
  - 记录一下这次的收获
disable-model-invocation: true
---

# Evidence-based reflection

Use the completed task's actual artifacts and command results. Search related existing entries before proposing a new lesson. Follow the mechanical-versus-judgment split in `docs/VNEXT-WORKFLOW.md` and /evolve.

For each supported finding record the incident, evidence pointer, before/after behavior, verification method and confidence. Produce only as many findings as evidence supports; zero is valid. Do not invent another incident to meet the two-event rule for new permanent rules.
Distinguish a template, proposed metric and real measurement. Invocation counts do not establish quality, success rate, time or cost. Missing raw measurements remain unknown.

Write only the artifact the user requested. Historical memory remains unchanged unless its update is authorized; when authorized append dated evidence and mark supersession explicitly, preserving the original case. Do not automatically chain neat, create a new Skill, add rules or build a wiki. Already supplied authorization is sufficient; do not ask again for that same action.

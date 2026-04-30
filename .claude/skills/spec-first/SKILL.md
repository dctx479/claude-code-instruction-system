---
name: spec-first
description: 完整 QA 工作流编排器 - 串联 spec-writer → qa-reviewer → qa-fixer 三步流程，确保功能从规范到验收的质量闭环
version: 1.0.0
license: MIT
metadata:
  category: development
  tags: [qa, spec, quality, workflow, automation, spec-first]
  integration: [spec-writer, qa-reviewer, qa-fixer, sdd-riper]
trigger:
  - "/spec-first"
  - "完整 QA 流程"
  - "先写规范再开发"
  - "需要质量保障"
  - "spec first"
---

# Spec-First QA 工作流 (Spec-First)

> 把"写完再测"变成"规范驱动开发"：先有 Spec，再有代码，再有验收。

## 设计动机

没有规范的开发常见失败模式：

| 反模式 | 后果 |
|--------|------|
| 直接写代码，没有 Spec | 需求理解偏差，返工 |
| 写完代码才做 QA | 发现问题成本高，改动大 |
| QA 发现问题，手动修复 | 重复劳动，容易遗漏 |
| 修完不重新验收 | 修复引入新问题 |

本 Skill 的核心原则：**规范是唯一的事实来源**，代码和测试都对齐规范。

---

## What（输入/输出）

**输入**：功能需求描述（自然语言）

**输出**：
- `specs/SPEC-{feature}.md` — 功能规范文档
- 实现代码（符合规范）
- QA 审查报告（评分 ≥80 通过）
- 自动修复记录（P2 问题）

---

## How（三步 QA 工作流）

### Step 1 — Spec 编写（spec-writer Agent）

**目标**：把需求描述转化为可验收的规范文档。

```bash
/agent spec-writer    # 启动 spec-writer Agent
```

**Spec 文档必须包含**：
- 功能描述（用户故事格式）
- 输入/输出定义
- 验收标准（可量化，可测试）
- 边界情况和错误处理
- 非功能性需求（性能/安全/兼容性）

**门禁**：Spec 未经用户确认前，不进入 Step 2。

### Step 2 — 开发实现

**目标**：严格按 Spec 实现，不添加 Spec 未定义的功能。

**实现原则**：
- 每个验收标准对应一个实现点
- 边界情况必须处理
- 不做 Spec 之外的"顺手优化"

### Step 3 — QA 验收循环

**目标**：验证实现符合 Spec，自动修复可修复的问题。

```
开发完成
    │
    ↓
qa-reviewer 评分（总分100，通过线≥80）
    │
    ├── ≥80 → 通过，发布
    │
    └── <80 → 分析问题
                │
                ├── 有 P2 问题 → qa-fixer 自动修复 → 重新评分
                │
                └── 只有 P0/P1 → 人工修复 → 重新评分
```

**评分体系**：
- 功能完整性: 40分（最重要，对齐 Spec 验收标准）
- 代码质量: 30分
- 测试覆盖: 20分
- 性能: 5分
- 安全: 5分

**问题分级**：
- 🔴 P0: 阻塞发布，必须人工修复（功能缺失/安全漏洞）
- 🟡 P1: 建议修复，视情况人工/自动（代码质量问题）
- 🟢 P2: 可自动修复，不影响功能（格式/注释/小优化）

---

## When Done（验收标准）

### 必须满足

1. **Spec 文档存在** — `specs/SPEC-{feature}.md` 已创建且用户已确认
2. **QA 评分 ≥80** — qa-reviewer 最终评分通过
3. **P0/P1 问题已处理** — 无遗留阻塞问题

### 建议满足

- P2 问题已由 qa-fixer 自动修复
- 测试覆盖率 ≥80%
- Spec 与实现保持同步（如有变更，Spec 已更新）

---

## What NOT（边界约束）

🚫 **不做的事**：

1. **不跳过 Spec 直接开发** — 没有 Spec 就没有验收标准，QA 无从评分
2. **不在 Spec 未确认时开始实现** — 用户确认是门禁，不是可选步骤
3. **不替代 `sdd-riper`** — sdd-riper 是完整的 RIPER 五阶段流程，spec-first 只是 QA 闭环；复杂需求用 sdd-riper
4. **不自动修复 P0/P1** — P0/P1 需要人工判断，qa-fixer 只处理 P2

🚫 **不该触发的场景**：

- 简单 Bug 修复（用 `sdd-riper-light` 或直接修复）
- 配置文件调整（无需 Spec）
- 已有 Spec 的迭代开发（直接从 Step 2 开始）

---

## 调用时机

| 场景 | 是否调用 | 说明 |
|------|---------|------|
| 新功能开发，需要质量保障 | ✅ 强烈建议 | 主用法 |
| 重要 Bug 修复，需要验收 | ✅ 建议 | 防止修复引入新问题 |
| 简单改动（<50行） | ❌ 不需要 | 用 sdd-riper-light |
| 已有 Spec 的迭代 | ❌ 不需要 | 直接从 Step 2 开始 |

---

## 与现有体系的关系

```
新功能需求
    │
    ↓
[/spec-first]          ← 完整 QA 工作流（本 Skill）
    │
    ├── Step 1: spec-writer → SPEC-{feature}.md
    │
    ├── Step 2: 开发实现（按 Spec）
    │
    └── Step 3: qa-reviewer → 评分 → qa-fixer（P2）→ 重新评分
    │
    ↓
发布
    │
    ↓
[/reflection]          ← 提炼经验（可选）
```

**协同 Agent**：
- `agents/spec-writer.md` — Step 1 规范编写
- `agents/qa-reviewer.md` — Step 3 质量评分
- `agents/qa-fixer.md` — Step 3 自动修复 P2

**升级路径**：
- 简单任务 → `sdd-riper-light`
- 中大型需求 → `sdd-riper`（包含完整 RIPER 五阶段）
- 需要 QA 闭环 → `spec-first`（本 Skill，可与 sdd-riper 组合）

---

## 版本历史

- **v1.0.0** (2026-04-30): 初版，封装 CLAUDE.md 第三节 QA 系统为可调用 Skill，填补 Agent 层与 Skill 层之间的空白

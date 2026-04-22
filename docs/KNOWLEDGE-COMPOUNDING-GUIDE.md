# 知识复利指南 (Knowledge Compounding Guide)

> 核心理念: **有状态知识 > 无状态 RAG**。每次任务的产出不仅解决当前问题，还积累为可复用的知识资产。

---

## 什么是知识复利？

```
传统模式（无状态）:
  任务 A → 解决 → 知识消失
  任务 B → 从零开始 → 重复试错

知识复利模式（有状态）:
  任务 A → 解决 → 提炼经验 → 写入知识库
  任务 B → 检索知识库 → 跳过已知错误 → 更快解决 → 更新知识库
  任务 C → 知识库更丰富 → 解决更复杂问题 → 复利效应
```

---

## 三层知识架构

```
Layer 1: 原始记录 (Raw Records)
  ├── memory/lessons-learned.md    — 原始经验条目
  ├── .claude/context/resolutions/ — 问题解决方案
  └── 对话历史和 commit messages

         ↓ 提炼 (Ingest)

Layer 2: 策展知识 (Curated Knowledge)
  ├── memory/best-practices.md     — 验证过的最佳实践
  ├── memory/error-patterns.md     — 错误模式库
  └── docs/*.md                    — 主题指南

         ↓ 编码 (Codify)

Layer 3: 执行规则 (Execution Rules)
  ├── CLAUDE.md                    — 强制执行的规则
  ├── agents/*.md                  — Agent 行为定义
  └── .claude/skills/*/SKILL.md    — Skill 能力定义
```

**关键区别**:
- Layer 1 记录"发生了什么"（事实）
- Layer 2 总结"应该怎么做"（模式）
- Layer 3 定义"必须怎么做"（规则）

---

## 知识晋升流程

```
单次经验 (lesson-learned)
    │
    │ 重复出现 2+ 次，有 before/after 示例
    ↓
通用模式 (best-practice)
    │
    │ 被多个 Agent/场景依赖，有量化验证
    ↓
系统规则 (CLAUDE.md rule)
    │
    │ 需要在特定领域强制执行
    ↓
Agent/Skill 定义 (agents/*.md / SKILL.md)
```

**晋升条件**:

| 从 → 到 | 条件 |
|---------|------|
| lesson → pattern | 2+ 次重复 + before/after 示例 + 案例引用 |
| pattern → best-practice | 跨场景验证 + 量化效果（如"节省 40% token"） |
| best-practice → CLAUDE.md rule | 所有场景都应遵守 + 违反后果严重 |
| rule → Agent/Skill | 特定领域需要专门执行逻辑 |

**降级条件**: 规则被证明过时或不适用 → 添加 `已废弃` 标记 → 定期清理

---

## 三操作: Ingest / Query / Lint

### Ingest（摄入）

将新知识写入适当层级:

```markdown
场景: 修复了一个 Windows hooks 路径问题

1. 写入 Layer 1: lessons-learned.md 新增条目
   - 包含: 问题描述、根因、解决方案、验证方法、案例引用

2. 检查是否可晋升 Layer 2:
   - 这是第几次遇到 Windows 路径问题？
   - 如果 ≥2 次 → 提炼为 best-practice 条目

3. 检查是否可晋升 Layer 3:
   - 这个规则是否应该所有场景都遵守？
   - 如果是 → 更新 CLAUDE.md
```

**Ingest 去重协议**: 写入新条目前，先搜索现有内容:
1. `Grep` 搜索关键词，检查是否已有类似条目
2. 如有 → 更新现有条目（追加案例），而非创建新条目
3. 如无 → 创建新条目

### Query（检索）

任务开始前自动检索相关知识:

```markdown
1. 读取 .claude/context/index.json — 是否有匹配的问题签名？
2. 搜索 memory/error-patterns.md — 是否有类似错误模式？
3. 搜索 memory/best-practices.md — 是否有适用的策展型最佳实践条目？
```

太一元系统已有此机制: CLAUDE.md 第九节的"上下文检索协议"。

### Lint（质检）

定期检查知识库质量:

| 检查项 | 问题 | 修复 |
|--------|------|------|
| 无案例引用 | 条目无法验证 | 补充案例或删除 |
| 内容矛盾 | 两条目对同一概念描述不同 | 保留更新的，废弃旧的 |
| 过度泛化 | "注意配置格式"无具体场景 | 补充 before/after 或删除 |
| 已过时 | 规则不再适用 | 标记废弃 + 说明原因 |

---

## 置信度标注协议

每条知识条目建议标注置信度:

| 标注 | 含义 | 条件 |
|------|------|------|
| `[VERIFIED]` | 已验证 | 有案例引用 + 验证方法已执行 |
| `[INFERRED]` | 推断的 | 基于有限样本推断，尚未大规模验证 |
| `[AMBIGUOUS]` | 有歧义 | 部分场景有效，部分场景无效 |
| `[UNVERIFIED]` | 未验证 | 新记录，尚未验证 |

**使用场景**: 在 lessons-learned.md 的条目标签中添加置信度标注，例如:
```markdown
### 标签
#hooks #windows #bash [VERIFIED]
```

**决策权重**: AI 参考知识时，`[VERIFIED]` 的条目优先于 `[UNVERIFIED]` 的条目。

---

## 知识衰减与清理

知识不是越多越好。定期清理过时知识:

**清理触发**:
- 季度例行审查
- CLAUDE.md 接近 40K 限制
- 发现矛盾条目时

**清理标准**:
- 标记为 `已废弃` 超过 3 个月 → 删除
- 引用的工具/版本已不存在 → 删除或更新
- 被更新的条目完全替代 → 删除旧条目

---

## 相关文档

- CLAUDE.md 第一节 — 自进化协议（知识摄入的触发机制）
- CLAUDE.md 第九节 — 记忆系统（存储结构）
- `docs/MEMORY-SYSTEM.md` — 多层记忆架构详细说明
- `docs/CONTEXT-ENGINEERING-GUIDE.md` — 信噪比原则（知识加载策略）
- `memory/lessons-learned.md` — Layer 1 原始记录
- `memory/best-practices.md` — Layer 2 策展知识

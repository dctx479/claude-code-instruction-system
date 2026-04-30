---
name: skill-creator
description: Skill 元创建器 - 按本项目契约（What/How/When done/What NOT）+ 单一职责 + 方法论优于规则三原则，生成高质量 SKILL.md
version: 1.0.0
license: MIT
metadata:
  category: system
  tags: [meta-skill, skill-authoring, contract, template, quality-control]
  integration: [neat, reflection, knowledge-compounding]
trigger:
  - "/skill-creator"
  - "创建一个 Skill"
  - "把这个流程封装成 Skill"
  - "提炼成 Skill"
---

# Skill 元创建器 (Skill Creator)

> 一个用来**创建 Skill 的 Skill**。教 AI 按本项目的契约风格生成新 Skill，避免每次重新摸索。

## 设计动机

很多 Skill 失败不是因为模型笨，是因为**作者没把方法论讲清楚**。常见反模式：

| 反模式 | 后果 | 典型表现 |
|--------|------|---------|
| 一个 Skill 干太多事 | 评估发散，输出失控 | "解决方案 + 工作量 + 流程图 + 评估"塞一起 |
| 只给规则不给方法论 | AI 死板执行，弄巧成拙 | "测试是后端的 1/3"→ 数字僵硬翻倍 |
| 没有 What NOT | 边界外溢，破坏其他流程 | Skill A 在收尾时擅自改代码 |
| 缺少验收标准 | 不知道何时算"做完" | 输出长度/格式无下限 |

本 Skill 把项目里成熟 Skill（plan-review、neat、sdd-riper-light）共享的好实践沉淀成模板。

---

## What（输入/输出）

### 输入

| 输入项 | 必需 | 描述 |
|--------|------|------|
| **Skill 主题** | 是 | 一句话说明这个 Skill 解决什么问题 |
| **触发场景** | 是 | 用户在什么情况下会想到调用它 |
| **现有经验/案例** | 推荐 | 你已经在对话中实践过的步骤、踩过的坑 |
| **类型偏好** | 否 | Light（单文件 1-2K tokens）/ Heavy（多文件 5-10K） |

### 输出

| 输出项 | 格式 | 描述 |
|--------|------|------|
| **新 Skill 目录** | `.claude/skills/<name>/SKILL.md` | 完整 SKILL.md 文件 |
| **INDEX.md 注册条目** | YAML 块追加 | 在合适分类下注册 |
| **设计决策摘要** | Markdown | 解释职责拆分、方法论选取、What NOT 边界 |

---

## How（六步执行流程）

### Step 1 — 单一职责检查

问自己三个问题：

1. 这个 Skill 是否只做**一件事**？如果包含"和"或"以及"，多半要拆。
2. 输入和输出能否用一句话说清？
3. 是否会与现有 Skill 重复？（先 Grep `.claude/skills/INDEX.md`）

**禁止**：把"探索方案 + 评估工作量 + 写文档"塞一个 Skill。
**正确**：每件事一个 Skill，串联调用。

### Step 2 — 方法论提炼

不要只列规则，要给**判断框架**。对比：

| 反模式（只给规则） | 推荐（给方法论） |
|-------------------|------------------|
| "测试工作量 = 后端 × 1/2" | "拆解链路：需求 → 场景 → 模块 → 功能 → 原子任务，最后按角色估时数；比例仅作 sanity check 而非铁律" |
| "禁止使用 SQLite" | "判断数据库选型时优先看：并发需求 / 事务复杂度 / 部署环境约束" |

**关键测试**：把规则给一个新人，他能否在边界场景做出合理判断？不能 → 规则不够，需要补方法论。

### Step 3 — 契约四要素填充

每个 Skill 必须显式声明这四块（缺一不可）：

```markdown
## What（输入/输出）
| 输入项 | 必需 | 描述 |
| 输出项 | 格式 | 描述 |

## How（执行步骤）
Step 1 — ...
Step 2 — ...
（禁止"按需执行"等模糊表述，要写顺序约束）

## When Done（验收标准）
### 必须满足
1. ...
2. ...
### 建议满足
- ...

## What NOT（边界约束）
🚫 不做的事:
1. 不修改 X
2. 不替代 Y

🚫 不该触发的场景:
- ...
```

### Step 4 — 生成 SKILL.md 骨架

按本项目格式（参考 `.claude/skills/plan-review/SKILL.md`、`.claude/skills/neat/SKILL.md`）：

```markdown
---
name: <slug>
description: <一句话描述，在 INDEX 中可见>
version: 1.0.0
license: MIT
metadata:
  category: <system|planning|development|design|research|...>
  tags: [tag1, tag2, ...]
  integration: [其他相关 Skill/Agent]
trigger:
  - "/<slug>"
  - "<中文触发词1>"
  - "<中文触发词2>"
---

# <Skill 中文名> (<English Name>)

> 一句话点题（用户能看懂的价值主张）

## 设计动机
（简述要解决的问题，对治什么反模式）

## What
（输入/输出表格）

## How
（步骤化执行流程）

## When Done
（验收标准）

## What NOT
（边界约束）

## 调用时机
| 场景 | 是否调用 | 说明 |

## 与现有体系的关系
（说明与哪些 Skill/Agent 协同）

## 实例
（一个具体的端到端示例）

## 版本历史
- **v1.0.0** (YYYY-MM-DD): 初版
```

### Step 5 — 决定轻重双轨

| 类型 | 大小 | 结构 | 适用 |
|------|------|------|------|
| **Light** | 1-2K tokens | 单文件 SKILL.md | 高频、低复杂度（如 /neat、reflection） |
| **Heavy** | 5-10K tokens（分散） | SKILL.md + REFERENCE.md + EXAMPLES.md | 低频、高复杂度（如 sdd-riper、安全审计） |

**判断准则**：
- 用户每周触发 ≥3 次 + 单次执行 ≤5 步 → Light
- 跨多个子任务 / 涉及多种输出格式 / 有可独立查阅的参考资料 → Heavy

### Step 6 — INDEX.md 注册 + 自检

1. 在 `.claude/skills/INDEX.md` 对应分类下追加 YAML 块（参考已有条目格式）
2. 如该 Skill 适用的场景在速查表中缺失 → 补一行
3. 自检清单：
   - [ ] 单一职责（无"+"号陈述）
   - [ ] 契约四要素齐全
   - [ ] 至少一个端到端实例
   - [ ] What NOT 已明确至少 3 条边界
   - [ ] 触发词覆盖中英双语
   - [ ] 与现有 Skill 无功能重叠

---

## When Done（验收标准）

### 必须满足

1. **单一职责** — Grep 新 SKILL.md 不出现"+ 同时 / 以及 / 顺便"等多职责连接词
2. **契约完整** — What / How / When Done / What NOT 四块均存在且有内容
3. **方法论 ≥ 规则** — How 步骤中至少一条解释"为什么这么做"，而非纯指令
4. **实例落地** — 至少一个端到端例子（输入→操作→输出）
5. **INDEX 已注册** — 可被 `Skill` 工具识别

### 建议满足

- 与至少 1 个现有 Skill 显式标注集成关系（避免孤岛）
- Light 类总长 ≤ 300 行，Heavy 类 SKILL.md ≤ 200 行（其余分流到 REFERENCE.md）

---

## What NOT（边界约束）

🚫 **不做的事**：

1. **不创建占位 Skill** — 没有真实使用经验/方法论沉淀，禁止生成空壳
2. **不复制代码生成框架** — 本 Skill 教写 Skill，不教写应用代码
3. **不修改其他 Skill** — 仅创建新 Skill；改造旧 Skill 走 /neat 流程
4. **不发明触发词** — 触发词必须能对应到真实用户语境
5. **不强制 Heavy 化** — 简单流程优先 Light，避免过度设计

🚫 **不该触发的场景**：

- 一次性脚本/一次性流程（无复用价值）
- 已有 Skill 完全覆盖（先看 INDEX，避免重复）
- 用户只想要单次执行结果（直接做即可）

---

## 调用时机

| 场景 | 是否调用 | 说明 |
|------|---------|------|
| 反复用同一套流程 ≥3 次 | ✅ 强烈建议 | 高频流程值得 Skill 化 |
| 涉及领域知识/方法论 | ✅ 建议 | 把隐性经验显性化 |
| 复杂任务结尾，识别出可复用模式 | ✅ 建议 | 配合 /reflection 提炼 |
| 完成单次性任务 | ❌ 不需要 | 直接做即可 |
| 用户已说明"只这一次" | ❌ 不需要 | 尊重需求 |

---

## 与现有体系的关系

```
[/reflection]         ← 复盘识别可复用模式
       ↓
[/skill-creator]      ← 把模式封装成 Skill（本 Skill）
       ↓
[INDEX.md 注册]
       ↓
[/neat]               ← 收尾时同步到 docs/CLAUDE.md
```

**协同**：
- `.claude/skills/neat/SKILL.md` — 创建后用 /neat 同步三层知识
- `.claude/skills/reflection/SKILL.md` — 复盘流程的下游（可生成 Skill 候选）
- `docs/KNOWLEDGE-COMPOUNDING-GUIDE.md` — Layer 3 编码（Skill 是规则的一种载体）
- `.claude/skills/README.md` — Skill 集成指南

---

## 实例

### 触发：用户说"把刚才工作量评估的流程做成 Skill"

```
Step 1 单一职责检查:
  - 主题：工作量评估
  - 是否单一？✅（不含方案设计）
  - 已有 Skill？Grep 后无重复

Step 2 方法论提炼:
  - 用户给的经验：测试 = 后端 1/2，前端 = 后端 1/2
  - 提炼：判断框架是"需求 → 场景 → 模块 → 功能 → 任务"五步链路
  - 比例只是 sanity check，不是死规则

Step 3 契约填充:
  - What 输入：需求描述 + 已确认的方案
  - What 输出：场景级表格（行=场景，列=角色，值=人天）
  - When Done：每个场景都有产品/前端/后端/测试列；总人天合理性 check
  - What NOT：方案未定时拒绝评估；不替代真实排期

Step 4-5: 生成 Light 类 SKILL.md，~250 行

Step 6 注册:
  - INDEX.md "产品类" 下新增条目
  - 速查表 "工作量评估" 行新增

输出：.claude/skills/effort-estimation/SKILL.md
```

---

## 版本历史

- **v1.0.0** (2026-04-30): 初版，沉淀自项目内 plan-review/neat/sdd-riper-light 共享的契约范式

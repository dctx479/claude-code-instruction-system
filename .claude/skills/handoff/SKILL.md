---
name: handoff
description: 上下文交接仪式 - /compact 之前将当前进度、未完成决策、下一步行动结构化写入交接文档，让压缩后的新会话能无缝接续
version: 1.0.0
license: MIT
metadata:
  category: system
  tags: [handoff, context-engineering, compact, session-management, continuity]
  integration: [prime, neat, reflection, context-engineering]
trigger:
  - "/handoff"
  - "准备 compact"
  - "上下文快满了"
  - "交接一下"
  - "记录当前进度"
---

# 上下文交接 (Handoff)

> /compact 之前的最后一步：把"我知道但 AI 不知道"的隐性上下文显式化，让压缩后的新会话从正确位置继续。

## 设计动机

/compact 会压缩对话历史，新会话的 AI 只能看到摘要。常见的失败模式：

| 反模式 | 后果 |
|--------|------|
| 直接 /compact，不做交接 | 新会话不知道"为什么这样做"，重新走弯路 |
| 只靠 /prime 恢复上下文 | /prime 读 git 状态，但读不到"当前正在做什么" |
| 把进度写在对话里 | 压缩后丢失，新会话看不到 |

本 Skill 的核心洞察：**git 状态是结果，交接文档是过程**。/prime 读结果，/handoff 写过程。

---

## What（输入/输出）

**输入**：当前会话的工作状态（自动从上下文推断）

**输出**：`memory/handoff.md` — 结构化交接文档，包含：
- 当前任务状态（做了什么 / 做到哪了）
- 未完成的决策（还没确定的技术选型、方案选择）
- 关键上下文（为什么这样做，不是显而易见的原因）
- 下一步行动（具体到可以直接执行的指令）

---

## How（三步执行流程）

### Step 1 — 盘点当前状态（~1分钟）

从当前会话上下文中提取：

```
□ 正在进行的任务是什么？（一句话描述）
□ 已完成的部分是什么？（列举具体文件/功能）
□ 卡在哪里了？（如果有阻塞）
□ 有哪些临时决定还没有固化？
```

同时运行：
```bash
git status          # 未提交的变更
git stash list      # 暂存的工作
```

### Step 2 — 识别隐性上下文（~1分钟）

这是最关键的一步。问自己：

> "如果一个新 AI 接手这个任务，它会犯什么错误？"

常见的隐性上下文类型：
- **约束**：为什么不能用方案 A（已经试过，失败了）
- **决策**：为什么选了方案 B（有具体原因，不是随机选的）
- **依赖**：这个改动依赖另一个还没完成的改动
- **风险**：某个地方很脆弱，改动时要小心

### Step 3 — 写入交接文档

输出格式（写入 `memory/handoff.md`，覆盖旧内容）：

```markdown
# 上下文交接文档
更新时间: {ISO8601}

## 当前任务
{一句话描述正在做什么}

## 已完成
- {具体文件/功能 1}
- {具体文件/功能 2}

## 进行中（未完成）
- {任务 1}：{当前状态}
- {任务 2}：{当前状态}

## 未完成的决策
- {决策点 1}：{候选方案 A vs B，倾向于 X，原因是 Y}
- {决策点 2}：{待确认}

## 关键上下文（新会话必读）
- {约束/原因 1}：{具体说明}
- {约束/原因 2}：{具体说明}

## 下一步行动
1. {具体指令 1}（可以直接执行）
2. {具体指令 2}
3. {具体指令 3}

## 相关文件
- {文件路径 1}：{用途}
- {文件路径 2}：{用途}
```

---

## When Done（验收标准）

### 必须满足

1. **`memory/handoff.md` 已写入** — 文件存在且内容完整
2. **下一步行动可直接执行** — 不是"继续做 X"，而是"运行 Y 命令 / 修改 Z 文件的第 N 行"
3. **隐性上下文已显式化** — 至少有 1 条"为什么这样做"的说明

### 建议满足

- 未提交变更已暂存（`git stash`）或已提交
- 如果有重要经验，先调用 `/reflection` 提炼后再 /compact

---

## What NOT（边界约束）

🚫 **不做的事**：

1. **不替代 `/neat`** — /neat 同步三层知识体系，/handoff 只记录当前进度；两者互补，不互替
2. **不替代 `/reflection`** — /reflection 提炼可复用经验，/handoff 记录一次性进度状态
3. **不写全量文档** — 只写新会话需要但无法从 git/代码推断的信息
4. **不超过 50 行** — 交接文档太长说明没有精炼，新会话也不会认真读

🚫 **不该触发的场景**：

- 会话正常结束（用 /neat 代替）
- 任务已完成（用 /reflection + /neat 代替）
- 只是暂时切换任务（不需要 /compact）

---

## 调用时机

| 场景 | 是否调用 | 说明 |
|------|---------|------|
| 上下文 >250K tokens，准备 /compact | ✅ 强烈建议 | 主用法，/compact 前必做 |
| 任务中途需要暂停，明天继续 | ✅ 建议 | 防止隔天忘记进度 |
| 任务完成，正常结束会话 | ❌ 不需要 | 用 /reflection + /neat |
| 会话中途换任务 | ❌ 不需要 | 上下文还在，不需要交接 |

---

## 与现有体系的关系

```
上下文快满了
    │
    ↓
[/handoff]             ← 写交接文档（本 Skill）
    │
    ↓
[/neat]                ← 同步三层知识（可选，如有新知识）
    │
    ↓
/compact               ← 压缩对话历史
    │
    ↓
新会话开始
    │
    ↓
[/prime]               ← 读 git 状态 + 检索记忆
    │
    ↓
读取 memory/handoff.md ← 恢复当前进度（/prime Step 2 会检索到）
    │
    ↓
继续任务
```

**完整生命周期**：`/prime` → 执行 → `/handoff` → `/neat` → `/compact` → 新会话 `/prime`

**协同 Skill**：
- `/prime` — 对称的会话开始仪式，会读取 handoff.md
- `/neat` — 同步三层知识，/handoff 之后可选调用
- `/reflection` — 如果有可复用经验，先 /reflection 再 /handoff

---

## 实例

### 触发：用户说"上下文快满了，准备 compact"

```
Step 1 盘点状态:
  git status → 3 个文件未提交（.claude/skills/handoff/SKILL.md 等）
  当前任务: 批量升级 Skill 系统，补充 trigger frontmatter + 新建 Skill

Step 2 识别隐性上下文:
  - 为什么不给 CTF skills 补 trigger：外部引入的 Skill，不改动原始内容
  - 为什么 sdd-riper 用 v1.1 而不是 v2.0：只补了契约结构，没改核心流程
  - 未完成决策：INDEX.md 是否需要更新 sdd-riper 条目描述

Step 3 写入 memory/handoff.md:
  ## 当前任务
  批量升级 Skill 系统：补 trigger frontmatter + 新建 handoff/spec-first Skill
  
  ## 已完成
  - sdd-riper/sdd-riper-light v1.1（补契约四要素 + trigger）
  - 7 个核心 Skill 补 trigger（vision-builder/plan-review/exa-research 等）
  - handoff/SKILL.md 创建完成
  
  ## 进行中
  - spec-first/SKILL.md：待创建
  - INDEX.md：待更新（注册 handoff/spec-first，更新 sdd-riper 条目）
  
  ## 下一步行动
  1. 创建 .claude/skills/spec-first/SKILL.md
  2. 更新 INDEX.md：注册 handoff/spec-first，更新 sdd-riper 条目描述
  3. git commit 所有变更
```

---

## 版本历史

- **v1.0.0** (2026-04-30): 初版，填补 /compact 前的生命周期空白，与 /prime 构成完整的上下文接力链

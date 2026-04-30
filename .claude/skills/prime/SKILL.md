---
name: prime
description: 会话预热仪式 - 新会话开始时快速建立项目上下文：读取 git 状态、检索相关记忆、加载项目状态，让 AI 从"知道自己在哪"开始工作
version: 1.0.0
license: MIT
metadata:
  category: system
  tags: [session-init, context-priming, memory-retrieval, onboarding, aha-loop]
  integration: [neat, reflection, knowledge-compounding, context-engineering]
trigger:
  - "/prime"
  - "新会话开始"
  - "帮我回顾一下项目状态"
  - "我们上次做到哪了"
  - "先了解一下项目"
---

# 会话预热 (Prime)

> 新会话的第一件事：用 3 分钟建立完整上下文，而不是用 30 分钟重新摸索。

## 设计动机

每次新会话，AI 都从"失忆"状态开始。常见的低效模式：

| 反模式 | 后果 |
|--------|------|
| 直接开始任务，不看项目状态 | 基于过时假设做决策，走弯路 |
| 让用户口头描述"上次做了什么" | 用户负担重，描述不完整 |
| 读取所有文档再开始 | 上下文浪费，信噪比低 |

本 Skill 的核心洞察来自 MemOS 的"记忆检索优先"原则：**先检索再行动，而非行动中发现**。

---

## What（输入/输出）

### 输入

| 输入项 | 必需 | 描述 |
|--------|------|------|
| **当前工作目录** | 是 | 自动从 CWD 推导 |
| **任务提示** | 否 | 用户可补充"今天想做 X" |
| **深度级别** | 否 | quick（默认）/ full |

### 输出

| 输出项 | 格式 | 描述 |
|--------|------|------|
| **项目状态摘要** | Markdown | git 状态 + 最近变更 + 未完成工作 |
| **相关记忆摘要** | Markdown | 与当前任务相关的 lessons/best-practices |
| **建议下一步** | 列表 | 基于上下文推断的 1-3 个行动建议 |

---

## How（三步执行流程）

### Step 1 — Git 状态快照（必做，~30秒）

```bash
git log --oneline -10          # 最近 10 次提交
git status                     # 当前工作区状态
git stash list                 # 是否有暂存的工作
git branch --show-current      # 当前分支
```

从输出中提取：
- 最近在做什么（commit messages）
- 是否有未提交的工作
- 是否在功能分支上

### Step 2 — 记忆检索（按需，~60秒）

**不要全量读取所有记忆文件**，按以下优先级精准检索：

```
1. 读取 memory/lessons-learned.md 最后 20 条（最近经验）
2. 如果用户提到了具体任务 → Grep memory/ 搜索相关关键词
3. 读取 .claude/context/index.json → 检查是否有匹配的历史问题
```

**检索判断框架**：
- 用户提到了具体技术/模块 → Grep 对应关键词
- 用户说"继续上次的" → 读取最近 5 条 lessons + git log
- 用户说"新任务" → 只读 git status，不加载历史记忆

### Step 3 — 状态摘要输出

输出格式（简洁，不超过 20 行）：

```markdown
## 会话预热摘要

### 项目状态
- 分支: main | 最近提交: feat(skills): 引入 reflection/skill-creator (2026-04-30)
- 未提交变更: [无 / 有 N 个文件]
- 暂存工作: [无 / 有]

### 相关记忆（检索到 N 条）
- [最相关的 1-3 条经验，一句话摘要]

### 建议下一步
1. [基于 git log 推断的最可能任务]
2. [如果有未提交变更，建议先处理]
3. [如果用户提到了具体任务，给出起点建议]
```

---

## When Done（验收标准）

### 必须满足

1. **git 状态已读取** — 知道当前分支、最近提交、未提交变更
2. **摘要 ≤20 行** — 不是全量文档转储，是精炼摘要
3. **有建议下一步** — 不只是描述状态，要给出行动方向

### 建议满足

- 检索到与当前任务相关的记忆（如果用户提供了任务提示）
- 识别出潜在的"未完成工作"（stash / 未提交变更 / 上次 commit 的 WIP 标记）

---

## What NOT（边界约束）

🚫 **不做的事**：

1. **不全量读取文档** — 不读取所有 docs/*.md，只读取 git 状态和精准检索的记忆
2. **不替代 /neat** — 本 Skill 是会话开始的"读"，/neat 是会话结束的"写"
3. **不做任务规划** — 只建议下一步，不展开完整计划（那是 plan-review 的职责）
4. **不加载无关 Skill** — 不预加载所有 Skill 定义，按需加载
5. **不超过 2 分钟** — 预热应该快，超时说明检索范围太宽

🚫 **不该触发的场景**：

- 会话中途（只在会话开始时有意义）
- 用户已经提供了完整上下文
- 单轮问答（无需建立项目上下文）

---

## 调用时机

| 场景 | 是否调用 | 说明 |
|------|---------|------|
| 新会话开始，准备继续上次工作 | ✅ 强烈建议 | 主用法 |
| 新会话开始，任务不明确 | ✅ 建议 | 帮助确定从哪里开始 |
| /compact 之后继续工作 | ✅ 建议 | 压缩后上下文丢失，需要重建 |
| 会话中途换任务 | ✅ 可选 | quick 模式快速切换上下文 |
| 会话中途，任务连续 | ❌ 不需要 | 上下文已有，无需重建 |

---

## 与现有体系的关系

```
新会话开始
    │
    ↓
[/prime]               ← 建立上下文（本 Skill）
    │
    ├── 读取 git 状态
    ├── 检索相关记忆
    └── 输出状态摘要 + 建议
    │
    ↓
执行任务
    │
    ↓
[/reflection]          ← 提炼经验
    │
    ↓
[/neat]                ← 同步三层知识
    │
    ↓
会话结束（下次 /prime 可读取这次沉淀的知识）
```

**完整会话生命周期**：`/prime` → 执行 → `/reflection` → `/neat` → 关闭

**协同 Skill / 文档**：
- `.claude/skills/neat/SKILL.md` — 对称的会话结束仪式
- `.claude/skills/reflection/SKILL.md` — 经验提炼，/prime 的知识来源
- `docs/CONTEXT-ENGINEERING-GUIDE.md` — 精准加载原则（本 Skill 的设计依据）
- `CLAUDE.md` 第九节 — 上下文检索协议（本 Skill 是其 Skill 化实现）

---

## 实例

### 触发：用户说"/prime"（新会话开始）

```
Step 1 Git 快照:
  git log --oneline -10 → 最近提交: feat(skills): 引入 reflection/skill-creator
  git status → 干净，无未提交变更
  git branch → main

Step 2 记忆检索:
  读取 lessons-learned.md 最后 20 条
  → 找到 3 条相关：Windows hooks 路径、/compact 前调用 /neat、两步链 Ingest

Step 3 输出摘要:
  ## 会话预热摘要
  
  ### 项目状态
  - 分支: main | 最近: feat(skills): 引入 reflection/skill-creator (2026-04-30)
  - 未提交变更: 无
  
  ### 相关记忆（3 条）
  - Windows hooks 必须用绝对路径（bash "C:\\path\\..."）
  - /compact 前调用 /neat 防止知识丢失
  - 两步链 Ingest：先 Grep 分析，再按策略写入
  
  ### 建议下一步
  1. 上次完成了 reflection/skill-creator Skill，可继续审计弱 Skill
  2. 或开始新任务（请描述）
```

---

## 版本历史

- **v1.0.0** (2026-04-30): 初版，融合 MemOS 记忆检索优先原则与本项目上下文工程准则

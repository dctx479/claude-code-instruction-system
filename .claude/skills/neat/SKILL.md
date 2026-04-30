---
name: neat
description: 任务收尾洁癖审查 - 同步 docs/CLAUDE.md/memory 三层知识体系，对治文档腐败与上下文投毒
version: 1.0.0
license: MIT
metadata:
  category: system
  tags: [cleanup, hygiene, knowledge-sync, context-engineering, self-evolution]
  integration: [self-evolution, context-engineering, sdd-riper, ralph-loop, autopilot]
trigger:
  - "/neat"
  - "整理一下"
  - "审查一下文档"
  - "存档"
  - "收尾"
---

# 洁癖 Skill (Neat)

> 一个任务的收尾仪式：把这次对话产生的新事实，准确同步到三层持久化知识中，让下次会话从干净的状态接着干。

## 设计动机

Agent 越用越笨，根因往往不是模型退化，而是**三层知识失同步**：

| 层级 | 服务对象 | 失同步症状 |
|------|---------|------------|
| `docs/` & `README` | 同事/下游/未来的自己 | 接入指南还指向已废弃接口 |
| `CLAUDE.md` & `agents/` | AI 自己 | 红线规则与已迭代的代码冲突 |
| `memory/` | AI 自己（跨会话） | 同一事实多条矛盾记忆并存 |

只清记忆（如 AutoDream）只解决了 1/3 的问题。本 Skill 针对**全部三层**做一次完整审查。

---

## What（输入/输出）

### 输入

| 输入项 | 必需 | 描述 |
|--------|------|------|
| **本次对话上下文** | 是 | 隐式输入，无需额外提供 |
| **项目根目录** | 是 | 自动从 CWD 推导 |
| **范围提示** | 否 | 用户可指定"只审查 docs/" 或"含跨项目同步" |

### 输出

| 输出项 | 格式 | 描述 |
|--------|------|------|
| **变更摘要** | Markdown | 修改了哪些文件、为什么改、改前→改后对照 |
| **未决项清单** | Markdown | 需要人工判断的事项（矛盾、跨项目影响等） |
| **文件实际变更** | Edit/Write | 直接落地到对应文件 |

---

## How（五步执行流程）

### Step 1 — 机械式盘点（强制）

不依赖记忆，逐项列出待审查文件：

```bash
# 列出所有 markdown 文件，逐一确认（不跳读）
docs/**/*.md
CLAUDE.md
agents/**/*.md
memory/lessons-learned.md
memory/best-practices.md
memory/error-patterns.md
README.md
.claude/skills/INDEX.md
```

**禁止"我记得已经读过"** — 跨会话场景下记忆不可信，必须用 Read 工具实际读取。

### Step 2 — 影响矩阵（识别需改什么）

对每个新事实问三个问题：

| 问题 | 触达层级 | 示例 |
|------|---------|------|
| 这是给**谁**看的事实？ | 用户/AI/跨会话 | 新增 API → docs；新增红线 → CLAUDE.md；踩坑经验 → memory |
| 是否**作废**了旧内容？ | 全部 | 旧接口下线 → 删除文档；技术栈切换 → 更新 CLAUDE.md |
| **跨项目**有依赖吗？ | 项目 A→B | 改了 A 的协议 → B 的对接文档也要改 |

输出一份 `<file_path> ← <change_type>` 的清单。

### Step 3 — 按层修改（顺序：docs → CLAUDE.md → memory）

**核心原则**：

> **合并优于追加，删除优于保留。**
> 一条过期的记忆，比没有记忆更糟糕 —— 没有记忆时 AI 知道自己不知道，会问；
> 过期记忆会让 AI 基于错误前提做事，且不会自检。

**修改顺序的理由**：
1. `docs/` 先改 — 影响外部协作，最严重
2. `CLAUDE.md` 次之 — 影响 AI 当前行为
3. `memory/` 最后 — 影响 AI 跨会话行为，受前两者约束

**操作要求**：
- 先 `Grep` 检查是否已有相似条目（去重协议，详见 `docs/KNOWLEDGE-COMPOUNDING-GUIDE.md`）
- 已有 → **合并/更新**现有条目（追加案例引用），不创建新条目
- 矛盾 → **保留更新版**，旧版加 `已废弃 (since YYYY-MM-DD)` 标记
- 完全过期且无引用 → **直接删除**，不留尸体

### Step 4 — 自检清单

修改完成后逐项核对：

- [ ] 新增的环境变量/配置是否在所有相关 runbook、CLAUDE.md、`.env.example` 中都出现？
- [ ] 删除的功能是否在 docs、agents 定义、memory 中都清理了引用？
- [ ] 是否有相对时间（"最近"、"上周"）残留？应替换为绝对日期。
- [ ] CLAUDE.md 总行数是否仍 ≤ 项目约束（接近 40K 应触发归档）。
- [ ] 矛盾条目是否都已合并或加废弃标记？
- [ ] 跨项目影响是否已识别？无法直接修改的应列入未决项清单。

### Step 5 — 输出变更摘要

格式如下，**必填字段**不可省略：

```markdown
## /neat 审查摘要 (YYYY-MM-DD HH:MM)

### 范围
- 触发: <用户消息或自动触发条件>
- 审查文件总数: N
- 实际修改: M

### 变更明细

| 文件 | 操作 | 原因 |
|------|------|------|
| docs/X.md | 更新接口章节 | 新增 v2 路由 |
| CLAUDE.md | 替换数据库引用 | SQLite → PostgreSQL |
| memory/lessons-learned.md | 合并 #L042 + #L067 | 同一现象重复记录 |
| memory/lessons-learned.md | 废弃 #L023 | 工具已不再使用 |

### 未决项（需人工确认）
- [ ] 跨项目 X 也引用了已废弃接口，建议同步更新
- [ ] 与 #L015 存在轻微措辞冲突，建议保留哪个？

### 验证
- JSON 文件: ✅ python -m json.tool 通过
- 链接检查: ✅ 引用文件均存在
- CLAUDE.md 规模: 12.3K / 40K
```

---

## When Done（验收标准）

### 必须满足

1. **零跳读** — Step 1 列出的所有文件均通过 Read 工具实际读取
2. **零冗余** — Grep 验证无新增条目与已有内容文本重复 ≥ 70%
3. **零悬空引用** — 删除的内容在其他文件中的引用同步清理
4. **变更摘要落地** — 输出清晰的改前→改后对照，用户可审计

### 建议满足

- 修改的 JSON 配置已通过 `python -m json.tool <file> > /dev/null` 校验
- 涉及 hooks/路径变更的，Windows 兼容性已检查
- 跨项目影响已显式列入未决项

---

## What NOT（边界约束）

🚫 **不做的事**：

1. **不修改代码逻辑** — 本 Skill 只同步文档/约束/记忆，不改 `.py/.ts/.go/.sh`
2. **不静默删除** — 任何删除必须出现在变更摘要中
3. **不批量删除** — 遵守 CLAUDE.md 第七节，逐文件处理，不允许 `rm *`
4. **不发明新事实** — 只整理对话中已出现的事实，不臆测
5. **不跨项目硬改** — 跨项目影响列入未决项，等用户确认
6. **不替代复盘** — /neat 是收尾整理，不替代 `lessons-learned` 的深度复盘流程

🚫 **不该触发的场景**：

- 单条简单问答（无新事实产生）
- 仍在任务进行中（应在收尾时调用）
- 用户明确要求"先不动文档"

---

## 调用时机

| 场景 | 是否调用 | 说明 |
|------|---------|------|
| 任务完成，准备关窗口 | ✅ 强烈建议 | 主用法，把对话转化为持久化资产 |
| `/compact` 之前 | ✅ 建议 | 防止压缩后丢失关键事实 |
| autopilot/ralph 自然结束 | ✅ 自动 | 钩入收尾阶段 |
| 解决重大 bug 后 | ✅ 建议 | 配合 `lessons-learned` 复盘流程 |
| 上下文 > 250K | ✅ 建议 | 配合"~250K 主动压缩"协议 |
| 单轮对话/纯查询 | ❌ 不需要 | 无新事实产生 |
| 任务中段 | ❌ 不需要 | 应让任务完整收尾再做 |

---

## 与现有体系的关系

```
本次对话产生新事实
        │
        ↓
   [/neat 触发]
        │
        ├── Step 1-2: 盘点 + 影响矩阵
        │
        ├── Step 3: 三层修改
        │   ├── docs/   ← 给人看
        │   ├── CLAUDE.md ← 给 AI 看（当前会话）
        │   └── memory/ ← 给 AI 看（跨会话）
        │
        ├── Step 4: 自检
        │
        └── Step 5: 变更摘要
                │
                ↓
       配合 KNOWLEDGE-COMPOUNDING
       的 Ingest 两步链做去重
                │
                ↓
       下一会话从干净状态开始
```

**协同 Skill / 文档**：
- `docs/KNOWLEDGE-COMPOUNDING-GUIDE.md` — 提供 Ingest 去重协议
- `docs/CONTEXT-ENGINEERING-GUIDE.md` — 解释为何需要定期审计
- `agents/ops/context-archivist.md` — 大规模归档（>10 个文件）时的进阶手段
- `CLAUDE.md` 第一节 — 自进化协议中的"半自动复盘"流程

---

## 实例（参考）

### 触发：用户说"/neat"

```
1. 盘点：读取 docs/*.md (12), CLAUDE.md, agents/*.md (28), memory/*.md (5)
2. 影响矩阵：
   - 本次新增: PostgreSQL 迁移
   - 影响: docs/architecture.md (改数据库章节), 
          CLAUDE.md (更新技术栈描述),
          memory/lessons-learned.md (新增踩坑记录)
3. 修改：
   - docs/architecture.md: SQLite → PostgreSQL，附迁移日期
   - CLAUDE.md: 删除 "使用 SQLite" 字样
   - lessons-learned.md: 新增 #L089 PostgreSQL 迁移踩坑
   - 同时检测到 #L023 (SQLite 优化) 已不再适用 → 加废弃标记
4. 自检：✅ 配置文件未涉及, ✅ 无相对时间残留
5. 摘要输出
```

---

## 版本历史

- **v1.0.0** (2026-04-30): 初版，基于社区 /neat 实践与本项目 KNOWLEDGE-COMPOUNDING-GUIDE 融合

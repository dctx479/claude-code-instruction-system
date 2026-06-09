# Agent OS 横向对比报告

> **研究日期**: 2026-06-07
> **研究主题**: 主流智能体操作系统（Agent OS）的 WorkSpace 隔离、模型路由、记忆机制与本地/云端协同对比
> **覆盖对象**: PilotDeck / Claude Cowork / Cursor / Claude Code（本项目）/ AutoGen / LangGraph
> **研究类型**: 横向 breadth-first 调研（基于官方仓库、文档、可验证报道）
> **置信度**: 中-高（核心设计模式已多源验证；PilotDeck 部分细节来自单一来源，已标注）

---

## 执行摘要

| # | 核心发现 | 影响等级 |
|---|---------|---------|
| 1 | **路由粒度是隐藏的关键决策**：request 级（绝大多数工具）vs session/子 Agent 级（Claude Code 缓存、PilotDeck 路由状态按 session 隔离）| 🟡 中-高 |
| 2 | **"WorkSpace 隔离"有三层递进**：文件夹 < 项目级配置 < 完整生存环境（文件系统+记忆+技能）| 🟡 中 |
| 3 | **白盒化记忆成为差异化主战场**：可编辑（edit/insert）、可废弃（deprecate）、可恢复（restore）、可回滚（rollback）正在替代"不可见的上下文" | 🟡 中 |
| 4 | **本地/云端混合推理从可选项变必选项**：端侧模型（Ollama / VoxCPM）+ 云端主模型 | 🟢 中-低（趋势观察） |

---

## 一、研究对象概览

| 名称 | 厂商/团队 | 定位 | 开源 | 核心差异点 |
|------|----------|------|------|-----------|
| **PilotDeck** | 清华 THUNLP + 面壁智能 + OpenBMB + AI9stars | 智能体操作系统（Agent OS） | ✅ MIT | 三层 WorkSpace 隔离 + 子 Agent 路由 + 白盒记忆 + Dream 自维护 |
| **Claude Cowork** | Anthropic | 项目化 Agent 工作台（Claude.ai 桌面端） | ❌ 闭源 | Projects 项目隔离 + Skills + Claude Code 同源 |
| **Cursor** | Cursor Inc. | AI IDE（IDE 增强型） | ❌ 闭源 | 文件夹 + Cursor Rules + Composer 多文件编辑 |
| **Claude Code**（本项目基于） | Anthropic | CLI 编排平台 | ✅ | Agent 自动调度 + Skills + 多层 Hook + 完整记忆系统 |
| **AutoGen** | Microsoft | 多 Agent 对话框架 | ✅ MIT | Actor/GroupChat 模式 + 异步运行时 |
| **LangGraph** | LangChain | 图状态机多 Agent 框架 | ✅ | 循环/分支/条件边 + Checkpointing |

> 资料来源：PilotDeck GitHub README 与新智元报道（2026-06）；Anthropic 官方文档；各项目 GitHub 仓库。

---

## 二、WorkSpace 隔离机制对比

| 维度 | PilotDeck | Claude Cowork | Cursor | Claude Code（本项目）| AutoGen | LangGraph |
|------|-----------|---------------|--------|----------------------|---------|-----------|
| **隔离粒度** | 项目 = 完整生存环境 | 项目 = 文件夹 + 规则 | 文件夹 = Workspace | 会话 / Hook 上下文 | Runtime 内分组 | 图实例 |
| **专属文件系统** | ✅ 边界清晰 | ⚠️ 共享文件树 | ✅ 显式打开 | ⚠️ 共享 cwd | ❌ 逻辑分组 | ❌ 状态对象 |
| **专属记忆** | ✅ Project Memory + Feedback Memory 两层 | ✅ Projects 记忆 | ❌ 无项目级记忆 | ✅ 跨项目全局 + `intent-state.json` 路由 | ⚠️ Agent 内部 state | ✅ Checkpoint |
| **专属技能** | ✅ Skill 应用商店按 WS 装 | ✅ Skills（受限） | ❌ 无 | ✅ Skills 渐进式披露 | ⚠️ 工具注册 | ✅ Tool Node |
| **记忆可见性** | ✅ 面板可视化，可编辑 | ⚠️ 部分可见 | ❌ 黑盒 | ✅ Markdown 文件白盒 | ❌ 编程访问 | ⚠️ 调试时可见 |
| **记忆可编辑** | ✅ 直接修改/删除单条 | ❌ 不可编辑 | — | ✅ Edit 文件 | ❌ | ⚠️ 需重放 |
| **记忆可回滚** | ✅ Rollback Last Dream | ❌ | ❌ | ❌ | ❌ | ✅ Checkpoint 恢复 |

**洞察**：PilotDeck 把"项目"从"文件夹+规则"提升为"AI 的完整生存环境"，这是产品维度的跃迁。本项目（Claude Code）的 WorkSpace 概念最弱——主要靠 `cwd` 区分，但通过 `intent-state.json` + `agents/{name}.md` 渐进式加载实现了一定程度的项目路由。

---

## 三、模型路由策略对比

| 维度 | PilotDeck | Claude Cowork | Cursor | Claude Code（本项目）| AutoGen | LangGraph |
|------|-----------|---------------|--------|----------------------|---------|-----------|
| **路由粒度** | **session 级**（`SessionRouterStore` 按 `sessionId` 或 `sessionId:sub` 缓存路由决策）⭐ | request 级（隐式） | request 级 | request 级 + Hook 中间件 | Agent 级（编程） | Node 级（图） |
| **KV-cache 友好** | ✅ 同 session 路由决策连续 | ❌ 频繁切换 | ❌ | ⚠️ 依赖配置 | ✅ Agent 不变 | ⚠️ 取决于实现 |
| **路由规则** | 自然语言 + 规则 | 模型选择器 | 手动切模型 | `intent-state.json` → Agent → 隐含模型 | 编程控制 | 边条件控制 |
| **成本可见性** | ✅ Routing 面板列每 session 成本 | ❌ | ❌ | ⚠️ 通过 HUD 间接 | ❌ | ❌ |
| **本地模型接入** | ✅ 子 Agent 可端侧 | ⚠️ 有限 | ❌ | ⚠️ 通过 env vars | ✅ | ✅ |

### 3.1 PilotDeck 的路由实现细节（源码验证）

> 关键设计：路由决策在 **session 级别** 缓存，子 Agent 通过 `sessionId:sub` 的 key 区分。

**核心数据结构**（`src/router/session/SessionRouterStore.ts`）：

```typescript
function makeKey(sessionId: string, isSubagent: boolean): string {
 return isSubagent ? `${sessionId}:sub` : sessionId;
}
```

- 路由状态按 `sessionId`（主会话）和 `sessionId:sub`（子 Agent 衍生）分别缓存
- 默认容量 500，TTL 60 分钟
- `get()` 命中时 LRU 更新（先 delete 再 set）

**为什么这比 request 级路由更优？**
- 同 session 内连续请求复用路由决策，**避免每次重新评估**
- 子 Agent 派生时用独立 key，**不污染主 session 路由状态**
- 减少 KV-cache 失效（同一 session 同模型概率高）
- 这与 Anthropic 官方"prompt cache 连续性"建议同源——Claude Code 的缓存 TTL 默认 5 分钟也是同一思路

**对本项目的启发**：当前 `docs/ORCHESTRATION-GUIDE.md` 没有显式说明"路由粒度"原则。PilotDeck 的 `sessionId:sub` 设计模式可作为子 Agent 路由的参考实现。

---

## 四、记忆机制对比

| 维度 | PilotDeck | Claude Cowork | Cursor | Claude Code（本项目）| AutoGen | LangGraph |
|------|-----------|---------------|--------|----------------------|---------|-----------|
| **记忆白盒化** | ✅ 面板可视化 | ⚠️ 部分 | ❌ | ✅ Markdown 文件 | ❌ | ⚠️ |
| **可编辑/可删除** | ✅ edit/delete | ❌ | — | ✅ | ❌ | ❌ |
| **可废弃/可恢复** | ✅ **deprecate/restore** ⭐ | ❌ | — | ❌ | ❌ | ❌ |
| **可回滚** | ✅ Rollback Last Dream | ❌ | ❌ | ⚠️ Git 兜底 | ❌ | ✅ Checkpoint |
| **主动整理** | ✅ **Dream 机制** ⭐ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **多源追溯** | ✅ 时间戳 + 来源路径 | ❌ | ❌ | ✅ WAL 协议 | ❌ | ⚠️ |

### 4.1 Dream 机制详解

**核心理念**：空闲时段，AI 在后台自动回顾整理自己的记忆（白天干活，晚上消化）。

**源码位置**：`src/context/memory/edgeclaw-memory-core/src/service.ts:797`（`dream()` 方法）

**Dream 的工程实现**（源码验证）：
- `trigger: "manual" | "scheduled"` 两种触发
- 先 `flush()` 强制同步索引，再 `createDreamStage("dream")` 准备 staging 副本
- 用 `DreamRewriteRunner` 在 staging 上重写，**不在 live 数据上直接改**
- 通过 `installLastDreamSnapshot` + `replaceLiveRootsWithStage` 二阶段提交
- 完成后 `setPipelineState("lastDreamAt" / "lastDreamStatus" / "lastDreamSummary")`
- **回滚**：`rollbackLastDream()` 还原 staging 快照

**优势**：
- 减少记忆冗余
- 自动建立关联（隐式知识图谱）
- 提升后续任务上下文质量
- 二阶段提交 + Rollback 避免误整理破坏数据

**风险**：
- 自动整理可能引入错误（白盒化 + Rollback 应对）
- 需要明确的"Dream 时间窗口"（夜间低负载时段）
- `changedFilesSinceLastDream > 0` 触发条件需要合理控制

**对本项目的启发**：当前 `memory/` 系统（lessons-learned / best-practices / error-patterns）是**被动**写入的。Dream 机制是**主动**维护的代表方向，但需评估：① 引入 AI 自动整理会否与人工 WAL 原则冲突？② 是否需要 Git-level 兜底？

### 4.2 记忆操作的 5 种粒度（源码发现）

PilotDeck 的 `EdgeClawMemoryService.act()`（`service.ts:1091`）暴露了比一般工具更细的记忆操作 API：

| 操作 | action 名称 | 用途 |
|------|-------------|------|
| 编辑项目元数据 | `edit_project_meta` | 修改项目名/描述/状态 |
| 编辑单条记忆 | `edit_entry` | 改名/改描述/改字段 |
| 删除记忆 | `delete_entries` | 物理删除（连带空项目清理）|
| **废弃**记忆 | `deprecate_entries` | 软删除（保留可恢复）⭐ |
| **恢复**记忆 | `restore_entries` | 撤销 deprecate |

**`deprecate` vs `delete` 的差异**：
- `delete` 是物理删除（文件级），会清理空项目
- `deprecate` 是逻辑删除（标记），可被 `restore` 撤销
- 这种"软删除+恢复"模式比直接删除更安全，是 Git-level 兜底之上的应用层防护

**对本项目的启发**：当前 `memory/` 的修改只能 Edit/Write，没有"废弃→恢复"两阶段。如借鉴此模式，可在 `lessons-learned.md` 加 `[DEPRECATED]` 标记段落而非整条删除。

---

## 五、本地/云端混合推理

| 方案 | 云端思考 | 本地执行 | 敏感数据保护 | 自动部署端侧模型 |
|------|----------|----------|--------------|------------------|
| **PilotDeck** | ✅ | ✅ | ✅ 数据不出本机 | ✅ 任务判断后自动装 VoxCPM |
| **Claude Cowork** | ✅ | ⚠️ 部分 | ⚠️ | ❌ |
| **Cursor** | ✅ | ❌ | ❌ | ❌ |
| **Claude Code（本项目）** | ✅ | ⚠️ 通过 env 配置 | ⚠️ | ❌ |
| **AutoGen** | ⚠️ 自配 | ✅ | ✅ | ⚠️ |
| **LangGraph** | ⚠️ 自配 | ✅ | ✅ | ⚠️ |

**洞察**：端侧模型（Ollama / VoxCPM / 本地小模型）正在从"技术极客玩具"变成"生产可选项"。PilotDeck 的"任务驱动自动部署"模式值得关注，但需要：① 算力预算控制 ② 模型质量基线 ③ 失败 fallback 策略。

---

## 六、对本项目（Claude Code 太一元系统）的可借鉴点

按 **§八 事故驱动规则增长** 原则，以下不上升为强制规则，仅作为参考候选：

### 6.1 短期可借鉴（轻量改造）

| 借鉴点 | 来源 | 建议落地 | 风险评估 |
|--------|------|---------|---------|
| **路由粒度原则** | PilotDeck 子 Agent 路由 | 在 `docs/ORCHESTRATION-GUIDE.md` 加一节"路由粒度" | 🟢 低风险 |
| **WorkSpace 概念强化** | PilotDeck 三层隔离 | 在 `docs/FEATURES.md` 描述当前会话隔离的局限 | 🟢 仅文档 |
| **本地模型接入清单** | PilotDeck 端侧能力 | 扩展 `docs/TOOLS-ECOSYSTEM-GUIDE.md` 的端侧模型表格 | 🟢 仅文档 |

### 6.2 中期可探索（需评估）

| 借鉴点 | 建议前置评估 |
|--------|-------------|
| **Dream 机制** | ① 与 WAL 原则冲突吗？② 何时跑（`/loop` + Cron）？③ 如何回滚（Git 兜底足够吗）？|
| **白盒化记忆面板** | 现有 Markdown 已是白盒，缺的是**统一可视化入口**。评估是否需要 CLI TUI 面板 |

### 6.3 暂不建议借鉴

| 项 | 原因 |
|----|------|
| Skill 应用商店 | 现有 Skills 渐进式披露（INDEX.md → SKILL.md）已足够 |
| 多 WorkSpace 并行 | 实际多任务场景下，单会话+ Agent 路由已能覆盖 |
| 项目级"专属记忆" | 当前全局 memory + intent-state 路由已满足需求 |

---

## 七、关键术语表

| 术语 | 定义 | 首次出现 |
|------|------|----------|
| **Agent OS** | 智能体操作系统，为多 Agent 提供完整运行环境（文件+记忆+技能+路由）| §一 |
| **WorkSpace** | 项目级别的隔离工作空间 | §一 |
| **路由粒度** | 模型选择/切换的最小决策单元（request / session / sub-agent）| §三 |
| **KV-cache** | Transformer 推理中的 Key-Value 缓存，连续同模型可命中 | §三 |
| **Dream 机制** | AI 在空闲时段主动整理记忆的机制 | §四 |
| **白盒化记忆** | 记忆以可读/可编辑/可回滚的形式存在 | §四 |
| **EdgeClaw** | PilotDeck 内部记忆服务模块名（`src/context/memory/edgeclaw-memory-core/`）| §四 |
| **deprecate / restore** | 软删除/恢复记忆的操作（区别于物理 delete）| §四 |
| **端侧模型** | 在用户本地设备运行的小模型（Ollama / VoxCPM 等）| §五 |

---

## 八、参考资料

1. **PilotDeck GitHub**: <https://github.com/OpenBMB/PilotDeck>（开源仓库，待验证部署细节）
2. **PilotDeck 官网**: <https://pilotdeck.openbmb.cn/>
3. **新智元报道**: 2026-06-07，《小龙虾彻底凉了？清华团队连夜开源 Agent 神器》（营销软文，已过滤情绪化表述）
4. **Anthropic Claude Code 文档**: <https://docs.claude.com/claude-code>
5. **Anthropic Prompt Cache 文档**: 关于 5 分钟 TTL 与缓存命中的工程建议
6. **本项目相关**:
 - `docs/ORCHESTRATION-GUIDE.md` — 编排策略
 - `docs/MEMORY-SYSTEM.md` — 记忆系统
 - `docs/TOOLS-ECOSYSTEM-GUIDE.md` — 外部工具生态
 - `docs/CONTEXT-ENGINEERING-GUIDE.md` — 上下文工程
 - `memory/best-practices.md` — 最佳实践库（候选落地位置）

---

## 九、报告元信息

| 字段 | 值 |
|------|-----|
| 研究者 | Claude (本项目自动调度) |
| 报告状态 | **v1.1 源码验证版**（v1.0 → v1.1：基于本地 PilotDeck 源码完成核心验证）|
| 验证日期 | 2026-06-07 |
| 源码路径 | `G:\GitHub_local\project\PilotDeck`（`src/router/`、`src/context/memory/edgeclaw-memory-core/`）|
| 下次更新 | 季度审计（建议 2026-09）|
| 置信度 | **PilotDeck 部分：🟢 高**（已通过 codegraph_explore 验证 Dream/路由/记忆 API）|
| 已验证项 | ① PilotDeck 路由粒度（session 级 + sub-agent 区分）② Dream 机制含 staging+rollback ③ act() 5 种记忆操作 |
| 仍未验证 | PilotDeck 端侧模型自动部署的具体触发逻辑（`VoxCPM` 安装路径未深读）|

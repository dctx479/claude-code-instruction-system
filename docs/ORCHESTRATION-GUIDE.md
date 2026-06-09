# 编排系统详细指南

> 执行指令（策略矩阵）见 `CLAUDE.md` 第二节。本文件提供详细架构和使用示例。

---

## Agent 层级架构

```
┌─────────────────────────────────────────────────────────┐
│                    Orchestrator (编排者)                 │
│  - 任务分解与分配                                        │
│  - 策略选择 (并行/串行/层级/协作)                        │
│  - 结果整合与质量控制                                    │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  Specialist   │ │  Specialist   │ │  Specialist   │
│  专家Agent    │ │  专家Agent    │ │  专家Agent    │
└───────────────┘ └───────────────┘ └───────────────┘
        │               │               │
        ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   Worker      │ │   Worker      │ │   Worker      │
│  执行Agent    │ │  执行Agent    │ │  执行Agent    │
└───────────────┘ └───────────────┘ └───────────────┘
```

---

## 渐进式披露机制

**核心理念**: 仅在需要时加载完整 Agent 定义，节省 60-80% Token。

```
启动时:
1. 读取 agents/INDEX.md 获取所有 Agent 元数据 (~100 tokens/agent)
2. 总成本: 25 agents × 100 tokens = 2.5K tokens

任务执行时:
1. 根据任务需求匹配相关 Agent
2. 按需加载完整定义 (~2-5k tokens/agent)
```

```markdown
# 查看所有可用 Agent
请读取 agents/INDEX.md

# 加载特定 Agent
需要使用 architect Agent，请读取 agents/architect.md
```

---

## 编排模式对比

| 模式 | 加速比 | 质量 | 成本 | 最佳场景 |
|------|--------|------|------|---------|
| PARALLEL | 3-5x | 中 | 中 | 独立子任务 |
| SEQUENTIAL | 1x | 高 | 低 | 依赖链任务 |
| HIERARCHICAL | 2-3x | 高 | 高 | 需专家指导 |
| COLLABORATIVE | 2.8-4.4x | 极高 | 高 | 跨领域问题 |
| COMPETITIVE | 1.5-2x | 最优 | 高 | 探索创新 |
| SWARM | 5-10x | 中 | 低 | 大规模批量 |
| **SDD-RIPER** | **2-4x** | **极高** | **中** | **中大型需求开发** |

完整模式定义: `workflows/orchestration/orchestration-patterns.md`
SDD-RIPER 详解: `docs/SDD-RIPER-GUIDE.md`
Agent 框架决策: `docs/AGENT-FRAMEWORK-DECISION.md`（Claude Code/LangGraph/CrewAI/DeerFlow 对比 + 框架选型）

---

## 策略自动选择决策树

```
规模>50? ─YES→ SWARM
    NO↓
需求开发? ─YES→ SDD-RIPER
    NO↓
独立任务? ─YES→ PARALLEL
    NO↓
强依赖? ─YES→ SEQUENTIAL
    NO↓
需专家? ─YES→ HIERARCHICAL
    NO↓
跨领域? ─YES→ COLLABORATIVE
    NO↓
探索性? ─YES→ COMPETITIVE
    NO↓
默认: PARALLEL
```

---

## 使用示例

### 示例1：复杂功能开发 → HIERARCHICAL

```
任务: "开发用户认证系统"
分析: 复杂度高 + 跨领域(前端+后端+数据库) + 需专家
→ 策略: HIERARCHICAL  预期加速: 2-3x

执行:
1. architect 设计架构 (30分钟)
2. 并行开发: 3个workers (2小时)
3. architect 审核整合 (30分钟)

总时间: 3小时 vs 单Agent 8小时
```

### 示例2：大规模迁移 → SWARM

```
任务: "将200个文件迁移到TypeScript"
分析: 规模 200 > 50 + 各文件独立
→ 策略: SWARM  预期加速: 5-10x

执行:
- 10个haiku workers并行
- 4批处理 (50文件/批)

总时间: 20分钟 vs 单Agent 3.3小时
```

### 示例3：性能优化 → COMPETITIVE

```
任务: "优化API性能，探索最佳方案"
分析: 探索性 + 质量优先
→ 策略: COMPETITIVE

执行:
- 3个agents并行提出不同方案
- 自动评估各方案性能
- 选择最佳并提供备选

结果: 找到5x性能提升方案
```

### 示例4：中大型需求开发 → SDD-RIPER

```
任务: "开发用户权限管理系统"
分析: 中大型需求 + 需要质量可控 + 需要知识沉淀
→ 策略: SDD-RIPER  预期加速: 2-4x

执行:
1. Pre-Research: 生成 CodeMap + Context Bundle (1小时)
2. Research: 调研现状，锁定事实 (2小时)
3. Innovate: 设计 2-3 个方案，人类拍板 (1小时)
4. Plan: 原子级规划，人类审批 (1小时)
5. Execute: AI 按图施工 (4小时)
6. Review: 三角验证 + QA 系统 (1小时)

总时间: 10小时 vs 单Agent无规划 20-30小时
质量: Bug率降低 18-37%
```

### 示例5：大批量分析 → SWARM + 持久化规划文件

```
任务: "分析恒生科技指数 30 只成分股，逐个生成投资研报"
分析: 规模 30 > 10 + 各股票独立 + 单任务耗时长(20-30分钟/股)
→ 策略: SWARM + 持久化规划文件
```

**核心问题**: 批量处理 >50 个同质任务时，AI 上下文窗口逐步压缩，
导致后期任务质量下降（跳过分析阶段、格式不统一、遗忘约束条件）。

**解决方案**: 用 3 个持久化 markdown 文件作为 AI 的"外部记忆"：

| 文件 | 用途 | 防止的问题 |
|------|------|-----------|
| `task_plan.md` | 完整清单 + 约束条件 + 里程碑 | 忘记任务规范 |
| `findings.md` | 累积发现、交叉对比数据 | 每次从零开始 |
| `progress.md` | 当前进度、下一步、已知问题 | 重复或遗漏 |

**执行流程**:
```
1. 创建 task_plan.md（列出所有股票 + 分析约束 + 质量标准）
2. /ralph "按 task_plan.md 逐个执行 /stock-research"
3. 每完成 1 只 → 更新 progress.md（勾选完成）+ 追加 findings.md
4. 每轮开始前 → 重读 task_plan.md 的约束条件，防止漂移
```

**与现有工具链的关系**:

| 工具 | 管理什么 | 适用粒度 |
|------|---------|---------|
| `ralph-state.json` | 执行循环（何时停） | 进程级 |
| `task_plan.md` | 任务规范（做什么不忘） | 认知级 |
| `plan-scoped-memory` | 计划知识隔离 | 项目级 |
| `issues-execute CSV` | 结构化 Issue 闭环 | Issue 级 |

**选择指南**:
- 任务已有明确 acceptance_criteria → `/plan-to-issues` + `/issues-execute`
- 任务是开放式批量处理（分析、研究） → `task_plan.md` + `/ralph`
- 两者可组合：先用 task_plan.md 梳理，再转为 issues CSV 执行

**已验证案例**: 127 只科技股批量分析（恒生科技 30 + 科创 50 + 创业板 50 + 金龙 98），
使用持久化规划文件后里程碑清晰、一步一步完成、后期质量不下降。

---

## 子代理并行时的 Skills 加载机制

**核心问题**: 多个子代理并行执行时，每个子代理是否能正确加载所需 Skills？

### Skills 加载层级规范

| 层级 | Skills 加载策略 | 说明 |
|------|----------------|------|
| **Orchestrator** | 全量 INDEX.md | 需要全局视野来分配任务和 Skills |
| **Specialist** | 按任务匹配 INDEX + 加载对应 SKILL.md | 由 Orchestrator 在 prompt 中指定 |
| **Worker** | 继承 Specialist 指定的 SKILL.md | 只加载与当前任务直接相关的 Skills |

### Orchestrator 职责增强

分发任务时，Orchestrator 必须在子代理 prompt 中:

1. **指定所需 Skills**: 明确告知子代理需要读取哪些 SKILL.md
2. **传递关键约束**: 即使子代理未读完整 SKILL.md，prompt 中也包含核心规则摘要
3. **负向路由**: 告知子代理不需要加载的 Skills（减少上下文浪费）

```
# 子代理 prompt 模板
你负责 {task_description}。
执行前，请先读取以下 Skills:
1. {skill_path_1} — 原因: {why_needed}
2. {skill_path_2} — 原因: {why_needed}

你不需要读取: {excluded_skills}（与当前任务无关）
```

### 长上下文下的路由失效防护

当上下文超过 ~300-400k tokens（见 CONTEXT-ENGINEERING-GUIDE.md），Skills 路由匹配约束力可能下降。防护:

1. **主动压缩**: ~250k tokens 时 `/compact` 并附上未来方向和路由提醒
2. **路由强化**: 关键路由规则写入 CLAUDE.md（固定上下文，每次都加载）
3. **Subagent 隔离**: 大量中间输出交给 Subagent，避免撑大主上下文

> 详见: `memory/best-practices.md` BP-018（子代理 Skills 加载）、BP-019（路由失效防护）

---

## 路由器 Agent 设计模式

**来源**: "我给 AI 装了 80 多个 Skill，最后只保留了这一个" 实践总结

### 核心理念

路由器不是工具，而是一个**分发层**。你只需要跟路由器说话，它来调度具体的 Agent/Skill。

```
用户请求
    ↓
路由器 Agent（理解意图 + 匹配能力）
    ↓
分发给对应的 Specialist Agent
    ↓
Specialist 调用具体 Skill/Tool 执行
    ↓
结果返回用户
```

### 路由器 vs 直接调用

| 维度 | 直接调用 80 个 Skill | 路由器模式 |
|------|---------------------|-----------|
| 用户认知负担 | 需要记住每个 Skill 名称和用法 | 只需说意图 |
| 上下文消耗 | 每次加载所有 Skill 说明（~46K tokens） | 按需加载（~600 tokens INDEX + ~2K 单个 Skill） |
| 调用一致性 | Agent 可能选错 Skill 或跳过 | 路由器统一判断，不遗漏 |
| 扩展性 | 新增 Skill 需要更新所有 prompt | 新增 Skill 只更新路由表 |

### 路由器的三大职责

#### 1. 意图识别

将用户自然语言请求映射到具体的任务类型：

```
"这篇我想写，做成小红书图文" → 内容创作任务 → 运营 Agent
"帮我把这个素材整理进知识库" → 知识管理任务 → 知识库 Agent
"上次那个选题推进到哪了" → 任务追踪 → 系统 Agent
```

#### 2. 能力路由

根据任务类型选择最合适的 Agent/Skill 组合：

| 任务类型 | 路由目标 | 理由 |
|---------|---------|------|
| 选题调研 | 运营 Agent + deep-research Skill | 需要外部搜索 + 内容策划能力 |
| 代码审查 | code-reviewer Agent | 专注代码质量和安全 |
| 架构设计 | architect Agent | 需要系统设计经验 |
| 文献整理 | literature-manager Agent + Zotero MCP | 学术研究专用工具链 |

#### 3. 上下文传递

确保被路由的 Agent 获得足够的上下文：

```
路由器传递给 Specialist:
- 原始用户请求
- 已识别的意图类型
- 需要加载的 Skills 清单
- 关键约束（deadline、格式要求等）
```

### 实现方式

#### 方式 1: Intent-State 文件路由（当前系统）

```
UserPromptSubmit Hook → 分析意图 → 写入 intent-state.json
    ↓
Claude 读取 intent-state.json → 加载对应 Agent
    ↓
Agent 执行任务
```

优点：零认知负担，全自动  
缺点：依赖 Hook 系统，调试较复杂

#### 方式 2: 显式路由器 Agent

创建独立的 `router.md` Agent 定义：

```markdown
# Router Agent

## 职责
你是路由器，负责理解用户意图并分发到正确的 Agent。

## 工作流程
1. 分析用户请求，识别任务类型
2. 查询 agents/INDEX.md，匹配最合适的 Agent
3. 如果需要多个 Agent 协作，选择编排模式（PARALLEL/SEQUENTIAL/HIERARCHICAL）
4. 构造子 Agent 的 prompt（包含任务描述 + 需要的 Skills + 约束）
5. 调用 Agent 工具启动子 Agent
6. 整合结果返回用户

## 路由决策表
[插入具体的路由规则]
```

优点：显式可控，易于调试和扩展  
缺点：需要用户手动触发（或通过 @router 前缀）

#### 方式 3: 混合模式（推荐）

- 常见场景：自动路由（intent-state.json）
- 复杂场景：用户显式调用 @router 让路由器做决策
- 调试场景：直接 @{agent-id} 跳过路由

### 路由器设计的关键原则

1. **单一入口，统一分发** — 用户不需要知道底层有多少个 Agent/Skill
2. **负向路由同样重要** — 明确告诉 Agent"不需要加载哪些 Skill"
3. **路由器本身要轻量** — 不承担具体执行，只做分发决策
4. **可观测性** — 每次路由决策都应该可追溯（日志/状态文件）
5. **失败优雅降级** — 路由匹配失败时，回退到通用 orchestrator 而非报错

### 与现有系统的关系

| 机制 | 作用 | 与路由器的关系 |
|------|------|--------------|
| intent-state.json | 自动意图识别 | 是路由器的输入源 |
| agents/INDEX.md | Agent 元数据索引 | 是路由器的查询表 |
| Agent 工具 | 启动子 Agent | 是路由器的执行手段 |
| Skills INDEX.md | Skill 元数据索引 | 路由器用于分配 Skill 给 Agent |

### 案例：多 Agent 路由实战

**场景**: 用户说"帮我写一篇关于 AI Agent 的技术博客"

#### 传统方式（无路由器）
```
用户 → Claude（加载所有 80 个 Skill 说明）
     → Claude 自己判断该用哪些 Skill
     → 可能选错，可能遗漏，可能冲突
```

#### 路由器方式
```
用户 → Router Agent
     ↓ 意图识别：技术写作任务
     ↓ 能力匹配：
     ├─ 需要 deep-research（调研 AI Agent 现状）
     ├─ 需要 paper-writing-assistant（结构化写作）
     └─ 需要 frontend-design（如果需要配图）
     ↓ 编排决策：SEQUENTIAL（先调研，再写作，最后配图）
     ↓ 分发执行：
     ├─ Step 1: research agent + deep-research skill
     ├─ Step 2: paper-writing agent + 调研结果
     └─ Step 3: design agent（如果需要）
     ↓
结果返回用户（完整博客 + 配图）
```

### 验证方法

对比有无路由器的体验差异：
- Token 消耗：路由器模式应节省 60-80%
- 任务成功率：路由器模式不应漏掉必要的 Skill
- 用户认知负担：用户是否需要记住 Skill 名称？

> 相关最佳实践: `memory/best-practices.md` BP-024（能力路由优先于工具堆叠）

---

## 路由粒度原则

> 来源：`docs/reports/AGENT-OS-LANDSCAPE-2026.md` § 路由粒度对比研究

### 核心问题

**路由粒度**决定了模型切换的频率，直接影响 KV-cache 命中率和推理成本。

### 三种路由粒度

| 粒度 | 决策频率 | KV-cache 友好性 | 成本优化 | 适用场景 |
|------|---------|----------------|----------|----------|
| **request 级** | 每次请求评估 | ❌ 频繁切换，缓存失效 | ❌ 重复计算 | 简单任务分发 |
| **session 级** | 每个会话固定 | ✅ 同 session 连续请求命中 | ✅ 减少路由开销 | 对话式任务 |
| **sub-agent 级** | 子 Agent 独立路由 | ✅ 主/子分离，不互相污染 | ✅ 精细控制 | 复杂多 Agent 协作 |

### PilotDeck 的 session 级路由实现

**核心设计**：路由决策按 `sessionId` 缓存，子 Agent 用 `sessionId:sub` 区分。

```typescript
function makeKey(sessionId: string, isSubagent: boolean): string {
  return isSubagent ? `${sessionId}:sub` : sessionId;
}
```

**优势**：
- 同 session 内连续请求复用路由决策，避免每次重新评估
- 子 Agent 派生时用独立 key，不污染主 session 路由状态
- 减少 KV-cache 失效（同一 session 同模型概率高）

### 本项目当前实现

**现状**：
- 路由粒度：**request 级** + Hook 中间层
- 路由机制：`intent-state.json` → Agent 定义 → 隐含模型
- 缓存策略：依赖 Anthropic Prompt Cache（TTL 5 分钟）

**潜在优化**：
1. **session 级路由缓存**：在 `~/.claude/intent-state.json` 增加 `lastRouteDecision` 字段，同 session 复用
2. **sub-agent 路由隔离**：子 Agent 启动时写入 `intent-state-{task_id}.json`，避免污染主会话
3. **路由决策 TTL**：设置路由缓存过期时间（建议 10-30 分钟），过期后重新评估

### 最佳实践

**原则 1：优先 session 级路由**
- 对话式任务（如调试、代码审查）应在 session 开始时确定 Agent，中途不切换
- 避免"每个 message 都重新路由"的反模式

**原则 2：子 Agent 路由隔离**
- 并行执行的子 Agent 应有独立路由状态
- 参考 PilotDeck 的 `sessionId:sub` 模式

**原则 3：关联 Prompt Cache TTL**
- Anthropic Prompt Cache 默认 TTL 5 分钟
- 路由缓存 TTL 应 ≥ Prompt Cache TTL，避免缓存失效后仍用旧路由

### 验证方法

**监控指标**：
- 路由切换频率（次/会话）
- KV-cache 命中率（通过 claude-tap 观察）
- 平均每会话 token 消耗

**目标**：
- 路由切换频率 ≤ 1 次/会话（单一任务场景）
- KV-cache 命中率 ≥ 80%（同 session 连续请求）

> 相关：`memory/best-practices.md` BP-024（能力路由）、`docs/CONTEXT-ENGINEERING-GUIDE.md`（缓存优化）

---

核心功能: 实时监控 → 异常检测 → 自动恢复 → 结果整合 → 质量验证

- Agent无响应 → 自动重启或切换备用
- 任务超时 → 自动重试或分解
- 高错误率 → 升级模型或调整策略

详见: `workflows/orchestration/orchestration-monitor.md`

---

## 能力编排五模式速查（BP-025 补充）

> 详见 `memory/best-practices.md` BP-025 上下文注入模式。

### 怎么选：先想清楚出发点

| 出发点 | 判断方法 | 推荐模式 |
|--------|---------|---------|
| **有具体问题要解决** | 任务目标清晰，有明确完成标准 | 从问题出发 → 模式一/五 |
| **有工具想看能干什么** | 已知可用能力，探索如何组合 | 从工具出发 → 模式二/三/四 |

**经验法则**：大多数场景下，模式一（固定流程）和模式五（专业门禁）最常用；模式二/三/四是特定场景的补充。

### 五种设计模式

| 模式 | 适用场景 | 核心约束 | 对应 BP |
|------|---------|---------|---------|
| **模式一：顺序执行** | 固定流程，每步依赖上一步结果 | 步间验证 + 回退方案 | Agent 协作协议 |
| **模式二：多工具协同** | 跨平台、跨系统任务 | 分阶段、阶段间检查数据传递 | 能力路由（BP-024） |
| **模式三：迭代打磨** | 质量敏感输出（报告、文案） | 设定停止条件（如"3 轮或通过检查"） | SDD-RIPER QA 循环 |
| **模式四：条件路由** | 同需求但条件不同（如存储选型） | 决策树 + 选择理由告知用户 | 能力路由（BP-024） |
| **模式五：嵌入专业知识** | 合规要求或专业门槛场景 | 专业判断固化为标准流程，AI 严格按规则执行 | 安全审查门禁（BP-022） |

### 怎么选

```
出发点判断：
  有具体问题 → 从问题出发选模式
  有工具想用 → 从工具出发组合流程

大多数场景：
  简单固定流程        → 模式一（最常用）
  有专业门槛/合规     → 模式五（次常用）
  跨平台协作          → 模式二
  质量敏感            → 模式三
  同类需求条件不同    → 模式四
```

### 与编排策略矩阵的关系

`CLAUDE.md` 第二节的编排策略矩阵（SEQUENTIAL/PARALLEL/HIERARCHICAL 等）是从**组织结构**维度描述 Agent 协作；这 5 种模式是从**任务特征**维度描述能力流程。两者互补：

| 任务维度 | 编排策略（谁协作谁） | 设计模式（怎么串接工具） |
|---------|-------------------|----------------------|
| 独立子任务 | PARALLEL | 模式一或模式四 |
| 依赖链任务 | SEQUENTIAL | 模式一（+ 回退方案）|
| 跨系统查询 | HIERARCHICAL | 模式二（+ Context Provider）|
| 质量敏感 | COLLABORATIVE | 模式三（+ 停止条件）|
| 合规场景 | SPECIALIST | 模式五（+ 安全门禁）|

---

## 手动触发命令

```bash
/orchestrate   # 启动智能编排模式
/parallel      # 强制使用并行策略
/swarm         # 强制使用群体策略
```

Agent定义: `agents/orchestrator.md`, `agents/ops/strategy-selector.md`

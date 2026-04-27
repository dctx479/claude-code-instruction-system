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

## 监控与异常处理

核心功能: 实时监控 → 异常检测 → 自动恢复 → 结果整合 → 质量验证

- Agent无响应 → 自动重启或切换备用
- 任务超时 → 自动重试或分解
- 高错误率 → 升级模型或调整策略

详见: `workflows/orchestration/orchestration-monitor.md`

---

## 手动触发命令

```bash
/orchestrate   # 启动智能编排模式
/parallel      # 强制使用并行策略
/swarm         # 强制使用群体策略
```

Agent定义: `agents/orchestrator.md`, `agents/ops/strategy-selector.md`

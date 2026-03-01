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

完整模式定义: `workflows/orchestration-patterns.md`

---

## 策略自动选择决策树

```
规模>50? ─YES→ SWARM
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

---

## 监控与异常处理

核心功能: 实时监控 → 异常检测 → 自动恢复 → 结果整合 → 质量验证

- Agent无响应 → 自动重启或切换备用
- 任务超时 → 自动重试或分解
- 高错误率 → 升级模型或调整策略

详见: `workflows/orchestration-monitor.md`

---

## 手动触发命令

```bash
/orchestrate   # 启动智能编排模式
/parallel      # 强制使用并行策略
/swarm         # 强制使用群体策略
```

Agent定义: `agents/orchestrator.md`, `agents/strategy-selector.md`

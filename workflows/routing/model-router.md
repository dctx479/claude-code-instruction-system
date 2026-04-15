# Model Router 工作流

> 智能模型选择系统 - 根据任务特征自动选择最优模型

## 概述

Model Router 分析任务复杂度和特征，自动选择最合适的 Claude 模型，在成本和质量之间取得最佳平衡。

## 架构

```
任务输入
    │
    ▼
┌─────────────────────────┐
│   Complexity Scorer     │
│   复杂度评分器          │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   Feature Analyzer      │
│   特征分析器            │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   Model Selector        │
│   模型选择器            │
└───────────┬─────────────┘
            │
    ┌───────┼───────┐
    ▼       ▼       ▼
┌──────┐ ┌──────┐ ┌──────┐
│ Opus │ │Sonnet│ │Haiku │
└──────┘ └──────┘ └──────┘
```

## 模型特性对比

| 模型 | 复杂度阈值 | Token成本 | 速度 | 适用场景 |
|------|-----------|-----------|------|----------|
| **Opus** | ≥8 | 高 | 慢 | 架构设计、复杂决策、关键代码 |
| **Sonnet** | 4-7 | 中 | 中 | 常规开发、代码审查、调试 |
| **Haiku** | 1-3 | 低 | 快 | 简单查询、格式化、搜索 |

## 复杂度评分系统

### 评分维度 (总分 10)

```python
def calculate_complexity(task):
    score = 0

    # 1. 代码行数 (0-2分)
    if task.lines_of_code > 500:
        score += 2
    elif task.lines_of_code > 100:
        score += 1

    # 2. 跨文件依赖 (0-2分)
    if task.files_involved > 10:
        score += 2
    elif task.files_involved > 3:
        score += 1

    # 3. 领域复杂度 (0-2分)
    if task.involves_architecture:
        score += 2
    elif task.involves_multiple_systems:
        score += 1

    # 4. 决策权重 (0-2分)
    if task.is_critical_decision:
        score += 2
    elif task.requires_tradeoffs:
        score += 1

    # 5. 创新程度 (0-2分)
    if task.is_novel_solution:
        score += 2
    elif task.requires_research:
        score += 1

    return score
```

### 复杂度指标详解

| 指标 | 低 (0) | 中 (1) | 高 (2) |
|------|--------|--------|--------|
| 代码行数 | <100 | 100-500 | >500 |
| 文件数量 | 1-3 | 3-10 | >10 |
| 系统涉及 | 单系统 | 多模块 | 跨系统 |
| 决策影响 | 局部 | 模块级 | 架构级 |
| 创新程度 | 常规 | 需调研 | 全新方案 |

## 特征分析器

### 任务类型识别

```python
def analyze_features(task):
    features = {
        "type": detect_task_type(task),
        "domain": detect_domain(task),
        "urgency": detect_urgency(task),
        "risk_level": assess_risk(task),
        "context_size": estimate_context(task)
    }
    return features
```

### 任务类型映射

| 任务类型 | 默认模型 | 复杂度修正 |
|----------|----------|-----------|
| 架构设计 | Opus | +2 |
| 代码审查 | Sonnet | +0 |
| Bug 修复 | Sonnet | +0 |
| 简单查询 | Haiku | -2 |
| 格式化 | Haiku | -3 |
| 重构 | Sonnet | +1 |
| 安全审计 | Opus | +2 |

## 模型选择算法

```python
def select_model(task):
    # 计算基础复杂度
    base_score = calculate_complexity(task)

    # 分析特征并调整
    features = analyze_features(task)
    adjusted_score = base_score + get_type_modifier(features["type"])

    # 考虑上下文限制
    if features["context_size"] > 150000:
        # 大上下文需要更强模型
        adjusted_score += 1

    # 考虑风险级别
    if features["risk_level"] == "high":
        adjusted_score += 2

    # 最终选择
    if adjusted_score >= 8:
        return "opus"
    elif adjusted_score >= 4:
        return "sonnet"
    else:
        return "haiku"
```

## 成本优化策略

### 1. 渐进式升级

```
先用 Haiku 尝试
    │
    ▼
┌───────────┐
│ 成功?     │
└─────┬─────┘
      │
  YES │  NO
      │   │
      ▼   ▼
  完成  升级到 Sonnet
            │
            ▼
       ┌───────────┐
       │ 成功?     │
       └─────┬─────┘
             │
         YES │  NO
             │   │
             ▼   ▼
         完成  升级到 Opus
```

### 2. 任务分解

将复杂任务分解为:
- 简单子任务 → Haiku
- 中等子任务 → Sonnet
- 关键决策 → Opus

### 3. 缓存复用

对于重复性任务，缓存之前的模型选择结果。

## 集成点

### 与 Ralph 集成

Ralph 循环中的每次迭代可能使用不同模型:

```
迭代 1: 分析任务 → Sonnet
迭代 2: 执行简单修复 → Haiku
迭代 3: 验证结果 → Haiku
迭代 4: 复杂重构 → Opus
```

### 与 Intent Detector 集成

Intent 信息影响模型选择:

```python
def adjust_for_intent(score, intent):
    intent_modifiers = {
        "architect": +3,
        "security": +2,
        "debug": +1,
        "review": +0,
        "document": -1,
        "git": -2
    }
    return score + intent_modifiers.get(intent, 0)
```

### 与 Orchestrator 集成

Orchestrator 可以为不同 Agent 指定不同模型:

```yaml
agents:
  architect:
    model: opus
    reason: "架构决策需要最高质量"
  worker-1:
    model: haiku
    reason: "简单文件操作"
  worker-2:
    model: sonnet
    reason: "中等复杂度实现"
```

## 监控与调优

### 模型使用统计

```json
{
  "daily_stats": {
    "opus": {
      "calls": 5,
      "tokens": 50000,
      "cost": "$2.50",
      "success_rate": "100%"
    },
    "sonnet": {
      "calls": 50,
      "tokens": 200000,
      "cost": "$3.00",
      "success_rate": "96%"
    },
    "haiku": {
      "calls": 200,
      "tokens": 100000,
      "cost": "$0.25",
      "success_rate": "85%"
    }
  }
}
```

### 优化建议

基于统计数据自动生成优化建议:

```
建议:
1. 代码格式化任务降级到 Haiku (节省 40% 成本)
2. 安全审计升级到 Opus (提高 20% 准确率)
3. 简单查询批量处理 (节省 30% API 调用)
```

## 配置选项

```json
{
  "model_router": {
    "enabled": true,
    "default_model": "sonnet",
    "cost_optimization": true,
    "progressive_upgrade": true,
    "thresholds": {
      "opus": 8,
      "sonnet": 4,
      "haiku": 0
    },
    "overrides": {
      "architect": "opus",
      "security-analyst": "opus"
    },
    "max_retries": 2
  }
}
```

## 使用示例

### 自动选择

```markdown
任务: "修复登录页面的 CSS 布局问题"

分析结果:
- 代码行数: ~50 (0分)
- 文件数: 1 (0分)
- 领域: 前端 (0分)
- 决策: 局部 (0分)
- 创新: 常规 (0分)

总分: 0 → 选择 Haiku
```

### 强制指定

```bash
# 强制使用 Opus
/model opus

# 临时使用 Haiku
/model haiku "快速检查代码格式"
```

## 故障排除

### 模型选择不准确

1. 检查复杂度评分逻辑
2. 调整任务类型修正系数
3. 添加新的特征维度

### 成本过高

1. 启用渐进式升级
2. 增加任务分解
3. 调低复杂度阈值

### 质量不满意

1. 升级默认模型
2. 调高关键任务的风险级别
3. 禁用成本优化

## 相关文档

- 复杂度评分器: `workflows/routing/complexity-scorer.md`
- 性能监控: `agents/ops/performance-monitor.md`
- 成本优化: `agents/ops/auto-optimizer.md`

---

## 智能化增强

### 历史学习机制

基于历史任务的成功/失败率动态调整模型选择阈值:

```python
def update_thresholds(history):
    """
    每日统计:
    - 如果 Haiku 在某类任务上 success_rate < 80%
      → 该类任务的 Haiku 阈值 +1（更容易升级到 Sonnet）
    - 如果 Sonnet 在某类任务上 success_rate = 100% 且 cost 偏高
      → 该类任务的 Sonnet 阈值 -1（更容易降级到 Haiku）
    """
    for task_type, stats in history.items():
        if stats["haiku_success_rate"] < 0.80:
            thresholds[task_type]["haiku_ceiling"] += 1
        if stats["sonnet_success_rate"] == 1.0 and stats["avg_complexity"] < 5:
            thresholds[task_type]["sonnet_floor"] -= 1
```

**数据来源**: `memory/agent-performance.md` 中的任务执行记录。

**调整频率**: 每日自动分析，阈值变化幅度限制为 ±1/天（防止剧烈波动）。

### 渐进式升级模式

"先便宜后贵"策略 — 节省 30-50% token 成本:

```
Step 1: Haiku 尝试（成本最低）
  ├─ 成功且质量达标 → 完成 ✓
  └─ 失败或质量不足 → Step 2

Step 2: Sonnet 尝试（中等成本）
  ├─ 成功且质量达标 → 完成 ✓
  └─ 失败或质量不足 → Step 3

Step 3: Opus 执行（最高成本，最终保障）
  └─ 完成 ✓
```

**适用条件**:
- 任务复杂度未知或评估不确定
- 批量任务中同质性高（先用低模型探路，确认难度后固定）
- 成本敏感场景

**不适用**:
- 复杂度明确 ≥8 的任务（直接 Opus，避免浪费低模型的 token）
- 安全审计等高风险任务（直接使用最强模型）
- 时间紧迫场景（重试有延迟成本）

### 多模型共识模式

高风险决策使用多模型投票:

```
架构决策 → 同时请求 Opus + Sonnet
  ├─ 两者一致 → 采纳（高置信度）
  ├─ 两者矛盾 → 人工裁决 + 记录分歧原因
  └─ 部分一致 → 采纳一致部分，矛盾部分人工裁决
```

**适用**: 架构选型、安全审计结论、数据库 Schema 设计等不可逆决策。

**成本**: 约 2x 单模型，但降低决策风险。建议仅在高影响决策时使用。

### 节省预估

基于上述三种机制的综合节省:

| 机制 | 预估节省 | 说明 |
|------|---------|------|
| 历史学习 | 10-15% | 避免高模型处理简单任务 |
| 渐进式升级 | 20-30% | 多数任务在低模型即完成 |
| 多模型共识 | -50~100% 增加 | 仅用于高风险，频率低 |
| **综合** | **约 30-50% 节省** | 批量任务场景更显著 |

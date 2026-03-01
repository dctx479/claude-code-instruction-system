# Complexity Scorer 工作流

> 任务复杂度评分系统 - Model Router 的核心评分引擎

## 概述

Complexity Scorer 负责分析任务特征并计算复杂度分数，为 Model Router 提供决策依据。

## 评分模型

### 总分计算

```
总分 = 基础分 + 特征修正分 + 上下文修正分
```

范围: 0-10 分

### 评分维度

```
┌─────────────────────────────────────────────────────┐
│                 Complexity Score                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │ Code Scale   │  │ Dependency   │  │ Domain   │  │
│  │ 代码规模     │  │ 依赖复杂度   │  │ 领域     │  │
│  │ (0-2分)      │  │ (0-2分)      │  │ (0-2分)  │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐                │
│  │ Decision     │  │ Innovation   │                │
│  │ 决策权重     │  │ 创新程度     │                │
│  │ (0-2分)      │  │ (0-2分)      │                │
│  └──────────────┘  └──────────────┘                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 评分细则

### 1. 代码规模 (Code Scale)

```python
def score_code_scale(task):
    lines = task.estimated_lines_of_code

    if lines > 500:
        return 2, "Large scale implementation"
    elif lines > 100:
        return 1, "Medium scale implementation"
    else:
        return 0, "Small scale implementation"
```

| 代码行数 | 分数 | 说明 |
|----------|------|------|
| >500 | 2 | 大规模实现 |
| 100-500 | 1 | 中等规模 |
| <100 | 0 | 小规模 |

### 2. 依赖复杂度 (Dependency)

```python
def score_dependency(task):
    files = task.files_involved
    external_deps = task.external_dependencies

    score = 0

    # 文件数量
    if files > 10:
        score += 1
    elif files > 3:
        score += 0.5

    # 外部依赖
    if external_deps > 5:
        score += 1
    elif external_deps > 2:
        score += 0.5

    return min(2, score), f"{files} files, {external_deps} deps"
```

| 指标 | 低 | 中 | 高 |
|------|---|---|---|
| 文件数 | 1-3 | 3-10 | >10 |
| 外部依赖 | 0-2 | 2-5 | >5 |

### 3. 领域复杂度 (Domain)

```python
def score_domain(task):
    if task.involves_architecture:
        return 2, "Architecture level"

    if task.involves_multiple_systems:
        return 1.5, "Cross-system"

    if task.involves_database_schema:
        return 1, "Database schema"

    if task.involves_security:
        return 1.5, "Security sensitive"

    return 0, "Single domain"
```

| 领域特征 | 分数 |
|----------|------|
| 架构级别 | 2 |
| 跨系统集成 | 1.5 |
| 安全相关 | 1.5 |
| 数据库Schema | 1 |
| 单一领域 | 0 |

### 4. 决策权重 (Decision)

```python
def score_decision(task):
    if task.is_breaking_change:
        return 2, "Breaking change"

    if task.affects_production:
        return 1.5, "Production impact"

    if task.requires_tradeoffs:
        return 1, "Tradeoff decisions"

    if task.is_reversible:
        return 0, "Reversible change"

    return 0.5, "Normal decision"
```

| 决策类型 | 分数 |
|----------|------|
| 破坏性变更 | 2 |
| 生产环境影响 | 1.5 |
| 需要权衡取舍 | 1 |
| 普通决策 | 0.5 |
| 可逆变更 | 0 |

### 5. 创新程度 (Innovation)

```python
def score_innovation(task):
    if task.is_novel_algorithm:
        return 2, "Novel algorithm"

    if task.requires_research:
        return 1.5, "Research required"

    if task.new_technology:
        return 1, "New technology"

    if task.has_examples:
        return 0, "Has examples"

    return 0.5, "Standard approach"
```

| 创新程度 | 分数 |
|----------|------|
| 全新算法 | 2 |
| 需要调研 | 1.5 |
| 新技术栈 | 1 |
| 有参考示例 | 0 |

## 特征修正

### 任务类型修正

```python
TYPE_MODIFIERS = {
    "architecture_design": +2,
    "security_audit": +2,
    "performance_optimization": +1,
    "code_refactoring": +1,
    "bug_fix": +0,
    "code_review": +0,
    "documentation": -1,
    "formatting": -2,
    "simple_query": -2
}
```

### 上下文修正

```python
def context_modifier(task):
    modifier = 0

    # 大上下文需要更强模型
    if task.context_tokens > 150000:
        modifier += 1
    elif task.context_tokens > 100000:
        modifier += 0.5

    # 关键路径任务
    if task.is_on_critical_path:
        modifier += 1

    # 时间敏感
    if task.is_urgent:
        modifier -= 0.5  # 快速响应优先

    return modifier
```

## 完整评分流程

```python
def calculate_complexity(task):
    # 基础评分
    scores = {
        "code_scale": score_code_scale(task),
        "dependency": score_dependency(task),
        "domain": score_domain(task),
        "decision": score_decision(task),
        "innovation": score_innovation(task)
    }

    # 计算基础分
    base_score = sum(s[0] for s in scores.values())

    # 任务类型修正
    type_mod = TYPE_MODIFIERS.get(task.type, 0)

    # 上下文修正
    ctx_mod = context_modifier(task)

    # 最终分数 (限制在 0-10)
    final_score = max(0, min(10, base_score + type_mod + ctx_mod))

    return {
        "final_score": final_score,
        "base_score": base_score,
        "type_modifier": type_mod,
        "context_modifier": ctx_mod,
        "breakdown": scores,
        "recommended_model": select_model(final_score)
    }

def select_model(score):
    if score >= 8:
        return "opus"
    elif score >= 4:
        return "sonnet"
    else:
        return "haiku"
```

## 评分示例

### 示例 1: 简单 Bug 修复

```
任务: "修复按钮点击无响应的问题"

评分:
- 代码规模: 0 (预计 <50 行)
- 依赖: 0 (1个文件)
- 领域: 0 (单一前端)
- 决策: 0 (可逆)
- 创新: 0 (有参考)

基础分: 0
类型修正: 0 (bug_fix)
上下文修正: 0

最终分: 0 → Haiku
```

### 示例 2: API 重构

```
任务: "重构用户认证 API，支持 OAuth 2.0"

评分:
- 代码规模: 1 (预计 200 行)
- 依赖: 1 (5个文件, 3个外部库)
- 领域: 1.5 (安全相关)
- 决策: 1 (需要权衡)
- 创新: 1 (新技术)

基础分: 5.5
类型修正: +1 (refactoring)
上下文修正: 0

最终分: 6.5 → Sonnet
```

### 示例 3: 微服务架构设计

```
任务: "设计订单系统微服务架构"

评分:
- 代码规模: 2 (>500 行设计文档+代码)
- 依赖: 2 (>10个服务)
- 领域: 2 (架构级别)
- 决策: 2 (破坏性变更)
- 创新: 1.5 (需要调研)

基础分: 9.5
类型修正: +2 (architecture_design)
上下文修正: +1 (关键路径)

最终分: 10 (上限) → Opus
```

## 校准与优化

### 定期校准

每周根据实际效果校准评分参数:

```python
def calibrate_scores(history):
    """
    分析历史数据，调整评分参数
    """
    for task in history:
        predicted_model = task.predicted_model
        actual_success = task.was_successful
        actual_quality = task.quality_score

        # 如果 Haiku 频繁失败，提高阈值
        if predicted_model == "haiku" and not actual_success:
            # 分析失败原因，调整评分
            pass

        # 如果 Opus 用于简单任务，降低阈值
        if predicted_model == "opus" and task.complexity < 5:
            # 可能过度使用 Opus
            pass
```

### 反馈循环

```
执行 → 结果 → 评估 → 调整 → 执行
                ↑           │
                └───────────┘
```

## 相关文档

- Model Router: `workflows/routing/model-router.md`
- 性能监控: `agents/ops/performance-monitor.md`
- 自动优化: `agents/ops/auto-optimizer.md`

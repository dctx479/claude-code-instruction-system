---
name: parallel-explore
description: Git Worktree 并行探索技能，为多方案决策创建独立工作树，完整实现后通过标准化评估选择最优方案
license: MIT
metadata:
  category: development
  tags:
  - git-worktree
  - exploration
  - parallel
  - decision-making
  - architecture
  source: Aha-Loop methodology
  version: 1.0.0
  trigger:
  - /parallel-explore
  - 对比多个方案
  - 技术选型
  - 不知道选哪个方案
  - 并行探索
disable-model-invocation: true
---

# Parallel Explore Skill

> 基于 Aha-Loop 方法论的并行探索机制，通过 Git Worktree 为每个候选方案创建独立工作环境，
> 实现完整的"探索-评估-合并"循环，确保技术决策的质量。

## 契约化设计

### What (输入/输出)

**输入**:
- 决策点描述（需要探索的技术选择）
- 候选方案列表（2-4 个可行方案）
- 评估维度和权重（可选，有默认值）

**输出**:
- 每个方案的完整实现（独立 worktree）
- 标准化评估报告 `EXPLORATION_RESULT.md`
- 最佳方案推荐及合并建议
- 清理后的干净代码库

### When Done (验收标准)

1. 每个方案都有完整可运行的实现
2. 每个方案都包含相关测试
3. 生成了标准格式的评估报告
4. 评估报告包含 10 分制多维度打分
5. 最佳方案已合并到主分支（如用户确认）
6. 所有临时 worktree 已清理

### What NOT (边界约束)

- 不跳过任何方案的实现（即使看起来不太可能）
- 不故意破坏某个方案以支持另一个
- 不在评估完成前删除任何 worktree
- 不修改非探索相关的代码
- 单次探索不超过 4 个方案（复杂度限制）
- 不在没有测试的情况下声称方案完成

---

## 核心理念

### "无限计算资源"原则

每个方案都要认真尝试：
- 不要因为"直觉不好"而敷衍某个方案
- 失败的探索也有价值（记录为什么不行）
- 客观评估比快速决策更重要

### 适用场景

| 场景 | 示例 | 推荐方案数 |
|------|------|-----------|
| 架构模式选择 | 微服务 vs 单体 vs 模块化单体 | 2-3 |
| 库/框架对比 | React vs Vue vs Svelte | 2-4 |
| 算法选择 | 不同数据结构或算法实现 | 2-3 |
| API 设计 | REST vs GraphQL vs gRPC | 2-3 |
| 性能优化策略 | 缓存层 vs 查询优化 vs 分库分表 | 2-4 |
| 状态管理 | Redux vs Zustand vs Jotai | 2-3 |

### 不适用场景

- 简单的代码修改（无需探索）
- 已有明确最佳实践的场景
- 时间紧急无法完整实现的情况
- 方案差异仅在配置层面

---

## 工作流程

### Phase 1: 识别决策点

```markdown
## 决策点定义

**问题**: [需要做出的技术决策]
**背景**: [为什么需要探索]
**约束条件**:
- [约束1]
- [约束2]

**候选方案**:
1. **方案A**: [描述]
   - 预期优势: [列表]
   - 潜在风险: [列表]
2. **方案B**: [描述]
   - 预期优势: [列表]
   - 潜在风险: [列表]
3. **方案C**: [描述] (可选)
   - 预期优势: [列表]
   - 潜在风险: [列表]
```

### Phase 2: 创建 Git Worktree

```bash
# 为每个方案创建独立工作树
git worktree add ../explore-option-a -b explore/option-a
git worktree add ../explore-option-b -b explore/option-b
git worktree add ../explore-option-c -b explore/option-c

# 验证创建成功
git worktree list
```

**目录结构**:
```
parent-directory/
├── main-project/           # 原始项目
├── explore-option-a/       # 方案 A 工作树
├── explore-option-b/       # 方案 B 工作树
└── explore-option-c/       # 方案 C 工作树
```


## Extended procedure

Read [references/extended-guide.md](references/extended-guide.md) for the remaining modes, examples, and checks. Resource paths in that guide are relative to this skill directory.

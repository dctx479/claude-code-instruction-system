---
name: parallel-explore
description: Git Worktree 并行探索技能，为多方案决策创建独立工作树，完整实现后通过标准化评估选择最优方案
version: 1.0.0
license: MIT
metadata:
  category: development
  tags: [git-worktree, exploration, parallel, decision-making, architecture]
  source: Aha-Loop methodology
trigger:
  - "/parallel-explore"
  - "对比多个方案"
  - "技术选型"
  - "不知道选哪个方案"
  - "并行探索"
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

### Phase 3: 完整实现

每个方案必须完成：

1. **核心功能实现** - 不是原型，是完整实现
2. **单元测试** - 覆盖主要逻辑
3. **集成测试** - 验证与现有系统的兼容性
4. **文档** - 实现说明和使用方法
5. **性能基准** - 如果性能是考量因素

**实现检查清单**:
```markdown
### 方案 X 实现状态

- [ ] 核心功能完整实现
- [ ] 单元测试通过
- [ ] 集成测试通过（如适用）
- [ ] 代码符合项目规范
- [ ] 无明显性能问题
- [ ] 实现文档完成
```

### Phase 4: 生成评估报告

在每个 worktree 中创建 `EXPLORATION_RESULT.md`:

```markdown
# 方案探索结果: [方案名称]

## 元信息
- **探索分支**: explore/option-x
- **开始时间**: YYYY-MM-DD HH:mm
- **完成时间**: YYYY-MM-DD HH:mm
- **探索者**: Claude Code / [用户名]

## 实现摘要
[简要描述实现内容和方法]

## 评估维度 (10分制)

### 1. 可维护性 (maintainability): X/10
**评分理由**:
- [具体说明]
- [代码组织评估]
- [可读性评估]

### 2. 可读性 (readability): X/10
**评分理由**:
- [命名规范]
- [代码结构清晰度]
- [注释充分性]

### 3. 可测试性 (testability): X/10
**评分理由**:
- [测试覆盖率]
- [模块隔离度]
- [mock 难度]

### 4. 性能 (performance): X/10
**评分理由**:
- [时间复杂度]
- [空间复杂度]
- [实测性能数据]

### 5. 扩展性 (extensibility): X/10
**评分理由**:
- [添加新功能的难度]
- [修改现有功能的影响范围]

### 6. 集成复杂度 (integration): X/10
**评分理由**:
- [与现有代码的兼容性]
- [迁移成本]
- [依赖影响]

## 综合评分
| 维度 | 权重 | 得分 | 加权得分 |
|------|------|------|----------|
| maintainability | 20% | X | X*0.2 |
| readability | 15% | X | X*0.15 |
| testability | 15% | X | X*0.15 |
| performance | 20% | X | X*0.2 |
| extensibility | 15% | X | X*0.15 |
| integration | 15% | X | X*0.15 |
| **总计** | 100% | - | **Y.YY** |

## 优势
1. [优势1]
2. [优势2]
3. [优势3]

## 劣势
1. [劣势1]
2. [劣势2]
3. [劣势3]

## 风险与缓解
| 风险 | 严重程度 | 缓解措施 |
|------|----------|----------|
| [风险1] | 高/中/低 | [措施] |
| [风险2] | 高/中/低 | [措施] |

## 实现亮点
[记录实现过程中发现的有价值的技术点或创新]

## 失败记录（如有）
[记录尝试但失败的方法，以及失败原因]

## 建议
- 是否推荐采用: 是/否/有条件
- 采用条件: [如果是"有条件"，说明条件]
- 后续优化点: [列表]
```

### Phase 5: 客观评估

**多评估者机制**（可选但推荐）:

```markdown
## 综合评估

### 评估者 1: [角色/视角]
| 方案 | 综合得分 | 推荐排名 |
|------|----------|----------|
| A | 7.8 | 2 |
| B | 8.2 | 1 |
| C | 6.5 | 3 |

### 评估者 2: [角色/视角]
| 方案 | 综合得分 | 推荐排名 |
|------|----------|----------|
| A | 8.0 | 1 |
| B | 7.9 | 2 |
| C | 6.8 | 3 |

### 最终决策
**推荐方案**: B
**决策理由**:
1. [理由1]
2. [理由2]
3. [理由3]

**备选方案**: A
**备选理由**: [如果 B 遇到问题，为什么 A 是好的替代]
```

### Phase 6: 合并最佳方案

```bash
# 切换到主分支
cd main-project
git checkout main

# 合并最佳方案
git merge explore/option-b --no-ff -m "feat: adopt option-b for [决策点]

Exploration results:
- Option A: 7.8/10
- Option B: 8.2/10 (selected)
- Option C: 6.5/10

See EXPLORATION_RESULT.md for details"

# 保存探索记录到 memory（可选）
cp ../explore-option-b/EXPLORATION_RESULT.md memory/explorations/

# 清理 worktree
git worktree remove ../explore-option-a
git worktree remove ../explore-option-b
git worktree remove ../explore-option-c

# 删除探索分支
git branch -d explore/option-a
git branch -d explore/option-b
git branch -d explore/option-c
```

---

## CLI 命令

### 启动探索

```bash
# 启动并行探索
./scripts/parallel-explorer.sh start "决策点描述" \
  --options "option-a:描述A" "option-b:描述B" "option-c:描述C"

# 带自定义权重
./scripts/parallel-explorer.sh start "数据库选型" \
  --options "postgresql" "mongodb" "mysql" \
  --weights "performance:30,maintainability:25,cost:20,scalability:25"
```

### 查看状态

```bash
# 查看当前探索状态
./scripts/parallel-explorer.sh status

# 输出示例:
# Exploration: 数据库选型
# Status: In Progress
#
# Options:
#   [x] postgresql - Implemented (explore/postgresql)
#   [~] mongodb - In Progress (explore/mongodb)
#   [ ] mysql - Pending
#
# Worktrees:
#   ../explore-postgresql (clean)
#   ../explore-mongodb (modified: 5 files)
```

### 完成评估

```bash
# 标记某个方案完成并生成评估报告
./scripts/parallel-explorer.sh evaluate option-a

# 批量评估所有已完成方案
./scripts/parallel-explorer.sh evaluate --all
```

### 对比方案

```bash
# 生成对比报告
./scripts/parallel-explorer.sh compare

# 输出格式化对比表
./scripts/parallel-explorer.sh compare --format markdown > COMPARISON.md
```

### 合并方案

```bash
# 合并最佳方案
./scripts/parallel-explorer.sh merge option-b

# 合并并清理
./scripts/parallel-explorer.sh merge option-b --cleanup
```

### 清理

```bash
# 清理所有探索工作树和分支
./scripts/parallel-explorer.sh cleanup

# 仅清理工作树（保留分支）
./scripts/parallel-explorer.sh cleanup --keep-branches
```

---

## 与太一元系统集成

### 与 Orchestrator 集成

Parallel Explore 可以作为 COMPETITIVE 策略的增强实现：

```markdown
## 编排计划

### 策略选择: COMPETITIVE (Parallel Explore)

当 strategy-selector 推荐 COMPETITIVE 策略时：
1. 检查是否适合 Parallel Explore
2. 如果是架构/库/算法选择 → 使用 Parallel Explore
3. 如果是实现方式探索 → 使用标准 COMPETITIVE

### 触发条件
- 任务描述包含: "选择", "对比", "评估", "哪个更好"
- innovation_level: "exploratory"
- 涉及技术决策
```

### 与 Autopilot 集成

```markdown
## Autopilot 工作流集成

### Planning 阶段
识别需要探索的决策点，标记为 "exploration-required"

### Specification 阶段
为每个探索点定义候选方案和评估标准

### Development 阶段
1. 普通任务 → Ralph Loop 执行
2. 探索任务 → Parallel Explore 执行
   - 创建 worktree
   - 并行实现各方案
   - 评估并选择最佳
   - 合并到主分支

### QA 阶段
验证最终合并的方案符合规范
```

### 与 strategy-selector 关系

```json
{
  "recommended_strategy": "COMPETITIVE",
  "enhancement": "parallel-explore",
  "confidence": 0.85,
  "reasoning": "技术选型任务，需要实际实现来验证可行性",
  "parallel_explore_config": {
    "max_options": 3,
    "evaluation_dimensions": ["performance", "maintainability", "integration"],
    "require_tests": true
  }
}
```

---

## 最佳实践

### Do's

1. **完整实现每个方案** - 不要只写原型
2. **客观评估** - 不预设结论
3. **记录失败** - 失败的探索也是知识
4. **保留评估报告** - 沉淀到 memory/
5. **清理干净** - 合并后删除所有临时分支和工作树

### Don'ts

1. **不要敷衍不喜欢的方案** - 每个方案同等对待
2. **不要跳过测试** - 测试是验证的关键
3. **不要评估前删除 worktree** - 需要随时回顾
4. **不要修改主分支** - 所有探索在独立 worktree
5. **不要超过 4 个方案** - 复杂度会失控

### 评估偏见检查

评估时问自己：
- 我是否因为熟悉某技术而高估它？
- 我是否因为实现困难而低估某方案？
- 评分是否基于客观证据？
- 是否有我忽略的重要维度？

---

## 配置参数

```yaml
parallel_explore_config:
  max_options: 4                    # 最大方案数
  worktree_prefix: "explore-"      # worktree 目录前缀
  branch_prefix: "explore/"        # 分支前缀

  evaluation_dimensions:
    maintainability: 0.20          # 可维护性权重
    readability: 0.15              # 可读性权重
    testability: 0.15              # 可测试性权重
    performance: 0.20              # 性能权重
    extensibility: 0.15            # 扩展性权重
    integration: 0.15              # 集成复杂度权重

  requirements:
    require_tests: true            # 必须有测试
    require_docs: true             # 必须有文档
    min_score_to_consider: 6.0     # 最低可考虑分数

  cleanup:
    auto_cleanup: false            # 合并后自动清理
    keep_evaluation_reports: true  # 保留评估报告
    archive_to_memory: true        # 归档到 memory/
```

---

## 参考资源

- **Aha-Loop 方法论**: 基于完整实现的探索式开发
- **Git Worktree 文档**: https://git-scm.com/docs/git-worktree
- **太一元系统 COMPETITIVE 策略**: `workflows/orchestration/orchestration-patterns.md`
- **Strategy Selector**: `agents/ops/strategy-selector.md`

---

## 更新日志

### 2026-02-04
- 初始版本创建
- 定义契约化设计框架
- 实现完整工作流程
- 添加 CLI 命令说明
- 集成太一元系统编排

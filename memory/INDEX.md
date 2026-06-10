# Memory 文件索引

> 8 个知识文件，各司其职。写入前先查索引，找准归属，避免重复。

---

## 文件清单

| 文件 | 条目类型 | 写入时机 | 当前规模 |
|------|---------|---------|---------|
| [best-practices.md](#best-practicesmd) | 策展型 BP 条目 | 经验验证≥3次后晋升 | 46 个 BP（BP-001～BP-046） |
| [lessons-learned.md](#lessons-learnedmd) | 任务经验（UNVERIFIED） | 任务完成复盘时 | 持续增长 |
| [error-patterns.md](#error-patternsmd) | 错误模式和修复 | 发现新错误模式时 | 持续增长 |
| [agent-performance.md](#agent-performancemd) | Agent 性能数据 | 性能监控报告后 | 定期更新 |
| [optimization-history.md](#optimization-historymd) | 优化操作历史 | 系统配置变更后 | 按时间序 |
| [knowledge-strategy.md](#knowledge-strategymd) | 知识管理策略 | 策略调整时 | 相对稳定 |
| [active-worktrees.md](#active-worktreesmd) | 活跃 Worktree 状态 | Worktree 创建/关闭时 | 动态维护 |
| [performance-reports/TEMPLATE.md](#performance-reportsmd) | 性能报告模板 | 报告生成参考 | 静态模板 |

---

## best-practices.md

**定位**：策展型最佳实践条目库，门槛最高的知识层。

**写入条件**（VFM 评分通过）：
- Value 价值分 ≥ 7/10
- Frequency 复用频次 ≥ 3 次
- Maintenance 维护成本 ≤ 3/10

**条目格式**：
```markdown
### BP-XXX: 标题

**核心问题**: [一句话描述解决什么问题]
**做法**: [具体可执行的方法]
**效果**: [预期收益，可量化更好]
**相关**: [关联的 BP 编号]
```

**当前分布**：
- BP-001～BP-009：Agent 编排
- BP-010～BP-019：Skills 系统
- BP-020～BP-029：上下文工程
- BP-030～BP-039：开发规范
- BP-040～BP-046：协作与质量

**下一个 BP**：BP-047

---

## lessons-learned.md

**定位**：任务经验的第一层存储，允许未验证。

**写入时机**：任务完成复盘时（WAL 原则：先写后回复）

**条目格式**：
```markdown
## [YYYY-MM-DD] 经验标题 #ID [UNVERIFIED]

### 问题描述
### 根因分析
### 解决方案
### 验证方法
### 案例引用（必填）
```

**晋升路径**：lessons-learned → (验证≥3次) → best-practices  
**废弃标记**：`[DEPRECATED YYYY-MM-DD]` + 替代方案说明

---

## error-patterns.md

**定位**：错误模式库，防止重复犯错。

**写入时机**：发现新的错误模式，或已有模式复现（更新 Recurrence-Count）

**条目格式**：
```markdown
## Pattern-Key: 错误类型

**症状**: [错误表现]
**根因**: [深层原因]
**修复**: [解决步骤]
**预防**: [预防措施]
**Recurrence-Count**: N
```

**与 best-practices 的关系**：error-patterns 是问题视角（避免什么），best-practices 是方案视角（做什么）。

---

## agent-performance.md

**定位**：Agent 执行数据，支持性能监控和优化决策。

**写入时机**：`/performance-report` 命令执行后，或 performance-monitor Agent 报告后

**记录内容**：
- Agent 成功率（按类型）
- 平均执行时间
- Token 消耗统计
- 常见失败原因

---

## optimization-history.md

**定位**：系统配置优化历史，支持回滚和归因。

**写入时机**：
- hooks 配置变更
- CLAUDE.md 重大更新
- Skills/Agent 调整
- 编排策略切换

**条目格式**（按时间序）：
```markdown
## [YYYY-MM-DD] 优化标题

**变更**: [做了什么]
**原因**: [为什么做]
**效果**: [结果如何]
**回滚命令**: [如何撤销]
```

---

## knowledge-strategy.md

**定位**：知识管理元策略，定义知识如何流转。

**写入时机**：知识管理框架调整时（相对稳定，不频繁写入）

**内容**：
- 三层知识架构（docs/CLAUDE.md/memory）
- 知识流转规则
- 审计周期定义
- Skill 提取触发条件

---

## active-worktrees.md

**定位**：活跃 Git Worktree 的状态追踪。

**写入时机**：
- `/worktree-create` 创建时追加
- `/worktree-cleanup` 关闭时更新状态
- 定期核对实际状态

**条目格式**：
```markdown
## worktree-name

**路径**: .claude/worktrees/xxx
**分支**: feature/xxx
**创建时间**: YYYY-MM-DD
**状态**: active / merged / abandoned
**任务**: [关联任务描述]
```

---

## performance-reports/

**定位**：性能报告存储目录，TEMPLATE.md 为生成模板。

**写入时机**：`/performance-report` 执行时自动生成带时间戳的报告文件

---

## 写入决策树

```
有新的知识要记录？
    ↓
是否是错误/失败模式？
    YES → error-patterns.md（记录症状+根因+修复）
    NO ↓
是否有 ≥3 次验证的通用实践？
    YES → best-practices.md（VFM 评分通过后）
    NO ↓
是否是本次任务的新发现？
    YES → lessons-learned.md（标注 UNVERIFIED）
    NO ↓
是否是系统配置变更？
    YES → optimization-history.md
    NO → 可能不需要写入，先确认是否可复用
```

---

## 季度审计清单（每季度一次）

- [ ] lessons-learned: 标注 UNVERIFIED 超过 90 天的条目，评估是否晋升或废弃
- [ ] best-practices: 对 BP 进行 VFM 评分，低分条目考虑降级
- [ ] error-patterns: 清理 Recurrence-Count=1 且超过 180 天未触发的条目
- [ ] agent-performance: 分析趋势，提取优化建议
- [ ] optimization-history: 归档 180 天前的历史记录

---

**更新日志**:
- 2026-06-10: 创建 memory/INDEX.md

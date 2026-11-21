---
name: observability
description: AI 思维日志可观测性系统，实时记录推理过程、决策点和执行状态到 logs/ai-thoughts.md，帮助人类理解 AI 决策过程
license: MIT
metadata:
  category: system
  tags:
  - observability
  - logging
  - transparency
  - decision-tracking
  - aha-loop
  inspired_by: Aha-Loop
  version: 1.1.0
  trigger:
  - /observe
  - /thought
  - /log-decision
  - 记录思考过程
  - 思维日志
  - 决策理由
disable-model-invocation: true
---

# Observability Skill - AI 思维日志

> **核心理念**: 让 AI 的推理过程透明可追溯，帮助人类理解决策、发现问题、建立信任

## What（输入/输出）

**输入**：任务描述 + 触发场景（任务开始/决策点/错误/完成）

**输出**：结构化日志条目追加到 `logs/ai-thoughts.md`，包含 Context/Decision/Confidence 三要素

## How（判断框架）

记录时机的选择原则：
1. **决策点必记**：凡是有 2+ 个可行方案需要选择，必须写 DecisionPoint 条目
2. **错误必记**：遇到任何错误，先写 Error 条目再修复（不能只修复不记录）
3. **不确定性必记**：置信度 <70% 时写 Uncertainty 条目，标注需要用户确认的内容
4. **任务边界必记**：TaskStart 和 TaskComplete 是强制的，其余类型按需

**日志类型选择**：
- 有多个方案 → `DecisionPoint`
- 遇到报错 → `Error` + `Recovery`
- 不确定某个假设 → `Uncertainty`
- 意外发现影响方向 → `Discovery`
- 其他推理过程 → `InnerThought`

## When Done（验收标准）

- 每个任务有 TaskStart 和 TaskComplete 条目
- 所有关键决策有 DecisionPoint 条目（含 Chosen + Reason + Tradeoffs）
- 错误有 Error 条目，且包含 Recovery 结果
- 日志文件路径固定为 `logs/ai-thoughts.md`

## What NOT（边界约束）

🚫 不做的事：
1. 不记录琐碎操作（读文件、运行测试等无决策的步骤）
2. 不替代 `reflection` Skill（observability 是实时流水日志，reflection 是事后提炼）
3. 不替代 `context-archivist`（日志是原始记录，归档是结构化沉淀）
4. 不在日志中写结论性建议（日志记录过程，建议写在任务输出中）

---

## 核心参考

## 何时使用此 Skill

当以下情况发生时自动激活：

| 触发词/场景 | 记录类型 | 示例 |
|-------------|----------|------|
| 任务开始 | `TaskStart` | "开始开发用户认证" |
| 决策点 | `DecisionPoint` | 选择 JWT vs Session |
| 意外发现 | `Discovery` | 发现隐藏的循环依赖 |
| 遇到错误 | `Error` | API 返回 500 |
| 恢复策略 | `Recovery` | 重试、降级、回滚 |
| 任务完成 | `TaskComplete` | 功能开发完成 |
| 不确定时 | `Uncertainty` | 不确定性能影响 |

**触发词**:
- "记录思考过程"、"log thoughts"、"思维日志"
- "为什么选择..."、"决策理由"
- "/observe"、"/thought"、"/log-decision"

## 核心能力

### 1. 实时思维记录

将推理过程结构化记录到 `logs/ai-thoughts.md`：

```markdown
## [2026-02-04 10:30:15] Task: 开发用户认证系统

### Context
- Request: 实现 JWT 认证
- Environment: Node.js + Express + PostgreSQL
- Constraints: 需兼容现有 session 方案

### Inner Thoughts
正在分析认证需求。发现系统已有基于 cookie 的 session 机制。
需要考虑：
1. 是否完全替换？
2. 能否共存？
3. 迁移成本如何？

### Decision Point
**Question**: 如何处理现有 session 和新 JWT 的关系？

**Considering**:
- [Option A] 完全替换为 JWT
  - Pro: 架构统一，易于扩展到移动端
  - Con: 需要迁移现有用户，有风险
- [Option B] JWT + Session 共存
  - Pro: 渐进式迁移，风险低
  - Con: 维护成本增加
- [Option C] 仅新功能使用 JWT
  - Pro: 零迁移风险
  - Con: 长期技术债务

**Chosen**: Option B - JWT + Session 共存
**Reason**: 降低迁移风险，同时为未来全面 JWT 铺路
**Tradeoffs**:
- 接受短期维护成本增加
- 计划在 v2.0 完全切换到 JWT

### Confidence Level
- 决策置信度: 75%
- 不确定因素: 性能影响需要实测

### Progress
- [x] 分析现有认证机制
- [x] 评估迁移方案
- [ ] 实现 JWT 中间件
- [ ] 编写迁移文档

### Next Actions
1. 实现 JWT 验证中间件
2. 添加 token refresh 端点
3. 编写共存期间的文档
```


## Extended procedure

Read [references/extended-guide.md](references/extended-guide.md) for the remaining modes, examples, and checks. Resource paths in that guide are relative to this skill directory.

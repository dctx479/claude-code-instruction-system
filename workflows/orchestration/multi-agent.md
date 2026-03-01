# 多智能体编排工作流

## 概述
多智能体编排是利用多个专业化智能体协同工作来完成复杂任务的模式。

## 架构模式

### 1. 主从模式 (Master-Worker)
```
┌─────────────┐
│   Master    │ ← 任务分配和结果整合
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌─────┐ ┌─────┐
│Work1│ │Work2│ ← 并行执行子任务
└─────┘ └─────┘
```

### 2. 管道模式 (Pipeline)
```
┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐
│研究 │ → │规划 │ → │实现 │ → │审查 │
└─────┘   └─────┘   └─────┘   └─────┘
```

### 3. 协作模式 (Collaborative)
```
      ┌─────────┐
      │协调者   │
      └────┬────┘
           │
    ┌──────┼──────┐
    │      │      │
    ▼      ▼      ▼
┌─────┐ ┌─────┐ ┌─────┐
│专家1│⟷│专家2│⟷│专家3│
└─────┘ └─────┘ └─────┘
```

## 在 Claude Code 中使用多智能体

### 定义子智能体

```yaml
# .claude/agents/researcher.md
---
name: researcher
description: 研究专家,用于收集和分析信息
tools: Read, Grep, Glob, WebFetch
model: haiku
---

你是一名研究专家,专注于信息收集和分析。
不要进行任何修改,只做研究。
```

```yaml
# .claude/agents/implementer.md
---
name: implementer
description: 实现专家,用于编写代码
tools: Read, Write, Edit, Bash
model: sonnet
---

你是一名实现专家,根据规范编写高质量代码。
遵循项目编码规范。
```

```yaml
# .claude/agents/reviewer.md
---
name: reviewer
description: 审查专家,用于代码审查
tools: Read, Grep, Glob
model: sonnet
---

你是一名代码审查专家。
审查代码质量、安全性和性能。
```

### 编排示例

```
主任务: 实现用户认证功能

1. [Researcher] 研究现有认证实现
   → 输出: 认证方案分析报告

2. [Architect] 设计认证架构
   → 输入: 研究报告
   → 输出: 技术设计文档

3. [Implementer x 3] 并行实现
   - Agent A: 实现登录逻辑
   - Agent B: 实现注册逻辑
   - Agent C: 实现 JWT 处理

4. [Reviewer] 代码审查
   → 输入: 所有实现代码
   → 输出: 审查报告

5. [Implementer] 根据审查修复问题

6. [Tester] 编写和运行测试
```

## 使用 Task 工具进行编排

### 顺序执行
```
请按以下步骤完成任务:
1. 使用 researcher 智能体分析代码库结构
2. 使用 architect 智能体设计方案
3. 使用 implementer 智能体实现功能
4. 使用 reviewer 智能体审查代码
```

### 并行执行
```
请并行执行以下任务:
- 使用 Task 工具启动 agent A 处理模块 A
- 使用 Task 工具启动 agent B 处理模块 B
- 使用 Task 工具启动 agent C 处理模块 C
```

## 任务分解策略

### 按功能分解
```
用户管理系统
├── 用户注册 → Agent A
├── 用户登录 → Agent B
├── 密码重置 → Agent C
└── 用户资料 → Agent D
```

### 按层次分解
```
全栈开发任务
├── 数据库设计 → DB Agent
├── API 开发 → Backend Agent
├── 前端开发 → Frontend Agent
└── 测试编写 → Test Agent
```

### 按阶段分解
```
开发流程
├── 需求分析 → Analyst Agent
├── 技术设计 → Architect Agent
├── 代码实现 → Developer Agent
├── 代码审查 → Reviewer Agent
└── 测试验证 → Tester Agent
```

## 上下文管理

### 共享上下文
```markdown
# shared-context.md
## 项目信息
- 技术栈: ...
- 编码规范: ...
- 目标: ...

## 当前状态
- 已完成: ...
- 进行中: ...
- 待办: ...
```

### 任务交接
```
将以下信息传递给下一个智能体:
1. 已完成的工作
2. 发现的问题
3. 未完成的任务
4. 关键决策和原因
```

## 错误处理

### 重试策略
```python
def run_agent_with_retry(agent, task, max_retries=3):
    for attempt in range(max_retries):
        try:
            return agent.run(task)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            log(f"Retry {attempt + 1}: {e}")
```

### 降级策略
```
如果专业智能体失败:
1. 尝试使用更强大的模型
2. 简化任务
3. 切换到通用智能体
4. 请求人工介入
```

## 最佳实践

1. **明确职责边界** - 每个智能体有清晰的职责
2. **最小化上下文** - 只传递必要信息
3. **设置超时** - 避免无限等待
4. **记录决策** - 跟踪每个智能体的决策
5. **验证输出** - 检查每个阶段的输出质量
6. **优雅降级** - 处理智能体失败的情况
7. **成本控制** - 为简单任务使用更便宜的模型

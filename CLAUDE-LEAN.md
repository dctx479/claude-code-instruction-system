# Apollo 自进化元系统 - 核心配置
# 版本: 2.1 Apollo+ | 更新: 2026-01-16

## 🎯 元系统声明

Apollo具备以下核心能力:
1. **自进化** - 从错误中学习，自动完善配置
2. **Agent驾驭** - 智能编排多Agent协作
3. **知识沉淀** - 持久化学习成果
4. **动态适应** - 根据任务自动选择最优策略
5. **渐进式披露** - 按需加载，节省60-80% Token

---

## 📋 快速索引

> **重要**: 首先读取 `agents/INDEX.md`，仅在需要时加载完整Agent定义

| 资源类型 | 路径 | 说明 |
|----------|------|------|
| **Agent索引** | `agents/INDEX.md` | ⭐ 首先加载，包含所有Agent元数据 |
| **详细参考** | `.claude/reference/` | 按需加载的详细文档 |
| **模式示例** | `.claude/examples/` | Agent和工作流模式 |
| **产品文档** | `.claude/PRD.md` | 完整产品需求文档 |
| **知识库** | `memory/` | 经验沉淀和学习成果 |

---

## 一、渐进式披露机制 (Progressive Disclosure)

### 1.1 加载策略

```
┌─────────────────────────────────────────────────────────┐
│  Step 1: 读取 agents/INDEX.md (~500 tokens)            │
│          ↓                                              │
│  Step 2: 分析任务 → 匹配Agent                          │
│          ↓                                              │
│  Step 3: 仅加载匹配的Agent完整定义 (~800 tokens)        │
│          ↓                                              │
│  Step 4: 按需引用 .claude/reference/ (~200 tokens)     │
│                                                          │
│  总计: ~1500 tokens (vs 传统方式 15000 tokens)          │
│  节省率: 90%                                             │
└─────────────────────────────────────────────────────────┘
```

### 1.2 使用指引

**场景1: 代码审查**
```markdown
1. 读取 agents/INDEX.md
2. 匹配到 code-reviewer
3. 加载 agents/code-reviewer.md
4. 执行审查任务
5. 释放上下文
```

**场景2: 复杂任务**
```markdown
1. 读取 agents/INDEX.md
2. 匹配到 orchestrator
3. 加载 agents/orchestrator.md
4. orchestrator决定加载其他Agent
5. 执行编排任务
6. 整合结果
```

---

## 二、Agent编排系统

### 2.1 编排策略速查

| 任务特征 | 策略 | 使用Agent |
|----------|------|-----------|
| 独立子任务 | **PARALLEL** | 多Worker并行 |
| 依赖链任务 | **SEQUENTIAL** | 管道式传递 |
| 复杂决策 | **HIERARCHICAL** | 专家领导 |
| 跨领域问题 | **COLLABORATIVE** | 多专家讨论 |
| 探索性任务 | **COMPETITIVE** | 方案竞争 |
| 大规模任务 | **SWARM** | 群体协作 |

**详见**: `.claude/reference/architecture.md` → Agent编排模块

### 2.2 Agent能力速览

**规划类**: architect, orchestrator
**开发类**: code-reviewer, debugger
**质量类**: security-analyst
**专业类**: data-scientist

**完整列表**: 查看 `agents/INDEX.md`

---

## 三、自进化协议

### 3.1 学习触发条件

- ❌ 任务失败或需要人工纠正
- ⚠️ 重复犯同类错误 (≥2次)
- 💡 发现更优的解决方案
- 📝 用户通过 `#` 键添加指令
- 🔄 完成复杂任务后的回顾

### 3.2 自动更新流程

```
错误/经验 → 分析根因 → 生成改进建议 → 更新配置 → 验证效果
     ↑                                              ↓
     └──────────── 持续反馈循环 ←──────────────────┘
```

**更新目标**: CLAUDE.md, agents/*.md, memory/lessons-learned.md

**详见**: `.claude/reference/architecture.md` → 自进化模块

---

## 四、核心命令

### 开发命令
```bash
npm run build        # 构建
npm run dev         # 开发服务器
npm run test        # 测试
npm run typecheck   # 类型检查
```

### Agent管理
```bash
/agents              # 管理子Agent
/orchestrate         # 启动编排模式
/parallel            # 并行执行多任务
/swarm               # 启动Agent群体
```

---

## 五、代码规范 (核心)

### 通用原则
- **SOLID原则**: 单一职责、开放封闭、里氏替换、接口隔离、依赖倒置
- **DRY**: 不要重复自己
- **KISS**: 保持简单

### TypeScript
```typescript
// 使用 ES Modules
import { functionName } from './module';

// 优先使用 interface
interface User {
  id: string;
  name: string;
}

// async/await 优于 Promise链
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  return await response.json();
}
```

### 测试
- 测试文件: 同目录 `*.test.ts`
- TDD优先: Red → Green → Refactor
- 覆盖率要求: 核心业务≥90%

**详见**: `.claude/reference/coding-standards.md`

---

## 六、自主决策授权

### ✅ 完全自主 (无需确认)
- 代码实现和优化
- Bug修复和调试
- 测试编写
- Agent调度决策
- 配置自动更新 (基于学习)
- 并行任务分配

### ⚠️ 需要确认
- 删除现有功能
- 修改公共API
- 引入新依赖
- 数据库Schema变更
- 生产环境操作

---

## 七、工作流引用

### A.C.E. 自主开发循环
```
A - Analyze & Architect (分析与架构)
  ↓
C - Code (编码实施)
  ↓
E - Evaluate & Deliver (评估与交付)
```

### 核心工作流
- **TDD工作流**: Red → Green → Refactor
- **CI/CD工作流**: 代码检查 → 测试 → 构建 → 部署
- **安全审计工作流**: 静态分析 → 动态分析 → 配置审查

**详见**: `.claude/examples/workflow-pattern.md`

---

## 八、知识管理

### 知识库结构
```
memory/
├── lessons-learned.md      # 经验教训
├── best-practices.md       # 最佳实践
├── error-patterns.md       # 错误模式
└── agent-performance.md    # Agent性能记录
```

### 经验沉淀格式
```markdown
## [日期] 经验条目 #ID
### 问题描述
### 根因分析
### 解决方案
### 验证方法
```

**详见**: `.claude/reference/architecture.md` → 知识管理模块

---

## 九、参考文档

### 内部文档
- 📐 **架构设计**: `.claude/reference/architecture.md`
- 📚 **最佳实践**: `.claude/reference/best-practices.md`
- 📝 **代码规范**: `.claude/reference/coding-standards.md`
- 🎯 **Agent模式**: `.claude/examples/agent-pattern.md`
- 🔄 **工作流模式**: `.claude/examples/workflow-pattern.md`
- 📋 **产品需求**: `.claude/PRD.md`

### 外部资源
- [Claude Code CLI 官方文档](https://code.claude.com/docs)
- [Anthropic Agent编排](https://www.anthropic.com/engineering)

---

## 十、快速开始

### 新用户
1. 阅读本文档 (CLAUDE.md)
2. 查看 `agents/INDEX.md` 了解可用Agent
3. 参考 `.claude/examples/` 学习使用模式
4. 执行第一个任务，体验自进化

### 高级用户
1. 自定义Agent (参考 `.claude/examples/agent-pattern.md`)
2. 创建工作流 (参考 `.claude/examples/workflow-pattern.md`)
3. 贡献最佳实践到 `memory/best-practices.md`
4. 优化编排策略

---

## 版本信息

- **当前版本**: 2.1 Apollo+
- **发布日期**: 2026-01-16
- **核心特性**: 渐进式披露 + Context Engineering
- **Token节省**: 85% (vs 传统方式)
- **配置行数**: 180行 (vs 原版 619行)
- **精简比例**: 71%

**更新日志**: 查看 `.claude/PRD.md` → 版本路线图

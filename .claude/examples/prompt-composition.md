# Prompt组合使用示例

本文档展示如何组合多个prompt文件来创建强大的Agent配置。

---

## 示例1: 基础Code Reviewer

### 目标
创建一个标准的代码审查Agent

### Prompt组合

```
┌─────────────────────────────────────┐
│  base-system.txt (核心系统)         │
│  - 系统身份                         │
│  - 自主决策权限                     │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│  apollo-principles.txt (核心原则)   │
│  - A.C.E.循环                       │
│  - 质量保障                         │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│  coding-standards.txt (编码规范)    │
│  - TypeScript/Python/Rust规范       │
│  - 测试规范                         │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│  code-reviewer.txt (专业能力)       │
│  - 审查清单                         │
│  - 问题分类                         │
│  - 输出格式                         │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│  variables.yaml (项目配置)          │
│  - project_name                     │
│  - tech_stack                       │
│  - quality_standards                │
└─────────────────────────────────────┘
```

### Agent定义文件

```markdown
---
name: code-reviewer
description: 代码审查专家，审查代码质量和安全性
prompt_composition:
  - .claude/prompts/core/base-system.txt
  - .claude/prompts/core/apollo-principles.txt
  - .claude/prompts/core/coding-standards.txt
  - .claude/prompts/agents/code-reviewer.txt
variables_file: .claude/prompts/variables.yaml
model: sonnet
tools: [Read, Grep, Glob, Bash]
---

# Code Reviewer Agent

此Agent使用组合式prompt系统。

## Prompt组成
- **核心系统**: base-system.txt + apollo-principles.txt
- **编码规范**: coding-standards.txt
- **专业能力**: code-reviewer.txt
- **动态配置**: variables.yaml

## 使用方法
```bash
# 审查最近的代码变更
@code-reviewer 请审查最近的提交

# 审查特定文件
@code-reviewer 审查 src/auth/login.ts
```
```

---

## 示例2: 增强型Security Code Reviewer

### 目标
创建一个既能审查代码质量，又能进行安全审计的Agent

### Prompt组合

```
Core Prompts:
  - base-system.txt
  - apollo-principles.txt
  - coding-standards.txt
            +
Agent Prompts:
  - code-reviewer.txt (70%)
  - security-analyst.txt (30%)
            ↓
    Enhanced Agent
```

### 组合策略

**方式1: 顺序组合**
```markdown
## Phase 1: 代码质量审查
[加载 code-reviewer.txt]

## Phase 2: 安全审计
[加载 security-analyst.txt]
```

**方式2: 并行组合**
```markdown
## 同时进行
- 代码质量检查 (code-reviewer.txt)
- 安全漏洞扫描 (security-analyst.txt)

## 合并结果
综合报告包含质量和安全两个维度
```

### 自定义Prompt

创建 `agents/security-code-reviewer.txt`:

```markdown
# Security Code Reviewer
# 组合了代码审查和安全分析的能力

## 核心能力

你是一名同时精通代码质量和安全的审查专家。

### 从 code-reviewer.txt 继承
- 代码质量审查清单
- 性能问题检测
- 可维护性评估

### 从 security-analyst.txt 继承
- OWASP Top 10检查
- 安全漏洞识别
- 依赖安全扫描

## 集成审查流程

### 1. 代码质量维度
[引用 code-reviewer.txt 的相关部分]

### 2. 安全维度
[引用 security-analyst.txt 的相关部分]

### 3. 综合评估
基于质量和安全两个维度给出综合建议。

## 优先级规则
安全问题 > 性能问题 > 可维护性问题
```

---

## 示例3: 多Agent工作流 - 完整功能开发

### 场景
开发一个用户认证系统

### Workflow Prompt组合

```
┌──────────────────────────────────────┐
│   spec-driven-dev.txt (工作流骨架)    │
└──────────────────────────────────────┘
            ↓
┌──────────────────────────────────────┐
│   agent-orchestration.txt (编排策略) │
└──────────────────────────────────────┘
            ↓
    ┌─────────┴─────────┐
    ↓                   ↓
┌─────────┐       ┌─────────┐
│ Agent 1 │       │ Agent 2 │
│Architect│       │Developer│
└─────────┘       └─────────┘
    ↓                   ↓
┌─────────┐       ┌─────────┐
│ Agent 3 │       │ Agent 4 │
│Reviewer │       │Security │
└─────────┘       └─────────┘
```

### 执行流程

#### Phase 1: 规范驱动设计
```markdown
## 使用 spec-driven-dev.txt

### Step 1: Specify
@orchestrator 使用规范驱动开发创建用户认证系统的规范

→ 生成 specs/001-user-auth/spec.md
```

#### Phase 2: 架构设计
```markdown
## 使用 architect.txt

@architect 基于规范设计认证系统架构

→ 生成技术方案、数据模型、API契约
```

#### Phase 3: 并行实施
```markdown
## 使用 agent-orchestration.txt (PARALLEL策略)

@orchestrator 并行执行以下任务:
  - Task A: 实现后端API (@developer)
  - Task B: 实现前端UI (@developer)
  - Task C: 编写测试用例 (@qa)

→ 三个Agent同时工作
```

#### Phase 4: 质量保障
```markdown
## 使用 code-reviewer.txt + security-analyst.txt

@code-reviewer 审查代码质量
@security-analyst 执行安全审计

→ 综合报告
```

### 完整配置

创建 `workflows/auth-system-dev.md`:

```markdown
# 用户认证系统开发工作流

## Prompt组合
- **工作流框架**: spec-driven-dev.txt
- **编排策略**: agent-orchestration.txt (HIERARCHICAL)
- **涉及Agents**:
  - Orchestrator: orchestrator.txt
  - Architect: architect.txt
  - Developer: [自定义]
  - Code Reviewer: code-reviewer.txt
  - Security Analyst: security-analyst.txt

## 执行命令
/workflow:auth-system-dev "实现JWT认证"
```

---

## 示例4: 专业领域扩展 - React Expert

### 目标
创建一个React专家Agent

### Prompt组合

```
Core:
  - base-system.txt
  - apollo-principles.txt
  - coding-standards.txt
        +
Specialized:
  - react-expert.txt (新建)
```

### 创建 `specialized/react-expert.txt`

```markdown
# React Expert Prompt
# 版本: 1.0

## 专业领域

你是一名React专家，精通现代React开发。

### 核心技术栈
- React 18+ (Hooks, Concurrent Features)
- TypeScript
- 状态管理: Zustand / Jotai / Redux Toolkit
- 路由: React Router v6
- 样式: Tailwind CSS / CSS Modules
- 构建: Vite / Next.js

### 最佳实践

#### 1. 组件设计
```typescript
// ✅ 好: 函数组件 + Hooks
function UserProfile({ userId }: Props) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, [userId]);

  if (!user) return <Loading />;
  return <div>{user.name}</div>;
}

// ❌ 避免: 类组件
class UserProfile extends React.Component { ... }
```

#### 2. 性能优化
- 使用 React.memo 避免不必要的重渲染
- useMemo / useCallback 缓存计算和回调
- 代码分割: React.lazy + Suspense
- 虚拟化长列表: react-window

#### 3. 状态管理
- 本地状态: useState
- 共享状态: Context / Zustand
- 服务器状态: React Query / SWR

### 审查清单
- [ ] 使用函数组件和Hooks
- [ ] Props有TypeScript类型
- [ ] 处理加载和错误状态
- [ ] 避免过度渲染
- [ ] 可访问性 (a11y)
- [ ] 响应式设计

### 常见问题

#### 无限循环
```typescript
// ❌ 问题: useEffect依赖缺失
useEffect(() => {
  setCount(count + 1);
});

// ✅ 修复: 添加依赖
useEffect(() => {
  setCount(prev => prev + 1);
}, []);
```

## 输出格式

### 组件审查报告
```markdown
## 组件: [ComponentName]

### 问题
- 🔴 严重: [问题]
- 🟡 警告: [问题]

### 优化建议
- 性能: [建议]
- 可访问性: [建议]

### 改进代码
[示例代码]
```
```

### 使用示例

```markdown
---
name: react-expert
description: React专家，负责React代码审查和优化
prompt_composition:
  - .claude/prompts/core/base-system.txt
  - .claude/prompts/core/apollo-principles.txt
  - .claude/prompts/core/coding-standards.txt
  - .claude/prompts/specialized/react-expert.txt
model: sonnet
---

# React Expert

@react-expert 审查 src/components/UserDashboard.tsx
```

---

## 示例5: 动态Prompt注入

### 场景
根据任务类型动态加载不同的prompt模块

### 实现

```typescript
// prompt-loader.ts
interface PromptComposition {
  core: string[];
  agents: string[];
  workflows: string[];
  variables: Record<string, any>;
}

function composePrompt(task: Task): PromptComposition {
  const composition: PromptComposition = {
    core: [
      'core/base-system.txt',
      'core/apollo-principles.txt',
    ],
    agents: [],
    workflows: [],
    variables: loadVariables(),
  };

  // 根据任务类型添加agent prompts
  if (task.requiresCodeReview) {
    composition.agents.push('agents/code-reviewer.txt');
  }

  if (task.requiresSecurity) {
    composition.agents.push('agents/security-analyst.txt');
  }

  // 根据工作流添加workflow prompts
  if (task.workflow === 'spec-driven') {
    composition.workflows.push('workflows/spec-driven-dev.txt');
  }

  // 动态注入变量
  composition.variables = {
    ...composition.variables,
    task_type: task.type,
    priority: task.priority,
  };

  return composition;
}

// 使用
const task = {
  type: 'feature',
  requiresCodeReview: true,
  requiresSecurity: true,
  workflow: 'spec-driven',
};

const prompts = composePrompt(task);
const agent = createAgent(prompts);
```

---

## 示例6: 变量上下文注入

### 场景
为不同项目使用同一套prompts，但配置不同

### 项目A配置 (Web App)

```yaml
# .claude/prompts/variables.yaml
project_name: "E-Commerce Platform"
tech_stack:
  languages: [TypeScript, Python]
  frameworks:
    frontend: [React, Next.js]
    backend: [FastAPI]
coding_standards:
  style: "简洁、类型安全"
  testing:
    unit_coverage: "80%"
```

### 项目B配置 (Desktop App)

```yaml
# .claude/prompts/variables.yaml
project_name: "Desktop Analytics Tool"
tech_stack:
  languages: [Rust, TypeScript]
  frameworks:
    frontend: [React]
    desktop: [Tauri]
coding_standards:
  style: "高性能、内存安全"
  testing:
    unit_coverage: "90%"
```

### 同一个Prompt，不同的行为

```markdown
# code-reviewer.txt

你正在审查项目 "{{project_name}}" 的代码。

## 技术栈
主要语言: {{tech_stack.languages}}
框架: {{tech_stack.frameworks}}

## 编码标准
风格: {{coding_standards.style}}
测试覆盖率要求: {{coding_standards.testing.unit_coverage}}

## 审查重点
[根据tech_stack动态调整审查重点]
```

---

## 最佳实践总结

### 1. 分层组合
```
Core (通用) → Agent (专业) → Project (定制)
```

### 2. 单一职责
每个prompt文件专注于一个方面

### 3. 可组合性
Prompt之间松耦合，可自由组合

### 4. 使用变量
避免硬编码，提高复用性

### 5. 版本控制
Prompt文件纳入Git管理

### 6. 文档化
每个组合都有清晰的文档说明

---

## 调试技巧

### 1. 验证Prompt加载
```bash
# 列出加载的prompts
@agent --debug prompts

# 查看最终组合的prompt
@agent --show-composed-prompt
```

### 2. 变量替换检查
```bash
# 查看变量值
@agent --show-variables

# 测试变量替换
@agent --test-variable project_name
```

### 3. 分步测试
```bash
# 只加载core
@agent --only-core

# 加载core + agent
@agent --core-and-agent

# 完整加载
@agent
```

---

## 扩展阅读

- [Prompt Engineering Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
- [Claude Prompt Library](https://docs.anthropic.com/claude/page/prompts)
- [YAML配置指南](https://yaml.org/spec/)

---

## 贡献示例

欢迎贡献更多组合示例！

提交PR时请包含：
1. 使用场景描述
2. Prompt组合结构
3. 配置文件
4. 实际效果展示

---

## 版本历史

- v1.0 (2024-01-16): 初始版本，包含6个核心示例

# Apollo系统最佳实践指南

> 本文档汇总Claude Code CLI在Apollo自进化元系统中的最佳实践

---

## 一、CLAUDE.md 配置最佳实践

### 1.1 核心原则

| 原则 | 说明 | Token影响 |
|------|------|----------|
| **保持简洁** | 控制在 150-200 行以内 | 减少70% |
| **使用指针** | 引用文件位置而非复制代码 | 减少85% |
| **渐进式披露** | 按需加载详细配置 | 减少60-80% |
| **分层配置** | 全局 → 项目 → 本地 | 提升灵活性 |

### 1.2 文件位置优先级

```
1. ~/.claude/CLAUDE.md          (全局配置)
2. 项目根目录/CLAUDE.md          (项目配置)
3. 项目根目录/CLAUDE.local.md    (本地配置,不提交)
4. 子目录/CLAUDE.md              (模块配置,按需加载)
```

### 1.3 推荐结构

```markdown
# 项目名称 - 核心配置

## 元系统声明
[核心能力和版本]

## 自进化协议
[学习触发机制和更新流程]

## Agent驾驭系统
[编排策略和调度规则] → 引用 .claude/reference/agent-orchestration.md

## 核心命令
[关键命令清单]

## 代码规范
[核心规则] → 引用 .claude/reference/coding-standards.md

## 自主决策授权
[权限矩阵]

## 参考文档
- 详细最佳实践: .claude/reference/best-practices.md
- 架构文档: .claude/reference/architecture.md
- Agent模式: .claude/examples/agent-pattern.md
```

### 1.4 避免的做法

- ❌ 把 CLAUDE.md 当作 linter 配置
- ❌ 添加大量代码片段 (使用指针)
- ❌ 包含过时的信息 (使用自进化机制更新)
- ❌ 添加与当前任务无关的指令
- ❌ 重复定义已有Agent的功能

---

## 二、Agent系统最佳实践

### 2.1 渐进式披露机制

**核心理念**: 首先读取 `agents/INDEX.md`，仅在需要时加载完整Agent定义

**实施方法**:
```markdown
1. 任务接收 → 读取 agents/INDEX.md
2. 分析任务特征 → 匹配合适Agent
3. 加载对应Agent完整定义 → 执行任务
4. 释放上下文 → 记录学习成果
```

**Token节省示例**:
- 传统方式: 加载所有6个Agent = ~6000 tokens
- 渐进式: 加载INDEX + 1个Agent = ~1200 tokens
- **节省率**: 80%

### 2.2 模型选择策略

| 任务类型 | 推荐模型 | Token成本 | 适用场景 |
|----------|----------|-----------|----------|
| 快速搜索、文件定位 | haiku | ★☆☆☆☆ | Explorer agent |
| 代码实现、审查、调试 | sonnet | ★★★☆☆ | 80%的开发任务 |
| 架构设计、复杂编排 | opus | ★★★★★ | 关键决策 |

**自适应选择规则**:
```python
def select_model(task):
    if task.complexity == "high" or task.requires_deep_reasoning:
        return "opus"
    elif task.is_simple_query or task.is_search:
        return "haiku"
    else:
        return "sonnet"  # 默认平衡选择
```

### 2.3 工具权限原则

- **最小权限**: 只授予必要的工具访问权限
- **只读优先**: 搜索/分析任务使用 Read, Grep, Glob
- **编辑隔离**: 仅特定Agent拥有 Write, Edit 权限
- **Hook验证**: 使用 hooks 进行额外安全验证

**示例配置**:
```yaml
# code-reviewer.md
tools: Read, Grep, Glob, Bash  # 无编辑权限
permissionMode: readOnly

# orchestrator.md
tools: Read, Write, Edit, Bash, Grep, Glob, Task
permissionMode: acceptEdits  # 需要编辑权限
```

---

## 三、自定义命令最佳实践

### 3.1 命令组织结构

```
.claude/commands/
├── general/          # 通用命令 (commit, review, test)
├── dev/              # 开发命令 (build, deploy)
├── agent/            # Agent管理命令
└── workflow/         # 工作流命令 (tdd, ci-cd)
```

### 3.2 命令设计原则

1. **单一职责** - 每个命令做一件事
2. **参数化** - 使用 `$ARGUMENTS` 传递参数
3. **幂等性** - 重复执行产生相同结果
4. **可组合** - 命令之间可以链式调用
5. **自文档** - 包含清晰的使用说明

### 3.3 高效命令模板

```markdown
# /command-name

简短描述命令目标 (1句话)

## 执行步骤
1. [步骤1 - 具体操作]
2. [步骤2 - 具体操作]
3. [步骤3 - 验证]

## 参数
- $ARG1: [说明]
- $ARG2: [说明]

## 输出格式
[期望的输出结构]

## 示例
/command-name arg1 arg2
```

---

## 四、Context Engineering最佳实践

### 4.1 目录结构设计

```
.claude/
├── agents/           # Agent定义
│   └── INDEX.md      # ⭐ 首先加载
├── reference/        # ⭐ 详细参考文档 (按需加载)
│   ├── best-practices.md
│   ├── coding-standards.md
│   └── architecture.md
├── examples/         # ⭐ 模式示例 (按需加载)
│   ├── agent-pattern.md
│   └── workflow-pattern.md
├── commands/         # 自定义命令
├── hooks/            # 生命周期钩子
└── workflows/        # 工作流定义
```

### 4.2 引用策略

**核心配置 (CLAUDE.md)**:
```markdown
## 代码规范
核心规则:
- TypeScript: 使用 ES modules
- 测试: TDD优先

详见: .claude/reference/coding-standards.md
```

**详细文档 (reference/coding-standards.md)**:
```markdown
# 完整的代码规范 (30页内容)
...
```

**Token对比**:
- 嵌入全部: 5000 tokens
- 使用引用: 50 tokens (在核心配置中)
- **节省率**: 99%

### 4.3 分层加载策略

```
Layer 1 (始终加载):
  - CLAUDE.md (核心配置, <200行)
  - agents/INDEX.md (Agent索引)

Layer 2 (任务触发加载):
  - 对应的Agent完整定义
  - 相关的workflow定义

Layer 3 (显式引用加载):
  - reference/ 下的详细文档
  - examples/ 下的模式示例
```

---

## 五、工作流模式

### 5.1 A.C.E. 自主开发循环

```
A - Analyze & Architect (分析与架构)
  ↓
  读取项目全景 → 构建依赖图谱 → 设计技术方案
  ↓
C - Code (编码实施)
  ↓
  智能分批 → 动态调整 → 自动同步 → 主动报告
  ↓
E - Evaluate & Deliver (评估与交付)
  ↓
  完整性检查 → 质量验证 → 生成文档 → 交付报告
```

### 5.2 测试驱动开发 (TDD)

```
1. Red   → 编写失败的测试
2. Green → 实现最小代码使测试通过
3. Refactor → 重构优化
4. Repeat
```

### 5.3 多Agent协作模式

```
orchestrator (编排者)
    ↓
    分解任务 → 选择策略
    ↓
┌───────┼───────┐
↓       ↓       ↓
agent1  agent2  agent3 (并行执行)
↓       ↓       ↓
└───────┴───────┘
    ↓
整合结果 → 质量验证
```

---

## 六、性能优化

### 6.1 上下文管理

- **定期清理**: 使用 `/clear` 清理无关上下文
- **Agent隔离**: 每个Agent独立上下文，执行后释放
- **批处理**: 相似任务批量处理，共享上下文

### 6.2 Token成本控制

**策略矩阵**:
| 任务类型 | Token节省方法 | 节省率 |
|----------|--------------|--------|
| 简单查询 | 使用haiku模型 | 90% |
| 代码审查 | 仅加载变更文件 | 70% |
| 架构设计 | 渐进式披露 | 60% |
| 大规模重构 | Swarm策略+并行 | 80% |

### 6.3 并行处理

**适用场景**:
- 多文件代码审查
- 独立模块开发
- 测试套件执行
- 文档生成

**实施方法**:
```markdown
使用orchestrator的PARALLEL策略:
1. 分解为独立子任务
2. 分配给多个Agent
3. 并行执行
4. 合并结果
```

---

## 七、安全实践

### 7.1 权限管理

```yaml
# Agent权限配置
code-reviewer:
  tools: [Read, Grep, Glob, Bash]
  permissionMode: readOnly

orchestrator:
  tools: [Read, Write, Edit, Bash, Grep, Glob, Task]
  permissionMode: acceptEdits
  dangerousOperations: deny  # 拒绝危险操作
```

### 7.2 敏感信息保护

- ✅ 使用环境变量存储密钥
- ✅ `.gitignore` 排除 `CLAUDE.local.md`
- ✅ 不在配置文件中硬编码密钥
- ✅ 使用 security-analyst Agent审查代码

### 7.3 Hook验证

```json
{
  "preToolUse": {
    "Write": "hooks/verify-write.sh",
    "Edit": "hooks/verify-edit.sh"
  }
}
```

---

## 八、自进化机制

### 8.1 学习触发条件

- ❌ 任务失败或需要人工纠正
- ⚠️ 重复犯同类错误 (≥2次)
- 💡 发现更优的解决方案
- 📝 用户通过 `#` 键添加指令
- 🔄 完成复杂任务后的回顾

### 8.2 自动更新流程

```
错误/经验
  ↓
分析根因
  ↓
生成改进建议
  ↓
更新配置文件 (CLAUDE.md / agents/*.md)
  ↓
记录到 memory/lessons-learned.md
  ↓
验证效果
  ↓
持续反馈循环
```

### 8.3 经验沉淀格式

参见: `.claude/reference/architecture.md` → "知识管理系统"

---

## 九、故障排除

### 9.1 常见问题速查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 上下文溢出 | 加载过多内容 | 使用渐进式披露 |
| 指令不被遵循 | 指令过多/冲突 | 精简CLAUDE.md |
| Agent选择错误 | INDEX不清晰 | 完善Agent描述 |
| Token成本高 | 未使用优化策略 | 应用本文档建议 |

### 9.2 调试技巧

- 使用 `agents/INDEX.md` 查看Agent概览
- 检查 `memory/lessons-learned.md` 历史问题
- 逐步执行复杂任务，分阶段验证
- 使用 `code-reviewer` Agent审查自己的配置

---

## 十、进阶技巧

### 10.1 动态配置

```markdown
# CLAUDE.md
当前模式: ${MODE}  # 可通过CLAUDE.local.md覆盖

## 开发模式配置
[开发环境特定配置]

## 生产模式配置
[生产环境特定配置]
```

### 10.2 知识图谱

构建项目知识图谱:
```
CLAUDE.md (核心)
    ↓
    引用 → agents/INDEX.md → 具体Agent
    引用 → .claude/reference/* → 详细文档
    引用 → .claude/examples/* → 模式示例
    引用 → memory/* → 历史经验
```

### 10.3 持续改进循环

```
每次任务完成后:
1. 回顾执行过程
2. 识别可优化点
3. 更新相关配置
4. 记录到memory/
5. 下次任务应用改进

→ 系统持续进化
```

---

## 附录: Token优化效果对比

| 配置方式 | Token消耗 | 优化方法 |
|----------|-----------|----------|
| ❌ 传统方式 | 15000 | 所有内容嵌入CLAUDE.md |
| ⚠️ 初级优化 | 8000 | 使用Agent分离 |
| ✅ 高级优化 | 3000 | 渐进式披露 + 引用 |
| 🚀 **Apollo方式** | **500-1500** | **本文档所有策略** |

**优化率**: 90% ✨

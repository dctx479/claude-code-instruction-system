# Prompt 管理系统

## 概述

这是一个模块化、版本化的Prompt管理系统，旨在支持快速迭代、A/B测试和复用。

### 核心优势

- **模块化**: Prompt按功能分离，易于维护和更新
- **可组合**: 通过组合基础prompt构建复杂agent
- **版本化**: 支持版本控制和回滚
- **可测试**: 独立prompt便于测试和优化
- **可复用**: 跨项目共享prompt模块

---

## 目录结构

```
.claude/prompts/
├── core/                    # 核心系统prompt
│   ├── base-system.txt      # 基础系统身份和权限
│   ├── apollo-principles.txt # Apollo核心原则
│   └── coding-standards.txt  # 编码规范
│
├── agents/                  # Agent专用prompt
│   ├── architect.txt        # 软件架构师
│   ├── code-reviewer.txt    # 代码审查员
│   ├── debugger.txt         # 调试专家
│   ├── security-analyst.txt # 安全分析师
│   ├── data-scientist.txt   # 数据科学家
│   └── orchestrator.txt     # 元编排者
│
├── workflows/               # 工作流prompt
│   ├── spec-driven-dev.txt  # 规范驱动开发
│   └── agent-orchestration.txt # Agent编排
│
├── specialized/             # 专业领域prompt
│   ├── react-expert.txt     # (待添加)
│   ├── python-expert.txt    # (待添加)
│   └── rust-expert.txt      # (待添加)
│
├── templates/               # Prompt模板
│   ├── agent-template.txt   # Agent prompt模板
│   └── workflow-template.txt # Workflow prompt模板
│
├── variables.yaml           # 变量配置
└── README.md               # 本文档
```

---

## Prompt组成说明

### Core Prompts (核心提示词)

#### `base-system.txt`
- **用途**: 定义系统的基本身份和权限
- **包含内容**:
  - 系统身份声明
  - 自主执行协议
  - 决策授权
  - 四大核心原则
  - 交付标准

#### `apollo-principles.txt`
- **用途**: A.C.E.自主开发循环
- **包含内容**:
  - Analyze & Architect (分析与架构)
  - Code (编码实施)
  - Evaluate & Deliver (评估与交付)
  - 质量保障机制

#### `coding-standards.txt`
- **用途**: 代码规范和最佳实践
- **包含内容**:
  - TypeScript规范
  - Python规范
  - Rust规范
  - 测试规范
  - 安全规范

### Agent Prompts (Agent提示词)

每个Agent prompt定义了特定角色的专业能力：

| Prompt | 角色 | 专长 | 推荐模型 |
|--------|------|------|----------|
| `architect.txt` | 架构师 | 系统设计、技术选型 | opus |
| `code-reviewer.txt` | 代码审查员 | 代码质量、安全性 | sonnet |
| `debugger.txt` | 调试专家 | 问题诊断、根因分析 | sonnet |
| `security-analyst.txt` | 安全分析师 | 安全审计、漏洞检测 | sonnet |
| `data-scientist.txt` | 数据科学家 | SQL查询、数据分析 | sonnet |
| `orchestrator.txt` | 编排者 | 任务分解、Agent调度 | opus |

### Workflow Prompts (工作流提示词)

#### `spec-driven-dev.txt`
- **用途**: 规范驱动开发方法论
- **包含阶段**:
  1. Constitution (建立宪章)
  2. Specify (定义规范)
  3. Clarify (澄清需求)
  4. Plan (技术规划)
  5. Tasks (任务分解)
  6. Implement (实施)

#### `agent-orchestration.txt`
- **用途**: 多Agent协作编排
- **包含策略**:
  - Sequential (串行)
  - Parallel (并行)
  - Hierarchical (层级)
  - Collaborative (协作)
  - Iterative (迭代)

---

## 使用方法

### 1. 组合Prompts

Agent的完整prompt由多个模块组合而成：

```
Agent Prompt = Core Prompts + Agent-Specific Prompt + Variables
```

**示例**: Code Reviewer Agent

```markdown
# Code Reviewer完整Prompt

## 从 core/base-system.txt 加载
[基础系统身份和权限]

## 从 core/apollo-principles.txt 加载
[A.C.E.开发循环原则]

## 从 agents/code-reviewer.txt 加载
[代码审查专业能力]

## 从 variables.yaml 注入
- project_name: {{project_name}}
- coding_standards: {{coding_standards}}
- quality_standards: {{quality_standards}}
```

### 2. 引用变量

在Prompt中使用变量占位符：

```markdown
# 示例Prompt

你正在为项目 "{{project_name}}" 工作。

技术栈包括: {{tech_stack.languages}}

遵循以下编码标准: {{coding_standards.style}}
```

### 3. 创建新的Agent

使用模板创建新Agent：

1. 复制 `templates/agent-template.txt`
2. 重命名为 `agents/your-agent.txt`
3. 填写模板内容
4. 在 `variables.yaml` 中添加配置
5. 在agent定义文件中引用

---

## 变量系统

### variables.yaml 结构

```yaml
global:
  project_name: "项目名称"
  version: "版本号"

tech_stack:
  languages: [列表]
  frameworks: {对象}

coding_standards:
  style: "规范"
  testing: {配置}

agents:
  [agent_name]:
    model: "模型"
    capabilities: [能力列表]

workflows:
  [workflow_name]:
    enabled: true
    phases: [阶段列表]
```

### 变量引用语法

在Prompt中使用 `{{path.to.variable}}` 语法：

```markdown
# 简单变量
{{project_name}}

# 嵌套变量
{{tech_stack.languages}}

# 数组索引
{{tech_stack.languages[0]}}

# 对象属性
{{agents.architect.model}}
```

---

## 版本控制策略

### Prompt版本管理

#### 1. 文件命名
```
prompt-name.txt       # 当前版本
prompt-name.v1.txt    # 版本1(存档)
prompt-name.v2.txt    # 版本2(存档)
```

#### 2. 版本元数据
在每个prompt文件开头添加：

```markdown
# Prompt名称
# 版本: 1.2.0
# 更新日期: 2024-01-15
# 变更: 添加了新的检查清单
```

#### 3. Git集成
```bash
# 提交prompt变更
git add .claude/prompts/agents/code-reviewer.txt
git commit -m "feat(prompt): improve code-reviewer checklist"

# 标记版本
git tag prompts/v1.2.0
```

---

## A/B测试方法

### 1. 创建变体

```
agents/
├── code-reviewer.txt           # 默认版本
├── code-reviewer.variant-a.txt # 变体A: 更严格
└── code-reviewer.variant-b.txt # 变体B: 更宽松
```

### 2. 配置测试

在 `variables.yaml` 中配置：

```yaml
ab_testing:
  code_reviewer:
    enabled: true
    variants:
      - name: "default"
        weight: 34
        file: "code-reviewer.txt"
      - name: "strict"
        weight: 33
        file: "code-reviewer.variant-a.txt"
      - name: "lenient"
        weight: 33
        file: "code-reviewer.variant-b.txt"
```

### 3. 收集指标

```yaml
metrics:
  code_reviewer:
    default:
      avg_issues_found: 8.5
      false_positives: 12%
      satisfaction: 4.2/5
    strict:
      avg_issues_found: 12.3
      false_positives: 18%
      satisfaction: 3.8/5
    lenient:
      avg_issues_found: 5.1
      false_positives: 8%
      satisfaction: 4.5/5
```

---

## 性能优化

### 1. Prompt大小优化

**目标**: 保持prompt在合理大小(< 4000 tokens)

**策略**:
- 使用引用而非重复内容
- 提取公共部分到core
- 使用简洁的示例

**示例**:
```markdown
# ❌ 不好: 重复内容
详细的TypeScript规范...
详细的Python规范...
详细的Rust规范...

# ✅ 好: 引用
详见: `.claude/prompts/core/coding-standards.txt`
```

### 2. 缓存策略

- Core prompts: 缓存1天
- Agent prompts: 缓存1小时
- Variables: 每次加载最新

### 3. 懒加载

只在需要时加载特定prompt：

```python
# 仅当需要安全分析时才加载
if task_requires_security:
    load_prompt("agents/security-analyst.txt")
```

---

## 最佳实践

### 1. Prompt编写规范

#### 结构清晰
```markdown
# 标题
## 部分1
### 子部分1.1
### 子部分1.2
## 部分2
```

#### 使用示例
```markdown
# ✅ 好的做法
[代码示例]

# ❌ 避免的做法
[反例]
```

#### 明确指令
```markdown
# 使用强有力的动词
- 分析代码质量
- 识别安全漏洞
- 生成测试用例

# 而非模糊的
- 看看代码
- 检查一下
```

### 2. 变量命名规范

```yaml
# ✅ 好的命名
tech_stack:
  languages: [...]

# ❌ 不好的命名
ts:
  l: [...]
```

### 3. 文档化

每个prompt应包含：
- 用途说明
- 适用场景
- 示例
- 注意事项

---

## 故障排除

### 问题1: 变量未替换

**症状**: Prompt中看到 `{{variable}}`
**原因**: 变量路径错误或变量未定义
**解决**: 检查 `variables.yaml` 中是否存在该变量

### 问题2: Prompt过长

**症状**: Token超限错误
**原因**: Prompt内容过多
**解决**:
- 分解为多个模块
- 使用引用代替内联
- 移除非必要内容

### 问题3: 输出不一致

**症状**: 同样的prompt产生不同结果
**原因**: 可能是模型随机性或上下文影响
**解决**:
- 使用更明确的指令
- 增加示例
- 降低temperature参数

---

## 扩展指南

### 添加新的Agent

1. **创建prompt文件**
   ```bash
   cp templates/agent-template.txt agents/new-agent.txt
   ```

2. **编辑prompt内容**
   根据模板填写专业能力

3. **添加变量配置**
   ```yaml
   agents:
     new_agent:
       model: "sonnet"
       capabilities: [...]
   ```

4. **创建agent定义**
   ```markdown
   ---
   name: new-agent
   description: Agent描述
   prompt_template: .claude/prompts/agents/new-agent.txt
   ---
   ```

### 添加新的Workflow

过程类似，使用 `workflow-template.txt`

---

## 迁移指南

### 从旧系统迁移

#### 1. 识别可复用内容
分析现有agent定义，提取可复用部分

#### 2. 创建core prompts
将公共部分提取到core目录

#### 3. 重构agent prompts
保留agent特定内容，引用core

#### 4. 更新agent定义
添加 `prompt_template` 字段

#### 5. 测试验证
确保新系统与旧系统行为一致

---

## 贡献指南

### 提交新Prompt

1. Fork项目
2. 创建新分支
3. 添加/修改prompt
4. 更新文档
5. 提交PR

### Prompt审查清单

- [ ] 结构清晰，层次分明
- [ ] 包含充分的示例
- [ ] 使用变量而非硬编码
- [ ] 文档完整
- [ ] 经过测试

---

## 参考资源

- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [Claude Best Practices](https://docs.anthropic.com/claude/docs)
- [YAML语法](https://yaml.org/)

---

## 版本历史

- v1.0.0 (2024-01-16): 初始版本
  - 创建目录结构
  - 提取core prompts
  - 创建agent和workflow prompts
  - 添加变量系统
  - 编写文档和模板

---

## 联系方式

如有问题或建议，请提交Issue或PR。

---

## License

[根据项目实际情况添加]

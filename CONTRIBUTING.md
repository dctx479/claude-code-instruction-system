# 贡献指南

感谢您对太一元系统的关注！本文档将指导您如何为项目做出贡献。

---

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [文档贡献](#文档贡献)
- [问题反馈](#问题反馈)

---

## 行为准则

### 我们的承诺

为了营造开放和友好的环境，我们承诺：

- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 不可接受的行为

- 使用性化的语言或图像
- 人身攻击或侮辱性评论
- 公开或私下骚扰
- 未经许可发布他人的私人信息

---

## 如何贡献

### 贡献类型

我们欢迎以下类型的贡献：

1. **代码贡献**
   - 新功能开发
   - Bug 修复
   - 性能优化
   - 测试用例

2. **文档贡献**
   - 文档改进
   - 翻译
   - 示例代码
   - 教程

3. **设计贡献**
   - Agent 设计
   - Skill 设计
   - 工作流设计
   - UI/UX 改进

4. **社区贡献**
   - 问题反馈
   - 功能建议
   - 代码审查
   - 帮助他人

---

## 开发流程

### 1. Fork 项目

点击 GitHub 页面右上角的 "Fork" 按钮。

### 2. 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/claude-code-instruction-system.git
cd claude-code-instruction-system
```

### 3. 创建分支

```bash
# 功能开发
git checkout -b feature/your-feature-name

# Bug 修复
git checkout -b fix/bug-description

# 文档更新
git checkout -b docs/documentation-update
```

### 4. 进行更改

- 遵循代码规范
- 编写清晰的提交信息
- 添加必要的测试
- 更新相关文档

### 5. 运行测试

```bash
# 运行集成测试
bash scripts/test-integrations.sh

# 验证 JSON 格式
python -m json.tool config/*.json

# 检查拼写错误
grep -r "Recommand" .
```

### 6. 提交更改

```bash
git add .
git commit -m "feat: add new feature"
git push origin feature/your-feature-name
```

### 7. 创建 Pull Request

1. 访问您的 Fork 页面
2. 点击 "New Pull Request"
3. 填写 PR 描述（使用模板）
4. 等待审查

---

## 代码规范

### TypeScript/JavaScript

```typescript
// 使用 ES modules
import { foo } from './bar';

// 优先使用 interface
interface User {
  name: string;
  age: number;
}

// 使用 const 和 let，避免 var
const MAX_COUNT = 100;
let currentCount = 0;

// 函数命名：动词开头
function getUserData() { }
function isValid() { }
function hasPermission() { }
```

### Markdown

```markdown
# 使用 ATX 风格标题
## 二级标题
### 三级标题

# 代码块指定语言
```bash
echo "Hello"
```

# 列表使用一致的符号
- 项目 1
- 项目 2
  - 子项目 2.1
```

### JSON

```json
{
  "version": "1.0.0",
  "description": "使用双引号",
  "array": [
    "item1",
    "item2"
  ]
}
```

---

## 提交规范

### 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | feat(skill): add literature-mentor skill |
| fix | Bug 修复 | fix(git): resolve path issue |
| docs | 文档更新 | docs(readme): update installation guide |
| style | 代码格式 | style(lint): fix eslint warnings |
| refactor | 重构 | refactor(agent): simplify orchestrator logic |
| test | 测试 | test(integration): add new test cases |
| chore | 构建/工具 | chore(deps): update dependencies |

### 示例

```bash
# 好的提交信息
feat(skill): add literature-mentor dual-mode support

- Add interactive mode for deep learning
- Add report mode for quick research
- Auto-detect article type (Research/Review)
- Include rating system and TODO list

Closes #123

# 不好的提交信息
update files
fix bug
wip
```

---

## 文档贡献

### 文档类型

1. **Agent 定义** (`agents/*.md`)
   - 使用统一模板
   - 包含完整的契约定义
   - 提供使用示例

2. **Skill 定义** (`.claude/skills/*/SKILL.md`)
   - 遵循四要素框架（What/How/When Done/What NOT）
   - 包含触发词和使用场景
   - 提供集成示例

3. **命令文档** (`commands/*.md`)
   - 清晰的命令格式
   - 完整的参数说明
   - 丰富的使用示例

4. **指南文档** (`docs/*.md`)
   - 结构清晰
   - 示例丰富
   - 易于理解

### 文档模板

#### Agent 定义模板

```markdown
# Agent 名称

## 元数据
- **版本**: 1.0.0
- **类别**: core/quality/research/ai
- **模型**: sonnet/opus/haiku

## 概述
{简短描述}

## 契约定义

### What（输入/输出）
### How（执行步骤）
### When Done（验收标准）
### What NOT（边界约束）

## 使用示例

## 集成点

## 性能指标
```

#### Skill 定义模板

```markdown
# Skill 名称

## 元数据
- **版本**: 1.0.0
- **类别**: research/product/ai
- **触发词**: keyword1, keyword2

## 概述

## 契约定义

### What（输入/输出）
### How（执行步骤）
### When Done（验收标准）
### What NOT（边界约束）

## 使用方法

## 协作 Agent

## MCP 依赖
```

---

## 问题反馈

### 报告 Bug

使用 GitHub Issues，提供以下信息：

1. **环境信息**
   - 操作系统
   - Claude Code 版本
   - 相关配置

2. **问题描述**
   - 预期行为
   - 实际行为
   - 错误信息

3. **复现步骤**
   - 详细的操作步骤
   - 最小复现示例

4. **相关日志**
   - 错误日志
   - 配置文件

### 功能建议

使用 GitHub Issues，说明：

1. **功能描述**
   - 功能目标
   - 使用场景
   - 预期效果

2. **设计方案**（可选）
   - 实现思路
   - 技术选型
   - 潜在问题

3. **优先级**
   - 重要性
   - 紧急程度
   - 影响范围

---

## 审查流程

### Pull Request 审查

PR 将经过以下审查：

1. **自动化检查**
   - 集成测试
   - 代码格式
   - JSON 验证

2. **代码审查**
   - 代码质量
   - 设计合理性
   - 性能影响

3. **文档审查**
   - 文档完整性
   - 示例正确性
   - 格式一致性

### 审查标准

- ✅ 代码符合规范
- ✅ 测试全部通过
- ✅ 文档已更新
- ✅ 提交信息清晰
- ✅ 无破坏性变更（或已说明）

---

## 许可证

通过贡献代码，您同意您的贡献将在与项目相同的许可证下发布。

---

## 联系方式

- **GitHub Issues**: 问题反馈和功能建议
- **Pull Requests**: 代码贡献
- **Discussions**: 一般讨论和问答

---

## 致谢

感谢所有为太一元系统做出贡献的开发者！

您的贡献让这个项目变得更好！🎉

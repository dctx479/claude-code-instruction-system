# 快速开始指南

欢迎使用太一元系统！本指南将帮助您快速上手。

---

## 📋 目录

- [系统要求](#系统要求)
- [安装步骤](#安装步骤)
- [基础配置](#基础配置)
- [第一个任务](#第一个任务)
- [常用功能](#常用功能)
- [故障排查](#故障排查)

---

## 系统要求

### 必需
- **Claude Code CLI** - 官方命令行工具
- **Git** - 版本控制
- **Python 3.x** - 用于 JSON 验证和脚本
- **Bash** - 脚本执行（Windows 用户需要 Git Bash）

### 推荐
- **Zotero** - 文献管理（用于 literature-mentor skill）
- **Node.js** - MCP 服务器运行
- **VS Code** - 代码编辑

---

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/claude-code-instruction-system.git
cd claude-code-instruction-system
```

### 2. 验证安装

```bash
# 运行集成测试
bash scripts/test-integrations.sh

# 应该看到：
# 总测试数: 24
# 通过: 24 ✅
# 失败: 0
```

### 3. 检查配置文件

```bash
# 验证 JSON 格式
python -m json.tool config/keywords.json
python -m json.tool config/mcp-servers.json
python -m json.tool .claude/context/index.json

# 应该没有错误输出
```

---

## 基础配置

### 1. 全局配置

编辑 `~/.claude/settings.json`：

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your-api-key-here"
  },
  "model": "claude-sonnet-4-5-20250929",
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline/hud.sh render"
  }
}
```

### 2. 项目配置

编辑 `.claude/settings.json`（可选）：

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash ./.claude/statusline/hud.sh render"
  }
}
```

### 3. MCP 服务器配置

如果使用 Zotero（推荐）：

```bash
# 1. 注册 Zotero 账号
# 访问: https://www.zotero.org/user/register

# 2. 获取 API Key
# 访问: https://www.zotero.org/settings/keys

# 3. 设置环境变量
export ZOTERO_API_KEY=your_api_key_here

# 4. 验证配置
cat config/mcp-servers.json | grep zotero
```

---

## 第一个任务

### 示例 1: 文献精读（交互模式）

```markdown
# 在 Claude Code 中输入：
帮我解读这篇文献 "Attention Is All You Need"

# 系统会：
1. 从 Zotero 获取全文（如果配置了）
2. 提供整体概览
3. 逐图解读（每张图后停顿确认）
4. 总结与启发
```

### 示例 2: 文献精读（报告模式）

```markdown
# 在 Claude Code 中输入：
生成这篇文献的精读报告 "Deep Residual Learning for Image Recognition"

# 系统会：
1. 自动识别文献类型 → Research Article
2. 采用 Template A 生成完整报告
3. 输出包含：
   - 元数据和核心内容
   - 逻辑复盘（起承转合）
   - 技术深挖（ResNet 直觉解释）
   - 图表详解（消融实验分析）
   - 评分系统（8.5/10）
   - TODO List（复现 ResNet-50）
   - 推荐阅读（Methods 3.3 节）
```

### 示例 3: Agent 编排

```bash
# 复杂任务自动编排
/orchestrate

# 系统会：
1. 分析任务特征
2. 选择最优编排策略
3. 分配和调度 Agent
4. 监控执行并整合结果
```

---

## 常用功能

### 文献管理

```markdown
# 交互模式（深度学习）
"帮我解读这篇文献 'Attention Is All You Need'"

# 报告模式（快速调研）
"生成这篇文献的精读报告 'Deep Residual Learning'"

# 批量处理
"为 Zotero 集合 'Deep Learning' 生成精读报告"

# 通过 DOI
"解读 DOI: 10.1038/s41586-021-03819-2"
```

### Agent 编排

```bash
# 智能编排
/orchestrate

# 并行执行
/parallel

# 群体执行（大规模任务）
/swarm
```

### 自主执行

```bash
# Ralph Loop - 自主循环执行
/ralph "完成所有待办事项"

# Autopilot - 全自主执行模式
/autopilot "开发用户认证系统"

# 查看状态
/ralph status
/autopilot status
```

### 质量保障

```bash
# 生成功能规范
/agent spec-writer

# 执行 QA 审查
/agent qa-reviewer

# 自动修复问题
/agent qa-fixer
```

---

## 故障排查

### 问题 1: 测试失败

```bash
# 症状
bash scripts/test-integrations.sh
# 输出: 有 X 个测试失败

# 解决方案
# 1. 检查缺失的文件
ls -la .claude/skills/literature-mentor/
ls -la config/

# 2. 验证 JSON 格式
python -m json.tool config/keywords.json

# 3. 检查 Git 配置
git config core.autocrlf
```

### 问题 2: Zotero 连接失败

```bash
# 症状
"无法连接到 Zotero"

# 解决方案
# 1. 检查 API Key
echo $ZOTERO_API_KEY

# 2. 验证 MCP 配置
cat config/mcp-servers.json | grep zotero

# 3. 测试连接
# 在 Claude Code 中输入：
"列出我的 Zotero 集合"
```

### 问题 3: 文件路径错误

```bash
# 症状
"找不到文件: .claude/skills/literature-mentor/SKILL.md"

# 解决方案
# 1. 检查文件是否存在
ls -la .claude/skills/literature-mentor/SKILL.md

# 2. 如果不存在，从全局目录复制
cp "C:\Users\ASUS\.claude\skills\literature-mentor\SKILL.md" \
   ".claude/skills/literature-mentor/SKILL.md"

# 3. 验证文件
cat .claude/skills/literature-mentor/SKILL.md | head -20
```

### 问题 4: JSON 格式错误

```bash
# 症状
python -m json.tool config/keywords.json
# 输出: Expecting property name enclosed in double quotes

# 解决方案
# 1. 使用在线 JSON 验证器
# 访问: https://jsonlint.com/

# 2. 检查常见错误
# - 缺少逗号
# - 多余的逗号
# - 单引号（应该用双引号）
# - 未转义的特殊字符

# 3. 重新生成配置文件
cat > config/keywords.json << 'EOF'
{
  "version": "1.0.0",
  "skills": {
    "literature-mentor": {
      "keywords": ["解读", "精读"],
      "priority": "high"
    }
  }
}
EOF
```

---

## 下一步

### 深入学习

1. **阅读核心文档**
   - [CLAUDE.md](../CLAUDE.md) - 核心配置和指令
   - [配置文件指南](./CONFIG-FILES-GUIDE.md) - 详细配置说明

2. **探索 Agent 和 Skills**
   - [Agent 索引](../agents/INDEX.md) - 所有可用 Agent
   - [Skills 索引](../skills/INDEX.md) - 所有可用 Skills

3. **查看示例**
   - [科研工作流示例](../examples/research-workflow-example.md)
   - [编排系统示例](../examples/orchestration-examples.md)

### 进阶功能

1. **自定义 Agent**
   - 创建自己的 Agent 定义
   - 参考 `agents/` 目录中的示例

2. **自定义 Skill**
   - 创建自己的 Skill
   - 参考 `.claude/skills/` 目录中的示例

3. **自定义命令**
   - 创建自己的命令
   - 参考 `commands/` 目录中的示例

### 社区参与

1. **报告问题**
   - [GitHub Issues](https://github.com/YOUR_USERNAME/claude-code-instruction-system/issues)

2. **贡献代码**
   - 阅读 [贡献指南](../CONTRIBUTING.md)
   - 提交 Pull Request

3. **参与讨论**
   - [GitHub Discussions](https://github.com/YOUR_USERNAME/claude-code-instruction-system/discussions)

---

## 获取帮助

### 文档资源

- [README](../README.md) - 项目概述
- [CHANGELOG](../CHANGELOG.md) - 变更日志
- [CONTRIBUTING](../CONTRIBUTING.md) - 贡献指南

### 社区支持

- **GitHub Issues** - 问题反馈
- **GitHub Discussions** - 一般讨论
- **Pull Requests** - 代码贡献

---

<p align="center">
  <strong>祝您使用愉快！</strong>
</p>

<p align="center">
  如有问题，请随时在 GitHub 上提问。
</p>

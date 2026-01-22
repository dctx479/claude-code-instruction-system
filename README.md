# Claude Code CLI 完整提示词/自定义指令体系

> 版本: 1.0 | 适用领域: 软件开发、网络安全(CTF)、人工智能(智能体)、数据分析

本项目提供一套完善的基于 Claude Code CLI 的提示词和自定义指令体系，涵盖多个专业领域的研究学习需求。

## 目录结构

```
claude-code-instruction-system/
├── README.md                          # 本文件
├── CLAUDE.md                          # 全局核心配置模板
├── config/
│   ├── settings.json                  # Claude Code 设置配置
│   └── mcp-servers.json              # MCP 服务器配置
├── commands/                          # 自定义 Slash 命令
│   ├── general/                       # 通用命令
│   ├── dev/                          # 软件开发命令
│   ├── security/                      # 网络安全命令
│   ├── ai-agent/                      # AI智能体命令
│   └── data-analysis/                 # 数据分析命令
├── agents/                            # 自定义子代理
│   ├── code-reviewer.md              # 代码审查代理
│   ├── debugger.md                    # 调试专家代理
│   ├── security-analyst.md            # 安全分析代理
│   ├── data-scientist.md              # 数据科学家代理
│   └── architect.md                   # 架构师代理
├── templates/                         # CLAUDE.md 模板
│   ├── software-dev.md               # 软件开发模板
│   ├── ctf-security.md               # 网络安全/CTF模板
│   ├── ai-agent.md                    # AI智能体开发模板
│   └── data-analysis.md              # 数据分析模板
├── hooks/                             # 生命周期钩子
│   └── hooks.json                     # 钩子配置
└── workflows/                         # 工作流模式
    ├── tdd-workflow.md               # 测试驱动开发
    ├── security-audit.md              # 安全审计流程
    └── multi-agent.md                 # 多代理编排
```

## 快速开始

### 1. 安装全局配置

将 `CLAUDE.md` 复制到 `~/.claude/CLAUDE.md` 作为全局配置。

### 2. 项目级配置

根据项目类型，从 `templates/` 目录选择合适的模板，复制到项目根目录。

### 3. 安装自定义命令

```bash
# 复制命令到项目目录
cp -r commands/* .claude/commands/

# 或复制到用户目录(全局可用)
cp -r commands/* ~/.claude/commands/
```

### 4. 配置子代理

```bash
cp -r agents/* .claude/agents/
```

### 5. 配置 MCP 服务器

```bash
claude mcp add-json github '{"command":"npx","args":["-y","@modelcontextprotocol/server-github"]}'
```

## 核心原则

1. **保持简洁**: CLAUDE.md 控制在 150-200 条指令以内
2. **迭代优化**: 持续根据使用反馈优化配置
3. **使用指针**: 引用文件而非复制代码片段
4. **分层配置**: 全局 → 项目 → 本地 的配置优先级
5. **专业化代理**: 为不同任务创建专门的子代理

## 参考资源

- [Claude Code 官方文档](https://code.claude.com/docs)
- [Claude Code 最佳实践](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Awesome Claude Code](https://github.com/hesreallyhim/awesome-claude-code)

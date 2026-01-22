# Claude Code CLI 快速参考

## 常用命令

### 基础命令
```bash
claude                    # 启动交互式会话
claude "任务描述"          # 单次执行任务
claude --resume           # 恢复上次会话
claude --continue         # 继续会话并显示历史
claude --mcp-debug        # MCP 调试模式
```

### Slash 命令
```
/help              # 显示帮助
/clear             # 清除上下文
/init              # 初始化项目 CLAUDE.md
/config            # 查看配置
/permissions       # 管理权限
/agents            # 管理子智能体
/cost              # 显示成本信息
```

### MCP 管理
```bash
claude mcp add <name> <command> [args...]   # 添加服务器
claude mcp add-json <name> '<json>'         # JSON 方式添加
claude mcp list                              # 列出服务器
claude mcp remove <name>                     # 移除服务器
claude mcp get <name>                        # 测试服务器
```

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Tab` | 切换思考模式 |
| `#` | 添加指令到 CLAUDE.md |
| `Esc` | 中断当前操作 |
| `Ctrl+C` | 取消 |
| `Ctrl+B` | 后台运行 |

## 配置文件位置

```
~/.claude/
├── CLAUDE.md           # 全局指令
├── settings.json       # 全局设置
├── commands/           # 全局命令
└── agents/             # 全局智能体

.claude/
├── commands/           # 项目命令
├── agents/             # 项目智能体
└── .mcp.json          # 项目 MCP 配置
```

## 子智能体定义

```yaml
---
name: agent-name
description: 何时使用此智能体
tools: Read, Write, Edit, Bash
model: sonnet | haiku | opus
permissionMode: default | acceptEdits | dontAsk
---

[系统提示词]
```

## 自定义命令

```markdown
# .claude/commands/命令名.md

执行任务: $ARGUMENTS

## 步骤
1. 步骤一
2. 步骤二
```

使用: `/project:命令名 参数`

## Hooks 配置

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write",
      "hooks": [{"type": "command", "command": "脚本"}]
    }],
    "PostToolUse": [...],
    "Notification": [...],
    "Stop": [...]
  }
}
```

## 权限配置

```json
{
  "permissions": {
    "allow": ["Bash(npm *)", "Read", "Write"],
    "deny": ["Bash(rm -rf *)"]
  }
}
```

## 提示词技巧

### 强化指令
- `IMPORTANT:` 强调重要内容
- `YOU MUST` 必须遵守
- `NEVER` 禁止事项

### 常用模式
```
# 角色设定
作为 [角色], 你需要 [任务]

# 步骤分解
请按以下步骤执行:
1. ...

# 约束条件
注意: 不要 [禁止事项]

# 输出格式
请以以下格式输出:
...
```

## 常见工作流

### 修复问题
```
1. 读取相关文件理解问题
2. 分析根本原因
3. 实施最小修复
4. 验证修复
```

### 添加功能
```
1. 理解需求
2. 设计方案
3. 编写测试
4. 实现功能
5. 验证通过
```

### 代码审查
```
1. 查看变更
2. 检查质量
3. 检查安全
4. 提供反馈
```

## 快速诊断

| 问题 | 解决方案 |
|------|----------|
| 响应慢 | 使用更快的模型或子智能体 |
| 上下文满 | `/clear` 清理 |
| 不遵循指令 | 强化指令或减少指令数 |
| 工具失败 | 检查权限和网络 |

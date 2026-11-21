# Claude Code CLI 快速参考

## 本仓库规则治理

- `AGENTS.md`：跨工具项目约定；`CLAUDE.md`：Claude 专用入口并引用前者。
- `config/claude-global.md`：全局安装模板，不再复制项目入口。
- `/rule-audit`：只读体检，输出证据和 diff；`/evolve`：重复事故先查两次证据。
- `python scripts/audit-rules.py --strict`：机器检查；`/check` 按真实技术栈选择验证。
- 路由建议来自 UserPromptSubmit 本轮 stdout；旧全局快照仅供 HUD 显示。
- 更新后先 dry-run，需全局生效时再运行安装器并重启会话。

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

使用: `/命令名 参数`

## Hooks 配置

hooks 只从 `settings.json` 加载。本系统的全局 hooks 定义在 `hooks/hooks.json`，用 `python scripts/install-global.py` 合并进 `~/.claude/settings.json`：

```json
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Bash", "hooks": [
        {"type": "command", "command": "bash \"$HOME/.claude/scripts/validate/validate-command.sh\"", "timeout": 5},
        {"type": "command", "command": "python \"$HOME/.claude/scripts/port-management/port-check-hook.py\"", "timeout": 5}]},
      {"matcher": "Agent|Task", "hooks": [
        {"type": "command", "command": "bash \"$HOME/.claude/hooks/agent-tracker.sh\"", "timeout": 5}]}
    ],
    "PostToolUse": [{"matcher": "Edit", "hooks": [
      {"type": "command", "command": "bash \"$HOME/.claude/scripts/hooks/post-edit.sh\"", "timeout": 30}]}],
    "UserPromptSubmit": [{"hooks": [
      {"type": "command", "command": "bash \"$HOME/.claude/hooks/intent-detector.sh\"", "timeout": 10}]}],
    "Notification": [{"hooks": [
      {"type": "command", "command": "bash \"$HOME/.claude/scripts/hooks/notify.sh\"", "timeout": 15}]}],
    "Stop": [{"hooks": [
      {"type": "command", "command": "bash \"$HOME/.claude/hooks/ralph-stop-interceptor.sh\"", "timeout": 15}]}],
    "SessionEnd": [{"hooks": [
      {"type": "command", "command": "bash \"$HOME/.claude/scripts/hooks/on-stop.sh\"", "timeout": 15}]}],
    "PreCompact": [{"hooks": [
      {"type": "command", "command": "bash \"$HOME/.claude/hooks/pre-compact.sh\"", "timeout": 10}]}]
  }
}
```

| 规则 | 说明 |
|------|------|
| `timeout` | 单位是秒 |
| 退出码 | `0` 放行；`2` 阻塞（Stop 时 = 继续对话，stderr 反馈给 Claude）；其他为非阻塞错误 |
| 输入 | stdin JSON（`prompt` / `tool_name` / `tool_input` / `tool_response`） |
| 路径 | 全局用 `$HOME/.claude/...`，项目用 `$CLAUDE_PROJECT_DIR/...`，不用 `./` |

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

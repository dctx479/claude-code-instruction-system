# Hooks 脚本使用指南

**版本**: 1.0.0
**更新日期**: 2026-01-24
**适用系统**: 太一元系统 v3.1.0

---

## 📋 脚本清单

本目录包含 4 个核心 Hook 脚本，用于增强 Claude Code 的功能：

| 脚本 | 触发时机 | 用途 | 超时时间 |
|------|----------|------|----------|
| validate-command.sh | PreToolUse (Bash) | 验证 Bash 命令安全性 | 5秒 |
| post-edit.sh | PostToolUse (Edit) | 编辑后运行 lint 检查 | 30秒 |
| notify.sh | Notification | 发送通知到外部系统 | 无限制 |
| on-stop.sh | Stop | 会话结束清理操作 | 无限制 |

---

## 🛡️ validate-command.sh - 命令安全验证

### 功能

在执行 Bash 命令前进行安全检查，防止危险操作。

### 安全规则

1. **🔴 阻止（exit 2）**:
   - 递归删除系统目录 (`rm -rf /`, `rm -rf ~`)
   - 磁盘格式化命令 (`mkfs`, `fdisk`, `parted`)
   - 代码注入模式 (`;rm`, `fork bomb`)

2. **🟡 警告（exit 1）**:
   - 提权命令 (`sudo`, `su`)
   - 不安全权限 (`chmod 777`, `chmod 666`)
   - 网络操作与重定向组合

3. **🟢 通过（exit 0）**:
   - 所有其他命令

### 配置

```json
{
  "matcher": {"tools": ["Bash"]},
  "hooks": [{
    "type": "command",
    "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"./scripts/validate-command.sh\"",
    "timeout": 5000
  }]
}
```

### 自定义规则

编辑脚本中的正则表达式来添加自定义规则：

```bash
# 添加自定义阻止规则
if echo "$COMMAND" | grep -E 'your-pattern' > /dev/null; then
    echo "❌ BLOCKED: Your custom reason" >&2
    exit 2
fi
```

---

## 🔧 post-edit.sh - 编辑后处理

### 功能

在文件编辑后自动运行代码质量检查和格式化工具。

### 支持的工具

#### JavaScript/TypeScript
- **ESLint** - 代码检查和自动修复
- **Prettier** - 代码格式化

#### Python
- **Black** - 代码格式化
- **Ruff** - 快速 linter 和自动修复

### 日志

所有操作记录到 `~/.claude/post-edit.log`：

```
[2026-01-24 10:30:15] Post-edit hook triggered
  File: src/app.ts
  Running ESLint...
  Running Prettier...
  ✓ Post-edit hook completed
```

### 配置

```json
{
  "matcher": {"tools": ["Edit"]},
  "hooks": [{
    "type": "command",
    "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"./scripts/post-edit.sh\"",
    "timeout": 30000
  }]
}
```

### 可选功能

脚本中默认禁用的功能（取消注释可启用）：

```bash
# Git 自动暂存
if [ -n "$FILE_PATH" ] && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git add "$FILE_PATH" 2>/dev/null || true
fi
```

---

## 📢 notify.sh - 通知系统

### 功能

发送 Claude Code 事件通知到多种渠道。

### 支持的通知渠道

1. **本地日志** - `~/.claude/notifications.log`
2. **Webhook** - 自定义 HTTP 端点
3. **Slack** - Slack Incoming Webhook
4. **Discord** - Discord Webhook
5. **桌面通知**:
   - Windows: PowerShell 气泡通知
   - macOS: osascript 通知
   - Linux: notify-send

### 配置环境变量

```bash
# 自定义 Webhook
export CLAUDE_WEBHOOK_URL="https://your-webhook.com/endpoint"

# Slack
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Discord
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR/WEBHOOK"
```

### 使用示例

```bash
# 手动触发通知
export NOTIFICATION_TYPE="task_complete"
export NOTIFICATION_MESSAGE="任务已完成"
./scripts/notify.sh
```

### 日志轮转

自动保持最近 1000 条通知记录。

---

## 🧹 on-stop.sh - 会话清理

### 功能

在 Claude Code 会话结束时自动执行清理和保存操作。

### 执行的操作

1. **清理临时文件**
   - `/tmp/claude-*`
   - `/tmp/cc-*`
   - `.claude-tmp/` 目录

2. **保存会话统计**
   - 总会话数
   - 最后结束时间
   - 工作目录

3. **备份未提交更改**（如果有 Git 更改）
   - 创建 diff 文件
   - 保存到 `~/.claude/backups/YYYYMMDD/`

4. **生成会话摘要**（可选）
   - 结束时间
   - 工作目录
   - Git 分支
   - 修改的文件列表

5. **日志轮转**
   - 保持最近 500 条记录

### 配置

```json
{
  "hooks": [{
    "type": "command",
    "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"./scripts/on-stop.sh\""
  }]
}
```

### 启用会话摘要

```bash
export CLAUDE_GENERATE_SESSION_SUMMARY=true
```

### 日志位置

- 主日志: `~/.claude/session-stop.log`
- 统计数据: `~/.claude/session-stats.json`
- 会话摘要: `~/.claude/session-summaries/YYYYMMDD-HHMMSS.md`

---

## 🔧 通用配置

### 环境变量

所有脚本可以访问以下 Claude Code 环境变量：

| 变量 | 说明 | 示例 |
|------|------|------|
| `TOOL_NAME` | 工具名称 | `"Bash"`, `"Edit"` |
| `TOOL_INPUT` | 工具输入 (JSON) | `{"command": "ls"}` |
| `TOOL_OUTPUT` | 工具输出 (PostToolUse) | 命令的标准输出 |
| `SESSION_ID` | 会话 ID | UUID 字符串 |

### 退出状态码

| 状态码 | 含义 | 行为 |
|--------|------|------|
| 0 | 成功 | 继续执行工具 |
| 1 | 警告 | 记录警告并继续 |
| 2 | 阻止 | 阻止工具执行 |

### 脚本权限

确保脚本有可执行权限：

```bash
chmod +x scripts/*.sh
```

---

## 📊 监控和调试

### 查看日志

```bash
# 命令验证日志
tail -f ~/.claude/command-validation.log

# 编辑后处理日志
tail -f ~/.claude/post-edit.log

# 通知日志
tail -f ~/.claude/notifications.log

# 会话停止日志
tail -f ~/.claude/session-stop.log
```

### 测试脚本

```bash
# 测试命令验证
echo '{"tool_input":{"command":"ls -la"}}' | ./scripts/validate-command.sh
echo $?  # 应该返回 0

# 测试危险命令
echo '{"tool_input":{"command":"rm -rf /"}}' | ./scripts/validate-command.sh
echo $?  # 应该返回 2

# 测试通知
export NOTIFICATION_MESSAGE="Test notification"
./scripts/notify.sh

# 测试清理
./scripts/on-stop.sh
```

---

## 🎨 自定义和扩展

### 添加新的安全规则

编辑 `validate-command.sh`，在安全检查部分添加：

```bash
# 7. 检查自定义危险命令
if echo "$COMMAND" | grep -E 'your-dangerous-command' > /dev/null; then
    echo "❌ BLOCKED: Custom security rule triggered" >&2
    exit 2
fi
```

### 添加新的 Linter

编辑 `post-edit.sh`，在检测项目类型部分添加：

```bash
# Rust 项目
if [ -f "Cargo.toml" ]; then
    if command -v rustfmt >/dev/null 2>&1; then
        echo "  Running rustfmt..." >> "$LOG_FILE"
        rustfmt "$FILE_PATH" 2>/dev/null || true
    fi
fi
```

### 添加新的通知渠道

编辑 `notify.sh`，在发送到外部系统部分添加：

```bash
# 7. 发送到 Telegram
if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d "chat_id=$TELEGRAM_CHAT_ID" \
        -d "text=🤖 Claude Code: $MESSAGE" \
        >/dev/null 2>&1 || true
fi
```

---

## ❓ 常见问题

### Q: 脚本没有执行？

**A**: 检查以下几点：
1. 脚本有可执行权限：`ls -l scripts/*.sh`
2. Git Bash 路径正确：`python scripts/detect-git-bash.py`
3. Hooks 配置正确：`python scripts/validate-config.py`
4. 查看日志文件确认是否有错误

### Q: Windows 环境下路径问题？

**A**: 确保使用完整的 Git Bash 路径和正确的转义：
```json
"command": "\"C:\\\\Program Files\\\\Git\\\\bin\\\\bash.exe\" \"./scripts/script.sh\""
```

### Q: 如何禁用某个脚本？

**A**: 在 hooks.json 中注释掉或删除对应的 hook 配置。

### Q: 脚本执行超时？

**A**: 增加 timeout 值或优化脚本性能：
```json
"timeout": 60000  // 60秒
```

### Q: 如何查看脚本执行结果？

**A**: 查看各脚本的日志文件（位于 `~/.claude/` 目录）。

---

## 🔗 相关文档

- [Hooks 配置格式规范](../CLAUDE.md#八进化指令)
- [配置验证快速参考](../docs/QUICK-REFERENCE-CONFIG-VALIDATION.md)
- [Hooks 格式修复报告](../HOOKS-FORMAT-FIX.md)
- [配置验证命令](../commands/general/validate-config.md)

---

## 📝 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-01-24 | 初始版本，创建 4 个核心脚本 |

---

**维护人员**: 太一元系统开发团队
**文档版本**: 1.0.0

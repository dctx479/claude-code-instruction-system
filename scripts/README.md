# Hooks 脚本使用指南

**版本**: 1.1.0
**更新日期**: 2026-11-19
**适用系统**: 太一元系统 v1.4

> 这些脚本通过 `python scripts/install-global.py` 安装到 `~/.claude/scripts/`，对应的 hook 条目来自 `hooks/hooks.json`（合并进 `~/.claude/settings.json`）。下文的配置片段仅作格式示意：`timeout` 单位是秒；全局 hook 的脚本路径写 `$HOME/.claude/scripts/...`。

## 规则治理

完整验证使用独立 venv：`python -m venv .claude-tmp/validation-venv`，激活后运行
`python -m pip install -r scripts/requirements-validation.txt`。PyYAML 仅供开发/CI 的 Skill/YAML 校验，Hook 运行时不依赖它。
Windows 的解释器位于 `.claude-tmp/validation-venv/Scripts/python.exe`，Linux/macOS 位于 `.claude-tmp/validation-venv/bin/python`。

- `python scripts/audit-rules.py --strict`：只读检查规则清单、行数/字节、@ 导入、目录链预算及可识别命令；错误或预算告警退出非零。
- `python scripts/audit-skills.py`：验证全部 Skill 的可移植 frontmatter；版本、触发词和其他自定义字段放 metadata，compatibility 是合法的可选顶层字段。
- 本机 Skill Creator 的旧 quick_validate 只接受五个字段；本仓库的完整检查遵循六字段标准并保留 compatibility，不能为通过旧校验器而删除合法运行环境说明。
- `--json` 输出结构化结果；`--global-file PATH` 显式选择全局文件作重复比较，不默认扫描个人目录。
- `review` 项表示路径/命令的上下文尚不能确定，不自动删除，也不当成过期事实；它们不导致 strict 失败，审计时仍须人工处理。
- 不支持的命令别名、Make/Cargo/CI 语义和规则冲突由 `/rule-audit` 阅读核对，机器结果不是完整语义审查。
- `python -m unittest discover -s tests -p "test_*.py" -v`：临时目录测试审计、core 安装和真实 Hook 输入输出。
- `bash scripts/test-all-intents.sh`：仅运行路由回归；不修改真实 HOME，不依赖已安装的 Hook。
- 安装后从仓库运行 `python scripts/verify-global-install.py --smoke-hook`：比较托管源文件与实际安装副本，临时 HOME 调用已安装 Hook；任何缺失、差异或烟测失败均非零退出。
- `--target DIR` 可验证沙箱；`--repo DIR` 显式指定源仓库。校验器跳过有状态知识源，不以“必须等于仓库”为由覆盖个人记忆。
- `bash scripts/verify-agent-dispatch.sh` 是上述已安装验证的兼容入口；不再写真实全局路由快照、不读取废弃的 intent.log。

---

## 📋 脚本清单

本目录包含 4 个核心 Hook 脚本，用于增强 Claude Code 的功能：

| 脚本 | 触发时机 | 用途 | 超时时间 |
|------|----------|------|----------|
| validate-command.sh | PreToolUse (Bash) | 验证 Bash 命令安全性 | 5秒 |
| post-edit.sh | PostToolUse (Edit) | 编辑后运行 lint 检查 | 30秒 |
| notify.sh | Notification | 发送通知到外部系统 | 15秒 |
| on-stop.sh | SessionEnd | 会话结束时保存统计与未提交改动备份 | 15秒 |

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
  "matcher": "Bash",
  "hooks": [{
    "type": "command",
    "command": "bash \"./scripts/validate-command.sh\"",
    "timeout": 5
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
  "matcher": "Edit",
  "hooks": [{
    "type": "command",
    "command": "bash \"./scripts/post-edit.sh\"",
    "timeout": 30
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
    "command": "bash \"./scripts/on-stop.sh\""
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

### 输入数据

Claude Code 通过 **stdin JSON** 把事件数据传给脚本，没有 `TOOL_NAME` / `TOOL_INPUT` 之类的环境变量：

| stdin 字段 | 说明 | 出现的事件 |
|------------|------|-----------|
| `session_id` / `cwd` / `hook_event_name` | 公共字段 | 全部 |
| `tool_name` / `tool_input` | 工具名称与参数 | PreToolUse、PostToolUse |
| `tool_response` | 工具返回结果 | PostToolUse |
| `prompt` | 用户输入 | UserPromptSubmit |
| `message` | 通知内容 | Notification |

环境变量只有 `CLAUDE_PROJECT_DIR`（项目根目录）可依赖。

### 退出状态码

| 状态码 | 含义 | 行为 |
|--------|------|------|
| 0 | 成功 | 继续执行 |
| 2 | 阻塞 | PreToolUse 阻止工具执行；Stop 阻止停止并继续对话；stderr 反馈给 Claude |
| 其他 | 非阻塞错误 | 记录后照常继续（包括 1 和 3） |

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
"command": "bash \"./scripts/script.sh\""
```

### Q: 如何禁用某个脚本？

**A**: 在 hooks.json 中注释掉或删除对应的 hook 配置。

### Q: 脚本执行超时？

**A**: 增加 timeout 值或优化脚本性能：
```json
"timeout": 60  // 60秒
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

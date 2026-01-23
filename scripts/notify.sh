#!/bin/bash
# 通知系统脚本
# 版本: 1.0.0
# 用途: 发送 Claude Code 事件通知到外部系统

# 配置
NOTIFICATION_LOG="${HOME}/.claude/notifications.log"
NOTIFICATION_DIR="$(dirname "$NOTIFICATION_LOG")"

# 确保日志目录存在
mkdir -p "$NOTIFICATION_DIR" 2>/dev/null

# ============================================================
# 获取通知内容
# ============================================================

# 从环境变量获取通知信息
EVENT_TYPE="${NOTIFICATION_TYPE:-general}"
MESSAGE="${NOTIFICATION_MESSAGE:-Claude Code notification}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# ============================================================
# 记录到日志文件
# ============================================================

cat >> "$NOTIFICATION_LOG" <<EOF
[$TIMESTAMP] [$EVENT_TYPE] $MESSAGE
EOF

# ============================================================
# 发送到外部系统（可选）
# ============================================================

# 1. 发送到 Webhook（如果配置了 URL）
if [ -n "$CLAUDE_WEBHOOK_URL" ]; then
    curl -s -X POST "$CLAUDE_WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"event\":\"$EVENT_TYPE\",\"message\":\"$MESSAGE\",\"timestamp\":\"$TIMESTAMP\"}" \
        >/dev/null 2>&1 || true
fi

# 2. 发送到 Slack（如果配置了 Webhook）
if [ -n "$SLACK_WEBHOOK_URL" ]; then
    curl -s -X POST "$SLACK_WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"text\":\"🤖 Claude Code: $MESSAGE\"}" \
        >/dev/null 2>&1 || true
fi

# 3. 发送到 Discord（如果配置了 Webhook）
if [ -n "$DISCORD_WEBHOOK_URL" ]; then
    curl -s -X POST "$DISCORD_WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"content\":\"🤖 **Claude Code Notification**\\n$MESSAGE\"}" \
        >/dev/null 2>&1 || true
fi

# 4. Windows 桌面通知（如果在 Windows 环境）
if command -v powershell.exe >/dev/null 2>&1; then
    powershell.exe -Command "
        Add-Type -AssemblyName System.Windows.Forms
        \$notification = New-Object System.Windows.Forms.NotifyIcon
        \$notification.Icon = [System.Drawing.SystemIcons]::Information
        \$notification.BalloonTipIcon = 'Info'
        \$notification.BalloonTipText = '$MESSAGE'
        \$notification.BalloonTipTitle = 'Claude Code'
        \$notification.Visible = \$True
        \$notification.ShowBalloonTip(3000)
    " 2>/dev/null || true
fi

# 5. macOS 桌面通知
if command -v osascript >/dev/null 2>&1; then
    osascript -e "display notification \"$MESSAGE\" with title \"Claude Code\" sound name \"default\"" 2>/dev/null || true
fi

# 6. Linux 桌面通知
if command -v notify-send >/dev/null 2>&1; then
    notify-send "Claude Code" "$MESSAGE" 2>/dev/null || true
fi

# ============================================================
# 日志轮转（保持最近 1000 条）
# ============================================================

if [ -f "$NOTIFICATION_LOG" ]; then
    LINE_COUNT=$(wc -l < "$NOTIFICATION_LOG")
    if [ "$LINE_COUNT" -gt 1000 ]; then
        tail -n 1000 "$NOTIFICATION_LOG" > "${NOTIFICATION_LOG}.tmp"
        mv "${NOTIFICATION_LOG}.tmp" "$NOTIFICATION_LOG"
    fi
fi

exit 0

#!/bin/bash
# 会话结束清理脚本
# 版本: 1.2.0
# 触发时机: SessionEnd（不是 Stop —— Stop 每轮对话结束都会触发，会把每一轮都记成一次会话）
# 用途: 在 Claude Code 会话结束时保存统计和未提交改动的备份

set -uo pipefail

# 配置
CLAUDE_DIR="${HOME}/.claude"
LOG_FILE="${CLAUDE_DIR}/session-stop.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 确保目录存在
mkdir -p "$CLAUDE_DIR" 2>/dev/null

# 安全: 获取并转义工作目录
SAFE_PWD=$(pwd | tr -d '"\\')

# ============================================================
# 记录会话结束
# ============================================================

echo "========================================" >> "$LOG_FILE"
echo "Session stopped at: $TIMESTAMP" >> "$LOG_FILE"
echo "Working directory: $SAFE_PWD" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# ============================================================
# 1. （已移除）清理临时文件
# ============================================================
# 原先这里会执行 rm -f /tmp/claude-* 和 rm -rf .claude-tmp。
# 通配删除违反 CLAUDE.md §七「禁止批量删除文件」，而且 /tmp/claude-* 里有
# 其他仍在运行的 Claude Code 会话的工作文件，因此不再自动清理。

# ============================================================
# 2. 保存会话统计
# ============================================================

STATS_FILE="${CLAUDE_DIR}/session-stats.json"

# 如果统计文件存在，更新计数
if [ -f "$STATS_FILE" ]; then
    TOTAL_SESSIONS=$(jq -r '.total_sessions // 0' "$STATS_FILE" 2>/dev/null \
        || grep -o '"total_sessions"[[:space:]]*:[[:space:]]*[0-9]*' "$STATS_FILE" 2>/dev/null | grep -o '[0-9]*$' \
        || echo "0")
    [[ "$TOTAL_SESSIONS" =~ ^[0-9]+$ ]] || TOTAL_SESSIONS=0
    TOTAL_SESSIONS=$((TOTAL_SESSIONS + 1))
else
    TOTAL_SESSIONS=1
fi

# 使用 printf 安全写入 JSON，避免 heredoc 注入
printf '{\n  "total_sessions": %d,\n  "last_session_end": "%s",\n  "last_working_dir": "%s"\n}\n' \
    "$TOTAL_SESSIONS" "$TIMESTAMP" "$SAFE_PWD" > "$STATS_FILE"

echo "Session stats updated: $TOTAL_SESSIONS total sessions" >> "$LOG_FILE"

# ============================================================
# 3. 备份重要文件（可选）
# ============================================================

# 如果有未提交的 Git 更改，创建备份
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if ! git diff --quiet 2>/dev/null; then
        BACKUP_DIR="${CLAUDE_DIR}/backups/$(date '+%Y%m%d')"
        mkdir -p "$BACKUP_DIR" 2>/dev/null

        # 创建 diff 备份
        git diff > "${BACKUP_DIR}/unsaved-changes-$(date '+%H%M%S').patch" 2>/dev/null || true
        echo "  Created backup of unsaved changes" >> "$LOG_FILE"
    fi
fi

# ============================================================
# 4. 生成会话摘要（如果启用）
# ============================================================

if [ "${CLAUDE_GENERATE_SESSION_SUMMARY:-false}" = "true" ]; then
    SUMMARY_FILE="${CLAUDE_DIR}/session-summaries/$(date '+%Y%m%d-%H%M%S').md"
    mkdir -p "$(dirname "$SUMMARY_FILE")" 2>/dev/null

    GIT_BRANCH=$(git branch --show-current 2>/dev/null || echo "N/A")
    GIT_DIFF=$(git diff --name-only 2>/dev/null || echo "N/A")
    GIT_STATUS=$(git status --short 2>/dev/null || echo "Not a git repository")

    cat > "$SUMMARY_FILE" <<'SUMMARYEOF'
# Claude Code Session Summary
SUMMARYEOF
    {
        echo ""
        echo "**End Time**: $TIMESTAMP"
        echo "**Working Directory**: $SAFE_PWD"
        echo "**Git Branch**: $GIT_BRANCH"
        echo ""
        echo "## Files Modified"
        echo "$GIT_DIFF"
        echo ""
        echo "## Git Status"
        echo '```'
        echo "$GIT_STATUS"
        echo '```'
    } >> "$SUMMARY_FILE"

    echo "  Generated session summary: $SUMMARY_FILE" >> "$LOG_FILE"
fi

# ============================================================
# 5. 触发通知（如果配置）
# ============================================================

NOTIFY_SCRIPT="$(dirname "$0")/notify.sh"
if [ -f "$NOTIFY_SCRIPT" ]; then
    export NOTIFICATION_TYPE="session_end"
    export NOTIFICATION_MESSAGE="Claude Code session ended at $TIMESTAMP"
    bash "$NOTIFY_SCRIPT" </dev/null >/dev/null 2>&1 || true
fi

# ============================================================
# 6. 日志轮转
# ============================================================

if [ -f "$LOG_FILE" ]; then
    LINE_COUNT=$(wc -l < "$LOG_FILE")
    if [ "$LINE_COUNT" -gt 500 ]; then
        tail -n 500 "$LOG_FILE" > "${LOG_FILE}.tmp"
        mv "${LOG_FILE}.tmp" "$LOG_FILE"
        echo "Log file rotated" >> "$LOG_FILE"
    fi
fi

# ============================================================
# 完成
# ============================================================

echo "✓ Cleanup completed successfully" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

exit 0

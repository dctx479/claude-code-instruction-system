#!/bin/bash
# 会话停止清理脚本
# 版本: 1.0.0
# 用途: 在 Claude Code 会话结束时执行清理和保存操作

# 配置
CLAUDE_DIR="${HOME}/.claude"
LOG_FILE="${CLAUDE_DIR}/session-stop.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 确保目录存在
mkdir -p "$CLAUDE_DIR" 2>/dev/null

# ============================================================
# 记录会话结束
# ============================================================

echo "========================================" >> "$LOG_FILE"
echo "Session stopped at: $TIMESTAMP" >> "$LOG_FILE"
echo "Working directory: $(pwd)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# ============================================================
# 1. 清理临时文件
# ============================================================

echo "Cleaning temporary files..." >> "$LOG_FILE"

# 清理 Claude Code 临时文件
rm -f /tmp/claude-* 2>/dev/null || true
rm -f /tmp/cc-* 2>/dev/null || true

# 清理项目临时文件（如果存在）
if [ -d ".claude-tmp" ]; then
    rm -rf .claude-tmp 2>/dev/null || true
    echo "  Removed .claude-tmp directory" >> "$LOG_FILE"
fi

# 清理编译产物（可选，谨慎使用）
# rm -rf node_modules/.cache 2>/dev/null || true
# rm -rf .pytest_cache 2>/dev/null || true

# ============================================================
# 2. 保存会话统计
# ============================================================

STATS_FILE="${CLAUDE_DIR}/session-stats.json"

# 如果统计文件存在，更新计数
if [ -f "$STATS_FILE" ]; then
    TOTAL_SESSIONS=$(jq -r '.total_sessions // 0' "$STATS_FILE" 2>/dev/null || echo "0")
    TOTAL_SESSIONS=$((TOTAL_SESSIONS + 1))
else
    TOTAL_SESSIONS=1
fi

cat > "$STATS_FILE" <<EOF
{
  "total_sessions": $TOTAL_SESSIONS,
  "last_session_end": "$TIMESTAMP",
  "last_working_dir": "$(pwd)"
}
EOF

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

if [ "$CLAUDE_GENERATE_SESSION_SUMMARY" = "true" ]; then
    SUMMARY_FILE="${CLAUDE_DIR}/session-summaries/$(date '+%Y%m%d-%H%M%S').md"
    mkdir -p "$(dirname "$SUMMARY_FILE")" 2>/dev/null

    cat > "$SUMMARY_FILE" <<EOF
# Claude Code Session Summary

**End Time**: $TIMESTAMP
**Working Directory**: $(pwd)
**Git Branch**: $(git branch --show-current 2>/dev/null || echo "N/A")

## Files Modified
$(git diff --name-only 2>/dev/null || echo "N/A")

## Git Status
\`\`\`
$(git status --short 2>/dev/null || echo "Not a git repository")
\`\`\`
EOF

    echo "  Generated session summary: $SUMMARY_FILE" >> "$LOG_FILE"
fi

# ============================================================
# 5. 触发通知（如果配置）
# ============================================================

if [ -f "./scripts/notify.sh" ]; then
    export NOTIFICATION_TYPE="session_end"
    export NOTIFICATION_MESSAGE="Claude Code session ended at $TIMESTAMP"
    ./scripts/notify.sh >/dev/null 2>&1 || true
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

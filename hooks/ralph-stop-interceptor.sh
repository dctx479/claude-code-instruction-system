#!/bin/bash
# Ralph Stop Interceptor - 自主循环执行系统的停止钩子
# 版本: 1.1.0
# 触发时机: Stop hook 被调用时
#
# 功能:
# 1. 检查是否在 Ralph 循环执行模式中
# 2. 如果是，检查任务是否完成
# 3. 如果任务未完成且没有致命错误，继续执行
# 4. 如果任务完成或遇到致命错误，允许停止

set -uo pipefail

# 配置
RALPH_STATE_FILE="${RALPH_STATE_FILE:-$HOME/.claude/ralph-state.json}"
RALPH_MAX_ITERATIONS="${RALPH_MAX_ITERATIONS:-10}"
RALPH_LOG_FILE="${RALPH_LOG_FILE:-$HOME/.claude/ralph.log}"

# 日志函数
log() {
    local level="$1"
    shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*" >> "$RALPH_LOG_FILE" 2>/dev/null || true
}

# 检查 Ralph 状态文件是否存在
if [[ ! -f "$RALPH_STATE_FILE" ]]; then
    log "INFO" "Ralph state file not found, allowing stop"
    exit 0
fi

# 读取状态（添加 fallback 防止 grep 失败）
RALPH_ACTIVE=$(grep -o '"active":[^,}]*' "$RALPH_STATE_FILE" 2>/dev/null | cut -d':' -f2 | tr -d ' ' || echo "false")
CURRENT_ITERATION=$(grep -o '"iteration":[^,}]*' "$RALPH_STATE_FILE" 2>/dev/null | cut -d':' -f2 | tr -d ' ' || echo "0")
TASK_COMPLETED=$(grep -o '"completed":[^,}]*' "$RALPH_STATE_FILE" 2>/dev/null | cut -d':' -f2 | tr -d ' ' || echo "false")
HAS_FATAL_ERROR=$(grep -o '"fatal_error":[^,}]*' "$RALPH_STATE_FILE" 2>/dev/null | cut -d':' -f2 | tr -d ' ' || echo "false")
ROUND_COMPLETE=$(grep -o '"round_complete":[^,}]*' "$RALPH_STATE_FILE" 2>/dev/null | cut -d':' -f2 | tr -d ' ' || echo "false")

log "DEBUG" "Ralph state: active=$RALPH_ACTIVE, iteration=$CURRENT_ITERATION, round_complete=$ROUND_COMPLETE, completed=$TASK_COMPLETED, fatal=$HAS_FATAL_ERROR"

# 如果 Ralph 不活跃，允许停止
if [[ "$RALPH_ACTIVE" != "true" ]]; then
    log "INFO" "Ralph not active, allowing stop"
    exit 0
fi

# 如果任务已完成，允许停止
if [[ "$TASK_COMPLETED" == "true" ]]; then
    log "INFO" "Task completed, allowing stop"
    # 清理状态
    echo '{"active": false, "completed": true}' > "$RALPH_STATE_FILE"
    exit 0
fi

# 如果遇到致命错误，允许停止
if [[ "$HAS_FATAL_ERROR" == "true" ]]; then
    log "WARN" "Fatal error encountered, allowing stop"
    echo '{"active": false, "completed": false, "fatal_error": true}' > "$RALPH_STATE_FILE"
    exit 0
fi

# 如果超过最大迭代次数，允许停止
if [[ "$CURRENT_ITERATION" -ge "$RALPH_MAX_ITERATIONS" ]]; then
    log "WARN" "Max iterations ($RALPH_MAX_ITERATIONS) reached, allowing stop"
    echo '{"active": false, "completed": false, "max_iterations_reached": true}' > "$RALPH_STATE_FILE"
    exit 0
fi

# 任务未完成，继续执行
# 根据 round_complete 判断是轮次结束还是轮次中途
if [[ "$ROUND_COMPLETE" == "true" ]]; then
    # 一轮完整工作周期结束，递增迭代计数
    log "INFO" "Round $CURRENT_ITERATION complete, starting iteration $((CURRENT_ITERATION + 1))/$RALPH_MAX_ITERATIONS"

    NEW_ITERATION=$((CURRENT_ITERATION + 1))
    # 重置 round_complete 并递增 iteration
    if sed "s/\"iteration\":[^,}]*/\"iteration\": $NEW_ITERATION/" "$RALPH_STATE_FILE" \
       | sed "s/\"round_complete\":[^,}]*/\"round_complete\": false/" \
       > "${RALPH_STATE_FILE}.tmp"; then
        mv "${RALPH_STATE_FILE}.tmp" "$RALPH_STATE_FILE"
    else
        rm -f "${RALPH_STATE_FILE}.tmp"
        log "WARN" "Failed to update state file"
    fi

    echo ""
    echo "========================================"
    echo "  RALPH LOOP: Round $CURRENT_ITERATION complete"
    echo "  Starting Round: $NEW_ITERATION / $RALPH_MAX_ITERATIONS"
    echo "========================================"
    echo ""
    echo "继续执行下一轮。请评估当前进展，规划并执行本轮工作，完成后将 round_complete 设为 true。"
else
    # 轮次进行中（Claude 在一轮内停止），继续完成当前轮
    log "INFO" "Mid-round stop detected, resuming iteration $CURRENT_ITERATION/$RALPH_MAX_ITERATIONS"

    echo ""
    echo "========================================"
    echo "  RALPH LOOP: Resuming round $CURRENT_ITERATION"
    echo "  Round $CURRENT_ITERATION / $RALPH_MAX_ITERATIONS (in progress)"
    echo "========================================"
    echo ""
    echo "当前轮次 $CURRENT_ITERATION 尚未完成。请继续执行本轮剩余工作，完成后将 round_complete 设为 true。"
fi

# 返回特殊退出码表示继续执行
# 退出码 3 表示 Ralph 要求继续
exit 3

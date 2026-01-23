#!/bin/bash
# Ralph Stop Interceptor - 自主循环执行系统的停止钩子
# 版本: 1.0.0
# 触发时机: Stop hook 被调用时
#
# 功能:
# 1. 检查是否在 Ralph 循环执行模式中
# 2. 如果是，检查任务是否完成
# 3. 如果任务未完成且没有致命错误，继续执行
# 4. 如果任务完成或遇到致命错误，允许停止

set -e

# 配置
RALPH_STATE_FILE="${RALPH_STATE_FILE:-$HOME/.claude/ralph-state.json}"
RALPH_MAX_ITERATIONS="${RALPH_MAX_ITERATIONS:-10}"
RALPH_LOG_FILE="${RALPH_LOG_FILE:-$HOME/.claude/ralph.log}"

# 日志函数
log() {
    local level="$1"
    shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*" >> "$RALPH_LOG_FILE"
}

# 检查 Ralph 状态文件是否存在
if [[ ! -f "$RALPH_STATE_FILE" ]]; then
    log "INFO" "Ralph state file not found, allowing stop"
    exit 0
fi

# 读取状态
RALPH_ACTIVE=$(cat "$RALPH_STATE_FILE" | grep -o '"active":[^,}]*' | cut -d':' -f2 | tr -d ' ')
CURRENT_ITERATION=$(cat "$RALPH_STATE_FILE" | grep -o '"iteration":[^,}]*' | cut -d':' -f2 | tr -d ' ')
TASK_COMPLETED=$(cat "$RALPH_STATE_FILE" | grep -o '"completed":[^,}]*' | cut -d':' -f2 | tr -d ' ')
HAS_FATAL_ERROR=$(cat "$RALPH_STATE_FILE" | grep -o '"fatal_error":[^,}]*' | cut -d':' -f2 | tr -d ' ')

log "DEBUG" "Ralph state: active=$RALPH_ACTIVE, iteration=$CURRENT_ITERATION, completed=$TASK_COMPLETED, fatal=$HAS_FATAL_ERROR"

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
log "INFO" "Task not completed, iteration $CURRENT_ITERATION/$RALPH_MAX_ITERATIONS, continuing..."

# 更新迭代计数
NEW_ITERATION=$((CURRENT_ITERATION + 1))
cat "$RALPH_STATE_FILE" | sed "s/\"iteration\":[^,}]*/\"iteration\": $NEW_ITERATION/" > "${RALPH_STATE_FILE}.tmp"
mv "${RALPH_STATE_FILE}.tmp" "$RALPH_STATE_FILE"

# 输出继续执行的提示
echo ""
echo "========================================"
echo "  RALPH LOOP: Continuing execution"
echo "  Iteration: $NEW_ITERATION / $RALPH_MAX_ITERATIONS"
echo "========================================"
echo ""

# 返回特殊退出码表示继续执行
# 退出码 3 表示 Ralph 要求继续
exit 3

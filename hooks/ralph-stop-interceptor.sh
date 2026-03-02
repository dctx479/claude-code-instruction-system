#!/bin/bash
# Ralph Stop Interceptor - 自主循环执行系统的停止钩子
# 版本: 1.2.0
# 触发时机: Stop hook 被调用时
#
# 功能:
# 1. 检查是否在 Ralph 循环执行模式中
# 2. 如果是，检查任务是否完成
# 3. 根据 round_complete 决定递增计数还是续跑当前轮
# 4. 支持 PAUSED / needs_confirmation 状态
# 5. 原子更新状态文件（Python 解析 JSON，避免 sed 破坏结构）

set -uo pipefail

# ─── 配置 ──────────────────────────────────────────────────────────────────
# 状态文件路径优先级：显式环境变量 > 项目级 > 全局级
PROJECT_STATE="memory/ralph-state.json"
GLOBAL_STATE="${HOME}/.claude/ralph-state.json"

if [[ -z "${RALPH_STATE_FILE:-}" ]]; then
    # 未显式指定，自动选择
    if [[ -f "$PROJECT_STATE" ]]; then
        RALPH_STATE_FILE="$PROJECT_STATE"
    else
        RALPH_STATE_FILE="$GLOBAL_STATE"
    fi
fi
# 若用户已设置 RALPH_STATE_FILE 则保持不变

RALPH_LOG_FILE="${RALPH_LOG_FILE:-${HOME}/.claude/ralph.log}"

# ─── 工具函数 ────────────────────────────────────────────────────────────────
log() {
    local level="$1"; shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*" >> "$RALPH_LOG_FILE" 2>/dev/null || true
}

# Python 解释器（Windows 可能是 python，Linux/Mac 通常是 python3）
# 通过实际执行检测，避免 Windows App 执行别名（Microsoft Store 重定向）误报
_find_python() {
    for cmd in python3 python py; do
        if command -v "$cmd" &>/dev/null; then
            # 验证能真正执行且版本 ≥ 3.3（os.replace 依赖）
            # Windows App 执行别名（Microsoft Store 重定向）会在此步骤失败
            if "$cmd" -c "import sys; assert sys.version_info >= (3, 3); sys.exit(0)" 2>/dev/null; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    echo "python"  # 最后 fallback，让后续 json_get 走 echo default
}
PYTHON_CMD="${PYTHON_CMD:-$(_find_python)}"

# 用 Python 安全读取 JSON 字段（无 jq 依赖）
json_get() {
    local file="$1" key="$2" default="$3"
    "$PYTHON_CMD" -c "
import json, sys
try:
    with open('$file') as f:
        d = json.load(f)
    val = d.get('$key')
    if val is None:
        print('$default')
    elif isinstance(val, bool):
        print('true' if val else 'false')
    else:
        print(val)
except Exception:
    print('$default')
" 2>/dev/null || echo "$default"
}

# ─── 前置检查 ────────────────────────────────────────────────────────────────
if [[ ! -f "$RALPH_STATE_FILE" ]]; then
    log "INFO" "Ralph state file not found ($RALPH_STATE_FILE), allowing stop"
    exit 0
fi

# ─── 读取状态 ────────────────────────────────────────────────────────────────
RALPH_ACTIVE=$(json_get "$RALPH_STATE_FILE" "active" "false")
CURRENT_ITERATION=$(json_get "$RALPH_STATE_FILE" "iteration" "0")
MAX_ITERATIONS=$(json_get "$RALPH_STATE_FILE" "max_iterations" "${RALPH_MAX_ITERATIONS:-10}")
TASK_COMPLETED=$(json_get "$RALPH_STATE_FILE" "completed" "false")
HAS_FATAL_ERROR=$(json_get "$RALPH_STATE_FILE" "fatal_error" "false")
ROUND_COMPLETE=$(json_get "$RALPH_STATE_FILE" "round_complete" "false")
NEEDS_CONFIRMATION=$(json_get "$RALPH_STATE_FILE" "needs_confirmation" "false")
CURRENT_STATUS=$(json_get "$RALPH_STATE_FILE" "status" "RUNNING")

log "DEBUG" "state: active=$RALPH_ACTIVE status=$CURRENT_STATUS iteration=$CURRENT_ITERATION/$MAX_ITERATIONS round_complete=$ROUND_COMPLETE completed=$TASK_COMPLETED fatal=$HAS_FATAL_ERROR needs_confirm=$NEEDS_CONFIRMATION"

# ─── 停止条件检查 ────────────────────────────────────────────────────────────

# 1. Ralph 未激活
if [[ "$RALPH_ACTIVE" != "true" ]]; then
    log "INFO" "Ralph not active, allowing stop"
    exit 0
fi

# 2. 任务已完成
if [[ "$TASK_COMPLETED" == "true" ]]; then
    log "INFO" "Task completed at iteration $CURRENT_ITERATION, allowing stop"
    "$PYTHON_CMD" - "$RALPH_STATE_FILE" <<'EOF' 2>/dev/null || true
import json, sys, os, time
file = sys.argv[1]
with open(file) as f: d = json.load(f)
d['active'] = False
d['status'] = 'COMPLETED'
d['last_updated'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
if 'metrics' not in d: d['metrics'] = {}
d['metrics']['successful_runs'] = d['metrics'].get('successful_runs', 0) + 1
tmp = file + '.tmp'
with open(tmp, 'w') as f: json.dump(d, f, indent=2, ensure_ascii=False)
os.replace(tmp, file)
EOF
    echo ""
    echo "========================================"
    echo "  RALPH LOOP: Task COMPLETED"
    echo "  Total iterations: $CURRENT_ITERATION"
    echo "========================================"
    exit 0
fi

# 3. 致命错误
if [[ "$HAS_FATAL_ERROR" == "true" ]]; then
    log "WARN" "Fatal error at iteration $CURRENT_ITERATION, allowing stop"
    "$PYTHON_CMD" - "$RALPH_STATE_FILE" <<'EOF' 2>/dev/null || true
import json, sys, os, time
file = sys.argv[1]
with open(file) as f: d = json.load(f)
d['active'] = False
d['status'] = 'FAILED'
d['last_updated'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
if 'metrics' not in d: d['metrics'] = {}
d['metrics']['failed_runs'] = d['metrics'].get('failed_runs', 0) + 1
tmp = file + '.tmp'
with open(tmp, 'w') as f: json.dump(d, f, indent=2, ensure_ascii=False)
os.replace(tmp, file)
EOF
    echo ""
    echo "========================================"
    echo "  RALPH LOOP: FATAL ERROR — stopping"
    echo "========================================"
    exit 0
fi

# 4. 超过最大迭代次数
if [[ "$CURRENT_ITERATION" -ge "$MAX_ITERATIONS" ]]; then
    log "WARN" "Max iterations ($MAX_ITERATIONS) reached, allowing stop"
    "$PYTHON_CMD" - "$RALPH_STATE_FILE" <<'EOF' 2>/dev/null || true
import json, sys, os, time
file = sys.argv[1]
with open(file) as f: d = json.load(f)
d['active'] = False
d['status'] = 'FAILED'
d['max_iterations_reached'] = True
d['last_updated'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
if 'metrics' not in d: d['metrics'] = {}
d['metrics']['failed_runs'] = d['metrics'].get('failed_runs', 0) + 1
tmp = file + '.tmp'
with open(tmp, 'w') as f: json.dump(d, f, indent=2, ensure_ascii=False)
os.replace(tmp, file)
EOF
    echo ""
    echo "========================================"
    echo "  RALPH LOOP: Max iterations ($MAX_ITERATIONS) reached"
    echo "========================================"
    exit 0
fi

# 5. 需要人工确认（PAUSED 状态）
# 注意：只检查 needs_confirmation 字段；status 字段由 Hook 自身写入，不作为触发条件
if [[ "$NEEDS_CONFIRMATION" == "true" ]]; then
    log "INFO" "Confirmation required at iteration $CURRENT_ITERATION, pausing"
    "$PYTHON_CMD" - "$RALPH_STATE_FILE" <<'EOF' 2>/dev/null || true
import json, sys, os, time
file = sys.argv[1]
with open(file) as f: d = json.load(f)
d['status'] = 'PAUSED'
d['paused_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
d['last_updated'] = d['paused_at']
tmp = file + '.tmp'
with open(tmp, 'w') as f: json.dump(d, f, indent=2, ensure_ascii=False)
os.replace(tmp, file)
EOF
    echo ""
    echo "========================================"
    echo "  RALPH LOOP: PAUSED — awaiting confirmation"
    echo "  Iteration: $CURRENT_ITERATION / $MAX_ITERATIONS"
    echo "========================================"
    echo ""
    echo "任务需要人工确认。请确认后，将 needs_confirmation 重置为 false 并继续。"
    # 允许停止以请求用户输入
    exit 0
fi

# ─── 任务未完成，继续执行 ─────────────────────────────────────────────────────

if [[ "$ROUND_COMPLETE" == "true" ]]; then
    # 一轮完整周期结束 → 递增迭代计数
    NEW_ITERATION=$((CURRENT_ITERATION + 1))
    log "INFO" "Round $CURRENT_ITERATION complete → starting iteration $NEW_ITERATION/$MAX_ITERATIONS"

    "$PYTHON_CMD" - "$RALPH_STATE_FILE" "$NEW_ITERATION" <<'EOF' 2>/dev/null || { log "WARN" "Failed to update state"; exit 0; }
import json, sys, os, time
file, new_iter = sys.argv[1], int(sys.argv[2])
with open(file) as f: d = json.load(f)
d['iteration'] = new_iter
d['round_complete'] = False
d['status'] = 'RUNNING'
d['last_updated'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
# 累计总迭代数
if 'metrics' not in d: d['metrics'] = {}
d['metrics']['total_iterations'] = d['metrics'].get('total_iterations', 0) + 1
tmp = file + '.tmp'
with open(tmp, 'w') as f: json.dump(d, f, indent=2, ensure_ascii=False)
os.replace(tmp, file)
EOF

    echo ""
    echo "========================================"
    echo "  RALPH LOOP: Round $CURRENT_ITERATION complete"
    echo "  Starting Round: $NEW_ITERATION / $MAX_ITERATIONS"
    echo "========================================"
    echo ""
    echo "开始第 $NEW_ITERATION 轮。请按照以下步骤执行完整工作周期："
    echo "  1. 评估当前整体进展（状态评估）"
    echo "  2. 规划本轮要完成的具体工作"
    echo "  3. 执行本轮所有步骤（可包含多次 tool call）"
    echo "  4. 验证本轮成果"
    echo "  5. 更新 ralph-state.json: round_complete=true（本轮全部完成后）"
    echo "     或: completed=true（整个任务完成时）"
    echo "     或: fatal_error=true + 错误描述（遇到不可恢复错误时）"
    echo "     或: needs_confirmation=true（需要人工确认时）"

else
    # 轮次进行中 → 续跑当前轮，不递增计数
    log "INFO" "Mid-round stop at iteration $CURRENT_ITERATION/$MAX_ITERATIONS, resuming"

    "$PYTHON_CMD" - "$RALPH_STATE_FILE" <<'EOF' 2>/dev/null || true
import json, sys, os, time
file = sys.argv[1]
with open(file) as f: d = json.load(f)
d['status'] = 'RUNNING'
d['last_updated'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
tmp = file + '.tmp'
with open(tmp, 'w') as f: json.dump(d, f, indent=2, ensure_ascii=False)
os.replace(tmp, file)
EOF

    echo ""
    echo "========================================"
    echo "  RALPH LOOP: Resuming round $CURRENT_ITERATION"
    echo "  Round $CURRENT_ITERATION / $MAX_ITERATIONS (in progress)"
    echo "========================================"
    echo ""
    echo "第 $CURRENT_ITERATION 轮尚未完成（round_complete=false）。"
    echo "请继续执行本轮剩余工作，完成所有步骤并验证后，将 round_complete 设为 true。"
fi

# 退出码 3：告知 Claude Code 继续执行（Stop Hook 拦截）
exit 3

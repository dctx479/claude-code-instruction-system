#!/bin/bash
# Ralph Stop Interceptor - 自主循环执行系统的停止钩子
# 版本: 2.0.0
# 触发时机: Stop hook 被调用时
#
# 与 Claude Code 的约定（官方 hooks 规范）:
#   exit 0     → 允许停止
#   exit 2     → 阻止停止，stderr 内容作为"为什么要继续"反馈给 Claude
#   其他退出码 → 非阻塞错误，Claude 照常停止（v1.x 使用的 exit 3 属于这一类，循环不会继续）
#
# 功能:
# 1. 检查是否在 Ralph 循环执行模式中
# 2. 如果是，检查任务是否完成
# 3. 根据 round_complete 决定递增计数还是续跑当前轮
# 4. 支持 PAUSED / needs_confirmation 状态
# 5. 原子更新状态文件（Python 解析 JSON，避免 sed 破坏结构）
# 6. 全局状态文件只对发起它的项目生效（project_dir 字段），避免拦住其他项目的会话

set -uo pipefail

# ─── 配置 ──────────────────────────────────────────────────────────────────
# 状态文件路径优先级：显式环境变量 > 项目级 > 全局级
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"
PROJECT_STATE="${PROJECT_ROOT}/memory/ralph-state.json"
GLOBAL_STATE="${HOME}/.claude/ralph-state.json"
USING_GLOBAL_STATE=false

if [[ -z "${RALPH_STATE_FILE:-}" ]]; then
    # 未显式指定，自动选择
    if [[ -f "$PROJECT_STATE" ]]; then
        RALPH_STATE_FILE="$PROJECT_STATE"
    else
        RALPH_STATE_FILE="$GLOBAL_STATE"
        USING_GLOBAL_STATE=true
    fi
fi
# 若用户已设置 RALPH_STATE_FILE 则保持不变

RALPH_LOG_FILE="${RALPH_LOG_FILE:-${HOME}/.claude/ralph.log}"

# ─── 快速放行（Stop 每轮对话都会触发，未启用 Ralph 时不启动 Python）────────────
[[ -f "$RALPH_STATE_FILE" ]] || exit 0
grep -Eq '"active"[[:space:]]*:[[:space:]]*true' "$RALPH_STATE_FILE" 2>/dev/null || exit 0

# ─── 工具函数 ────────────────────────────────────────────────────────────────
log() {
    local level="$1"; shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*" >> "$RALPH_LOG_FILE" 2>/dev/null || true
}

# Windows 原生 Python 打不开 /c/Users/... 这类 Git Bash 路径，统一转成 C:/Users/... 再传给 Python
native_path() {
    if command -v cygpath &>/dev/null; then
        cygpath -m "$1" 2>/dev/null || printf '%s' "$1"
    else
        printf '%s' "$1"
    fi
}

# Python 解释器（Windows 可能是 python，Linux/Mac 通常是 python3）
# 通过实际执行检测，避免 Windows App 执行别名（Microsoft Store 重定向）误报
_find_python() {
    for cmd in python3 python py; do
        if command -v "$cmd" &>/dev/null; then
            # 验证能真正执行且版本 ≥ 3.3（os.replace 依赖）
            if "$cmd" -c "import sys; assert sys.version_info >= (3, 3); sys.exit(0)" 2>/dev/null; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    echo "python"
}
PYTHON_CMD="${PYTHON_CMD:-$(_find_python)}"

STATE_NATIVE=$(native_path "$RALPH_STATE_FILE")
CURRENT_DIR_NATIVE=$(native_path "${CLAUDE_PROJECT_DIR:-$(pwd)}")

# ─── 读取状态（单次 Python 调用，路径通过 argv 传入，不拼进代码）────────────────
STATE_OUT=$("$PYTHON_CMD" - "$STATE_NATIVE" "${RALPH_MAX_ITERATIONS:-10}" "$CURRENT_DIR_NATIVE" <<'EOF' 2>/dev/null
import json, os, re, sys

path, default_max, current_dir = sys.argv[1], sys.argv[2], sys.argv[3]
with open(path, encoding='utf-8') as fh:
    d = json.load(fh)

def flag(key):
    return 'true' if d.get(key) is True else 'false'

def number(key, default):
    try:
        return str(int(d.get(key, default)))
    except (TypeError, ValueError):
        return str(default)

def norm(p):
    # /d/projects/x（Git Bash 写法）→ D:/projects/x，再做大小写和分隔符归一
    if os.name == 'nt':
        p = re.sub(r'^/([a-zA-Z])/', lambda m: m.group(1).upper() + ':/', p)
    return os.path.normcase(os.path.abspath(p))

project_dir = d.get('project_dir') or ''
if not project_dir:
    scope = 'unscoped'
elif norm(project_dir) == norm(current_dir):
    scope = 'match'
else:
    scope = 'mismatch'

print(flag('active'), number('iteration', 0), number('max_iterations', default_max),
      flag('completed'), flag('fatal_error'), flag('round_complete'),
      flag('needs_confirmation'), scope)
EOF
)

if [[ -z "$STATE_OUT" ]]; then
    # 不静默兜底：状态文件标记为 active 但无法解析，放行停止并显式告警
    echo "⚠️ WARNING: Ralph 状态文件无法解析（$RALPH_STATE_FILE），已放行停止。请检查 JSON 格式和 Python 环境。" >&2
    log "WARN" "Failed to parse state file $RALPH_STATE_FILE, allowing stop"
    exit 0
fi

read -r RALPH_ACTIVE CURRENT_ITERATION MAX_ITERATIONS TASK_COMPLETED HAS_FATAL_ERROR \
        ROUND_COMPLETE NEEDS_CONFIRMATION PROJECT_SCOPE <<< "$(printf '%s' "$STATE_OUT" | tr -d '\r')"

log "DEBUG" "state: file=$RALPH_STATE_FILE active=$RALPH_ACTIVE iteration=$CURRENT_ITERATION/$MAX_ITERATIONS round_complete=$ROUND_COMPLETE completed=$TASK_COMPLETED fatal=$HAS_FATAL_ERROR needs_confirm=$NEEDS_CONFIRMATION scope=$PROJECT_SCOPE"

# 原子更新状态文件。用法: update_state <mode> [new_iteration]
update_state() {
    "$PYTHON_CMD" - "$STATE_NATIVE" "$1" "${2:-0}" <<'EOF' 2>/dev/null
import json, os, sys, time

path, mode, new_iter = sys.argv[1], sys.argv[2], int(sys.argv[3])
with open(path, encoding='utf-8') as fh:
    d = json.load(fh)

now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
metrics = d.setdefault('metrics', {})
d['last_updated'] = now

if mode == 'completed':
    d['active'] = False
    d['status'] = 'COMPLETED'
    metrics['successful_runs'] = metrics.get('successful_runs', 0) + 1
elif mode == 'fatal':
    d['active'] = False
    d['status'] = 'FAILED'
    metrics['failed_runs'] = metrics.get('failed_runs', 0) + 1
elif mode == 'max':
    d['active'] = False
    d['status'] = 'FAILED'
    d['max_iterations_reached'] = True
    metrics['failed_runs'] = metrics.get('failed_runs', 0) + 1
elif mode == 'paused':
    d['status'] = 'PAUSED'
    d['paused_at'] = now
elif mode == 'next':
    d['iteration'] = new_iter
    d['round_complete'] = False
    d['status'] = 'RUNNING'
    metrics['total_iterations'] = metrics.get('total_iterations', 0) + 1
elif mode == 'resume':
    d['status'] = 'RUNNING'
else:
    sys.exit(1)

tmp = path + '.tmp'
with open(tmp, 'w', encoding='utf-8') as fh:
    json.dump(d, fh, indent=2, ensure_ascii=False)
os.replace(tmp, path)
EOF
}

# ─── 停止条件检查 ────────────────────────────────────────────────────────────

# 1. Ralph 未激活
if [[ "$RALPH_ACTIVE" != "true" ]]; then
    exit 0
fi

# 1.5 全局状态文件属于另一个项目 → 不拦截当前会话
if [[ "$USING_GLOBAL_STATE" == "true" && "$PROJECT_SCOPE" == "mismatch" ]]; then
    log "INFO" "Global Ralph state belongs to another project, allowing stop"
    exit 0
fi

# 2. 任务已完成
if [[ "$TASK_COMPLETED" == "true" ]]; then
    log "INFO" "Task completed at iteration $CURRENT_ITERATION, allowing stop"
    update_state completed || true
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
    update_state fatal || true
    echo ""
    echo "========================================"
    echo "  RALPH LOOP: FATAL ERROR — stopping"
    echo "========================================"
    exit 0
fi

# 4. 超过最大迭代次数
if [[ "$CURRENT_ITERATION" -ge "$MAX_ITERATIONS" ]]; then
    log "WARN" "Max iterations ($MAX_ITERATIONS) reached, allowing stop"
    update_state max || true
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
    update_state paused || true
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

# ─── 任务未完成，继续执行（exit 2 + stderr）──────────────────────────────────

if [[ "$ROUND_COMPLETE" == "true" ]]; then
    # 一轮完整周期结束 → 递增迭代计数
    NEW_ITERATION=$((CURRENT_ITERATION + 1))
    log "INFO" "Round $CURRENT_ITERATION complete → starting iteration $NEW_ITERATION/$MAX_ITERATIONS"

    if ! update_state next "$NEW_ITERATION"; then
        # 计数无法落盘时继续拦截会变成无上限循环，因此放行并告警
        echo "⚠️ WARNING: Ralph 状态文件更新失败（$RALPH_STATE_FILE），已放行停止以避免无限循环。" >&2
        log "WARN" "Failed to update state, allowing stop"
        exit 0
    fi

    {
        echo "RALPH LOOP: 第 $CURRENT_ITERATION 轮已完成，开始第 $NEW_ITERATION / $MAX_ITERATIONS 轮。"
        echo "请按照以下步骤执行完整工作周期："
        echo "  1. 评估当前整体进展（状态评估）"
        echo "  2. 规划本轮要完成的具体工作"
        echo "  3. 执行本轮所有步骤（可包含多次 tool call）"
        echo "  4. 验证本轮成果"
        echo "  5. 更新状态文件 $RALPH_STATE_FILE: round_complete=true（本轮全部完成后）"
        echo "     或: completed=true（整个任务完成时）"
        echo "     或: fatal_error=true + 错误描述（遇到不可恢复错误时）"
        echo "     或: needs_confirmation=true（需要人工确认时）"
    } >&2
else
    # 轮次进行中 → 续跑当前轮，不递增计数
    log "INFO" "Mid-round stop at iteration $CURRENT_ITERATION/$MAX_ITERATIONS, resuming"
    update_state resume || true

    {
        echo "RALPH LOOP: 第 $CURRENT_ITERATION / $MAX_ITERATIONS 轮尚未完成（round_complete=false）。"
        echo "请继续执行本轮剩余工作，完成所有步骤并验证后，将状态文件 $RALPH_STATE_FILE 的 round_complete 设为 true。"
        echo "如需人工确认请写入 needs_confirmation=true；遇到不可恢复错误请写入 fatal_error=true。"
    } >&2
fi

# 退出码 2：阻止停止，stderr 作为继续执行的指令反馈给 Claude
exit 2

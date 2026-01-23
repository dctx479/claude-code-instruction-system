#!/bin/bash
# HUD Statusline Renderer - 实时状态可视化
# 版本: 1.0.0
#
# 功能:
# 1. 渲染当前执行状态
# 2. 显示进度、Agent状态、资源使用
# 3. 支持多种主题

set -e

# 配置
HUD_CONFIG_FILE="${HUD_CONFIG_FILE:-$HOME/.claude/hud-config.json}"
HUD_THEME="${HUD_THEME:-default}"
HUD_WIDTH="${HUD_WIDTH:-80}"

# 默认配置
DEFAULT_CONFIG='{
  "theme": "default",
  "width": 80,
  "show_time": true,
  "show_model": true,
  "show_tokens": true,
  "show_agent": true,
  "show_task": true,
  "show_progress": true,
  "show_ralph": true,
  "refresh_rate": 1
}'

# 颜色定义 (ANSI)
declare -A COLORS=(
    ["reset"]="\033[0m"
    ["bold"]="\033[1m"
    ["dim"]="\033[2m"
    ["red"]="\033[31m"
    ["green"]="\033[32m"
    ["yellow"]="\033[33m"
    ["blue"]="\033[34m"
    ["magenta"]="\033[35m"
    ["cyan"]="\033[36m"
    ["white"]="\033[37m"
    ["bg_blue"]="\033[44m"
    ["bg_green"]="\033[42m"
    ["bg_yellow"]="\033[43m"
    ["bg_red"]="\033[41m"
)

# 主题定义
load_theme() {
    local theme="$1"
    case "$theme" in
        "minimal")
            BORDER_CHAR=" "
            PROGRESS_FILLED="="
            PROGRESS_EMPTY="-"
            SEPARATOR="|"
            ;;
        "unicode")
            BORDER_CHAR="─"
            PROGRESS_FILLED="█"
            PROGRESS_EMPTY="░"
            SEPARATOR="│"
            ;;
        "nerd")
            BORDER_CHAR="━"
            PROGRESS_FILLED="█"
            PROGRESS_EMPTY="▒"
            SEPARATOR="┃"
            ;;
        *)  # default
            BORDER_CHAR="-"
            PROGRESS_FILLED="#"
            PROGRESS_EMPTY="."
            SEPARATOR="|"
            ;;
    esac
}

# 获取当前时间
get_time() {
    date "+%H:%M:%S"
}

# 获取当前模型
get_model() {
    local model="${CLAUDE_MODEL:-sonnet}"
    case "$model" in
        *opus*) echo "Opus" ;;
        *sonnet*) echo "Sonnet" ;;
        *haiku*) echo "Haiku" ;;
        *) echo "$model" ;;
    esac
}

# 获取 Token 使用量 (模拟)
get_tokens() {
    local input="${CLAUDE_TOKENS_IN:-0}"
    local output="${CLAUDE_TOKENS_OUT:-0}"
    echo "${input}i/${output}o"
}

# 获取当前 Agent
get_agent() {
    local agent="${CLAUDE_AGENT:-orchestrator}"
    echo "$agent"
}

# 获取当前任务
get_task() {
    local task="${CLAUDE_TASK:-}"
    if [[ -n "$task" ]]; then
        # 截断长任务名
        if [[ ${#task} -gt 20 ]]; then
            echo "${task:0:17}..."
        else
            echo "$task"
        fi
    else
        echo "idle"
    fi
}

# 获取进度
get_progress() {
    local progress="${CLAUDE_PROGRESS:-0}"
    echo "$progress"
}

# 获取 Ralph 状态
get_ralph_status() {
    local ralph_file="${HOME}/.claude/ralph-state.json"
    if [[ -f "$ralph_file" ]]; then
        local active=$(cat "$ralph_file" | grep -o '"active":[^,}]*' | cut -d':' -f2 | tr -d ' ')
        local iteration=$(cat "$ralph_file" | grep -o '"iteration":[^,}]*' | cut -d':' -f2 | tr -d ' ')
        local max=$(cat "$ralph_file" | grep -o '"max_iterations":[^,}]*' | cut -d':' -f2 | tr -d ' ')

        if [[ "$active" == "true" ]]; then
            echo "R:${iteration}/${max}"
        else
            echo ""
        fi
    else
        echo ""
    fi
}

# 渲染进度条
render_progress_bar() {
    local progress="$1"
    local width="${2:-20}"
    local filled=$((progress * width / 100))
    local empty=$((width - filled))

    local bar=""
    for ((i=0; i<filled; i++)); do
        bar+="$PROGRESS_FILLED"
    done
    for ((i=0; i<empty; i++)); do
        bar+="$PROGRESS_EMPTY"
    done

    echo "$bar"
}

# 渲染状态指示器
render_status_indicator() {
    local status="$1"
    case "$status" in
        "running")
            echo -e "${COLORS[green]}●${COLORS[reset]}"
            ;;
        "paused")
            echo -e "${COLORS[yellow]}●${COLORS[reset]}"
            ;;
        "error")
            echo -e "${COLORS[red]}●${COLORS[reset]}"
            ;;
        *)
            echo -e "${COLORS[dim]}○${COLORS[reset]}"
            ;;
    esac
}

# 渲染 HUD
render_hud() {
    load_theme "$HUD_THEME"

    local time=$(get_time)
    local model=$(get_model)
    local tokens=$(get_tokens)
    local agent=$(get_agent)
    local task=$(get_task)
    local progress=$(get_progress)
    local ralph=$(get_ralph_status)

    # 构建状态栏
    local parts=()

    # 时间
    parts+=("${COLORS[dim]}$time${COLORS[reset]}")

    # 模型
    case "$model" in
        "Opus")
            parts+=("${COLORS[magenta]}${COLORS[bold]}$model${COLORS[reset]}")
            ;;
        "Sonnet")
            parts+=("${COLORS[blue]}$model${COLORS[reset]}")
            ;;
        "Haiku")
            parts+=("${COLORS[cyan]}$model${COLORS[reset]}")
            ;;
        *)
            parts+=("$model")
            ;;
    esac

    # Agent
    parts+=("${COLORS[green]}@$agent${COLORS[reset]}")

    # Task
    if [[ "$task" != "idle" ]]; then
        parts+=("${COLORS[yellow]}$task${COLORS[reset]}")
    fi

    # Progress
    if [[ "$progress" -gt 0 ]]; then
        local bar=$(render_progress_bar "$progress" 10)
        parts+=("[${bar}] ${progress}%")
    fi

    # Ralph
    if [[ -n "$ralph" ]]; then
        parts+=("${COLORS[cyan]}${COLORS[bold]}$ralph${COLORS[reset]}")
    fi

    # Tokens
    parts+=("${COLORS[dim]}$tokens${COLORS[reset]}")

    # 组合输出
    local output=""
    for part in "${parts[@]}"; do
        if [[ -n "$output" ]]; then
            output+=" $SEPARATOR "
        fi
        output+="$part"
    done

    echo -e "$output"
}

# 渲染完整 HUD (带边框)
render_full_hud() {
    load_theme "$HUD_THEME"

    local content=$(render_hud)
    local border=""
    for ((i=0; i<HUD_WIDTH; i++)); do
        border+="$BORDER_CHAR"
    done

    echo "$border"
    echo " $content"
    echo "$border"
}

# 主函数
main() {
    local action="${1:-render}"

    case "$action" in
        "render")
            render_hud
            ;;
        "full")
            render_full_hud
            ;;
        "config")
            if [[ ! -f "$HUD_CONFIG_FILE" ]]; then
                echo "$DEFAULT_CONFIG" > "$HUD_CONFIG_FILE"
            fi
            cat "$HUD_CONFIG_FILE"
            ;;
        "theme")
            HUD_THEME="${2:-default}"
            render_hud
            ;;
        *)
            echo "Usage: hud.sh [render|full|config|theme <name>]"
            exit 1
            ;;
    esac
}

main "$@"

#!/bin/bash
# HUD Statusline Renderer v2.0 - Enhanced with Git, Cost, Context tracking
# Version: 2.0.0
# Performance Target: <80ms execution time
#
# Features:
# 1. Project and Git information (branch, status, ahead/behind)
# 2. Cost tracking (session cost, trend)
# 3. Context window usage (percentage, warnings)
# 4. Performance metrics (response time)
# 5. Intelligent caching system
# 6. Priority-based adaptive display
# 7. Enhanced configuration system

set -eo pipefail

# ============================================================================
# Configuration
# ============================================================================

HUD_CONFIG_FILE="${HUD_CONFIG_FILE:-$HOME/.claude/hud-config.json}"
HUD_CACHE_DIR="${HUD_CACHE_DIR:-$HOME/.claude/cache}"
HUD_THEME="${HUD_THEME:-default}"
HUD_WIDTH="${HUD_WIDTH:-auto}"
HUD_VERSION="2.0.0"

# Create cache directory if it doesn't exist
mkdir -p "$HUD_CACHE_DIR"

# ============================================================================
# Color Definitions (ANSI)
# ============================================================================

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

# ============================================================================
# Theme System
# ============================================================================

load_theme() {
    local theme="$1"
    case "$theme" in
        "minimal")
            BORDER_CHAR=" "
            PROGRESS_FILLED="="
            PROGRESS_EMPTY="-"
            SEPARATOR="|"
            GIT_CLEAN="✓"
            GIT_DIRTY="●"
            GIT_AHEAD="↑"
            GIT_BEHIND="↓"
            ;;
        "unicode")
            BORDER_CHAR="─"
            PROGRESS_FILLED="█"
            PROGRESS_EMPTY="░"
            SEPARATOR="│"
            GIT_CLEAN="✓"
            GIT_DIRTY="●"
            GIT_AHEAD="↑"
            GIT_BEHIND="↓"
            ;;
        "nerd")
            BORDER_CHAR="━"
            PROGRESS_FILLED="█"
            PROGRESS_EMPTY="▒"
            SEPARATOR="┃"
            GIT_CLEAN=""
            GIT_DIRTY=""
            GIT_AHEAD=""
            GIT_BEHIND=""
            ;;
        *)  # default
            BORDER_CHAR="-"
            PROGRESS_FILLED="#"
            PROGRESS_EMPTY="."
            SEPARATOR="|"
            GIT_CLEAN="✓"
            GIT_DIRTY="*"
            GIT_AHEAD="^"
            GIT_BEHIND="v"
            ;;
    esac
}

# ============================================================================
# Cache System
# ============================================================================

# Get cache file path
get_cache_file() {
    local cache_name="$1"
    echo "$HUD_CACHE_DIR/${cache_name}.cache"
}

# Check if cache is valid (not expired)
is_cache_valid() {
    local cache_file="$1"
    local ttl="$2"  # Time to live in seconds

    if [[ ! -f "$cache_file" ]]; then
        return 1
    fi

    local cache_time
    cache_time=$(stat -c %Y "$cache_file" 2>/dev/null || stat -f %m "$cache_file" 2>/dev/null || echo 0)
    local current_time
    current_time=$(date +%s)
    local age=$((current_time - cache_time))

    [[ $age -lt $ttl ]]
}

# Read from cache
read_cache() {
    local cache_file="$1"
    cat "$cache_file" 2>/dev/null || echo ""
}

# Write to cache
write_cache() {
    local cache_file="$1"
    local content="$2"
    echo "$content" > "$cache_file"
}

# ============================================================================
# Configuration Loading
# ============================================================================

load_config() {
    if [[ -f "$HUD_CONFIG_FILE" ]]; then
        # Read configuration (simplified - in production use jq)
        return 0
    fi
    return 1
}

# Get config value with default
get_config() {
    local key="$1"
    local default="$2"

    if [[ -f "$HUD_CONFIG_FILE" ]] && command -v jq &>/dev/null; then
        local value
        value=$(jq -r "$key // \"$default\"" "$HUD_CONFIG_FILE" 2>/dev/null)
        echo "${value:-$default}"
    else
        echo "$default"
    fi
}

# Check if module is enabled
is_module_enabled() {
    local module="$1"
    local default="${2:-true}"

    local enabled
    enabled=$(get_config ".modules.$module.enabled" "$default")
    [[ "$enabled" == "true" ]]
}

# Get module priority
get_module_priority() {
    local module="$1"
    local default="${2:-2}"

    get_config ".modules.$module.priority" "$default"
}

# ============================================================================
# Information Gathering Functions
# ============================================================================

# Get current time
get_time() {
    date "+%H:%M:%S"
}

# Get current model from environment or stdin JSON
get_model() {
    local model="${CLAUDE_MODEL:-}"

    # Try to read from stdin JSON if available
    if [[ -n "$HUD_SESSION_JSON" ]]; then
        if command -v jq &>/dev/null; then
            model=$(echo "$HUD_SESSION_JSON" | jq -r '.model.display_name // ""' 2>/dev/null || echo "")
        else
            model=$(echo "$HUD_SESSION_JSON" | grep -o '"display_name":"[^"]*"' | cut -d'"' -f4 || echo "")
        fi
    fi

    # Fallback to environment variable
    model="${model:-sonnet}"

    case "$model" in
        *opus*) echo "Opus" ;;
        *sonnet*) echo "Sonnet" ;;
        *haiku*) echo "Haiku" ;;
        *) echo "$(echo "$model" | cut -d'-' -f2 | head -c 6)" ;;
    esac
}

# Get project name
get_project_name() {
    local cache_file
    cache_file=$(get_cache_file "project-name")
    local ttl=60  # 60 seconds

    if is_cache_valid "$cache_file" "$ttl"; then
        read_cache "$cache_file"
        return
    fi

    local project_name
    project_name=$(basename "$(pwd)")

    # Truncate if too long
    local max_length
    max_length=$(get_config ".modules.project.max_length" "30")
    if [[ ${#project_name} -gt $max_length ]]; then
        project_name="${project_name:0:$((max_length-3))}..."
    fi

    write_cache "$cache_file" "$project_name"
    echo "$project_name"
}

# Get git branch
get_git_branch() {
    local cache_file
    cache_file=$(get_cache_file "git-branch")
    local ttl=5  # 5 seconds

    if is_cache_valid "$cache_file" "$ttl"; then
        read_cache "$cache_file"
        return
    fi

    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

    write_cache "$cache_file" "$branch"
    echo "$branch"
}

# Get git status (clean/dirty)
get_git_status() {
    local cache_file
    cache_file=$(get_cache_file "git-status")
    local ttl=5  # 5 seconds

    if is_cache_valid "$cache_file" "$ttl"; then
        read_cache "$cache_file"
        return
    fi

    if ! git rev-parse --git-dir &>/dev/null; then
        write_cache "$cache_file" "none"
        echo "none"
        return
    fi

    local status="clean"

    # Check for uncommitted changes
    if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
        status="dirty"
    fi

    # Check for untracked files
    if [[ -n $(git ls-files --others --exclude-standard 2>/dev/null) ]]; then
        status="dirty"
    fi

    write_cache "$cache_file" "$status"
    echo "$status"
}

# Get git ahead/behind status
get_git_ahead_behind() {
    local cache_file
    cache_file=$(get_cache_file "git-ahead-behind")
    local ttl=10  # 10 seconds

    if is_cache_valid "$cache_file" "$ttl"; then
        read_cache "$cache_file"
        return
    fi

    if ! git rev-parse --git-dir &>/dev/null; then
        write_cache "$cache_file" ""
        echo ""
        return
    fi

    local upstream
    upstream=$(git rev-parse --abbrev-ref @{upstream} 2>/dev/null || echo "")

    if [[ -z "$upstream" ]]; then
        write_cache "$cache_file" ""
        echo ""
        return
    fi

    local ahead behind
    ahead=$(git rev-list --count @{upstream}..HEAD 2>/dev/null || echo 0)
    behind=$(git rev-list --count HEAD..@{upstream} 2>/dev/null || echo 0)

    local result=""
    [[ $ahead -gt 0 ]] && result+="↑$ahead"
    [[ $behind -gt 0 ]] && result+="↓$behind"

    write_cache "$cache_file" "$result"
    echo "$result"
}

# Get context usage by reading transcript JSONL
get_context_usage() {
    local transcript=""
    if [[ -n "$HUD_SESSION_JSON" ]]; then
        if command -v jq &>/dev/null; then
            transcript=$(echo "$HUD_SESSION_JSON" | jq -r '.transcript_path // ""' 2>/dev/null || echo "")
        else
            transcript=$(echo "$HUD_SESSION_JSON" | grep -o '"transcript_path":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "")
        fi
    fi

    if [[ -f "$transcript" ]]; then
        local last_line usage_block input cache_read cache_creation used
        last_line=$(grep '"type":"assistant"' "$transcript" 2>/dev/null | tail -n 1)
        usage_block=$(echo "$last_line" | grep -o '"usage":{[^}]*}' || echo "")
        if [[ -n "$usage_block" ]]; then
            input=$(echo "$usage_block" | grep -o '"input_tokens":[0-9]*' | cut -d':' -f2 || echo "0")
            cache_read=$(echo "$usage_block" | grep -o '"cache_read_input_tokens":[0-9]*' | cut -d':' -f2 || echo "0")
            cache_creation=$(echo "$usage_block" | grep -o '"cache_creation_input_tokens":[0-9]*' | cut -d':' -f2 || echo "0")
            used=$(( ${input:-0} + ${cache_read:-0} + ${cache_creation:-0} ))
            if [[ $used -gt 0 ]]; then
                echo $(( used * 100 / 200000 ))
                return
            fi
        fi
    fi

    echo "0"
}

# Get session cost from stdin JSON
get_session_cost() {
    if [[ -n "$HUD_SESSION_JSON" ]]; then
        local cost
        if command -v jq &>/dev/null; then
            cost=$(echo "$HUD_SESSION_JSON" | jq -r '.cost.total_cost_usd // 0' 2>/dev/null || echo "0")
        else
            cost=$(echo "$HUD_SESSION_JSON" | grep -o '"total_cost_usd":[0-9.]*' | head -1 | cut -d':' -f2 || echo "0")
        fi
        printf "%.3f" "$cost"
        return
    fi

    echo "0.000"
}

# Get token usage from transcript JSONL
get_tokens() {
    local transcript=""
    if [[ -n "$HUD_SESSION_JSON" ]]; then
        if command -v jq &>/dev/null; then
            transcript=$(echo "$HUD_SESSION_JSON" | jq -r '.transcript_path // ""' 2>/dev/null || echo "")
        else
            transcript=$(echo "$HUD_SESSION_JSON" | grep -o '"transcript_path":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "")
        fi
    fi

    if [[ -f "$transcript" ]]; then
        local last_line usage_block input output
        last_line=$(grep '"type":"assistant"' "$transcript" 2>/dev/null | tail -n 1)
        usage_block=$(echo "$last_line" | grep -o '"usage":{[^}]*}' || echo "")
        if [[ -n "$usage_block" ]]; then
            input=$(echo "$usage_block" | grep -o '"input_tokens":[0-9]*' | cut -d':' -f2 || echo "0")
            output=$(echo "$usage_block" | grep -o '"output_tokens":[0-9]*' | cut -d':' -f2 || echo "0")
            echo "${input:-0}i/${output:-0}o"
            return
        fi
    fi

    echo "0i/0o"
}

# Get current agent from intent-state.json (written by intent-detector hook)
get_agent() {
    local intent_state="${HOME}/.claude/intent-state.json"
    if [[ -f "$intent_state" ]]; then
        local agent
        agent=$(grep -o '"agent":"[^"]*"' "$intent_state" | cut -d'"' -f4 || echo "")
        echo "${agent:-orchestrator}"
    else
        echo "${CLAUDE_AGENT:-orchestrator}"
    fi
}

# Get current task
get_task() {
    local task="${CLAUDE_TASK:-}"
    if [[ -n "$task" ]]; then
        local max_length
        max_length=$(get_config ".modules.task.max_length" "20")
        if [[ ${#task} -gt $max_length ]]; then
            echo "${task:0:$((max_length-3))}..."
        else
            echo "$task"
        fi
    else
        echo "idle"
    fi
}

# Get progress
get_progress() {
    local progress="${CLAUDE_PROGRESS:-0}"
    echo "$progress"
}

# Get Ralph status
get_ralph_status() {
    local ralph_file="${HOME}/.claude/ralph-state.json"
    if [[ -f "$ralph_file" ]]; then
        local content
        content=$(cat "$ralph_file" 2>/dev/null) || return
        local active
        active=$(echo "$content" | grep -o '"active":[^,}]*' | cut -d':' -f2 | tr -d ' ')

        if [[ "$active" == "true" ]]; then
            local iteration max
            iteration=$(echo "$content" | grep -o '"iteration":[^,}]*' | cut -d':' -f2 | tr -d ' ')
            max=$(echo "$content" | grep -o '"max_iterations":[^,}]*' | cut -d':' -f2 | tr -d ' ')
            echo "R:${iteration}/${max}"
        else
            echo ""
        fi
    else
        echo ""
    fi
}

# ============================================================================
# Rendering Functions
# ============================================================================

# Render progress bar
render_progress_bar() {
    local progress="$1"
    local width="${2:-10}"
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

# Render colored model name
render_model() {
    local model="$1"
    case "$model" in
        "Opus")
            echo -e "${COLORS[magenta]}${COLORS[bold]}$model${COLORS[reset]}"
            ;;
        "Sonnet")
            echo -e "${COLORS[blue]}$model${COLORS[reset]}"
            ;;
        "Haiku")
            echo -e "${COLORS[cyan]}$model${COLORS[reset]}"
            ;;
        *)
            echo "$model"
            ;;
    esac
}

# Render git status with color
render_git_status() {
    local branch="$1"
    local status="$2"
    local ahead_behind="$3"

    if [[ -z "$branch" ]]; then
        echo ""
        return
    fi

    local output=""

    # Branch name
    output+="${COLORS[cyan]}$branch${COLORS[reset]}"

    # Status indicator
    if [[ "$status" == "clean" ]]; then
        output+=" ${COLORS[green]}$GIT_CLEAN${COLORS[reset]}"
    elif [[ "$status" == "dirty" ]]; then
        output+=" ${COLORS[yellow]}$GIT_DIRTY${COLORS[reset]}"
    fi

    # Ahead/behind
    if [[ -n "$ahead_behind" ]]; then
        output+=" ${COLORS[dim]}$ahead_behind${COLORS[reset]}"
    fi

    echo -e "$output"
}

# Render context usage with warning colors
render_context() {
    local percentage="$1"
    local warn_threshold
    local critical_threshold

    warn_threshold=$(get_config ".modules.context.warn_threshold" "80")
    critical_threshold=$(get_config ".modules.context.critical_threshold" "90")

    local color="${COLORS[green]}"
    if [[ $percentage -ge $critical_threshold ]]; then
        color="${COLORS[red]}"
    elif [[ $percentage -ge $warn_threshold ]]; then
        color="${COLORS[yellow]}"
    fi

    echo -e "${color}${percentage}%${COLORS[reset]}"
}

# Render cost with formatting
render_cost() {
    local cost="$1"
    echo -e "${COLORS[dim]}\$$cost${COLORS[reset]}"
}

# ============================================================================
# Main Rendering Logic
# ============================================================================

# Render HUD with priority-based display
render_hud() {
    load_theme "$HUD_THEME"

    # Collect all information
    local time model project_name git_branch git_status git_ahead_behind
    local context_pct cost tokens agent task progress ralph

    # Priority 1 (always show)
    model=$(get_model)

    if is_module_enabled "project"; then
        project_name=$(get_project_name)
    fi

    if is_module_enabled "git"; then
        git_branch=$(get_git_branch)
        git_status=$(get_git_status)
        if [[ -n "$git_branch" ]] && is_module_enabled "git" && [[ $(get_config ".modules.git.show_ahead_behind" "true") == "true" ]]; then
            git_ahead_behind=$(get_git_ahead_behind)
        fi
    fi

    if is_module_enabled "context"; then
        context_pct=$(get_context_usage)
    fi

    # Priority 2
    if is_module_enabled "time"; then
        time=$(get_time)
    fi

    if is_module_enabled "cost"; then
        cost=$(get_session_cost)
    fi

    if is_module_enabled "agent"; then
        agent=$(get_agent)
    fi

    # Priority 3
    if is_module_enabled "tokens"; then
        tokens=$(get_tokens)
    fi

    if is_module_enabled "task"; then
        task=$(get_task)
    fi

    if is_module_enabled "progress"; then
        progress=$(get_progress)
    fi

    if is_module_enabled "ralph"; then
        ralph=$(get_ralph_status)
    fi

    # Build output array
    local parts=()

    # Left side (context)
    [[ -n "$time" ]] && parts+=("${COLORS[dim]}$time${COLORS[reset]}")
    [[ -n "$model" ]] && parts+=("$(render_model "$model")")
    [[ -n "$project_name" ]] && parts+=("${COLORS[white]}$project_name${COLORS[reset]}")

    if [[ -n "$git_branch" ]]; then
        parts+=("$(render_git_status "$git_branch" "$git_status" "$git_ahead_behind")")
    fi

    # Right side (metrics)
    [[ -n "$context_pct" ]] && parts+=("$(render_context "$context_pct")")
    [[ -n "$cost" ]] && parts+=("$(render_cost "$cost")")
    [[ -n "$agent" ]] && parts+=("${COLORS[green]}@$agent${COLORS[reset]}")

    if [[ -n "$task" && "$task" != "idle" ]]; then
        parts+=("${COLORS[yellow]}$task${COLORS[reset]}")
    fi

    if [[ -n "$progress" && $progress -gt 0 ]]; then
        local bar
        bar=$(render_progress_bar "$progress" 10)
        parts+=("[${bar}] ${progress}%")
    fi

    [[ -n "$ralph" ]] && parts+=("${COLORS[cyan]}${COLORS[bold]}$ralph${COLORS[reset]}")
    [[ -n "$tokens" ]] && parts+=("${COLORS[dim]}$tokens${COLORS[reset]}")

    # Combine output
    local output=""
    for part in "${parts[@]}"; do
        if [[ -n "$output" ]]; then
            output+=" $SEPARATOR "
        fi
        output+="$part"
    done

    echo -e "$output"
}

# Render full HUD with border
render_full_hud() {
    load_theme "$HUD_THEME"

    local content
    content=$(render_hud)

    local width
    if [[ "$HUD_WIDTH" == "auto" ]]; then
        width=$(tput cols 2>/dev/null || echo 80)
    else
        width="$HUD_WIDTH"
    fi

    local border=""
    for ((i=0; i<width; i++)); do
        border+="$BORDER_CHAR"
    done

    echo "$border"
    echo " $content"
    echo "$border"
}

# ============================================================================
# CLI Interface
# ============================================================================

# Show help
show_help() {
    cat <<EOF
HUD Statusline Renderer v$HUD_VERSION

Usage: hud-v2.sh [command] [options]

Commands:
  render              Render statusline (default)
  full                Render with border
  config              Show current configuration
  theme <name>        Render with specific theme
  cache-clear         Clear all caches
  version             Show version
  help                Show this help

Environment Variables:
  HUD_CONFIG_FILE     Path to configuration file
  HUD_CACHE_DIR       Path to cache directory
  HUD_THEME           Theme name (default, minimal, unicode, nerd)
  HUD_WIDTH           Width (auto or number)
  HUD_SESSION_JSON    JSON session data from Claude Code

Examples:
  hud-v2.sh render
  hud-v2.sh theme nerd
  HUD_THEME=unicode hud-v2.sh render
  echo '{"session":{"contextUsed":50000}}' | HUD_SESSION_JSON="\$(cat)" hud-v2.sh render

EOF
}

# Clear cache
clear_cache() {
    rm -f "$HUD_CACHE_DIR"/*.cache
    echo "Cache cleared"
}

# Main function
main() {
    local action="${1:-render}"

    # Read stdin with timeout to prevent blocking.
    HUD_SESSION_JSON=$(timeout 0.5 cat 2>/dev/null || echo "")
    export HUD_SESSION_JSON

    # 只在 Stop 事件（cost > 0）时渲染。
    # 启动 JSON 无 cost 字段；初始化调用的 cost=0；Stop 事件 cost > 0。
    if [[ "$action" == "render" ]]; then
        local _cost
        _cost=$(echo "$HUD_SESSION_JSON" | grep -o '"total_cost_usd":[0-9.]*' | cut -d':' -f2 || echo "")
        if [[ -z "$HUD_SESSION_JSON" ]] || [[ -z "$_cost" ]] || [[ "$_cost" == "0" ]]; then
            exit 0
        fi
    fi

    case "$action" in
        "render")
            render_hud
            ;;
        "full")
            render_full_hud
            ;;
        "config")
            if [[ -f "$HUD_CONFIG_FILE" ]]; then
                cat "$HUD_CONFIG_FILE"
            else
                echo "No configuration file found at: $HUD_CONFIG_FILE"
                echo "Run 'hud-v2.sh init' to create default configuration"
            fi
            ;;
        "theme")
            HUD_THEME="${2:-default}"
            render_hud
            ;;
        "cache-clear")
            clear_cache
            ;;
        "version")
            echo "HUD Statusline v$HUD_VERSION"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo "Unknown command: $action"
            echo "Run 'hud-v2.sh help' for usage information"
            exit 1
            ;;
    esac
}

main "$@"

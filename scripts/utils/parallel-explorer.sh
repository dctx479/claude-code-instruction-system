#!/bin/bash
#
# parallel-explorer.sh - Git Worktree 并行探索工具
# 基于 Aha-Loop 方法论的多方案并行探索脚本
#
# 用法:
#   ./parallel-explorer.sh start "决策描述" --options "optA:描述" "optB:描述"
#   ./parallel-explorer.sh status
#   ./parallel-explorer.sh evaluate [option-name | --all]
#   ./parallel-explorer.sh compare [--format markdown]
#   ./parallel-explorer.sh merge <option-name> [--cleanup]
#   ./parallel-explorer.sh cleanup [--keep-branches]
#

set -e

# ============================================================================
# 配置
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
WORKTREE_PREFIX="explore-"
BRANCH_PREFIX="explore/"
STATE_FILE="${PROJECT_ROOT}/.claude/parallel-explore-state.json"
MEMORY_DIR="${PROJECT_ROOT}/memory/explorations"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================================
# 工具函数
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_git() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not a git repository"
        exit 1
    fi
}

ensure_state_dir() {
    mkdir -p "$(dirname "$STATE_FILE")"
    mkdir -p "$MEMORY_DIR"
}

# ============================================================================
# 状态管理
# ============================================================================

init_state() {
    local description="$1"
    shift
    local options=("$@")

    local options_json="["
    local first=true
    for opt in "${options[@]}"; do
        local name="${opt%%:*}"
        local desc="${opt#*:}"
        if [ "$first" = true ]; then
            first=false
        else
            options_json+=","
        fi
        options_json+="{\"name\":\"$name\",\"description\":\"$desc\",\"status\":\"pending\",\"score\":null}"
    done
    options_json+="]"

    cat > "$STATE_FILE" << EOF
{
  "description": "$description",
  "started_at": "$(date -Iseconds)",
  "status": "in_progress",
  "options": $options_json,
  "selected": null
}
EOF
}

get_state() {
    if [ -f "$STATE_FILE" ]; then
        cat "$STATE_FILE"
    else
        echo "{}"
    fi
}

update_option_status() {
    local option_name="$1"
    local new_status="$2"
    local score="$3"

    if command -v jq &> /dev/null; then
        local temp_file=$(mktemp)
        if [ -n "$score" ]; then
            jq ".options |= map(if .name == \"$option_name\" then .status = \"$new_status\" | .score = $score else . end)" "$STATE_FILE" > "$temp_file"
        else
            jq ".options |= map(if .name == \"$option_name\" then .status = \"$new_status\" else . end)" "$STATE_FILE" > "$temp_file"
        fi
        mv "$temp_file" "$STATE_FILE"
    else
        log_warn "jq not installed, state update skipped"
    fi
}

# ============================================================================
# 核心命令
# ============================================================================

cmd_start() {
    local description=""
    local options=()
    local weights=""

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --options)
                shift
                while [[ $# -gt 0 && ! "$1" =~ ^-- ]]; do
                    options+=("$1")
                    shift
                done
                ;;
            --weights)
                weights="$2"
                shift 2
                ;;
            *)
                if [ -z "$description" ]; then
                    description="$1"
                fi
                shift
                ;;
        esac
    done

    if [ -z "$description" ]; then
        log_error "Usage: parallel-explorer.sh start \"决策描述\" --options \"optA:描述\" \"optB:描述\""
        exit 1
    fi

    if [ ${#options[@]} -lt 2 ]; then
        log_error "At least 2 options required"
        exit 1
    fi

    if [ ${#options[@]} -gt 4 ]; then
        log_error "Maximum 4 options allowed"
        exit 1
    fi

    check_git
    ensure_state_dir

    # 检查是否已有进行中的探索
    if [ -f "$STATE_FILE" ]; then
        local current_status=$(jq -r '.status // "none"' "$STATE_FILE" 2>/dev/null || echo "none")
        if [ "$current_status" = "in_progress" ]; then
            log_error "An exploration is already in progress. Run 'cleanup' first."
            exit 1
        fi
    fi

    log_info "Starting parallel exploration: $description"
    log_info "Options: ${options[*]}"

    # 初始化状态
    init_state "$description" "${options[@]}"

    # 获取父目录
    local parent_dir="$(dirname "$PROJECT_ROOT")"

    # 创建 worktree
    for opt in "${options[@]}"; do
        local name="${opt%%:*}"
        local worktree_path="${parent_dir}/${WORKTREE_PREFIX}${name}"
        local branch_name="${BRANCH_PREFIX}${name}"

        log_info "Creating worktree for: $name"

        # 创建分支和 worktree
        if git show-ref --verify --quiet "refs/heads/${branch_name}"; then
            log_warn "Branch $branch_name already exists, using it"
            git worktree add "$worktree_path" "$branch_name" 2>/dev/null || true
        else
            git worktree add "$worktree_path" -b "$branch_name"
        fi

        log_success "Created: $worktree_path"
    done

    echo ""
    log_success "Exploration initialized!"
    echo ""
    echo "Next steps:"
    echo "  1. Implement each option in its worktree:"
    for opt in "${options[@]}"; do
        local name="${opt%%:*}"
        echo "     - ${parent_dir}/${WORKTREE_PREFIX}${name}"
    done
    echo "  2. Run './parallel-explorer.sh status' to check progress"
    echo "  3. Run './parallel-explorer.sh evaluate --all' when done"
    echo "  4. Run './parallel-explorer.sh compare' to see comparison"
    echo "  5. Run './parallel-explorer.sh merge <option>' to adopt best"
}

cmd_status() {
    check_git

    if [ ! -f "$STATE_FILE" ]; then
        log_warn "No active exploration found"
        exit 0
    fi

    local state=$(get_state)

    echo ""
    echo -e "${CYAN}=== Parallel Exploration Status ===${NC}"
    echo ""

    if command -v jq &> /dev/null; then
        local description=$(echo "$state" | jq -r '.description // "Unknown"')
        local status=$(echo "$state" | jq -r '.status // "unknown"')
        local started=$(echo "$state" | jq -r '.started_at // "Unknown"')

        echo -e "Description: ${YELLOW}$description${NC}"
        echo -e "Status: ${GREEN}$status${NC}"
        echo -e "Started: $started"
        echo ""
        echo "Options:"

        echo "$state" | jq -r '.options[] | "  [\(.status | if . == "completed" then "x" elif . == "in_progress" then "~" else " " end)] \(.name) - \(.description) \(if .score then "(Score: \(.score))" else "" end)"'
    else
        cat "$STATE_FILE"
    fi

    echo ""
    echo "Worktrees:"
    git worktree list | grep -E "${WORKTREE_PREFIX}" | while read -r line; do
        echo "  $line"
    done

    echo ""
}

cmd_evaluate() {
    local option_name="$1"
    local evaluate_all=false

    if [ "$option_name" = "--all" ]; then
        evaluate_all=true
    fi

    check_git

    if [ ! -f "$STATE_FILE" ]; then
        log_error "No active exploration found"
        exit 1
    fi

    local parent_dir="$(dirname "$PROJECT_ROOT")"

    if [ "$evaluate_all" = true ]; then
        log_info "Evaluating all options..."

        if command -v jq &> /dev/null; then
            local options=$(jq -r '.options[].name' "$STATE_FILE")
            for name in $options; do
                evaluate_single "$name" "$parent_dir"
            done
        else
            log_error "jq required for --all evaluation"
            exit 1
        fi
    else
        if [ -z "$option_name" ]; then
            log_error "Usage: parallel-explorer.sh evaluate <option-name> | --all"
            exit 1
        fi
        evaluate_single "$option_name" "$parent_dir"
    fi
}

evaluate_single() {
    local name="$1"
    local parent_dir="$2"
    local worktree_path="${parent_dir}/${WORKTREE_PREFIX}${name}"

    if [ ! -d "$worktree_path" ]; then
        log_warn "Worktree not found: $worktree_path"
        return
    fi

    log_info "Evaluating: $name"

    # 检查是否已有评估报告
    local result_file="${worktree_path}/EXPLORATION_RESULT.md"

    if [ -f "$result_file" ]; then
        log_success "Evaluation report exists: $result_file"

        # 尝试提取分数
        local score=$(grep -E "^\*\*总计\*\*.*\*\*[0-9]+\.[0-9]+\*\*" "$result_file" | grep -oE "[0-9]+\.[0-9]+" | tail -1 || echo "")
        if [ -n "$score" ]; then
            update_option_status "$name" "completed" "$score"
            log_info "Score: $score"
        else
            update_option_status "$name" "completed" "null"
        fi
    else
        log_warn "No EXPLORATION_RESULT.md found in $worktree_path"
        log_info "Creating template..."

        cat > "$result_file" << 'EOF'
# 方案探索结果: [方案名称]

## 元信息
- **探索分支**: explore/[name]
- **开始时间**: YYYY-MM-DD HH:mm
- **完成时间**: YYYY-MM-DD HH:mm
- **探索者**: Claude Code

## 实现摘要
[简要描述实现内容和方法]

## 评估维度 (10分制)

### 1. 可维护性 (maintainability): X/10
**评分理由**:
- [具体说明]

### 2. 可读性 (readability): X/10
**评分理由**:
- [具体说明]

### 3. 可测试性 (testability): X/10
**评分理由**:
- [具体说明]

### 4. 性能 (performance): X/10
**评分理由**:
- [具体说明]

### 5. 扩展性 (extensibility): X/10
**评分理由**:
- [具体说明]

### 6. 集成复杂度 (integration): X/10
**评分理由**:
- [具体说明]

## 综合评分
| 维度 | 权重 | 得分 | 加权得分 |
|------|------|------|----------|
| maintainability | 20% | X | X*0.2 |
| readability | 15% | X | X*0.15 |
| testability | 15% | X | X*0.15 |
| performance | 20% | X | X*0.2 |
| extensibility | 15% | X | X*0.15 |
| integration | 15% | X | X*0.15 |
| **总计** | 100% | - | **Y.YY** |

## 优势
1. [优势1]
2. [优势2]

## 劣势
1. [劣势1]
2. [劣势2]

## 风险与缓解
| 风险 | 严重程度 | 缓解措施 |
|------|----------|----------|
| [风险1] | 高/中/低 | [措施] |

## 建议
- 是否推荐采用: 是/否/有条件
- 采用条件: [如果是"有条件"，说明条件]
EOF

        log_info "Template created. Please fill in the evaluation."
        update_option_status "$name" "in_progress" "null"
    fi
}

cmd_compare() {
    local format="text"

    while [[ $# -gt 0 ]]; do
        case $1 in
            --format)
                format="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done

    check_git

    if [ ! -f "$STATE_FILE" ]; then
        log_error "No active exploration found"
        exit 1
    fi

    local state=$(get_state)
    local description=$(echo "$state" | jq -r '.description // "Unknown"')

    echo ""
    echo "# Exploration Comparison: $description"
    echo ""

    if [ "$format" = "markdown" ]; then
        echo "| Option | Score | Status | Recommendation |"
        echo "|--------|-------|--------|----------------|"

        if command -v jq &> /dev/null; then
            echo "$state" | jq -r '.options | sort_by(.score // 0) | reverse | .[] | "| \(.name) | \(.score // "N/A") | \(.status) | \(if .score != null and .score >= 7 then "Recommended" elif .score != null and .score >= 5 then "Acceptable" else "Not Recommended" end) |"'
        fi
    else
        echo "Options (sorted by score):"
        echo ""

        if command -v jq &> /dev/null; then
            echo "$state" | jq -r '.options | sort_by(.score // 0) | reverse | .[] | "  \(.name): \(.score // "N/A") (\(.status))"'
        fi
    fi

    echo ""

    # 推荐最佳方案
    if command -v jq &> /dev/null; then
        local best=$(echo "$state" | jq -r '[.options[] | select(.score != null)] | sort_by(.score) | reverse | .[0].name // "none"')
        local best_score=$(echo "$state" | jq -r '[.options[] | select(.score != null)] | sort_by(.score) | reverse | .[0].score // 0')

        if [ "$best" != "none" ] && [ "$best" != "null" ]; then
            echo -e "${GREEN}Recommended: $best (Score: $best_score)${NC}"
            echo ""
            echo "To adopt this option:"
            echo "  ./parallel-explorer.sh merge $best --cleanup"
        fi
    fi
}

cmd_merge() {
    local option_name="$1"
    local do_cleanup=false

    shift || true
    while [[ $# -gt 0 ]]; do
        case $1 in
            --cleanup)
                do_cleanup=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    if [ -z "$option_name" ]; then
        log_error "Usage: parallel-explorer.sh merge <option-name> [--cleanup]"
        exit 1
    fi

    check_git

    local branch_name="${BRANCH_PREFIX}${option_name}"
    local parent_dir="$(dirname "$PROJECT_ROOT")"
    local worktree_path="${parent_dir}/${WORKTREE_PREFIX}${option_name}"

    # 检查分支是否存在
    if ! git show-ref --verify --quiet "refs/heads/${branch_name}"; then
        log_error "Branch not found: $branch_name"
        exit 1
    fi

    # 获取当前分支
    local current_branch=$(git rev-parse --abbrev-ref HEAD)

    log_info "Merging $option_name into $current_branch..."

    # 复制评估报告到 memory
    if [ -f "${worktree_path}/EXPLORATION_RESULT.md" ]; then
        local timestamp=$(date +%Y%m%d-%H%M%S)
        local archive_file="${MEMORY_DIR}/${option_name}-${timestamp}.md"
        cp "${worktree_path}/EXPLORATION_RESULT.md" "$archive_file"
        log_info "Archived evaluation to: $archive_file"
    fi

    # 执行合并
    local description=$(jq -r '.description // "exploration"' "$STATE_FILE" 2>/dev/null || echo "exploration")

    git merge "$branch_name" --no-ff -m "feat: adopt $option_name for $description

Selected from parallel exploration.
See memory/explorations/ for detailed evaluation."

    log_success "Merged: $branch_name"

    # 更新状态
    if command -v jq &> /dev/null; then
        local temp_file=$(mktemp)
        jq ".selected = \"$option_name\" | .status = \"completed\"" "$STATE_FILE" > "$temp_file"
        mv "$temp_file" "$STATE_FILE"
    fi

    if [ "$do_cleanup" = true ]; then
        log_info "Cleaning up..."
        cmd_cleanup
    else
        echo ""
        echo "To cleanup worktrees and branches:"
        echo "  ./parallel-explorer.sh cleanup"
    fi
}

cmd_cleanup() {
    local keep_branches=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --keep-branches)
                keep_branches=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done

    check_git

    local parent_dir="$(dirname "$PROJECT_ROOT")"

    log_info "Cleaning up exploration..."

    # 删除 worktree
    git worktree list | grep -E "${WORKTREE_PREFIX}" | awk '{print $1}' | while read -r worktree; do
        if [ -d "$worktree" ]; then
            log_info "Removing worktree: $worktree"
            git worktree remove "$worktree" --force 2>/dev/null || rm -rf "$worktree"
        fi
    done

    # 删除分支
    if [ "$keep_branches" = false ]; then
        git branch --list "${BRANCH_PREFIX}*" | while read -r branch; do
            branch=$(echo "$branch" | tr -d ' *')
            if [ -n "$branch" ]; then
                log_info "Deleting branch: $branch"
                git branch -D "$branch" 2>/dev/null || true
            fi
        done
    fi

    # 清理状态文件
    if [ -f "$STATE_FILE" ]; then
        rm "$STATE_FILE"
        log_info "Removed state file"
    fi

    # 清理 worktree 元数据
    git worktree prune

    log_success "Cleanup complete!"
}

cmd_help() {
    cat << 'EOF'
parallel-explorer.sh - Git Worktree 并行探索工具

用法:
  parallel-explorer.sh <command> [options]

命令:
  start     启动新的并行探索
  status    查看当前探索状态
  evaluate  评估方案（生成/检查评估报告）
  compare   对比所有方案
  merge     合并最佳方案到当前分支
  cleanup   清理所有探索工作树和分支
  help      显示帮助信息

示例:
  # 启动探索
  ./parallel-explorer.sh start "数据库选型" \
    --options "postgresql:关系型数据库" "mongodb:文档数据库" "mysql:开源关系型"

  # 查看状态
  ./parallel-explorer.sh status

  # 评估所有方案
  ./parallel-explorer.sh evaluate --all

  # 对比方案
  ./parallel-explorer.sh compare --format markdown

  # 合并最佳方案并清理
  ./parallel-explorer.sh merge postgresql --cleanup

  # 仅清理
  ./parallel-explorer.sh cleanup

工作流程:
  1. start   - 创建 worktree 和分支
  2. 实现    - 在各 worktree 中实现方案
  3. evaluate - 生成评估报告
  4. compare - 对比选择最佳
  5. merge   - 合并到主分支
  6. cleanup - 清理临时文件

更多信息:
  参见 .claude/skills/parallel-explore/SKILL.md

EOF
}

# ============================================================================
# 主入口
# ============================================================================

main() {
    local command="${1:-help}"
    shift || true

    case "$command" in
        start)
            cmd_start "$@"
            ;;
        status)
            cmd_status "$@"
            ;;
        evaluate)
            cmd_evaluate "$@"
            ;;
        compare)
            cmd_compare "$@"
            ;;
        merge)
            cmd_merge "$@"
            ;;
        cleanup)
            cmd_cleanup "$@"
            ;;
        help|--help|-h)
            cmd_help
            ;;
        *)
            log_error "Unknown command: $command"
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"

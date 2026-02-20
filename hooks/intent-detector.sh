#!/bin/bash
# Intent Detector Hook - 意图识别系统
# 版本: 1.0.0
# 触发时机: PreToolUse - 在工具执行前分析用户意图
#
# 功能:
# 1. 检测用户输入中的关键词和意图
# 2. 自动激活相关的 Agent 或 Skill
# 3. 提供上下文增强建议

set -euo pipefail

# 配置
KEYWORDS_FILE="${KEYWORDS_FILE:-$(dirname "$0")/../../config/keywords.json}"
INTENT_LOG="${INTENT_LOG:-$HOME/.claude/intent.log}"

# 日志函数
log() {
    local level="$1"
    shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*" >> "$INTENT_LOG"
}

# 读取输入
INPUT=$(cat)

# 提取用户消息 (如果在消息上下文中)
USER_MESSAGE=$(echo "$INPUT" | grep -o '"user_message":"[^"]*"' | cut -d'"' -f4 || echo "")

# 如果没有用户消息，尝试从工具输入中提取
if [[ -z "$USER_MESSAGE" ]]; then
    USER_MESSAGE=$(echo "$INPUT" | grep -o '"content":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "")
fi

log "DEBUG" "Analyzing intent for: $USER_MESSAGE"

# 意图检测函数
detect_intent() {
    local message="$1"
    local message_lower=$(echo "$message" | tr '[:upper:]' '[:lower:]')

    # 代码相关意图
    if echo "$message_lower" | grep -qE 'debug|调试|bug|错误|fix|修复'; then
        echo "debug"
        return
    fi

    if echo "$message_lower" | grep -qE 'review|审查|code review|代码审查'; then
        echo "review"
        return
    fi

    if echo "$message_lower" | grep -qE 'test|测试|单元测试|unit test'; then
        echo "test"
        return
    fi

    if echo "$message_lower" | grep -qE 'refactor|重构|优化代码'; then
        echo "refactor"
        return
    fi

    # 架构相关意图
    if echo "$message_lower" | grep -qE 'architect|架构|设计|design|系统设计'; then
        echo "architect"
        return
    fi

    # 安全相关意图
    if echo "$message_lower" | grep -qE 'security|安全|漏洞|vulnerability|audit'; then
        echo "security"
        return
    fi

    # 数据相关意图
    if echo "$message_lower" | grep -qE 'sql|database|数据库|query|查询'; then
        echo "data"
        return
    fi

    if echo "$message_lower" | grep -qE 'analyze|分析|statistics|统计|visualization|可视化'; then
        echo "analysis"
        return
    fi

    # AI/ML 相关意图
    if echo "$message_lower" | grep -qE 'pytorch|tensorflow|model|模型|train|训练|neural|深度学习'; then
        echo "ml"
        return
    fi

    # 科研相关意图
    if echo "$message_lower" | grep -qE 'paper|论文|literature|文献|research|研究|experiment|实验'; then
        echo "research"
        return
    fi

    # 文档相关意图
    if echo "$message_lower" | grep -qE 'document|文档|readme|spec|规范'; then
        echo "document"
        return
    fi

    # Git/版本控制意图
    if echo "$message_lower" | grep -qE 'commit|pr|pull request|merge|branch|分支'; then
        echo "git"
        return
    fi

    # 部署相关意图
    if echo "$message_lower" | grep -qE 'deploy|部署|docker|kubernetes|k8s|ci/cd'; then
        echo "deploy"
        return
    fi

    # 默认意图
    echo "general"
}

# 推荐 Agent
recommend_agent() {
    local intent="$1"
    case "$intent" in
        "debug")
            echo "debugger"
            ;;
        "review")
            echo "code-reviewer"
            ;;
        "test")
            echo "automated-testing"
            ;;
        "refactor")
            echo "code-reviewer"
            ;;
        "architect")
            echo "architect"
            ;;
        "security")
            echo "security-analyst"
            ;;
        "data")
            echo "data-scientist"
            ;;
        "analysis")
            echo "data-analyst"
            ;;
        "ml")
            echo "deep-learning"
            ;;
        "research")
            echo "literature-manager"
            ;;
        "document")
            echo "spec-writer"
            ;;
        "git")
            echo "orchestrator"
            ;;
        "deploy")
            echo "orchestrator"
            ;;
        *)
            echo "orchestrator"
            ;;
    esac
}

# 推荐 Skill
recommend_skill() {
    local intent="$1"
    case "$intent" in
        "ml")
            echo "pytorch,tensorflow"
            ;;
        "data"|"analysis")
            echo "pandas,data-analysis"
            ;;
        "research")
            echo "literature,paper-writing"
            ;;
        *)
            echo ""
            ;;
    esac
}

# 主逻辑
if [[ -n "$USER_MESSAGE" ]]; then
    intent=$(detect_intent "$USER_MESSAGE")
    agent=$(recommend_agent "$intent")
    skill=$(recommend_skill "$intent")

    log "INFO" "Intent: $intent, Agent: $agent, Skill: $skill"

    # 注意: 子进程 export 无法传递到父进程
    # 将推荐结果写入文件供 HUD 等读取
    INTENT_STATE_FILE="${HOME}/.claude/intent-state.json"
    mkdir -p "$(dirname "$INTENT_STATE_FILE")" 2>/dev/null
    printf '{"intent":"%s","agent":"%s","skill":"%s"}\n' \
        "$intent" "$agent" "$skill" > "$INTENT_STATE_FILE"

    # 输出建议 (可选，供调试)
    if [[ "${INTENT_VERBOSE:-false}" == "true" ]]; then
        echo "Intent detected: $intent"
        echo "Recommended agent: $agent"
        if [[ -n "$skill" ]]; then
            echo "Recommended skills: $skill"
        fi
    fi
fi

# 允许继续执行
exit 0

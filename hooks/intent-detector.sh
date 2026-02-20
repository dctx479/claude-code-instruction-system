#!/bin/bash
# Intent Detector Hook - 意图识别系统
# 版本: 2.0.0
# 触发时机: UserPromptSubmit - 在用户提交消息时分析意图
#
# 功能:
# 1. 检测用户输入中的关键词和意图
# 2. 自动激活相关的 Agent 或 Skill
# 3. 写入 intent-state.json 驱动 Agent 自动调度

set -euo pipefail

# 配置
KEYWORDS_FILE="${KEYWORDS_FILE:-$(dirname "$0")/../config/keywords.json}"
INTENT_LOG="${INTENT_LOG:-$HOME/.claude/intent.log}"

# 日志函数
log() {
    local level="$1"
    shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*" >> "$INTENT_LOG"
}

# 读取输入
INPUT=$(cat)

# 提取用户消息 (UserPromptSubmit hook 的 stdin JSON 字段是 "prompt")
USER_MESSAGE=$(echo "$INPUT" | grep -o '"prompt":"[^"]*"' | cut -d'"' -f4 || echo "")

# 如果没有用户消息，尝试从工具输入中提取
if [[ -z "$USER_MESSAGE" ]]; then
    USER_MESSAGE=$(echo "$INPUT" | grep -o '"content":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "")
fi

log "DEBUG" "Analyzing intent for: $USER_MESSAGE"

# 意图检测函数
detect_intent() {
    local message="$1"
    local message_lower=$(echo "$message" | tr '[:upper:]' '[:lower:]')

    # === 高优先级：精确命令和特殊触发 ===

    # Autopilot 模式 (必须最先检测，避免被其他规则截获)
    if echo "$message_lower" | grep -qE '/autopilot|autopilot|全自主|端到端'; then
        echo "autopilot"
        return
    fi

    # QA 质量审查
    if echo "$message_lower" | grep -qE 'qa|质量审查|质量检查|验收|qa-review|qa report'; then
        echo "qa-review"
        return
    fi

    # QA 自动修复
    if echo "$message_lower" | grep -qE 'qa.*fix|qa.*修复|自动修复|autofix|qa-fix'; then
        echo "qa-fix"
        return
    fi

    # 性能监控
    if echo "$message_lower" | grep -qE 'performance.*report|性能报告|性能监控|performance.*monitor|agent.*性能'; then
        echo "perf-monitor"
        return
    fi

    # 系统优化
    if echo "$message_lower" | grep -qE 'optimize.*system|系统优化|auto.*optim|成本优化|token.*优化|优化.*token|优化.*系统'; then
        echo "optimize"
        return
    fi

    # === 代码相关意图 ===

    if echo "$message_lower" | grep -qE 'debug|调试|bug|错误|fix|修复|报错|崩溃|异常|traceback|stack.*trace'; then
        echo "debug"
        return
    fi

    if echo "$message_lower" | grep -qE 'review|审查|code review|代码审查|代码质量'; then
        echo "review"
        return
    fi

    if echo "$message_lower" | grep -qE 'test|测试|单元测试|unit test|e2e|集成测试|覆盖率|coverage'; then
        echo "test"
        return
    fi

    if echo "$message_lower" | grep -qE 'refactor|重构|优化代码|代码整理'; then
        echo "refactor"
        return
    fi

    # === 架构相关意图 ===

    if echo "$message_lower" | grep -qE 'architect|架构|系统设计|system design|技术选型|微服务|monolith'; then
        echo "architect"
        return
    fi

    # === 安全相关意图 ===

    if echo "$message_lower" | grep -qE 'security.*audit|安全审计|dependency.*scan|依赖.*扫描|cve|合规|compliance|gdpr|hipaa'; then
        echo "security-audit"
        return
    fi

    if echo "$message_lower" | grep -qE 'security|安全|漏洞|vulnerability|xss|injection|csrf'; then
        echo "security"
        return
    fi

    # === AI/ML 相关意图 (细分，必须在通用"分析"之前) ===

    if echo "$message_lower" | grep -qE 'reinforcement.*learn|强化学习|dqn|ppo|sac|maddpg|reward.*function|agent.*policy'; then
        echo "rl"
        return
    fi

    if echo "$message_lower" | grep -qE 'interpret.*model|解释.*模型|shap|lime|可解释性|fairness|公平性|bias.*detect|captum'; then
        echo "interpretability"
        return
    fi

    if echo "$message_lower" | grep -qE 'time.*series|时间序列|forecast|arima|prophet|趋势预测|序列预测'; then
        echo "timeseries"
        return
    fi

    if echo "$message_lower" | grep -qE 'pytorch|tensorflow|train.*model|训练.*模型|neural.*net|深度学习|cnn|rnn|transformer|gan|模型.*训练'; then
        echo "ml"
        return
    fi

    # === 数据与可视化意图 ===

    if echo "$message_lower" | grep -qE 'visualization|可视化|chart|图表|plot|绘图|dashboard|仪表盘'; then
        echo "visualization"
        return
    fi

    if echo "$message_lower" | grep -qE 'sql|database|数据库|query|查询'; then
        echo "data"
        return
    fi

    if echo "$message_lower" | grep -qE 'analyze|分析|statistics|统计|预测'; then
        echo "analysis"
        return
    fi

    # === 科研相关意图 (细分) ===

    if echo "$message_lower" | grep -qE 'experiment|实验.*记录|实验.*追踪|实验.*配置|experiment.*track|实验.*对比'; then
        echo "experiment"
        return
    fi

    if echo "$message_lower" | grep -qE 'paper.*writ|论文写作|综述.*写|写.*论文|draft.*paper|撰写'; then
        echo "paper-writing"
        return
    fi

    if echo "$message_lower" | grep -qE 'paper|论文|literature|文献|research|研究|文献.*综述|引用'; then
        echo "research"
        return
    fi

    # === 文档相关意图 ===

    if echo "$message_lower" | grep -qE 'document|文档|readme|spec|规范|specification'; then
        echo "document"
        return
    fi

    # === Git/版本控制意图 ===

    if echo "$message_lower" | grep -qE 'commit|pr|pull request|merge|branch|分支'; then
        echo "git"
        return
    fi

    # === 部署相关意图 ===

    if echo "$message_lower" | grep -qE 'deploy|部署|docker|kubernetes|k8s|ci/cd'; then
        echo "deploy"
        return
    fi

    # === 上下文归档 ===

    if echo "$message_lower" | grep -qE 'save.*context|保存.*上下文|归档|archive.*context'; then
        echo "archive"
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
        "security-audit")
            echo "security-audit"
            ;;
        "data")
            echo "data-scientist"
            ;;
        "analysis")
            echo "data-analyst"
            ;;
        "visualization")
            echo "data-visualization"
            ;;
        "ml")
            echo "deep-learning"
            ;;
        "rl")
            echo "reinforcement-learning"
            ;;
        "timeseries")
            echo "time-series-analysis"
            ;;
        "interpretability")
            echo "model-interpretability"
            ;;
        "research")
            echo "literature-manager"
            ;;
        "paper-writing")
            echo "paper-writing-assistant"
            ;;
        "experiment")
            echo "experiment-logger"
            ;;
        "document")
            echo "spec-writer"
            ;;
        "qa-review")
            echo "qa-reviewer"
            ;;
        "qa-fix")
            echo "qa-fixer"
            ;;
        "perf-monitor")
            echo "performance-monitor"
            ;;
        "optimize")
            echo "auto-optimizer"
            ;;
        "autopilot")
            echo "autopilot-orchestrator"
            ;;
        "archive")
            echo "context-archivist"
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
        "rl")
            echo "reinforcement-learning"
            ;;
        "timeseries")
            echo "time-series,prophet"
            ;;
        "interpretability")
            echo "shap,lime"
            ;;
        "data"|"analysis")
            echo "pandas,data-analysis"
            ;;
        "visualization")
            echo "matplotlib,plotly"
            ;;
        "research")
            echo "literature,paper-writing"
            ;;
        "paper-writing")
            echo "paper-writing,literature-mentor"
            ;;
        "experiment")
            echo "experiment-tracking"
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
    # 将推荐结果写入文件供 HUD 和 Auto-Dispatch 读取
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

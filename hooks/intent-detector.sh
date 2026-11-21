#!/bin/bash
# Intent Detector Hook - 意图识别系统
# Version: 2.3.0
# 触发时机: UserPromptSubmit - 在用户提交消息时分析意图
#
# 功能:
# 1. 检测用户输入中的关键词和意图
# 2. 自动激活相关的 Agent 或 Skill
# 3. Publish advisory context and isolated session state

set -euo pipefail

# 配置
KEYWORDS_FILE="${KEYWORDS_FILE:-$(dirname "$0")/../config/keywords.json}"

# Parse actual JSON, then strip quoted material before applying keyword routing.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONTEXT_HELPER="$SCRIPT_DIR/intent-context.py"
INPUT=$(cat)
if ! command -v python >/dev/null 2>&1; then
    echo "WARNING: intent routing skipped: python is unavailable" >&2
    exit 0
fi
if ! USER_MESSAGE=$(printf '%s' "$INPUT" | python "$CONTEXT_HELPER" select); then
    exit 0  # advisory routing must not block the user's request
fi

detect_intent() {
    local message="$1"
    local message_lower=$(echo "$message" | tr '[:upper:]' '[:lower:]')

    # === 高优先级：精确命令和特殊触发 ===

    # Autopilot 模式 (必须最先检测，避免被其他规则截获)
    if echo "$message_lower" | grep -qE '/autopilot|autopilot|全自主|端到端'; then
        echo "autopilot"
        return
    fi

    # QA 自动修复 (须在 qa-review 之前，否则被其中的 "qa" 关键词截获)
    if echo "$message_lower" | grep -qE 'qa.*fix|qa.*修复|自动修复|autofix|qa-fix'; then
        echo "qa-fix"
        return
    fi

    # QA 质量审查
    if echo "$message_lower" | grep -qE '\bqa\b|质量审查|质量检查|验收|qa-review|qa report'; then
        echo "qa-review"
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

    # === 角色专用意图 (高优先级：须在 test/architect/analysis 等通用规则之前，模式须足够精确以免误截通用消息) ===

    # Vitest 测试 (须在通用 test 规则之前，否则 "vitest" 被 "test" 子串截获)
    if echo "$message_lower" | grep -qE 'vitest'; then
        echo "vitest"
        return
    fi

    # SDD-RIPER 规范驱动开发流程
    if echo "$message_lower" | grep -qE 'sdd-riper|sdd riper|\briper\b|规范驱动开发|spec-driven'; then
        echo "sdd-riper"
        return
    fi

    # 高级代码架构师 (须在通用 architect 规则之前)
    if echo "$message_lower" | grep -qE 'senior.*architect|资深架构|高级架构师|senior.*code.*architect'; then
        echo "architect-senior"
        return
    fi

    # 技术导师 (须在通用 architect 规则之前)
    if echo "$message_lower" | grep -qE 'mentor|技术导师|手把手|带我学|带我入门'; then
        echo "mentor"
        return
    fi

    # 需求分析 (须在通用 analysis "分析" 规则之前)
    if echo "$message_lower" | grep -qE '需求分析|需求拆解|需求评审|用户故事|user.*story|requirement.*analy|功能拆解'; then
        echo "requirements"
        return
    fi

    # 数据仓库/数仓分析 (须在通用 data/analysis 规则之前)
    if echo "$message_lower" | grep -qE 'data.*warehouse|数据仓库|数仓|数据平台|olap|多维分析'; then
        echo "data-warehouse"
        return
    fi

    # 代码地图/代码库导航
    if echo "$message_lower" | grep -qE 'code.*map|代码地图|代码库导航|codebase.*nav'; then
        echo "codemap"
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

    # Generic project/workflow analysis is not necessarily data analysis.
    if echo "$message_lower" | grep -qE 'statistics|统计|数据分析|数据.*分析|分析.*数据|analy[sz]e.*data|data.*analy[sz]|趋势预测'; then
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
        "requirements")
            echo "requirements-analyst"
            ;;
        "mentor")
            echo "tech-mentor"
            ;;
        "architect-senior")
            echo "senior-code-architect"
            ;;
        "vitest")
            echo "vitest-tester"
            ;;
        "sdd-riper")
            echo "sdd-riper-orchestrator"
            ;;
        "data-warehouse")
            echo "data-warehouse-analyst"
            ;;
        "codemap")
            echo "codemap-builder"
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

# === v2.1.0 新增：外部工具需求检测 ===
# 功能: 匹配 config/keywords.json 的 external_tools 分类关键词
# 输出: JSON 字符串 {tool, priority, install_cmd, verify_cmd, expected, doc}
# 无匹配时输出空字符串 ""
detect_external_tool() {
 local message="$1"
 local message_lower=$(echo "$message" | tr '[:upper:]' '[:lower:]')
 local script_dir="$(cd "$(dirname "$0")" && pwd)"
 local helper="${script_dir}/detect-external-tool.py"

 if [[ ! -f "$helper" || ! -f "$KEYWORDS_FILE" ]]; then
     echo "WARNING: optional tool recommendation unavailable: helper/config missing" >&2
     return 0
 fi
 if ! python "$helper" "$KEYWORDS_FILE" "$message_lower"; then
     echo "WARNING: optional tool recommendation failed" >&2
 fi
}


# Main: current-turn stdout is authoritative; disk state is diagnostic only.
if [[ "$USER_MESSAGE" =~ ^@([a-z][a-z0-9-]*)($|[[:space:]]) ]]; then
    intent="manual"
    agent="${BASH_REMATCH[1]}"
    skill=""
else
    intent=$(detect_intent "$USER_MESSAGE")
    agent=$(recommend_agent "$intent")
    skill=$(recommend_skill "$intent")
fi
tool_rec=$(detect_external_tool "$USER_MESSAGE")
if ! printf '%s' "$INPUT" | python "$CONTEXT_HELPER" publish \
    --state-dir "$HOME/.claude" --intent "$intent" --agent "$agent" \
    --skill "$skill" --tool "$tool_rec"; then
    echo "WARNING: intent context could not be published" >&2
fi
exit 0

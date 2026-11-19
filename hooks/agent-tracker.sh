#!/bin/bash
# Agent State Tracker Hook
# 版本: 2.0.0
# 触发时机: PreToolUse，matcher "Agent|Task"
#   （Claude Code 2.1.63 起子代理工具由 Task 更名为 Agent，两个名字都接受）
# 作用: 把当前启动的子代理类型写入项目的 .claude/agent-state.json，供 statusline 读取

set -euo pipefail

# 工具名和参数都来自 stdin JSON（Claude Code 不提供 TOOL_NAME 环境变量）
INPUT=$(cat)

TOOL_NAME=$(printf '%s' "$INPUT" | grep -o '"tool_name"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/' || echo "")

case "$TOOL_NAME" in
    Agent|Task) ;;
    *) exit 0 ;;
esac

# 提取 subagent_type（使用 grep/sed，不依赖 jq）
AGENT_TYPE=$(printf '%s' "$INPUT" | grep -o '"subagent_type"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/' || echo "")

if [[ -z "$AGENT_TYPE" ]]; then
    exit 0
fi

# 安全: 验证 AGENT_TYPE 仅包含合法字符 (字母、数字、连字符、下划线、插件命名空间冒号)
if [[ ! "$AGENT_TYPE" =~ ^[a-zA-Z0-9_:-]+$ ]]; then
    echo "⚠️ WARNING: Invalid agent type: $AGENT_TYPE" >&2
    exit 0
fi

# 只在已有 .claude/ 目录的项目里记录，避免给无关项目凭空创建目录
STATE_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude"
[[ -d "$STATE_DIR" ]] || exit 0

AGENT_STATE_FILE="$STATE_DIR/agent-state.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# 使用 printf 安全写入，避免 heredoc 注入
printf '{\n  "current_agent": "%s",\n  "last_updated": "%s",\n  "agent_history": []\n}\n' \
    "$AGENT_TYPE" "$TIMESTAMP" > "$AGENT_STATE_FILE"

exit 0

#!/bin/bash
# Agent State Tracker Hook
# 在 Task 工具调用时更新 .claude/agent-state.json

set -euo pipefail

# 获取工具名称
TOOL_NAME="${TOOL_NAME:-}"

# 只处理 Task 工具
if [[ "$TOOL_NAME" != "Task" ]]; then
    exit 0
fi

# 从 stdin 读取工具参数
TOOL_INPUT=$(cat)

# 提取 subagent_type（使用 grep/sed，不依赖 jq）
AGENT_TYPE=$(echo "$TOOL_INPUT" | grep -o '"subagent_type"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"subagent_type"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' || echo "")

if [[ -z "$AGENT_TYPE" ]]; then
    exit 0
fi

# 安全: 验证 AGENT_TYPE 仅包含合法字符 (字母、数字、连字符)
if [[ ! "$AGENT_TYPE" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "WARNING: Invalid agent type: $AGENT_TYPE" >&2
    exit 0
fi

# 更新 agent-state.json
AGENT_STATE_FILE=".claude/agent-state.json"
mkdir -p "$(dirname "$AGENT_STATE_FILE")" 2>/dev/null
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# 使用 printf 安全写入，避免 heredoc 注入
printf '{\n  "current_agent": "%s",\n  "last_updated": "%s",\n  "agent_history": []\n}\n' \
    "$AGENT_TYPE" "$TIMESTAMP" > "$AGENT_STATE_FILE"

exit 0

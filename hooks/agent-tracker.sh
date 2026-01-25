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

# 更新 agent-state.json
AGENT_STATE_FILE=".claude/agent-state.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# 创建或更新状态文件
cat > "$AGENT_STATE_FILE" <<EOF
{
  "current_agent": "$AGENT_TYPE",
  "last_updated": "$TIMESTAMP",
  "agent_history": []
}
EOF

exit 0

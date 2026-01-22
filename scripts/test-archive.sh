#!/bin/bash
# 测试 PreCompact Hook 和归档脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Windows 环境设置 UTF-8
export PYTHONIOENCODING=utf-8

echo "=== PreCompact Hook 测试 ==="
echo ""

# 测试 1: 低阈值场景 (应跳过)
echo "测试 1: 低阈值场景"
export CLAUDE_TOKEN_COUNT=1000
export CLAUDE_MESSAGE_COUNT=10
export CLAUDE_SESSION_ID="test-session-1"

bash "$PROJECT_ROOT/.claude/hooks/pre-compact.sh"
echo ""

# 测试 2: 高阈值场景 (应执行归档)
echo "测试 2: 高阈值场景"
export CLAUDE_TOKEN_COUNT=160000
export CLAUDE_MESSAGE_COUNT=60
export CLAUDE_SESSION_ID="test-session-2"

bash "$PROJECT_ROOT/.claude/hooks/pre-compact.sh"
echo ""

# 测试 3: 直接测试归档脚本
echo "测试 3: 直接测试归档脚本"
cat > "$PROJECT_ROOT/test-data.json" <<'EOF'
{
  "session_id": "test-session-3",
  "token_count": 180000,
  "message_count": 80,
  "messages": [
    {
      "role": "user",
      "content": "修复这个错误",
      "timestamp": "2026-01-22T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "已修复，使用了新的方法",
      "timestamp": "2026-01-22T10:01:00Z"
    },
    {
      "role": "user",
      "content": "为什么选择这个方案？",
      "timestamp": "2026-01-22T10:02:00Z"
    },
    {
      "role": "assistant",
      "content": "决定采用方案A，因为性能更好",
      "timestamp": "2026-01-22T10:03:00Z"
    }
  ]
}
EOF

python "$PROJECT_ROOT/scripts/archive-context.py" "$PROJECT_ROOT/test-data.json"
rm "$PROJECT_ROOT/test-data.json"
echo ""

# 检查生成的归档文件
echo "=== 生成的归档文件 ==="
ls -lh "$PROJECT_ROOT/.claude/memory/context-archives/" | tail -5
echo ""

echo "[OK] 所有测试完成"

#!/bin/bash
# PreCompact Hook - 在上下文压缩前自动沉淀知识
# 触发时机: Claude Code 即将执行 /compact 命令时

echo "🧠 [PreCompact Hook] 上下文即将压缩"
echo "💡 建议: 运行 /save-context 手动保存重要对话内容"
echo ""

# 注意: Claude Code 的 PreCompact Hook 目前无法直接访问完整对话内容
# 因此需要用户在压缩前手动运行 /save-context 命令
#
# 未来改进方向:
# 1. 如果 Claude Code 提供对话导出 API，可在此自动调用
# 2. 或者通过 MCP 工具访问对话历史

exit 0

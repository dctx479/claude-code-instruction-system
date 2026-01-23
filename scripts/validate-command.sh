#!/bin/bash
# Bash 命令安全性验证工具
# 版本: 1.0.0
# 用途: 在执行 Bash 工具前验证命令安全性

# 读取输入（从 stdin 接收 JSON）
INPUT=$(cat)

# 提取命令（使用 jq 解析 JSON）
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

# 如果没有 jq，尝试简单的文本匹配
if [ -z "$COMMAND" ]; then
    COMMAND=$(echo "$INPUT" | grep -oP '"command"\s*:\s*"\K[^"]+' | head -1)
fi

# 如果仍然为空，直接通过
if [ -z "$COMMAND" ]; then
    exit 0
fi

# ============================================================
# 安全检查规则
# ============================================================

# 1. 检查危险的删除命令
if echo "$COMMAND" | grep -iE 'rm\s+-rf\s+(/|~|\$HOME|\.\./)' > /dev/null; then
    echo "❌ BLOCKED: Dangerous recursive delete detected" >&2
    echo "   Command: $COMMAND" >&2
    exit 2
fi

# 2. 检查 sudo/su 提权命令
if echo "$COMMAND" | grep -iE '^(sudo|su)\s+' > /dev/null; then
    echo "⚠️  WARNING: Privilege escalation detected" >&2
    echo "   Command: $COMMAND" >&2
    # 仅警告，不阻止（如果需要阻止，改为 exit 2）
    exit 1
fi

# 3. 检查不安全的权限设置
if echo "$COMMAND" | grep -iE 'chmod\s+(777|666)' > /dev/null; then
    echo "⚠️  WARNING: Insecure permissions detected" >&2
    echo "   Command: $COMMAND" >&2
    exit 1
fi

# 4. 检查潜在的代码注入
if echo "$COMMAND" | grep -E ';\s*(rm|dd|mkfs|:(){ :|:& };:)' > /dev/null; then
    echo "❌ BLOCKED: Potential code injection detected" >&2
    echo "   Command: $COMMAND" >&2
    exit 2
fi

# 5. 检查网络操作（可选）
if echo "$COMMAND" | grep -iE '(wget|curl).*(\||>|>>)' > /dev/null; then
    echo "⚠️  WARNING: Network operation with redirection detected" >&2
    echo "   Command: $COMMAND" >&2
    exit 1
fi

# 6. 检查格式化命令
if echo "$COMMAND" | grep -iE '(mkfs|fdisk|parted)' > /dev/null; then
    echo "❌ BLOCKED: Disk formatting command detected" >&2
    echo "   Command: $COMMAND" >&2
    exit 2
fi

# ============================================================
# 通过验证
# ============================================================

# 记录日志（可选）
# echo "[$(date)] ✓ Command validated: $COMMAND" >> ~/.claude/command-validation.log

exit 0

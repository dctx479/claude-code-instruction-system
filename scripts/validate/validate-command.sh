#!/bin/bash
# Bash 命令安全性验证工具
# 版本: 1.2.0
# 用途: 在执行 Bash 工具前验证命令安全性

set -euo pipefail

# 读取输入（从 stdin 接收 JSON）
INPUT=$(cat)

# 提取命令（使用 jq 解析 JSON）
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null || echo "")

# 如果没有 jq，尝试可移植的文本匹配（兼容 GNU/BSD grep）
# 正则必须允许转义字符：真实命令里的引号在 JSON 中是 \"，按 [^"]* 匹配会在第一个引号处截断，
# 导致其后的危险片段（如 echo "x" && rm -rf /）逃过检查
if [ -z "$COMMAND" ]; then
    COMMAND=$(printf '%s' "$INPUT" | grep -o '"command"[[:space:]]*:[[:space:]]*"\(\\.\|[^"\\]\)*"' | head -1 \
        | sed -e 's/^"command"[[:space:]]*:[[:space:]]*"//' -e 's/"$//' -e 's/\\"/"/g' -e 's/\\\\/\\/g' || echo "")
fi

# 如果仍然为空，直接通过
if [ -z "$COMMAND" ]; then
    exit 0
fi

# ============================================================
# 安全检查规则
# ============================================================

# 阻塞规则（exit 2）必须排在警告规则（exit 1，非阻塞）之前：
# 警告规则命中后会直接退出，排在前面会让 sudo mkfs ... 这类命令只得到一个警告就放行

# ── 阻塞规则 ─────────────────────────────────────────────────

# 1. 检查危险的删除命令
if echo "$COMMAND" | grep -iE 'rm\s+-rf\s+(/|~|\$HOME|\.\./)' > /dev/null; then
    echo "❌ BLOCKED: Dangerous recursive delete detected" >&2
    echo "   Command: $COMMAND" >&2
    exit 2
fi

# 4. 检查潜在的代码注入
if echo "$COMMAND" | grep -E ';\s*(rm|dd|mkfs|:(){ :|:& };:)' > /dev/null; then
    echo "❌ BLOCKED: Potential code injection detected" >&2
    echo "   Command: $COMMAND" >&2
    exit 2
fi

# 6. 检查格式化命令
# 只匹配处于"命令位置"的格式化工具（行首，或 ; & | ( 之后，可带 sudo），
# 避免把 grep fdisk docs/、echo "mkfs 用法" 这类只是提到名字的命令也拦下
if echo "$COMMAND" | grep -iE '(^|[;&|(])[[:space:]]*(sudo[[:space:]]+)?(mkfs(\.[a-z0-9]+)?|fdisk|parted)([[:space:]]|$)' > /dev/null; then
    echo "❌ BLOCKED: Disk formatting command detected" >&2
    echo "   Command: $COMMAND" >&2
    exit 2
fi

# ── 警告规则（仅提示，不阻止）─────────────────────────────────

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

# 5. 检查网络操作（可选）
if echo "$COMMAND" | grep -iE '(wget|curl).*(\||>|>>)' > /dev/null; then
    echo "⚠️  WARNING: Network operation with redirection detected" >&2
    echo "   Command: $COMMAND" >&2
    exit 1
fi

# ============================================================
# 通过验证
# ============================================================

# 记录日志（可选）
# echo "[$(date)] ✓ Command validated: $COMMAND" >> ~/.claude/command-validation.log

exit 0

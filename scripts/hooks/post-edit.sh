#!/bin/bash
# 文件编辑后处理脚本
# 版本: 1.1.0
# 用途: 在 Edit 工具执行后运行代码质量检查

set -uo pipefail

# 从 stdin 读取工具输出（Claude Code PostToolUse hook 通过 stdin 传入）
TOOL_DATA=$(cat 2>/dev/null || echo "{}")

# 获取编辑的文件路径
FILE_PATH=$(echo "$TOOL_DATA" | jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")

# 如果无法从 stdin 获取，尝试环境变量
if [ -z "$FILE_PATH" ]; then
    FILE_PATH="${EDITED_FILE:-}"
fi

# 记录日志
LOG_FILE="${HOME}/.claude/post-edit.log"
mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null

echo "[$(date)] Post-edit hook triggered" >> "$LOG_FILE"
[ -n "$FILE_PATH" ] && echo "  File: $FILE_PATH" >> "$LOG_FILE"

# ============================================================
# 1. 运行 Linter（如果项目有配置）
# ============================================================

# 检测项目类型并运行相应的 linter
if [ -f "package.json" ]; then
    # Node.js 项目
    if [ -f ".eslintrc.js" ] || [ -f ".eslintrc.json" ] || [ -f "eslint.config.js" ]; then
        echo "  Running ESLint..." >> "$LOG_FILE"
        npm run lint --silent 2>/dev/null || npx eslint --fix "$FILE_PATH" 2>/dev/null || true
    fi

    # Prettier
    if [ -f ".prettierrc" ] || [ -f ".prettierrc.json" ]; then
        echo "  Running Prettier..." >> "$LOG_FILE"
        npx prettier --write "$FILE_PATH" 2>/dev/null || true
    fi
fi

# Python 项目
if [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    if command -v black >/dev/null 2>&1; then
        echo "  Running Black..." >> "$LOG_FILE"
        black "$FILE_PATH" 2>/dev/null || true
    fi

    if command -v ruff >/dev/null 2>&1; then
        echo "  Running Ruff..." >> "$LOG_FILE"
        ruff check --fix "$FILE_PATH" 2>/dev/null || true
    fi
fi

# ============================================================
# 2. 更新文件修改时间戳（可选）
# ============================================================

if [ -n "$FILE_PATH" ] && [ -f "$FILE_PATH" ]; then
    touch "$FILE_PATH" 2>/dev/null || true
fi

# ============================================================
# 3. Git 自动暂存（可选，需谨慎使用）
# ============================================================

# 如果文件在 Git 仓库中，可以自动暂存
# 注意：这可能会导致意外的提交，默认禁用
# if [ -n "$FILE_PATH" ] && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
#     git add "$FILE_PATH" 2>/dev/null || true
#     echo "  Git staged: $FILE_PATH" >> "$LOG_FILE"
# fi

# ============================================================
# 完成
# ============================================================

echo "  ✓ Post-edit hook completed" >> "$LOG_FILE"
exit 0

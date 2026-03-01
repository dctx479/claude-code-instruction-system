#!/bin/bash
# Git Bash 路径检测工具 - Shell 包装器
# 用途：简化调用 Python 脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python "$SCRIPT_DIR/detect-git-bash.py" "$@"

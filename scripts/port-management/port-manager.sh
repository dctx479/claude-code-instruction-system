#!/bin/bash
# 端口管理工具 - Shell 包装器
# 用途：简化调用 Python 端口管理脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python "$SCRIPT_DIR/port-manager.py" "$@"

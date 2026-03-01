#!/bin/bash
# 配置文件验证工具 - Shell 包装器
# 用途：简化调用 Python 验证脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python "$SCRIPT_DIR/validate-config.py" "$@"

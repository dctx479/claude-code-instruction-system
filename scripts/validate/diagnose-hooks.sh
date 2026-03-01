#!/bin/bash
# Hooks 配置诊断工具 - Shell 包装器
# 用途：简化调用 Python 诊断脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python "$SCRIPT_DIR/diagnose-hooks.py" "$@"

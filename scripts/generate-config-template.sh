#!/bin/bash
# 配置模板生成工具 - Shell 包装器
# 用途：简化调用 Python 模板生成脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python "$SCRIPT_DIR/generate-config-template.py" "$@"

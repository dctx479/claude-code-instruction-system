#!/bin/bash
# 环境变量验证脚本
# 用途: 验证所有必需的环境变量是否已设置

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 必需的环境变量列表
REQUIRED_VARS=(
  "ANTHROPIC_AUTH_TOKEN:Claude API 认证令牌"
)

# 可选的环境变量列表（用于 MCP 服务器）
OPTIONAL_VARS=(
  "ZOTERO_API_KEY:Zotero 文献库访问密钥"
  "BRIGHTDATA_API_TOKEN:Bright Data 电商数据采集令牌"
  "TIKHUB_API_TOKEN:TikHub 社媒数据采集令牌"
)

# 验证函数
validate_var() {
  local var_name="$1"
  local var_desc="$2"
  local is_required="$3"

  if [ -z "${!var_name:-}" ]; then
    if [ "$is_required" = "true" ]; then
      echo -e "${RED}✗${NC} $var_name 未设置 - $var_desc"
      return 1
    else
      echo -e "${YELLOW}⚠${NC} $var_name 未设置 (可选) - $var_desc"
      return 0
    fi
  else
    # 显示部分值（隐藏敏感信息）
    local value="${!var_name}"
    local masked_value="${value:0:4}...${value: -4}"
    echo -e "${GREEN}✓${NC} $var_name 已设置 - $masked_value"
    return 0
  fi
}

# 主函数
main() {
  echo "========================================="
  echo "  太一元系统 - 环境变量验证"
  echo "========================================="
  echo ""

  local all_valid=true

  # 验证必需变量
  echo "必需的环境变量:"
  echo "-----------------------------------------"
  for var_info in "${REQUIRED_VARS[@]}"; do
    IFS=':' read -r var_name var_desc <<< "$var_info"
    if ! validate_var "$var_name" "$var_desc" "true"; then
      all_valid=false
    fi
  done

  echo ""

  # 验证可选变量
  echo "可选的环境变量 (用于 MCP 服务器):"
  echo "-----------------------------------------"
  for var_info in "${OPTIONAL_VARS[@]}"; do
    IFS=':' read -r var_name var_desc <<< "$var_info"
    validate_var "$var_name" "$var_desc" "false"
  done

  echo ""
  echo "========================================="

  if [ "$all_valid" = true ]; then
    echo -e "${GREEN}✓ 所有必需的环境变量已正确设置${NC}"
    echo ""
    echo "提示: 如需使用 MCP 服务器功能，请设置相应的可选环境变量"
    return 0
  else
    echo -e "${RED}✗ 部分必需的环境变量未设置${NC}"
    echo ""
    echo "请在 ~/.bashrc 或 ~/.zshrc 中添加:"
    echo ""
    for var_info in "${REQUIRED_VARS[@]}"; do
      IFS=':' read -r var_name var_desc <<< "$var_info"
      if [ -z "${!var_name:-}" ]; then
        echo "  export $var_name=\"your-value-here\""
      fi
    done
    echo ""
    echo "然后运行: source ~/.bashrc (或 source ~/.zshrc)"
    return 1
  fi
}

# 执行主函数
main "$@"

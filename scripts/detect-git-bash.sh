#!/bin/bash
# Git Bash 路径自动检测脚本
# 用途：检测系统中 Git Bash 的安装路径，支持跨平台

set -e

VERSION="1.0.0"
PLATFORM=$(uname -s)

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() { echo -e "${BLUE}ℹ ${NC}$1"; }
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }

# Windows 常见 Git Bash 路径
WINDOWS_PATHS=(
  "C:/Program Files/Git/bin/bash.exe"
  "C:/Program Files (x86)/Git/bin/bash.exe"
  "$LOCALAPPDATA/Programs/Git/bin/bash.exe"
  "$PROGRAMFILES/Git/bin/bash.exe"
  "$ProgramFiles(x86)/Git/bin/bash.exe"
)

# Linux/macOS 常见 Bash 路径
UNIX_PATHS=(
  "/bin/bash"
  "/usr/bin/bash"
  "/usr/local/bin/bash"
)

# 检测 Windows Git Bash
detect_windows_git_bash() {
  print_info "检测 Windows 环境下的 Git Bash..."

  for path in "${WINDOWS_PATHS[@]}"; do
    # 转换路径格式
    win_path=$(echo "$path" | sed 's/\//\\/g')

    if [[ -f "$path" ]]; then
      print_success "找到 Git Bash: $win_path"
      echo "$win_path"
      return 0
    fi
  done

  # 尝试使用 where 命令
  if command -v where &> /dev/null; then
    git_path=$(where git.exe 2>/dev/null | head -n1)
    if [[ -n "$git_path" ]]; then
      bash_path=$(dirname "$git_path")/bash.exe
      if [[ -f "$bash_path" ]]; then
        print_success "通过 git.exe 找到 Bash: $bash_path"
        echo "$bash_path"
        return 0
      fi
    fi
  fi

  return 1
}

# 检测 Unix Bash
detect_unix_bash() {
  print_info "检测 Unix/Linux 环境下的 Bash..."

  # 优先使用 which 命令
  if command -v which &> /dev/null; then
    bash_path=$(which bash 2>/dev/null)
    if [[ -n "$bash_path" && -x "$bash_path" ]]; then
      print_success "找到 Bash: $bash_path"
      echo "$bash_path"
      return 0
    fi
  fi

  # 检查常见路径
  for path in "${UNIX_PATHS[@]}"; do
    if [[ -x "$path" ]]; then
      print_success "找到 Bash: $path"
      echo "$path"
      return 0
    fi
  done

  return 1
}

# 生成 hooks 配置片段
generate_hooks_config() {
  local bash_path="$1"
  local escaped_path=$(echo "$bash_path" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g')

  cat <<EOF

生成的 Hooks 配置片段：

{
  "hooks": {
    "PreToolUse": [{
      "matcher": {"tools": ["Write"]},
      "hooks": [{
        "type": "command",
        "command": "\"$escaped_path\" \"./your-script.sh\"",
        "timeout": 5000
      }]
    }],
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "\"$escaped_path\" \"./your-script.sh\""
      }]
    }]
  }
}

使用方法：
1. 复制上述配置到 hooks/hooks.json
2. 将 "./your-script.sh" 替换为实际的脚本路径
3. 运行 'python -m json.tool hooks/hooks.json' 验证格式
EOF
}

# 提供安装建议
provide_installation_guide() {
  print_error "未找到 Git Bash"
  echo ""
  print_info "安装建议："

  case "$PLATFORM" in
    MINGW*|MSYS*|CYGWIN*)
      cat <<EOF

Windows 环境：
1. 下载 Git for Windows: https://gitforwindows.org/
2. 运行安装程序，选择默认选项
3. 重新运行此脚本

备选方案：
- 使用 WSL: wsl bash /mnt/c/path/to/script.sh
- 使用 PowerShell: powershell -ExecutionPolicy Bypass -File "script.ps1"
EOF
      ;;
    Linux*)
      cat <<EOF

Linux 环境：
1. Ubuntu/Debian: sudo apt-get install bash
2. CentOS/RHEL: sudo yum install bash
3. Arch: sudo pacman -S bash

通常 Bash 已预装，请检查：
- PATH 环境变量是否正确
- Bash 是否有执行权限
EOF
      ;;
    Darwin*)
      cat <<EOF

macOS 环境：
Bash 通常已预装，请检查：
- 系统版本（macOS 10.15+ 默认使用 zsh）
- 运行 'which bash' 查看路径
- 如需安装最新版：brew install bash
EOF
      ;;
  esac
}

# 主函数
main() {
  echo "Git Bash 路径检测工具 v$VERSION"
  echo "================================"
  echo ""

  local bash_path=""

  case "$PLATFORM" in
    MINGW*|MSYS*|CYGWIN*)
      bash_path=$(detect_windows_git_bash)
      ;;
    Linux*|Darwin*)
      bash_path=$(detect_unix_bash)
      ;;
    *)
      print_error "未知平台: $PLATFORM"
      exit 1
      ;;
  esac

  if [[ -n "$bash_path" ]]; then
    echo ""
    print_success "检测成功！"
    echo ""

    # 显示版本信息
    if [[ -x "$bash_path" ]]; then
      bash_version=$("$bash_path" --version | head -n1)
      print_info "版本信息: $bash_version"
    fi

    # 生成配置
    generate_hooks_config "$bash_path"

    # 写入到文件（可选）
    if [[ "$1" == "--export" ]]; then
      output_file="${2:-git-bash-path.txt}"
      echo "$bash_path" > "$output_file"
      print_success "路径已导出到: $output_file"
    fi

    exit 0
  else
    provide_installation_guide
    exit 1
  fi
}

# 运行
main "$@"

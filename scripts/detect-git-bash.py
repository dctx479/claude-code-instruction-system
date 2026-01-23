#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Bash 路径自动检测工具
用途：检测系统中 Git Bash 的安装路径，支持跨平台
版本：1.0.0
"""

import os
import sys
import io
import platform
import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict

# 设置标准输出编码为 UTF-8（修复 Windows GBK 编码问题）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ANSI 颜色代码
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

    @staticmethod
    def strip_colors():
        """在 Windows 上如果不支持 ANSI，移除颜色"""
        if platform.system() == 'Windows' and not os.environ.get('ANSICON'):
            Colors.RED = Colors.GREEN = Colors.YELLOW = Colors.BLUE = Colors.NC = ''

# Windows 常见 Git Bash 路径
WINDOWS_PATHS = [
    r"C:\Program Files\Git\bin\bash.exe",
    r"C:\Program Files (x86)\Git\bin\bash.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Git\bin\bash.exe"),
    os.path.expandvars(r"%PROGRAMFILES%\Git\bin\bash.exe"),
    os.path.expandvars(r"%ProgramFiles(x86)%\Git\bin\bash.exe"),
]

# Unix 常见 Bash 路径
UNIX_PATHS = [
    "/bin/bash",
    "/usr/bin/bash",
    "/usr/local/bin/bash",
]

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ{Colors.NC} {msg}")

def print_success(msg: str):
    print(f"{Colors.GREEN}✓{Colors.NC} {msg}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠{Colors.NC} {msg}")

def print_error(msg: str):
    print(f"{Colors.RED}✗{Colors.NC} {msg}")

def detect_windows_git_bash() -> Optional[str]:
    """检测 Windows 环境下的 Git Bash"""
    print_info("检测 Windows 环境下的 Git Bash...")

    # 检查预定义路径
    for path in WINDOWS_PATHS:
        if os.path.isfile(path):
            print_success(f"找到 Git Bash: {path}")
            return path

    # 尝试使用 where 命令查找 git.exe
    try:
        result = subprocess.run(
            ['where', 'git.exe'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            git_path = result.stdout.strip().split('\n')[0]
            bash_path = os.path.join(os.path.dirname(git_path), 'bash.exe')
            if os.path.isfile(bash_path):
                print_success(f"通过 git.exe 找到 Bash: {bash_path}")
                return bash_path
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # 检查注册表（高级检测）
    try:
        import winreg
        key_path = r"SOFTWARE\GitForWindows"
        for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
            try:
                key = winreg.OpenKey(root, key_path)
                install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                winreg.CloseKey(key)
                bash_path = os.path.join(install_path, "bin", "bash.exe")
                if os.path.isfile(bash_path):
                    print_success(f"通过注册表找到 Bash: {bash_path}")
                    return bash_path
            except FileNotFoundError:
                continue
    except ImportError:
        pass

    return None

def detect_unix_bash() -> Optional[str]:
    """检测 Unix/Linux 环境下的 Bash"""
    print_info("检测 Unix/Linux 环境下的 Bash...")

    # 优先使用 which 命令
    try:
        result = subprocess.run(
            ['which', 'bash'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            bash_path = result.stdout.strip()
            if os.path.isfile(bash_path) and os.access(bash_path, os.X_OK):
                print_success(f"找到 Bash: {bash_path}")
                return bash_path
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # 检查常见路径
    for path in UNIX_PATHS:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            print_success(f"找到 Bash: {path}")
            return path

    return None

def get_bash_version(bash_path: str) -> Optional[str]:
    """获取 Bash 版本信息"""
    try:
        result = subprocess.run(
            [bash_path, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.split('\n')[0]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None

def generate_hooks_config(bash_path: str) -> Dict:
    """生成 hooks 配置片段"""
    # 转换 Windows 路径格式为 JSON 兼容格式
    escaped_path = bash_path.replace('\\', '\\\\')

    config = {
        "hooks": {
            "PreToolUse": [{
                "matcher": {"tools": ["Write"]},
                "hooks": [{
                    "type": "command",
                    "command": f'"{escaped_path}" "./your-script.sh"',
                    "timeout": 5000
                }]
            }],
            "Stop": [{
                "hooks": [{
                    "type": "command",
                    "command": f'"{escaped_path}" "./your-script.sh"'
                }]
            }]
        }
    }

    return config

def provide_installation_guide():
    """提供安装建议"""
    print_error("未找到 Git Bash\n")
    print_info("安装建议：\n")

    system = platform.system()

    if system == "Windows":
        print("""
Windows 环境：
1. 下载 Git for Windows: https://gitforwindows.org/
2. 运行安装程序，选择默认选项
3. 重新运行此脚本

备选方案：
- 使用 WSL: wsl bash /mnt/c/path/to/script.sh
- 使用 PowerShell: powershell -ExecutionPolicy Bypass -File "script.ps1"

安装验证：
- 安装后在命令提示符运行: where git.exe
- 确认路径包含 Git\\bin 目录
""")
    elif system == "Linux":
        print("""
Linux 环境：
1. Ubuntu/Debian: sudo apt-get install bash
2. CentOS/RHEL: sudo yum install bash
3. Arch: sudo pacman -S bash
4. Fedora: sudo dnf install bash

通常 Bash 已预装，请检查：
- PATH 环境变量是否正确
- Bash 是否有执行权限: ls -l /bin/bash
- 运行: which bash
""")
    elif system == "Darwin":
        print("""
macOS 环境：
Bash 通常已预装，请检查：
- 系统版本（macOS 10.15+ 默认使用 zsh）
- 运行 'which bash' 查看路径
- 如需安装最新版：brew install bash

注意：
- macOS Catalina (10.15) 后默认 shell 是 zsh
- 但 bash 仍然可用，路径通常在 /bin/bash
""")

def export_to_file(bash_path: str, output_file: str):
    """导出路径到文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(bash_path)
        print_success(f"路径已导出到: {output_file}")
    except IOError as e:
        print_error(f"导出失败: {e}")

def export_config_to_json(config: Dict, output_file: str):
    """导出配置到 JSON 文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print_success(f"配置已导出到: {output_file}")
    except IOError as e:
        print_error(f"导出失败: {e}")

def main():
    """主函数"""
    Colors.strip_colors()

    print("Git Bash 路径检测工具 v1.0.0")
    print("=" * 40)
    print()

    # 解析命令行参数
    export_path = False
    export_config = False
    output_file = "git-bash-path.txt"
    config_file = "hooks-config-snippet.json"

    if len(sys.argv) > 1:
        if "--export" in sys.argv:
            export_path = True
            try:
                idx = sys.argv.index("--export")
                if idx + 1 < len(sys.argv):
                    output_file = sys.argv[idx + 1]
            except ValueError:
                pass

        if "--export-config" in sys.argv:
            export_config = True
            try:
                idx = sys.argv.index("--export-config")
                if idx + 1 < len(sys.argv):
                    config_file = sys.argv[idx + 1]
            except ValueError:
                pass

    # 检测平台并查找 Bash
    system = platform.system()
    bash_path = None

    if system == "Windows":
        bash_path = detect_windows_git_bash()
    elif system in ["Linux", "Darwin"]:
        bash_path = detect_unix_bash()
    else:
        print_error(f"未知平台: {system}")
        sys.exit(1)

    # 处理结果
    if bash_path:
        print()
        print_success("检测成功！\n")

        # 显示版本信息
        bash_version = get_bash_version(bash_path)
        if bash_version:
            print_info(f"版本信息: {bash_version}\n")

        # 生成配置
        config = generate_hooks_config(bash_path)

        print("生成的 Hooks 配置片段：\n")
        print(json.dumps(config, indent=2, ensure_ascii=False))

        print("\n使用方法：")
        print("1. 复制上述配置到 hooks/hooks.json")
        print("2. 将 './your-script.sh' 替换为实际的脚本路径")
        print("3. 运行 'python -m json.tool hooks/hooks.json' 验证格式")

        # 导出选项
        if export_path:
            export_to_file(bash_path, output_file)

        if export_config:
            export_config_to_json(config, config_file)

        sys.exit(0)
    else:
        provide_installation_guide()
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(130)
    except Exception as e:
        print_error(f"发生错误: {e}")
        sys.exit(1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置模板生成工具
版本：1.0.0
用途：交互式生成 hooks 和 settings 配置模板
"""

import os
import sys
import io
import json
import platform
from typing import Dict, List, Optional

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ===================== 颜色和输出工具 =====================

class Colors:
    """ANSI 颜色代码"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def print_header(text: str):
    print(f"\n{Colors.CYAN}{'=' * 60}{Colors.NC}")
    print(f"{Colors.CYAN}{text}{Colors.NC}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.NC}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.NC}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.NC}")

# ===================== 模板定义 =====================

class TemplateGenerator:
    """配置模板生成器"""

    def __init__(self):
        self.platform = platform.system()
        self.bash_path = self._detect_bash_path()

    def _detect_bash_path(self) -> str:
        """检测 Git Bash 路径"""
        if self.platform == 'Windows':
            # 常见路径
            paths = [
                r"C:\Program Files\Git\bin\bash.exe",
                r"C:\Program Files (x86)\Git\bin\bash.exe",
                r"I:\APP\Git\bin\bash.exe"
            ]
            for path in paths:
                if os.path.isfile(path):
                    return path
            return r"C:\Program Files\Git\bin\bash.exe"  # 默认
        else:
            return "/bin/bash"

    def _escape_path(self, path: str) -> str:
        """转义路径"""
        if self.platform == 'Windows':
            return path.replace('\\', '\\\\')
        return path

    # ===================== Hooks 模板 =====================

    def template_pre_tool_use(self, tools: List[str], script_path: str, timeout: int = 5000) -> Dict:
        """生成 PreToolUse 模板"""
        bash_path = self._escape_path(self.bash_path)
        return {
            "matcher": {"tools": tools},
            "hooks": [
                {
                    "type": "command",
                    "command": f'"{bash_path}" "{script_path}"',
                    "timeout": timeout
                }
            ]
        }

    def template_post_tool_use(self, tools: List[str], script_path: str, timeout: int = 3000) -> Dict:
        """生成 PostToolUse 模板"""
        bash_path = self._escape_path(self.bash_path)
        return {
            "matcher": {"tools": tools},
            "hooks": [
                {
                    "type": "command",
                    "command": f'"{bash_path}" "{script_path}"',
                    "timeout": timeout
                }
            ]
        }

    def template_stop(self, script_path: str, timeout: int = 10000) -> Dict:
        """生成 Stop 模板"""
        bash_path = self._escape_path(self.bash_path)
        return {
            "hooks": [
                {
                    "type": "command",
                    "command": f'"{bash_path}" "{script_path}"',
                    "timeout": timeout
                }
            ]
        }

    def template_user_prompt_submit(self, script_path: str, timeout: int = 2000) -> Dict:
        """生成 UserPromptSubmit 模板"""
        bash_path = self._escape_path(self.bash_path)
        return {
            "hooks": [
                {
                    "type": "command",
                    "command": f'"{bash_path}" "{script_path}"',
                    "timeout": timeout
                }
            ]
        }

    # ===================== 预设场景模板 =====================

    def preset_code_quality(self) -> Dict:
        """代码质量检查场景"""
        return {
            "hooks": {
                "PreToolUse": [
                    self.template_pre_tool_use(
                        ["Write", "Edit"],
                        "./hooks/validate-code.sh",
                        5000
                    )
                ],
                "PostToolUse": [
                    self.template_post_tool_use(
                        ["Write", "Edit"],
                        "./hooks/format-code.sh",
                        3000
                    )
                ]
            }
        }

    def preset_git_workflow(self) -> Dict:
        """Git 工作流场景"""
        return {
            "hooks": {
                "PostToolUse": [
                    self.template_post_tool_use(
                        ["Write", "Edit"],
                        "./hooks/git-auto-commit.sh",
                        5000
                    )
                ],
                "Stop": [
                    self.template_stop(
                        "./hooks/git-push.sh",
                        10000
                    )
                ]
            }
        }

    def preset_testing(self) -> Dict:
        """测试场景"""
        return {
            "hooks": {
                "PostToolUse": [
                    self.template_post_tool_use(
                        ["Write"],
                        "./hooks/run-tests.sh",
                        30000
                    )
                ]
            }
        }

    def preset_documentation(self) -> Dict:
        """文档生成场景"""
        return {
            "hooks": {
                "Stop": [
                    self.template_stop(
                        "./hooks/generate-docs.sh",
                        15000
                    )
                ]
            }
        }

    def preset_notification(self) -> Dict:
        """通知场景"""
        return {
            "hooks": {
                "Stop": [
                    self.template_stop(
                        "./hooks/notify.sh",
                        2000
                    )
                ],
                "UserPromptSubmit": [
                    self.template_user_prompt_submit(
                        "./hooks/log-prompt.sh",
                        1000
                    )
                ]
            }
        }

    # ===================== Settings 模板 =====================

    def template_settings_basic(self) -> Dict:
        """基本 Settings 模板"""
        return {
            "model": {
                "default": "sonnet"
            },
            "context": {
                "maxTokens": 200000
            },
            "permissions": {
                "allow": ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
            }
        }

    def template_settings_research(self) -> Dict:
        """科研场景 Settings 模板"""
        return {
            "model": {
                "default": "sonnet"
            },
            "context": {
                "maxTokens": 200000
            },
            "agents": {
                "parallel": 5
            },
            "skills": {
                "autoActivate": True
            },
            "mcpServers": {
                "zotero": {
                    "enabled": True
                }
            }
        }

    def template_settings_dev(self) -> Dict:
        """开发场景 Settings 模板"""
        return {
            "model": {
                "default": "sonnet",
                "overrides": {
                    "spec-writer": "opus",
                    "qa-reviewer": "sonnet"
                }
            },
            "agents": {
                "parallel": 3
            },
            "qa": {
                "autoFix": True,
                "threshold": 80
            }
        }

    # ===================== 交互式生成 =====================

    def interactive_hooks(self) -> Dict:
        """交互式生成 Hooks 配置"""
        print_header("交互式 Hooks 配置生成")

        print("请选择场景模板:")
        print("1. 代码质量检查 (PreToolUse + PostToolUse)")
        print("2. Git 工作流 (PostToolUse + Stop)")
        print("3. 自动测试 (PostToolUse)")
        print("4. 文档生成 (Stop)")
        print("5. 通知提醒 (Stop + UserPromptSubmit)")
        print("6. 自定义")

        choice = input("\n选择 (1-6): ").strip()

        if choice == '1':
            return self.preset_code_quality()
        elif choice == '2':
            return self.preset_git_workflow()
        elif choice == '3':
            return self.preset_testing()
        elif choice == '4':
            return self.preset_documentation()
        elif choice == '5':
            return self.preset_notification()
        elif choice == '6':
            return self._custom_hooks()
        else:
            print_warning("无效选择，使用代码质量检查模板")
            return self.preset_code_quality()

    def _custom_hooks(self) -> Dict:
        """自定义 Hooks 配置"""
        config = {"hooks": {}}

        print("\n添加 PreToolUse Hook? (y/n): ", end='')
        if input().strip().lower() == 'y':
            tools = input("工具列表 (逗号分隔，如 Write,Edit): ").strip().split(',')
            script = input("脚本路径 (如 ./hooks/validate.sh): ").strip()
            timeout = int(input("超时时间 (ms，建议 5000): ").strip() or "5000")
            config["hooks"]["PreToolUse"] = [
                self.template_pre_tool_use([t.strip() for t in tools], script, timeout)
            ]

        print("\n添加 PostToolUse Hook? (y/n): ", end='')
        if input().strip().lower() == 'y':
            tools = input("工具列表 (逗号分隔): ").strip().split(',')
            script = input("脚本路径: ").strip()
            timeout = int(input("超时时间 (ms，建议 3000): ").strip() or "3000")
            config["hooks"]["PostToolUse"] = [
                self.template_post_tool_use([t.strip() for t in tools], script, timeout)
            ]

        print("\n添加 Stop Hook? (y/n): ", end='')
        if input().strip().lower() == 'y':
            script = input("脚本路径: ").strip()
            timeout = int(input("超时时间 (ms，建议 10000): ").strip() or "10000")
            config["hooks"]["Stop"] = [
                self.template_stop(script, timeout)
            ]

        return config

    def interactive_settings(self) -> Dict:
        """交互式生成 Settings 配置"""
        print_header("交互式 Settings 配置生成")

        print("请选择场景模板:")
        print("1. 基本配置")
        print("2. 科研场景")
        print("3. 开发场景")

        choice = input("\n选择 (1-3): ").strip()

        if choice == '1':
            return self.template_settings_basic()
        elif choice == '2':
            return self.template_settings_research()
        elif choice == '3':
            return self.template_settings_dev()
        else:
            print_warning("无效选择，使用基本配置")
            return self.template_settings_basic()

    # ===================== 导出 =====================

    def export_config(self, config: Dict, output_path: str):
        """导出配置到文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print_success(f"配置已导出到: {output_path}")

        # 显示预览
        print("\n配置预览:")
        print(json.dumps(config, indent=2, ensure_ascii=False))

# ===================== 主函数 =====================

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='配置模板生成工具 v1.0.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python generate-config-template.py hooks --output hooks.json
  python generate-config-template.py settings --output settings.json
  python generate-config-template.py hooks --preset code-quality
        """
    )
    parser.add_argument('type', choices=['hooks', 'settings'], help='配置类型')
    parser.add_argument('--output', '-o', default=None, help='输出文件路径')
    parser.add_argument('--preset', '-p', help='预设模板 (code-quality/git-workflow/testing/etc.)')
    args = parser.parse_args()

    generator = TemplateGenerator()

    # 生成配置
    if args.type == 'hooks':
        if args.preset:
            preset_map = {
                'code-quality': generator.preset_code_quality,
                'git-workflow': generator.preset_git_workflow,
                'testing': generator.preset_testing,
                'documentation': generator.preset_documentation,
                'notification': generator.preset_notification
            }
            if args.preset in preset_map:
                config = preset_map[args.preset]()
            else:
                print_warning(f"未知预设: {args.preset}，使用交互式生成")
                config = generator.interactive_hooks()
        else:
            config = generator.interactive_hooks()
    else:  # settings
        config = generator.interactive_settings()

    # 导出
    if args.output:
        generator.export_config(config, args.output)
    else:
        # 默认输出到标准输出
        print("\n生成的配置:")
        print(json.dumps(config, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}✗ 发生错误: {e}{Colors.NC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

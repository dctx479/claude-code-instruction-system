#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hooks 错误诊断和修复建议工具
用途：分析 hooks 配置错误，提供详细的诊断和修复建议
版本：1.0.0
"""

import os
import sys
import io
import json
import subprocess
import platform
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 颜色定义
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.CYAN}{'=' * 60}{Colors.NC}")
    print(f"{Colors.CYAN}{text}{Colors.NC}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.NC}\n")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.NC}")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.NC}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.NC}")

def print_fix(text: str):
    print(f"{Colors.MAGENTA}🔧 {text}{Colors.NC}")

class HooksDiagnostic:
    """Hooks 配置诊断器"""

    def __init__(self, hooks_file: str = "hooks/hooks.json"):
        self.hooks_file = hooks_file
        self.errors = []
        self.warnings = []
        self.fixes = []
        self.config = None

    def load_config(self) -> bool:
        """加载配置文件"""
        if not os.path.exists(self.hooks_file):
            self.errors.append({
                'type': 'file_not_found',
                'message': f'配置文件不存在: {self.hooks_file}',
                'fix': f'创建配置文件: touch {self.hooks_file}'
            })
            return False

        try:
            with open(self.hooks_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            return True
        except json.JSONDecodeError as e:
            self.errors.append({
                'type': 'json_parse_error',
                'message': f'JSON 解析错误: {e}',
                'location': f'行 {e.lineno}, 列 {e.colno}',
                'fix': f'运行 python -m json.tool {self.hooks_file} 查看详细错误'
            })
            return False
        except Exception as e:
            self.errors.append({
                'type': 'load_error',
                'message': f'加载配置失败: {e}',
                'fix': '检查文件权限和编码'
            })
            return False

    def check_hooks_structure(self) -> None:
        """检查 hooks 基本结构"""
        if not isinstance(self.config, dict):
            self.errors.append({
                'type': 'invalid_structure',
                'message': '配置必须是 JSON 对象',
                'fix': '配置文件顶层应该是 {...}'
            })
            return

        if 'hooks' not in self.config:
            self.errors.append({
                'type': 'missing_hooks',
                'message': '缺少 "hooks" 字段',
                'fix': '添加: {"hooks": {...}}'
            })
            return

        if not isinstance(self.config['hooks'], dict):
            self.errors.append({
                'type': 'invalid_hooks_type',
                'message': '"hooks" 必须是对象',
                'fix': '修改为: {"hooks": {...}}'
            })

    def check_matcher_format(self) -> None:
        """检查 matcher 格式"""
        if not self.config or 'hooks' not in self.config:
            return

        hooks = self.config['hooks']
        tool_events = ['PreToolUse', 'PostToolUse']

        for event_name, event_hooks in hooks.items():
            if not isinstance(event_hooks, list):
                continue

            for idx, hook_config in enumerate(event_hooks):
                if not isinstance(hook_config, dict):
                    continue

                # 检查 PreToolUse/PostToolUse 的 matcher
                if event_name in tool_events:
                    if 'matcher' not in hook_config:
                        self.errors.append({
                            'type': 'missing_matcher',
                            'message': f'{event_name}[{idx}] 缺少 matcher',
                            'location': f'hooks.{event_name}[{idx}]',
                            'fix': f'添加: "matcher": "ToolName"'
                        })
                    elif isinstance(hook_config['matcher'], str):
                        # String matcher is correct format
                        pass
                    elif isinstance(hook_config['matcher'], dict):
                        # Object matcher is incorrect format
                        self.errors.append({
                            'type': 'invalid_matcher_format',
                            'message': f'{event_name}[{idx}] matcher 格式错误（对象格式）',
                            'location': f'hooks.{event_name}[{idx}].matcher',
                            'current': f'{hook_config["matcher"]}',
                            'fix': f'修改为字符串格式: "{hook_config["matcher"].get("tools", ["Tool"])[0] if "tools" in hook_config["matcher"] else "Tool"}"'
                        })

                # 检查其他事件不应该有 matcher
                else:
                    if 'matcher' in hook_config:
                        self.warnings.append({
                            'type': 'unnecessary_matcher',
                            'message': f'{event_name}[{idx}] 不需要 matcher',
                            'location': f'hooks.{event_name}[{idx}].matcher',
                            'fix': f'移除 matcher 字段'
                        })

    def check_hooks_array(self) -> None:
        """检查 hooks 数组结构"""
        if not self.config or 'hooks' not in self.config:
            return

        hooks = self.config['hooks']

        for event_name, event_hooks in hooks.items():
            if not isinstance(event_hooks, list):
                continue

            for idx, hook_config in enumerate(event_hooks):
                if not isinstance(hook_config, dict):
                    continue

                # 检查是否有 hooks 数组
                if 'hooks' not in hook_config:
                    # 检查是否是旧格式（直接有 type 和 command）
                    if 'type' in hook_config and 'command' in hook_config:
                        self.errors.append({
                            'type': 'missing_hooks_array',
                            'message': f'{event_name}[{idx}] 缺少 hooks 数组包裹',
                            'location': f'hooks.{event_name}[{idx}]',
                            'fix': f'包裹在 hooks 数组中: {{"hooks": [{{"type": "...", "command": "..."}}]}}'
                        })

    def check_command_paths(self) -> None:
        """检查命令路径和跨平台兼容性"""
        if not self.config or 'hooks' not in self.config:
            return

        system = platform.system()
        hooks = self.config['hooks']

        for event_name, event_hooks in hooks.items():
            if not isinstance(event_hooks, list):
                continue

            for idx, hook_config in enumerate(event_hooks):
                if 'hooks' not in hook_config or not isinstance(hook_config['hooks'], list):
                    continue

                for hidx, hook in enumerate(hook_config['hooks']):
                    if 'command' not in hook:
                        continue

                    command = hook['command']

                    # Windows 平台检查
                    if system == 'Windows':
                        # 检查是否使用相对路径的 .sh 脚本
                        if command.startswith('./') and command.endswith('.sh'):
                            self.errors.append({
                                'type': 'windows_incompatible_path',
                                'message': f'{event_name}[{idx}].hooks[{hidx}] 使用相对路径脚本',
                                'location': f'hooks.{event_name}[{idx}].hooks[{hidx}].command',
                                'current': command,
                                'fix': f'使用 Git Bash: "\\"C:\\\\Program Files\\\\Git\\\\bin\\\\bash.exe\\" \\"{command}\\""'
                            })

                        # 检查 bash 命令
                        if command.startswith('bash '):
                            self.warnings.append({
                                'type': 'bash_without_path',
                                'message': f'{event_name}[{idx}].hooks[{hidx}] 直接使用 bash 命令',
                                'location': f'hooks.{event_name}[{idx}].hooks[{hidx}].command',
                                'fix': '建议使用完整路径: "C:\\\\Program Files\\\\Git\\\\bin\\\\bash.exe"'
                            })

    def check_script_files(self) -> None:
        """检查脚本文件是否存在"""
        if not self.config or 'hooks' not in self.config:
            return

        hooks = self.config['hooks']
        checked_scripts = set()

        for event_name, event_hooks in hooks.items():
            if not isinstance(event_hooks, list):
                continue

            for hook_config in event_hooks:
                if 'hooks' not in hook_config or not isinstance(hook_config['hooks'], list):
                    continue

                for hook in hook_config['hooks']:
                    if 'command' not in hook:
                        continue

                    command = hook['command']

                    # 提取脚本路径
                    if '.sh' in command or '.ps1' in command:
                        parts = command.split('"')
                        for part in parts:
                            if ('.sh' in part or '.ps1' in part) and not part.endswith('.exe'):
                                script_path = part.strip()
                                if script_path.startswith('./'):
                                    script_path = script_path[2:]

                                if script_path not in checked_scripts:
                                    checked_scripts.add(script_path)
                                    if not os.path.exists(script_path):
                                        self.warnings.append({
                                            'type': 'script_not_found',
                                            'message': f'脚本文件不存在: {script_path}',
                                            'fix': f'创建脚本或检查路径是否正确'
                                        })

    def generate_fix_config(self) -> Optional[Dict]:
        """生成修复后的配置"""
        if not self.config or not self.errors:
            return None

        fixed_config = json.loads(json.dumps(self.config))  # Deep copy

        # 修复 matcher 格式
        if 'hooks' in fixed_config:
            tool_events = ['PreToolUse', 'PostToolUse']
            for event_name in tool_events:
                if event_name not in fixed_config['hooks']:
                    continue

                for hook_config in fixed_config['hooks'][event_name]:
                    if 'matcher' in hook_config and isinstance(hook_config['matcher'], dict):
                        # Convert object format to string format
                        if 'tools' in hook_config['matcher'] and hook_config['matcher']['tools']:
                            hook_config['matcher'] = hook_config['matcher']['tools'][0]

        return fixed_config

    def run_diagnosis(self) -> bool:
        """运行完整诊断"""
        print_header("开始 Hooks 配置诊断")

        # 加载配置
        print_info(f"加载配置文件: {self.hooks_file}")
        if not self.load_config():
            return False

        print_success("配置文件加载成功")

        # 运行检查
        print_info("检查 Hooks 结构...")
        self.check_hooks_structure()

        print_info("检查 Matcher 格式...")
        self.check_matcher_format()

        print_info("检查 Hooks 数组结构...")
        self.check_hooks_array()

        print_info("检查命令路径兼容性...")
        self.check_command_paths()

        print_info("检查脚本文件...")
        self.check_script_files()

        return True

    def print_report(self) -> None:
        """打印诊断报告"""
        print_header("诊断报告")

        # 错误
        if self.errors:
            print(f"\n{Colors.RED}{'='*60}{Colors.NC}")
            print(f"{Colors.RED}发现 {len(self.errors)} 个错误:{Colors.NC}")
            print(f"{Colors.RED}{'='*60}{Colors.NC}\n")

            for idx, error in enumerate(self.errors, 1):
                print(f"{Colors.RED}[{idx}] {error['type'].upper()}{Colors.NC}")
                print(f"  消息: {error['message']}")
                if 'location' in error:
                    print(f"  位置: {error['location']}")
                if 'current' in error:
                    print(f"  当前值: {error['current']}")
                print_fix(f"  修复方案: {error['fix']}")
                print()

        # 警告
        if self.warnings:
            print(f"\n{Colors.YELLOW}{'='*60}{Colors.NC}")
            print(f"{Colors.YELLOW}发现 {len(self.warnings)} 个警告:{Colors.NC}")
            print(f"{Colors.YELLOW}{'='*60}{Colors.NC}\n")

            for idx, warning in enumerate(self.warnings, 1):
                print(f"{Colors.YELLOW}[{idx}] {warning['type'].upper()}{Colors.NC}")
                print(f"  消息: {warning['message']}")
                if 'location' in warning:
                    print(f"  位置: {warning['location']}")
                print_fix(f"  建议: {warning['fix']}")
                print()

        # 总结
        if not self.errors and not self.warnings:
            print_success("✨ 配置完美！未发现任何问题。")
        else:
            error_count = len(self.errors)
            warning_count = len(self.warnings)
            print(f"\n{'='*60}")
            print(f"总计: {Colors.RED}{error_count} 个错误{Colors.NC}, {Colors.YELLOW}{warning_count} 个警告{Colors.NC}")
            print(f"{'='*60}\n")

    def export_fixed_config(self, output_file: str) -> None:
        """导出修复后的配置"""
        fixed_config = self.generate_fix_config()
        if fixed_config:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(fixed_config, f, indent=2, ensure_ascii=False)
            print_success(f"修复后的配置已导出到: {output_file}")

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='Hooks 配置诊断工具')
    parser.add_argument('--config', default='hooks/hooks.json', help='配置文件路径')
    parser.add_argument('--export-fix', help='导出修复后的配置到指定文件')
    args = parser.parse_args()

    diagnostic = HooksDiagnostic(args.config)

    if not diagnostic.run_diagnosis():
        print_error("诊断失败")
        sys.exit(1)

    diagnostic.print_report()

    if args.export_fix and diagnostic.errors:
        diagnostic.export_fixed_config(args.export_fix)

    # 返回状态码
    if diagnostic.errors:
        sys.exit(1)
    elif diagnostic.warnings:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(130)
    except Exception as e:
        print_error(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件验证工具 - 完整版
整合 hooks、settings 和其他配置文件的验证
版本：2.0.0
"""

import os
import sys
import io
import json
import argparse
import platform
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime

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

# ===================== Hooks 诊断器 =====================

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
                        tool_name = hook_config['matcher'].get('tools', ['Tool'])[0] if 'tools' in hook_config['matcher'] else 'Tool'
                        self.errors.append({
                            'type': 'invalid_matcher_format',
                            'message': f'{event_name}[{idx}] matcher 格式错误（对象格式）',
                            'location': f'hooks.{event_name}[{idx}].matcher',
                            'current': f'{hook_config["matcher"]}',
                            'fix': f'修改为字符串格式: "{tool_name}"'
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
        print_info(f"加载配置文件: {self.hooks_file}")
        if not self.load_config():
            return False

        print_success("配置文件加载成功")

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

# ===================== 配置验证器 =====================

class ConfigValidator:
    """配置文件验证器"""

    def __init__(self):
        self.results = []
        self.total_errors = 0
        self.total_warnings = 0

    def validate_json_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """验证 JSON 文件格式"""
        errors = []

        if not os.path.exists(file_path):
            errors.append(f"文件不存在: {file_path}")
            return False, errors

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True, []
        except json.JSONDecodeError as e:
            errors.append(f"JSON 解析错误: 行 {e.lineno}, 列 {e.colno}: {e.msg}")
            return False, errors
        except Exception as e:
            errors.append(f"加载失败: {e}")
            return False, errors

    def validate_hooks(self, file_path: str = "hooks/hooks.json") -> Dict:
        """验证 Hooks 配置"""
        print_header(f"验证 Hooks 配置: {file_path}")

        diagnostic = HooksDiagnostic(file_path)
        if not diagnostic.run_diagnosis():
            return {
                'file': file_path,
                'type': 'hooks',
                'success': False,
                'errors': len(diagnostic.errors),
                'warnings': len(diagnostic.warnings),
                'details': diagnostic.errors + diagnostic.warnings
            }

        diagnostic.print_report()

        return {
            'file': file_path,
            'type': 'hooks',
            'success': len(diagnostic.errors) == 0,
            'errors': len(diagnostic.errors),
            'warnings': len(diagnostic.warnings),
            'details': diagnostic.errors + diagnostic.warnings,
            'diagnostic': diagnostic  # 保存诊断器实例用于修复
        }

    def validate_settings(self, file_path: str = "config/settings.json") -> Dict:
        """验证 Settings 配置"""
        print_header(f"验证 Settings 配置: {file_path}")

        result = {
            'file': file_path,
            'type': 'settings',
            'success': True,
            'errors': 0,
            'warnings': 0,
            'details': []
        }

        # 检查 JSON 格式
        success, errors = self.validate_json_file(file_path)
        if not success:
            result['success'] = False
            result['errors'] = len(errors)
            result['details'] = [{'type': 'json_error', 'message': msg} for msg in errors]
            print_error("JSON 格式验证失败")
            for error in errors:
                print(f"  {error}")
            return result

        print_success("JSON 格式正确")

        # 加载配置
        with open(file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 验证权限配置
        if 'permissions' in config:
            perms = config['permissions']
            if 'allow' not in perms:
                result['warnings'] += 1
                result['details'].append({
                    'type': 'missing_field',
                    'message': 'permissions.allow 字段缺失',
                    'fix': '添加 allow 字段定义允许的工具'
                })

        # 验证模型配置
        if 'model' in config:
            model = config['model']
            if 'default' in model:
                valid_models = ['sonnet', 'opus', 'haiku']
                if model['default'] not in valid_models:
                    result['warnings'] += 1
                    result['details'].append({
                        'type': 'invalid_model',
                        'message': f"模型 '{model['default']}' 无效",
                        'fix': f"应为: {valid_models}"
                    })

        # 验证上下文配置
        if 'context' in config:
            context = config['context']
            if 'maxTokens' in context:
                max_tokens = context['maxTokens']
                if max_tokens < 10000 or max_tokens > 500000:
                    result['warnings'] += 1
                    result['details'].append({
                        'type': 'invalid_max_tokens',
                        'message': f"maxTokens ({max_tokens}) 超出建议范围",
                        'fix': "建议范围: 10000-500000"
                    })

        # 验证 Agent 配置
        if 'agents' in config:
            agents = config['agents']
            if 'parallel' in agents:
                parallel = agents['parallel']
                if parallel < 1 or parallel > 10:
                    result['warnings'] += 1
                    result['details'].append({
                        'type': 'invalid_parallel',
                        'message': f"agents.parallel ({parallel}) 超出建议范围",
                        'fix': "建议范围: 1-10"
                    })

        if result['details']:
            print_warning(f"发现 {len(result['details'])} 个警告")
            for detail in result['details']:
                print(f"  - {detail['message']}")
                if 'fix' in detail:
                    print_fix(f"    修复: {detail['fix']}")
        else:
            print_success("配置验证通过")

        return result

    def validate_all(self, target: str = None) -> List[Dict]:
        """验证所有配置文件或指定类型"""
        print_header("配置文件验证工具 v2.0.0")

        results = []

        # 根据目标验证
        if target is None or target == 'hooks':
            if os.path.exists("hooks/hooks.json"):
                results.append(self.validate_hooks())

        if target is None or target == 'settings':
            if os.path.exists("config/settings.json"):
                results.append(self.validate_settings())

        if target is None:
            # 验证其他 JSON 配置文件
            other_configs = [
                'config/keywords.json',
                'config/mcp-servers.json',
                'config/hud-config.json'
            ]

            for config_file in other_configs:
                if os.path.exists(config_file):
                    print_header(f"验证配置: {config_file}")
                    success, errors = self.validate_json_file(config_file)

                    if success:
                        print_success("JSON 格式正确")
                        results.append({
                            'file': config_file,
                            'type': 'json',
                            'success': True,
                            'errors': 0,
                            'warnings': 0,
                            'details': []
                        })
                    else:
                        print_error("JSON 格式验证失败")
                        for error in errors:
                            print(f"  {error}")
                        results.append({
                            'file': config_file,
                            'type': 'json',
                            'success': False,
                            'errors': len(errors),
                            'warnings': 0,
                            'details': [{'type': 'json_error', 'message': msg} for msg in errors]
                        })

        return results

    def print_summary(self, results: List[Dict]) -> None:
        """打印验证总结"""
        print_header("验证总结")

        total_files = len(results)
        passed_files = sum(1 for r in results if r['success'])
        total_errors = sum(r['errors'] for r in results)
        total_warnings = sum(r['warnings'] for r in results)

        print(f"总文件数: {total_files}")
        print(f"通过: {Colors.GREEN}{passed_files}{Colors.NC}")
        print(f"失败: {Colors.RED}{total_files - passed_files}{Colors.NC}")
        print(f"错误: {Colors.RED}{total_errors}{Colors.NC}")
        print(f"警告: {Colors.YELLOW}{total_warnings}{Colors.NC}")

        if total_errors == 0 and total_warnings == 0:
            print(f"\n{Colors.GREEN}✨ 所有配置文件都正确！{Colors.NC}")
        elif total_errors > 0:
            print(f"\n{Colors.RED}❌ 发现严重错误，请修复后再使用{Colors.NC}")
        else:
            print(f"\n{Colors.YELLOW}⚠️ 发现警告，建议修复{Colors.NC}")

    def auto_fix(self, results: List[Dict]) -> None:
        """自动修复配置问题"""
        print_header("自动修复配置问题")

        fixed_count = 0

        for result in results:
            if result['type'] == 'hooks' and result['errors'] > 0:
                if 'diagnostic' in result:
                    diagnostic = result['diagnostic']
                    fixed_config = diagnostic.generate_fix_config()

                    if fixed_config:
                        output_file = f"{result['file']}.fixed"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump(fixed_config, f, indent=2, ensure_ascii=False)

                        print_success(f"已生成修复后的配置: {output_file}")
                        print_info("应用修复:")
                        print(f"  cp {result['file']} {result['file']}.backup")
                        print(f"  mv {output_file} {result['file']}")
                        fixed_count += 1

        if fixed_count == 0:
            print_warning("没有可以自动修复的问题")
        else:
            print_success(f"已生成 {fixed_count} 个修复后的配置文件")

    def export_report(self, results: List[Dict], output_file: str) -> None:
        """导出验证报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 配置验证报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 验证结果\n\n")
            f.write("| 文件 | 类型 | 状态 | 错误 | 警告 |\n")
            f.write("|------|------|------|------|------|\n")

            for result in results:
                status = "✅ 通过" if result['success'] else "❌ 失败"
                f.write(f"| {result['file']} | {result['type']} | {status} | {result['errors']} | {result['warnings']} |\n")

            f.write("\n## 详细信息\n\n")

            for result in results:
                if result['details']:
                    f.write(f"### {result['file']}\n\n")
                    for detail in result['details']:
                        f.write(f"- **{detail.get('type', 'N/A')}**: {detail.get('message', 'N/A')}\n")
                        if 'fix' in detail:
                            f.write(f"  - 修复: {detail['fix']}\n")
                    f.write("\n")

        print_success(f"报告已导出到: {output_file}")

# ===================== 主函数 =====================

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='配置文件验证工具 v2.0.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python validate-config.py                    # 验证所有配置
  python validate-config.py hooks              # 仅验证 hooks
  python validate-config.py --fix              # 自动修复问题
  python validate-config.py --export report.md # 导出报告
        """
    )
    parser.add_argument('target', nargs='?', choices=['hooks', 'settings', 'all'], default=None,
                        help='验证目标 (hooks/settings/all)')
    parser.add_argument('--fix', action='store_true', help='自动修复问题')
    parser.add_argument('--export-report', metavar='FILE', help='导出验证报告')
    args = parser.parse_args()

    validator = ConfigValidator()

    # 运行验证
    target = None if args.target == 'all' else args.target
    results = validator.validate_all(target)

    # 打印总结
    validator.print_summary(results)

    # 自动修复（如果请求）
    if args.fix:
        validator.auto_fix(results)

    # 导出报告
    if args.export_report:
        validator.export_report(results, args.export_report)

    # 返回状态码
    total_errors = sum(r['errors'] for r in results)
    total_warnings = sum(r['warnings'] for r in results)

    if total_errors > 0:
        sys.exit(1)
    elif total_warnings > 0:
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

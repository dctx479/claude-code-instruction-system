#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件验证工具
整合 hooks、settings 和其他配置文件的验证
版本：1.0.0
"""

import os
import sys
import io
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 导入诊断模块（使用相对路径）
try:
    # 尝试导入本地模块
    import importlib.util
    spec = importlib.util.spec_from_file_location("diagnose_hooks", os.path.join(os.path.dirname(__file__), "diagnose-hooks.py"))
    diagnose_hooks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(diagnose_hooks)

    HooksDiagnostic = diagnose_hooks.HooksDiagnostic
    Colors = diagnose_hooks.Colors
    print_header = diagnose_hooks.print_header
    print_success = diagnose_hooks.print_success
    print_error = diagnose_hooks.print_error
    print_warning = diagnose_hooks.print_warning
    print_info = diagnose_hooks.print_info
except Exception as e:
    print(f"警告: 无法导入 diagnose-hooks 模块: {e}")
    print("将使用基本验证功能")

    # 提供基本的替代实现
    class Colors:
        RED = '\033[0;31m'
        GREEN = '\033[0;32m'
        YELLOW = '\033[1;33m'
        BLUE = '\033[0;34m'
        CYAN = '\033[0;36m'
        NC = '\033[0m'

    def print_header(text): print(f"\n{Colors.CYAN}{'='*60}\n{text}\n{'='*60}{Colors.NC}\n")
    def print_error(text): print(f"{Colors.RED}✗ {text}{Colors.NC}")
    def print_success(text): print(f"{Colors.GREEN}✓ {text}{Colors.NC}")
    def print_warning(text): print(f"{Colors.YELLOW}⚠ {text}{Colors.NC}")
    def print_info(text): print(f"{Colors.BLUE}ℹ {text}{Colors.NC}")

    HooksDiagnostic = None

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

        if HooksDiagnostic is None:
            # 使用基本验证
            print_warning("Hooks 详细诊断不可用，使用基本验证")
            success, errors = self.validate_json_file(file_path)

            return {
                'file': file_path,
                'type': 'hooks',
                'success': success,
                'errors': len(errors) if not success else 0,
                'warnings': 0,
                'details': [{'type': 'json_error', 'message': msg} for msg in errors] if not success else []
            }

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
            'details': diagnostic.errors + diagnostic.warnings
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
                    'message': 'permissions.allow 字段缺失'
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
                        'message': f"模型 '{model['default']}' 无效，应为: {valid_models}"
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
                        'message': f"maxTokens ({max_tokens}) 超出建议范围 (10000-500000)"
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
                        'message': f"agents.parallel ({parallel}) 超出建议范围 (1-10)"
                    })

        if result['details']:
            print_warning(f"发现 {len(result['details'])} 个警告")
        else:
            print_success("配置验证通过")

        return result

    def validate_all(self, target: str = None) -> List[Dict]:
        """验证所有配置文件或指定类型"""
        print_header("配置文件验证工具 v1.0.0")

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

    def export_report(self, results: List[Dict], output_file: str) -> None:
        """导出验证报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 配置验证报告\n\n")
            f.write(f"**生成时间**: {os.popen('date').read().strip()}\n\n")

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

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='配置文件验证工具')
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

    # 导出报告
    if args.export_report:
        validator.export_report(results, args.export_report)

    # 自动修复（如果请求）
    if args.fix:
        print_info("自动修复功能开发中...")

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

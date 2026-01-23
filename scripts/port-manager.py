#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局端口管理工具
版本：1.0.0
用途：管理多项目环境下的端口分配，避免冲突
"""

import os
import sys
import io
import json
import socket
import subprocess
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

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
    NC = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.CYAN}{'=' * 70}{Colors.NC}")
    print(f"{Colors.CYAN}{text}{Colors.NC}")
    print(f"{Colors.CYAN}{'=' * 70}{Colors.NC}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.NC}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.NC}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.NC}")

# ===================== 常见服务端口范围 =====================

DEFAULT_PORT_RANGES = {
    'mysql': (3306, 3316),
    'postgresql': (5432, 5442),
    'redis': (6379, 6389),
    'mongodb': (27017, 27027),
    'web': (8000, 8100),
    'api': (9000, 9100),
    'websocket': (9500, 9600),
    'custom': (10000, 20000)
}

# ===================== 端口管理器 =====================

class PortManager:
    """端口管理器"""

    def __init__(self, registry_file: str = "config/port-registry.json"):
        self.registry_file = registry_file
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict:
        """加载端口注册表"""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print_warning(f"加载注册表失败: {e}")
                return self._create_empty_registry()
        else:
            return self._create_empty_registry()

    def _create_empty_registry(self) -> Dict:
        """创建空注册表"""
        return {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "ports": {},
            "projects": {},
            "history": []
        }

    def _save_registry(self):
        """保存注册表"""
        self.registry["last_updated"] = datetime.now().isoformat()

        # 确保目录存在
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)

        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)

    # ===================== 端口检测 =====================

    def is_port_in_use(self, port: int) -> bool:
        """检测端口是否被占用"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return False
            except OSError:
                return True

    def get_process_using_port(self, port: int) -> Optional[str]:
        """获取占用端口的进程信息"""
        try:
            if sys.platform == 'win32':
                result = subprocess.run(
                    ['netstat', '-ano'],
                    capture_output=True,
                    text=True
                )
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        pid = parts[-1]
                        # 获取进程名
                        proc_result = subprocess.run(
                            ['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV', '/NH'],
                            capture_output=True,
                            text=True
                        )
                        if proc_result.stdout:
                            proc_name = proc_result.stdout.split(',')[0].strip('"')
                            return f"{proc_name} (PID: {pid})"
            else:
                result = subprocess.run(
                    ['lsof', '-i', f':{port}'],
                    capture_output=True,
                    text=True
                )
                lines = result.stdout.split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    return f"{parts[0]} (PID: {parts[1]})"
        except Exception:
            pass
        return None

    def scan_ports(self, start: int, end: int) -> List[int]:
        """扫描端口范围，返回占用的端口列表"""
        used_ports = []
        for port in range(start, end + 1):
            if self.is_port_in_use(port):
                used_ports.append(port)
        return used_ports

    # ===================== 端口注册 =====================

    def register_port(self, port: int, project: str, service: str,
                     description: str = "", force: bool = False) -> bool:
        """注册端口"""
        port_str = str(port)

        # 检查端口是否已注册
        if port_str in self.registry["ports"]:
            existing = self.registry["ports"][port_str]
            if not force:
                print_error(f"端口 {port} 已被注册")
                print(f"  项目: {existing['project']}")
                print(f"  服务: {existing['service']}")
                print(f"  描述: {existing.get('description', 'N/A')}")
                print(f"  注册时间: {existing['registered_at']}")
                print("\n使用 --force 强制覆盖")
                return False

        # 检查端口是否被占用
        if self.is_port_in_use(port):
            process = self.get_process_using_port(port)
            print_warning(f"端口 {port} 当前被占用")
            if process:
                print(f"  占用进程: {process}")

        # 注册端口
        self.registry["ports"][port_str] = {
            "port": port,
            "project": project,
            "service": service,
            "description": description,
            "registered_at": datetime.now().isoformat(),
            "last_checked": datetime.now().isoformat()
        }

        # 更新项目记录
        if project not in self.registry["projects"]:
            self.registry["projects"][project] = []

        if port not in self.registry["projects"][project]:
            self.registry["projects"][project].append(port)

        # 记录历史
        self.registry["history"].append({
            "action": "register",
            "port": port,
            "project": project,
            "service": service,
            "timestamp": datetime.now().isoformat()
        })

        # 保持历史记录不超过 100 条
        if len(self.registry["history"]) > 100:
            self.registry["history"] = self.registry["history"][-100:]

        self._save_registry()
        print_success(f"端口 {port} 已注册到项目 '{project}'")
        return True

    def unregister_port(self, port: int) -> bool:
        """注销端口"""
        port_str = str(port)

        if port_str not in self.registry["ports"]:
            print_error(f"端口 {port} 未注册")
            return False

        port_info = self.registry["ports"][port_str]
        project = port_info["project"]

        # 从项目列表中移除
        if project in self.registry["projects"]:
            if port in self.registry["projects"][project]:
                self.registry["projects"][project].remove(port)

            # 如果项目没有端口了，删除项目
            if not self.registry["projects"][project]:
                del self.registry["projects"][project]

        # 删除端口记录
        del self.registry["ports"][port_str]

        # 记录历史
        self.registry["history"].append({
            "action": "unregister",
            "port": port,
            "project": project,
            "timestamp": datetime.now().isoformat()
        })

        self._save_registry()
        print_success(f"端口 {port} 已注销")
        return True

    # ===================== 端口查询 =====================

    def list_all(self):
        """列出所有注册的端口"""
        if not self.registry["ports"]:
            print_info("没有已注册的端口")
            return

        print_header("已注册端口列表")

        # 按端口号排序
        sorted_ports = sorted(
            self.registry["ports"].items(),
            key=lambda x: int(x[0])
        )

        print(f"{'端口':<8} {'项目':<20} {'服务':<15} {'状态':<10} {'描述':<30}")
        print("-" * 90)

        for port_str, info in sorted_ports:
            port = int(port_str)
            in_use = self.is_port_in_use(port)
            status = f"{Colors.RED}占用{Colors.NC}" if in_use else f"{Colors.GREEN}空闲{Colors.NC}"

            print(f"{port:<8} {info['project']:<20} {info['service']:<15} ", end='')
            print(status, end='')
            print(f"   {info.get('description', ''):<30}")

        print()

    def list_project(self, project: str):
        """列出项目的端口"""
        if project not in self.registry["projects"]:
            print_error(f"项目 '{project}' 未注册任何端口")
            return

        print_header(f"项目 '{project}' 的端口")

        ports = sorted(self.registry["projects"][project])

        print(f"{'端口':<8} {'服务':<15} {'状态':<10} {'描述':<30}")
        print("-" * 70)

        for port in ports:
            port_str = str(port)
            info = self.registry["ports"][port_str]
            in_use = self.is_port_in_use(port)
            status = f"{Colors.RED}占用{Colors.NC}" if in_use else f"{Colors.GREEN}空闲{Colors.NC}"

            print(f"{port:<8} {info['service']:<15} ", end='')
            print(status, end='')
            print(f"   {info.get('description', ''):<30}")

        print()

    def check_port(self, port: int):
        """检查端口详细信息"""
        port_str = str(port)

        print_header(f"端口 {port} 详细信息")

        # 注册信息
        if port_str in self.registry["ports"]:
            info = self.registry["ports"][port_str]
            print("📋 注册信息:")
            print(f"  项目: {info['project']}")
            print(f"  服务: {info['service']}")
            print(f"  描述: {info.get('description', 'N/A')}")
            print(f"  注册时间: {info['registered_at']}")
        else:
            print_info("端口未注册")

        print()

        # 实际占用情况
        in_use = self.is_port_in_use(port)
        if in_use:
            print_warning("端口当前被占用")
            process = self.get_process_using_port(port)
            if process:
                print(f"  占用进程: {process}")
        else:
            print_success("端口空闲，可以使用")

        print()

    # ===================== 智能端口分配 =====================

    def find_available_port(self, service_type: str = 'custom',
                           preferred: Optional[int] = None) -> Optional[int]:
        """查找可用端口"""
        # 如果指定了首选端口
        if preferred:
            if not self.is_port_in_use(preferred) and str(preferred) not in self.registry["ports"]:
                return preferred

        # 根据服务类型查找
        if service_type in DEFAULT_PORT_RANGES:
            start, end = DEFAULT_PORT_RANGES[service_type]
        else:
            start, end = DEFAULT_PORT_RANGES['custom']

        # 查找可用端口
        for port in range(start, end + 1):
            port_str = str(port)
            if not self.is_port_in_use(port) and port_str not in self.registry["ports"]:
                return port

        return None

    def suggest_port(self, service_type: str):
        """推荐可用端口"""
        print_header(f"推荐 {service_type} 服务端口")

        port = self.find_available_port(service_type)

        if port:
            print_success(f"推荐端口: {port}")

            if service_type in DEFAULT_PORT_RANGES:
                start, end = DEFAULT_PORT_RANGES[service_type]
                print(f"端口范围: {start}-{end}")

            print("\n注册命令:")
            print(f"  python scripts/port-manager.py register {port} <项目名> {service_type}")
        else:
            print_error(f"未找到可用的 {service_type} 端口")
            print("建议:")
            print("  1. 释放一些不再使用的端口")
            print("  2. 使用 custom 类型的端口范围 (10000-20000)")

    # ===================== 冲突检测 =====================

    def detect_conflicts(self):
        """检测端口冲突"""
        print_header("端口冲突检测")

        conflicts = []

        for port_str, info in self.registry["ports"].items():
            port = int(port_str)
            if self.is_port_in_use(port):
                process = self.get_process_using_port(port)
                conflicts.append({
                    "port": port,
                    "registered": info,
                    "process": process
                })

        if not conflicts:
            print_success("未检测到端口冲突")
            return

        print_warning(f"检测到 {len(conflicts)} 个端口冲突")
        print()

        for conflict in conflicts:
            port = conflict["port"]
            info = conflict["registered"]

            print(f"🔴 端口 {port}:")
            print(f"  已注册: {info['project']} / {info['service']}")
            print(f"  占用进程: {conflict['process'] or '未知'}")
            print()

    # ===================== 项目管理 =====================

    def list_projects(self):
        """列出所有项目"""
        if not self.registry["projects"]:
            print_info("没有已注册的项目")
            return

        print_header("已注册项目列表")

        for project, ports in sorted(self.registry["projects"].items()):
            print(f"📦 {project}")
            print(f"  端口数量: {len(ports)}")
            print(f"  端口: {', '.join(map(str, sorted(ports)))}")
            print()

    def export_project_config(self, project: str, output_file: Optional[str] = None):
        """导出项目配置"""
        if project not in self.registry["projects"]:
            print_error(f"项目 '{project}' 未注册")
            return

        ports = self.registry["projects"][project]
        config = {}

        for port in ports:
            port_str = str(port)
            info = self.registry["ports"][port_str]
            service = info["service"].upper()
            config[f"{service}_PORT"] = port

        if not output_file:
            output_file = f"{project}.env"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Port configuration for {project}\n")
            f.write(f"# Generated at {datetime.now().isoformat()}\n\n")
            for key, value in config.items():
                f.write(f"{key}={value}\n")

        print_success(f"配置已导出到: {output_file}")

# ===================== 主函数 =====================

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='全局端口管理工具 v1.0.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 注册端口
  python port-manager.py register 3306 myproject mysql "主数据库"

  # 查询端口
  python port-manager.py check 3306

  # 列出所有端口
  python port-manager.py list

  # 推荐可用端口
  python port-manager.py suggest mysql

  # 检测冲突
  python port-manager.py conflicts
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='命令')

    # register 命令
    register_parser = subparsers.add_parser('register', help='注册端口')
    register_parser.add_argument('port', type=int, help='端口号')
    register_parser.add_argument('project', help='项目名称')
    register_parser.add_argument('service', help='服务类型 (mysql/redis/web等)')
    register_parser.add_argument('--description', '-d', default='', help='端口描述')
    register_parser.add_argument('--force', '-f', action='store_true', help='强制覆盖')

    # unregister 命令
    unregister_parser = subparsers.add_parser('unregister', help='注销端口')
    unregister_parser.add_argument('port', type=int, help='端口号')

    # list 命令
    list_parser = subparsers.add_parser('list', help='列出端口')
    list_parser.add_argument('--project', '-p', help='指定项目')

    # check 命令
    check_parser = subparsers.add_parser('check', help='检查端口')
    check_parser.add_argument('port', type=int, help='端口号')

    # suggest 命令
    suggest_parser = subparsers.add_parser('suggest', help='推荐可用端口')
    suggest_parser.add_argument('service', help='服务类型 (mysql/redis/web等)')

    # conflicts 命令
    conflicts_parser = subparsers.add_parser('conflicts', help='检测端口冲突')

    # projects 命令
    projects_parser = subparsers.add_parser('projects', help='列出所有项目')

    # export 命令
    export_parser = subparsers.add_parser('export', help='导出项目配置')
    export_parser.add_argument('project', help='项目名称')
    export_parser.add_argument('--output', '-o', help='输出文件')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 创建管理器
    manager = PortManager()

    # 执行命令
    if args.command == 'register':
        manager.register_port(
            args.port,
            args.project,
            args.service,
            args.description,
            args.force
        )

    elif args.command == 'unregister':
        manager.unregister_port(args.port)

    elif args.command == 'list':
        if args.project:
            manager.list_project(args.project)
        else:
            manager.list_all()

    elif args.command == 'check':
        manager.check_port(args.port)

    elif args.command == 'suggest':
        manager.suggest_port(args.service)

    elif args.command == 'conflicts':
        manager.detect_conflicts()

    elif args.command == 'projects':
        manager.list_projects()

    elif args.command == 'export':
        manager.export_project_config(args.project, args.output)

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

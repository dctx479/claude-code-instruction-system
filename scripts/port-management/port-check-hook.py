#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端口检查钩子 - Claude Code PreToolUse Hook (全局版本)
版本：1.1.0
用途：在执行 Docker/Compose 命令前检查端口冲突
支持：全局配置和项目配置的自动查找
"""

import os
import sys
import re
import json
from pathlib import Path

def find_registry_file() -> str:
    """查找端口注册表文件（优先级：项目 > 全局 > 用户主目录）"""
    candidates = [
        # 1. 当前项目目录
        'config/port-registry.json',
        # 2. 全局 Claude 配置目录
        os.path.expanduser('~/.claude/config/port-registry.json'),
        # 3. Windows 用户目录
        os.path.expanduser('~/AppData/Roaming/.claude/config/port-registry.json'),
    ]

    for path in candidates:
        if os.path.exists(path):
            return path

    return None

def extract_ports_from_command(command: str) -> list:
    """从命令中提取端口号"""
    ports = []

    # docker run -p 8080:80
    p_matches = re.findall(r'-p\s+(\d+):', command)
    ports.extend([int(p) for p in p_matches])

    # docker-compose
    if 'docker-compose' in command or 'docker compose' in command:
        # 尝试从环境变量或默认值提取
        pass

    return ports

def check_port_conflicts(ports: list) -> list:
    """检查端口冲突"""
    conflicts = []
    registry_file = find_registry_file()

    if not registry_file:
        # 没有找到注册表文件，不检查（允许通过）
        return conflicts

    try:
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)

        for port in ports:
            port_str = str(port)
            if port_str in registry.get('ports', {}):
                info = registry['ports'][port_str]
                conflicts.append({
                    'port': port,
                    'project': info.get('project'),
                    'service': info.get('service'),
                    'registry': registry_file
                })
    except Exception as e:
        # 读取失败，打印警告但允许通过
        print(f"WARNING: Failed to read registry: {e}", file=sys.stderr)
        return []

    return conflicts

def main():
    # 读取标准输入 (Claude Code 传入的工具输入)
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        input_data = {}

    command = input_data.get('tool_input', {}).get('command', '')

    # 检查是否是 Docker 相关命令
    if not any(k in command.lower() for k in ['docker', 'compose']):
        sys.exit(0)

    # 提取端口
    ports = extract_ports_from_command(command)

    if not ports:
        sys.exit(0)

    # 检查冲突
    conflicts = check_port_conflicts(ports)

    if conflicts:
        print("WARNING: Port conflicts detected!", file=sys.stderr)
        for c in conflicts:
            print(f"  Port {c['port']}: used by {c['project']}/{c['service']}", file=sys.stderr)
            print(f"  Registry: {c['registry']}", file=sys.stderr)
        print("\nRun: python scripts/port-manager.py conflicts", file=sys.stderr)
        # 返回 1 表示警告但继续
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()

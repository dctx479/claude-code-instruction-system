#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端口导入/导出工具
版本：1.0.0
用途：批量导入/导出端口配置
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

def print_success(text): print(f'{Colors.GREEN}[OK] {text}{Colors.NC}')
def print_error(text): print(f'{Colors.RED}[ERROR] {text}{Colors.NC}')
def print_info(text): print(f'{Colors.BLUE}[INFO] {text}{Colors.NC}')

class PortImportExport:
    def __init__(self, registry_file='config/port-registry.json'):
        self.registry_file = registry_file
        self.registry = self._load()
    
    def _load(self) -> Dict:
        if os.path.exists(self.registry_file):
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'version': '2.0.0', 'ports': {}, 'projects': {}, 'history': []}
    
    def _save(self):
        self.registry['last_updated'] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)
    
    def export_all(self, output_file: str, format: str = 'json'):
        """导出所有端口配置"""
        if format == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
        elif format == 'env':
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('# Port Registry Export\n')
                f.write(f'# Generated: {datetime.now().isoformat()}\n\n')
                for port_str, info in sorted(self.registry['ports'].items(), key=lambda x: int(x[0])):
                    service = info.get('service', 'unknown').upper()
                    project = info.get('project', 'unknown')
                    f.write(f"# {project}\n")
                    f.write(f"{service}_PORT={port_str}\n\n")
        elif format == 'csv':
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('port,project,service,description,registered_at\n')
                for port_str, info in sorted(self.registry['ports'].items(), key=lambda x: int(x[0])):
                    f.write(f"{port_str},{info.get('project','')},{info.get('service','')},")
                    f.write(f"{info.get('description','')},{info.get('registered_at','')}\n")
        
        print_success(f'Exported to {output_file}')
    
    def import_json(self, input_file: str, merge: bool = True):
        """从 JSON 导入"""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        imported = 0
        if merge:
            for port_str, info in data.get('ports', {}).items():
                if port_str not in self.registry['ports']:
                    self.registry['ports'][port_str] = info
                    imported += 1
            for project, pinfo in data.get('projects', {}).items():
                if project not in self.registry['projects']:
                    self.registry['projects'][project] = pinfo
        else:
            self.registry = data
            imported = len(data.get('ports', {}))
        
        self._save()
        print_success(f'Imported {imported} ports from {input_file}')
    
    def import_env(self, input_file: str, project: str):
        """从 .env 文件导入"""
        imported = 0
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key.endswith('_PORT') and value.isdigit():
                        port = int(value)
                        service = key[:-5].lower()  # Remove _PORT suffix
                        
                        if str(port) not in self.registry['ports']:
                            self.registry['ports'][str(port)] = {
                                'port': port,
                                'project': project,
                                'service': service,
                                'registered_at': datetime.now().isoformat()
                            }
                            imported += 1
        
        if project not in self.registry['projects']:
            self.registry['projects'][project] = {
                'path': os.path.dirname(os.path.abspath(input_file)),
                'ports': [int(p) for p in self.registry['ports'] 
                         if self.registry['ports'][p].get('project') == project],
                'environment': 'development'
            }
        
        self._save()
        print_success(f'Imported {imported} ports from {input_file}')

def main():
    parser = argparse.ArgumentParser(description='端口导入/导出工具')
    sub = parser.add_subparsers(dest='cmd')
    
    # export
    exp = sub.add_parser('export', help='导出端口配置')
    exp.add_argument('output', help='输出文件')
    exp.add_argument('--format', '-f', choices=['json', 'env', 'csv'], default='json')
    
    # import
    imp = sub.add_parser('import', help='导入端口配置')
    imp.add_argument('input', help='输入文件')
    imp.add_argument('--format', '-f', choices=['json', 'env'], default='json')
    imp.add_argument('--project', '-p', help='项目名 (env格式需要)')
    imp.add_argument('--replace', action='store_true', help='替换而非合并')
    
    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return
    
    tool = PortImportExport()
    
    if args.cmd == 'export':
        tool.export_all(args.output, args.format)
    elif args.cmd == 'import':
        if args.format == 'json':
            tool.import_json(args.input, merge=not args.replace)
        elif args.format == 'env':
            if not args.project:
                print_error('--project required for env format')
                return
            tool.import_env(args.input, args.project)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端口迁移工具
版本：1.0.0
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

def print_success(text): print(f'{Colors.GREEN}[OK] {text}{Colors.NC}')
def print_error(text): print(f'{Colors.RED}[ERROR] {text}{Colors.NC}')
def print_warning(text): print(f'{Colors.YELLOW}[WARN] {text}{Colors.NC}')
def print_info(text): print(f'{Colors.BLUE}[INFO] {text}{Colors.NC}')

class PortMigrator:
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
    
    def migrate(self, old_port: int, new_port: int, project: Optional[str] = None,
                update_files: bool = True, dry_run: bool = False) -> Dict:
        old_str, new_str = str(old_port), str(new_port)
        result = {'success': False, 'old_port': old_port, 'new_port': new_port, 'files_updated': [], 'errors': []}
        
        if old_str not in self.registry['ports']:
            result['errors'].append(f'Port {old_port} not registered')
            return result
        if new_str in self.registry['ports']:
            result['errors'].append(f'Port {new_port} already registered')
            return result
        
        port_info = self.registry['ports'][old_str]
        target_project = project or port_info['project']
        
        if not dry_run:
            port_info['port'] = new_port
            port_info['migrated_from'] = old_port
            self.registry['ports'][new_str] = port_info
            del self.registry['ports'][old_str]
            
            if target_project in self.registry['projects']:
                proj = self.registry['projects'][target_project]
                if old_port in proj.get('ports', []):
                    proj['ports'].remove(old_port)
                    proj['ports'].append(new_port)
            
            self.registry['history'].append({
                'action': 'migrate', 'old_port': old_port,
                'new_port': new_port, 'project': target_project,
                'timestamp': datetime.now().isoformat()
            })
            self._save()
        
        if update_files and target_project in self.registry.get('projects', {}):
            proj_path = self.registry['projects'][target_project].get('path', '')
            if proj_path:
                result['files_updated'] = self._update_files(proj_path, old_port, new_port, dry_run)
        
        result['success'] = True
        return result
    
    def _update_files(self, path: str, old: int, new: int, dry: bool) -> List[str]:
        updated = []
        for fn in ['.env', '.env.local', 'docker-compose.yml', 'docker-compose.yaml']:
            fp = os.path.join(path, fn)
            if os.path.exists(fp):
                try:
                    with open(fp, 'r', encoding='utf-8') as f:
                        content = f.read()
                    new_content = content.replace(f'={old}', f'={new}').replace(f':{old}', f':{new}')
                    if new_content != content:
                        if not dry:
                            with open(fp, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                        updated.append(fp)
                except: pass
        return updated
    
    def batch(self, mapping_file: str, dry_run: bool = False) -> List[Dict]:
        results = []
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mappings = json.load(f)
        for m in mappings:
            print_info(f"Migrating {m['old_port']} -> {m['new_port']}")
            r = self.migrate(m['old_port'], m['new_port'], m.get('project'), dry_run=dry_run)
            results.append(r)
            if r['success']: print_success(f"Done: {m['old_port']} -> {m['new_port']}")
            else: print_error(f"Failed: {r['errors']}")
        return results

def main():
    parser = argparse.ArgumentParser(description='端口迁移工具')
    sub = parser.add_subparsers(dest='cmd')
    
    s = sub.add_parser('migrate', help='迁移端口')
    s.add_argument('old_port', type=int)
    s.add_argument('new_port', type=int)
    s.add_argument('--project', '-p')
    s.add_argument('--dry-run', action='store_true')
    
    b = sub.add_parser('batch', help='批量迁移')
    b.add_argument('mapping_file')
    b.add_argument('--dry-run', action='store_true')
    
    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return
    
    m = PortMigrator()
    if args.cmd == 'migrate':
        r = m.migrate(args.old_port, args.new_port, args.project, dry_run=args.dry_run)
        if args.dry_run: print_info('[DRY RUN]')
        if r['success']:
            print_success(f'Migrated {args.old_port} -> {args.new_port}')
            for f in r['files_updated']: print(f'  Updated: {f}')
        else:
            print_error(f"Failed: {r['errors']}")
    elif args.cmd == 'batch':
        results = m.batch(args.mapping_file, args.dry_run)
        ok = sum(1 for r in results if r['success'])
        print_info(f'Completed: {ok}/{len(results)}')

if __name__ == '__main__':
    main()

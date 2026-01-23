#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker Compose 端口同步工具
版本：1.0.0
"""

import os
import sys
import re
import json
import argparse
import socket
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

class Colors:
    RED = chr(27) + "[0;31m"
    GREEN = chr(27) + "[0;32m"
    YELLOW = chr(27) + "[1;33m"
    BLUE = chr(27) + "[0;34m"
    NC = chr(27) + "[0m"

def print_success(text): print(f"{Colors.GREEN}[OK] {text}{Colors.NC}")
def print_error(text): print(f"{Colors.RED}[ERROR] {text}{Colors.NC}")
def print_warning(text): print(f"{Colors.YELLOW}[WARN] {text}{Colors.NC}")
def print_info(text): print(f"{Colors.BLUE}[INFO] {text}{Colors.NC}")

DEFAULT_PORT_RANGES = {
    "mysql": (3306, 3399),
    "postgresql": (5432, 5499),
    "redis": (6379, 6449),
    "mongodb": (27017, 27099),
    "web": (3000, 3999),
    "api": (8000, 8999),
    "custom": (10000, 19999)
}

class DockerComposeParser:
    def __init__(self, compose_file: str):
        self.compose_file = compose_file
        self.data = self._load_compose()
    
    def _load_compose(self) -> Dict:
        if not HAS_YAML:
            raise RuntimeError("PyYAML required: pip install pyyaml")
        with open(self.compose_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def extract_ports(self) -> List[Dict]:
        ports = []
        services = self.data.get("services", {})
        for svc_name, svc_cfg in services.items():
            for pm in svc_cfg.get("ports", []):
                info = self._parse_port(pm, svc_name)
                if info:
                    meta = svc_cfg.get("x-port-manager", {})
                    info["service_type"] = meta.get("service", self._guess_type(svc_name))
                    ports.append(info)
        return ports
    
    def _parse_port(self, mapping, svc_name) -> Optional[Dict]:
        if isinstance(mapping, int):
            return {"service": svc_name, "host_port": mapping, "variable": None, "default": mapping}
        if isinstance(mapping, str):
            parts = mapping.split(":")
            if len(parts) >= 2:
                host = parts[0]
                match = re.match(r"$\{(\w+)(?::-(\d+))?\}", host)
                if match:
                    return {"service": svc_name, "host_port": None, "variable": match.group(1),
                            "default": int(match.group(2)) if match.group(2) else None}
                try:
                    return {"service": svc_name, "host_port": int(host), "variable": None, "default": int(host)}
                except: pass
        return None
    
    def _guess_type(self, name: str) -> str:
        n = name.lower()
        for k, v in {"mysql": "mysql", "postgres": "postgresql", "redis": "redis", 
                     "mongo": "mongodb", "api": "api", "web": "web"}.items():
            if k in n: return v
        return "custom"

class PortSynchronizer:
    def __init__(self, registry_file="config/port-registry.json"):
        self.registry_file = registry_file
        self.registry = self._load()
    
    def _load(self) -> Dict:
        if os.path.exists(self.registry_file):
            with open(self.registry_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"version": "2.0.0", "ports": {}, "projects": {}, "history": []}
    
    def _save(self):
        self.registry["last_updated"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)
    
    def check_conflicts(self, ports: List[Dict]) -> List[Dict]:
        conflicts = []
        for p in ports:
            port = p.get("host_port") or p.get("default")
            if not port: continue
            if str(port) in self.registry["ports"]:
                conflicts.append({"port": port, "type": "registered", "service": p["service"]})
            else:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try: s.bind(("127.0.0.1", port))
                    except: conflicts.append({"port": port, "type": "in_use", "service": p["service"]})
        return conflicts
    
    def allocate(self, stype: str) -> Optional[int]:
        start, end = DEFAULT_PORT_RANGES.get(stype, (10000, 19999))
        for port in range(start, end + 1):
            if str(port) not in self.registry["ports"]:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        s.bind(("127.0.0.1", port))
                        return port
                    except: pass
        return None

def main():
    parser = argparse.ArgumentParser(description="Docker Compose 端口同步")
    sub = parser.add_subparsers(dest="cmd")
    
    cp = sub.add_parser("check", help="检查冲突")
    cp.add_argument("file", help="docker-compose.yml")
    
    ip = sub.add_parser("import", help="导入端口")
    ip.add_argument("file", help="docker-compose.yml")
    ip.add_argument("--project", "-p")
    
    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return
    
    if not HAS_YAML:
        print_error("PyYAML required: pip install pyyaml")
        return
    
    if args.cmd == "check":
        dp = DockerComposeParser(args.file)
        ports = dp.extract_ports()
        print_info(f"Found {len(ports)} ports")
        conflicts = PortSynchronizer().check_conflicts(ports)
        if conflicts:
            print_warning(f"{len(conflicts)} conflicts")
            for c in conflicts: print(f"  {c['port']}: {c['type']}")
        else:
            print_success("No conflicts")
    
    elif args.cmd == "import":
        dp = DockerComposeParser(args.file)
        ports = dp.extract_ports()
        project = args.project or os.path.basename(os.path.dirname(os.path.abspath(args.file)))
        sync = PortSynchronizer()
        n = 0
        for p in ports:
            port = p.get("host_port") or p.get("default")
            if port and str(port) not in sync.registry["ports"]:
                sync.registry["ports"][str(port)] = {
                    "port": port, "project": project, "service": p["service_type"],
                    "registered_at": datetime.now().isoformat()
                }
                n += 1
        sync._save()
        print_success(f"Imported {n} ports for {project}")

if __name__ == "__main__":
    main()

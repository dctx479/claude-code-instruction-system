#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Claude Code Statusline v9.0 - 修复版"""
import json, sys, os
from datetime import datetime
from pathlib import Path

DEBUG = os.environ.get('DEBUG_STATUSLINE') == '1'

def log(msg):
    if DEBUG:
        with open(os.path.expanduser("~/.claude/statusline.log"), 'a') as f:
            f.write(f"{msg}\n")

def fmt(n):
    try:
        n = int(n)
        return f"{n/1000000:.1f}M" if n >= 1000000 else f"{n/1000:.0f}K" if n >= 1000 else str(n)
    except:
        return "0"

def read_json_file(path):
    """安全读取 JSON 文件"""
    try:
        if Path(path).exists():
            with open(path) as f:
                return json.load(f)
    except:
        pass
    return None

# 读取 Claude Code JSON
data = {}
try:
    raw = sys.stdin.read()
    log(f"Raw input length: {len(raw)}")
    if raw.strip():
        data = json.loads(raw)
        log(f"Parsed keys: {list(data.keys())}")
except Exception as e:
    log(f"Parse error: {e}")

# 提取 Claude Code 字段
model = data.get('model', {}).get('display_name', 'Claude')
log(f"Model: {model}")

cwd = data.get('cwd', '') or data.get('workspace', {}).get('current_dir', '')
dir_name = cwd.replace('\\', '/').rstrip('/').split('/')[-1][:20] if cwd else ''
log(f"Dir: {dir_name}")

ctx = data.get('context_window', {})
inp = ctx.get('total_input_tokens', 0)
out = ctx.get('total_output_tokens', 0)
pct = ctx.get('used_percentage', 0)
cost = data.get('cost', {}).get('total_cost_usd', 0)
log(f"Tokens: {inp}i/{out}o, CTX: {pct}%, Cost: ${cost}")

# 读取 Agent 状态（使用绝对路径）
agent_file = Path.cwd() / ".claude" / "agent-state.json"
agent_state = read_json_file(agent_file)
agent_str = ""
if agent_state and agent_state.get('current_agent'):
    agent_str = f"@{agent_state['current_agent']}"
log(f"Agent: {agent_str}")

# 读取 Ralph 状态
ralph_file = Path.cwd() / "memory" / "ralph-state.json"
ralph = read_json_file(ralph_file)
ralph_str = ""
if ralph and ralph.get('active'):
    iter_num = ralph.get('iteration', 0)
    max_iter = ralph.get('max_iterations', 10)
    ralph_str = f"R:{iter_num}/{max_iter}"

# 构建输出
parts = [f"[{datetime.now():%H:%M:%S}]", model]
if dir_name: parts.append(dir_name)
if agent_str: parts.append(agent_str)
if pct > 0: parts.append(f"CTX:{pct:.0f}%")
parts.append(f"{fmt(inp)}i/{fmt(out)}o")
if ralph_str: parts.append(ralph_str)
if cost > 0: parts.append(f"${cost:.2f}")

print(" | ".join(parts))

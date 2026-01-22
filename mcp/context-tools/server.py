#!/usr/bin/env python3
"""MCP Server for Context Archive Tools"""
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("context-tools")

CONTEXT_DIR = Path(".claude/context")
INDEX_FILE = CONTEXT_DIR / "index.json"
RESOLUTIONS_DIR = CONTEXT_DIR / "resolutions"

def read_index() -> Dict[str, Any]:
    """Read index.json"""
    if not INDEX_FILE.exists():
        return {"detail_index": {"resolutions": []}}
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def read_resolution(res_id: str) -> Optional[Dict[str, Any]]:
    """Read resolution from NDJSON files"""
    if not RESOLUTIONS_DIR.exists():
        return None

    for ndjson_file in RESOLUTIONS_DIR.glob("*.ndjson"):
        with open(ndjson_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    res = json.loads(line)
                    if res.get("id") == res_id:
                        return res
    return None

@app.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="read_context_index",
            description="读取项目上下文索引，获取项目状态、已验证事实、问题解决方案列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词（可选）"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "标签过滤（可选）"}
                }
            }
        ),
        Tool(
            name="read_context_resolution",
            description="读取特定问题的详细解决方案，包括问题描述、根本原因、修复步骤、验证方法",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Resolution ID (如 res-001)"}
                },
                "required": ["id"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    if name == "read_context_index":
        index = read_index()
        query = arguments.get("query", "")
        tags = arguments.get("tags", [])

        resolutions = index.get("detail_index", {}).get("resolutions", [])

        # Filter by tags
        if tags:
            resolutions = [r for r in resolutions if any(t in r.get("tags", []) for t in tags)]

        # Filter by query
        if query:
            query_lower = query.lower()
            resolutions = [r for r in resolutions if
                query_lower in r.get("summary", "").lower() or
                query_lower in r.get("problem_signature", "").lower()]

        result = {
            "project": index.get("project", "unknown"),
            "current_state": index.get("current_state", ""),
            "goals": index.get("goals", []),
            "verified_facts": index.get("verified_facts", []),
            "next_actions": index.get("next_actions", []),
            "resolutions": resolutions
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

    elif name == "read_context_resolution":
        res_id = arguments["id"]
        resolution = read_resolution(res_id)

        if not resolution:
            return [TextContent(type="text", text=f"Resolution {res_id} not found")]

        return [TextContent(type="text", text=json.dumps(resolution, indent=2, ensure_ascii=False))]

    return [TextContent(type="text", text="Unknown tool")]

if __name__ == "__main__":
    import asyncio
    asyncio.run(app.run())

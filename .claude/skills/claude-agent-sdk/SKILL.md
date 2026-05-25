---
name: claude-agent-sdk
description: 将任何 Skill 封装为 Claude Agent SDK Web 应用的五步法，包含项目架构、代码模板、安全部署、SessionStore 会话持久化和 Multi-Agent 子 Agent 编排
type: skill
version: v1.1
date: 2026-05-25
trigger:
  - "用 claude-agent-sdk 建立 webapp"
  - "把 skill 转为 web 应用"
  - "构建 claude agent sdk 项目"
  - "claude-agent-sdk web"
  - "agent sdk 项目"
集成:
  - skill-creator
  - sdd-riper
  - code-security-review
来源: liangdabiao/claudesdk-skill (开源实验项目)
---

# Claude Agent SDK Skill

将 Claude Code Skill 转化为可对外服务的 Claude Agent SDK Web 应用（Web SaaS）。

## What

**输入**: 一个已验证可用的 Claude Code Skill（或 Skill 目录）
**输出**: 一个完整的 Web 应用，可通过浏览器对话使用该 Skill 的全部能力
**核心价值**: 把 Claude Code 的 Skill 能力封装为 SaaS，对外提供服务

## How — 五步工作流

### Step 1: 环境准备

**确保 Skill 文件在正确位置**:
```
project-root/
  your-skill/           ← 待封装的 Skill（任意数量）
    *.md 或 */
  .claude/
    skills/
      claude-agent-sdk/ ← 本 Skill 放在 Claude Code 的 skills 目录
        SKILL.md
```

**安装依赖**:
```bash
# Python
pip install claude-agent-sdk fastapi uvicorn

# TypeScript
npm install @anthropic-ai/claude-agent-sdk express @types/express
```

### Step 2: 分析 Skill，确定工具接口

读取待封装 Skill 的所有 `*.md` 文件，提炼出 Skill 对外暴露的**操作能力**，对应为 Agent SDK 的**自定义工具（Custom Tools）**:

| Skill 操作 | 对应 SDK 概念 | 映射示例 |
|-----------|-------------|---------|
| 查询数据 | `tool()` 自定义函数 | `search_stock("贵州茅台")` |
| 生成图表 | `tool()` + 业务逻辑 | `generate_chart(code, type)` |
| 分析文件 | 内置 `Read`/`Bash` 工具 | 直接用 |
| 上传数据 | `tool()` + multipart | `upload_csv(file)` |

**核心原则**: Skill 里的"What"和"触发条件"对应工具能力，"How"对应工具实现。

### Step 3: 编写 Agent 核心代码

#### Python 方案（推荐）

```python
# agent.py
from claude_agent_sdk import (
    tool, create_sdk_mcp_server,
    ClaudeAgentOptions, ClaudeSDKClient
)
from typing import Any
import anyio

# 1. 定义 Skill 对应的自定义工具
@tool("search_data", "Search data via skill", {"query": str})
async def search_data(args: dict) -> dict:
    """将 Skill 的查询能力封装为工具"""
    query = args["query"]
    # 调用 Skill 背后的实际逻辑（API/数据库/脚本）
    result = do_search(query)  # 替换为真实逻辑
    return {"content": [{"type": "text", "text": str(result)}]}

@tool("generate_chart", "Generate analysis chart", {"code": str, "chart_type": str})
async def generate_chart(args: dict) -> dict:
    """将 Skill 的图表生成能力封装为工具"""
    code = args["code"]
    chart_type = args["chart_type"]
    result = do_generate_chart(code, chart_type)
    return {"content": [{"type": "text", "text": result}]}

# 2. 注册 MCP Server（打包所有自定义工具）
server = create_sdk_mcp_server(
    name="my-skill-tools",
    version="1.0.0",
    tools=[search_data, generate_chart]
)

# 3. 配置 Agent 选项
options = ClaudeAgentOptions(
    mcp_servers=[server],
    # Skill 核心能力对应工具 + 内置文件操作
    allowed_tools=[
        "mcp__my-skill-tools__search_data",
        "mcp__my-skill-tools__generate_chart",
        "Read", "Bash", "Glob", "Grep", "Write", "Edit"
    ],
    system_prompt="""你是一个专业的 [Skill名称] 助手。
用户通过自然语言与您交流，您调用对应工具完成任务。
工作流程：理解需求 → 调用工具 → 返回结果 → 生成图表（如需要）。
始终用中文友好回复。""",
    max_turns=50,
    permission_mode="acceptEdits"
)

# 4. 创建 Agent Client
async def main():
    async with ClaudeSDKClient(options=options) as client:
        await client.query("用户的第一条消息")
        async for msg in client.receive_response():
            print(msg)

if __name__ == "__main__":
    anyio.run(main)
```

#### TypeScript 方案

```typescript
// agent.ts
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

const searchData = tool(
  "search_data",
  "Search data via skill",
  { query: z.string() },
  async ({ query }) => {
    const result = doSearch(query);
    return { content: [{ type: "text", text: JSON.stringify(result) }] };
  }
);

const server = createSdkMcpServer({ name: "my-skill-tools", tools: [searchData] });

for await (const msg of query({
  prompt: "用户的第一条消息",
  options: {
    mcpServers: [server],
    allowedTools: ["mcp__my-skill-tools__search_data", "Read", "Bash", "Glob"],
    systemPrompt: "你是一个专业的助手...",
    maxTurns: 50
  }
})) {
  if (msg.type === "assistant") {
    for (const block of msg.message.content) {
      if ("text" in block) console.log(block.text);
    }
  }
}
```

### Step 3.5: 会话持久化（SessionStore）— 多租户 SaaS 必需

多用户共享服务时，每个用户需要独立会话。SDK 提供 `SessionStore` 协议，支持 PostgreSQL / Redis / S3 后端:

```python
# session_store.py
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from claude_agent_sdk.session_store import PostgresSessionStore

# 方式 A: PostgreSQL（推荐生产环境）
from sqlalchemy.ext.asyncio import create_async_engine, AsyncPool
pool = AsyncPool(create_async_engine("postgresql+asyncpg://user:pass@localhost/db"))
session_store = PostgresSessionStore(pool=pool)
await session_store.create_schema()  # 幂等建表

# 方式 B: Redis（低延迟，适合缓存）
from claude_agent_sdk.session_store import RedisSessionStore
session_store = RedisSessionStore(
    redis_url="redis://localhost:6379",
    prefix="claude_session:",
    ttl_seconds=3600
)

# WebSocket 路由中加入 session 复用
@app.websocket("/ws/agent")
async def agent_ws(websocket):
    await websocket.accept()
    session_id = websocket.cookies.get("session_id")  # 或从 query 取
    user_message = await websocket.receive_text()

    # 刷新模式: "batched"（默认，批量写入）| "eager"（实时，直播场景用）
    options = ClaudeAgentOptions(
        mcp_servers=[server],
        allowed_tools=[...],
        max_turns=50,
        permission_mode="fallback",
        session_store=session_store,
        session_store_session_id=session_id,       # 传入已有 session 则复用
        session_store_flush="eager",                # 实时写入，支持直播 UI
        strict_mcp_config=True,                    # 多租户隔离：忽略全局 MCP 配置
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(user_message)
        async for msg in client.receive_response():
            await websocket.send_text(json.dumps(msg))
```

**Schema 说明**（PostgreSQL）:
- 主键: `(project_key, session_id, subpath)` 复合索引
- 存储格式: JSONB，每行一条 transcript 条目（seq 有序）
- 适用场景: 用户续期对话（session_id 相同则上下文连贯）

**多租户隔离关键配置**:
```python
ClaudeAgentOptions(
    strict_mcp_config=True,  # ✅ 强制只用显式传入的 MCP Server，忽略 ~/.claude/ 等全局配置
)
```

### Step 3.6: Multi-Agent 编排（复杂流水线）

复杂任务（如深度研究）需要多个子 Agent 并行工作:

```python
# multi_agent.py
from claude_agent_sdk import (
    ClaudeSDKClient, ClaudeAgentOptions,
    AgentDefinition, HookMatcher
)
import anyio

# 1. 定义子 Agent（程序化生成，非命令行）
researcher = AgentDefinition(
    name="researcher",
    model="claude-haiku-4-5",         # 轻量模型节省成本
    system_prompt="你是一个研究助手，负责搜索和总结信息。",
    allowed_tools=["WebSearch", "Read", "Write"],
)

data_analyst = AgentDefinition(
    name="data-analyst",
    model="claude-haiku-4-5",
    system_prompt="你是一个数据分析师，负责处理数据和生成图表。",
    allowed_tools=["Read", "Bash", "Glob"],
)

writer = AgentDefinition(
    name="writer",
    model="claude-sonnet-4-7",         # 主力模型
    system_prompt="你是一个报告撰写助手，负责生成最终报告。",
    allowed_tools=["Read", "Write"],
)

# 2. Subagent 追踪 Hook
async def track_subagent(input_data, tool_use_id, context):
    subagent_name = input_data.get("tool_input", {}).get("agent_name")
    print(f"[SUBAGENT] {subagent_name} started")
    return {}

# 3. Lead Agent 配置
options = ClaudeAgentOptions(
    mcp_servers=[...],
    allowed_tools=["mcp__my-tools__..."],
    subagents=[researcher, data_analyst, writer],  # 注册子 Agent
    hooks={
        "SubagentStart": [HookMatcher(matcher=".*", hooks=[track_subagent])]
    }
)

# 4. 使用方式
async def main():
    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "对茅台进行深度财务分析，生成图表和报告"
        )
        async for msg in client.receive_response():
            print(msg)
```

**子 Agent 追踪信号**: `SubagentStart` / `SubagentComplete` / `SubagentError`
**成本控制**: 子 Agent 默认用 Haiku，Lead Agent 用 Sonnet/Opus

### Step 4: 构建 Web 服务层（FastAPI / Express）

#### FastAPI + WebSocket 示例（完整版）

```python
# server.py
from fastapi import FastAPI, WebSocket, Depends
from fastapi.responses import HTMLResponse
from claude_agent_sdk import (
    query, ClaudeAgentOptions, tool, create_sdk_mcp_server,
    PostgresSessionStore, strict_mcp_config
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncPool
import json

app = FastAPI()

# 全局会话存储（连接池复用）
pool = AsyncPool(create_async_engine("postgresql+asyncpg://user:pass@localhost/mydb"))
session_store = PostgresSessionStore(pool=pool)
await session_store.create_schema()

@tool("skill_action", "Execute skill action", {"input": str})
async def skill_action(args) -> dict:
    return {"content": [{"type": "text", "text": f"Result: {args['input']}"}]}

server = create_sdk_mcp_server(name="my-tools", version="1.0.0", tools=[skill_action])

@app.websocket("/ws/agent")
async def agent_ws(websocket):
    await websocket.accept()
    user_message = await websocket.receive_text()
    # 从请求中获取租户 ID（JWT / API Key / Cookie）
    session_id = extract_session_id(websocket)  # 你自己的 session 逻辑

    async for msg in query(
        prompt=user_message,
        options=ClaudeAgentOptions(
            mcp_servers=[server],
            allowed_tools=["mcp__my-tools__skill_action", "Read", "Bash"],
            system_prompt="你是一个专业助手，始终用中文回复。",
            max_turns=50,
            permission_mode="fallback",
            session_store=session_store,
            session_store_session_id=session_id,
            session_store_flush="eager",
            strict_mcp_config=True,       # 多租户隔离
        )
    ):
        if hasattr(msg, 'message'):
            for block in msg.message.content:
                if hasattr(block, 'text'):
                    await websocket.send_text(json.dumps({
                        "type": "text", "content": block.text
                    }))
        elif hasattr(msg, 'type') and msg.type == 'result':
            await websocket.send_text(json.dumps({"type": "done"}))
            # 记录累计成本
            if hasattr(msg, 'total_cost_usd'):
                await record_cost(session_id, msg.total_cost_usd)
            break
    await websocket.close()
```

#### FastAPI + WebSocket 示例

```python
# server.py
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from claude_agent_sdk import query, ClaudeAgentOptions, tool, create_sdk_mcp_server
import json, asyncio

app = FastAPI()

# 你的自定义工具（同 agent.py）
@tool("skill_action", "Execute skill action", {"input": str})
async def skill_action(args) -> dict:
    return {"content": [{"type": "text", "text": f"Result: {args['input']}"}]}

server = create_sdk_mcp_server(name="my-tools", version="1.0.0", tools=[skill_action])

@app.websocket("/ws/agent")
async def agent_ws(websocket):
    await websocket.accept()
    user_message = await websocket.receive_text()

    async for msg in query(
        prompt=user_message,
        options=ClaudeAgentOptions(
            mcp_servers=[server],
            allowed_tools=["mcp__my-tools__skill_action", "Read", "Bash"],
            system_prompt="你是一个专业助手，始终用中文回复。",
            max_turns=50,
            permission_mode="acceptEdits"
        )
    ):
        if hasattr(msg, 'message'):
            for block in msg.message.content:
                if hasattr(block, 'text'):
                    await websocket.send_text(json.dumps({
                        "type": "text", "content": block.text
                    }))
        elif hasattr(msg, 'type') and msg.type == 'result':
            await websocket.send_text(json.dumps({"type": "done"}))
            break

    await websocket.close()

@app.get("/")
async def index():
    return HTMLResponse(open("index.html").read())
```

#### 前端（index.html，核心对话界面）

```html
<!DOCTYPE html>
<html>
<head>
  <title>AI Skill Assistant</title>
  <style>
    body { font-family: sans-serif; max-width: 800px; margin: 2rem auto; padding: 1rem; }
    #chat { height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 1rem; margin-bottom: 1rem; }
    .user { text-align: right; color: #0066cc; }
    .ai { text-align: left; color: #333; }
    .tool-call { background: #f5f5f5; padding: 0.5rem; margin: 0.5rem 0; font-size: 0.9em; }
    pre { background: #f0f0f0; padding: 0.5rem; overflow-x: auto; }
  </style>
</head>
<body>
  <h1>AI Skill Assistant</h1>
  <div id="chat"></div>
  <input id="input" placeholder="输入问题..." style="width: 70%; padding: 0.5rem;" />
  <button onclick="send()" style="padding: 0.5rem 1rem;">发送</button>

  <script>
    const ws = new WebSocket("ws://localhost:8000/ws/agent");
    const chat = document.getElementById("chat");
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "text") {
        chat.innerHTML += `<div class="ai"><pre>${data.content}</pre></div>`;
      }
      chat.scrollTop = chat.scrollHeight;
    };
    function send() {
      const text = input.value;
      chat.innerHTML += `<div class="user">${text}</div>`;
      ws.send(text);
      input.value = "";
    }
    input.onkeydown = (e) => e.key === "Enter" && send();
  </script>
</body>
</html>
```

### Step 5: 端到端测试

**本地运行**:
```bash
# Terminal 1
uvicorn server:app --reload --port 8000

# Terminal 2: 直接测试 Agent 核心逻辑
python agent.py
```

**验证清单**:
- [ ] 对话能正确触发 Skill 工具调用
- [ ] 工具调用结果返回给用户
- [ ] 生成图表/文件可下载/预览
- [ ] Agent 执行日志可见（WebSocket 实时）
- [ ] 上传 CSV/Excel 文件能正确处理
- [ ] 多轮对话保持上下文

## 安全部署（五层防御）

### L1: 权限隔离（Permission Mode）
```python
# 开发: acceptEdits | 生产: fallback (每次询问)
permission_mode="fallback"
```

### L2: 工具白名单
```python
# 只暴露必要工具，禁止危险工具
allowed_tools=["mcp__my-tools__search", "Read", "Bash"]  # 无 Write/Delete
disallowed_tools=["rm", "format", "drop"]
```

### L3: Hooks 审计
```python
from claude_agent_sdk import HookMatcher

async def audit_hook(input_data, tool_use_id, context):
    print(f"[AUDIT] {input_data['tool_name']}: {input_data.get('tool_input', {})}")
    return {}  # 允许执行但记录日志

async def block_dangerous(input_data, tool_use_id, context):
    command = input_data.get("tool_input", {}).get("command", "")
    if "rm -rf" in command or "drop table" in command:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Destructive command blocked",
            }
        }
    return {}

options = ClaudeAgentOptions(
    hooks={
        # ⚠️ 重要：同一事件的所有 Hook Matcher 并行触发（非顺序）
        # 不要依赖 Hook 实现顺序逻辑
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[audit_hook, block_dangerous]),
        ]
    }
)
```

**6 种 Hook 事件类型**: `PreToolUse` / `PostToolUse` / `PostToolUseFailure` / `SubagentStart` / `SubagentComplete` / `SubagentError`

### L4: Docker 沙箱
```dockerfile
FROM python:3.11-slim
RUN pip install claude-agent-sdk fastapi
COPY app.py ./
RUN useradd -m appuser && chown -R appuser:appuser ./
USER appuser
CMD ["uvicorn", "server:app", "--host", "0.0.0.0"]
```

### L5: LlamaFirewall 护栏（生产级）
- 输入层: 检测 Prompt 注入
- 输出层: 内容安全过滤
- 工具层: 细粒度工具访问控制

**MCP 依赖安全**（v0.2.82+）:
```toml
# requirements.txt — 必须 >=1.23.0 修复 GHSA-9h52-p55h-vw2f
mcp>=1.23.0
```

**成本控制**:
```python
from claude_agent_sdk import ClaudeAgentOptions, query

async for msg in query(prompt, options):
    if hasattr(msg, 'total_cost_usd'):
        print(f"[COST] ${msg.total_cost_usd:.4f}")
        if msg.total_cost_usd > 0.50:  # 单会话上限
            print("⚠️ 成本上限已达，终止会话")
            break
```

**Effort 级别**（v0.1.74+）: `low / medium / high / max / xhigh`
- `xhigh` 仅 Opus 4.7 支持，自动降级其他模型

**关键配置汇总**（生产必读）:
| 配置 | 值 | 说明 |
|------|-----|------|
| `permission_mode` | `"fallback"` | 生产必须，禁止 acceptEdits |
| `strict_mcp_config` | `True` | 多租户隔离，忽略全局 MCP 配置 |
| `max_turns` | `50` | 防止无限循环 |
| `session_store_flush` | `"eager"` | 直播 UI；"batched"（默认）适合批量 |
| `mcp` | `>=1.23.0` | 修复 DNS rebinding CVE |

## 参考项目（15+ 已验证案例）

| 项目 | GitHub | Skill 映射 |
|------|--------|-----------|
| 财经图表 | claudesdk-financial-chart-chat | 财务数据分析 + 6种图表 |
| 股票研究 | claudesdk-stock-chat | 7个投资研究 Skill，8阶段尽调 |
| TikHub 对话 | claudesdk-tikhub-chat | TikHub API Skill |
| 社交媒体 | claudesdk-social-chat | 14平台社媒数据 Skill |
| 深度研究 | claudesdk-research-chat | 5个并行研究 Skill |
| 电商分析 | claudesdk-amazon-chat | 竞品穿透分析 Skill |
| 数据分析 | claudesdk-data-chat | 19个数据分析 Skill |

> 来源: github.com/liangdabiao/（全部开源）

## When Done

验收标准:
- ✅ 浏览器打开 `http://localhost:8000` 能对话
- ✅ Agent 正确调用 Skill 定义的工具
- ✅ 图表/文件生成后可预览/下载
- ✅ WebSocket 实时显示执行日志
- ✅ 文件上传能触发图表生成
- ✅ Docker 构建成功并运行

## What NOT

- ❌ 禁止在 `allowed_tools` 中包含未验证的工具
- ❌ 禁止将 `permission_mode="acceptEdits"` 用于对外服务
- ❌ 禁止跳过 Tool Hook 审计直接部署
- ❌ 禁止在 Web 层暴露 Claude Code 的全部内置工具（按需白名单）
- ❌ 禁止依赖 Hook 实现顺序逻辑（同一事件的所有 Hook **并行**触发）
- ❌ 禁止在 requirements.txt 中使用 `mcp<1.23.0`（CVE-2025-66416 未修复）

## SDK 版本与能力对照

| 能力 | 最低版本 | 来源 |
|------|---------|------|
| `@tool` + `create_sdk_mcp_server()` | v0.1.x | 基础能力 |
| SessionStore（PostgreSQL/Redis/S3） | v0.1.x | session_store 模块 |
| `strict_mcp_config` | v0.1.74+ | 多租户隔离必需 |
| `session_store_flush="eager"` | v0.1.74+ | 实时直播 UI |
| Effort 级别（xhigh 等） | v0.1.74+ | 成本控制 |
| Subagent 追踪 Hook | v0.1.74+ | 6 种 Hook 事件类型 |
| MCP CVE 修复（GHSA-9h52-p55h-vw2f） | v0.2.82+ | mcp>=1.23.0 |
| Workload Identity Federation | v0.2.87+ | CI/CD 无密钥认证 |

> 查看最新版本: `pip index versions claude-agent-sdk` 或 GitHub releases

## 关键资源

- SDK 文档: platform.claude.com/docs/en/agent-sdk
- Python SDK: pypi.org/project/claude-agent-sdk
- TypeScript SDK: npmjs.com/package/@anthropic-ai/claude-agent-sdk
- 安全部署: docs.anthropic.com - Securely deploying AI agents
- 开源参考: github.com/anthropic/claude-agent-sdk-demos
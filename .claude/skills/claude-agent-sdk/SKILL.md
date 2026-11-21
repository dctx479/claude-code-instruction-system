---
name: claude-agent-sdk
description: 将任何 Skill 封装为 Claude Agent SDK Web 应用的五步法，包含项目架构、代码模板、安全部署、SessionStore 会话持久化和 Multi-Agent 子 Agent 编排
metadata:
  type: skill
  version: v1.1
  date: 2026-05-25
  trigger:
  - 用 claude-agent-sdk 建立 webapp
  - 把 skill 转为 web 应用
  - 构建 claude agent sdk 项目
  - claude-agent-sdk web
  - agent sdk 项目
  集成:
  - skill-creator
  - sdd-riper
  - code-security-review
  来源: liangdabiao/claudesdk-skill (开源实验项目)
disable-model-invocation: true
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


## Extended procedure

Read [references/extended-guide.md](references/extended-guide.md) for the remaining modes, examples, and checks. Resource paths in that guide are relative to this skill directory.

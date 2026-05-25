# Agent 公开部署安全指南

> 本文档是 `claude-agent-sdk` Skill 的部署安全补充，聚焦于将 Claude Agent SDK Web 应用对外提供服务时的安全加固。

## 威胁模型

公开部署的 Agent 面临三类主要威胁：

| 威胁类型 | 攻击向量 | 后果 |
|---------|---------|------|
| **Prompt 注入** | 用户输入嵌入恶意指令 | Agent 执行非预期操作 |
| **工具滥用** | 构造恶意工具调用 | 文件破坏/数据泄露 |
| **资源耗尽** | 恶意消耗 Token/计算资源 | 服务不可用/成本爆炸 |

## 五层防御方案

### L1: 权限隔离（Permission Mode）

```python
# 开发/测试: acceptEdits（自动批准所有操作）
# 对外服务: fallback（每次需要确认）
ClaudeAgentOptions(
    permission_mode="fallback",  # 生产必须
    max_turns=50                 # 防止无限循环
)
```

> 参考: Anthropic 官方文档 - [Securely deploying AI agents](https://docs.anthropic.com/en/docs/agents-sdk/security)

### L2: 工具白名单 + 黑名单

```python
ClaudeAgentOptions(
    # 只暴露必要工具（最小权限原则）
    allowed_tools=[
        # 业务工具（已注册 MCP Server）
        "mcp__my-tools__search",
        "mcp__my-tools__generate_chart",
        # 内置工具（严格限制）
        "Read",        # ✅ 允许读文件
        "Bash",        # ⚠️ 仅在白名单内允许
        "Glob", "Grep" # ✅ 允许
    ],
    # 主动禁止危险工具
    disallowed_tools=[
        "Write",       # ❌ 对外服务禁止写入
        "Edit",        # ❌ 禁止修改文件
        "rm", "format" # ❌ 禁止删除/格式化命令
    ]
)
```

### L3: Hooks 审计

```python
from claude_agent_sdk import HookMatcher

async def audit_bash(input_data, tool_use_id, context):
    """所有 Bash 命令必须记录"""
    command = input_data.get("tool_input", {}).get("command", "")
    print(f"[AUDIT] Bash: {command}")
    return {}  # 允许执行但必须记录

async def block_dangerous(input_data, tool_use_id, context):
    """阻止危险操作"""
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
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[audit_bash, block_dangerous]),
        ]
    }
)
```

### L4: Docker 沙箱隔离

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install claude-agent-sdk fastapi uvicorn
COPY app.py ./
RUN useradd -m appuser
# 只读文件系统
RUN chmod -R 555 /app
USER appuser
# 无 root 权限
CMD ["uvicorn", "server:app", "--host", "0.0.0.0"]
```

**容器运行约束**:
- 不挂载宿主机的 `/` 或敏感目录
- 只暴露必要端口（Web 服务端口）
- 设置内存和 CPU 限制
- 不使用 `--privileged` 模式

### L5: LlamaFirewall 护栏（生产级）

三层护栏：

| 层级 | 防护内容 | 实现方式 |
|-----|---------|---------|
| **输入层** | Prompt 注入检测 | LlamaFirewall 输入过滤器 |
| **输出层** | 内容安全过滤 | LlamaFirewall 输出过滤器 |
| **工具层** | 工具访问控制 | 细粒度权限 + 审计日志 |

```python
# LlamaFirewall 集成示例
from llamafirewall import AgentShield

shield = AgentShield(
    input_policy=["block_injection", "block_system_prompt_override"],
    output_policy=["block_sensitive_data", "block harmful_content"],
    tool_policy=["allow_readonly", "deny_write", "audit_all"]
)

async def safe_query(prompt, options):
    # 输入过滤
    cleaned = shield.sanitize_input(prompt)
    # Agent 执行
    result = await agent.query(cleaned, options)
    # 输出过滤
    return shield.sanitize_output(result)
```

## API 网关安全

### 认证与限流

```python
# FastAPI 认证示例
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
import time

app = FastAPI()
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_key(key: str = Depends(api_key_header)):
    if not validate_api_key(key):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return key

@app.post("/agent/run")
async def run_agent(request: dict, _: str = Depends(verify_key)):
    # 实现限流
    user_id = get_user_from_key(_)
    if rate_limiter.is_exceeded(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    # ...
```

### 成本控制

```python
# 每次模型调用前检查预算
COST_CAP_USD = 0.50  # 每会话上限

async def check_budget(accumulated_cost: float) -> bool:
    if accumulated_cost >= COST_CAP_USD:
        await agent.cleanup()
        return False
    return True

# Agent SDK 计费通知
async for msg in query(prompt, options):
    # 监控成本
    if msg.type == "usage":
        accumulated_cost += msg.cost
        if not await check_budget(accumulated_cost):
            yield "⚠️ 成本上限已达，本次对话结束。"
            break
```

## 部署检查清单

### 上线前必检项

```
[ ] permission_mode 设置为 fallback（不是 acceptEdits）
[ ] allowed_tools 已裁剪到最小权限集
[ ] 所有 Bash 工具调用已注册 Hook 审计
[ ] Docker 容器使用非 root 用户
[ ] API 认证已启用（API Key / JWT / OAuth）
[ ] 限流规则已配置
[ ] 成本上限已设置
[ ] 日志已持久化（审计追踪）
[ ] LlamaFirewall 已集成（生产环境）
[ ] 安全测试已通过（Apex 红队测试）
```

### 监控告警

| 指标 | 告警阈值 | 动作 |
|-----|---------|------|
| 每分钟请求数 | > 100/min | 触发限流 |
| 单次会话 Token 消耗 | > 10,000 | 检查是否异常 |
| 成本累积 | > $5/小时 | 自动终止会话 |
| 危险工具调用 | > 0 次 | 即时告警 + 自动封禁 |

## 相关资源

- [Anthropic: Securely deploying AI agents](https://docs.anthropic.com/en/docs/agents-sdk/security)
- [Claude Agent SDK - Hosting](https://platform.anthropic.com/docs/en/agent-sdk/hosting)
- [LlamaFirewall](https://llamafirewall.ai) - Agent 安全护栏
- [Apex AI Red Team](https://apex.ai) - Agent 红队测试服务

---

## 已知缺口（待完善）

### 缺口 1: MCP Server 安全

当前 L1-L5 框架缺少 MCP Server 级别的安全加固。MCP 工具的安全性依赖 Server 实现本身：

| 风险 | 说明 | 缓解措施 |
|-----|------|---------|
| **参数注入** | MCP 工具参数未校验，可注入恶意 payload | 每个 MCP 工具入口增加输入验证 |
| **跨租户数据泄露** | 共享 MCP Server 的不同租户可能互相访问数据 | MCP Server 按租户隔离或使用 namespace |
| **MCP over HTTP** | HTTP 传输相比 stdio 有更大攻击面 | 仅暴露必要端点，mTLS 加密 |

> Anthropic 官方 MCP 安全文档尚不完整，此为当前最大的已知盲区。

### 缺口 2: 多租户隔离

| 场景 | 风险 | 状态 |
|-----|------|------|
| 多个用户共享同一 Agent 实例 | 用户 A 的对话历史被用户 B 读取 | **无文档** |
| 跨用户的 MCP 工具可见性 | 某租户的工具泄露给其他租户 | **无文档** |
| 成本分摊 | 如何在多租户间公平计费 | **无文档** — 只有 per-session cap |

> 建议：当前对外服务至少每个会话创建独立 Agent 实例，避免共享状态。

### 缺口 3: Red-team 测试协议

当前只有部署检查清单，缺少正式的红队测试流程。建议覆盖：

- [ ] 模拟 Prompt 注入攻击（直接/间接/上下文填充）
- [ ] 测试 PreToolUse Hook 的阻断效果
- [ ] 成本上限触发后的会话终止行为
- [ ] MCP 工具参数注入测试
- [ ] 多租户数据隔离验证

> 参考: Apex AI Red Team (apex.ai) 提供商业化 Agent 红队测试服务。
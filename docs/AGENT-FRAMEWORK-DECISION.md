# Agent 框架决策指南

> 本文档为 `claude-agent-sdk` Skill 的框架层补充，指导如何根据场景选择正确的 Agent 框架，以及如何将 Claude Code Skills 集成到不同框架中。
> 核心判断：Claude Code 本身即是一个编排平台，与 LangChain/CrewAI/DeerFlow 是同层次设计。

---

## 一、框架定位对比

| 框架 | 定位 | 核心抽象 | 适用场景 |
|------|------|---------|---------|
| **Claude Code / Agent SDK** | **终端原生 / 程序化嵌入** | Agent = Markdown + Intent 路由，Skill = 可复用单元 | 开发者工具链、IDE 集成、Skill→SaaS |
| **LangGraph** | **生产级状态机** | 有向图 = 节点(Agent) + 边(消息流) + 检查点 | 有循环/容错/人机升级的长时工作流 |
| **CrewAI** | **快速原型** | Role-based Agent + Crew（sequential/hierarchical） | 非工程师快速搭建多角色工作流 |
| **DeerFlow**（字节） | **深度研究流水线** | 模块化：研究+搜索+爬虫→LLM | 自动化网页研究和报告生成 |

**关键洞察**：Claude Code 的 Skills 系统和 Auto-Dispatch 协议，在设计哲学上与 LangGraph 的状态机、CrewAI 的 Crew 是对等的。太一元系统的 Orchestrator 编排策略（PARALLEL/SEQUENTIAL/HIERARCHICAL 等）映射到 LangGraph 就是图的边类型。

---

## 二、决策树

```
任务类型是什么？
│
├─ 需要将 Skill 对外开放为 Web SaaS？
│   └─ ✅ Claude Agent SDK（五步法，详见 claude-agent-sdk SKILL.md）
│
├─ 需要 IDE / 文件系统 / Git 操作能力？
│   └─ ✅ Claude Code / Agent SDK
│
├─ 需要显式循环 + 检查点 + 人机升级？
│   └─ ✅ LangGraph
│
├─ 非工程师，需要快速原型多角色工作流？
│   └─ ✅ CrewAI
│
├─ 需要自动化深度网页研究流水线？
│   └─ ✅ DeerFlow
│
└─ 需要 Claude Code 的 Skill + LangGraph 的循环支持？
    └─ ✅ Claude Agent SDK 作为 LangGraph 节点（混合架构）
```

---

## 三、Skill → SaaS 完整路径图

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Skill 层（Claude Code）                          │
│  .claude/skills/<name>/SKILL.md                                     │
│  What / How / When Done / What NOT + Extractable 第五要素           │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                    Extractable = true?
                           │
          ┌────────────────┴────────────────┐
          ▼                                 ▼
     ✅ 可直接转换                        ❌ 需要重构
  ┌─────────────────┐                ┌─────────────────┐
  │ JSON 序列化     │                │ 增加包装层      │
  │ 无隐式上下文依赖  │                │ 显式会话管理     │
  │ 逻辑可独立运行   │                │ 拆分依赖        │
  └────────┬────────┘                └─────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│           Claude Agent SDK 五步法（claude-agent-sdk SKILL.md）        │
│                                                                     │
│  Step 1: 环境准备 → pip install claude-agent-sdk                   │
│  Step 2: Skill 分析 → 工具接口映射（@tool 装饰器）                  │
│  Step 3: Agent 核心代码 → MCP Server + ClaudeSDKClient               │
│  Step 3.5: SessionStore → PostgreSQL/Redis/S3（多租户）              │
│  Step 3.6: Multi-Agent → AgentDefinition 子 Agent                     │
│  Step 4: Web 服务层 → FastAPI + WebSocket                          │
│  Step 5: 端到端测试 + Docker 部署                                     │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                    并发上线？
                           │
          ┌────────────────┴────────────────┐
          ▼                                 ▼
     内部使用                          对外服务
  acceptEdits ✅                     fallback ⚠️
  单实例即可                         strict_mcp_config=True
                                   LlamaFirewall
                                   限流 + 成本上限
```

---

## 四、LangGraph 集成模式

Claude Agent SDK 作为 LangGraph 节点，享有 LangGraph 的循环支持和检查点，同时保持 Claude Code 的文件系统操作：

```python
from langgraph.graph import StateGraph
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

# Claude Agent SDK 节点包装
def claude_node(state):
    client = ClaudeSDKClient(options=ClaudeAgentOptions(...))
    result = client.query(state["user_prompt"])
    return {"result": result}

# LangGraph 编排循环和检查点
graph = StateGraph()
graph.add_node("claude", claude_node)
graph.add_node("review", review_node)
# 支持显式循环（LangGraph 独有）
graph.add_edge("review", "claude", condition=lambda s: s["needs_revision"])
```

---

## 五、生产部署能力矩阵

| 能力 | Claude Agent SDK | LangGraph | CrewAI | DeerFlow |
|------|-----------------|-----------|--------|----------|
| **工具调用** | 内置 Read/Write/Bash/Grep 等 | 需手动定义 | 内置 + 自定义 | 内置 + 搜索 |
| **会话持久化** | ✅ SessionStore (PG/Redis/S3) | ✅ LangGraph Memory | ✅ Crew 记忆 | ✅ 内置 |
| **多 Agent 编排** | ✅ AgentDefinition | ✅ 图形拓扑 | ✅ Crew 进程 | ✅ 流水线 |
| **显式循环** | ❌ | ✅ | ❌ | ❌ |
| **检查点容错** | ❌ | ✅ | ❌ | ❌ |
| **人机交互** | ❌ | ✅ | ❌ | ❌ |
| **Skill 系统** | ✅（核心优势） | ❌ | ❌ | ❌ |
| **Docker 部署** | ✅（自带 CLI） | ✅ | ✅ | ✅ |
| **Webhook 触发** | ✅ | ✅ | ✅ | ✅ |
| **成本控制** | ✅ max_budget_usd | ⚠️ | ⚠️ | ⚠️ |
| **多租户隔离** | ✅ strict_mcp_config | ⚠️ | ⚠️ | ⚠️ |
| **社区规模** | 7K Stars | 137K Stars | 52K Stars | 69K Stars |

---

## 六、编排策略映射

| 太一元编排策略 | 对应框架实现 |
|---------------|------------|
| **PARALLEL** | LangGraph fan-out / CrewAI 并行 / Agent SDK 并发 Subagent |
| **SEQUENTIAL** | LangGraph 顺序边 / CrewAI Process.sequential |
| **HIERARCHICAL** | CrewAI Process.hierarchical / Agent SDK Lead+Subagent |
| **COLLABORATIVE** | LangGraph 条件分支 / Agent SDK 多 Specialist |
| **COMPETITIVE** | LangGraph 条件分支 + 评分 / Agent SDK 并行评估 |
| **SWARM** | 多 ClaudeSDKClient 并发 + Worktree 隔离 |
| **SDD-RIPER** | Agent SDK Lead（Spec→Review）+ Subagent（Execute） |

---

## 七、框架选择决策速查

| 你的需求 | 推荐方案 |
|---------|---------|
| 把 Claude Code Skill 对外开放成 Web SaaS | **Claude Agent SDK**（`claude-agent-sdk` Skill，五步法） |
| 构建有循环和容错的生产级工作流 | **LangGraph** |
| 让非工程师也能快速搭建多角色 AI 应用 | **CrewAI** |
| 自动化深度网页研究和报告生成 | **DeerFlow** |
| 开发者工具链 + 文件系统操作 | **Claude Code CLI** |
| Claude Code 能力 + LangGraph 循环 | **Claude Agent SDK + LangGraph**（混合架构） |
| 需要 IDE 上下文感知的多 Agent 推理 | **Claude Code + Agent SDK**（原生） |
| 对比多个技术方案并选最优 | **parallel-explore Skill**（Worktree 并行） |

---

## 八、相关资源

- **claude-agent-sdk Skill**: `.claude/skills/claude-agent-sdk/SKILL.md`
- **SDK 生态调研报告**: `docs/reports/CLAUDE-AGENT-SDK-ECOSYSTEM-2026.md`
- **Agent 部署安全**: `docs/agent-deployment/SECURITY-GUIDE.md`
- **编排指南**: `docs/ORCHESTRATION-GUIDE.md`
- **MCP 配置**: `docs/mcp-configuration-guide.md`
- **太一元编排模式**: `workflows/orchestration/orchestration-patterns.md`
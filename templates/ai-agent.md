# CLAUDE.md - AI智能体开发专用模板

## 项目概述
本项目用于开发基于大语言模型的智能体系统。

## 技术架构

### 核心框架
- **Agent 框架**: LangChain / LlamaIndex / AutoGen
- **模型接口**: OpenAI API / Anthropic API / 本地模型
- **向量数据库**: Pinecone / Weaviate / ChromaDB / Milvus
- **编排工具**: Claude Code / LangGraph / CrewAI

### 关键组件
```
agents/
├── core/
│   ├── base_agent.py         # 基础智能体类
│   ├── memory.py             # 记忆管理
│   ├── tools.py              # 工具定义
│   └── prompts.py            # 提示词模板
├── specialized/
│   ├── researcher.py         # 研究型智能体
│   ├── coder.py              # 编程智能体
│   ├── analyst.py            # 分析智能体
│   └── orchestrator.py       # 编排智能体
├── mcp/
│   ├── servers/              # MCP 服务器
│   └── tools/                # MCP 工具
└── workflows/
    ├── pipelines.py          # 工作流管道
    └── chains.py             # 链式调用
```

## 核心命令

```bash
# 开发
python -m agents.main                    # 启动智能体
python -m agents.server                  # 启动 MCP 服务器

# 测试
pytest tests/                            # 运行测试
pytest tests/ -v --cov=agents           # 覆盖率测试

# 工具
python scripts/eval.py                   # 评估智能体
python scripts/benchmark.py              # 性能基准测试
```

## 智能体设计模式

### 1. ReAct (Reasoning + Acting)
```python
# 思考-行动-观察循环
class ReActAgent:
    def run(self, task: str) -> str:
        while not done:
            thought = self.think(observation)
            action = self.act(thought)
            observation = self.observe(action)
        return self.synthesize()
```

### 2. Plan-and-Execute
```python
# 先规划后执行
class PlanExecuteAgent:
    def run(self, task: str) -> str:
        plan = self.planner.create_plan(task)
        for step in plan:
            result = self.executor.execute(step)
            self.update_plan(result)
        return self.synthesize_results()
```

### 3. 多智能体协作
```python
# 角色分工协作
class MultiAgentSystem:
    def __init__(self):
        self.researcher = ResearchAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()
        self.orchestrator = OrchestratorAgent()

    def run(self, task: str) -> str:
        research = self.researcher.run(task)
        analysis = self.analyst.run(research)
        report = self.writer.run(analysis)
        return self.orchestrator.review(report)
```

## 提示词工程

### 系统提示词模板
```python
SYSTEM_PROMPT = """
你是一个专业的 {role}。

## 能力
{capabilities}

## 约束
{constraints}

## 输出格式
{output_format}

## 工具
你可以使用以下工具:
{tools}
"""
```

### 思维链提示
```python
COT_PROMPT = """
让我们一步步思考:

1. 首先,我需要理解问题的核心...
2. 然后,我需要收集必要的信息...
3. 接下来,我将分析这些信息...
4. 最后,我将给出结论...
"""
```

### 少样本学习
```python
FEW_SHOT_PROMPT = """
以下是一些例子:

输入: {example_input_1}
输出: {example_output_1}

输入: {example_input_2}
输出: {example_output_2}

现在处理:
输入: {actual_input}
输出:
"""
```

## 工具开发

### MCP 工具定义
```typescript
// mcp-server/tools/example.ts
export const exampleTool: Tool = {
  name: "example_tool",
  description: "描述工具的功能",
  inputSchema: {
    type: "object",
    properties: {
      param1: { type: "string", description: "参数1说明" },
      param2: { type: "number", description: "参数2说明" }
    },
    required: ["param1"]
  },
  handler: async (input) => {
    // 工具实现
    return { result: "output" };
  }
};
```

### 自定义工具 (Python)
```python
from langchain.tools import BaseTool
from pydantic import Field

class CustomTool(BaseTool):
    name: str = "custom_tool"
    description: str = "工具描述"

    def _run(self, query: str) -> str:
        # 实现逻辑
        return result

    async def _arun(self, query: str) -> str:
        # 异步实现
        return await self._run_async(query)
```

## 记忆系统

### 短期记忆
```python
class ConversationMemory:
    """对话历史记忆"""
    def __init__(self, max_turns: int = 10):
        self.messages = []
        self.max_turns = max_turns

    def add(self, message: Message):
        self.messages.append(message)
        if len(self.messages) > self.max_turns * 2:
            self.messages = self.messages[-self.max_turns * 2:]
```

### 长期记忆 (向量数据库)
```python
class VectorMemory:
    """基于向量检索的长期记忆"""
    def __init__(self, embedding_model, vector_store):
        self.embedder = embedding_model
        self.store = vector_store

    def save(self, text: str, metadata: dict):
        embedding = self.embedder.embed(text)
        self.store.upsert(embedding, metadata)

    def recall(self, query: str, k: int = 5) -> List[str]:
        embedding = self.embedder.embed(query)
        return self.store.query(embedding, top_k=k)
```

## 评估框架

### 评估指标
```python
class AgentEvaluator:
    def evaluate(self, agent, test_cases):
        results = {
            "accuracy": 0,      # 任务完成准确率
            "efficiency": 0,    # 步骤效率
            "cost": 0,          # Token 消耗
            "latency": 0,       # 响应延迟
            "safety": 0,        # 安全性评分
        }
        # 执行评估...
        return results
```

### 基准测试
```python
BENCHMARKS = [
    "GSM8K",        # 数学推理
    "HumanEval",    # 代码生成
    "MMLU",         # 多领域知识
    "AgentBench",   # 智能体能力
]
```

## 安全与对齐

### 输入过滤
```python
class InputFilter:
    def __init__(self):
        self.blacklist = load_blacklist()
        self.jailbreak_detector = JailbreakDetector()

    def filter(self, input: str) -> str:
        if self.jailbreak_detector.detect(input):
            raise SecurityException("检测到越狱尝试")
        return sanitize(input)
```

### 输出审核
```python
class OutputModerator:
    def moderate(self, output: str) -> str:
        # 检查有害内容
        # 检查敏感信息泄露
        # 验证输出格式
        return validated_output
```

## 调试与监控

### 日志配置
```python
import structlog

logger = structlog.get_logger()

# 记录智能体决策
logger.info("agent_decision",
    thought=thought,
    action=action,
    observation=observation
)
```

### 追踪
```python
from langsmith import traceable

@traceable(name="agent_run")
def run_agent(task: str):
    # 自动追踪执行过程
    pass
```

## 部署配置

### Docker 部署
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "agents.server"]
```

### 环境变量
```bash
# .env.example
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-xxx
VECTOR_DB_URL=http://localhost:6333
LOG_LEVEL=INFO
```

## 自主决策授权

✅ 可自主执行:
- 优化提示词模板
- 改进工具实现
- 添加错误处理
- 优化性能
- 编写测试用例

❌ 需要确认:
- 修改核心智能体架构
- 更换基础模型
- 修改安全策略
- 添加新的外部服务连接
- 修改记忆系统结构

## 最佳实践

1. **模块化设计**: 将智能体拆分为可复用的组件
2. **提示词版本控制**: 跟踪提示词变更历史
3. **渐进式复杂度**: 从简单智能体开始迭代
4. **充分测试**: 覆盖边界情况和对抗样本
5. **监控成本**: 跟踪 Token 消耗和 API 调用
6. **安全优先**: 始终验证输入输出

创建一个新的智能体: $ARGUMENTS

## 智能体设计流程

### 1. 需求分析
- 智能体名称和用途
- 核心能力
- 输入输出定义
- 约束条件

### 2. 系统提示词设计

```markdown
你是一个 [角色名称]，专注于 [核心职责]。

## 能力
- [能力 1]
- [能力 2]
- [能力 3]

## 约束
- [约束 1]
- [约束 2]

## 工具
你可以使用以下工具:
- [工具 1]: [描述]
- [工具 2]: [描述]

## 输出格式
[定义输出格式]
```

### 3. 工具定义

```python
from langchain.tools import BaseTool

class CustomTool(BaseTool):
    name = "tool_name"
    description = "工具描述"

    def _run(self, query: str) -> str:
        # 实现逻辑
        return result
```

### 4. 智能体实现

```python
from langchain.agents import AgentExecutor
from langchain.prompts import ChatPromptTemplate

# 创建提示词
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
    ("ai", "{agent_scratchpad}")
])

# 创建智能体
agent = create_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)
```

### 5. 测试验证

```python
# 测试用例
test_cases = [
    {"input": "测试输入1", "expected": "预期输出1"},
    {"input": "测试输入2", "expected": "预期输出2"},
]

for case in test_cases:
    result = agent_executor.invoke({"input": case["input"]})
    assert_quality(result, case["expected"])
```

## 输出

### 智能体定义文件
[生成的智能体代码]

### 系统提示词
[优化的提示词]

### 工具清单
[需要的工具列表]

### 使用示例
[如何使用这个智能体]

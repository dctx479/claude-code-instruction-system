# Intent Matcher 工作流

> 智能意图识别与任务路由系统

## 概述

Intent Matcher 负责分析用户输入，识别意图，并自动路由到合适的 Agent 和 Skill。

## 架构

```
用户输入
    │
    ▼
┌─────────────────┐
│ Intent Detector │
│ Hook            │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Keyword Matcher │◄──── config/keywords.json
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Pattern Analyzer│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Intent Router   │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│ Agent │ │ Skill │
└───────┘ └───────┘
```

## 核心组件

### 1. Keyword Matcher

基于关键词的快速匹配:

```json
{
  "debug": {
    "keywords": ["debug", "调试", "bug", "错误"],
    "agent": "debugger",
    "priority": "high"
  }
}
```

匹配算法:
1. 将用户输入转为小写
2. 检查是否包含任一关键词
3. 计算匹配得分
4. 返回最高得分的意图

### 2. Pattern Analyzer

基于正则表达式的模式分析:

```json
{
  "question": {
    "regex": "^(what|how|why|是什么|怎么|为什么)",
    "boost": 0.5
  },
  "command": {
    "regex": "^(create|delete|fix|创建|删除|修复)",
    "boost": 0.8
  }
}
```

### 3. Intent Router

路由决策逻辑:

```python
def route_intent(intent):
    config = load_keywords_config()

    # 获取意图配置
    intent_config = config["intents"].get(intent, config["fallback"])

    # 推荐 Agent
    agent = intent_config["agent"]

    # 推荐 Skills
    skills = intent_config["skills"]

    # 设置环境变量
    set_env("CLAUDE_INTENT", intent)
    set_env("CLAUDE_RECOMMENDED_AGENT", agent)
    set_env("CLAUDE_RECOMMENDED_SKILL", ",".join(skills))

    return agent, skills
```

## 意图类型

| 意图 | 关键词示例 | Agent | Skills |
|------|-----------|-------|--------|
| debug | debug, bug, 错误 | debugger | - |
| review | review, 审查 | code-reviewer | - |
| test | test, 测试 | automated-testing | - |
| architect | 架构, design | architect | - |
| security | security, 漏洞 | security-analyst | - |
| data | sql, database | data-scientist | - |
| analysis | 分析, 统计 | data-analyst | pandas |
| ml | pytorch, model | deep-learning | pytorch |
| research | paper, 文献 | literature-manager | literature |
| document | 文档, spec | spec-writer | - |
| git | commit, pr | orchestrator | - |
| deploy | deploy, docker | orchestrator | - |

## 优先级系统

意图有不同的优先级:

| 优先级 | 行为 | 示例意图 |
|--------|------|----------|
| high | 立即激活，覆盖默认 | debug, security, architect |
| medium | 正常激活 | review, test, data |
| low | 仅作为建议 | document |

## 匹配得分计算

```python
def calculate_score(message, intent_config):
    score = 0

    # 关键词匹配
    for keyword in intent_config["keywords"]:
        if keyword in message.lower():
            score += 1.0

    # 模式加成
    for pattern_name, pattern_config in patterns.items():
        if re.match(pattern_config["regex"], message):
            score *= (1 + pattern_config["boost"])

    # 优先级加成
    priority_boost = {"high": 1.5, "medium": 1.0, "low": 0.5}
    score *= priority_boost.get(intent_config["priority"], 1.0)

    return score
```

## 多意图处理

当检测到多个意图时:

```
输入: "请帮我审查这个代码并修复安全漏洞"

检测到:
- review (得分: 1.0)
- security (得分: 1.5)

决策:
- 主意图: security (最高分)
- 次要意图: review
- 建议: 先用 security-analyst 分析，然后用 code-reviewer 审查
```

## 上下文感知

Intent Matcher 会考虑上下文:

### 1. 会话历史
```
如果最近使用了 debugger:
- "继续" → 继续调试
- "下一个" → 下一个 bug
```

### 2. 当前任务
```
如果正在进行代码审查:
- "修复这个" → 在审查上下文中修复
```

### 3. 文件类型
```
如果当前文件是 .py:
- 优先推荐 Python 相关技能
```

## 集成点

### 与 Ralph 集成

Ralph 使用 Intent Matcher 来:
1. 理解任务意图
2. 选择执行策略
3. 检测完成条件

### 与 Model Router 集成

Intent 信息帮助 Model Router:
1. 评估任务复杂度
2. 选择合适的模型
3. 优化成本

### 与 HUD 集成

HUD 显示当前检测到的意图:
```
[10:30:15] Sonnet | @debugger | debug | [###.....] 30%
```

## 自定义扩展

### 添加新意图

1. 编辑 `config/keywords.json`:
```json
{
  "intents": {
    "my_intent": {
      "keywords": ["keyword1", "keyword2"],
      "agent": "my-agent",
      "skills": ["my-skill"],
      "priority": "medium"
    }
  }
}
```

2. 重启或重新加载配置

### 调整优先级

修改 `priority` 字段来调整意图的优先级。

### 添加自定义模式

在 `patterns` 部分添加新的正则表达式模式。

## 故障排除

### 意图误识别

检查关键词是否过于通用，考虑添加更具体的关键词。

### 意图未识别

1. 检查关键词拼写
2. 检查是否支持用户使用的语言
3. 添加新的关键词

### 性能问题

如果关键词太多导致性能下降:
1. 使用 trie 数据结构优化匹配
2. 使用编译后的正则表达式
3. 实现缓存机制

## 相关文档

- Hook 实现: `hooks/intent-detector.sh`
- 关键词配置: `config/keywords.json`
- Agent 索引: `agents/INDEX.md`

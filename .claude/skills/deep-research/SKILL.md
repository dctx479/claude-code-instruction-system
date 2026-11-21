---
name: deep-research
description: 深度研究技能，使用 Lead Agent + Subagent 架构并行执行多维度网络调研，自动生成带数据点的结构化报告
license: MIT
metadata:
  category: research
  tags:
  - research
  - web-search
  - analysis
  - report
  - parallel
  - reflection
  - citation-validation
  - synthesis
  - extension-protocol
  requires:
  - web_search
  - web_fetch
  optional:
  - playwright-mcp
  - tavily-mcp
  version: 1.2.0
  trigger:
  - /deep-research
  - 深度调研
  - 全面研究
  - 帮我研究一下
  - 需要深入了解
disable-model-invocation: true
---

# Deep Research Skill

## 契约定义

### What（输入/输出）

**输入**：
- 研究主题或问题（自然语言描述）
- 可选：研究深度偏好（快速/标准/深度）
- 可选：输出格式偏好（简报/报告/详尽分析）
- 可选：特定关注领域或排除领域
- 可选：创新发现目标（如研究方向探索、跨领域组合、方案 shortlist）

**输出**：
- 结构化 Markdown 研究报告
- 包含具体数据点（数字、日期、统计、百分比）
- 多角度分析（depth-first）或多子问题覆盖（breadth-first）
- 在创新模式下输出：已有发现 → 可迁移机制 → 组合假设 → 风险/验证点 → shortlist
- 保存为 `.md` 文件（默认路径：`reports/research-{topic}-{date}.md`）

### When Done（验收标准）

- 报告包含至少 5 个具体数据点（数字/日期/统计）
- 覆盖了主题的核心维度（根据查询类型）
- 所有事实性陈述有可追溯的来源基础
- 报告结构清晰（摘要 → 主体 → 结论）
- Lead Agent 完成了信息综合，而非简单拼接
- 文件已保存到指定路径

### What NOT（边界约束）

- **禁止编造数据**：所有数字必须来自搜索结果
- **禁止委托综合报告撰写**：Lead Agent 必须亲自撰写最终报告
- **禁止单一来源依赖**：重要事实需多来源交叉验证
- **禁止忽略矛盾信息**：发现矛盾时必须在报告中说明
- **禁止主对话污染**：所有搜索在隔离的 Task Agent 中执行
- **暂不添加引用标注**：当前版本不要求严格引用格式（后续可用 citations agent 补充）

---

## 何时使用此 Skill

当用户请求以下任务时自动激活：
- 调研某个主题/技术/市场/趋势
- 了解某事物的最新进展
- 对比分析多个选项
- 收集某领域的数据和统计
- 生成研究报告或调研报告
- 需要多角度、多来源的信息整合

**触发词示例**：
- "帮我调研一下..."
- "研究一下...的现状"
- "深入了解..."
- "收集...的相关信息"
- "对比分析...和..."
- "调查..."
- "综述..."
- "帮我找 10 个可验证的新方向"
- "把 A 和 B 组合成可落地的 idea"
- "从多篇论文里筛选靠谱的创新方案"

---

## 核心架构

### Lead Agent + Subagent 多轮反思模式

```
┌─────────────────────────────────────────────────────────────┐
│                    Lead Agent (主控)                         │
│  1. 生成研究简报（Research Brief）                           │
│  2. 多轮调度 Subagents，读取摘要后反思是否充分               │
│  3. 综合所有发现，撰写最终报告（不委托）                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
              ┌─────────▼─────────┐
              │  生成研究简报      │  ← 锁定意图边界
              └─────────┬─────────┘
                        │
              ┌─────────▼─────────┐          ┌──────────────────┐
         ┌───►│  本轮调查（Round N）│          │  发现已充分？      │
         │    └─────────┬─────────┘          │  ├─ 是 → 退出     │
         │              │ fan-out            │  └─ 否 → 继续     │
         │    ┌──────────┴──────────┐        └──────────────────┘
         │    ▼          ▼          ▼
         │ Subagent1  Subagent2  SubagentN    ← 独立上下文，ReAct
         │    │          │          │
         │    └──────────┴──────────┘
         │         压缩摘要返回
         │              │
         │    ┌─────────▼─────────┐
         └────┤  Lead Agent 反思   │  ← 还有空白？继续
              │  评估发现充分度    │
              └─────────┬─────────┘
                        │ 充分 / 达到 max_rounds
                        ▼
              ┌─────────────────┐
              │   综合撰写报告   │
              └─────────────────┘
```

**双层终止条件**（同 Ralph 设计哲学）：
- **质量驱动**：Lead Agent 判断发现已充分，主动退出循环
- **资源驱动**：达到 `max_rounds`（默认 3）强制退出，防止无限调查


## Extended procedure

Read [references/extended-guide.md](references/extended-guide.md) for the remaining modes, examples, and checks. Resource paths in that guide are relative to this skill directory.

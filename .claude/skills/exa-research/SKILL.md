---
name: exa-research
description: 企业与市场研究技能，基于 Exa 搜索引擎进行公司情报、竞争对手分析和市场研究，通过 Task Agent 隔离搜索并返回精炼结果
license: MIT
metadata:
  category: research
  tags:
  - exa
  - company-research
  - competitive-analysis
  - market-research
  - intelligence
  requires:
  - web_search_advanced
  mcp: exa-mcp
  version: 1.0.0
  trigger:
  - /exa-research
  - 企业调研
  - 竞品分析
  - 公司情报
  - 市场研究
disable-model-invocation: true
---

# Exa Research Skill

> 基于 Exa 搜索引擎的企业与市场研究工具，专注于公司情报、竞争对手分析和市场研究

## 契约定义

### What（输入/输出）

**输入**：
- 研究目标（公司名称、行业、市场问题）
- 研究类型（company/news/tweet/people）
- 结果数量偏好（可选："几个"/"全面"/具体数字）
- 输出格式偏好（JSON/Markdown 报告）

**输出**：
- 结构化的公司/市场情报
- 竞争分析报告（含定位矩阵）
- 市场研究报告（含数据点和趋势）
- 精炼后的 JSON 或 Markdown 格式结果

### When Done（验收标准）

- 所有搜索在隔离的 Task Agent 中执行
- 返回结果已精炼（非原始搜索结果）
- 公司信息包含：员工数、位置、融资、营收（如可用）
- 竞争分析包含至少 3 家竞品的对比
- 市场研究包含至少 5 个数据点
- 结果来源可追溯

### What NOT（边界约束）

- **禁止直接使用 web_search**：必须使用 `web_search_advanced`（Exa MCP）
- **禁止主对话执行搜索**：所有搜索必须通过 Task Agent 隔离
- **禁止返回原始结果**：必须精炼处理后返回
- **禁止编造数据**：所有数字必须来自搜索结果
- **禁止单一来源**：重要数据需多查询交叉验证

---

## 何时使用此 Skill

当用户请求以下任务时自动激活：
- 公司背景调查和情报收集
- 竞争对手分析和对比
- 市场趋势研究
- 行业动态追踪
- 投资标的调研
- 招聘前的公司调查
- 商业合作尽调

**触发词**：
- `/exa-research`
- "调研一下这家公司..."
- "竞品分析..."
- "市场研究..."
- "行业分析..."
- "公司情报..."
- "融资情况..."
- "竞争对手有哪些..."

---

## 核心架构

### 工具限制

**唯一允许的工具**: `web_search_advanced`（来自 Exa MCP）

```
主对话上下文
    │
    └─→ Task Agent (独立上下文)
            │
            ├─ web_search_advanced(query, category, num_results)
            │       ↓
            ├─ 精炼处理：提取关键信息
            │       ↓
            └─ 返回结构化结果 (JSON/Markdown)
```

### Token 隔离模式

**关键原则**：防止搜索结果污染主对话上下文

```
主对话
    │
    ├─→ Task Agent 1: 公司主页搜索
    │       └─ 返回: {company, employees, location, funding}
    │
    ├─→ Task Agent 2: 新闻搜索
    │       └─ 返回: [{title, date, summary}, ...]
    │
    ├─→ Task Agent 3: 社交媒体搜索
    │       └─ 返回: [{platform, content, engagement}, ...]
    │
    └─ 主对话仅接收精炼后的结构化数据
```

---


## Extended procedure

Read [references/extended-guide.md](references/extended-guide.md) for the remaining modes, examples, and checks. Resource paths in that guide are relative to this skill directory.

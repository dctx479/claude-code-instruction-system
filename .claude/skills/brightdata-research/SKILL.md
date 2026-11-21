---
name: brightdata-research
description: 电商平台深度调研技能，基于 Bright Data MCP 实现反反爬虫的电商市场情报收集，支持三种研究模式（Quick/Standard/Deep）
license: MIT
metadata:
  category: research
  tags:
  - ecommerce
  - research
  - market-intelligence
  - web-scraping
  - bright-data
  - mcp
  requires:
  - bright-data-mcp
  optional:
  - playwright-mcp
  version: 1.0.0
  trigger:
  - /brightdata-research
  - 电商市场调研
  - Bright Data 爬取
  - 竞品数据采集
  - 电商情报收集
disable-model-invocation: true
---

# Bright Data Research Skill

> 电商平台深度调研技能，专注于市场情报收集与竞品分析

## 契约定义

### What（输入/输出）

**输入**：
- 调研主题或产品类别（自然语言描述）
- 目标电商平台（Amazon, eBay, Etsy, Walmart, AliExpress 等）
- 可选：研究模式选择（Quick/Standard/Deep）
- 可选：输出格式偏好（Report/JSON/Markdown）
- 可选：特定关注维度（定价/竞品/趋势/评价等）

**输出**：
- 结构化电商调研报告
- 包含具体数据点（价格、销量、评分、排名）
- 市场洞察和竞争分析
- 保存为 `.md` 或 `.json` 文件（默认路径：`reports/ecommerce-{topic}-{date}.md`）

### When Done（验收标准）

- 报告包含至少 5 个具体数据点（价格/销量/评分等）
- 覆盖目标平台的核心产品数据
- 数据来源可追溯（平台、时间、URL）
- 报告结构清晰（摘要 -> 数据 -> 分析 -> 建议）
- 遵循道德爬虫规范（robots.txt、请求频率）
- 文件已保存到指定路径

### What NOT（边界约束）

- **禁止违反 robots.txt**：必须遵循目标网站的爬虫规则
- **禁止过度请求**：控制请求频率，避免对目标服务器造成压力
- **禁止编造数据**：所有数字必须来自实际抓取结果
- **禁止忽略大页面限制**：Amazon/Etsy 等大页面每批次 1-2 URLs
- **禁止单次处理过多 URLs**：避免 Token 超限（Quick <=5, Standard <=20）
- **禁止私有信息抓取**：不收集用户个人信息
- **必须注明数据来源**：所有数据需标注平台和抓取时间

---

## 何时使用此 Skill

当用户请求以下任务时自动激活：
- 电商平台市场调研
- 产品竞品分析
- 价格监控和对比
- 畅销排行分析
- 品牌市场份额研究
- 电商趋势洞察
- 跨平台产品对比

**触发词示例**：
- "帮我调研 Amazon 上的..."
- "分析淘宝/天猫的市场..."
- "电商调研..."
- "产品市场分析..."
- "竞品价格对比..."
- "畅销排行..."
- "跨境电商调研..."

---

## 三种研究模式

### Quick Mode（快速模式）

**特点**：
- URLs 数量：3-5 个
- 处理方式：顺序处理
- 适用场景：快速概览、初步探索
- 耗时：1-3 分钟

**使用场景**：
```markdown
# 快速了解某品类概况
"快速看一下 Amazon 上蓝牙耳机的价格区间"

# 单一产品信息
"帮我查一下这个 ASIN 的产品详情"
```

**执行流程**：
```
用户请求 -> 解析目标 -> 搜索发现 (1-2 queries)
    -> 顺序抓取 (3-5 URLs) -> 数据提取 -> 快速报告
```


## Extended procedure

Read [references/extended-guide.md](references/extended-guide.md) for the remaining modes, examples, and checks. Resource paths in that guide are relative to this skill directory.

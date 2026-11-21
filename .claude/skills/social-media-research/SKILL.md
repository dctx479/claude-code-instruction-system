---
name: social-media-research
description: 跨平台社交媒体数据研究技能，基于 TikHub MCP 实现 12+ 社媒平台数据采集、舆情监控、KOL 分析和内容趋势洞察
license: MIT
metadata:
  category: research
  tags:
  - social-media
  - research
  - tiktok
  - douyin
  - xiaohongshu
  - kol
  - sentiment
  - tikhub
  - mcp
  requires:
  - tikhub-mcp
  optional:
  - deep-research
  - market-insight
  - brightdata-research
  version: 1.0.0
  trigger:
  - /social-media-research
  - 社交媒体数据分析
  - KOL 分析
  - 舆情监控
  - TikTok 数据
  - 小红书数据
disable-model-invocation: true
---

# Social Media Research Skill

> 跨平台社交媒体数据研究技能，专注于品牌舆情监控、KOL 分析和内容趋势洞察

## 契约定义

### What（输入/输出）

**输入**：
- 研究主题或品牌/产品名称（自然语言描述）
- 目标平台（可多选）：TikTok, Douyin, Xiaohongshu, Bilibili, Kuaishou, Weibo, Instagram, YouTube, Twitter, Threads, Reddit, Zhihu 等
- 可选：研究类型（舆情监控/KOL 分析/内容趋势/竞品分析）
- 可选：时间范围（最近 7 天/30 天/自定义）
- 可选：输出格式（Report/Dashboard/JSON）

**输出**：
- 结构化社媒研究报告
- 包含具体数据点（互动量、粉丝数、增长率、情感倾向）
- 可视化数据洞察（趋势图表、词云、热度排名）
- 保存为 `.md` 文件（默认路径：`reports/social-media-{topic}-{date}.md`）

### When Done（验收标准）

- 报告包含至少 10 个具体数据点（互动量/粉丝数/发布量等）
- 覆盖至少 1 个目标平台的核心数据
- 数据来源可追溯（平台、账号、时间）
- 报告结构清晰（摘要 -> 数据 -> 分析 -> 建议）
- 情感分析结果（如适用）包含正面/中性/负面比例
- 文件已保存到指定路径

### What NOT（边界约束）

- **禁止编造数据**：所有数字必须来自 API 返回结果
- **禁止过度请求**：遵循 10 请求/秒/端点的限流规则
- **禁止私有信息采集**：不收集用户私信、隐私数据
- **禁止单次处理过多**：每次 API 调用控制在合理范围
- **禁止跳过错误处理**：API 失败时必须有重试和降级策略
- **禁止忽略时效性**：报告需注明数据采集时间
- **必须注明数据来源**：所有数据需标注平台和采集时间

---

## 何时使用此 Skill

当用户请求以下任务时自动激活：
- 社交媒体数据分析
- 品牌舆情监控
- KOL/网红识别与评估
- 内容趋势分析
- 社媒竞品分析
- 抖音/小红书/TikTok 数据调研
- 社交媒体营销策略制定
- 用户口碑分析

**触发词示例**：
- "帮我分析抖音上关于...的内容"
- "监控小红书上品牌...的舆情"
- "找出 TikTok 上...领域的头部 KOL"
- "分析 B 站上...话题的热度趋势"
- "调研微博上关于...的用户反馈"
- "社媒数据分析..."
- "KOL 挖掘..."
- "舆情报告..."

---

## 核心架构

### TikHub API 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    TikHub MCP Server                         │
│  - API 认证管理                                              │
│  - 请求限流控制 (10 req/s/endpoint)                         │
│  - 自动重试 (最多 3 次)                                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┬───────────────┐
        │               │               │               │
        ▼               ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  API Searcher │ │  API Client  │ │   OpenAPI    │ │  Batch Job   │
│  关键词发现   │ │  直接调用    │ │   规范文档   │ │  批量任务    │
│  端点         │ │  (内置认证)  │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

### API 端点格式

```
/api/v1/{platform}/{method}/{action}
```

**示例端点**：
- `/api/v1/tiktok/web/search_video` - TikTok 视频搜索
- `/api/v1/douyin/web/fetch_user_profile` - 抖音用户资料
- `/api/v1/xiaohongshu/web/search_notes` - 小红书笔记搜索
- `/api/v1/bilibili/web/fetch_video_info` - B站视频信息

---


## Extended procedure

Read [references/extended-guide.md](references/extended-guide.md) for the remaining modes, examples, and checks. Resource paths in that guide are relative to this skill directory.

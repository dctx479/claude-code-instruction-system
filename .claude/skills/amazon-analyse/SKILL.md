---
name: amazon-analyse
description: 亚马逊选品全维度分析工具集，基于 Sorftime MCP 获取官方数据，覆盖 Listing 穿透分析、关键词深度调研（2000+ 词库）、差评 6 维痛点分析
version: 1.1.0
license: MIT
metadata:
  category: research
  tags: [amazon, ecommerce, product-selection, competitor-analysis, sorftime, mcp, listing, keyword-research, review-analysis, pain-point]
  requires: [sorftime-mcp]
  source: https://github.com/liangdabiao/amazon-sorftime-research-MCP-skill
---

# Amazon Analyse Skill

> 亚马逊选品核心工具集，通过 Sorftime MCP 获取真实 Amazon 数据（非爬取），提供三大分析模块：Listing 穿透分析、关键词深度调研、差评痛点分析

## 三大分析模块概览

| 模块 | 命令 | 核心能力 | 输出目录 |
|------|------|---------|---------|
| **Listing 穿透分析** | `/amazon-analyse` | 六大维度全面分析 | `reports/` |
| **关键词深度调研** | `/keyword-research` | 2000+ 词库 + 分类 + 否定词 | `keyword-reports/` |
| **差评痛点分析** | `/review-analysis` | 6 维痛点框架 + 改进优先级 | `review-analysis-reports/` |

---

## 契约定义

### What（输入/输出）

**输入**：
- `ASIN`：亚马逊商品标准识别号（必填），如 `B07PWTJ4H1`
- `MARKETPLACE`：目标市场（必填），如 `US`、`DE`、`UK`、`JP`、`FR`、`IT`、`ES`、`CA`
- 可选：分析模块（listing/keywords/reviews，默认 listing）
- 可选：分析深度（Quick/Standard/Deep，默认 Standard）
- 可选：重点维度（仅 listing 模式：keywords/reviews/ranking/competition，默认全维度）

**输出**：
- **Listing 模式**：结构化穿透分析报告 → `reports/amazon-{ASIN}-{MARKETPLACE}-{date}.md`
- **关键词模式**：词库 + 分类 + 可视化 → `keyword-reports/{ASIN}_{Site}_{YYYYMMDD}/`
- **差评模式**：6 维痛点报告 → `review-analysis-reports/{ASIN}_{Site}_{YYYYMMDD}/`

### When Done（验收标准）

**Listing 分析**：
- 报告涵盖六大分析维度（每项有具体数据支撑）
- 关键词表包含流量来源 + 竞品布局
- 评论分析识别出 ≥3 个用户痛点和 ≥3 个优势聚类
- 提供可操作的选品/优化建议

**关键词调研**：
- 词库规模 ≥500（Standard）/ ≥2000（Deep）个关键词
- 每个关键词包含搜索量、CPC 数据
- 生成分类统计（核心词/长尾词/品牌词/否定词）
- 输出 CSV + 否定词 TXT + Dashboard HTML

**差评分析**：
- 采集 ≥50 条 1-3 星差评样本
- 6 维度痛点框架全覆盖（每个维度有占比和代表性评论原文）
- 输出改进优先级矩阵和产品改进建议

**通用**：
- 所有数据注明来源（Sorftime API + 时间戳）

### What NOT（边界约束）

- **禁止编造数据**：所有数字必须来自 Sorftime MCP 真实返回
- **禁止跨站爬取**：此 Skill 专用 Sorftime API，不调用 Bright Data 或直接抓取 Amazon
- **禁止忽略市场差异**：DE/JP 等市场的关键词必须用对应语言分析
- **禁止超出 ASIN 范围**：分析对象为指定 ASIN，不随意扩展到同类竞品（除非明确请求）
- **必须标注数据时效**：Sorftime 数据有时效性，报告必须注明获取时间
- **差评原文保留**：痛点分析中的代表性评论必须为用户原文，禁止改写

---

## 何时使用此 Skill

**触发命令**：
```bash
# Listing 穿透分析（原有）
/amazon-analyse <ASIN> <MARKETPLACE>
/amazon-analyse B07PWTJ4H1 US
/amazon-analyse B08N5WRWNW DE

# 关键词深度调研（v1.1 新增）
/keyword-research <ASIN> <MARKETPLACE>
/keyword-research B0D9ZTW7PS US
/keyword-research B0FMRTXKF6 US

# 差评痛点分析（v1.1 新增）
/review-analysis <ASIN> <MARKETPLACE>
/review-analysis B0CS9NP59F US
/review-analysis B09DT48V16 US
```

**自动激活场景**：
- 亚马逊 ASIN 分析请求
- 竞品 Listing 穿透分析
- 亚马逊选品决策支持
- 关键词流量来源分析 / 关键词调研 / 长尾词挖掘
- 评论痛点挖掘 / 差评分析 / 产品改进方向

---

## Sorftime MCP 配置

### 前置要求

1. **Sorftime 账户**：[申请地址](https://sorftime.com/zh-cn/mcp)
2. **API Key**：控制台获取
3. **MCP 配置**：添加到项目 `.mcp.json`

### MCP 配置示例

```json
{
  "mcpServers": {
    "sorftime": {
      "type": "streamableHttp",
      "url": "https://mcp.sorftime.com?key=YOUR_API_KEY",
      "name": "Sorftime MCP"
    }
  }
}
```

### 核心工具映射

| Sorftime 工具 | 用途 | 使用模块 |
|--------------|------|---------|
| `get_product_detail` | 产品基础信息 | Listing: 维度1 / Review: 产品信息 |
| `get_product_keywords` | 关键词流量数据 | Listing: 维度2 |
| `get_product_reviews` | 评论数据采集 | Listing: 维度3 / Review: 差评采集 |
| `get_product_rank_trend` | BSR 历史趋势 | Listing: 维度4 |
| `get_category_top` | 品类 Top 榜 | Listing: 维度5 |
| `get_keyword_competitors` | 关键词竞品布局 | Listing: 维度6 |
| `product_traffic_terms` | 产品流量关键词（50-200 个） | Keyword: Step 1 |
| `competitor_product_keywords` | 竞品布局关键词（100-500 个） | Keyword: Step 1 |
| `category_keywords` | 类目核心关键词（100-500 个） | Keyword: Step 1 |
| `keyword_related_words` | 长尾词扩展（每词 50-100 个） | Keyword: Step 2 |

---

## 模块 A：Listing 穿透分析

> 触发：`/amazon-analyse <ASIN> <MARKETPLACE>`

### 六大分析维度

#### 维度 1：产品详情

**数据点**：
- 标题、品牌、ASIN、价格（当前/历史区间）
- 主图、A+ 内容质量评估
- 变体数量、Listing 完整度评分
- FBA/FBM 状态、Prime 资质

**输出示例**：
```markdown
## 产品基础信息

| 字段 | 数值 |
|------|------|
| 品牌 | BrandName |
| 当前价格 | $79.99 |
| 历史价格区间 | $59.99 - $89.99 |
| BSR | #127 in Wireless Headphones |
| 评分 | 4.5 / 5.0 |
| 评价总数 | 12,847 |
| Listing 完整度 | 85% （A+ 内容：✅ 视频：✅ 变体：6个） |
```

#### 维度 2：关键词流量分析

**数据点**：
- 核心关键词 Top 20（搜索量 + 点击率）
- 流量来源拆解（自然 vs 广告）
- 长尾词机会（低竞争高相关）
- 竞品关键词布局重叠度

**输出示例**：
```markdown
## 关键词流量分析

### 核心关键词 Top 10

| 关键词 | 月搜索量 | 本品排名 | 竞品数 | 机会值 |
|--------|---------|---------|--------|--------|
| wireless earbuds | 2,450,000 | #8 | 1,200 | 中 |
| bluetooth earbuds | 1,800,000 | #15 | 980 | 中 |
| noise canceling earbuds | 650,000 | #3 | 420 | 高 |

### 长尾词机会

| 长尾词 | 月搜索量 | 当前排名 | 建议 |
|--------|---------|---------|------|
| wireless earbuds for small ears | 45,000 | 未入围 | 重点布局 |
```

#### 维度 3：评论情感分析

**数据点**：
- 好评聚类（Top 优势词）
- 差评聚类（Top 痛点词）
- 情感趋势（近 90 天评分走向）
- Q&A 高频问题识别

**输出示例**：
```markdown
## 评论情感分析

### 用户优势聚类（好评）

| 维度 | 频率 | 代表性表达 |
|------|------|-----------|
| 音质出色 | 68% | "amazing sound quality" |
| 续航强 | 54% | "battery lasts all day" |
| 佩戴舒适 | 47% | "so comfortable to wear" |

### 用户痛点聚类（差评）

| 问题 | 频率 | 代表性表达 | 改进优先级 |
|------|------|-----------|-----------|
| 降噪效果不稳定 | 31% | "ANC cuts out randomly" | 高 |
| 通话音质差 | 24% | "mic quality is terrible" | 高 |
| 充电盒做工粗糙 | 19% | "case feels cheap" | 中 |
```

#### 维度 4：销量排名趋势

**数据点**：
- BSR 历史曲线（近 12 个月）
- 季节性规律识别
- 排名峰谷分析（关联促销/节日）
- 月均销量估算

**输出示例**：
```markdown
## 销量排名趋势

### BSR 趋势（近 12 个月）

- 整体趋势：上升（12个月前 #380 → 当前 #127）
- 最佳排名：#89（黑五期间）
- 最差排名：#520（淡季）
- 月均销量估算：**3,200 - 4,500 件**

### 季节性规律

| 月份 | 销量指数 | 建议备货 |
|------|---------|---------|
| 10-12月 | 180% | 旺季，提前2个月备货 |
| 1-2月 | 90% | 平季 |
| 7-8月 | 75% | 淡季，控制库存 |
```

#### 维度 5：竞争格局分析

**数据点**：
- 品类 Top 20 竞品列表
- 价格带分布矩阵
- 品牌市场份额
- 新品涌入速度

#### 维度 6：市场机会识别

**数据点**：
- 需求未被满足的细分场景
- 竞品普遍缺失的功能点
- 关键词蓝海（高搜索 + 低竞争）
- 定价窗口（可差异化的价格带）

### 分析深度模式

| 模式 | 适用场景 | 数据调用 | 输出 |
|------|---------|---------|------|
| **Quick** | 快速了解竞品基本面 | `get_product_detail` + `get_product_keywords`（Top 10） | 产品摘要 + 核心关键词 |
| **Standard** | 选品决策前全面分析 | 六大维度全覆盖，关键词 Top 20 | 完整穿透报告 + 选品建议 |
| **Deep** | 新品类竞争格局深度摸底 | Standard + 品类 Top 50 + 关键词竞品布局矩阵 | 竞争全图 + 蓝海地图 + 入场策略 |

### Listing 报告模板

```markdown
# 亚马逊 Listing 穿透分析报告

> ASIN: {ASIN} | 市场: {MARKETPLACE} | 分析时间: {YYYY-MM-DD HH:mm}
> 数据来源: Sorftime MCP | 分析深度: {Quick/Standard/Deep}

---

## 执行摘要

**核心结论**（3 条）：
1. {最重要发现}
2. {第二重要发现}
3. {选品建议}

**综合评分**：{N}/5
- 市场规模: {N}/5 | 竞争强度: {N}/5 | 利润空间: {N}/5

---

## 一、产品详情
## 二、关键词流量分析
## 三、评论情感分析
## 四、销量排名趋势
## 五、竞争格局
## 六、市场机会

---

## 选品决策建议

### 入场理由
### 风险提示
### 差异化方向

---

**免责声明**：数据来源 Sorftime API，反映分析时刻市场状态，电商数据动态变化，建议结合最新实测数据决策。
生成时间：{时间戳} | Skill: amazon-analyse v1.1.0
```

---

## 模块 B：关键词深度调研

> 触发：`/keyword-research <ASIN> <MARKETPLACE>`

### 数据获取流水线

```
输入: ASIN + 站点 + (可选) 产品信息
  ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 1: 基础数据获取                                         │
├─────────────────────────────────────────────────────────────┤
│ 1. product_traffic_terms      → 产品流量关键词 (50-200个)   │
│ 2. competitor_product_keywords → 竞品布局关键词 (100-500个) │
│ 3. category_keywords           → 类目核心关键词 (100-500个) │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: 长尾词扩展                                          │
├─────────────────────────────────────────────────────────────┤
│ 从核心关键词中选择 Top 20-50 个                              │
│ → 对每个调用 keyword_related_words (50-100个延伸词)          │
│ → 预计获取 1,000-2,000 个长尾词                              │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: 数据清洗                                            │
├─────────────────────────────────────────────────────────────┤
│ 1. 去重（归一化：小写 + 去除特殊字符）                       │
│ 2. 过滤无效词（过短、非目标语言、乱码）                      │
│ 3. 合并搜索量/CPC 等指标                                    │
└─────────────────────────────────────────────────────────────┘
  ↓
最终词库: 2,000+ 关键词（含搜索量、CPC 等数据）
```

### 关键词分类体系

| 分类 | 定义 | 应用策略 |
|------|------|---------|
| **核心词** | 高搜索量、高相关性的主关键词 | Listing 标题 + 广告投放主力 |
| **长尾词** | 3+ 词组合、精准意图 | 后台关键词 + 精准广告 |
| **品牌词** | 包含品牌名的关键词 | 品牌广告防御 |
| **竞品词** | 包含竞品品牌名的关键词 | 竞品拦截广告 |
| **属性词** | 描述产品特征（颜色/尺寸/材质） | A+ 内容 + 变体优化 |
| **场景词** | 描述使用场景的关键词 | Listing 五点 + 图片场景 |
| **否定词** | 不相关/低转化的关键词 | 否定关键词列表（节省广告费） |

### 输出文件结构

```
keyword-reports/
└── {ASIN}_{Site}_{YYYYMMDD}/
    ├── report.md                    # Markdown 分析报告
    ├── keywords.csv                 # 完整关键词词库（含分类标签）
    ├── negative_words.txt           # 否定词（直接复制到广告后台）
    ├── brand_words.txt              # 品牌词列表
    ├── categorized_summary.json     # 分类统计 JSON
    └── dashboard.html               # HTML 可视化仪表板
```

### 关键词报告模板

```markdown
# 关键词调研分析报告

## 分析概览

| 项目 | 详情 |
|------|------|
| **ASIN** | [{ASIN}](https://www.amazon.com/dp/{ASIN}) |
| **产品名称** | {产品名} |
| **亚马逊站点** | {Site} |
| **分析时间** | {YYYY-MM-DD HH:mm:ss} |
| **词库规模** | {N} 个关键词（原始：{M} 个） |
| **总搜索量** | {总搜索量} |
| **平均 CPC** | ${CPC} |

---

## 分类统计

| 分类 | 数量 | 占比 | 总搜索量 | 平均搜索量 | 应用策略 |
|------|------|------|----------|-----------|----------|
| 核心词 | {N} | {%} | {V} | {AVG} | Listing 标题 + PPC |
| 长尾词 | {N} | {%} | {V} | {AVG} | 后台 ST + 精准广告 |
| 品牌词 | {N} | {%} | {V} | {AVG} | 品牌防御 |
| 否定词 | {N} | {%} | — | — | 否定投放 |

---

## 核心关键词 Top 20

| # | 关键词 | 月搜索量 | CPC | 竞争度 | 建议 |
|---|--------|---------|-----|--------|------|
| 1 | {keyword} | {volume} | ${cpc} | {level} | {action} |

---

## 长尾词机会 Top 30

| 关键词 | 月搜索量 | CPC | 竞争度 | 机会评分 |
|--------|---------|-----|--------|---------|

---

## 否定词列表

> 以下关键词建议添加到广告否定词列表，直接复制使用

{否定词列表，每行一个}

---

## 选词建议

### Listing 优化
- **标题**：{建议嵌入的核心关键词}
- **五点描述**：{建议覆盖的场景词/属性词}
- **后台 Search Terms**：{建议的长尾词组合}

### PPC 广告
- **自动广告**：{建议出价策略}
- **手动广告-精准**：{Top 核心词}
- **手动广告-短语**：{长尾词}
- **否定词**：见 negative_words.txt

---

生成时间：{时间戳} | Skill: amazon-analyse v1.1.0 (keyword-research)
```

---

## 模块 C：差评痛点分析

> 触发：`/review-analysis <ASIN> <MARKETPLACE>`

### 6 维痛点分析框架

```
采集 1-3 星差评（≥50 条样本）
  ↓
┌────────────────────────────────────────────────────┐
│                 6 维痛点分类框架                     │
├────────────────────────────────────────────────────┤
│ D1: 电子模块故障    │ 电池/蓝牙/传感器/主板等故障   │
│ D2: 结构/组装问题   │ 松动/断裂/配合不良/脱胶       │
│ D3: 设计/功能缺陷   │ 操作不便/功能缺失/设计不合理   │
│ D4: 外观/材质问题   │ 做工粗糙/材质廉价/色差/异味    │
│ D5: 描述不符        │ 与图片/文字描述不一致           │
│ D6: 服务/物流问题   │ 配送损坏/客服差/退换困难       │
└────────────────────────────────────────────────────┘
  ↓
每个维度输出: 占比 + 代表性原文 + 严重度 + 改进建议
  ↓
汇总: 改进优先级矩阵 + 产品改进建议 + 竞品差异化方向
```

### 分析执行步骤

1. **数据采集**：调用 `get_product_detail` 获取产品基础信息 + `get_product_reviews`（筛选 1-3 星，≥50 条）
2. **痛点归类**：逐条评论分析，按 6 维框架归类（一条评论可归入多个维度）
3. **频率统计**：计算每个维度的提及占比
4. **严重度评估**：按影响程度标记（Critical / Major / Minor）
5. **原文标注**：每个维度选取 3-5 条最具代表性的原文
6. **改进建议**：基于痛点频率和严重度，输出优先级排序的改进方向

### 痛点严重度定义

| 级别 | 标签 | 定义 | 改进优先级 |
|------|------|------|-----------|
| **Critical** | 致命 | 产品无法正常使用、安全隐患 | P0 - 立即修复 |
| **Major** | 严重 | 核心功能受损、用户体验严重下降 | P1 - 优先修复 |
| **Minor** | 轻微 | 不影响核心功能、但影响满意度 | P2 - 计划改进 |

### 输出文件结构

```
review-analysis-reports/
└── {ASIN}_{Site}_{YYYYMMDD}/
    └── report.md                    # 差评深度分析报告
```

### 差评分析报告模板

```markdown
# {产品名} - 评论深度分析报告

> ASIN: {ASIN} | 站点: {Site} | 分析时间: {YYYY-MM-DD}

---

## 产品基础信息

| 项目 | 内容 |
|------|------|
| 产品标题 | {完整标题} |
| 品牌 | {品牌} |
| 价格 | ${价格} |
| 评分 | {评分}/5.0 |
| 评论总数 | {评论数} |
| 分析样本 | {N} 条 (1-3星差评) |

---

## 痛点分析汇总

| 维度 | 痛点类型 | 提及占比 | 严重度 | 改进优先级 |
|------|---------|---------|--------|-----------|
| D1 | 电子模块故障 | {%} | {级别} | {P0/P1/P2} |
| D2 | 结构/组装问题 | {%} | {级别} | {P0/P1/P2} |
| D3 | 设计/功能缺陷 | {%} | {级别} | {P0/P1/P2} |
| D4 | 外观/材质问题 | {%} | {级别} | {P0/P1/P2} |
| D5 | 描述不符 | {%} | {级别} | {P0/P1/P2} |
| D6 | 服务/物流问题 | {%} | {级别} | {P0/P1/P2} |

---

## D1: 电子模块故障

**占比**: {%} | **严重度**: {级别}

**典型问题**:
- {具体问题描述 1}
- {具体问题描述 2}

**代表性评论原文**:
> "{用户原文 1}" — {星级}, {日期}

> "{用户原文 2}" — {星级}, {日期}

**改进建议**: {具体改进方向}

---

## D2: 结构/组装问题
{同上结构}

## D3: 设计/功能缺陷
{同上结构}

## D4: 外观/材质问题
{同上结构}

## D5: 描述不符
{同上结构}

## D6: 服务/物流问题
{同上结构}

---

## 改进优先级矩阵

| 优先级 | 维度 | 核心问题 | 建议措施 | 预期影响 |
|--------|------|---------|---------|---------|
| P0 | {维度} | {问题} | {措施} | {影响} |
| P1 | {维度} | {问题} | {措施} | {影响} |
| P2 | {维度} | {问题} | {措施} | {影响} |

---

## 产品改进建议

### 必须修复（P0 - 影响退货率）
- {建议 1}

### 重点优化（P1 - 影响评分）
- {建议 2}

### 持续改进（P2 - 提升满意度）
- {建议 3}

### 竞品差异化方向
- {基于痛点分析的差异化机会}

---

**免责声明**：分析基于 Sorftime API 采集的评论样本，样本量和时间窗口可能影响结论全面性。
生成时间：{时间戳} | Skill: amazon-analyse v1.1.0 (review-analysis)
```

---

## 与太一元系统集成

### Agent 协作

| 集成点 | 说明 |
|--------|------|
| **market-insight** | amazon-analyse 数据 → market-insight 用户动机分析 → 产品机会定义 |
| **brightdata-research** | 两者互补：Sorftime 提供官方 API 数据，Bright Data 补充爬取细节 |
| **spec-writer** | 分析结论 → 产品规格文档 → 开发路线图 |
| **deep-research** | 品类背景调研 → amazon-analyse 竞品定向分析 |

### 三模块协同数据流

```
deep-research（品类背景调研）
        ↓
amazon-analyse（Listing 穿透分析，建立全局视野）
        ↓
  ┌─────────────┬──────────────────┐
  ↓             ↓                  ↓
keyword-research   review-analysis    market-insight
（关键词词库）      （痛点挖掘）        （用户动机）
  ↓             ↓                  ↓
  └─────────────┴──────────────────┘
        ↓
spec-writer（新品规格定义 / Listing 优化方案）
```

### 推荐组合用法

| 场景 | 组合 | 说明 |
|------|------|------|
| **选品决策** | `/amazon-analyse` → `/keyword-research` → `/review-analysis` | 全面评估后决策 |
| **Listing 优化** | `/keyword-research` + `/review-analysis` | 关键词布局 + 卖点提炼 |
| **竞品拆解** | `/amazon-analyse` + `/review-analysis` | 竞品弱点 → 差异化方向 |
| **广告投放** | `/keyword-research` | 词库 + 否定词 → 直接用于 PPC |

---

## 版本历史

### v1.1.0 (2026-03-17)
- 新增模块 B：关键词深度调研（`/keyword-research`）
  - 三阶段数据获取流水线：基础数据 → 长尾词扩展 → 数据清洗
  - 7 类关键词分类体系（核心/长尾/品牌/竞品/属性/场景/否定）
  - 多格式输出（CSV + TXT + JSON + Dashboard HTML）
  - 词库规模目标 2,000+
- 新增模块 C：差评痛点分析（`/review-analysis`）
  - 6 维痛点分析框架（电子故障/结构组装/设计功能/外观材质/描述不符/服务物流）
  - 三级严重度评估（Critical/Major/Minor → P0/P1/P2）
  - 代表性评论原文保留
  - 改进优先级矩阵
- 扩展 Sorftime MCP 工具映射（新增 4 个关键词相关工具）
- 新增三模块协同数据流和推荐组合用法
- 参考来源: [amazon-sorftime-research-MCP-skill](https://github.com/liangdabiao/amazon-sorftime-research-MCP-skill)

### v1.0.0 (2026-03-04)
- 初始版本，基于 Sorftime MCP 实现六大维度分析
- 三种分析深度模式（Quick/Standard/Deep）
- 完整选品报告模板
- 参考来源: [amazon-sorftime-research-MCP-skill](https://github.com/liangdabiao/amazon-sorftime-research-MCP-skill)

### 规划中
- v1.2.0: 新增模块 D — **选品深度调研**（`/product-research`）
  - 宏观整合模块，串联 Listing/关键词/评论三模块数据
  - 多维度交叉分析找市场空位（价格带×评分×功能矩阵）
  - 痛点挖掘 + 竞争格局 + 市场空白识别
  - 参考: liangdabiao/amazon-sorftime-research-MCP-skill (轻量版) 及 zach22/amazon-skills (10 章标准化 unified_payload.json)
  - 支持品类级搜索输入（如 `/product-research "Action Figure toy" US`），而非仅 ASIN
- v1.3.0: 支持多 ASIN 批量对比分析
- v1.4.0: 集成历史价格波动预警
- v1.5.0: 支持新兴市场（MX/AU/SG）

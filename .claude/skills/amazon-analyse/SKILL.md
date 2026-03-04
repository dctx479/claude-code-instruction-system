---
name: amazon-analyse
description: 亚马逊竞品 Listing 全维度穿透分析报告，基于 Sorftime MCP 获取官方数据，覆盖关键词流量、评论情感、销量趋势、竞争格局六大维度
version: 1.0.0
license: MIT
metadata:
  category: research
  tags: [amazon, ecommerce, product-selection, competitor-analysis, sorftime, mcp, listing]
  requires: [sorftime-mcp]
  source: https://github.com/liangdabiao/amazon-sorftime-research-MCP-skill
---

# Amazon Analyse Skill

> 亚马逊选品核心工具，通过 Sorftime MCP 获取真实 Amazon 数据（非爬取），对指定 ASIN 进行全维度穿透分析

## 契约定义

### What（输入/输出）

**输入**：
- `ASIN`：亚马逊商品标准识别号（必填），如 `B07PWTJ4H1`
- `MARKETPLACE`：目标市场（必填），如 `US`、`DE`、`UK`、`JP`、`FR`、`IT`、`ES`、`CA`
- 可选：分析深度（Quick/Standard/Deep，默认 Standard）
- 可选：重点维度（keywords/reviews/ranking/competition，默认全维度）

**输出**：
- 结构化 Listing 穿透分析报告（Markdown）
- 包含六大维度数据：产品详情、关键词流量、评论情感、销量排名、竞争格局、市场机会
- 保存至 `reports/amazon-{ASIN}-{MARKETPLACE}-{date}.md`

### When Done（验收标准）

- 报告涵盖六大分析维度（每项有具体数据支撑）
- 关键词表包含流量来源 + 竞品布局
- 评论分析识别出 ≥3 个用户痛点和 ≥3 个优势聚类
- 提供可操作的选品/优化建议
- 所有数据注明来源（Sorftime API + 时间戳）

### What NOT（边界约束）

- **禁止编造数据**：所有数字必须来自 Sorftime MCP 真实返回
- **禁止跨站爬取**：此 Skill 专用 Sorftime API，不调用 Bright Data 或直接抓取 Amazon
- **禁止忽略市场差异**：DE/JP 等市场的关键词必须用对应语言分析
- **禁止超出 ASIN 范围**：分析对象为指定 ASIN，不随意扩展到同类竞品（除非明确请求）
- **必须标注数据时效**：Sorftime 数据有时效性，报告必须注明获取时间

---

## 何时使用此 Skill

**触发命令**：
```bash
/amazon-analyse <ASIN> <MARKETPLACE>

# 示例
/amazon-analyse B07PWTJ4H1 US
/amazon-analyse B08N5WRWNW DE
```

**自动激活场景**：
- 亚马逊 ASIN 分析请求
- 竞品 Listing 穿透分析
- 亚马逊选品决策支持
- 关键词流量来源分析
- 评论痛点挖掘

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

| Sorftime 工具 | 用途 | 分析维度 |
|--------------|------|---------|
| `get_product_detail` | 产品基础信息 | 维度1: 产品详情 |
| `get_product_keywords` | 关键词流量数据 | 维度2: 关键词分析 |
| `get_product_reviews` | 评论数据采集 | 维度3: 评论情感 |
| `get_product_rank_trend` | BSR 历史趋势 | 维度4: 销量排名 |
| `get_category_top` | 品类 Top 榜 | 维度5: 竞争格局 |
| `get_keyword_competitors` | 关键词竞品布局 | 维度6: 市场机会 |

---

## 六大分析维度

### 维度 1：产品详情

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

### 维度 2：关键词流量分析

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
| ... | ... | ... | ... | ... |

### 长尾词机会

| 长尾词 | 月搜索量 | 当前排名 | 建议 |
|--------|---------|---------|------|
| wireless earbuds for small ears | 45,000 | 未入围 | 重点布局 |
```

### 维度 3：评论情感分析

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
| 降噪效果不稳定 | 31% | "ANC cuts out randomly" | 🔴 高 |
| 通话音质差 | 24% | "mic quality is terrible" | 🔴 高 |
| 充电盒做工粗糙 | 19% | "case feels cheap" | 🟡 中 |
```

### 维度 4：销量排名趋势

**数据点**：
- BSR 历史曲线（近 12 个月）
- 季节性规律识别
- 排名峰谷分析（关联促销/节日）
- 月均销量估算

**输出示例**：
```markdown
## 销量排名趋势

### BSR 趋势（近 12 个月）

- 整体趋势：📈 上升（12个月前 #380 → 当前 #127）
- 最佳排名：#89（2025年11月 黑五期间）
- 最差排名：#520（2025年8月 淡季）
- 月均销量估算：**3,200 - 4,500 件**

### 季节性规律

| 月份 | 销量指数 | 建议备货 |
|------|---------|---------|
| 10-12月 | 180% | 旺季，提前2个月备货 |
| 1-2月 | 90% | 平季 |
| 7-8月 | 75% | 淡季，控制库存 |
```

### 维度 5：竞争格局分析

**数据点**：
- 品类 Top 20 竞品列表
- 价格带分布矩阵
- 品牌市场份额
- 新品涌入速度

**输出示例**：
```markdown
## 竞争格局

### 品类 Top 5 竞品对比

| ASIN | 品牌 | 价格 | 评分 | 评价数 | 月销量 | 核心差异 |
|------|------|------|------|--------|--------|---------|
| B0TARGET | Sony | $99 | 4.7 | 45K | 8,000 | 降噪更强 |
| B0XXX | Anker | $49 | 4.4 | 28K | 6,500 | 性价比高 |
| 本品 | BrandName | $79 | 4.5 | 12K | 3,800 | 续航领先 |

### 价格带竞争热度

- $0-40: ⭐⭐ 中度竞争（性价比品牌为主）
- $40-80: ⭐⭐⭐ 激烈竞争（本品所在区间）
- $80-120: ⭐⭐ 中度竞争（品质品牌为主）
- $120+: ⭐ 低竞争（高端小众）
```

### 维度 6：市场机会识别

**数据点**：
- 需求未被满足的细分场景
- 竞品普遍缺失的功能点
- 关键词蓝海（高搜索 + 低竞争）
- 定价窗口（可差异化的价格带）

---

## 分析深度模式

### Quick Mode（快速模式）

**适用**：快速了解竞品基本面，10 分钟内得出结论
**数据调用**：`get_product_detail` + `get_product_keywords`（Top 10）
**输出**：产品摘要 + 核心关键词 + 初步评估

### Standard Mode（标准模式，默认）

**适用**：选品决策前的全面分析
**数据调用**：六大维度全覆盖，关键词 Top 20
**输出**：完整穿透分析报告 + 选品建议

### Deep Mode（深度模式）

**适用**：进入新品类前的竞争格局深度摸底
**数据调用**：Standard 基础上 + 品类 Top 50 + 关键词竞品布局矩阵
**输出**：竞争格局全图 + 蓝海机会地图 + 入场策略

---

## 输出报告模板

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

**综合评分**：⭐⭐⭐⭐ （4/5）
- 市场规模: ★★★★★ | 竞争强度: ★★★☆☆ | 利润空间: ★★★★☆

---

## 一、产品详情
{维度1输出}

## 二、关键词流量分析
{维度2输出}

## 三、评论情感分析
{维度3输出}

## 四、销量排名趋势
{维度4输出}

## 五、竞争格局
{维度5输出}

## 六、市场机会
{维度6输出}

---

## 选品决策建议

### ✅ 入场理由
- {数据支撑的理由1}
- {数据支撑的理由2}

### ⚠️ 风险提示
- {具体风险1}
- {具体风险2}

### 🎯 差异化方向
- {基于痛点分析的产品改进方向}

---

**免责声明**：数据来源 Sorftime API，反映分析时刻市场状态，电商数据动态变化，建议结合最新实测数据决策。
生成时间：{时间戳} | Skill: amazon-analyse v1.0.0
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

### 数据流

```
deep-research（品类背景）
        ↓
amazon-analyse（竞品 Listing 穿透）
        ↓
market-insight（用户需求与动机）
        ↓
spec-writer（新品规格定义）
```

---

## 版本历史

### v1.0.0 (2026-03-04)
- 初始版本，基于 Sorftime MCP 实现六大维度分析
- 三种分析深度模式（Quick/Standard/Deep）
- 完整选品报告模板
- 参考来源: [amazon-sorftime-research-MCP-skill](https://github.com/liangdabiao/amazon-sorftime-research-MCP-skill)

### 规划中
- v1.1.0: 支持多 ASIN 批量对比分析
- v1.2.0: 集成历史价格波动预警
- v1.3.0: 支持新兴市场（MX/AU/SG）

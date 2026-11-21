---
name: amazon-analyse
description: 亚马逊选品全维度分析工具集，基于 Sorftime MCP 获取官方数据，覆盖 Listing 穿透分析、关键词深度调研（2000+ 词库）、差评 6 维痛点分析
license: MIT
metadata:
  category: research
  tags:
  - amazon
  - ecommerce
  - product-selection
  - competitor-analysis
  - sorftime
  - mcp
  - listing
  - keyword-research
  - review-analysis
  - pain-point
  requires:
  - sorftime-mcp
  source: https://github.com/liangdabiao/amazon-sorftime-research-MCP-skill
  version: 1.1.0
  trigger:
  - /amazon-analyse
  - 亚马逊选品分析
  - Listing 分析
  - 亚马逊关键词调研
  - 差评痛点分析
disable-model-invocation: true
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


## Extended procedure

Read [references/extended-guide.md](references/extended-guide.md) for the remaining modes, examples, and checks. Resource paths in that guide are relative to this skill directory.

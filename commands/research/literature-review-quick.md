# /literature-review-quick - 快速文献精读

## 功能描述

快速生成文献精读报告（报告模式）。自动识别文献类型（Research Article / Review Article），采用对应模板生成完整的结构化报告，包含评分、TODO List 和推荐阅读段落。

## 使用场景

- 快速调研多篇文献（一周 20 篇）
- 文献综述写作准备
- 需要结构化输出
- 批量处理文献

## 命令格式

```bash
/literature-review-quick <文献标识> [选项]
```

## 参数说明

### 必需参数

- `<文献标识>`: 文献的标识符，支持以下格式：
  - 文献标题：`"Attention Is All You Need"`
  - DOI：`10.1038/s41586-021-03819-2`
  - Zotero Item Key：`ABCD1234`

### 可选参数

- `--output <路径>`: 指定报告输出路径（默认：当前目录）
- `--format <格式>`: 输出格式（markdown / pdf / docx，默认：markdown）
- `--save-to-zotero`: 将报告保存到 Zotero 笔记

## 使用示例

### 示例 1: 通过标题快速生成报告

```bash
/literature-review-quick "Deep Residual Learning for Image Recognition"
```

**输出**：
- 自动识别为 Research Article
- 生成完整精读报告（Template A）
- 包含：元数据、逻辑复盘、技术深挖、图表详解、评分、TODO List、推荐阅读

### 示例 2: 通过 DOI 生成报告并保存到 Zotero

```bash
/literature-review-quick 10.1038/s41586-021-03819-2 --save-to-zotero
```

**输出**：
- 从 DOI 获取文献信息
- 生成精读报告
- 自动保存到 Zotero 笔记

### 示例 3: 生成 PDF 格式报告

```bash
/literature-review-quick "A Survey on Deep Learning" --format pdf --output ./reports/
```

**输出**：
- 自动识别为 Review Article
- 生成精读报告（Template B）
- 输出为 PDF 格式
- 保存到 ./reports/ 目录

## 工作流程

```
用户输入
    ↓
获取文献全文（Zotero / DOI / 网络）
    ↓
自动识别文献类型
    ├─ Research Article → Template A
    └─ Review Article → Template B
    ↓
生成完整精读报告
    ├─ 元数据
    ├─ 核心内容
    ├─ 深度分析
    ├─ 详细复盘/全景脉络
    ├─ 总结评价（含评分）
    ├─ 推荐阅读
    └─ 实施笔记/行动清单
    ↓
输出报告（Markdown / PDF / Docx）
    ↓
（可选）保存到 Zotero
```

## 报告结构

### Research Article 报告（Template A）

1. 📌 **元数据**：标题、作者、期刊、DOI、关键词
2. 💡 **核心内容**：主要概念、研究问题
3. 🔍 **深度分析**：背景、方法、数据、结果、意义
4. 📖 **详细复盘**：
   - 逻辑链条（起承转合）
   - 技术深挖（直觉解释）
   - 图表详解（控制变量分析）
5. ⭐ **总结评价**：亮点、不足、未来方向、评分（X/10）
6. 📚 **推荐阅读**：必读段落、选读段落
7. ✅ **实施笔记**：TODO List（立即/短期/长期）、技术栈

### Review Article 报告（Template B）

1. 📌 **元数据**：标题、作者、期刊、DOI、关键词、涵盖范围
2. 💡 **核心内容**：主要概念、范围目标
3. 🔍 **深度分析**：为何现在、分类框架、共识、争议
4. 🌐 **全景脉络**：
   - 历史演进（萌芽期 → 爆发期 → 繁荣期）
   - 流派详解（流派对比）
   - 综合串联（方法论迁移、矛盾点）
   - 金句积累（精彩定义、高情商评价）
5. ⭐ **总结评价**：价值、偏见、未来方向、评分（X/10）
6. 📚 **推荐阅读**：必读段落、选读段落
7. ✅ **行动清单**：必读论文、知识图谱、工具数据

## 评分系统

### 评分维度（总分 10 分）

| 维度 | 权重 | 评分标准 |
|------|------|---------|
| 创新性 | 30% | 方法/发现的新颖程度 |
| 严谨性 | 25% | 实验设计、统计方法 |
| 影响力 | 20% | 引用量、期刊影响因子 |
| 可复现性 | 15% | 代码/数据开放程度 |
| 写作质量 | 10% | 逻辑清晰度、图表质量 |

## 与其他命令的区别

| 命令 | 模式 | 输出 | 适用场景 |
|------|------|------|---------|
| `/literature-review` | 交互模式 | 逐图解读 | 深度学习单篇论文 |
| `/literature-review-quick` | 报告模式 | 完整报告 | 快速调研多篇文献 |
| `/literature-batch-review` | 批量报告 | 多个报告 | 批量处理 Zotero 集合 |

## 集成点

- **literature-mentor skill**: 核心解读引擎
- **Zotero MCP**: 文献获取和笔记保存
- **literature-manager agent**: 文献分类和管理
- **paper-writing-assistant agent**: 综述写作支持

## 注意事项

1. **文献获取**：优先从 Zotero 获取，确保全文可用
2. **自动分类**：如果无法自动识别文献类型，会询问用户
3. **报告质量**：报告质量取决于文献全文的完整性
4. **保存到 Zotero**：需要配置 Zotero MCP 服务器

## 相关文档

- Skill 定义：`C:\Users\ASUS\.claude\skills\literature-mentor\SKILL.md`
- Template A：`C:\Users\ASUS\.claude\skills\literature-mentor\templates\research-article-template.md`
- Template B：`C:\Users\ASUS\.claude\skills\literature-mentor\templates\review-article-template.md`
- Zotero 集成：`integrations/zotero-mcp-setup.md`

## 预期效果

- **效率提升**：快速调研 20 篇论文/周
- **质量保证**：结构化输出，便于后续引用
- **可操作性**：TODO List 驱动行动，避免"看完就忘"
- **评分系统**：帮助筛选高质量文献

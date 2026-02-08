# /literature-review - 文献综述生成

## 功能描述
基于 Vibe Researching 理念，生成高质量文献综述。

## 使用方法
```bash
/literature-review <主题> [选项]
```

## 参数
- `<主题>`: 综述主题（必需）
- `--zotero-collection`: Zotero 文献集合名称
- `--style`: 写作风格（nature/ieee/apa，默认 nature）
- `--output`: 输出文件路径

## 工作流程

### 1. 准备阶段（人工）
- 在 Zotero 中收集高质量文献（闭源期刊）
- 准备 1-2 篇顶级期刊综述作为范本

### 2. 学习阶段（AI）
- 分析范本综述的写作风格和结构
- 生成写作指南（WRITING-GUIDE.md）

### 3. 规划阶段（AI + 人工审核）
- 访问 Zotero 文献库
- 搜索开源文献（arXiv, PubMed）
- 生成综述框架（REVIEW-PLAN.md）
- **人工审核框架，必要时修改**

### 4. 写作阶段（AI）
- 按照框架撰写综述
- 自动引用文献
- 生成图表

### 5. 审核阶段（人工）
- Review 全文
- 补充图表
- 调整参考文献格式

## 核心理念
**AI 是高质量信息加工器**
- 输入：高质量文献（Zotero + 开源数据库）
- 处理：结构化编排和信息整合
- 输出：符合期刊标准的综述初稿

## 示例
```bash
# 生成医学影像 AI 综述
/literature-review "Deep Learning for Medical Image Segmentation" \
  --zotero-collection "Coronary CTA" \
  --style nature \
  --output reviews/medical-imaging-review.md
```

## 输出
- `WRITING-GUIDE.md`: 写作风格指南
- `REVIEW-PLAN.md`: 综述框架
- `<output>.md`: 综述初稿（Markdown）
- `<output>.docx`: Word 格式（通过 pandoc 转换）
- `references.bib`: BibTeX 引用文件

## 质量保证
- 所有引用来自真实文献（Zotero + arXiv + PubMed）
- 遵循顶级期刊写作风格
- 结构化框架，人工审核
- 避免 AI 幻觉和编造

## 相关命令

### 文献精读命令对比

| 命令 | 用途 | 输入 | 输出 | 交互性 | 适用场景 |
|------|------|------|------|--------|---------|
| `/literature-review` | 生成文献综述 | 主题 + 多篇文献 | 综述文章 | 需人工审核框架 | 撰写综述论文 |
| `/literature-review-quick` | 单篇文献精读 | 1 篇文献标识 | 精读报告 | 全自动（报告模式） | 快速调研文献 |
| `/literature-batch-review` | 批量文献精读 | Zotero 集合 | 多个报告 + 汇总 | 全自动（并行处理） | 批量处理文献库 |
| 交互模式 | 深度解读文献 | 文献标题/DOI | 逐图交互解读 | 高度交互 | 深度学习单篇论文 |

### 使用建议

**场景 1: 撰写文献综述**
```bash
# 步骤 1: 批量精读文献（建立知识库）
/literature-batch-review "Deep Learning Papers" --generate-index

# 步骤 2: 生成综述文章
/literature-review "Deep Learning for Medical Imaging" \
  --zotero-collection "Deep Learning Papers" \
  --style nature
```

**场景 2: 快速调研新领域**
```bash
# 快速生成多篇文献的精读报告
/literature-review-quick "Attention Is All You Need"
/literature-review-quick "BERT: Pre-training of Deep Bidirectional Transformers"
/literature-review-quick "GPT-3: Language Models are Few-Shot Learners"
```

**场景 3: 深度学习单篇论文**
```markdown
# 使用交互模式（直接对话）
"帮我解读这篇论文：Attention Is All You Need"

# 系统会：
# 1. 提供整体概览
# 2. 逐图交互解读
# 3. 等待用户确认后继续
# 4. 提供总结与启发
```

**场景 4: 批量处理文献库**
```bash
# 批量处理 Zotero 集合，生成汇总索引
/literature-batch-review "Computer Vision" \
  --workers 5 \
  --generate-index \
  --save-to-zotero
```

### 命令选择决策树

```
需要生成综述文章？
  ├─ 是 → /literature-review
  └─ 否 → 需要处理多篇文献？
           ├─ 是 → /literature-batch-review
           └─ 否 → 需要深度交互讨论？
                    ├─ 是 → 交互模式（直接对话）
                    └─ 否 → /literature-review-quick
```

## 相关文档
- **单篇快速精读**: `commands/research/literature-review-quick.md`
- **批量文献精读**: `commands/research/literature-batch-review.md`
- **Literature Mentor Skill**: `.claude/skills/literature-mentor/SKILL.md`
- **Zotero 集成**: `integrations/zotero-mcp-setup.md`
- **科研工作流**: `docs/research-support-guide.md`

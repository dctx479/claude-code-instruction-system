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

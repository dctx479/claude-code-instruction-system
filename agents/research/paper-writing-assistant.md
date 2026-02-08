# Paper Writing Assistant Agent

## 角色定义

论文写作助手（Paper Writing Assistant），基于 Vibe Researching 理念，辅助完成文献综述和研究论文的写作。

## 核心理念

**AI 是高质量信息加工器**
- 人类：提供高质量文献、确定框架、把控质量
- AI：信息整理、编排、格式化、润色

## 核心职责

### 1. 学习写作风格
- 分析 Top 期刊综述（Nature、Science、Cell）
- 提取写作框架和风格
- 生成写作指南（CLAUDE.md）

### 2. 生成写作计划
- 基于文献库生成大纲
- 确定章节结构
- 制定写作计划（IMPLEMENT.md）

### 3. 撰写初稿
- 按章节生成内容
- 自动引用管理
- 保持风格一致性

### 4. 格式化输出
- LaTeX 格式
- Markdown 格式
- Word 格式（通过 pandoc）

### 5. 语言润色
- 学术语言优化
- 逻辑连贯性检查
- 语法和拼写检查

## 工作流程

### Vibe Researching 写作流程

```
Phase 1: 准备阶段（人工主导）
1. 筛选高质量文献
   - 闭源期刊（Nature、IEEE、Springer）
   - 开源数据库（arXiv、PubMed）
   ↓
2. 导入 Zotero 文献库
   - 按主题创建集合
   - 添加标签和笔记
   ↓
3. 提供范本综述
   - Top 期刊综述 1-2 篇
   - 让 AI 学习写作风格

Phase 2: 规划阶段（AI + 人工审查）
1. AI 学习写作风格
   - 分析范本结构
   - 提取写作规范
   - 生成写作指南（CLAUDE.md）
   ↓
2. AI 访问文献库
   - 通过 Zotero MCP 读取文献
   - 补充 arXiv/PubMed 搜索
   - 整合 DeepResearch 报告
   ↓
3. AI 生成写作计划
   - 综述框架
   - 章节大纲
   - 引用分配
   - 输出 IMPLEMENT.md
   ↓
4. 人工审查框架
   - 检查结构合理性
   - 调整章节安排
   - 确认写作计划

Phase 3: 写作阶段（AI 主导）
1. AI 按计划写作
   - 逐章节生成内容
   - 自动引用文献
   - 保持风格一致
   ↓
2. 生成初稿
   - Markdown 格式
   - 包含引用标记
   - 生成图表建议

Phase 4: 审查阶段（人工主导）
1. 人工 Review 全文
   - 检查内容准确性
   - 调整逻辑结构
   - 补充图表
   ↓
2. AI 润色和格式化
   - 语言优化
   - 格式统一
   - 生成最终版本
```

## 使用示例

### 1. 学习写作风格

```bash
# 切换到 plan 模式
/plan

# 提供范本综述
"请分析这篇 Nature Reviews Cardiology 的综述，
提取其写作风格、结构编排和语言特点，
生成一份综述写作指南保存为 CLAUDE.md"

# AI 输出：
# - 分析范本结构
# - 提取写作规范
# - 生成 CLAUDE.md
```

### 2. 生成写作计划

```bash
# 在 plan 模式下
"访问我的 Zotero 文献库中的 'Coronary CTA Segmentation' 集合，
同时搜索 arXiv 和 PubMed 相关文献，
基于写作指南生成一份文献综述的写作计划 IMPLEMENT.md"

# AI 输出：
# - 访问 Zotero 文献
# - 搜索开源数据库
# - 生成综述框架
# - 输出 IMPLEMENT.md
```

### 3. 撰写初稿

```bash
# 退出 plan 模式
/exit-plan

# 开始写作
"按照 IMPLEMENT.md 的计划，
参考 CLAUDE.md 的写作风格，
撰写文献综述初稿"

# AI 输出：
# - 逐章节生成内容
# - 自动引用文献
# - 生成 draft.md
```

### 4. 格式化输出

```bash
# 转换为 LaTeX
/research paper export latex

# 转换为 Word
/research paper export word

# 生成 PDF
/research paper export pdf
```

## 输出格式

### 写作指南 (CLAUDE.md)

```markdown
# 文献综述写作指南

## 写作风格
- 基于 Nature Reviews Cardiology (IF: 44.2)
- 学术严谨，逻辑清晰
- 使用主动语态，避免冗余

## 结构框架
1. Abstract (200-250 words)
2. Introduction (2-3 pages)
3. Main Body (按主题分节)
4. Future Directions (1-2 pages)
5. Conclusions (1 page)

## 语言规范
- 使用过渡句连接段落
- 每段首句概括主题
- 引用格式：(Author et al., Year)

## 图表要求
- 每 3-4 页一个图表
- 图表标题简洁明确
- 引用所有图表
```

### 写作计划 (IMPLEMENT.md)

```markdown
# 文献综述写作计划

## 标题
Deep Learning for Coronary Artery Segmentation: A Comprehensive Review

## 大纲

### 1. Abstract
- 研究背景
- 主要发现
- 未来方向

### 2. Introduction (3 pages)
- 冠脉疾病背景
- CTA 成像技术
- 深度学习应用
- 综述目标和范围

### 3. Deep Learning Architectures (8 pages)
#### 3.1 CNN-based Methods
- U-Net 及变体 [引用: paper-001, paper-005]
- ResNet 架构 [引用: paper-010]

#### 3.2 Transformer-based Methods
- Vision Transformer [引用: paper-020]
- Swin Transformer [引用: paper-025]

### 4. Datasets and Benchmarks (5 pages)
- 公开数据集
- 评估指标
- 性能对比

### 5. Challenges and Future Directions (4 pages)
- 当前挑战
- 未来研究方向

### 6. Conclusions (2 pages)

## 引用分配
- 总计：100-120 篇
- Introduction: 20 篇
- Main Body: 70 篇
- Future: 10 篇
```

### 初稿 (draft.md)

```markdown
# Deep Learning for Coronary Artery Segmentation: A Comprehensive Review

## Abstract

Coronary artery disease remains a leading cause of mortality worldwide...
[200-250 words]

## 1. Introduction

### 1.1 Background

Coronary computed tomography angiography (CTA) has emerged as a non-invasive...

Recent advances in deep learning have revolutionized medical image analysis (Smith et al., 2024)...

### 1.2 Scope of This Review

This comprehensive review synthesizes recent progress in deep learning-based coronary artery segmentation...

## 2. Deep Learning Architectures

### 2.1 CNN-based Methods

#### 2.1.1 U-Net and Variants

The U-Net architecture (Ronneberger et al., 2015) has become the de facto standard...

[详细内容...]

## References

1. Smith, J. et al. (2024). Deep learning in medical imaging. Nature Reviews, 10(1), 1-20.
2. ...
```

## 技术实现

### 核心脚本

```python
def learn_writing_style(reference_paper_path):
    """学习写作风格"""
    text = extract_text(reference_paper_path)
    prompt = f"""
    分析以下综述论文，提取：
    1. 结构框架
    2. 写作风格
    3. 语言规范
    4. 引用格式

    生成写作指南。

    论文内容：
    {text}
    """
    guide = call_claude_api(prompt)
    save_to_file("CLAUDE.md", guide)

def generate_writing_plan(zotero_collection, topic):
    """生成写作计划"""
    # 访问 Zotero
    papers = fetch_from_zotero(zotero_collection)

    # 搜索开源数据库
    arxiv_papers = search_arxiv(topic)
    pubmed_papers = search_pubmed(topic)

    # 生成计划
    prompt = f"""
    基于以下文献，生成文献综述写作计划：

    Zotero 文献：{papers}
    arXiv 文献：{arxiv_papers}
    PubMed 文献：{pubmed_papers}

    要求：
    1. 生成章节大纲
    2. 分配引用文献
    3. 估算篇幅
    """
    plan = call_claude_api(prompt)
    save_to_file("IMPLEMENT.md", plan)

def write_draft(plan_file, style_guide):
    """撰写初稿"""
    plan = read_file(plan_file)
    guide = read_file(style_guide)

    prompt = f"""
    按照以下计划和风格指南撰写文献综述：

    写作计划：{plan}
    风格指南：{guide}

    要求：
    1. 逐章节生成内容
    2. 自动引用文献
    3. 保持风格一致
    """
    draft = call_claude_api(prompt)
    save_to_file("draft.md", draft)
```

## 质量控制

### 人工审查点

1. **框架审查**（Phase 2）
   - 检查 IMPLEMENT.md 结构
   - 调整章节安排
   - 确认引用分配

2. **内容审查**（Phase 4）
   - 检查准确性
   - 验证引用
   - 补充图表

3. **最终审查**
   - 语言润色
   - 格式统一
   - 投稿前检查

### AI 辅助检查

- 引用完整性检查
- 语法和拼写检查
- 格式一致性检查
- 字数统计

## 成功案例

### 医学影像综述
- 主题：冠脉 CTA 深度学习分割
- 文献：113 篇（Zotero + arXiv + PubMed）
- 输出：45 页，13,813 词
- 风格：Nature 期刊风格
- 时间：AI 写作 2-3 小时，人工审查 1-2 天

### 关键成功因素
1. ✅ 高质量文献（人工筛选）
2. ✅ 明确框架（AI 生成 + 人工审查）
3. ✅ 风格范本（Top 期刊综述）
4. ✅ 分阶段执行（准备-规划-写作-审查）

## 与现有系统集成

### 1. 与 literature-mentor Skill 协作

**协作场景**：
- **深度文献理解**：在写作前，使用 literature-mentor 深度解读核心文献，提取关键观点和方法学启发
- **综述框架优化**：基于 literature-mentor 的精读报告，优化综述章节结构和论述逻辑
- **引用质量提升**：利用 literature-mentor 的批判性分析，确保引用准确且有深度

**工作流程**：
```
Phase 1: 文献深度解读
literature-mentor 精读核心文献（10-20篇）
    ↓
提取每篇文献的核心观点、方法、局限
    ↓
生成文献关系图谱和研究脉络

Phase 2: 综述框架设计
paper-writing-assistant 基于精读报告
    ↓
设计综述章节结构
    ↓
分配文献到各章节
    ↓
生成写作计划（IMPLEMENT.md）

Phase 3: 内容撰写
paper-writing-assistant 撰写初稿
    ↓
引用 literature-mentor 的深度分析
    ↓
确保论述有深度和批判性

Phase 4: 质量审查
对比 literature-mentor 报告
    ↓
验证引用准确性
    ↓
补充遗漏的关键观点
```

**使用示例**：
```bash
# Step 1: 深度解读核心文献
"使用 literature-mentor 解读以下 10 篇核心文献，
生成精读报告保存到 .research/literature/reviews/"

# Step 2: 基于精读报告生成写作计划
"访问 .research/literature/reviews/ 中的精读报告，
结合 Zotero 文献库，生成综述写作计划 IMPLEMENT.md"

# Step 3: 撰写初稿
"按照 IMPLEMENT.md 撰写综述初稿，
引用精读报告中的关键观点和批判性分析"
```

**集成优势**：
- 确保对核心文献的深度理解
- 提升综述的学术深度和批判性
- 避免浅层引用和误读文献
- 构建清晰的研究脉络和逻辑

### 2. 文献管理集成
- 调用 Literature Manager Agent
- 访问文献索引和图谱
- 自动引用管理

### 3. 知识图谱集成
- 可视化文献关系
- 识别研究脉络
- 发现研究空白

### 4. 上下文归档集成
- 写作过程归档
- 关键决策记录
- 经验沉淀

---

**核心原则**: AI 负责信息编排，人类负责质量把关
**参考项目**: medical-imaging-review skill
**开源地址**: https://github.com/luwill/research-skills

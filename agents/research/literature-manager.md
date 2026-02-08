# Literature Manager Agent

## 角色定义

文献管理专家（Literature Manager），负责文献导入、分类、摘要、推荐和引用图谱构建。

## 核心理念

**AI 是高质量信息加工器，而非生成器**
- "Garbage in, Garbage out" - 输入质量决定输出质量
- 人工筛选高质量文献（闭源期刊 + 开源数据库）
- AI 负责信息整理和编排

## 核心职责

### 1. 文献导入
- 支持 PDF、BibTeX 格式
- 集成 Zotero API
- 支持批量导入

### 2. 自动分类
- 基于主题自动分类
- 智能标签生成
- 文献集合管理

### 3. 摘要提取
- 自动提取关键信息
- 生成结构化摘要
- 提取核心观点

### 4. 相关文献推荐
- 基于引用关系推荐
- 基于主题相似度推荐
- 基于研究方向推荐

### 5. 引用图谱
- 构建引用关系网络
- 识别关键文献
- 追踪研究脉络

## 工具集成

### Zotero MCP
- 访问个人文献库
- 按集合筛选文献
- 导出引用信息

### 开源数据库
- arXiv MCP
- PubMed MCP
- bioRxiv

### 闭源期刊
- IEEE Xplore
- Springer
- Nature/Science
- Elsevier

## 工作流程

### 标准流程

```
1. 人工筛选高质量文献
   - 闭源期刊（IEEE、Nature、Springer）
   - 开源数据库（arXiv、PubMed）
   ↓
2. 导入 Zotero 文献库
   - 按主题创建集合
   - 添加标签和笔记
   ↓
3. Claude Code 访问 Zotero
   - 通过 Zotero MCP 读取文献
   - 提取摘要和关键信息
   ↓
4. 生成文献索引
   - 自动分类
   - 构建引用图谱
   - 生成推荐列表
```

### Vibe Researching 流程

```
人类：提出研究问题，筛选高质量文献
  ↓
AI：访问文献库，提取关键信息
  ↓
AI：整理、分类、构建关系网络
  ↓
人类：审查结果，调整方向
  ↓
AI：生成文献综述大纲
```

## 使用示例

### 导入文献

```bash
# 从 Zotero 导入特定集合
/research literature import --zotero "Coronary CTA Segmentation"

# 从本地导入 PDF
/research literature import --pdf papers/*.pdf

# 从 BibTeX 导入
/research literature import --bibtex references.bib
```

### 分析文献

```bash
# 自动分类和摘要
/research literature analyze

# 生成引用图谱
/research literature graph

# 推荐相关文献
/research literature recommend --topic "deep learning segmentation"
```

### 搜索文献

```bash
# 在 Zotero 中搜索
/research literature search "coronary artery" --source zotero

# 在 arXiv 中搜索
/research literature search "medical image segmentation" --source arxiv

# 在 PubMed 中搜索
/research literature search "CT imaging" --source pubmed
```

## 输出格式

### 文献索引 (.research/literature/index.json)

```json
{
  "papers": [
    {
      "id": "paper-001",
      "title": "Deep Learning for Coronary Artery Segmentation",
      "authors": ["Author A", "Author B"],
      "year": 2024,
      "venue": "Nature Reviews Cardiology",
      "impact_factor": 44.2,
      "tags": ["deep learning", "segmentation", "coronary artery"],
      "summary": "AI 生成的结构化摘要...",
      "key_findings": ["发现1", "发现2"],
      "methodology": "方法描述",
      "citations": ["paper-002", "paper-003"],
      "cited_by": ["paper-010"],
      "source": "zotero",
      "file_path": "literature/papers/paper-001.pdf"
    }
  ],
  "collections": {
    "Coronary CTA Segmentation": ["paper-001", "paper-002"],
    "Deep Learning Methods": ["paper-001", "paper-003"]
  }
}
```

### 引用图谱 (.research/literature/graph.json)

```json
{
  "nodes": [
    {
      "id": "paper-001",
      "label": "Deep Learning for Coronary Artery Segmentation",
      "type": "paper",
      "year": 2024,
      "citations": 15,
      "importance": 0.85
    }
  ],
  "edges": [
    {
      "from": "paper-001",
      "to": "paper-002",
      "type": "cites",
      "context": "引用上下文"
    }
  ]
}
```

## 最佳实践

### 1. 文献筛选原则

**高质量来源**:
- ✅ Top 期刊（Nature、Science、Cell）
- ✅ 顶会论文（CVPR、ICCV、NeurIPS）
- ✅ 最近 5 年文献
- ❌ 避免低质量预印本

**数量控制**:
- 综述：50-100 篇
- 研究论文：20-30 篇
- 方法论文：10-15 篇

### 2. Zotero 组织

**集合结构**:
```
My Research/
├── Core Papers (核心文献)
├── Methods (方法论)
├── Related Work (相关工作)
└── Background (背景知识)
```

**标签系统**:
- 主题标签：`deep-learning`, `segmentation`
- 状态标签：`to-read`, `reading`, `read`
- 重要性：`key-paper`, `reference`

### 3. 避免上下文爆炸

**错误做法**:
- ❌ 直接让 Claude Code 读取所有 PDF
- ❌ 一次性处理 100+ 篇文献

**正确做法**:
- ✅ 通过 Zotero MCP 访问元数据
- ✅ 分批处理（每次 10-20 篇）
- ✅ 只在需要时读取 PDF 全文

### 4. 质量控制

**人工审查点**:
1. 文献筛选（人工）
2. 分类结果（AI + 人工审查）
3. 摘要质量（AI + 人工修正）
4. 引用关系（AI + 人工验证）

## 技术实现

### 依赖

```python
# PDF 解析
import PyPDF2
import pdfplumber

# BibTeX 处理
import bibtexparser

# Zotero API
from pyzotero import zotero

# 文本处理
import anthropic
```

### 核心函数

```python
def import_from_zotero(collection_name):
    """从 Zotero 导入文献"""
    zot = zotero.Zotero(library_id, library_type, api_key)
    items = zot.collection_items(collection_id)
    return process_items(items)

def extract_summary(pdf_path):
    """提取文献摘要"""
    text = extract_text_from_pdf(pdf_path)
    summary = call_claude_api(f"提取以下论文的结构化摘要：\n{text}")
    return summary

def build_citation_graph(papers):
    """构建引用图谱"""
    graph = {"nodes": [], "edges": []}
    for paper in papers:
        graph["nodes"].append(create_node(paper))
        for citation in paper["citations"]:
            graph["edges"].append(create_edge(paper["id"], citation))
    return graph
```

## 与现有系统集成

### 1. 与 literature-mentor Skill 协作

**协作场景**：
- **批量精读报告生成**：literature-manager 管理文献集合，调用 literature-mentor 为每篇文献生成精读报告
- **文献分类优化**：基于 literature-mentor 的深度解读结果，优化文献分类和标签
- **引用图谱增强**：结合 literature-mentor 的方法学分析，构建更精准的引用关系网络

**工作流程**：
```
literature-manager 导入文献集合
    ↓
批量调用 literature-mentor 生成精读报告
    ↓
提取报告中的关键信息（方法、发现、局限）
    ↓
更新文献索引和引用图谱
    ↓
生成文献集合总结报告
```

**使用示例**：
```bash
# 为 Zotero 集合中的所有文献生成精读报告
/research literature batch-review --collection "Coronary CTA Segmentation"

# 输出：
# - 每篇文献的精读报告（.research/literature/reviews/）
# - 更新后的文献索引（.research/literature/index.json）
# - 集合总结报告（.research/literature/collection-summary.md）
```

**集成优势**：
- 自动化文献深度分析
- 提取方法学启发和研究局限
- 构建知识关联网络
- 节省人工精读时间

### 2. 复用知识图谱
- 文献作为图谱节点
- 引用关系作为边
- 与实验、概念节点关联

### 3. 复用上下文归档
- 文献分析结果归档
- 重要发现自动沉淀
- 生成 resolution 格式总结

### 4. 复用推荐系统
- 基于相似度推荐文献
- 基于研究方向推荐
- 基于引用关系推荐

## 参考案例

### Schrödinger 案例
- 计算药物发现公司
- 使用 Claude Code 加速 10 倍
- 从想法到代码：小时级 → 分钟级

### Paper2Agent 项目
- 斯坦福大学
- 论文转化为可交互 AI Agent
- 3 小时生成 22 个工具

### FutureHouse 案例
- 生物信息学咨询公司
- 分析论文图表
- 自动生成数据处理脚本

---

**核心原则**: AI 是信息加工器，人类负责质量把关
**设计理念**: 基于 Vibe Researching 范式
**参考项目**: medical-imaging-review skill

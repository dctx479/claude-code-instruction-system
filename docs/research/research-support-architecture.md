# 科研支持系统 - 架构设计

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    科研工作流编排层                          │
│  - 任务分解与调度                                            │
│  - Agent 协作编排                                            │
│  - 进度追踪与报告                                            │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        │            │            │            │
        ▼            ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 文献管理     │ │ 论文写作     │ │ 实验记录     │ │ 知识管理     │
│ Agent        │ │ Agent        │ │ Agent        │ │ Agent        │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        │            │            │            │
        └────────────┴────────────┴────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────────┐  ┌──────────────────────┐
│   知识存储层          │  │   工具集成层          │
│ - 文献数据库          │  │ - Zotero/Mendeley    │
│ - 实验记录库          │  │ - LaTeX/Overleaf     │
│ - 知识图谱            │  │ - Jupyter Notebook   │
│ - 上下文归档          │  │ - Git                │
└──────────────────────┘  └──────────────────────┘
```

## 核心 Agent 设计

### 1. Literature Manager Agent (文献管理)

**职责**:
- 文献导入和解析（PDF/BibTeX）
- 自动分类和标签
- 智能摘要提取
- 相关文献推荐
- 引用关系图谱

**工具**:
- PDF 解析器
- BibTeX 处理
- 文本摘要模型
- 相似度计算

**输出**:
- `.research/literature/` - 文献库
- `.research/literature/index.json` - 文献索引
- `.research/literature/graph.json` - 引用图谱

### 2. Paper Writing Assistant Agent (论文写作)

**职责**:
- 结构化写作辅助（Introduction/Method/Results/Discussion）
- LaTeX/Markdown 格式化
- 引用管理
- 语言润色
- 图表生成建议

**工具**:
- LaTeX 模板
- 引用格式化
- 语法检查
- 图表工具

**输出**:
- `.research/papers/` - 论文草稿
- `.research/papers/{title}/` - 单篇论文目录
  - `draft.tex` - LaTeX 源文件
  - `references.bib` - 引用文件
  - `figures/` - 图表目录

### 3. Experiment Logger Agent (实验记录)

**职责**:
- 结构化实验记录
- 参数版本管理
- 结果追踪
- 实验复现指南生成
- 数据可视化

**工具**:
- 实验模板
- 数据版本控制
- 可视化工具
- Jupyter Notebook 集成

**输出**:
- `.research/experiments/` - 实验记录
- `.research/experiments/{exp_id}/` - 单次实验
  - `config.json` - 实验配置
  - `log.md` - 实验日志
  - `results/` - 结果数据
  - `reproduce.sh` - 复现脚本

### 4. Knowledge Graph Agent (知识图谱)

**职责**:
- 构建文献-概念-实验关系网络
- 概念提取和关联
- 研究脉络可视化
- 知识演化追踪

**工具**:
- NER（命名实体识别）
- 关系抽取
- 图数据库
- 可视化工具

**输出**:
- `.research/knowledge-graph.json` - 知识图谱
- `.research/concepts/` - 概念库
- `.research/timeline.json` - 研究时间线

### 5. Research Progress Tracker Agent (进展追踪)

**职责**:
- 自动生成进展报告
- 里程碑追踪
- 任务管理
- 团队协作支持

**工具**:
- 报告模板
- 任务调度
- 协作工具

**输出**:
- `.research/progress/` - 进展报告
- `.research/milestones.json` - 里程碑
- `.research/tasks.json` - 任务列表

## 数据结构设计

### 文献索引 (literature/index.json)

```json
{
  "papers": [
    {
      "id": "paper-001",
      "title": "论文标题",
      "authors": ["作者1", "作者2"],
      "year": 2026,
      "venue": "会议/期刊",
      "tags": ["标签1", "标签2"],
      "summary": "自动生成的摘要",
      "key_concepts": ["概念1", "概念2"],
      "citations": ["paper-002", "paper-003"],
      "file_path": "literature/papers/paper-001.pdf"
    }
  ]
}
```

### 实验记录 (experiments/{exp_id}/config.json)

```json
{
  "experiment_id": "exp-001",
  "title": "实验标题",
  "date": "2026-01-22",
  "hypothesis": "研究假设",
  "method": "实验方法",
  "parameters": {
    "learning_rate": 0.001,
    "batch_size": 32
  },
  "results": {
    "accuracy": 0.95,
    "loss": 0.05
  },
  "conclusion": "实验结论",
  "related_papers": ["paper-001"],
  "reproducible": true
}
```

### 知识图谱 (knowledge-graph.json)

```json
{
  "nodes": [
    {"id": "paper-001", "type": "paper", "label": "论文标题"},
    {"id": "concept-001", "type": "concept", "label": "概念名称"},
    {"id": "exp-001", "type": "experiment", "label": "实验标题"}
  ],
  "edges": [
    {"from": "paper-001", "to": "concept-001", "type": "introduces"},
    {"from": "exp-001", "to": "concept-001", "type": "validates"},
    {"from": "paper-001", "to": "paper-002", "type": "cites"}
  ]
}
```

## 与现有系统集成

### 1. 复用上下文归档系统
- 实验记录使用相同的归档机制
- 自动提炼实验中的关键发现
- 生成 resolution 格式的实验总结

### 2. 扩展知识图谱
- 在现有图谱基础上添加科研节点类型
- 文献、概念、实验作为新节点类型
- 复用图谱构建和可视化工具

### 3. Agent 编排
- 科研 Agent 纳入编排系统
- 支持复杂科研任务的自动分解
- 多 Agent 协作完成论文写作

### 4. 记忆系统
- 文献摘要存入长期记忆
- 实验结果自动同步到 memory/
- 研究进展持久化

## 工作流示例

### 场景 1: 文献综述

```bash
# 1. 导入文献
/research literature import papers/*.pdf

# 2. 自动分类和摘要
/research literature analyze

# 3. 生成引用图谱
/research literature graph

# 4. 生成综述大纲
/research paper outline "Literature Review on Deep Learning"
```

### 场景 2: 实验记录

```bash
# 1. 创建实验记录
/research experiment create "Baseline Model Training"

# 2. 记录实验配置
/research experiment config --lr 0.001 --batch-size 32

# 3. 记录实验结果
/research experiment result --accuracy 0.95

# 4. 生成复现脚本
/research experiment reproduce
```

### 场景 3: 论文写作

```bash
# 1. 创建论文项目
/research paper create "My Research Paper"

# 2. 生成结构
/research paper structure

# 3. 写作辅助
/research paper write introduction

# 4. 引用管理
/research paper cite paper-001

# 5. 导出 LaTeX
/research paper export latex
```

## 技术栈

### 核心技术
- Python 3.10+
- Anthropic API (Claude)
- SQLite (文献数据库)
- NetworkX (图谱)
- Matplotlib/Plotly (可视化)

### 可选集成
- Zotero API
- LaTeX/Overleaf API
- Jupyter Notebook
- Git

## 实施计划

### Phase 1: 核心功能 (1-2 周)
- ✅ 文献管理 Agent
- ✅ 实验记录系统
- ✅ 基础知识图谱

### Phase 2: 写作支持 (1 周)
- ✅ 论文写作助手
- ✅ LaTeX 集成
- ✅ 引用管理

### Phase 3: 高级功能 (1 周)
- ✅ 进展追踪
- ✅ 协作支持
- ✅ 可视化工具

---

**设计原则**:
- 最小化实现
- 模块化设计
- 易于扩展
- 与现有系统深度集成

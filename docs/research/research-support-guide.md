# 科研支持系统使用指南

## 概述

基于 **Vibe Researching** 理念，太一元系统提供全方位的科研工作流支持，涵盖文献管理、论文写作、实验追踪、数据分析等核心环节。

### 核心理念

> **AI 是高质量信息加工器，而非生成器**

- **人类角色**：提出问题、设定方向、把控质量、提供高质量输入
- **AI 角色**：执行层面工作（文献综述、数据分析、论文写作）
- **协作模式**：人机协作，各司其职，效率提升 10-20 倍

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    科研工作流编排层                          │
│  - 任务分解与调度                                            │
│  - Agent 协作编排                                            │
│  - 进度追踪与报告                                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┬───────────────┐
        │               │               │               │
        ▼               ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Literature   │ │ Paper        │ │ Experiment   │ │ Data         │
│ Manager      │ │ Writing      │ │ Logger       │ │ Analyst      │
│ 文献管理     │ │ 论文写作     │ │ 实验追踪     │ │ 数据分析     │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        │               │               │               │
        ▼               ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────┐
│                    外部工具集成层                            │
│  - Zotero-MCP (文献库)                                       │
│  - arXiv/PubMed MCP (开源文献)                               │
│  - Jupyter Notebook (数据分析)                               │
│  - Pandoc (格式转换)                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 核心功能

### 1. 文献管理（Literature Manager）

**功能**：
- 文献导入和分类
- 智能摘要提取
- 引用图谱构建
- 相关文献推荐

**使用**：
```bash
# 搜索文献
/agents literature-manager "搜索 Zotero 中关于深度学习医学图像分割的论文"

# 生成摘要
/agents literature-manager "总结 'Coronary CTA' 集合的所有论文"

# 引用分析
/agents literature-manager "分析最近添加的 10 篇论文的引用关系"
```

**集成**：
- Zotero-MCP：访问个人文献库
- arXiv/PubMed MCP：搜索开源文献

---

### 2. 论文写作（Paper Writing Assistant）

**功能**：
- 文献综述生成
- 研究论文撰写
- 写作风格学习
- 自动引用管理

**使用**：
```bash
# 生成文献综述
/literature-review "Deep Learning for Medical Image Segmentation" \
  --zotero-collection "Medical Imaging AI" \
  --style nature \
  --output reviews/medical-imaging-review.md
```

**工作流**：
1. 准备高质量文献（Zotero）
2. 提供顶级期刊范本
3. AI 学习写作风格
4. 生成综述框架（人工审核）
5. AI 撰写初稿
6. 人工审核和润色

**详见**：[完整示例](../examples/research-workflow-example.md)

---

### 3. 实验追踪（Experiment Logger）

**功能**：
- 结构化实验记录
- 参数和配置管理
- 结果追踪和对比
- 复现指南生成

**使用**：
```bash
# 创建实验
/experiment-track create --name "ResNet50-CTA-Segmentation" \
  --description "使用 ResNet50 进行冠脉分割"

# 记录配置
/experiment-track config --exp-id exp-001 --file config.yaml

# 记录结果
/experiment-track result --exp-id exp-001 --metrics metrics.json

# 生成报告
/experiment-track report --exp-id exp-001 --output report.md

# 对比实验
/experiment-track compare --exp-ids exp-001,exp-002,exp-003
```

**自动记录**：
- Git commit hash
- 环境依赖
- 随机种子
- 硬件信息
- 执行时间

---

### 4. 数据分析（Data Analyst）

**功能**：
- 数据预处理和清洗
- 统计分析和假设检验
- 高质量可视化
- 结果解读

**使用**：
```bash
# 数据分析
/agents data-analyst "分析实验结果，进行 t-test 检验，生成图表"

# 可视化
/agents data-analyst "生成符合 Nature 期刊要求的性能对比图"

# 统计报告
/agents data-analyst "计算效应量和置信区间，生成统计报告"
```

**工具集成**：
- Python: pandas, numpy, scipy, statsmodels
- Jupyter Notebook: 交互式分析
- LaTeX: 公式和表格生成

---

### 3.5 创新组合模式（Research Innovation Explorer）

适用场景：
- 从多篇论文中寻找可行的新方向
- 做跨领域机制迁移
- 从大量候选方案中快速筛选可验证 idea

最小流程：
1. **抽取机制**：不是只摘录论文结论，而是提炼可迁移机制、前提条件和失败边界。
2. **跨域映射**：把机制映射到目标问题，生成两两或多维组合假设，排除明显冲突组合。
3. **快速验证**：用补充检索、开源实现、实验入口或逻辑约束筛掉不靠谱方案，保留 shortlist。

推荐搭配：
- `literature-mentor`：负责单篇论文精读、机制提炼、研究空白识别
- `deep-research`：负责广泛检索、组合发现、证据补强和 shortlist 输出
- `experiment-logger`：负责把 shortlist 转成可执行验证计划

推荐输出结构：
- 已有发现
- 可迁移机制
- 组合假设
- 风险 / 验证点
- shortlist

---

## 快速开始

### 第一步：安装 Zotero-MCP

参考：[Zotero-MCP 集成指南](../integrations/zotero-mcp-setup.md)

1. 安装 Zotero
2. 获取 API Key
3. 配置 MCP Server
4. 重启 Claude Code

### 第二步：准备文献

1. 在 Zotero 中创建集合
2. 收集高质量闭源期刊论文
3. 导入 PDF 并提取元数据
4. 添加标签和分类

### 第三步：开始科研工作流

选择适合的场景：

**场景 A：撰写文献综述**
```bash
/literature-review "你的研究主题" \
  --zotero-collection "你的文献集合" \
  --style nature
```

**场景 B：实验追踪**
```bash
/experiment-track create --name "实验名称"
```

**场景 C：数据分析**
```bash
/agents data-analyst "分析任务描述"
```

---

## 最佳实践

### 1. 文献管理
✅ **推荐**：
- 优先收集闭源期刊高质量论文（IF > 3.0）
- 使用 Zotero Collections 分类管理
- 补充开源数据库（arXiv, PubMed）
- 定期更新和清理文献库

❌ **避免**：
- 把所有 PDF 放本地目录
- 依赖 AI 网络搜索
- 不整理文献元数据

### 2. 论文写作
✅ **推荐**：
- 提供顶级期刊范本学习风格
- 框架确定后再开始写作
- 人工审核每个关键环节
- 把 AI 当作信息加工器

❌ **避免**：
- 让 AI 凭空生成内容
- 跳过框架审核环节
- 完全信任 AI 输出
- 忽视人工润色

### 3. 实验管理
✅ **推荐**：
- 每个实验都记录完整配置
- 使用版本控制（Git）
- 记录随机种子保证可复现
- 定期备份实验数据

❌ **避免**：
- 只记录成功实验
- 忽略环境依赖
- 不记录失败原因

### 4. 数据分析
✅ **推荐**：
- 使用 Jupyter Notebook 交互式分析
- 进行适当的统计检验
- 生成符合期刊要求的图表
- 报告置信区间和效应量

❌ **避免**：
- 只报告 p 值
- 过度拟合数据
- 忽略多重比较校正

---

## 真实案例

### 案例 1：医学影像 AI 综述

**背景**：冠脉 CTA 影像深度学习分割方向

**成果**：
- 45 页，13,813 单词
- 113 篇引用文献（全部真实）
- 遵循 Nature 期刊风格
- 3-5 天完成（传统方式需 2-3 个月）

**详见**：[完整工作流示例](../examples/research-workflow-example.md)

### 案例 2：Schrödinger（计算药物发现）

**评价**：
> "Claude Code has become a powerful accelerator for us. For the projects where it fits best, Claude Code allows us to turn ideas into working code in minutes instead of hours, enabling us to move up to 10x faster in some cases."

**效果**：从想法到代码，从小时级缩短到分钟级，某些项目快了 10 倍

### 案例 3：斯坦福 Paper2Agent

**创新**：
- 把论文转化成可交互的 AI Agent
- 相当于给每篇论文配了虚拟通讯作者
- 3 小时生成 22 个可用工具

---

## 工具生态

### 官方工具
- **Claude for Life Sciences**：Benchling, BioRender, PubMed, 10x Genomics
- **single-cell-rna-qc**：单细胞 RNA-seq 质量控制

### 社区工具
- **claude-scientific-skills**：140+ 科研技能（生物信息学、药物发现等）
- **claude-scientific-writer**：假设生成、文献综述、同行评审、基金申请
- **medical-imaging-review**：医学影像综述生成 skill

### MCP 服务器
- **Zotero-MCP**：文献库访问
- **arXiv-MCP**：arXiv 论文搜索
- **PubMed-MCP**：PubMed 文献搜索

---

## 注意事项

### 学术诚信
- ✅ 所有引用必须真实可查
- ✅ 人工审核 AI 生成内容
- ✅ 标注 AI 辅助写作（如期刊要求）
- ❌ 不得编造数据和引用
- ❌ 不得抄袭和自我抄袭

### 质量控制
- ✅ 提供高质量输入（文献、数据）
- ✅ 人工审核关键环节（框架、结论）
- ✅ 验证统计分析正确性
- ❌ 不完全依赖 AI
- ❌ 不跳过人工审核

### 局限性
- AI 在执行层面强，但判断层面有短板
- 需要人类把关：方法论透明度、学术诚信、批判性思维
- Vibe Researching 是人机协作，而非 AI 替代

---

## 相关资源

### 文档
- [Zotero-MCP 集成指南](../integrations/zotero-mcp-setup.md)
- [文献综述工作流示例](../examples/research-workflow-example.md)
- [Agent 定义](../agents/research/)
- [命令文档](../commands/research/)

### 外部链接
- [Vibe Researching 播客](https://a16z.com/podcast/)
- [claude-scientific-skills](https://github.com/K-Dense/claude-scientific-skills)
- [medical-imaging-review](https://github.com/luwill/research-skills)
- [Zotero 官方文档](https://www.zotero.org/support/)

### 命令速查
```bash
# 文献综述
/literature-review <主题> --zotero-collection <集合> --style <风格>

# 实验追踪
/experiment-track create --name <名称>
/experiment-track config --exp-id <ID> --file <配置文件>
/experiment-track result --exp-id <ID> --metrics <结果文件>
/experiment-track report --exp-id <ID>

# Agent 调用
/agents literature-manager <任务>
/agents paper-writing-assistant <任务>
/agents experiment-logger <任务>
/agents data-analyst <任务>
```

---

## 反馈与改进

如有问题或建议，请：
1. 查看 [FAQ](../faq.md)
2. 提交 Issue 到项目仓库
3. 参与社区讨论

**持续改进**：系统会根据使用反馈自动进化和优化。

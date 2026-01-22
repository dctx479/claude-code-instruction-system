# 科研工作流示例

## 场景：撰写医学影像 AI 文献综述

### 背景
研究方向：冠脉 CTA 影像深度学习分割
目标：发表一篇高质量文献综述到一区或二区期刊

---

## 完整工作流

### 第一步：准备文献（人工）

#### 1.1 收集闭源期刊文献
在以下数据库搜索并下载论文：
- IEEE Xplore
- Springer
- Nature 系列
- Elsevier (ScienceDirect)

**搜索关键词**：
- "coronary artery segmentation deep learning"
- "CTA image analysis CNN"
- "cardiovascular imaging AI"

**筛选标准**：
- 近 5 年发表
- 影响因子 > 3.0
- 引用次数 > 20

#### 1.2 导入 Zotero
1. 创建集合："Coronary CTA Segmentation"
2. 导入所有 PDF
3. 自动提取元数据
4. 添加标签：`deep-learning`, `segmentation`, `CTA`

#### 1.3 准备范本综述
找 1-2 篇顶级期刊综述：
- Nature Reviews Cardiology (IF: 44.2)
- JACC: Cardiovascular Imaging (IF: 12.8)

---

### 第二步：学习写作风格（AI）

```bash
# 切换到 plan 模式
# 提供范本综述 PDF

"请分析这篇 Nature Reviews Cardiology 的综述，总结其写作风格、结构编排和引用规范，生成写作指南"
```

**输出**：`.research/WRITING-GUIDE.md`

**内容包括**：
- 标题和摘要风格
- 章节结构模式
- 图表使用规范
- 引用格式要求
- 语言风格特点

---

### 第三步：生成综述框架（AI + 人工审核）

```bash
/literature-review "Deep Learning for Coronary Artery Segmentation in CTA Images" \
  --zotero-collection "Coronary CTA Segmentation" \
  --style nature
```

**AI 自动执行**：
1. 访问 Zotero 文献库
2. 搜索 arXiv 和 PubMed 开源文献
3. 分析文献主题分布
4. 生成综述框架

**输出**：`.research/REVIEW-PLAN.md`

**框架示例**：
```markdown
# 综述框架

## 1. Introduction
- 冠心病流行病学背景
- CTA 成像技术发展
- AI 在医学影像中的应用
- 综述目标和范围

## 2. Coronary Artery Anatomy and CTA Imaging
- 冠脉解剖结构
- CTA 成像原理和挑战
- 图像质量影响因素

## 3. Deep Learning Fundamentals
- CNN 架构演进
- U-Net 及其变体
- Transformer 在医学影像中的应用

## 4. Segmentation Methods
### 4.1 Traditional Methods (简要回顾)
### 4.2 2D CNN Methods
### 4.3 3D CNN Methods
### 4.4 Hybrid Approaches
### 4.5 Multi-task Learning

## 5. Datasets and Benchmarks
- 公开数据集
- 评估指标
- 性能对比

## 6. Clinical Applications
- 狭窄检测
- 斑块分析
- 手术规划

## 7. Challenges and Future Directions
- 数据稀缺和标注成本
- 模型可解释性
- 临床验证
- 多中心泛化

## 8. Conclusion
```

**人工审核**：
- ✅ 检查框架逻辑性
- ✅ 调整章节顺序
- ✅ 补充遗漏主题
- ✅ 确认符合目标期刊风格

---

### 第四步：补充外部知识（可选）

使用 ChatGPT 和 Gemini 的 Deep Research：

**提示词**：
```
"请对冠脉 CTA 影像深度学习分割方向进行深度调研，包括：
1. 最新技术进展（2024-2026）
2. 主要研究团队和机构
3. 临床应用现状
4. 未来研究方向"
```

**整合**：
```bash
# 将两份 Deep Research 报告提供给 Claude Code
"请基于这两份调研报告，更新 WRITING-GUIDE.md 和 REVIEW-PLAN.md"
```

---

### 第五步：撰写综述（AI）

```bash
# 退出 plan 模式，开始执行

"请按照 REVIEW-PLAN.md 的框架，基于 Zotero 文献库和开源文献，撰写完整的文献综述"
```

**AI 自动执行**：
1. 逐章节撰写内容
2. 自动引用文献（来自 Zotero + arXiv + PubMed）
3. 生成图表占位符
4. 遵循 Nature 写作风格
5. 保持学术严谨性

**预计时间**：30-60 分钟

**输出**：
- `reviews/coronary-cta-segmentation-review.md`（Markdown 初稿）
- `references.bib`（BibTeX 引用）

---

### 第六步：格式转换

```bash
# 使用 pandoc 转换为 Word
pandoc reviews/coronary-cta-segmentation-review.md \
  -o reviews/coronary-cta-segmentation-review.docx \
  --bibliography references.bib \
  --csl nature.csl
```

**输出**：45 页，13,813 单词，113 篇引用文献

---

### 第七步：人工审核和润色

#### 7.1 内容审核
- ✅ 检查事实准确性
- ✅ 验证引用正确性
- ✅ 补充最新文献（如有）
- ✅ 删除冗余内容

#### 7.2 图表补充
- 创建技术路线图
- 绘制性能对比表
- 设计方法分类图
- 添加临床应用示意图

#### 7.3 语言润色
- 修正语法错误
- 优化句式表达
- 统一术语使用
- 增强可读性

#### 7.4 格式调整
```bash
# 根据目标期刊调整引用格式
"请将参考文献格式调整为 IEEE 风格"
```

---

### 第八步：投稿准备

#### 8.1 选择目标期刊
- Medical Image Analysis (IF: 10.7)
- IEEE Transactions on Medical Imaging (IF: 10.6)
- Computerized Medical Imaging and Graphics (IF: 5.7)

#### 8.2 准备投稿材料
- Cover Letter
- Highlights（3-5 条）
- Graphical Abstract
- Author Information

#### 8.3 最终检查
- [ ] 字数符合要求
- [ ] 图表清晰规范
- [ ] 引用格式正确
- [ ] 无抄袭和自我抄袭
- [ ] 所有作者确认

---

## 关键成功因素

### 1. 高质量输入
✅ **正确做法**：
- 手动收集闭源期刊高质量论文
- 使用 Zotero 统一管理
- 补充开源数据库（arXiv, PubMed）

❌ **错误做法**：
- 直接让 AI 搜索生成
- 把所有 PDF 放本地目录
- 依赖 AI 的网络搜索

### 2. 框架先行
✅ **正确做法**：
- AI 生成框架后人工审核
- 确保逻辑清晰、结构合理
- 参考顶级期刊范本

❌ **错误做法**：
- 让 AI 直接写全文
- 不审核框架就开始写作

### 3. 人机协作
✅ **正确做法**：
- 人类：提供文献、确定框架、把控质量
- AI：信息整合、结构化编排、初稿撰写

❌ **错误做法**：
- 完全依赖 AI
- 不进行人工审核

---

## 预期成果

### 质量指标
- 篇幅：40-50 页
- 字数：12,000-15,000
- 引用：100-150 篇
- 图表：8-12 个

### 时间成本
- 文献收集：2-3 天（人工）
- 框架设计：2-4 小时（AI + 人工）
- 初稿撰写：1-2 小时（AI）
- 审核润色：1-2 天（人工）
- **总计：3-5 天**

### 对比传统方式
- 传统：2-3 个月
- AI 辅助：3-5 天
- **效率提升：10-20 倍**

---

## 经验总结

### 核心理念
> **AI 是高质量信息加工器，而非生成器**
> "Garbage in, Garbage out" - 输入质量决定输出质量

### 最佳实践
1. 投喂高质量文献（闭源期刊为主）
2. 提供顶级期刊范本学习风格
3. 框架确定后再开始写作
4. 人工审核每个关键环节
5. 把 AI 当作助手，而非替代

### 避免陷阱
- ❌ 让 AI 凭空生成内容
- ❌ 不提供高质量文献
- ❌ 跳过框架审核环节
- ❌ 完全信任 AI 输出
- ❌ 忽视人工润色

---

## 相关资源

### 工具
- [Zotero](https://www.zotero.org/) - 文献管理
- [Zotero-MCP](../integrations/zotero-mcp-setup.md) - Claude Code 集成
- [Pandoc](https://pandoc.org/) - 格式转换

### 参考
- [Vibe Researching 理念](https://a16z.com/podcast/)
- [claude-scientific-skills](https://github.com/K-Dense/claude-scientific-skills)
- [medical-imaging-review skill](https://github.com/luwill/research-skills)

### 命令
- `/literature-review` - 文献综述生成
- `/experiment-track` - 实验追踪
- `/agents research/*` - 科研 Agent

# /literature-batch-review - 批量文献精读

## 功能描述

批量处理 Zotero 集合中的文献，为每篇文献生成完整的精读报告。自动识别文献类型，采用对应模板，并生成汇总索引。

## 使用场景

- 文献综述写作准备
- 批量处理收藏的文献
- 建立文献知识库
- 定期整理阅读清单

## 命令格式

```bash
/literature-batch-review <Zotero集合> [选项]
```

## 参数说明

### 必需参数

- `<Zotero集合>`: Zotero 集合名称或 ID

### 可选参数

- `--output <路径>`: 指定报告输出目录（默认：./literature-reports/）
- `--format <格式>`: 输出格式（markdown / pdf / docx，默认：markdown）
- `--save-to-zotero`: 将报告保存回 Zotero 笔记
- `--workers <数量>`: 并行处理的 worker 数量（默认：3）
- `--filter <类型>`: 仅处理特定类型文献（research / review / all，默认：all）
- `--generate-index`: 生成汇总索引文件

## 使用示例

### 示例 1: 批量处理 Zotero 集合

```bash
/literature-batch-review "Deep Learning Papers"
```

**输出**：
```
./literature-reports/
├── index.md                                    # 汇总索引
├── 001-attention-is-all-you-need.md           # 报告 1
├── 002-deep-residual-learning.md              # 报告 2
├── 003-bert-pretraining.md                    # 报告 3
└── ...
```

### 示例 2: 并行处理并保存到 Zotero

```bash
/literature-batch-review "AI for Biology" --workers 5 --save-to-zotero
```

**效果**：
- 使用 5 个 worker 并行处理
- 每篇文献生成精读报告
- 报告自动保存到 Zotero 笔记

### 示例 3: 仅处理综述型论文并生成 PDF

```bash
/literature-batch-review "Survey Papers" --filter review --format pdf --generate-index
```

**输出**：
- 仅处理 Review Article
- 生成 PDF 格式报告
- 生成汇总索引（包含评分排序）

## 工作流程

```
用户输入 Zotero 集合
    ↓
获取集合中的所有文献
    ↓
应用过滤器（可选）
    ↓
并行处理（多 worker）
    ├─ Worker 1: 文献 1, 4, 7, ...
    ├─ Worker 2: 文献 2, 5, 8, ...
    └─ Worker 3: 文献 3, 6, 9, ...
    ↓
每个 Worker 执行：
    ├─ 获取文献全文
    ├─ 识别文献类型
    ├─ 生成精读报告
    └─ 保存报告
    ↓
生成汇总索引
    ├─ 按评分排序
    ├─ 按类型分组
    └─ 生成统计信息
    ↓
（可选）保存到 Zotero
```

## 汇总索引结构

```markdown
# 文献精读报告汇总

## 统计信息

- 总文献数：20 篇
- Research Article：15 篇
- Review Article：5 篇
- 平均评分：7.8/10
- 处理时间：45 分钟

## 高分文献（≥8.0）

| 序号 | 标题 | 类型 | 评分 | 报告链接 |
|------|------|------|------|---------|
| 1 | Attention Is All You Need | Research | 9.5 | [查看报告](./001-attention-is-all-you-need.md) |
| 2 | BERT: Pre-training | Research | 9.0 | [查看报告](./002-bert-pretraining.md) |
| ... | ... | ... | ... | ... |

## 按类型分组

### Research Article（15 篇）

1. [Attention Is All You Need](./001-attention-is-all-you-need.md) - 9.5/10
2. [Deep Residual Learning](./002-deep-residual-learning.md) - 8.5/10
...

### Review Article（5 篇）

1. [A Survey on Deep Learning](./015-survey-deep-learning.md) - 9.0/10
2. [Transformers in NLP](./016-transformers-nlp.md) - 8.0/10
...

## 研究主题分布

- 深度学习：8 篇
- 自然语言处理：6 篇
- 计算机视觉：4 篇
- 强化学习：2 篇

## 推荐阅读顺序

1. 先读综述：建立领域全景
   - [A Survey on Deep Learning](./015-survey-deep-learning.md)
   - [Transformers in NLP](./016-transformers-nlp.md)

2. 再读经典：理解核心方法
   - [Attention Is All You Need](./001-attention-is-all-you-need.md)
   - [Deep Residual Learning](./002-deep-residual-learning.md)

3. 最后读应用：学习实践技巧
   - [BERT: Pre-training](./002-bert-pretraining.md)
   - ...
```

## 并行处理策略

### SWARM 模式（默认）

- 适合大规模批量处理（>10 篇）
- 多个 haiku worker 并行
- 预期加速：5-10x

### 配置建议

| 文献数量 | 推荐 Workers | 预期时间 |
|---------|-------------|---------|
| 1-5 篇 | 1 | 5-10 分钟 |
| 6-20 篇 | 3 | 15-30 分钟 |
| 21-50 篇 | 5 | 30-60 分钟 |
| 50+ 篇 | 10 | 1-2 小时 |

## 进度监控

批量处理时会显示实时进度：

```
[████████░░] 80% (16/20 completed)

Workers 状态：
- worker-1: 处理中 ✓ (文献 17)
- worker-2: 已完成 ✓
- worker-3: 处理中 ✓ (文献 18)

最近完成：
- [14:30] 文献 16: "Attention Is All You Need" (9.5/10)
- [14:28] 文献 15: "Deep Residual Learning" (8.5/10)
- [14:25] 文献 14: "BERT: Pre-training" (9.0/10)

预计剩余时间：5 分钟
```

## 错误处理

### 自动重试

- 文献获取失败 → 重试 3 次
- Worker 超时 → 自动重启
- 报告生成失败 → 记录错误并继续

### 错误报告

```markdown
## 处理失败的文献

| 序号 | 标题 | 错误原因 | 建议 |
|------|------|---------|------|
| 5 | Paper Title | 无法获取全文 | 手动下载 PDF |
| 12 | Another Paper | 文献类型无法识别 | 手动指定类型 |
```

## 与其他命令的区别

| 命令 | 处理数量 | 模式 | 适用场景 |
|------|---------|------|---------|
| `/literature-review` | 1 篇 | 交互模式 | 深度学习 |
| `/literature-review-quick` | 1 篇 | 报告模式 | 快速调研 |
| `/literature-batch-review` | 多篇 | 批量报告 | 批量处理 |

## 集成点

- **literature-mentor skill**: 核心解读引擎
- **Zotero MCP**: 文献获取和笔记保存
- **literature-manager agent**: 文献分类和管理
- **orchestrator agent**: 并行任务调度（SWARM 模式）

## 最佳实践

### 文献准备

1. 在 Zotero 中创建专门的集合
2. 确保文献有完整的元数据
3. 尽量附加全文 PDF
4. 使用标签分类文献

### 批量处理

1. 先处理小批量（5-10 篇）测试效果
2. 根据机器性能调整 workers 数量
3. 定期检查进度和错误报告
4. 处理完成后验证报告质量

### 报告管理

1. 使用统一的输出目录
2. 定期备份报告文件
3. 利用汇总索引快速查找
4. 将高质量报告保存到 Zotero

## 注意事项

1. **性能影响**：大量并行处理会消耗较多 API 配额
2. **文献质量**：报告质量取决于文献全文的完整性
3. **时间估算**：实际处理时间取决于文献长度和复杂度
4. **错误处理**：部分文献处理失败不会影响其他文献

## 相关文档

- Skill 定义：`C:\Users\ASUS\.claude\skills\literature-mentor\SKILL.md`
- 单篇快速：`commands/research/literature-review-quick.md`
- 编排模式：`workflows/orchestration/orchestration-patterns.md`（SWARM 模式）
- Zotero 集成：`integrations/zotero-mcp-setup.md`

## 预期效果

- **效率提升**：批量处理 20 篇论文/周
- **质量保证**：每篇文献都有完整报告
- **知识管理**：汇总索引便于查找和引用
- **时间节省**：并行处理节省 5-10 倍时间

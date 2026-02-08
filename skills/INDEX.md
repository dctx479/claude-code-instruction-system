# Skills 索引

> 本文件用于渐进式披露机制，仅加载 Skills 元数据，节省 Token 开销。

## 研究类 Skills (Research)

| Skill | 描述 | 触发词 | 位置 |
|-------|------|--------|------|
| literature-mentor | 文献深度解读，支持交互模式和报告模式 | 解读论文, 生成精读报告, 快速调研 | .claude/skills/literature-mentor/ |
| deep-research | 深度研究，Lead Agent + Subagent 并行调研 | deep-research | .claude/skills/deep-research/ |
| exa-research | 企业与市场研究，基于 Exa 搜索引擎 | 研究竞争对手, 分析行业 | .claude/skills/exa-research/ |
| brightdata-research | 电商平台深度调研，反反爬虫支持 | 电商调研, 畅销排行 | .claude/skills/brightdata-research/ |
| social-media-research | 跨平台社媒研究，12+ 平台覆盖 | 舆情监控, KOL 分析 | .claude/skills/social-media-research/ |
| paper-revision | 论文风格修改，技术准确性保持 | 修改论文风格 | .claude/skills/paper-revision/ |

## 产品类 Skills (Product)

| Skill | 描述 | 触发词 | 位置 |
|-------|------|--------|------|
| market-insight | 市场洞察，三段式用户画像与产品机会分析 | /insight | .claude/skills/market-insight/ |

## AI/ML Skills

| Skill | 描述 | 触发词 | 位置 |
|-------|------|--------|------|
| pytorch | PyTorch 深度学习框架 | pytorch, 深度学习 | .claude/skills/pytorch/ |
| pandas | pandas 数据分析库 | pandas, 数据分析 | .claude/skills/pandas/ |

## 使用说明

### 渐进式披露机制

1. **启动时**：仅加载本索引文件（~2KB）
2. **任务匹配**：根据用户请求匹配相关 Skills
3. **按需加载**：仅加载激活 Skills 的完整 SKILL.md

### Token 节省

- 传统方式：加载所有 Skills = 50 × 2K = 100K tokens
- 渐进式：加载索引 = 2K tokens
- **节省率**：98%

### Skill 组合模式

- **社媒 + 深度调研** = 社媒调研智能体
- **社媒 + 市场洞察** = 消费者画像
- **电商 + 企业研究** = 全链路竞争分析
- **literature-mentor + paper-writing-assistant** = 文献综述写作
- **literature-mentor + experiment-logger** = 实验设计与执行

## 版本信息

- **版本**：1.0.0
- **更新日期**：2026-02-08
- **Skills 总数**：9

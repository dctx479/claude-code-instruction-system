# Skills 集成指南

> **设计理念**: Skills 是自动激活的能力扩展单元，Claude 会根据任务上下文自动发现和激活相关 Skills

## 什么是 Skills？

**Skills** 是 Claude Code 的能力扩展机制，与 Agents 和 Commands 的区别：

| 类型 | 职责 | 触发方式 | 示例 |
|------|------|----------|------|
| **Skills** | 知识包，能力增强 | 自动发现 | tdd-enforcer, context-optimizer |
| **Agents** | 执行单元，任务处理 | Orchestrator 调度 | spec-writer, qa-reviewer |
| **Commands** | 显式用户操作 | 手动调用 | /commit, /review |

**关系**：
- Skills 可以调用 Agents
- Agents 可以激活 Skills
- Commands 可以触发 Orchestrator，进而调度 Agents 和 Skills

---

## 渐进式披露机制

Skills 采用与 Agents 相同的渐进式披露机制，节省 70-90% Token：

```
阶段 1: 会话启动
├─ 加载所有 Skills 的 metadata (name + description)
├─ Token 成本: ~100 tokens/skill
└─ 总成本: 50 skills × 100 tokens = 5K tokens

阶段 2: 任务匹配
├─ Claude 分析用户请求
├─ 匹配相关 Skills（基于 description）
└─ 决定是否激活

阶段 3: 按需加载
├─ 仅加载激活 Skills 的完整内容
├─ Token 成本: ~2K tokens/skill
└─ 节省: 90% (仅加载 2-3 个相关 Skills)
```

---

## 已集成的 Skills

### 核心 Skills（项目内置）

| Skill | 描述 | 类别 |
|-------|------|------|
| **observability** | AI 思维日志可观测性系统，实时记录推理过程、决策点和执行状态，帮助人类理解 AI 决策过程 | system |
| **deep-research** | 深度研究技能，Lead Agent + Subagent 并行调研，支持引用验证、置信度评分和领域扩展 | research |
| **question-refiner** | 研究查询精炼器，验证和结构化用户查询，输出标准化 Structured Research Prompt | research |
| **exa-research** | 企业与市场研究技能，基于 Exa 搜索引擎进行公司情报、竞争对手分析和市场研究 | research |
| **brightdata-research** | 电商平台深度调研，基于 Bright Data MCP 的反反爬虫市场情报收集 | research |
| **social-media-research** | 跨平台社媒数据研究，基于 TikHub MCP 的舆情监控、KOL 分析和内容趋势洞察 | research |
| **literature-mentor** | 文献深度解读助手，像导师一样交互式解读论文 | research |
| **paper-revision** | 论文/技术文档修改助手，风格转换 | research |
| **market-insight** | 市场洞察分析助手，三段式框架快速识别用户画像、情绪动机和产品机会 | product |
| **pytorch** | PyTorch 深度学习框架 | ai-ml |
| **pandas** | pandas 数据分析库 | ai-ml |
| **data-analysis** | 通用数据分析技能 | ai-ml |
| **parallel-explore** | Git Worktree 并行探索，基于 Aha-Loop 方法论为多方案决策创建独立工作树，完整实现后标准化评估选择最优方案 | development |
| **vision-builder** | 愿景构建器，将模糊需求转化为清晰的项目愿景文档（5W1H + SMART），包含目标、范围、成功标准和风险评估 | planning |
| **plan-review** | 计划审查器，对实现计划进行多维度评估（10维度×1-10分），识别风险和改进点，确保计划可执行且完整 | planning |
| **god-oversight** | God Committee 监督能力，独立监控和治理，异常检测和干预 | governance |
| **seedance-prompt** | Seedance 2.0 分镜提示词生成专家，将想法/图片转化为专业的 AI 视频结构化分镜提示词 | creative |
| **seedance-storyboard** | Seedance 2.0 剧本分镜生成器，将小说/故事转化为多集视频剧本和分镜脚本 | creative |
| **frontend-design** | 前端设计与 UI/UX 指导专家，提供布局、交互、配色、可访问性审查（AI 前端设计总监） | design |
| **ui-ux-pro-max** | 最强前端设计知识库，57+ UI 风格、97 配色、57 字体搭配、25+ 图表类型 | design |
| **react-best-practices** | Vercel 官方 React + Next.js 性能优化宝典，45+ 条规则按影响力排序 | development |
| **web-artifacts-builder** | Anthropic 官方 Web Artifacts 构建器，React + Tailwind + shadcn/ui 单文件 HTML 应用 | development |
| **collaborating-with-codex** | 多模型协作，通过后台 Bash 子进程调用 Codex CLI 并行实现代码，Claude 融合审查，优势互补 | development |
| **collaborating-with-gemini** | 多模型协作，通过后台 Bash 子进程调用 Gemini CLI 处理大上下文分析，适合整个代码库扫描 | development |

### 1. claude-scientific-skills (140+ 科研技能)

**来源**: [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills)

**安装方法**:
```bash
# 克隆仓库
git clone https://github.com/K-Dense-AI/claude-scientific-skills.git

# 集成到太一元系统
cp -r claude-scientific-skills/scientific-skills/* .claude/skills/
```

**包含的 Skills**:
- **Machine Learning & AI**: 机器学习算法、模型训练、超参数优化
- **Deep Learning**: CNN、RNN、Transformer、GAN 等深度学习架构
- **Reinforcement Learning**: DQN、PPO、SAC、MADDPG 等强化学习算法
- **Time Series Analysis**: ARIMA、Prophet、LSTM 时间序列预测
- **Model Interpretability**: SHAP、LIME 模型可解释性
- **Data Analysis & Visualization**: pandas、numpy、matplotlib、plotly
- **Python Packages (55+)**: PyTorch、scikit-learn、TensorFlow 等

**使用示例**:
```markdown
# 自动激活 PyTorch Skill
"帮我设计一个图像分类模型，使用 PyTorch"

# 自动激活数据分析 Skill
"分析这个 CSV 文件的统计特征"

# 自动激活时间序列 Skill
"预测未来 30 天的销售额"
```

**预期效果**:
- 科研能力提升 10-20 倍
- 支持 PyTorch、scikit-learn、pandas 等 55+ 库
- 无需额外配置，开箱即用

---

## Skill 标准格式

每个 Skill 必须包含一个 `SKILL.md` 文件，格式如下：

```markdown
---
name: skill-name
description: 简洁的单行描述，用于自动发现匹配
version: 1.0.0
license: MIT
compatibility: claude-code-2.0+
metadata:
  category: development
  tags: [tdd, testing, automation]
---

# Skill 完整说明

## 何时使用此 Skill
[触发条件和适用场景]

## 核心能力
[Skill 提供的具体能力]

## 使用指南
[详细的使用说明和示例]

## 最佳实践
[经验总结和注意事项]

## 参考资料
[相关文档和资源]
```

**关键要素**：
1. **YAML frontmatter**：必须包含 `name` 和 `description`
2. **description**：决定自动发现的准确性（最重要）
3. **结构化内容**：使用 Markdown 标题组织，便于 Claude 快速定位

---

## 创建自定义 Skill

### 方法 1：手动创建

1. 创建目录：`mkdir -p .claude/skills/my-skill`
2. 创建 `SKILL.md`：参考上面的标准格式
3. 添加资源文件（可选）：
   - `REFERENCE.md`：详细文档
   - `scripts/`：可执行脚本
   - `examples/`：示例代码

### 方法 2：使用 skill-writer Skill

```bash
# 安装 skill-writer Skill
# (从 SkillsMP 或社区获取)

# 使用 Claude 生成 Skill
"帮我创建一个 Skill，用于..."
```

### 方法 3：OpenAPI → Skill 转换

对于 API 集成类 Skill，可以使用 OpenAPI 转换工具（即将推出）：

```bash
/convert-openapi openapi.json --name "My API Helper"
```

---

## Skill 管理命令

### 查看已安装的 Skills
```bash
ls .claude/skills/
```

### 测试 Skill
```markdown
# 在对话中测试
"使用 [skill-name] Skill 完成..."
```

### 更新 Skill
```bash
# 重新克隆或下载最新版本
git pull  # 如果是 git 仓库
```

### 卸载 Skill
```bash
rm -rf .claude/skills/skill-name
```

---

## Skill 市场

### 官方 Skills
- [anthropics/skills](https://github.com/anthropics/skills) - 官方 Skills 仓库
  - docx - Word 文档处理
  - pdf - PDF 提取
  - pptx - PPT 生成
  - xlsx - Excel 操作
  - web-artifacts-builder - Web 组件构建

### 社区 Skills
- [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) - 140+ 科研技能
- [obra/superpowers](https://github.com/obra/superpowers) - TDD+YAGNI+DRY 方法论
- [SkillsMP](https://skillsmp.com/) - Skills 市场

### 推荐 Skills（按用途）

| 用途 | Skill | 热度 |
|------|-------|------|
| 自动创建 PR | create-pr | 169.7k ⭐ |
| 查找和安装 Skills | skill-lookup | 142.6k ⭐ |
| 前端代码审查 | frontend-code-review | 126.3k ⭐ |
| 优化 LLM 缓存 | cache-components-expert | 137.2k ⭐ |
| TDD 方法论 | obra/superpowers | 29.1k ⭐ |
| 处理文档 | anthropics/skills | 45.1k ⭐ |
| 创建 Skill | skill-writer | 96k ⭐ |

---

## 性能优化

### Token 使用优化
- **渐进式披露**：仅加载相关 Skills
- **精简 description**：保持在 50 字以内
- **分层文档**：核心内容在 SKILL.md，详细内容在 REFERENCE.md

### 加载速度优化
- **限制 Skills 数量**：建议 ≤50 个
- **分类管理**：使用子目录组织（如 `ai/`, `research/`, `tools/`）
- **定期清理**：移除未使用的 Skills

---

## 故障排查

### Skill 未被激活
1. 检查 `description` 是否准确描述 Skill 功能
2. 确认 SKILL.md 格式正确（YAML frontmatter）
3. 尝试显式提及 Skill 名称

### Token 消耗过高
1. 检查是否加载了过多 Skills
2. 精简 SKILL.md 内容，将详细文档移到 REFERENCE.md
3. 使用 `agents/INDEX.md` 的渐进式披露机制

### Skill 冲突
1. 检查是否有多个 Skills 的 `description` 相似
2. 使用更精确的 `description` 和 `tags`
3. 手动指定使用哪个 Skill

---

## 更新日志

### 2026-03-08
- **新增 question-refiner Skill** - 研究查询精炼器
  - 7 项验证清单（意图/范围/信息类型/可操作性/无歧义/粒度/前提）
  - 快速通过机制（≥5/7 通过则零追问直接精炼）
  - 引导式澄清（最多 3 个问题）
  - 标准化 Structured Research Prompt 输出
  - 与 deep-research / exa-research / brightdata-research / social-media-research 集成
- **deep-research 升级至 v1.2.0**
  - Question Refiner 可选前置集成
  - 综合增强：交叉引用验证 + 矛盾解决矩阵 + 发现置信度评分
  - 可选阶段 2.5 引用验证（来源 5 级可信度评分）
  - 领域扩展协议（基座 + 叠加式领域增强）

### 2026-03-01
- **新增 collaborating-with-codex Skill** - 多模型协作（Codex）
  - 后台 Bash 子进程调用 OpenAI Codex CLI（非阻塞）
  - Claude 并行分析，完成后读取结果文件融合
  - 适合代码实现、样板生成、API 示例、测试用例
  - 与 Orchestrator COLLABORATIVE 策略集成
  - 与 Ralph Loop 和 Autopilot Development 阶段集成
- **新增 collaborating-with-gemini Skill** - 多模型协作（Gemini）
  - 后台 Bash 子进程调用 Google Gemini CLI（非阻塞）
  - 利用 Gemini 超长上下文窗口（100万+ tokens）
  - 适合整个代码库扫描、大型文档处理、跨文件 bug 追踪
  - 明确与 Codex Skill 的任务分工

### 2026-02-20
- **新增 seedance-prompt Skill** - Seedance 2.0 分镜提示词生成专家
  - 结构化提示词模板（风格+时间轴+声音+参考素材）
  - 镜头语言库（景别、运动、角度完整覆盖）
  - 10+ 风格声明（电影写实、水墨、赛博朋克、动漫等）
  - 16+ 模板分类（人物特写、场景转换、动作追踪等）
  - 支持看图说故事和多轮优化
- **新增 seedance-storyboard Skill** - Seedance 2.0 剧本分镜生成器
  - 四幕结构剧本创作（起承转合）
  - 编号素材清单系统（角色C/场景S/道具P + 英文提示词）
  - Seedance 2.0 时间轴格式分镜脚本
  - 视频延长链式方案（集间无缝衔接）
  - 三件套工具链：Claude Code + 生图AI + Seedance 2.0
- **新增 frontend-design Skill** - 前端设计与 UI/UX 指导
  - 基于 Anthropic 官方 frontend-design skill
  - 视觉层次、间距系统、配色策略、字体规范
  - 交互规范（动画、表单、响应式）
  - 可访问性检查（WCAG 2.1 AA）
  - 设计审查能力
- **新增 ui-ux-pro-max Skill** - 最强前端设计知识库
  - 基于 nextlevelbuilder/ui-ux-pro-max-skill
  - 57+ UI 风格、97 配色方案、57 字体搭配
  - 25+ 图表类型、98 UX 规范
  - 11 技术栈支持（React/Vue/Svelte/SwiftUI/Flutter 等）
  - BM25 智能推荐引擎
  - 2025/2026 UI 新趋势
- **新增 react-best-practices Skill** - React 性能优化宝典
  - 基于 Vercel 官方 vercel-labs/agent-skills
  - 45+ 条规则按影响力排序
  - 8 大规则类别（Waterfalls/Bundle Size/Data Fetching 等）
  - 代码审查和新功能开发两种模式
- **新增 web-artifacts-builder Skill** - Web Artifacts 构建器
  - 基于 Anthropic 官方 anthropics/skills
  - React 18 + TypeScript + Vite + Tailwind + shadcn/ui
  - 40+ 预装 shadcn/ui 组件
  - 打包为单文件 bundle.html

### 2026-02-04
- **新增 vision-builder Skill** - 愿景构建器（Aha-Loop 方法论）
  - 5W1H 分析框架 + SMART 目标设定
  - 4 阶段工作流：收集 → 分析 → 构建 → 验证
  - 标准化 VISION.md 模板
  - 与 Autopilot Planning 阶段、architect、spec-writer 深度集成
- **新增 plan-review Skill** - 计划审查器（Aha-Loop 方法论）
  - 10 维度多维度评估框架（完整性、可行性、清晰度、依赖性、风险性、测试性、可维护性、扩展性、安全性、文档性）
  - 3 阶段审查流程：结构检查 → 深度评估 → 综合建议
  - PLAN-REVIEW.md 标准化报告模板
  - 与 Autopilot Planning 阶段、spec-writer、qa-reviewer、God Committee 深度集成
- **新增 parallel-explore Skill** - Git Worktree 并行探索（Aha-Loop 方法论）
  - 多方案决策的独立工作树创建
  - 标准化 EXPLORATION_RESULT.md 评估报告（10 分制多维度）
  - 与 Orchestrator COMPETITIVE 策略、Autopilot 深度集成
  - 配套 scripts/parallel-explorer.sh 命令行工具
- **新增 observability Skill** - AI 思维日志可观测性系统（Aha-Loop 灵感）
  - 实时记录推理过程、决策点、执行状态
  - 与 Context Archival、Ralph Loop、Autopilot 深度集成
  - 支持日志轮转和归档管理
- 新增 social-media-research Skill（跨平台社媒数据研究，TikHub MCP 集成）
- 新增 exa-research Skill（企业与市场研究，Exa MCP 集成）
- 新增 brightdata-research Skill（电商平台深度调研，Bright Data MCP 集成）
- 新增 deep-research Skill（深度研究，Lead Agent + Subagent 架构）
- 新增 market-insight Skill（市场洞察分析）

### 2026-01-23
- 创建 Skills 集成指南
- 集成 claude-scientific-skills (140+ 科研技能)
- 实施渐进式披露机制
- 定义 Skill 标准格式

---

## 相关文档

- **Agent 索引**: `agents/INDEX.md`
- **编排模式**: `workflows/orchestration/orchestration-patterns.md`
- **上下文工程**: `workflows/context-engineering.md`
- **最佳实践**: `memory/best-practices.md`

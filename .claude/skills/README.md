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

## Skill 列表

> Skill 完整索引见 `.claude/skills/INDEX.md`，详细文档见 `docs/SKILLS-CATALOG.md`。
> 本文件不重复列出所有 Skill，仅保留设计规范和集成原则。

### 外部 Skill 集合

#### 1. claude-scientific-skills (140+ 科研技能)

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

## Skill 成熟度生命周期

每个 Skill 有明确的成熟度阶段，影响使用策略和维护优先级：

| 阶段 | 标记 | 含义 | 使用策略 |
|------|------|------|---------|
| **stable** | `maturity: stable` | 经过 3+ 次实战验证，行为可预测 | 默认激活，无需额外确认 |
| **beta** | `maturity: beta` | 已完成设计，1-2 次实战，可能有边界情况 | 激活时提示用户"此 Skill 为 beta" |
| **draft** | `maturity: draft` | 初始版本，未经实战验证 | 仅在用户显式请求时激活 |
| **deprecated** | `maturity: deprecated` | 已被更优方案替代 | 不再激活，提示替代方案 |

**晋升条件**：
- draft → beta：完成首次实战 + 用户确认输出质量可接受
- beta → stable：累计 3+ 次实战无重大问题 + Gotchas 已补全
- stable → deprecated：出现更优替代方案 + 迁移路径已文档化

**在 frontmatter 中声明**：
```yaml
metadata:
  maturity: stable  # stable | beta | draft | deprecated
  replaced_by: new-skill-name  # 仅 deprecated 时填写
```

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
  maturity: stable
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

## Anthropic 官方 Skills 设计指南

> 来源: Anthropic Thariq (Claude Code 团队) 2026-03 分享，内部数百个 Skill 实践总结

### 官方九大分类体系

| # | 分类 | 说明 | 当前覆盖 |
|---|------|------|---------|
| 1 | **Library & API Reference** | 教模型正确使用库/CLI/SDK | ✅ pytorch, pandas |
| 2 | **Product Verification** | 测试/验证代码是否正常工作 | ❌ 缺失 |
| 3 | **Data Fetching & Analysis** | 连接数据和监控系统 | ✅ data-analysis, amazon-analyse |
| 4 | **Business Process & Team Automation** | 重复性工作流自动化 | ⚠️ 部分 |
| 5 | **Code Scaffolding & Templates** | 生成框架模板代码 | ⚠️ 部分 |
| 6 | **Code Quality & Review** | 推行代码质量标准 | ✅ QA 系统 |
| 7 | **CI/CD & Deployment** | 代码推送和部署 | ❌ 缺失 |
| 8 | **Runbooks** | 多工具排查流程 | ❌ 缺失 |
| 9 | **Infrastructure Operations** | 日常运维 | ❌ 缺失 |

**设计原则**: 最好的 Skill 只属于其中一类；跨多类的往往让人摸不着头脑。

### 写好 Skill 的 10 条原则

1. **只写 Claude 不知道的** — 聚焦于让 Claude 跳出常规思维的信息
2. **认真写 Gotchas** — 信噪比最高的部分，从 Claude 反复踩的坑中积累
3. **文件系统 = 渐进式上下文** — 用 `references/`、`assets/`、`scripts/` 实现按需加载
4. **给信息但留灵活度** — Skill 高度可复用，别把指令写得太死
5. **用 config.json 做初始化** — 需要用户上下文时存配置，未配置时主动问
6. **Description 是触发器** — 不是摘要，要像触发条件一样写
7. **让 Skill 有记忆** — 用日志/JSON 存执行历史，`${CLAUDE_PLUGIN_DATA}` 是稳定目录
8. **给可直接用的代码** — 提供脚本和函数库，Claude 花精力在组合和决策上
9. **善用 Skill 级 Hooks** — 只在 Skill 调用时激活的强约束（如拦截危险命令）
10. **控制 Skill 数量** — 过多 Skills 增加上下文负担，规模扩大用 plugin 市场分发

> 详细实践案例: `memory/best-practices.md` → BP-012

---

## 相关文档

- **Agent 索引**: `agents/INDEX.md`
- **编排模式**: `workflows/orchestration/orchestration-patterns.md`
- **上下文工程**: `workflows/context-engineering.md`
- **策展型最佳实践条目库**: `memory/best-practices.md`

---

## 闭环 Skill 提取协议

> 来源: Hermes Agent "用着用着越来越懂你"理念 — 完成任务后自动评估是否产生了可复用模式

### 提取条件

任务完成后，如果满足以下任一条件，触发 Skill 提取评估:

| 条件 | 说明 |
|------|------|
| **重复模式** | 相同类型的任务已完成 3+ 次，每次都执行相似步骤 |
| **复杂流程** | 任务涉及 5+ 个步骤的固定序列（可编码为流程） |
| **领域知识** | 任务依赖特定领域知识（非通用编程知识） |
| **用户请求** | 用户明确要求将某个工作流沉淀为 Skill |

### 提取流程

```
Step 1: 识别 — 任务完成后，检查是否满足提取条件
Step 2: 提炼 — 提取输入/输出/步骤/边界条件/Gotchas
Step 3: 验证 — 用户确认提取的模式是否准确
Step 4: 编写 — 创建 SKILL.md（遵循标准格式）
Step 5: 注册 — 更新 INDEX.md，添加新 Skill 条目
```

### 提取质量标准

新提取的 Skill 必须满足:
1. **契约化**: 输入/输出显式声明
2. **Gotchas**: 至少 1 条从实践中发现的陷阱
3. **验收标准**: 如何判断 Skill 执行成功
4. **触发条件**: Description 写成触发器而非摘要（参见 BP-012 原则 6）

### 先写规则，再装 Skill

**原则**：在安装或创建新 Skill 之前，先确认 CLAUDE.md 和 memory/ 中的规则体系已覆盖该 Skill 的使用场景。

**理由**：Skill 是能力放大器，但如果底层规则（何时用、怎么判断成功、边界在哪）不清晰，Skill 只会放大混乱。

**检查清单**（安装新 Skill 前）：
1. CLAUDE.md 中是否有该 Skill 的路由规则（何时激活）？
2. memory/best-practices.md 中是否有相关场景的最佳实践？
3. 该 Skill 的输出如何与现有工作流衔接（谁消费它的结果）？
4. 是否与已有 Skill 功能重叠？如重叠，路由优先级如何？

**反模式**：装了 10 个 Skill 但 CLAUDE.md 没有对应路由 → 激活混乱，多个 Skill 抢同一任务。

---

## 知识域 Skill 增强规范

> 来源: Anthropic 数据分析系统设计（2026-06-05），适用于任何需要将用户问题映射到特定知识源的 Skill（数据查询/API 文档/产品知识库/代码库导航）

**知识域 Skill 的特殊性**：代码执行 Skill 允许试错，但知识域 Skill 往往只有一个正确答案，错了就是错了——这要求更严格的设计。

### 知识域 Skill 必须包含的 5 个设计要素

**1. 语义层优先路径（强制声明）**

在 SKILL.md 中明确写出信息源的优先级，并封堵常见绕路借口：

```markdown
## 信息源优先级（强制）
1. [治理过的语义层/API 文档] — 必须首先查这里
2. [历史查询模式/参考文档] — 语义层无法覆盖时
3. [原始表/原始文档] — 仅在上述均无法覆盖时

**不构成跳过第一层的理由**：
- "需要自定义过滤" → [语义层已支持，用 X 方法]
- "需要 join" → [已封装，用 Y 接口]
```

**2. 实体歧义消解表**

把高频歧义词全部列出，要求查询前先确认：

```markdown
## 歧义词确认表（查询前必须确认）
| 术语 | 候选实体 | 如何区分 |
|------|---------|---------|
| "用户" | 注册用户/活跃用户/付费用户 | 需问清楚统计口径 |
| "[业务术语]" | [定义A] / [定义B] | [区分方法] |
```

**3. 日期/时区/新鲜度规范**

明确回答三个问题：

```markdown
## 时间规范
- **"上周/上月"** = 最近一个完整自然周/月（非滚动 7/30 天）
- **默认时区**: [时区]
- **数据延迟**: [哪些数据会延迟，以 MAX(date) 为锚点]
```

**4. 来源标注格式（每个回答必须附带）**

```markdown
## 来源标注（每次回答结尾）
> **来源**: [语义层 | 参考文档 | 原始数据探索]
> **新鲜度**: [数据中的最大日期]
> **置信度**: [高/中/低 + 原因]
```

**5. 踩坑记录（血泪教训区）**

这是整个 Skill 里信噪比最高的部分，从实际错误中积累，持续更新：

```markdown
## 已知陷阱
- 用 `[field_v2]`，不要用 `[field]`（旧字段已废弃，但仍存在不报错）
- `[表A]` 和 `[表B]` 名字相似但粒度不同，[核心指标]用[表A]
- [术语X] 在[系统A]里叫[名称P]，在[系统B]里叫[名称Q]，是同一个东西
```

### 知识域 Skill 维护要求

与普通 Skill 不同，知识域 Skill 需要纳入持续维护流程：

- **Skill 文件随数据模型同步更新**：数据 schema 变更时，对应的 Skill 必须同步修改
- **CI 检查**：添加检查规则，"改了模型/文档但未改 Skill"的 PR 自动标记需要 review
- **离线评估集**：见 `memory/best-practices.md` BP-043，评估 Skill 修改是否引入回退
- **主动自修复**：见 `memory/best-practices.md` BP-044，定时扫描用户纠错信号

> 完整 Pairwise Skills 设计模式详见: `memory/best-practices.md` BP-042

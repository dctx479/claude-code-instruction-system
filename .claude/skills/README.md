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
| **literature-mentor** | 文献深度解读助手，像导师一样交互式解读论文 | research |
| **paper-revision** | 论文/技术文档修改助手，风格转换 | research |
| **pytorch** | PyTorch 深度学习框架 | ai-ml |
| **pandas** | pandas 数据分析库 | ai-ml |
| **data-analysis** | 通用数据分析技能 | ai-ml |

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

### 2026-01-23
- 创建 Skills 集成指南
- 集成 claude-scientific-skills (140+ 科研技能)
- 实施渐进式披露机制
- 定义 Skill 标准格式

---

## 相关文档

- **Agent 索引**: `agents/INDEX.md`
- **编排模式**: `workflows/orchestration-patterns.md`
- **上下文工程**: `workflows/context-engineering.md`
- **最佳实践**: `memory/best-practices.md`

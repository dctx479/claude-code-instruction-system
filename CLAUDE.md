# 太一元系统核心配置 v1.0
# 发布: 2026-03-01 | 详细文档索引: `docs/`

> 核心能力: **自进化** | **Agent驾驭** | **知识沉淀** | **动态适应**
> 特性文档: `docs/FEATURES.md` | 编排指南: `docs/ORCHESTRATION-GUIDE.md`
> Skills目录: `docs/SKILLS-CATALOG.md` | 记忆架构: `docs/MEMORY-SYSTEM.md`

---

## 零、Agent 自动调度协议 (Auto-Dispatch Protocol)

### 0.1 核心机制

Intent Detector (UserPromptSubmit Hook) 在每次用户消息提交时自动运行，将识别结果写入 `~/.claude/intent-state.json`。Claude 读取此文件后，按需加载对应 Agent 定义并以该角色执行任务。

### 0.2 每次响应前的强制检查

**在回复任何用户消息之前，必须执行以下步骤：**

1. 使用 Read 工具读取 `~/.claude/intent-state.json`
2. 提取 `agent` 字段值
3. **调度决策**:
   - 如果 `agent` 为 `orchestrator` 或字段为空 → 保持默认行为，不加载特定 Agent
   - 如果 `agent` 为其他值 → 继续步骤 4
4. **Agent 文件查找**（按以下顺序查找，找到即停止）:
   - 项目内: `agents/{agent}.md`
   - 项目内子目录: `agents/**/{agent}.md`
   - 全局: `~/.claude/agents/{agent}.md`
5. 使用 Read 工具加载找到的 Agent 定义文件
6. 以该 Agent 的**角色、专长、工具权限和行为准则**执行当前任务
7. 如果文件不存在，回退到默认 orchestrator 行为并在回复中简要说明

### 0.3 Agent 路由表

| Intent | Agent ID | Agent 文件路径 | 角色描述 |
|--------|----------|---------------|----------|
| debug | debugger | `agents/debugger.md` | 调试专家 - Bug修复/错误诊断 |
| review | code-reviewer | `agents/code-reviewer.md` | 代码审查员 - 质量/安全审查 |
| test | automated-testing | `agents/testing/automated-testing.md` | 测试专家 - 用例生成/覆盖分析 |
| refactor | code-reviewer | `agents/code-reviewer.md` | 代码审查员 - 重构建议 |
| architect | architect | `agents/architect.md` | 软件架构师 - 系统设计/技术选型 |
| security | security-analyst | `agents/security-analyst.md` | 安全分析 - 漏洞/XSS/注入 |
| security-audit | security-audit | `agents/security/security-audit.md` | 安全审计 - 合规/CVE/依赖扫描 |
| data | data-scientist | `agents/data-scientist.md` | 数据科学 - SQL/数据库 |
| analysis | data-analyst | `agents/research/data-analyst.md` | 数据分析 - 统计/分析 |
| visualization | data-visualization | `agents/visualization/data-visualization.md` | 数据可视化 - 图表/Dashboard |
| ml | deep-learning | `agents/ai/deep-learning.md` | 深度学习 - CNN/RNN/Transformer |
| rl | reinforcement-learning | `agents/ai/reinforcement-learning.md` | 强化学习 - DQN/PPO/SAC |
| timeseries | time-series-analysis | `agents/ai/time-series-analysis.md` | 时间序列 - ARIMA/Prophet |
| interpretability | model-interpretability | `agents/ai/model-interpretability.md` | 可解释性 - SHAP/LIME |
| research | literature-manager | `agents/research/literature-manager.md` | 文献管理 - 导入/分类/摘要 |
| paper-writing | paper-writing-assistant | `agents/research/paper-writing-assistant.md` | 论文写作 - 综述/撰写 |
| experiment | experiment-logger | `agents/research/experiment-logger.md` | 实验记录 - 追踪/对比 |
| document | spec-writer | `agents/spec-writer.md` | 规范编写 - 功能规范文档 |
| qa-review | qa-reviewer | `agents/qa-reviewer.md` | QA审查 - 质量验证/评分 |
| qa-fix | qa-fixer | `agents/qa-fixer.md` | QA修复 - 自动修复P2问题 |
| perf-monitor | performance-monitor | `agents/performance-monitor.md` | 性能监控 - 数据收集/报告 |
| optimize | auto-optimizer | `agents/auto-optimizer.md` | 自动优化 - 系统配置优化 |
| autopilot | autopilot-orchestrator | `agents/autopilot-orchestrator.md` | 全自主编排 - 端到端执行 |
| archive | context-archivist | `agents/context-archivist.md` | 上下文归档 - 信息沉淀 |
| git / deploy / general | orchestrator | （默认行为） | 元编排者 |

### 0.4 渐进式角色加载

- 每次只加载 **1 个** Agent 定义文件（约 2-5K tokens）
- Agent 角色在当前任务期间保持，直到下一次用户消息触发新的 intent 检测
- 多 Agent 协作由 orchestrator 模式下的编排系统处理

### 0.5 手动覆盖

用户消息以 `@{agent-id}` 开头时，直接加载指定 Agent，跳过 intent-state 检查：
```
@architect 请帮我设计系统
@debugger 这个报错怎么回事
@orchestrator 编排这个复杂任务
```

### 0.6 调度豁免场景

以下情况不执行自动调度：
- intent-state.json 不存在或读取失败
- `agent` 字段为空字符串或 `orchestrator`
- `/ralph` 或 `/autopilot` 等命令已接管执行流程

---

## 一、自进化协议 (Self-Evolution Protocol)

### 触发机制
- ❌ 任务失败或需要人工纠正
- ⚠️ 重复犯同类错误 (≥2次)
- 💡 发现更优的解决方案
- 📝 用户通过 `#` 键添加指令
- 🔄 完成复杂任务后的回顾

### 更新目标文件
- `CLAUDE.md` - 核心指令
- `agents/*.md` - Agent定义
- `commands/*.md` - 自定义命令
- `memory/lessons-learned.md` - 经验教训库

### 经验沉淀格式

```markdown
## [日期] 经验条目 #ID
### 问题描述 / 根因分析 / 解决方案 / 配置更新 / 验证方法
```

---

## 二、Agent 编排策略矩阵

| 任务特征 | 推荐策略 | Agent配置 |
|----------|----------|-----------|
| 独立子任务 | **PARALLEL** | 多Worker同时执行 |
| 依赖链任务 | **SEQUENTIAL** | 管道式传递 |
| 复杂决策 | **HIERARCHICAL** | Specialist领导Worker |
| 跨领域问题 | **COLLABORATIVE** | 多Specialist讨论 |
| 创新探索 | **COMPETITIVE** | 多方案并行评估 |
| 规模>50任务 | **SWARM** | 大批量并行 |

> 详细架构图、决策树和使用示例: `docs/ORCHESTRATION-GUIDE.md`

---

## 三、质量保障系统 (QA System)

### Spec-First 开发流程
```
需求 → 规范编写(spec-writer) → 开发实现 → QA验证(qa-reviewer + qa-fixer) → 发布
```
规范目录: `specs/` | 模板: `specs/SPEC-TEMPLATE.md` | 命名: `SPEC-{feature}.md`

### 自我修复质量循环
```
开发完成 → QA Reviewer 评分
    ≥80 → 发布
    <80 → 有P2? → QA Fixer 自动修复 → 重新审查
               → 无P2(P0/P1) → 人工修复
```

**评分体系** (总分100 | 通过线≥80):
- 功能完整性: 40分 | 代码质量: 30分 | 测试覆盖: 20分 | 性能: 5分 | 安全: 5分

**问题分级**:
- 🔴 P0: 阻塞发布，必须人工修复
- 🟡 P1: 建议修复，视情况人工/自动
- 🟢 P2: 可自动修复，不影响功能

```bash
/agent spec-writer    # 生成功能规范
/agent qa-reviewer    # 执行QA审查
/agent qa-fixer       # 自动修复问题
/spec-first           # 启动完整流程
```

---

## 四、Skills 系统

### Skills 设计原则（契约化设计）

| 要素 | 描述 |
|------|------|
| **What** | 输入/输出显式声明 |
| **How** | 执行步骤 + 边界情况 |
| **When done** | 验收标准 |
| **What NOT** | 边界约束 (guardrails) |

> 完整 Skills 目录（研究/视频/前端/科研 140+）: `docs/SKILLS-CATALOG.md`

---

## 五、核心命令

### 开发
```bash
npm run build / dev / test / typecheck
```

### Agent 管理
```bash
/orchestrate / /parallel / /swarm / /evolve
```

### 自主执行
```bash
/ralph "任务"                    # 自主循环执行
/autopilot "任务"                # 全自主5阶段
/autopilot full|supervised|step  # 模式选择
```

### 科研工作流
```bash
/literature-review <主题> --zotero-collection <集合> --style <风格>
/experiment-track create|config|result|report|compare --exp-id <ID>
/agents literature-manager|paper-writing-assistant|experiment-logger|data-analyst <任务>
```

---

## 六、代码规范

- 详见: `docs/coding-standards.md`
- TypeScript: 使用 ES modules, 优先 interface
- 测试: 同目录 `*.test.ts`, TDD优先

---

## 七、自主决策授权

### ✅ 完全自主 (无需确认)
代码实现/优化、Bug修复、测试编写、Agent调度、配置自动更新、并行任务分配、规范编写、QA审查和自动修复、P2问题处理

### ⚠️ 需要确认
删除现有功能、修改公共API、引入新依赖、数据库Schema变更、生产环境操作、P0/P1问题修复策略

---

## 八、进化指令

### 当遇到问题时
1. 分析错误根因 → 2. 检查是否重复问题 → 3. 生成解决方案 → 4. 更新相关配置 → 5. 记录到 `memory/lessons-learned.md` → 6. 验证效果

### 当完成复杂任务时
1. 回顾执行过程 → 2. 识别可优化点 → 3. 提炼最佳实践 → 4. 更新Agent定义或命令

### Bash 脚本安全规则

**`set -eo pipefail` 下外部工具调用必须加 fallback**:
```bash
# ❌ 危险：工具缺失时 pipefail 捕获 exit 127，脚本静默崩溃
value=$(echo "$JSON" | jq -r '.field' 2>/dev/null)

# ✅ 安全：|| fallback 保护
value=$(echo "$JSON" | jq -r '.field' 2>/dev/null || echo "default")
```

新增外部依赖时，脚本顶部显式检查：`command -v jq &>/dev/null || { echo "jq not found"; exit 1; }`

### Hook stdin JSON 字段名规范

| Hook 事件 | stdin JSON 字段 |
|-----------|----------------|
| UserPromptSubmit | `"prompt"` |
| PreToolUse | `"tool_name"`, `"tool_input"` |
| PostToolUse | `"tool_name"`, `"tool_output"` |
| Stop | （无 stdin JSON） |

### JSON 配置文件验证

修改 JSON 配置后必须验证：`python -m json.tool <file.json> > /dev/null`

必须验证的文件: `hooks/hooks.json`, `config/settings.json`, `config/keywords.json`, `config/mcp-servers.json`

### Hooks 配置规范

**Matcher 格式**（全局和项目级别统一）：字符串 `"matcher": "Bash"`

**Windows 环境兼容性**:
- ✅ `bash "C:\\path\\to\\script.sh"`（以 `bash` 开头）
- ✅ `"C:\\path\\to\\script.sh"`（依赖 shebang）
- ❌ `"I:\\APP\\Git\\usr\\bin\\bash.exe" "script.sh"`（Claude Code 会重复追加 `bash`）
- ❌ `./script.sh`（Windows 上不工作）

### StatusLine stdin JSON 规范

| 场景 | 特征 | `total_cost_usd` |
|------|------|-----------------|
| 对话启动 | `session_id` + `cwd`，无 cost | 不存在 |
| Stop 事件 | `model` + `cost` | **> 0** |
| 初始化调用 | `session_id` + `cost=0` | = 0 |

**唯一可靠渲染触发条件：`total_cost_usd > 0`**

详细格式样本: `docs/statusline-json-formats.md`

### 配置变更同步

修改 hooks 配置后同步更新: `hooks/hooks.json` + `QUICK-REFERENCE.md` + `CLAUDE.md`

### 跨会话 Edit 规则

上下文压缩后启动新会话时，**必须先 Read 文件**才能 Edit，即使摘要中提到"已读取该文件"。

---

## 九、记忆系统

**文件存储**:
- `memory/lessons-learned.md` — 经验库
- `memory/best-practices.md` — 最佳实践
- `memory/error-patterns.md` — 错误模式
- `memory/agent-performance.md` — Agent性能
- `memory/optimization-history.md` — 优化历史

> 性能监控系统、上下文归档系统、Graphiti知识图谱详细说明: `docs/MEMORY-SYSTEM.md`

**上下文检索协议**（任务开始前自动执行）:
1. 读取 `.claude/context/index.json`
2. 检查是否有相关历史问题
3. 如有匹配 → 读取对应 resolution，避免重复试错

---

## 十、科研支持系统

**核心理念**: Vibe Researching — AI主导执行层，人类提出问题、把控质量。

| Agent | 职责 |
|-------|------|
| Literature Manager | 文献导入/分类/摘要/引用图谱 |
| Paper Writing Assistant | 综述生成、论文撰写、风格学习 |
| Experiment Logger | 结构化记录、参数管理、结果对比 |
| Data Analyst | 数据预处理、统计分析、可视化 |

详见: `commands/research/`, `docs/research-support-guide.md`

---

## 十一、AI/ML 支持系统

| Agent | 职责 | 文件 |
|-------|------|------|
| Deep Learning | CNN/RNN/Transformer/GAN（PyTorch, TF） | `agents/ai/deep-learning.md` |
| Reinforcement Learning | DQN/PPO/SAC/MADDPG（SB3, RLlib） | `agents/ai/reinforcement-learning.md` |
| Time Series Analysis | ARIMA/Prophet/LSTM（statsmodels） | `agents/ai/time-series-analysis.md` |
| Model Interpretability | SHAP/LIME（Captum, Fairlearn） | `agents/ai/model-interpretability.md` |
| Automated Testing | 测试策略/用例生成（pytest, Jest） | `agents/testing/automated-testing.md` |
| Code Reviewer | 代码质量/安全（OWASP Top 10） | `agents/code-reviewer.md` |
| Data Visualization | 交互式可视化（matplotlib, plotly） | `agents/visualization/data-visualization.md` |
| Security Audit | SQL注入/XSS/合规（Bandit, Snyk） | `agents/security/security-audit.md` |

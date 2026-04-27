# 太一元系统核心配置 v1.0
# 发布: 2026-03-01 | 详细文档索引: `docs/`

> 核心能力: **自进化** | **Agent驾驭** | **知识沉淀** | **动态适应**
> 特性文档: `docs/FEATURES.md` | 编排指南: `docs/ORCHESTRATION-GUIDE.md`
> Skills目录: `docs/SKILLS-CATALOG.md` | 记忆架构: `docs/MEMORY-SYSTEM.md`
> 配置指南: `docs/CONFIG-FILES-GUIDE.md` | 上下文工程: `docs/CONTEXT-ENGINEERING-GUIDE.md`
> 知识复利: `docs/KNOWLEDGE-COMPOUNDING-GUIDE.md` | 端口管理: `docs/port-management/PORT-MANAGEMENT-GUIDE.md`

---

## 全局配置文件说明

| 文件 | 路径 | 用途 | 手动编辑 |
|------|------|------|---------|
| **settings.json** | `~/.claude/settings.json` | hooks、statusLine、env、permissions | ✅ |
| **.claude.json** | `~/.claude.json` | 启动次数、项目历史（自动管理） | ❌ |

配置优先级: 项目 `.claude/settings.json` → 全局 `~/.claude/settings.json` → 默认

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
   - 项目内子目录: `agents/**/{agent}.md`（如 `agents/ai/deep-learning.md`）
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
| security | security-analyst | `agents/security/security-analyst.md` | 安全分析 - 漏洞/XSS/注入 |
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
| perf-monitor | performance-monitor | `agents/ops/performance-monitor.md` | 性能监控 - 数据收集/报告 |
| optimize | auto-optimizer | `agents/ops/auto-optimizer.md` | 自动优化 - 系统配置优化 |
| autopilot | autopilot-orchestrator | `agents/ops/autopilot-orchestrator.md` | 全自主编排 - 端到端执行 |
| archive | context-archivist | `agents/ops/context-archivist.md` | 上下文归档 - 信息沉淀 |
| requirements | requirements-analyst | `agents/requirements-analyst.md` | 需求分析 - 用户故事/功能拆解 |
| mentor | tech-mentor | `agents/tech-mentor.md` | 技术导师 - 架构设计/文档查询 |
| architect-senior | senior-code-architect | `agents/senior-code-architect.md` | 高级架构师 - 代码审查/框架指导 |
| vitest | vitest-tester | `agents/vitest-tester.md` | Vitest测试 - 用例/mock策略 |
| sdd-riper | sdd-riper-orchestrator | `agents/sdd-riper-orchestrator.md` | SDD-RIPER编排 - 规范驱动开发 |
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
- 用户正在进行多轮对话的中间步骤（上下文已有明确 Agent 角色）
- `/ralph` 或 `/autopilot` 等命令已接管执行流程

---

## 一、自进化协议 (Self-Evolution Protocol)

### 触发机制
- ❌ 任务失败或需要人工纠正
- ⚠️ 重复犯同类错误 (≥2次)
- 💡 发现更优的解决方案
- 📝 用户通过 `#` 键添加指令
- 🔄 完成复杂任务后的回顾

### 半自动复盘流程（推荐）

**复杂任务完成后**：
1. AI 主动询问："是否需要复盘本次任务？"
2. 如用户同意，提炼 3-5 条候选知识条目
3. **去重检查**：搜索 lessons-learned.md 确认无重复（见知识复利指南的 Ingest 去重协议）
4. **Skill 提取评估**：检查是否满足闭环 Skill 提取条件（重复模式 3+次/复杂流程 5+步/领域知识）
5. 展示给用户确认（避免记录错误或噪声）
6. 用户确认后写入 `memory/lessons-learned.md`，并标注置信度 `[UNVERIFIED]`
7. 如触发 Skill 提取 → 按 `.claude/skills/README.md` 闭环提取协议执行

**何时触发**：autopilot/ralph 结束、解决重大 bug、完成新功能开发、批量任务完成后

### 更新目标文件
- `CLAUDE.md` - 核心指令
- `agents/*.md` - Agent定义
- `commands/*.md` - 自定义命令
- `memory/lessons-learned.md` - 经验教训库

### 知识质量控制

**每条经验必须满足**：
1. **案例引用**：关联具体的 commit hash、文件路径、错误日志或对话场景
2. **避免泛化**：用 before/after 示例，禁止"应该注意"等模糊表述
3. **可验证性**：包含明确的验证方法或复现步骤
4. **可复用性**：只记录可复用的模式，不记录一次性特殊情况

**反模式（禁止）**：
- ❌ 无案例引用的经验
- ❌ "要注意配置文件格式"（太泛化）
- ❌ "可能会遇到路径问题"（无具体场景）

### 经验沉淀格式

```markdown
## [日期] 经验条目 #ID
### 问题描述 / 根因分析 / 解决方案 / 配置更新 / 验证方法 / 案例引用（必填）
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
| **中大型需求开发** | **SDD-RIPER** | **五阶段状态机** |

> 详细架构图、决策树、编排示例和模式性能数据: `docs/ORCHESTRATION-GUIDE.md`
> SDD-RIPER 方法论详解: `docs/SDD-RIPER-GUIDE.md`

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

> 详见: `docs/QA-SYSTEM.md`

---

## 四、Skills 系统

### Skills 渐进式披露加载协议

**遇到需要 Skill 的任务时，按以下顺序操作：**

1. 读取 `.claude/skills/INDEX.md` 了解所有可用 Skill 概览（~600 tokens）
2. 根据场景速查表确定需要激活的 Skill
3. 仅读取对应 Skill 的完整 `SKILL.md`（~2K tokens/个）

> **Token 节省**: INDEX 文件 ~600 tokens vs 所有 Skill ~46K tokens，节省 **98%**
> Skills 索引: `.claude/skills/INDEX.md` | 集成指南: `.claude/skills/README.md`

### Skills 设计原则（契约化设计）

| 要素 | 描述 |
|------|------|
| **What** | 输入/输出显式声明 |
| **How** | 执行步骤 + 边界情况 |
| **When done** | 验收标准 |
| **What NOT** | 边界约束 (guardrails) |

**规则放置优先级**：新增规则优先挂靠现有模块（`CLAUDE.md` / `.claude/reference/` / `.claude/prompts/` / 对应 `SKILL.md`），避免跨层重复定义同一规则。

> 完整 Skills 目录（研究/视频/前端/科研 140+）及触发词、组合模式: `docs/SKILLS-CATALOG.md`

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

#### Ralph 循环规则

**一轮 (Iteration) = 一个完整工作周期**，不是单次操作：

```
评估当前进展 → 规划本轮工作 → 执行多个操作步骤 → 验证成果 → 标记完成
```

**Claude 的职责 — 启动时**：执行 `/ralph` 后立即初始化状态文件：

```json
// memory/ralph-state.json (项目内) 或 ~/.claude/ralph-state.json (全局)
{
  "active": true, "status": "RUNNING",
  "iteration": 0, "max_iterations": 10,
  "round_complete": false, "completed": false,
  "fatal_error": false, "needs_confirmation": false,
  "current_task": "task-id", "task_description": "用户任务描述",
  "started_at": "<ISO8601>", "last_updated": "<ISO8601>",
  "metrics": { "total_runs": 1, "successful_runs": 0, "failed_runs": 0, "total_iterations": 0 }
}
```

**Claude 的职责 — 每轮结束时**写入以下信号之一：

| 情形 | 写入字段 |
|------|----------|
| 本轮完成，任务未结束 | `round_complete: true` |
| 整个任务全部完成 | `completed: true` + `round_complete: true` |
| 不可恢复错误 | `fatal_error: true` |
| 需要人工确认 | `needs_confirmation: true` |

**Stop Hook 行为**（决策优先级从高到低）：
- `active = false` → 允许停止
- `completed = true` → 允许停止，写入 `status: COMPLETED`
- `fatal_error = true` → 允许停止，写入 `status: FAILED`
- `iteration ≥ max_iterations` → 允许停止
- `needs_confirmation = true` → 允许停止，写入 `status: PAUSED`（用户确认后重置该字段）
- `round_complete = true` → 递增 `iteration`，重置标志，启动下一轮（exit 3）
- `round_complete = false` → 续跑当前轮，**不**递增计数（exit 3）

> 详见: `commands/general/ralph.md`, `workflows/execution/ralph-manager.md`

### 科研工作流
```bash
/literature-review <主题> --zotero-collection <集合> --style <风格>
/experiment-track create|config|result|report|compare --exp-id <ID>
/agents literature-manager|paper-writing-assistant|experiment-logger|data-analyst <任务>
```

### 端口管理 (全局)
```bash
python scripts/port-manager.py register <port> <project> <service>
python scripts/port-manager.py conflicts / suggest <service>
```
> PreToolUse Hook 自动检测 Docker 端口冲突。详见: `docs/port-management/PORT-MANAGEMENT-GUIDE.md`

---

## 六、代码规范

- 详见: `docs/coding-standards.md`
- TypeScript: 使用 ES modules, 优先 interface
- 测试: 同目录 `*.test.ts`, TDD优先

---

## 六.五、上下文工程准则

> **核心指标**: 信噪比 (SNR) — 每个 token 对任务完成的贡献度。加载精准信息，而非更多信息。

**三大失效模式**:
- **上下文投毒**: 过时/矛盾信息污染上下文 → 定期审计 CLAUDE.md，废弃规则加标记，单一事实源
- **注意力漂移**: 长对话或批量任务中遗忘约束 → 持久化规划文件每轮重读，关键约束写入 CLAUDE.md
- **上下文衰减**: ~300-400k tokens 起性能退化 → 主动 ~250k 压缩，新任务开新会话

**5 习惯**: ① 精准加载按需注入 ② 压缩终端输出 ③ 单一事实源 ④ 定期审计固定上下文税 ⑤ 避免内容重复

**会话管理规则**:
- 新任务 → 新会话 | 失败尝试 → /rewind 重试而非纠正
- /compact 时附上未来方向说明（防坏压缩）| Subagent 隔离大量中间输出

> 详细指南: `docs/CONTEXT-ENGINEERING-GUIDE.md`

---

## 七、自主决策授权

### ✅ 完全自主 (无需确认)
代码实现/优化、Bug修复、测试编写、Agent调度、配置自动更新、并行任务分配、规范编写、QA审查和自动修复、P2问题处理

### ⚠️ 需要确认
删除现有功能、修改公共API、引入新依赖、数据库Schema变更、生产环境操作、P0/P1问题修复策略

### 🔴 绝对禁止 (硬性约束)
- **禁止批量删除文件**: 不允许 `rm *`、`rm -rf`、`find -delete`，必须逐个确认
- **禁止静默兜底机制**: 所有 fallback/catch-all 必须含 `⚠️ WARNING` 日志，不允许静默吞掉错误

> 详见运行约束: `memory/best-practices.md` BP-017；Claude Code 配置与使用指南: `docs/BEST-PRACTICES.md`

---

## 八、进化指令

### 当遇到问题时
1. 分析错误根因 → 2. 检查是否重复问题 → 3. 生成解决方案 → 4. 更新相关配置 → 5. 记录到 `memory/lessons-learned.md` → 6. 验证效果

### 当完成复杂任务时
1. 回顾执行过程 → 2. 识别可优化点 → 3. 提炼最佳实践 → 4. 更新Agent定义或命令

### 当发现更好方案时
1. 对比新旧方案 → 2. 评估改进幅度 → 3. 更新配置或创建新模式 → 4. 标记旧方案为deprecated

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
- ❌ `"I:\\APP\\Git\\usr\\bin\\bash.exe" "script.sh"`（Claude Code 会重复追加 `bash`，导致 `cannot execute binary file`）
- ❌ `./script.sh`（Windows 上不工作）

### 跨平台测试要求

提交配置变更前验证：① Windows 实际执行测试 ② JSON 格式验证 ③ 路径兼容性（绝对 vs 相对）④ hooks 执行效果（不仅是加载）

### StatusLine stdin JSON 规范

| 场景 | 特征 | `total_cost_usd` |
|------|------|-----------------|
| 对话启动 | `session_id` + `cwd`，无 cost | 不存在 |
| Stop 事件 | `model` + `cost` | **> 0** |
| 初始化调用 | `session_id` + `cost=0` | = 0 |

**唯一可靠渲染触发条件：`total_cost_usd > 0`**

**❌ 错误做法（已验证失效）**：
- `[[ -z "$HUD_SESSION_JSON" ]]` — 启动时 JSON **不为空**，此判断无效
- `grep -q '"session_id"'` — Stop 事件 JSON **也可能含 session_id**，会误杀渲染
- `! grep -q '"cost"'` — cost=0 的初始化调用也含 cost 字段

详细格式样本及 guard 逻辑示例: `docs/hud/statusline-json-formats.md`

### 配置变更同步

修改 hooks 配置后同步更新: `hooks/hooks.json` + `QUICK-REFERENCE.md` + `CLAUDE.md`

### 跨会话 Edit 规则

上下文压缩后启动新会话时，**必须先 Read 文件**才能 Edit，即使摘要中提到"已读取该文件"。

---

## 九、记忆系统

**文件存储**:
- `memory/lessons-learned.md` — 经验库
- `memory/best-practices.md` — 策展型最佳实践条目库
- `memory/error-patterns.md` — 错误模式
- `memory/agent-performance.md` — Agent性能
- `memory/optimization-history.md` — 优化历史
- `docs/BEST-PRACTICES.md` — Claude Code 使用与配置指南

> 性能监控系统、上下文归档系统、Graphiti知识图谱、多层记忆协同详细说明: `docs/MEMORY-SYSTEM.md`

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

详见: `commands/research/`, `docs/research/research-support-guide.md`

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

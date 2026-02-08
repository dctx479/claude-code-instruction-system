# 太一元系统核心配置
# 版本: 3.1.0 Taiyi (太一) - 道之演化 (Evolution of the Way)
# 发布日期: 2026-01-23

> **太一**，道家最高神格，代表宇宙本源。道生一，一生二，二生三，三生万物。
> 太一元系统承载此哲学，从本源智慧出发，驭众智、启新程，自进化而生生不息。

## 3.1 新特性

### Ralph Loop - 自主循环执行
```bash
/ralph "完成所有待办事项"  # 自主执行直到完成
/ralph status              # 查看执行状态
```
详见: `commands/general/ralph.md`

### HUD Statusline - 实时状态可视化
```
[10:30:15] Sonnet | @architect | designing | [###.....] 30% | R:3/10
```
详见: `.claude/statusline/hud.sh`

### Intent Detector - 智能意图识别
自动分析用户输入，推荐合适的 Agent 和 Skill。
详见: `hooks/intent-detector.sh`, `config/keywords.json`

### Model Router - 自动模型选择
根据任务复杂度自动选择最优模型 (Opus/Sonnet/Haiku)。
详见: `workflows/model-router.md`

### Plan-Scoped Memory - 计划级知识隔离
为每个开发计划创建独立的知识空间，避免上下文污染。
详见: `workflows/plan-scoped-memory.md`

### 主题系统
```bash
cc-patcher.sh theme nerd   # 切换主题
cc-patcher.sh themes       # 列出可用主题
```
可用主题: default, minimal, nerd

### TUI Config - 交互式配置系统
基于 Rust + ratatui 的终端配置界面:
```bash
taiyi-tui-config --path /project
```
- 实时预览配置变更
- 可视化编辑 Agent 定义
- 主题选择器
- 5 个标签页: Overview, Agents, Themes, Hooks, Memory

详见: `tools/tui-config/README.md`

### Autopilot - 全自主执行模式
端到端自动执行，从需求到交付:
```bash
/autopilot "开发用户认证系统"           # 默认监督模式
/autopilot full "快速原型开发"          # 完全自主
/autopilot supervised "重构支付模块"    # 阶段审核
/autopilot step "数据库迁移"            # 每步确认
```

**5 阶段工作流**:
1. Planning - 任务分解、策略选择
2. Specification - 规范生成、架构设计
3. Development - Ralph Loop 执行 + Model Router
4. QA - 自动审查、自愈修复
5. Delivery - 文档生成、变更记录

详见: `commands/general/autopilot.md`, `workflows/autopilot-flow.md`

### Research Parallel - 科研并行工作流
多 Agent 并行执行科研任务:
```bash
/literature-review "主题" --parallel --workers 5  # 3.3x 加速
/experiment-track parallel --workers 4             # 2.3x 加速
```

**并行策略**:
- SWARM: 文献综述 (5 workers)
- PARALLEL: 实验执行 (4 workers)
- HIERARCHICAL: 数据分析 (lead + workers)

详见: `workflows/research-parallel.md`

### Rust 性能工具
高性能 Rust 实现，显著提升执行速度:

**HUD Renderer** (7-10x 提升):
```bash
hud-render --theme nerd --format full
```
详见: `tools/hud-render-rust/README.md`

**Git Info Collector** (5-8x 提升):
```bash
git-info status --format compact
git-info log --oneline --count 10
```
详见: `tools/git-info-rust/README.md`

### Port Management - 全局端口管理系统
跨项目端口冲突预防与管理，自动集成到开发工作流：

**核心能力**：
- 🔍 **自动检测**: PreToolUse Hook 自动拦截 Docker 命令，检查端口冲突
- 📊 **集中管理**: 全局端口注册表 (config/port-registry.json v2.0.0)
- 🎯 **智能分配**: 按服务类型推荐可用端口 (MySQL: 3306-3399, Redis: 6379-6449)
- 🏢 **项目隔离**: 多项目端口分组，避免交叉干扰
- 📝 **审计追踪**: 操作历史记录，可追溯端口使用

**自动触发机制**：
```bash
# 当执行 Docker 命令时，自动检查端口冲突
docker run -p 3307:3306 mysql  # ⚠️ 自动警告：端口 3307 已被 test-project/mysql 占用
docker run -p 9999:80 nginx    # ✅ 自动通过：端口 9999 空闲
```

**手动管理命令**：
```bash
# 注册端口
python scripts/port-manager.py register 3307 myproject mysql -d "主数据库"

# 查看冲突
python scripts/port-manager.py conflicts

# 推荐可用端口
python scripts/port-manager.py suggest mysql

# 导出项目配置
python scripts/port-manager.py export myproject --output myproject.env
```

**集成点**：
- **Hooks**: 集成到 `hooks.json` 的 Bash PreToolUse 钩子
- **Docker**: 自动解析 `docker run -p` 和 `docker-compose` 端口映射
- **Git**: 可选 pre-commit hook 验证配置文件端口
- **CI/CD**: 支持导出 .env 和 docker-compose.yml 格式

**详见**：
- 架构设计: `docs/PORT-MANAGEMENT-ARCHITECTURE.md`
- 使用指南: `docs/PORT-MANAGEMENT-GUIDE.md`
- 集成指南: `docs/PORT-INTEGRATION.md`
- 配置文件: `config/port-registry.json`, `config/port-ranges.json`
- 核心工具: `scripts/port-manager.py`, `scripts/port-management/`

**效果**：
- 🚫 消除 "port already in use" 调试时间
- 📈 提升多项目并行开发效率
- 🛡️ 防止端口冲突导致的服务启动失败
- 📚 提供端口使用文档和历史审计

---

## 元系统声明

本系统具备以下核心能力:
1. **自进化** (道之演化): 从错误中学习，自动完善配置，如道之自然流转
2. **Agent驾驭** (统御万物): 智能编排多Agent协作，如太一统御宇宙万象
3. **知识沉淀** (明心见性): 持久化学习成果，如河图洛书承载天机
4. **动态适应** (因时制宜): 根据任务自动选择最优策略，如阴阳消长自然调和

---

## 配置文件说明 (Configuration Files Guide)

### 配置文件结构

太一元系统使用多个配置文件来管理不同层级的设置：

#### 全局配置文件

| 文件 | 路径 | 用途 | 是否手动编辑 |
|------|------|------|-------------|
| **settings.json** | `~/.claude/settings.json` | 全局设置（hooks、statusLine、env、permissions） | ✅ 是 |
| **.claude.json** | `~/.claude.json` | 用户数据（启动次数、项目历史、提示历史） | ❌ 否（自动管理） |

#### 项目配置文件

| 文件 | 路径 | 用途 | 是否提交到 Git |
|------|------|------|---------------|
| **settings.json** | `.claude/settings.json` | 项目级设置（覆盖全局设置） | ✅ 可选 |
| **hooks.json** | `hooks/hooks.json` | 项目特定的 hooks 配置 | ✅ 推荐 |

### 配置优先级

```
项目级 .claude/settings.json
    ↓ 覆盖
全局级 ~/.claude/settings.json
    ↓ 覆盖
默认配置
```

### 常见配置项

#### 全局 settings.json 示例

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your-token",
    "ANTHROPIC_BASE_URL": "https://api.anthropic.com/"
  },
  "model": "claude-sonnet-4-5-20250929",
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline/hud.sh render"
  },
  "hooks": {
    "PreToolUse": [...],
    "Stop": [...]
  },
  "permissions": {
    "defaultMode": "default"
  }
}
```

#### 项目 settings.json 示例

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash ./.claude/statusline/hud.sh render"
  },
  "hooks": {
    "PreToolUse": [...]
  }
}
```

### 配置文件查找顺序

遇到配置问题时，按以下顺序检查：

1. **项目配置**：`.claude/settings.json`
2. **全局配置**：`~/.claude/settings.json`
3. **用户数据**：`~/.claude.json`（通常不需要检查）

### 重要提示

⚠️ **不要手动编辑 `~/.claude.json`**
- 此文件由 Claude Code 自动管理
- 包含启动次数、项目历史等数据
- 手动编辑可能导致数据损坏

✅ **应该编辑 `~/.claude/settings.json`**
- 用于配置 hooks、statusLine、环境变量等
- 这是正确的全局配置文件

### 详细文档

- 配置文件完整指南：`docs/CONFIG-FILES-GUIDE.md`（待创建）
- Hooks 配置：参见"八、进化指令 - 配置文件验证规则"
- Statusline 配置：参见 `memory/lessons-learned.md` #007

---

## 一、自进化协议 (Self-Evolution Protocol)

### 1.1 学习触发机制

当以下情况发生时，触发自我完善:
- ❌ 任务失败或需要人工纠正
- ⚠️ 重复犯同类错误 (≥2次)
- 💡 发现更优的解决方案
- 📝 用户通过 `#` 键添加指令
- 🔄 完成复杂任务后的回顾

### 1.2 自动更新流程

```
错误/经验 → 分析根因 → 生成改进建议 → 更新配置 → 验证效果
     ↑                                              ↓
     └──────────── 持续反馈循环 ←──────────────────┘
```

**更新目标文件**:
- `CLAUDE.md` - 核心指令
- `agents/*.md` - Agent定义
- `commands/*.md` - 自定义命令
- `memory/lessons-learned.md` - 经验教训库

### 1.3 经验沉淀格式

```markdown
## [日期] 经验条目 #ID

### 问题描述
[什么出错了/什么可以更好]

### 根因分析
[为什么会发生]

### 解决方案
[如何修复/改进]

### 配置更新
[对CLAUDE.md或其他文件的具体修改]

### 验证方法
[如何确认改进有效]
```

---

## 二、Agent 驾驭系统 (Agent Orchestration System)

### 2.1 Agent 层级架构

```
┌─────────────────────────────────────────────────────────┐
│                    Orchestrator (编排者)                 │
│  - 任务分解与分配                                        │
│  - 策略选择 (并行/串行/层级/协作)                        │
│  - 结果整合与质量控制                                    │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  Specialist   │ │  Specialist   │ │  Specialist   │
│  专家Agent    │ │  专家Agent    │ │  专家Agent    │
└───────────────┘ └───────────────┘ └───────────────┘
        │               │               │
        ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   Worker      │ │   Worker      │ │   Worker      │
│  执行Agent    │ │  执行Agent    │ │  执行Agent    │
└───────────────┘ └───────────────┘ └───────────────┘
```

### 2.2 渐进式披露机制 (Progressive Disclosure)

**核心理念**: 仅在需要时加载完整Agent定义，节省60-80% Token开销

**加载策略**:
```
启动时:
1. 读取 agents/INDEX.md 获取所有Agent元数据
2. 仅加载元数据到上下文 (~100 tokens/agent)
3. 总成本: 25 agents × 100 tokens = 2.5K tokens

任务执行时:
1. 根据任务需求，匹配相关Agent
2. 按需加载完整的Agent定义 (~2-5k tokens/agent)
3. 执行完成后，可选择性卸载

预期效果:
- Token节省: 60-80%
- 支持规模: 100+ Agents
- 启动速度: 提升3-5倍
```

**使用方法**:
```markdown
# 查看所有可用Agent
请读取 agents/INDEX.md

# 加载特定Agent
需要使用 architect Agent，请读取 agents/architect.md

# 智能匹配
根据任务"设计用户认证系统"，自动匹配并加载相关Agent
```

**详细文档**: `agents/INDEX.md`

### 2.3 编排策略矩阵

| 任务特征 | 推荐策略 | Agent配置 |
|----------|----------|-----------|
| 独立子任务 | **并行** | 多Worker同时执行 |
| 依赖链任务 | **串行** | 管道式传递 |
| 复杂决策 | **层级** | Specialist领导Worker |
| 跨领域问题 | **协作** | 多Specialist讨论 |
| 创新探索 | **竞争** | 多方案并行评估 |

### 2.4 智能策略选择系统

#### 自动策略选择
系统通过 `strategy-selector` Agent 自动分析任务特征并推荐最优编排策略:

**分析维度**:
1. **任务复杂度**: 简单/中等/复杂
2. **子任务数量**: 1-2 / 3-5 / 6+
3. **依赖关系**: 无依赖/部分依赖/强依赖
4. **领域分布**: 单领域/跨领域/多领域
5. **创新程度**: 常规/创新/探索性
6. **时间敏感度**: 低/中/高
7. **规模等级**: 小(<10) / 中(10-50) / 大(50+)

**决策树**:
```
规模>50? ─YES→ SWARM
    NO↓
独立任务? ─YES→ PARALLEL
    NO↓
强依赖? ─YES→ SEQUENTIAL
    NO↓
需专家? ─YES→ HIERARCHICAL
    NO↓
跨领域? ─YES→ COLLABORATIVE
    NO↓
探索性? ─YES→ COMPETITIVE
    NO↓
默认: PARALLEL
```

**使用方式**:
```markdown
1. Orchestrator 自动调用 strategy-selector
2. 获得策略推荐和置信度
3. 根据推荐执行编排
4. 监控执行并记录性能
```

#### 编排模式详解

完整模式定义参见: `workflows/orchestration-patterns.md`

| 模式 | 加速比 | 质量 | 成本 | 最佳场景 |
|-----|--------|------|------|---------|
| PARALLEL | 3-5x | 中 | 中 | 独立子任务 |
| SEQUENTIAL | 1x | 高 | 低 | 依赖链任务 |
| HIERARCHICAL | 2-3x | 高 | 高 | 需专家指导 |
| COLLABORATIVE | 2.8-4.4x | 极高 | 高 | 跨领域问题 |
| COMPETITIVE | 1.5-2x | 最优 | 高 | 探索创新 |
| SWARM | 5-10x | 中 | 低 | 大规模批量 |

#### 监控与整合

完整监控机制参见: `workflows/orchestration-monitor.md`

**核心功能**:
- **实时监控**: Agent健康状态、任务进度、性能指标
- **异常处理**: 自动检测异常并执行恢复策略
- **结果整合**: 智能合并多Agent输出，解决冲突
- **质量验证**: 自动验证结果完整性和正确性
- **性能分析**: 识别瓶颈，优化编排效率

---

## 三、质量保障系统 (Quality Assurance System)

### 3.1 Spec-First开发流程

**核心理念**: 先写规范，后写代码

```
需求 → 规范编写 → 开发实现 → QA验证 → 发布
        (spec-writer)          (qa-reviewer + qa-fixer)
```

**规范管理**:
- 规范目录: `specs/`
- 规范模板: `specs/SPEC-TEMPLATE.md`
- 规范命名: `SPEC-{feature-name}.md`

**规范包含**:
1. 需求概述 - 背景、目标、范围
2. 技术方案 - 架构、数据模型、API、前端
3. 实现计划 - 任务拆分、时间估算
4. 验收标准 - 功能、性能、安全、测试
5. 风险与对策 - 技术风险、业务风险

### 3.2 自我修复质量循环 (Self-Healing QA Loop)

**工作流程**:
```
开发完成 → QA Reviewer (审查评分)
              ↓
         [评分 ≥80?]
              ↓
    是 → 发布    否 → [有P2问题?]
                        ↓
                  是 → QA Fixer (自动修复)
                        ↓
                  重新审查 (循环)
                        ↓
                  否 → 人工修复
```

**QA Agent对**:

**qa-reviewer** (质量审查专家):
- 对照规范验证功能完整性
- 评估代码质量 (类型、规范、错误处理)
- 检查测试覆盖率
- 验证性能和安全指标
- 生成 `QA-REPORT.md` (评分0-100)

**qa-fixer** (自动修复专家):
- 解析QA报告，识别可自动修复问题
- 修复低风险问题 (代码格式、类型标注等)
- 验证修复效果
- 生成 `FIX-REPORT.md`
- 触发重新审查

**评分体系** (总分100):
- 功能完整性: 40分
- 代码质量: 30分
- 测试覆盖: 20分
- 性能指标: 5分
- 安全检查: 5分
- 通过线: ≥80分

**问题严重程度**:
- 🔴 P0 (严重): 阻塞发布，必须人工修复
- 🟡 P1 (重要): 建议修复，视情况决定人工或自动
- 🟢 P2 (轻微): 可自动修复，不影响功能

### 3.3 质量保障命令

```bash
# 规范管理
/agent spec-writer     # 生成功能规范

# 质量验证
/agent qa-reviewer     # 执行QA审查
/agent qa-fixer        # 自动修复问题

# 完整流程
/spec-first           # 启动Spec-First完整流程
```

### 3.4 相关文档

- 规范指南: `specs/README.md`
- QA循环: `workflows/self-healing.md`
- 使用示例: `.claude/examples/spec-first-workflow.md`
- Agent定义: `agents/spec-writer.md`, `agents/qa-reviewer.md`, `agents/qa-fixer.md`

---

## 四、编排系统使用指南

### 4.1 快速开始

**基本用法**:
```markdown
当面对复杂任务时,Orchestrator 会自动:
1. 调用 strategy-selector 分析任务特征
2. 选择最优编排策略
3. 分配和调度Agent
4. 监控执行并整合结果
```

**手动触发编排**:
```bash
/orchestrate         # 启动智能编排模式
/parallel            # 强制使用并行策略
/swarm               # 强制使用群体策略
```

### 4.2 使用示例

#### 示例1: 复杂功能开发(自动选择HIERARCHICAL)
```markdown
任务: "开发用户认证系统"

自动分析:
- 复杂度: 高
- 跨领域: 是(前端+后端+数据库)
- 需专家: 是

→ 推荐策略: HIERARCHICAL
→ 预期加速: 2-3x

执行:
1. architect 设计架构 (30分钟)
2. 并行开发: 3个workers (2小时)
3. architect 审核整合 (30分钟)

总时间: 3小时 vs 单Agent 8小时
```

#### 示例2: 大规模迁移(自动选择SWARM)
```markdown
任务: "将200个文件迁移到TypeScript"

自动分析:
- 规模: 200个文件 > 50
- 独立: 是

→ 推荐策略: SWARM
→ 预期加速: 5-10x

执行:
- 10个haiku workers并行
- 4批处理 (50文件/批)
- 实时进度监控

总时间: 20分钟 vs 单Agent 3.3小时
```

#### 示例3: 性能优化(自动选择COMPETITIVE)
```markdown
任务: "优化API性能,探索最佳方案"

自动分析:
- 创新程度: 探索性
- 质量优先: 是

→ 推荐策略: COMPETITIVE
→ 预期: 获得最优解

执行:
- 3个agents并行提出不同方案
- 自动评估各方案性能
- 选择最佳并提供备选

结果: 找到5x性能提升方案
```

### 4.3 监控与调试

**实时进度查看**:
```markdown
系统自动显示:
[████████░░] 80% (8/10 completed)

Agents状态:
- architect: working ✓
- worker-1: completed ✓
- worker-2: working ✓
- worker-3: retrying ⚠

最近事件:
- [14:30] worker-1 完成任务
- [14:29] worker-3 超时,正在重试
```

**异常自动处理**:
- Agent无响应 → 自动重启或切换备用
- 任务超时 → 自动重试或分解
- 高错误率 → 升级模型或调整策略

### 4.4 性能优化建议

**提高效率**:
- 充分分解独立子任务
- 识别真实依赖关系
- 合理设置并行度

**降低成本**:
- 简单任务用 haiku
- 复杂任务用 sonnet
- 关键决策用 opus

**质量保证**:
- 设置清晰验收标准
- 启用自动质量验证
- 记录并学习失败案例

### 4.5 相关文档

- Agent定义: `agents/orchestrator.md`, `agents/strategy-selector.md`
- 编排模式库: `workflows/orchestration-patterns.md`
- 监控整合: `workflows/orchestration-monitor.md`
- 完整示例: `examples/orchestration-examples.md`

---

## 四、Skills 系统 (Skills System)

### 4.1 什么是 Skills？

**Skills** 是自动激活的能力扩展单元，与 Agents 和 Commands 的区别：

| 类型 | 职责 | 触发方式 | 示例 |
|------|------|----------|------|
| **Skills** | 知识包，能力增强 | 自动发现 | PyTorch, pandas, SHAP |
| **Agents** | 执行单元，任务处理 | Orchestrator 调度 | spec-writer, qa-reviewer |
| **Commands** | 显式用户操作 | 手动调用 | /commit, /review |

**关系**：
- Skills 可以调用 Agents
- Agents 可以激活 Skills
- Commands 可以触发 Orchestrator，进而调度 Agents 和 Skills

### 4.2 Skill 设计原则（契约化设计）

每个 Skill 应是自包含的执行单元，遵循四要素框架：

| 要素 | 描述 | 示例 |
|------|------|------|
| **What** | 输入/输出显式声明 | 输入: CSV 文件路径; 输出: 统计报告 |
| **How** | 执行步骤 + 边界情况 | 1. 加载数据 2. 检查缺失值 3. 计算统计量 |
| **When done** | 验收标准 | 报告包含均值、方差、分布图 |
| **What NOT** | 边界约束 (guardrails) | 不修改原始数据；不输出超过 10 列 |

**设计建议**：
- 原子化：每个 Skill 只做一件事
- 可组合：通过编排配置组合多个 Skills
- 可验证：明确验收标准，便于质量门检查

### 4.3 渐进式披露机制

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

### 4.4 已集成的 Skills

#### 核心研究 Skills（项目内置）

| Skill | 描述 | 触发词 | 类别 |
|-------|------|--------|------|
| **deep-research** | 深度研究，Lead Agent + Subagent 并行调研 | `deep-research <主题>` | research |
| **market-insight** | 市场洞察，三段式用户画像与产品机会分析 | `/insight <产品描述>` | product |
| **exa-research** | 企业与市场研究，基于 Exa 搜索引擎 | `研究竞争对手`, `分析行业` | research |
| **brightdata-research** | 电商平台深度调研，反反爬虫支持 | `电商调研`, `畅销排行` | research |
| **social-media-research** | 跨平台社媒研究，12+ 平台覆盖 | `舆情监控`, `KOL 分析` | research |
| **literature-mentor** | 文献深度解读，支持交互模式和报告模式，自动识别文献类型 | `解读这篇论文`, `生成精读报告` | research |
| **paper-revision** | 论文风格修改，技术准确性保持 | `修改论文风格` | research |

**使用示例**:
```markdown
# 深度研究
"deep-research 2024年AI Agent发展趋势"

# 市场洞察
"/insight 我要做一个AI产品：基于Claude Code的智能数据分析平台"

# 企业研究
"研究一下特斯拉的竞争对手"

# 电商调研
"分析Amazon上智能手表市场的畅销排行"

# 社媒分析
"监控小红书上品牌XXX的舆情"

# 文献精读（交互模式）
"帮我解读这篇文献 'Attention Is All You Need'"

# 文献精读（报告模式）
"生成这篇文献的精读报告 'Deep Residual Learning for Image Recognition'"
```

**Skill 组合模式**:
- **社媒 + 深度调研** = 社媒调研智能体
- **社媒 + 市场洞察** = 消费者画像
- **电商 + 企业研究** = 全链路竞争分析
- **literature-mentor + paper-writing-assistant** = 文献综述写作
- **literature-mentor + experiment-logger** = 实验设计与执行
- **literature-mentor + data-analyst** = 数据分析方法学习

#### claude-scientific-skills (140+ 科研技能)

**来源**: [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills)

**包含的 Skills**:
- **Machine Learning & AI**: 机器学习算法、模型训练、超参数优化
- **Deep Learning**: CNN、RNN、Transformer、GAN
- **Reinforcement Learning**: DQN、PPO、SAC、MADDPG
- **Time Series Analysis**: ARIMA、Prophet、LSTM
- **Model Interpretability**: SHAP、LIME、Captum、Fairlearn
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

**详细文档**: `.claude/skills/README.md`, `.claude/skills/INTEGRATION-GUIDE.md`

### 4.5 MCP 集成配置

新增的研究 Skills 需要配置对应的 MCP 服务器：

#### Exa MCP（企业与市场研究）
```bash
claude mcp add --transport http exa "https://mcp.exa.ai/mcp?tools=web_search_advanced_exa"
```

#### Bright Data MCP（电商调研）
```json
{
  "mcpServers": {
    "brightdata": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-brightdata"],
      "env": {
        "BRIGHTDATA_API_TOKEN": "your-token"
      }
    }
  }
}
```

#### TikHub MCP（社媒研究）
```json
{
  "mcpServers": {
    "tikhub": {
      "command": "npx",
      "args": ["-y", "@tikhub/mcp-server"],
      "env": {
        "TIKHUB_API_TOKEN": "your-token"
      }
    }
  }
}
```

**详细配置**: 参见各 Skill 的 `SKILL.md` 文件

---

## 五、核心命令

### 开发
```bash
npm run build        # 构建
npm run dev         # 开发服务器
npm run test        # 测试
npm run typecheck   # 类型检查
```

### Agent 管理
```bash
/agents              # 管理子Agent
/orchestrate         # 启动智能编排
/parallel            # 并行执行
/swarm               # 群体执行
/evolve              # 触发系统进化
```

### 自主执行
```bash
/ralph "任务"                    # Ralph Loop 自主执行
/autopilot "任务"                # Autopilot 全自主模式
/autopilot full "任务"           # 完全自主
/autopilot supervised "任务"     # 监督模式
/autopilot status                # 查看执行状态
```

### 科研工作流
```bash
# 文献综述
/literature-review <主题> --zotero-collection <集合> --style <风格>

# 实验追踪
/experiment-track create --name <名称>
/experiment-track config --exp-id <ID> --file <配置>
/experiment-track result --exp-id <ID> --metrics <结果>
/experiment-track report --exp-id <ID>
/experiment-track compare --exp-ids <ID1,ID2,ID3>

# 科研 Agent
/agents literature-manager <任务>      # 文献管理
/agents paper-writing-assistant <任务> # 论文写作
/agents experiment-logger <任务>       # 实验记录
/agents data-analyst <任务>            # 数据分析
```

---

## 六、代码规范

[保持简洁,引用详细规范文件]
- 详见: `docs/coding-standards.md`
- TypeScript: 使用 ES modules, 优先 interface
- 测试: 同目录 `*.test.ts`, TDD优先

---

## 七、自主决策授权

### ✅ 完全自主 (无需确认)
- 代码实现和优化
- Bug修复和调试
- 测试编写
- Agent调度决策
- 配置自动更新 (基于学习)
- 并行任务分配
- 规范编写和更新
- QA审查和自动修复
- P2问题的自动处理

### ⚠️ 需要确认
- 删除现有功能
- 修改公共API
- 引入新依赖
- 数据库Schema变更
- 生产环境操作
- P0/P1问题的修复策略

---

## 八、进化指令

### 当遇到问题时:
```
1. 分析错误根因
2. 检查是否为重复问题
3. 生成解决方案
4. 更新相关配置文件
5. 记录到 memory/lessons-learned.md
6. 验证改进效果
```

### 当完成复杂任务时:
```
1. 回顾执行过程
2. 识别可优化点
3. 提炼最佳实践
4. 更新Agent定义或命令
5. 沉淀为可复用模式
```

### 当发现更好方案时:
```
1. 对比新旧方案
2. 评估改进幅度
3. 更新配置或创建新模式
4. 标记旧方案为deprecated
```

### 配置文件验证规则 (新增)

#### JSON 配置文件
在修改或创建 JSON 配置文件后，必须进行验证：

```bash
# 验证 JSON 格式
python -m json.tool <配置文件.json> > /dev/null

# 或使用 jq
jq empty <配置文件.json>
```

**必须验证的文件**:
- `hooks/hooks.json` - Hooks 配置
- `config/settings.json` - 系统设置
- `config/keywords.json` - 关键词索引
- `config/mcp-servers.json` - MCP 服务器配置
- 所有 `.claude/**/*.json` 文件

#### Hooks 配置格式规范

**⚠️ 重要：全局 vs 项目级别差异**

**全局级别** (`~/.claude/settings.json`):
- ✅ Matcher 使用**字符串格式**: `"matcher": "Bash"`
- ✅ 支持精确匹配、正则表达式、通配符
- ✅ 示例：
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "python \"script.py\"",
        "timeout": 3000
      }]
    }]
  }
}
```

**项目级别** (`hooks/hooks.json`):
- ✅ Matcher 格式与全局配置**完全相同**，使用字符串
- ✅ 格式已验证：`"matcher": "Bash"` ✅ 可以参考项目中的 `hooks/hooks.json` 作为模板

**Matcher 格式统一**:
| 配置级别 | Matcher 格式 | 示例 |
|---------|-------------|------|
| 全局 | 字符串 | `"matcher": "Bash"` |
| 项目 | 字符串 | `"matcher": "Bash"` |

**支持的 Matcher 模式**（全局和项目通用）:
- 精确匹配：`"Bash"`, `"Write"`, `"Edit"`
- 正则表达式：`"/Bash|Write/"`
- 多工具匹配：`"Write|Edit"`
- 通配符：`"*"`

**Windows 环境兼容性**:
- ✅ 优先使用 Git Bash: `"C:\\Program Files\\Git\\bin\\bash.exe" "./script.sh"`
- ✅ 备选 WSL: `"wsl bash /mnt/c/path/to/script.sh"`
- ✅ 备选 PowerShell: `"powershell -ExecutionPolicy Bypass -File \"script.ps1\""`
- ❌ 避免直接使用 `./script.sh` (在 Windows 上不工作)

**示例 - 项目级别 hooks 配置**:
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write",
      "hooks": [{
        "type": "command",
        "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"./validate.sh\"",
        "timeout": 5000
      }]
    }],
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"./on-stop.sh\""
      }]
    }]
  }
}
```

**示例 - 全局 settings.json (仅 statusLine)**:
```json
{
  "statusLine": {
    "type": "command",
    "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"~/.claude/statusline-wrapper.sh\""
  }
}
```

#### 跨平台测试要求
在提交配置变更前：
1. ✅ 在 Windows 上测试（如果有 Windows 用户）
2. ✅ 验证 JSON 格式正确性
3. ✅ 检查路径兼容性（绝对路径 vs 相对路径）
4. ✅ 测试 hooks 实际执行（不仅是加载）

#### 配置变更同步
修改 hooks 配置后，必须同步更新：
1. `hooks/hooks.json` - 主配置文件
2. `QUICK-REFERENCE.md` - 快速参考示例
3. `CLAUDE.md` - 本文档（如有规范变更）
4. 相关文档中的示例代码

---

## 九、记忆系统

### 9.1 传统记忆 (文件存储)

- 经验库: `memory/lessons-learned.md`
- 最佳实践: `memory/best-practices.md`
- 错误模式: `memory/error-patterns.md`
- Agent性能: `memory/agent-performance.md`
- 优化历史: `memory/optimization-history.md`
- 性能报告: `memory/performance-reports/`

### 9.2 性能监控系统 (Performance Monitoring)

**核心能力**:
- 📊 全面的性能数据收集
- 📈 趋势分析和异常检测
- 🎯 数据驱动的优化决策
- 🔄 自动优化和A/B测试

**核心Agent**:
- **performance-monitor**: 监控和分析Agent性能数据
- **auto-optimizer**: 基于数据自动优化系统配置

**监控指标**:
- 任务完成率和成功率
- Token消耗和执行时间
- 用户满意度评分
- 成本效率分析
- 首次成功率和重试次数

**使用方法**:

**生成性能报告**:
```bash
/performance-report daily    # 日报
/performance-report weekly   # 周报
/performance-report monthly  # 月报
```

**触发系统优化**:
```bash
/optimize-system            # 全面优化分析
/optimize-system cost       # 专注成本优化
/optimize-system architect  # 优化特定Agent
```

**查询Agent性能**:
```bash
/agents performance-monitor "分析architect最近一周的表现"
```

**验证优化效果**:
```bash
/agents auto-optimizer "验证优化方案 #001 的效果"
```

**优化类型**:
1. **模型选择优化**: 识别可降级到Haiku的场景
2. **Prompt优化**: 精简长度,改进清晰度和有效性
3. **工作流优化**: 并行化、缓存、流程简化
4. **成本优化**: 识别高成本操作,推荐替代方案

**自动优化流程**:
```
数据分析 → 机会识别 → 方案设计 → A/B测试 → 效果验证 → 知识沉淀
```

**性能报告**:
- 日报: 关键指标和异常事件
- 周报: 趋势分析和对比
- 月报: 总结汇总和战略建议

**优化记录**:
- 优化历史: `memory/optimization-history.md`
- 优化提案: `memory/optimization-proposals/`
- 性能报告: `memory/performance-reports/`

**集成点**:
- 自进化协议: 性能数据驱动配置优化
- Agent驾驭: 基于性能选择最优Agent和策略
- 质量保障: 监控质量指标,触发质量改进
- 记忆系统: 沉淀优化模式和最佳实践

**详细文档**:
- Agent定义: `agents/performance-monitor.md`, `agents/auto-optimizer.md`
- 性能数据: `memory/agent-performance.md`
- 优化历史: `memory/optimization-history.md`
- 报告模板: `memory/performance-reports/TEMPLATE.md`
- 命令文档: `commands/general/performance-report.md`, `commands/general/optimize-system.md`

### 9.3 上下文归档系统 (Context Archival)

**核心理念**: 在上下文压缩前，将对话中的关键信息结构化沉淀，实现渐进式上下文注入。

**核心能力**:
- 🧠 自动提炼试错后的正确路径
- 📋 index/detail 分离的结构化存储
- 🔍 精准的问题签名匹配
- ⚡ 按需加载，节省 Token

**架构设计**:
```
Layer 1: 实时记忆 (当前对话)
    ↓ PreCompact Hook
Layer 2: 结构化沉淀 (.claude/context/)
    ├── index.json (项目状态、已验证事实)
    └── resolutions/*.ndjson (问题解决方案详情)
    ↓ 定期同步
Layer 3: 长期记忆 (memory/*.md)
```

**核心Agent**:
- **context-archivist**: 对话归档器，提炼关键信息

**使用方法**:

**手动保存上下文**:
```bash
/save-context "完成用户认证功能"
```

**读取项目状态**:
```bash
/read-context index
```

**读取问题解决方案**:
```bash
/read-context resolution res-001
```

**列出所有归档**:
```bash
/read-context list
```

**自动触发**:
- PreCompact Hook 在上下文压缩前自动调用
- 无需手动干预

**渐进式上下文注入**:
```
用户提出新需求
    ↓
自动读取 index.json (轻量级，<2KB)
    ↓
判断是否有相关历史
    ↓
如有相关 → 读取对应 resolution (详细)
    ↓
基于历史经验给出方案，避免重复试错
```

**文件结构**:
```
.claude/context/
├── index.json              # 项目状态索引
├── resolutions/            # 问题解决方案
│   ├── 2026-01-22-143052.ndjson
│   └── 2026-01-23-091234.ndjson
└── sessions/               # 完整会话归档（可选）
```

**index.json 包含**:
- 项目目标和当前状态
- 已验证事实（非猜测）
- 技术约束和环境信息
- 下一步行动计划
- 问题解决方案索引

**resolution 包含**:
- 问题签名（稳定的错误关键词）
- 根本原因分析
- 最终修复步骤（可复现）
- 验证方法
- 反模式（1-3 条不应该做的）
- 涉及的文件（不贴全文）

**集成点**:
- 自进化协议: 归档的 resolutions 同步到 lessons-learned.md
- Agent驾驭: 记录编排策略效果
- 质量保障: 沉淀 QA 发现的问题和修复
- 性能监控: 记录优化模式和效果

**详细文档**:
- Agent定义: `agents/context-archivist.md`
- 命令文档: `commands/general/save-context.md`, `commands/general/read-context.md`
- Hook配置: `.claude/hooks/pre-compact.sh`

### 9.4 知识图谱记忆 (Graphiti)

**核心能力**:
- 🧠 跨会话知识持久化
- 🔍 语义搜索和图遍历
- 🔗 自动关联发现
- 📊 知识演化追踪

**使用方法**:

**存储知识**:
```markdown
存储实体:
- 名称: "实体名称"
- 类型: "实体类型"
- 属性: {"key": "value"}

创建关系:
- 源: "实体A"
- 关系: "关系类型"
- 目标: "实体B"
```

**检索知识**:
```markdown
搜索: 关键词或语义描述
查询实体: 实体名称
检索事件: 时间范围
```

**集成点**:
- 自进化协议: 错误发生时自动沉淀错误模式和解决方案
- Agent驾驭: 记录Agent性能和编排策略效果
- 任务完成: 提炼最佳实践和可复用模式
- 技术决策: 记录决策依据和评估过程
- 性能监控: 记录优化模式和效果数据

**详细文档**:
- 集成指南: `.claude/integrations/graphiti-setup.md`
- 沉淀策略: `.claude/memory/knowledge-strategy.md`
- 使用示例: `.claude/examples/graphiti-usage.md`

### 9.5 多层记忆协同

```
实时记忆 (当前对话)
    ↓ PreCompact Hook
上下文归档 (.claude/context/)
    ├── index.json (轻量级索引)
    └── resolutions/*.ndjson (详细方案)
    ↓ 定期同步
文件记忆 (memory/*.md) ←→ 知识图谱 (Graphiti) ←→ 性能数据库
       ↓                        ↓                      ↓
   结构化文本               关系网络                时序数据
   易于阅读                 易于检索                易于分析
   版本控制                 语义搜索                趋势追踪
```

**同步策略**:
- 实时: 上下文归档 → .claude/context/ (PreCompact Hook)
- 每日: .claude/context/ → memory/*.md (结构化导入)
- 每周: memory/*.md → Graphiti (知识图谱化)
- 持续: 性能数据 → memory/agent-performance.md
- 按需: Graphiti → memory/*.md (生成报告)
- 冲突: 以最新数据为准,手动确认重要变更

**上下文检索协议**:

任务开始前:
1. 自动读取 `.claude/context/index.json`
2. 了解项目当前状态和已验证事实
3. 检查是否有相关历史问题

遇到问题时:
1. 搜索 index 中的 problem_signature
2. 如有匹配，读取对应 resolution
3. 参考历史方案，避免重复试错

提出方案时:
1. 引用相关 resolution ID
2. 说明与历史方案的关系
3. 如有改进，记录到新 resolution

---

## 十、科研支持系统 (Research Support System)

### 10.1 核心理念：Vibe Researching

**定义**：AI 协作研究的新范式
- **AI 角色**：主导执行层面工作（文献综述、数据分析、论文写作）
- **人类角色**：提出问题、设定方向、把控质量
- **核心原则**：AI 是高质量信息加工器，而非生成器

**"Garbage in, Garbage out"**：
- 输入质量决定输出质量
- 必须提供高质量文献（闭源期刊为主）
- 框架确定后再开始写作
- 人工审核每个关键环节

### 10.2 系统架构

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

### 10.3 核心 Agent

#### Literature Manager（文献管理专家）
**职责**：
- 文献导入和分类
- 智能摘要提取
- 引用图谱构建
- 相关文献推荐

**集成**：
- Zotero-MCP：访问个人文献库
- arXiv/PubMed MCP：搜索开源文献

**详见**：`agents/research/literature-manager.md`

#### Paper Writing Assistant（论文写作助手）
**职责**：
- 文献综述生成
- 研究论文撰写
- 写作风格学习
- 自动引用管理

**工作流**：
1. 准备高质量文献（Zotero）
2. 提供顶级期刊范本
3. AI 学习写作风格
4. 生成综述框架（人工审核）
5. AI 撰写初稿
6. 人工审核和润色

**详见**：`agents/research/paper-writing-assistant.md`

#### Experiment Logger（实验记录专家）
**职责**：
- 结构化实验记录
- 参数和配置管理
- 结果追踪和对比
- 复现指南生成

**自动记录**：
- Git commit hash
- 环境依赖
- 随机种子
- 硬件信息
- 执行时间

**详见**：`agents/research/experiment-logger.md`

#### Data Analyst（数据分析专家）
**职责**：
- 数据预处理和清洗
- 统计分析和假设检验
- 高质量可视化
- 结果解读

**工具集成**：
- Python: pandas, numpy, scipy, statsmodels
- Jupyter Notebook: 交互式分析
- LaTeX: 公式和表格生成

**详见**：`agents/research/data-analyst.md`

### 10.4 核心命令

#### /literature-review - 文献综述生成
```bash
/literature-review <主题> \
  --zotero-collection <集合名称> \
  --style <nature|ieee|apa> \
  --output <输出路径>
```

**工作流程**：
1. 准备阶段（人工）：在 Zotero 中收集高质量文献
2. 学习阶段（AI）：分析范本综述的写作风格
3. 规划阶段（AI + 人工审核）：生成综述框架
4. 写作阶段（AI）：按照框架撰写综述
5. 审核阶段（人工）：Review 全文并润色

**详见**：`commands/research/literature-review.md`

#### /experiment-track - 实验追踪
```bash
# 创建实验
/experiment-track create --name <名称> --description <描述>

# 记录配置
/experiment-track config --exp-id <ID> --file <配置文件>

# 记录结果
/experiment-track result --exp-id <ID> --metrics <结果文件>

# 生成报告
/experiment-track report --exp-id <ID> --output <报告路径>

# 对比实验
/experiment-track compare --exp-ids <ID1,ID2,ID3>
```

**详见**：`commands/research/experiment-track.md`

### 10.5 外部工具集成

#### Zotero-MCP
**功能**：访问个人 Zotero 文献库
**安装**：参见 `integrations/zotero-mcp-setup.md`
**使用**：
```bash
# 搜索文献
"帮我在 Zotero 中搜索关于深度学习医学图像分割的论文"

# 总结文献集合
"总结 Zotero 中 'Coronary CTA' 集合的所有论文"
```

#### arXiv/PubMed MCP
**功能**：搜索开源文献数据库
**使用**：自动集成到文献综述工作流

#### Jupyter Notebook
**功能**：交互式数据分析
**集成**：Claude Code 原生支持读写 cell、理解图表输出

#### Pandoc
**功能**：格式转换（Markdown → Word/PDF）
**使用**：
```bash
pandoc review.md -o review.docx --bibliography references.bib
```

### 10.6 最佳实践

#### 文献管理
✅ **推荐**：
- 优先收集闭源期刊高质量论文（IF > 3.0）
- 使用 Zotero Collections 分类管理
- 补充开源数据库（arXiv, PubMed）
- 定期更新和清理文献库

❌ **避免**：
- 把所有 PDF 放本地目录
- 依赖 AI 网络搜索
- 不整理文献元数据

#### 论文写作
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

#### 实验管理
✅ **推荐**：
- 每个实验都记录完整配置
- 使用版本控制（Git）
- 记录随机种子保证可复现
- 定期备份实验数据

❌ **避免**：
- 只记录成功实验
- 忽略环境依赖
- 不记录失败原因

#### 数据分析
✅ **推荐**：
- 使用 Jupyter Notebook 交互式分析
- 进行适当的统计检验
- 生成符合期刊要求的图表
- 报告置信区间和效应量

❌ **避免**：
- 只报告 p 值
- 过度拟合数据
- 忽略多重比较校正

### 10.7 真实案例

#### 案例 1：医学影像 AI 综述
**背景**：冠脉 CTA 影像深度学习分割方向

**成果**：
- 45 页，13,813 单词
- 113 篇引用文献（全部真实）
- 遵循 Nature 期刊风格
- 3-5 天完成（传统方式需 2-3 个月）

**效率提升**：10-20 倍

**详见**：`examples/research-workflow-example.md`

#### 案例 2：Schrödinger（计算药物发现）
**评价**：
> "Claude Code allows us to turn ideas into working code in minutes instead of hours, enabling us to move up to 10x faster in some cases."

**效果**：从想法到代码，从小时级缩短到分钟级

#### 案例 3：斯坦福 Paper2Agent
**创新**：
- 把论文转化成可交互的 AI Agent
- 相当于给每篇论文配了虚拟通讯作者
- 3 小时生成 22 个可用工具

### 10.8 学术诚信

#### 必须遵守
- ✅ 所有引用必须真实可查
- ✅ 人工审核 AI 生成内容
- ✅ 标注 AI 辅助写作（如期刊要求）
- ❌ 不得编造数据和引用
- ❌ 不得抄袭和自我抄袭

#### 质量控制
- ✅ 提供高质量输入（文献、数据）
- ✅ 人工审核关键环节（框架、结论）
- ✅ 验证统计分析正确性
- ❌ 不完全依赖 AI
- ❌ 不跳过人工审核

#### 局限性
- AI 在执行层面强，但判断层面有短板
- 需要人类把关：方法论透明度、学术诚信、批判性思维
- Vibe Researching 是人机协作，而非 AI 替代

### 10.9 相关文档

**核心文档**：
- 使用指南：`docs/research-support-guide.md`
- 工作流示例：`examples/research-workflow-example.md`
- Zotero 集成：`integrations/zotero-mcp-setup.md`

**Agent 定义**：
- `agents/research/literature-manager.md`
- `agents/research/paper-writing-assistant.md`
- `agents/research/experiment-logger.md`
- `agents/research/data-analyst.md`

**命令文档**：
- `commands/research/literature-review.md`
- `commands/research/experiment-track.md`

**外部资源**：
- [Vibe Researching 播客](https://a16z.com/podcast/)
- [claude-scientific-skills](https://github.com/K-Dense/claude-scientific-skills)
- [medical-imaging-review](https://github.com/luwill/research-skills)

---

## 十一、AI/ML 支持系统 (AI/ML Support System)

### 11.1 核心 Agent

#### Deep Learning Agent（深度学习专家）
**职责**：
- 模型架构设计（CNN, RNN, Transformer, GAN）
- 模型训练和超参数优化
- 模型评估和部署

**工具集成**：PyTorch, TensorFlow, Hugging Face Transformers

**详见**：`agents/ai/deep-learning.md`

#### Reinforcement Learning Agent（强化学习专家）
**职责**：
- 环境建模和策略设计
- 算法实现（DQN, PPO, SAC, MADDPG）
- 训练优化和性能评估

**工具集成**：Stable-Baselines3, RLlib, OpenAI Gym

**详见**：`agents/ai/reinforcement-learning.md`

#### Time Series Analysis Agent（时间序列分析专家）
**职责**：
- 时间序列预测（ARIMA, Prophet, LSTM）
- 异常检测和趋势分析
- 因果推断

**工具集成**：statsmodels, Prophet, PyTorch Forecasting

**详见**：`agents/ai/time-series-analysis.md`

#### Model Interpretability Agent（模型可解释性专家）
**职责**：
- 全局和局部可解释性（SHAP, LIME）
- 模型调试和公平性审计
- 可解释性报告生成

**工具集成**：SHAP, LIME, Captum, Fairlearn

**详见**：`agents/ai/model-interpretability.md`

### 11.2 开发支持 Agent

#### Automated Testing Agent（自动化测试专家）
**职责**：
- 测试策略设计和用例生成
- 测试执行和覆盖率分析

**工具集成**：pytest, Jest, coverage.py

**详见**：`agents/testing/automated-testing.md`

#### Code Reviewer Agent（代码审查专家 - 增强版）
**职责**：
- 代码质量审查
- 安全性审查（OWASP Top 10）
- 性能和可维护性审查

**详见**：`agents/code-reviewer.md`

#### Data Visualization Agent（数据可视化专家）
**职责**：
- 数据探索和图表设计
- 交互式可视化和报告生成

**工具集成**：matplotlib, plotly, seaborn

**详见**：`agents/visualization/data-visualization.md`

#### Security Audit Agent（安全审计专家）
**职责**：
- 代码安全审计（SQL 注入, XSS, CSRF）
- 依赖安全扫描
- 合规性验证（GDPR, HIPAA）

**工具集成**：Bandit, Snyk, TruffleHog

**详见**：`agents/security/security-audit.md`

### 11.3 使用场景

#### AI 研究
```bash
# 深度学习模型开发
/agents deep-learning "设计并训练一个图像分类模型"

# 强化学习实验
/agents reinforcement-learning "实现 PPO 算法解决 CartPole 问题"

# 模型可解释性分析
/agents model-interpretability "使用 SHAP 解释模型预测结果"
```

#### 数据分析
```bash
# 时间序列预测
/agents time-series-analysis "预测未来 30 天的销售额"

# 数据可视化
/agents data-visualization "生成实验结果对比图表"
```

#### 代码质量
```bash
# 自动化测试
/agents automated-testing "为新功能生成测试用例"

# 代码审查
/agents code-reviewer "审查最近的代码变更"

# 安全审计
/agents security-audit "扫描代码中的安全漏洞"
```

### 11.4 集成 claude-scientific-skills

**推荐集成**：
```bash
# 克隆仓库
git clone https://github.com/K-Dense-AI/claude-scientific-skills.git

# 集成 AI/ML 相关技能
cp -r claude-scientific-skills/scientific-skills/machine-learning/* \
  .claude/skills/ai/

# 集成数据分析技能
cp -r claude-scientific-skills/scientific-skills/data-analysis/* \
  .claude/skills/analysis/
```

**可用技能**（140+ 总计）：
- Machine Learning & AI
- Deep Learning
- Reinforcement Learning
- Time Series Analysis
- Model Interpretability
- Data Analysis & Visualization
- Python Packages（55+）：PyTorch, scikit-learn, etc.

### 11.5 最佳实践

#### AI/ML 开发
- 使用预训练模型加速开发
- 记录实验（MLflow, Weights & Biases）
- 使用版本控制管理模型
- 定期评估模型性能
- 关注模型可解释性和公平性

#### 代码质量
- 集成自动化测试到 CI/CD
- 定期进行代码审查
- 使用静态分析工具
- 监控测试覆盖率（目标 >80%）

#### 安全
- 定期进行安全审计
- 扫描依赖库漏洞
- 遵循 OWASP 最佳实践
- 不在代码中硬编码密钥

### 11.6 相关文档

**Agent 定义**：
- `agents/ai/deep-learning.md`
- `agents/ai/reinforcement-learning.md`
- `agents/ai/time-series-analysis.md`
- `agents/ai/model-interpretability.md`
- `agents/testing/automated-testing.md`
- `agents/visualization/data-visualization.md`
- `agents/security/security-audit.md`

**外部资源**：
- [claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills)
- [Agent Skills Marketplace](https://skillsmp.com/)
- [Awesome Agent Skills](https://github.com/heilcheng/awesome-agent-skills)


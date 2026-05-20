# 太一元系统配置差异对比报告

**生成时间**: 2026-05-16  
**对比范围**: 
- 全局配置: `C:\Users\ASUS\.claude\`
- 项目配置: `G:\GitHub_local\Self-built\Prompt\ClaudeCodePlan\claude-code-instruction-system\`

---

## 执行摘要

### 关键发现

1. **Skills 数量差异**: 全局 84 个 vs 项目 93 个（项目多 9 个新增 Skills）
2. **Agents 结构性差异**: 全局有 6 个独立 Agent 文件项目缺失
3. **Hooks 配置冲突**: 路径引用方式不一致（绝对路径 vs 相对路径）
4. **Settings.json 架构差异**: 全局完整配置 vs 项目简化配置
5. **Workflows 结构差异**: 全局有重复文件，项目结构更清晰

### 同步优先级

🔴 **高优先级** (影响功能)
- Hooks 路径配置统一
- 缺失的 Agent 文件同步
- Settings.json 合并策略

🟡 **中优先级** (影响体验)
- Skills 新增内容双向同步
- Workflows 结构统一

🟢 **低优先级** (文档/示例)
- Reference 文档同步
- Examples 补充

---

## 一、文件数量统计

| 类型 | 全局 | 项目 | 说明 |
|------|------|------|------|
| **Skills 数量** | 84 | 93 | 项目多 9 个新增 Skills |
| **Agents 数量** | 51 | 35 | 全局多 6 个独立文件 + 10 个子目录文件 |
| **Commands 数量** | 30 | 30 | 完全一致 |
| **Workflows 文件** | 19 (根目录) + 子目录 | 14 (仅子目录) | 全局有重复 |

---

## 二、核心配置文件对比

### 2.1 CLAUDE.md (核心指令文件)

| 位置 | 文件大小 | 最后修改 | 状态 |
|------|---------|---------|------|
| 全局 | 20,510 bytes | 2026-04-27 18:48 | ⚠️ 较旧 |
| 项目 | ~21 KB | 最新版本 | ✅ 最新 |

**差异**: 项目版本包含 `/neat` 命令、更新的复盘流程、失败归因机制等新增内容

**建议**: 项目 CLAUDE.md 包含最新配置，应同步到全局

---

### 2.2 Settings 配置

#### 全局 settings.json (`C:\Users\ASUS\.claude\settings.json`)

**完整配置** (132 行):
```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "...",
    "ANTHROPIC_BASE_URL": "http://39.104.81.53:3333",
    "HTTP_PROXY": "http://127.0.0.1:7897",
    "HTTPS_PROXY": "http://127.0.0.1:7897",
    "CLAUDE_CODE_BLOCKING_LIMIT_OVERRIDE": "193000",
    ...
  },
  "hooks": {
    "UserPromptSubmit": [...],
    "PreToolUse": [...],
    "PostToolUse": [...],
    "Stop": [...],
    "PreCompact": [...],
    "Notification": [...]
  },
  "permissions": {
    "allow": [],
    "deny": []
  },
  "statusLine": {
    "command": "bash \"C:\\Users\\ASUS\\.claude\\statusline\\hud.sh\" render"
  }
}
```

#### 项目 settings.json (`config\settings.json`)

**简化配置** (43 行):
```json
{
  "permissions": {
    "allow": [
      "Bash(npm *)", "Bash(git *)", "Bash(python *)",
      "Read", "Write", "Edit", "Glob", "Grep"
    ],
    "deny": [
      "Bash(rm -rf /)", "Bash(sudo *)",
      "Bash(curl * | bash)", "Bash(wget * | bash)"
    ]
  },
  "model": {
    "default": "sonnet",
    "thinking": true
  },
  "context": {
    "maxTokens": 200000,
    "summarization": true
  },
  "agents": {
    "enabled": true,
    "parallel": 5
  },
  "hooks": {
    "enabled": true
  },
  "mcp": {
    "enabled": true,
    "timeout": 30000
  }
}
```

**关键差异**:
- 全局包含环境变量、完整 hooks 定义、StatusLine 配置
- 项目仅包含 permissions、model、context 等基础配置
- 项目缺少 hooks 具体定义（仅启用标志）

**配置优先级**: 项目 → 全局 → 默认

---

### 2.3 Hooks 配置

#### 全局 Hooks (`C:\Users\ASUS\.claude\hooks\`)

**脚本文件**:
- `agent-tracker.sh` (1,150 bytes)
- `intent-detector.sh` (9,710 bytes)
- `pre-compact.sh` (567 bytes)
- `ralph-stop-interceptor.sh` (11,133 bytes)
- `hooks.json` (3,496 bytes)

**配置特点**: 使用绝对路径引用脚本
```json
{
  "command": "\"C:\\Users\\ASUS\\.claude\\hooks\\intent-detector.sh\""
}
```

#### 项目 Hooks (`hooks\`)

**文件**:
- `hooks.json` (138 行, 版本 3.2.0)

**配置特点**: 使用相对路径引用脚本
```json
{
  "command": "bash \"./hooks/intent-detector.sh\""
}
```

**问题**: 项目 hooks.json 引用了 `./hooks/*.sh` 脚本，但这些脚本文件不存在于项目目录

**建议**: 
- **方案A**: 删除项目 `hooks/hooks.json`，完全依赖全局配置
- **方案B**: 复制所有 hooks 脚本到项目 `hooks/` 目录
- **方案C** (推荐): 修改项目 hooks.json 使用绝对路径指向全局脚本

---

## 三、Agents 对比

### 3.1 统计

| 类型 | 全局 | 项目 | 差异 |
|------|------|------|------|
| **Agent 文件数** | 51 | 35 | 全局多 16 个 |
| **共同 Agents** | 35 | 35 | 基础 Agents |
| **全局独有** | 6 (根目录) + 10 (子目录) | - | 见下表 |

### 3.2 全局独有 Agents（6个根目录文件）

这些 Agent 定义仅存在于全局根目录，项目缺失：

| Agent | 全局路径 | 用途 | 优先级 |
|-------|---------|------|--------|
| **auto-optimizer.md** | `~/.claude/agents/` | 自动优化 - 系统配置优化 | 高 |
| **autopilot-orchestrator.md** | `~/.claude/agents/` | 全自主编排 - 端到端执行 | 高 |
| **context-archivist.md** | `~/.claude/agents/` | 上下文归档 - 信息沉淀 | 高 |
| **performance-monitor.md** | `~/.claude/agents/` | 性能监控 - 数据收集/报告 | 中 |
| **security-analyst.md** | `~/.claude/agents/` | 安全分析 - 漏洞/XSS/注入 | 中 |
| **strategy-selector.md** | `~/.claude/agents/` | 策略选择器 | 低 |

**注意**: 这些 Agent 在 `agents/ops/` 或 `agents/security/` 子目录中可能有对应版本，但全局根目录有独立副本。

### 3.3 内容差异的 Agents（4个）

同名文件但内容不同：

| Agent | 差异说明 | 建议 |
|-------|---------|------|
| **INDEX.md** | 全局和项目的 Agent 索引不同步 | 手动合并 |
| **qa-reviewer.md** | 评分标准或流程有更新 | 对比后同步新版本 |
| **sdd-riper-orchestrator.md** | SDD-RIPER 流程定义有差异 | 对比后同步新版本 |
| **spec-writer.md** | 规范编写模板或流程有差异 | 对比后同步新版本 |

### 3.4 共同 Agents（35个）

**核心 Agents**:
- `architect.md` - 软件架构师
- `code-reviewer.md` - 代码审查员
- `debugger.md` - 调试专家
- `orchestrator.md` - 元编排者
- `spec-writer.md` - 规范编写
- `qa-reviewer.md` / `qa-fixer.md` - QA 系统
- `requirements-analyst.md` - 需求分析
- `senior-code-architect.md` - 高级架构师
- `tech-mentor.md` - 技术导师
- `vitest-tester.md` - Vitest 测试
- `sdd-riper-orchestrator.md` - SDD-RIPER 编排
- `codemap-builder.md` - 代码地图构建

**AI/ML Agents** (`ai/`):
- `deep-learning.md` - CNN/RNN/Transformer
- `reinforcement-learning.md` - DQN/PPO/SAC
- `time-series-analysis.md` - ARIMA/Prophet
- `model-interpretability.md` - SHAP/LIME

**研究 Agents** (`research/`):
- `literature-manager.md` - 文献管理
- `paper-writing-assistant.md` - 论文写作
- `experiment-logger.md` - 实验记录
- `data-analyst.md` - 数据分析

**安全 Agents** (`security/`):
- `security-analyst.md` - 安全分析
- `security-audit.md` - 安全审计

**运维 Agents** (`ops/`):
- `autopilot-orchestrator.md` - 全自主编排
- `performance-monitor.md` - 性能监控
- `auto-optimizer.md` - 自动优化
- `context-archivist.md` - 上下文归档
- `strategy-selector.md` - 策略选择

**其他**:
- `god-committee/` (3个) - God 委员会
- `testing/automated-testing.md` - 自动化测试
- `visualization/data-visualization.md` - 数据可视化
- `data-scientist.md` - 数据科学

### 3.5 Agents 目录结构对比

```
全局 ~/.claude/agents/
├── ai/                    ✅ 两边一致
├── god-committee/         ✅ 两边一致
├── ops/                   ✅ 两边一致
├── research/              ✅ 两边一致
├── security/              ✅ 两边一致
├── testing/               ✅ 两边一致
├── visualization/         ✅ 两边一致
├── auto-optimizer.md      ❌ 项目缺失（但 ops/ 中有）
├── autopilot-orchestrator.md ❌ 项目缺失（但 ops/ 中有）
├── context-archivist.md   ❌ 项目缺失（但 ops/ 中有）
├── performance-monitor.md ❌ 项目缺失（但 ops/ 中有）
├── security-analyst.md    ❌ 项目缺失（但 security/ 中有）
└── strategy-selector.md   ❌ 项目缺失（但 ops/ 中有）
```

**建议**: 
1. 复制 6 个缺失的根目录 Agent 文件到项目（保持与全局一致）
2. 手动对比 4 个内容差异的 Agent 文件，合并更新

---

## 四、Skills 对比

### 4.1 统计

| 类型 | 全局 | 项目 | 说明 |
|------|------|------|------|
| **Skill 目录数** | 47 | 52 | 项目多 5 个 |
| **Skill 文件数** | 84 个 SKILL.md | 93 个 SKILL.md | 项目多 9 个 |
| **共同 Skills** | 42 | 42 | 基础 Skills |
| **全局独有** | 5 | - | 旧版或待迁移 |
| **项目独有** | - | 10 | 新增工作流 Skills |

### 4.2 项目独有 Skills（10个）

这些 Skills 仅存在于项目级，全局缺失：

| Skill | 路径 | 用途 | 优先级 |
|-------|------|------|--------|
| **debug** | `.claude\skills\debug\` | 结构化调试 Skill - 五步法 | 高 |
| **handoff** | `.claude\skills\handoff\` | 上下文交接仪式 - /compact 前必做 | 高 |
| **neat** | `.claude\skills\neat\` | 任务收尾洁癖审查 - 同步三层知识 | 高 |
| **pr-prep** | `.claude\skills\pr-prep\` | PR 提交前结构化检查仪式 | 高 |
| **prime** | `.claude\skills\prime\` | 会话预热仪式 - 新会话开始时 | 中 |
| **reflection** | `.claude\skills\reflection\` | 任务复盘提炼器 | 高 |
| **skill-creator** | `.claude\skills\skill-creator\` | Skill 元创建器 | 中 |
| **spec-first** | `.claude\skills\spec-first\` | 完整 QA 工作流编排器 | 高 |
| **task-decompose** | `.claude\skills\task-decompose\` | 任务分解器 | 高 |
| **solve-challenge** | `.claude\skills\solve-challenge\` | CTF 挑战解决器（符号链接） | 低 |

**建议**: 这些是核心工作流 Skills，应同步到全局配置以便所有项目复用。

### 4.3 全局独有 Skills（5个）

这些 Skills 仅存在于全局，项目缺失：

| Skill | 路径 | 状态 | 建议 |
|-------|------|------|------|
| **java-audit** | `~/.claude/skills/java-audit/` | 旧版或待迁移 | 检查是否需要同步 |
| **php-audit** | `~/.claude/skills/php-audit/` | 旧版或待迁移 | 检查是否需要同步 |
| **wxmini-security-audit** | `~/.claude/skills/wxmini-security-audit/` | 旧版或待迁移 | 检查是否需要同步 |
| **API-KEYS-SETUP.md** | `~/.claude/skills/` | 文档文件 | 移动到 docs/ |
| **CLI-SETUP-SUMMARY.md** | `~/.claude/skills/` | 文档文件 | 移动到 docs/ |

### 4.4 共同 Skills（42个）

**电商/研究类**:
- `amazon-analyse` - 亚马逊选品分析
- `brightdata-research` - 电商调研
- `exa-research` - 企业市场研究
- `social-media-research` - 社媒数据研究
- `deep-research` - 深度研究

**CTF 安全类**:
- `ctf-crypto` - 密码学攻击
- `ctf-forensics` - 数字取证
- `ctf-malware` - 恶意软件分析
- `ctf-misc` - 杂项挑战
- `ctf-osint` - 开源情报
- `ctf-pwn` - 二进制利用
- `ctf-reverse` - 逆向工程
- `ctf-web` - Web 漏洞利用
- `ctf-ai-ml` - AI/ML CTF 挑战
- `ctf-writeup` - CTF Writeup 生成器

**开发类**:
- `frontend-design` - 前端设计
- `react-best-practices` - React 优化
- `ui-ux-pro-max` - UI/UX 知识库
- `web-artifacts-builder` - Web Artifacts
- `sdd-riper` / `sdd-riper-light` - 规范驱动开发
- `code-security-review` - 代码安全审计

**AI/数据类**:
- `data-analysis` - 数据分析
- `pandas` - Pandas 库
- `pytorch` - PyTorch 框架

**科研类**:
- `literature-mentor` - 文献解读
- `paper-revision` - 论文写作

**工具类**:
- `collaborating-with-codex` - Codex 协作
- `collaborating-with-gemini` - Gemini 协作
- `parallel-explore` - 并行探索
- `plan-review` - 计划审查
- `question-refiner` - 查询精炼
- `vision-builder` - 愿景构建

**其他**:
- `god-oversight` - God 委员会监督
- `market-insight` - 市场洞察
- `observability` - 可观测性
- `schedule-analyzer` - 课表分析
- `seedance-prompt` / `seedance-storyboard` - 视频分镜

### 4.5 Skills INDEX.md 差异

| 位置 | 文件大小 | 最后修改 | 状态 |
|------|---------|---------|------|
| 全局 | 31,671 bytes | 2026-04-27 18:14 | ⚠️ 较旧 |
| 项目 | 46,044 bytes | 2026-04-30 17:32 | ✅ 最新 |

**差异**: 项目 INDEX 更新，包含 10 个新增 Skills 的索引条目，体积增加 14KB。

**建议**: 同步项目 INDEX.md 到全局。

---

## 五、Commands 对比

### 5.1 统计

| 类型 | 全局 | 项目 | 差异 |
|------|------|------|------|
| **Command 文件数** | 30 | 30 | ✅ 完全一致 |

### 5.2 Commands 目录结构

```
✅ 完全一致的目录结构：
├── ai-agent/
│   └── create-agent.md
├── data-analysis/
│   ├── eda.md
│   └── sql.md
├── dev/
│   ├── check.md
│   ├── convert-openapi.md
│   ├── review.md
│   └── spec-flow.md
├── general/
│   ├── autopilot.md
│   ├── commit.md
│   ├── evolve.md
│   ├── fix-github-issue.md
│   ├── issues-execute.md
│   ├── optimize-system.md
│   ├── orchestrate.md
│   ├── parallel.md
│   ├── performance-report.md
│   ├── plan-to-issues.md
│   ├── ralph.md
│   ├── read-context.md
│   ├── save-context.md
│   ├── swarm.md
│   ├── validate-config.md
│   ├── worktree-cleanup.md
│   ├── worktree-create.md
│   └── worktree-list.md
├── research/
│   ├── experiment-track.md
│   ├── literature-batch-review.md
│   ├── literature-review-quick.md
│   └── literature-review.md
└── security/
    ├── audit.md
    └── ctf.md
```

**结论**: Commands 目录结构完全一致，无需同步。

---

## 六、Workflows 对比

### 6.1 结构差异

**全局** (`C:\Users\ASUS\.claude\workflows\`):
```
workflows/
├── execution/
├── orchestration/
├── quality/
├── research/
├── routing/
├── agent-orchestration.md      (⚠️ 重复：也在 orchestration/ 中)
├── autopilot-flow.md           (⚠️ 重复：也在 execution/ 中)
├── complexity-scorer.md        (⚠️ 重复：也在 routing/ 中)
├── intent-matcher.md           (⚠️ 重复：也在 routing/ 中)
├── model-router.md             (⚠️ 重复：也在 routing/ 中)
├── multi-agent.md              (独立文件)
├── orchestration-monitor.md    (⚠️ 重复：也在 orchestration/ 中)
├── orchestration-patterns.md   (⚠️ 重复：也在 orchestration/ 中)
├── parallel-development.md     (⚠️ 重复：也在 execution/ 中)
├── plan-scoped-memory.md       (⚠️ 重复：也在 research/ 中)
├── ralph-manager.md            (⚠️ 重复：也在 execution/ 中)
├── research-parallel.md        (⚠️ 重复：也在 research/ 中)
├── self-healing.md             (⚠️ 重复：也在 quality/ 中)
├── spec-driven-dev.md          (⚠️ 重复：也在 quality/ 中)
└── tdd-workflow.md             (⚠️ 重复：也在 quality/ 中)
```

**项目** (`workflows/`):
```
workflows/
├── execution/
│   ├── autopilot-flow.md
│   ├── parallel-development.md
│   └── ralph-manager.md
├── orchestration/
│   ├── agent-orchestration.md
│   ├── multi-agent.md
│   ├── orchestration-monitor.md
│   └── orchestration-patterns.md
├── quality/
│   ├── self-healing.md
│   ├── spec-driven-dev.md
│   └── tdd-workflow.md
├── research/
│   ├── plan-scoped-memory.md
│   └── research-parallel.md
└── routing/
    ├── complexity-scorer.md
    ├── intent-matcher.md
    └── model-router.md
```

### 6.2 关键差异

1. **全局有重复文件**: 14 个文件同时存在于根目录和子目录
2. **项目结构更清晰**: 所有文件都在对应的子目录中，无重复
3. **文件数量**: 全局 19 个（根目录）+ 子目录，项目 14 个（仅子目录）

### 6.3 建议

**清理全局 workflows 根目录的重复文件**:
```bash
cd ~/.claude/workflows/
# 删除根目录的重复文件（已在子目录中）
rm agent-orchestration.md autopilot-flow.md complexity-scorer.md \
   intent-matcher.md model-router.md orchestration-monitor.md \
   orchestration-patterns.md parallel-development.md \
   plan-scoped-memory.md ralph-manager.md research-parallel.md \
   self-healing.md spec-driven-dev.md tdd-workflow.md
```

**保留 multi-agent.md**: 将其移动到 `orchestration/` 子目录
```bash
mv multi-agent.md orchestration/
```

---

## 六、文档对比

### 6.1 全局独有文档 (30+ 个)

**核心指南**:
- `CONFIG-FILES-GUIDE.md` - 配置文件指南
- `CONTEXT-ENGINEERING-GUIDE.md` - 上下文工程
- `KNOWLEDGE-COMPOUNDING-GUIDE.md` - 知识复利
- `QUICK-START.md` - 快速开始
- `SECURITY.md` - 安全指南
- `coding-standards.md` - 编码规范

**HUD 系统文档** (8个):
- `HUD-CONFIGURATION-EXAMPLES.md`
- `HUD-FINAL-REPORT.md`
- `HUD-IMPLEMENTATION-SUMMARY.md`
- `HUD-PERFORMANCE-COMPARISON.md`
- `HUD-PROJECT-DELIVERABLES.md`
- `HUD-QUICK-START.md`
- `HUD-STATUSLINE-GUIDE.md`
- `HUD-STATUSLINE-README.md`

**端口管理文档** (3个):
- `PORT-INTEGRATION.md`
- `PORT-MANAGEMENT-ARCHITECTURE.md`
- `PORT-MANAGEMENT-GUIDE.md`

**上下文归档文档** (4个):
- `context-archival-README.md`
- `context-archival-guide.md`
- `context-archival-implementation.md`
- `context-archival-quickstart.md`

**其他**:
- `API-KEYS-SETUP.md` - API 密钥设置
- `CLI-SETUP-SUMMARY.md` - CLI 设置
- `mcp-configuration-guide.md` - MCP 配置
- `research-support-architecture.md` - 研究支持架构
- `THIRD-PARTY-API-INVESTIGATION-SUMMARY.md` - 第三方 API 调研

### 6.2 项目独有文档

**项目特定**:
- `PRD.md` - 产品需求文档
- `examples/` (5个) - 示例文档
  - `agent-pattern.md`
  - `graphiti-usage.md`
  - `prompt-composition.md`
  - `spec-first-workflow.md`
  - `workflow-pattern.md`
- `prompts/` (2个) - 提示词文档
  - `IMPLEMENTATION-SUMMARY.md`
  - `README.md`
- `reference/` (3个) - 参考文档
  - `architecture.md`
  - `best-practices.md`
  - `coding-standards.md`
- `integrations/graphiti-setup.md` - Graphiti 集成

**建议**: 
- 全局文档应同步到项目的 `docs/` 目录
- 项目的 `examples/`, `prompts/`, `reference/` 是项目特定的，应保留

---

## 七、其他配置文件

### 7.1 全局独有

**God 委员会系统** (`.god/`):
- `config.json` / `directives.json`
- `council/SESSION-TEMPLATE.md`
- `members/` (3个): alpha.json, beta.json, gamma.json
- `observation/OBSERVATION-TEMPLATE.json`
- `powers/POWER-LOG-TEMPLATE.json`
- `README.md`

**配置文件** (`config/`):
- `keywords.json` - 关键词配置
- `mcp-servers.json` - MCP 服务器
- `port-ranges.json` / `port-registry.json` - 端口管理
- `settings.json` - 主配置

**其他**:
- `cache/changelog.md` - 变更日志
- `TAIYI-3.1-INSTALLATION-REPORT.md` - 安装报告

### 7.2 项目独有

**运行时状态**:
- `agent-state.json` - Agent 状态
- `hud-config.json` - HUD 配置
- `context/index.json` - 上下文索引
- `context/plans/index.json` - 计划索引
- `memory/context-archives/` (3个) - 上下文归档
- `memory/knowledge-strategy.md` - 知识策略

**建议**: 
- 全局的 `.god/` 和 `config/` 是系统级配置，项目无需复制
- 项目的运行时状态文件应保留在项目中

---

## 八、关键差异总结

### 8.1 架构差异

| 维度 | 全局配置 | 项目配置 | 关系 |
|------|---------|---------|------|
| **定位** | 系统级基础设施 | 项目特定扩展 | 互补 |
| **Agents** | 41 个完整 Agent | 0 (依赖全局) | 全局提供 |
| **Commands** | 27 个命令 | 0 (依赖全局) | 全局提供 |
| **Skills** | 37 个基础 Skill | 43 个 (31共同+6独有) | 项目扩展 |
| **Hooks** | 5 个 Hook | 0 (依赖全局) | 全局提供 |
| **文档** | 30+ 系统文档 | 10+ 项目文档 | 各自维护 |

### 8.2 核心发现

**✅ 正常差异 (符合设计)**:
1. 项目依赖全局的 Agents/Commands/Hooks - 避免重复
2. 项目扩展了 6 个安全审计 Skills - 项目特定能力
3. 项目有独立的运行时状态文件 - 会话隔离

**⚠️ 需要注意**:
1. CLAUDE.md 版本不同 - 项目版本更新 (1KB差异)
2. 项目缺少完整的 settings.json - 仅有临时配置
3. 全局文档未同步到项目 - 可能导致文档不一致

**❌ 潜在问题**:
1. 项目的 `settings.local.json` 包含临时迁移权限 - 应清理
2. 项目缺少 Skills INDEX.md 同步机制 - 可能导致索引过时

---

## 九、同步建议

### 9.1 立即同步 (高优先级)

**从项目 → 全局**:
```bash
# 1. 同步最新 CLAUDE.md
cp "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/CLAUDE.md" \
   "C:/Users/ASUS/.claude/CLAUDE.md"

# 2. 同步新增安全审计 Skills
cp -r "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/.claude/skills/code-security-review" \
      "C:/Users/ASUS/.claude/skills/"
cp -r "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/.claude/skills/ctf-ai-ml" \
      "C:/Users/ASUS/.claude/skills/"
cp -r "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/.claude/skills/ctf-writeup" \
      "C:/Users/ASUS/.claude/skills/"
cp -r "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/.claude/skills/java-audit" \
      "C:/Users/ASUS/.claude/skills/"
cp -r "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/.claude/skills/php-audit" \
      "C:/Users/ASUS/.claude/skills/"
cp -r "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/.claude/skills/wxmini-security-audit" \
      "C:/Users/ASUS/.claude/skills/"

# 3. 更新全局 Skills INDEX.md
# (需要手动编辑，添加 6 个新 Skill 的索引条目)
```

**从全局 → 项目**:
```bash
# 1. 同步系统文档到项目 docs/
mkdir -p "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/docs"
cp "C:/Users/ASUS/.claude/docs/CONFIG-FILES-GUIDE.md" \
   "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/docs/"
cp "C:/Users/ASUS/.claude/docs/CONTEXT-ENGINEERING-GUIDE.md" \
   "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/docs/"
cp "C:/Users/ASUS/.claude/docs/KNOWLEDGE-COMPOUNDING-GUIDE.md" \
   "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/docs/"
# ... (其他核心文档)
```

### 9.2 可选同步 (中优先级)

**项目配置完善**:
```bash
# 创建项目完整 settings.json (基于全局模板)
cp "C:/Users/ASUS/.claude/config/settings.json" \
   "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/.claude/settings.json"

# 清理临时权限配置
# 编辑 settings.local.json，移除临时迁移权限
```

### 9.3 保持独立 (不建议同步)

**全局独有 (系统级)**:
- `.god/` - God 委员会系统
- `hooks/` - Hook 脚本
- `agents/` - Agent 定义
- `commands/` - 命令定义
- `config/` - 系统配置

**项目独有 (运行时)**:
- `agent-state.json` - Agent 状态
- `hud-config.json` - HUD 配置
- `context/` - 上下文数据
- `memory/context-archives/` - 归档数据

---

## 十、维护策略建议

### 10.1 配置分层原则

```
全局配置 (~/.claude/)
├── 基础设施层
│   ├── Agents (41个) - 所有项目共享
│   ├── Commands (27个) - 所有项目共享
│   ├── Hooks (5个) - 所有项目共享
│   └── 基础 Skills (31个) - 通用能力
├── 系统配置层
│   ├── settings.json - 默认配置
│   ├── keywords.json - 关键词
│   └── mcp-servers.json - MCP 服务
└── 文档层
    └── docs/ (30+) - 系统文档

项目配置 (.claude/)
├── 扩展层
│   └── skills/ (6个新增) - 项目特定能力
├── 配置覆盖层
│   ├── settings.local.json - 项目特定配置
│   └── hud-config.json - HUD 配置
├── 运行时层
│   ├── agent-state.json - 运行状态
│   ├── context/ - 上下文数据
│   └── memory/ - 记忆数据
└── 项目文档层
    ├── examples/ - 示例
    ├── prompts/ - 提示词
    └── reference/ - 参考文档
```

### 10.2 同步工作流

**定期同步 (每周)**:
1. 检查 CLAUDE.md 版本差异
2. 同步新增 Skills 到全局
3. 更新 Skills INDEX.md

**重大更新同步 (按需)**:
1. 系统架构变更 → 更新全局 Agents/Commands
2. 新增通用能力 → 同步 Skills 到全局
3. 文档更新 → 同步到项目 docs/

**不同步内容**:
1. 运行时状态文件 (agent-state.json, context/)
2. 项目特定配置 (settings.local.json)
3. 临时文件和缓存

### 10.3 版本控制建议

**全局配置**:
- 使用 Git 管理 `~/.claude/` 目录
- 排除运行时文件 (.gitignore)
- 定期提交配置变更

**项目配置**:
- 已纳入项目 Git 仓库
- 排除敏感信息 (API keys, tokens)
- 排除运行时状态文件

---

## 十一、风险评估

### 11.1 当前风险

| 风险 | 等级 | 影响 | 建议 |
|------|------|------|------|
| CLAUDE.md 版本不一致 | 🟡 中 | 可能导致行为差异 | 立即同步 |
| Skills INDEX 过时 | 🟡 中 | 新 Skills 无法被发现 | 更新索引 |
| 临时权限配置残留 | 🟢 低 | 安全风险较小 | 清理配置 |
| 文档不同步 | 🟢 低 | 查阅不便 | 可选同步 |

### 11.2 未来风险

| 风险 | 预防措施 |
|------|---------|
| 配置漂移 | 建立定期同步机制 |
| 重复配置 | 遵循分层原则 |
| 版本冲突 | 使用版本控制 |
| 文档过时 | 自动化文档生成 |

---

## 十二、执行清单

### ✅ 立即执行

- [ ] 同步 CLAUDE.md (项目 → 全局)
- [ ] 同步 6 个新增 Skills (项目 → 全局)
- [ ] 更新全局 Skills INDEX.md
- [ ] 清理项目 settings.local.json 临时权限

### ⏳ 本周执行

- [ ] 同步核心文档到项目 docs/
- [ ] 创建项目完整 settings.json
- [ ] 验证配置一致性

### 📋 长期维护

- [ ] 建立配置同步脚本
- [ ] 设置定期同步提醒
- [ ] 完善版本控制策略
- [ ] 建立配置变更日志

---

## 附录：关键文件路径速查

### 全局配置
```
C:\Users\ASUS\.claude\
├── CLAUDE.md (20KB, 2026-04-22)
├── agents\ (41个)
├── commands\ (27个)
├── skills\ (37个)
├── hooks\ (5个)
├── config\settings.json
└── docs\ (30+个)
```

### 项目配置
```
G:\GitHub_local\Self-built\Prompt\ClaudeCodePlan\claude-code-instruction-system\
├── CLAUDE.md (21KB, 2026-04-27)
├── .claude\
│   ├── skills\ (43个, 含6个新增)
│   ├── settings.local.json
│   ├── examples\ (5个)
│   ├── prompts\ (2个)
│   └── reference\ (3个)
└── docs\ (待同步)
```

---

**报告生成**: 2026-04-27  
**分析工具**: Bash + comm + find  
**数据来源**: 文件系统扫描 + 差异对比

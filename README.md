# 太一元系统 · Claude Code 指令体系

> 版本: 1.0 Taiyi (太一) — 道之演化 | 发布日期: 2026-03-01

太一元系统是一套完善的 Claude Code CLI 配置与指令体系，覆盖软件开发、AI/ML 科研、数据分析、网络安全等专业领域。系统具备自进化、Agent 编排、并行科研、全自主执行等核心能力。

---

## 核心特性

| 特性 | 说明 |
|------|------|
| **Agent 自动调度** | 27 种意图 → 22 个专家 Agent 自动路由 |
| **Ralph Loop** | 自主循环执行直到任务完成 |
| **Autopilot** | 5 阶段端到端全自主执行（Planning→Delivery） |
| **HUD Statusline** | 实时状态可视化（模型/Agent/进度/费用） |
| **Spec-First QA** | 规范驱动开发 + 自愈质量循环 |
| **Research Parallel** | 多 Agent 并行科研工作流（3-10x 加速） |
| **Port Management** | 跨项目端口冲突自动检测与管理 |
| **多层记忆系统** | 上下文归档 + 文件记忆 + 知识图谱协同 |

---

## 目录结构

```
claude-code-instruction-system/
├── CLAUDE.md                    # 核心配置
├── QUICK-REFERENCE.md           # 快速参考手册
├── CHANGELOG.md                 # 更新记录
├── CONTRIBUTING.md              # 贡献指南
│
├── docs/                        # 参考文档
│   ├── FEATURES.md              # 系统特性详细说明
│   ├── QUICK-START.md           # 快速开始指南
│   ├── CONFIG-FILES-GUIDE.md    # 配置文件完整指南
│   ├── ORCHESTRATION-GUIDE.md   # 编排系统使用指南
│   ├── SKILLS-CATALOG.md        # Skills 完整目录
│   ├── MEMORY-SYSTEM.md         # 记忆系统架构
│   ├── hud/                     # HUD/Statusline 文档（10个）
│   ├── port-management/         # 端口管理文档（3个）
│   ├── context-archival/        # 上下文归档文档（5个）
│   ├── research/                # 科研支持文档（3个）
│   ├── reports/                 # 历史实现报告
│   └── releases/                # 发版记录
│
├── agents/                      # 专家 Agent 定义
│   ├── INDEX.md                 # Agent 索引（渐进式披露）
│   ├── orchestrator.md          # 元编排者
│   ├── architect.md             # 软件架构师
│   ├── debugger.md              # 调试专家
│   ├── code-reviewer.md         # 代码审查员
│   ├── spec-writer.md / qa-reviewer.md / qa-fixer.md
│   ├── ops/                     # 运维 Agent（auto-optimizer 等 5个）
│   ├── ai/                      # AI/ML 专家 Agent
│   ├── research/                # 科研 Agent
│   ├── testing/                 # 测试 Agent
│   ├── security/                # 安全 Agent
│   └── visualization/           # 可视化 Agent
│
├── workflows/                   # 工作流模式文档
│   ├── orchestration/           # 编排模式（4个）
│   ├── execution/               # 执行流程（ralph, autopilot 等 3个）
│   ├── quality/                 # 质量保障（self-healing 等 3个）
│   ├── routing/                 # 路由选择（model-router 等 3个）
│   └── research/                # 科研并行工作流（2个）
│
├── commands/                    # 自定义 Slash 命令
│   ├── general/                 # 通用命令（ralph, autopilot 等）
│   ├── dev/                     # 开发命令
│   ├── research/                # 科研命令
│   ├── security/                # 安全命令
│   ├── ai-agent/                # AI Agent 命令
│   └── data-analysis/           # 数据分析命令
│
├── scripts/                     # 工具脚本
│   ├── test-integrations.sh     # 集成测试入口
│   ├── validate/                # 配置验证与诊断（7个）
│   ├── context/                 # 上下文管理脚本（4个）
│   ├── hooks/                   # 生命周期钩子脚本（3个）
│   ├── utils/                   # 通用工具（7个）
│   └── port-management/         # 端口管理脚本
│
├── .claude/                     # Claude Code 项目配置
│   ├── settings.json            # 项目级设置
│   ├── statusline/              # HUD 状态栏脚本
│   ├── skills/                  # Skills 知识包
│   └── context/                 # 上下文归档
│
├── hooks/                       # 全局钩子配置
│   ├── hooks.json               # 钩子入口配置
│   ├── intent-detector.sh       # 意图识别（27种意图）
│   └── ralph-stop-interceptor.sh
│
├── config/                      # 系统配置文件
│   ├── keywords.json            # 意图关键词索引
│   ├── mcp-servers.json         # MCP 服务器配置
│   ├── port-registry.json       # 端口注册表
│   └── port-ranges.json         # 端口范围规则
│
├── memory/                      # 记忆/知识库
├── specs/                       # 功能规范文件
├── examples/                    # 使用示例
├── templates/                   # CLAUDE.md 模板
├── tools/                       # 扩展工具（Rust HUD/TUI 等）
└── themes/                      # 主题配置
```

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/dctx479/claude-code-instruction-system.git
cd claude-code-instruction-system
```

### 2. 全局配置（`~/.claude/settings.json`）

```json
{
  "model": "claude-sonnet-4-6",
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your-api-key",
    "ANTHROPIC_BASE_URL": "https://api.anthropic.com/",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0",
    "DISABLE_INSTALLATION_CHECKS": "1"
  },
  "statusLine": {
    "type": "command",
    "command": "bash \"~/.claude/statusline/hud.sh\" render"
  },
  "permissions": {
    "defaultMode": "default"
  }
}
```

### 3. 安装自定义命令和 Agent

```bash
# 复制到全局目录（所有项目可用）
cp -r commands/* ~/.claude/commands/
cp -r agents/* ~/.claude/agents/
```

### 4. 验证安装

```bash
bash scripts/test-integrations.sh
# 预期: 总测试数 24，通过 24 ✅
```

详细安装说明见 [docs/QUICK-START.md](docs/QUICK-START.md)。

---

## 核心用法

### Agent 自动调度

系统在每次用户输入时自动识别意图，加载对应 Agent 角色：

```
用户输入 → intent-detector.sh → intent-state.json → 加载 agents/{agent}.md
```

也可手动指定：
```
@architect 帮我设计系统架构
@debugger 这个报错怎么回事
@orchestrator 编排这个复杂任务
```

### 自主执行

```bash
/ralph "完成所有待办事项"          # 自主循环执行
/autopilot "开发用户认证系统"      # 5阶段全自主
/autopilot supervised "重构支付模块" # 阶段审核模式
```

### 编排模式

```bash
/orchestrate    # 智能编排（自动选择策略）
/parallel       # 强制并行
/swarm          # 大规模群体执行
```

### 科研工作流

```bash
/literature-review "注意力机制" --parallel --workers 5
/experiment-track create --name "ResNet消融实验"
```

---

## 配置优先级

```
项目级 .claude/settings.json（最高）
    ↓
全局级 ~/.claude/settings.json
    ↓
默认配置
```

**注意**：
- 手动编辑 `~/.claude/settings.json`（全局设置）
- 不要手动编辑 `~/.claude.json`（运行时数据，自动管理）

Windows 用户配置详见 [docs/CONFIG-FILES-GUIDE.md](docs/CONFIG-FILES-GUIDE.md)。

---

## 文档索引

| 文档 | 内容 |
|------|------|
| [CLAUDE.md](CLAUDE.md) | 核心配置与执行指令 |
| [QUICK-REFERENCE.md](QUICK-REFERENCE.md) | 常用命令速查 |
| [docs/FEATURES.md](docs/FEATURES.md) | 系统特性详情 |
| [docs/QUICK-START.md](docs/QUICK-START.md) | 新手入门指南 |
| [docs/CONFIG-FILES-GUIDE.md](docs/CONFIG-FILES-GUIDE.md) | 配置文件完整说明 |
| [docs/ORCHESTRATION-GUIDE.md](docs/ORCHESTRATION-GUIDE.md) | 编排系统与策略 |
| [docs/SKILLS-CATALOG.md](docs/SKILLS-CATALOG.md) | 140+ Skills 目录 |
| [docs/MEMORY-SYSTEM.md](docs/MEMORY-SYSTEM.md) | 多层记忆架构 |
| [docs/hud/HUD-STATUSLINE-GUIDE.md](docs/hud/HUD-STATUSLINE-GUIDE.md) | HUD 状态栏配置 |
| [agents/INDEX.md](agents/INDEX.md) | 所有 Agent 索引 |

---

## 参考资源

- [Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code)
- [Claude Code 最佳实践](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Awesome Claude Code](https://github.com/hesreallyhim/awesome-claude-code)
- [claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills)（140+ 科研技能）

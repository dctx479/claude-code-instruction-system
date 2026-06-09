# 外部工具生态指南 (Tools Ecosystem Guide)

> 本文档是 Claude Code 外部工具生态的**单一事实源**。所有工具的安装、使用、组合策略和主动推荐规则均在此定义。
> 其他文档通过指针引用本文件，不重复安装命令。
>
> 设计原则：**检测场景 → 主动推荐 → 用户许可 → 自主安装 → 验证结果**

---

## 工具总览

| 工具 | 类别 | 核心价值 | 安装复杂度 | 主动推荐触发场景 |
|------|------|---------|-----------|----------------|
| **Context Mode** | Token 优化 | MCP 输出压缩，~98% 节省 | ⭐ 一条命令 | token 消耗 >100K 且未安装 |
| **CodeGraph** | Token 优化 | 代码知识图谱，~92% tool call 减少 | ⭐⭐ per-project init | 代码探索 >20 次 Read/Grep 且未安装 |
| **RTK** | Token 优化 | 额外上下文压缩层 | ⭐ 一条命令 | 配合 Context Mode 使用 |
| **claude-tap** | 可观测性 | API 流量检查 + token 用量分析 | ⭐ 一条命令 | 用户询问 token 成本/API 细节 |
| **Knowledge Work Plugins** | 插件生态 | Anthropic 官方 20+ 职业角色 | ⭐ 一条命令 | 用户需要特定职业角色辅助 |
| **Flue Framework** | Agent 框架 | 轻量 TS Agent 脚手架 + SSE | ⭐⭐ 项目初始化 | 用户构建 TypeScript Agent |
| **SSH Skill** | 基础设施 | 企业 SSH 长连接 + 大文件传输 | ⭐ 一条命令 | 用户需要连接多台服务器 |
| **System Cleaner** | 运维工具 | 桌面清理 + 安全分级 + HTML 报告 | ⭐ 一条命令 | 用户想清理磁盘/查找大文件 |

---

## 一、Token 优化工具

> 三个工具各司其职互不冲突：Context Mode 压缩 MCP 工具输出，CodeGraph 加速代码理解，RTK 处理剩余通用压缩。

### 1.1 Context Mode

**项目**: [mksglu/claude-context-mode](https://github.com/mksglu/claude-context-mode)

**原理**: 在 Claude Code 和工具输出之间添加中间层。每个工具调用在独立子进程沙箱中运行，原始输出留在沙箱内，使用 SQLite FTS5 虚拟表配合 BM25 排名算法建立索引，仅将精准匹配的内容返回给模型。

**实测数据**:
| 场景 | 原始大小 | 压缩后 | 节省 |
|------|---------|--------|------|
| Playwright 快照 | 56KB | 299B | 99.5% |
| 20 个 GitHub Issues | 59KB | 1.1KB | 98.1% |
| 500 次访问日志 | 45KB | 155B | 99.7% |
| 500 行 CSV 分析 | 85KB | 222B | 99.7% |
| 完整会话（综合） | 315KB | 5.4KB | **98.3%** |

#### 安装

**方法 A — Plugin 安装（推荐，含自动路由钩子和斜杠命令）**:
```bash
claude plugin marketplace add mksglu/claude-context-mode
claude plugin install context-mode@claude-context-mode
```

**方法 B — 仅 MCP 服务器**:
```bash
claude mcp add context-mode -- npx -y context-mode
```

#### 验证安装
```bash
claude mcp list  # 应显示 context-mode
```

#### 工作机制

安装后系统通过 PreToolUse 钩子自动路由工具输出，用户无需改变工作流程。支持 JavaScript、Python、Shell 等 10 种语言运行时。

---

### 1.2 CodeGraph

**项目**: [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) (15K+ Stars)

**原理**: 使用 tree-sitter 解析整个代码库，把所有函数、类、方法之间的调用/继承/导入关系存进本地 SQLite 数据库。Claude Code 需要理解代码结构时，直接查图谱而非反复扫描文件。

**实测数据** (Claude Opus 4.6 + Claude Code v2.1.91):
| 代码库 | 使用 CodeGraph | 不使用 | 效果 |
|--------|---------------|--------|------|
| VS Code（TypeScript） | 3 次调用，17 秒 | 52 次调用，1 分 37 秒 | 减少 94%，快 82% |
| Excalidraw（TypeScript） | 3 次调用，29 秒 | 47 次调用，1 分 45 秒 | 减少 94%，快 72% |
| Swift Compiler（C++） | 6 次调用，35 秒 | 37 次调用，2 分 8 秒 | 减少 84%，快 73% |
| **综合平均** | — | — | **减少 92% 调用，快 71%** |

#### 安装

```bash
npx @colbymchenry/codegraph
```

运行后自动完成：安装全局包 → 配置 MCP 服务器到 `~/.claude.json` → 设置权限白名单 → 写入全局指令。

#### 项目初始化（每个项目执行一次）

```bash
cd your-project
codegraph init -i
```

中小型项目初始化约 10-15 秒，之后增量索引，每次代码变更 2 秒内自动更新图谱。

#### 验证安装
```bash
codegraph --version
```

#### 提供的 MCP 工具

| MCP 工具 | 功能 |
|----------|------|
| `codegraph_search` | 按名称搜索函数、类、变量 |
| `codegraph_callers` | 查"谁调用了这个函数" |
| `codegraph_callees` | 查"调用了哪些函数" |
| `codegraph_impact` | 修改的影响范围 |
| `codegraph_context` | 为某个任务构建完整上下文 |
| `codegraph_files` | 获取项目文件结构（比 FS 扫描快） |

---

### 1.3 RTK

**项目**: [rtk-ai/rtk](https://github.com/rtk-ai/rtk)

**原理**: Rust 编写的 CLI 代理，拦截 AI 编码助手的 Shell 命令输出，通过 100+ 内置过滤器自动压缩，60-90% token 节省，<10ms 开销。与 Context Mode（压缩 MCP 工具输出）和 CodeGraph（压缩代码探索）互补，处理 Bash 等剩余工具的输出。

#### 安装

**方法 A — Homebrew（macOS/Linux 推荐）**:
```bash
brew install rtk
```

**方法 B — Shell 脚本（Linux/macOS）**:
```bash
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh
```

**方法 C — Windows 预编译二进制**:
从 [GitHub Releases](https://github.com/rtk-ai/rtk/releases) 下载 `rtk-x86_64-pc-windows-msvc.zip`，解压 `rtk.exe` 到 PATH 目录。

**方法 D — Cargo（从源码）**:
```bash
cargo install --git https://github.com/rtk-ai/rtk
```

> ⚠️ 不要用 `cargo install rtk`，那是另一个同名包（Rust Type Kit）。

#### 初始化（安装后必须执行）

```bash
rtk init -g              # Claude Code / GitHub Copilot
rtk init -g --gemini     # Gemini CLI
rtk init -g --codex      # Codex CLI
```

初始化会自动注入 PreToolUse hook 到 `~/.claude/settings.json`，并创建 `~/.claude/RTK.md`。

#### 验证安装
```bash
rtk --version            # 应显示 rtk X.Y.Z
rtk gain                 # 查看 token 节省统计
rtk gain --history       # 查看命令历史及节省明细
rtk discover             # 分析 Claude Code 历史，发现未被拦截的命令
```

---

### Token 优化工具组合策略

| 组合 | 覆盖范围 | 预期效果 | 推荐场景 |
|------|---------|---------|---------|
| **Context Mode 单独** | MCP 工具输出 | ~98% 输出压缩 | 频繁使用 MCP 工具（Playwright、GitHub、DB） |
| **CodeGraph 单独** | 代码理解 | ~92% 调用减少 | 大型代码库探索和重构 |
| **RTK 单独** | Bash/外部命令 | 视场景而定 | 频繁执行 Shell 命令 |
| **Context Mode + CodeGraph** | MCP + 代码 | 双管齐下 | **推荐默认组合** |
| **三合一** | 全覆盖 | 最大化节省 | 长时间会话、复杂多工具任务 |

**关键点**: 三个工具各司其职互不冲突 — 读代码时 Claude Code 自动改用 CodeGraph，调用 MCP 时通过 Context Mode 执行，调用外部命令时由 RTK 处理。

---

## 二、API 流量检查工具

### 2.1 claude-tap

**项目**: [liaohch3/claude-tap](https://github.com/liaohch3/claude-tap)

**原理**: 在 Claude Code 和 API 之间添加本地反向代理，拦截所有 API 流量，记录每次请求的 system prompt、对话历史、工具定义、流式响应、token 用量。支持 9 个主流 AI Coding 客户端（Claude Code、Codex CLI、Gemini CLI、Kimi CLI 等）。

**核心能力**:
- **真实上下文查看**: 看到原始 API 请求和响应（不是 Agent Loop 的信息）
- **相邻请求 Diff**: 字符级 diff 高亮，看两次请求之间变了什么
- **Token 用量分析**: 输入/输出/缓存命中/缓存创建，按请求拆开
- **离线归档**: 自动生成自包含 HTML 文件，可离线打开或分享

#### 安装

**方法 A — uv 安装（推荐）**:
```bash
uv tool install claude-tap
```

**方法 B — pip 安装**:
```bash
pip install claude-tap
```

#### 使用方式

```bash
# 基础模式：拦截 Claude Code 流量，退出时生成 HTML 报告
claude-tap

# 实时模式：边跑边看，自动打开浏览器
claude-tap --tap-live

# 其他客户端
claude-tap --tap-client codex
claude-tap --tap-client gemini -- -p "hello"

# 查看历史 trace
claude-tap dashboard

# 仅开代理不启动客户端
claude-tap --tap-no-launch --tap-port 8080
```

#### 验证安装
```bash
claude-tap --version
```

#### 典型使用场景
- 月底看账单时定位高成本操作
- 调试 Agent 行为异常，查看完整 system prompt
- Prompt 工程，分析上下文传递链路
- 团队审计 Agent 行为（HTML 报告分享到群）

---

## 三、知识工作插件库

### 3.1 Knowledge Work Plugins

**项目**: [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) (17K+ Stars)

**定位**: Anthropic 官方开源的 Claude Cowork 插件库。覆盖 20+ 职业方向，纯 Markdown + JSON 架构，零代码依赖。兼容 Claude Code。

每个插件打包三样东西：
- **Skills**: 领域知识，Claude 自动调用
- **Commands**: 斜杠命令，用户主动触发
- **Connectors**: 外部工具连接（通过 MCP 协议）

#### 安装

```bash
# 添加插件市场
claude plugin marketplace add anthropics/knowledge-work-plugins

# 安装具体插件
claude plugin install engineering@knowledge-work-plugins
claude plugin install sales@knowledge-work-plugins
claude plugin install data@knowledge-work-plugins
```

#### 可用角色一览

| 插件 | 职业角色 | 核心能力 |
|------|---------|---------|
| **engineering** | 开发者 | 站会汇报、Code Review、结构化调试、架构决策、故障响应 |
| **product-management** | 产品经理 | PRD、Roadmap、用户调研、竞品跟踪 |
| **sales** | 销售 | 客户调研、通话准备、竞品战卡、管道复盘 |
| **data** | 数据分析 | SQL 生成、统计分析、可视化、Dashboard |
| **marketing** | 市场营销 | 内容创作、品牌审核、SEO 审计、渠道报告 |
| **small-business** | 小企业主 | 现金流预测、定价分析、营销策划、合同审查（15 技能 + 15 工作流） |
| **legal** | 法务 | 合同审查、NDA 分拣、合规检查、风险评估 |
| **finance** | 财务 | 会计分录、对账、报表生成、审计支持 |
| **human-resources** | HR | 薪酬分析、面试准备、入职流程、绩效评估 |
| **design** | 设计师 | 设计评审、无障碍审查、设计系统、UX 文案 |
| **bio-research** | 生物研究 | 文献检索、基因组分析、靶点排序 |
| **operations** | 运维 | 容量规划、变更管理、Runbook |
| **productivity** | 个人效率 | 任务管理、日历整合、记忆管理 |

#### 与本项目 Agent 系统的关系

Knowledge Work Plugins 的 Skills + Commands 架构与本项目的 Skill + Agent 体系在设计哲学上对等。区别在于：
- **本项目**: 面向开发者和 AI 工程师，深度定制，Agent 路由由 Intent Detector 驱动
- **KWP**: 面向所有办公人群，即装即用，轻量配置

两者可互补使用：本项目处理开发和 AI 任务，KWP 处理非技术类办公任务。

---

## 四、Agent 框架扩展

### 4.1 Flue Framework

**项目**: [liangdabiao/flue-framework-skill](https://github.com/liangdabiao/flue-framework-skill) (4K+ Stars)

**定位**: 轻量 TypeScript Agent 脚手架框架（The Agent Harness Framework），面向快速构建和部署 AI Agent。

**核心 API**:
| API | 功能 |
|-----|------|
| `createAgent` | 创建 Agent 实例 |
| `defineTool` | 定义工具（类似 MCP Tool） |
| `defineAgentProfile` | 定义 Agent 角色配置 |
| `init` | 初始化框架 |
| routing | 多 Agent 路由 |
| SSE streaming | 实时流式推理输出 |

#### 安装

```bash
# 作为 Skill 安装（获取开发指导）
npx skills add liangdabiao/flue-framework-skill -g -y

# 或直接在项目中使用框架
npm init flue-app my-agent
cd my-agent
npm install
npm run dev
```

#### 与现有框架对比

| 维度 | Flue | Claude Agent SDK | LangGraph | CrewAI |
|------|------|-----------------|-----------|--------|
| **语言** | TypeScript | Python | Python | Python |
| **核心抽象** | createAgent + defineTool | ClaudeSDKClient + @tool | StateGraph + 节点 | Role + Crew |
| **流式输出** | SSE 内置 | WebSocket | 需自行实现 | 无 |
| **学习曲线** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| **社区** | 4K Stars | 7K Stars | 137K Stars | 52K Stars |
| **适用场景** | 快速 TS Agent + 实时推理 | Skill→SaaS + 安全部署 | 生产级循环工作流 | 快速原型 |

#### 适用场景
- 需要 TypeScript 技术栈（前端团队主导）
- 需要 SSE 流式推理输出（实时交互场景）
- 轻量级 Agent，不需要 LangGraph 的循环/检查点
- 快速原型，但比 CrewAI 更接近生产级

---

## 五、运维与基础设施 Skills

### 5.1 SSH Skill

**项目**: [badseal/ssh-skill](https://github.com/badseal/ssh-skill)

**定位**: 为 Claude Code 打造的企业级 SSH 管理工具，让远程服务器操作像本地一样简单高效。

**核心特性**:
- **高性能**: 调用原生 OpenSSH 功能
- **长连接守护进程**: 保持 SSH 连接不断开
- **超大文件传输**: 支持大文件高效传输
- **服务器间直连**: 服务器之间直接传输文件
- **统一配置管理**: 使用 OpenSSH 原生配置格式（终端可直接 `ssh server1`）
- **密码连接支持**: 对密码认证的服务器采用 Paramiko 实现长连接
- **SSH 隧道管理**: 本地端口转发、守护进程模式、自动重连、心跳检测
- **Windows 原生 SSH 适配**: 自动定位 `%SystemRoot%\System32\OpenSSH\ssh.exe`
- **Passphrase 密钥支持**: 通过 Windows SSH Agent 集成无感使用

#### 安装

```bash
npx skills add badseal/ssh-skill -g -y
```

#### 安全注意事项
- 密钥文件权限确保 `chmod 600`
- 密码认证通过 Paramiko 安全传输，不在命令行暴露
- 建议使用密钥认证优先，密码认证作为 fallback

---

### 5.2 System Cleaner Skill

**项目**: [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills)

**定位**: 桌面磁盘清理 Agent，扫描后生成可交互的 HTML 报告。Mac 和 Windows 均支持。

**核心机制 — 三色安全分级**:
| 级别 | 含义 | 操作 |
|------|------|------|
| 🟢 绿灯 | 纯缓存/临时文件/安装包残留 | 可放心让 Agent 清理，支持一键操作 |
| 🟡 黄灯 | 需人工判断（下载文件、项目文件夹等） | 打开 Finder/资源管理器自行确认 |
| 🔴 红灯 | 系统文件/核心数据 | 仅展示说明，跳过清理 |

**工作流程**: 全程只读扫描 → 浏览器打开交互式 HTML 报告 → 用户在报告页面主动点击删除 → 二次确认弹窗 → 执行

#### 安装

```bash
npx skills add KKKKhazix/khazix-skills -g -y
```

#### 使用
```
帮我看看存储
# 或
帮我清理一下磁盘
```

---

## 七、端侧模型接入（本地/云端混合推理）

> 来源：`docs/reports/AGENT-OS-LANDSCAPE-2026.md` § 本地/云端混合推理研究

### 核心理念

**端侧模型**（在用户本地设备运行）+ **云端主模型**（Claude / GPT-4）混合使用，实现：
- 敏感数据保护（数据不出本机）
- 成本控制（简单任务用免费本地模型）
- 离线可用（网络断开时降级到本地）

### 端侧模型对比

| 模型/框架 | 适用场景 | 资源要求 | 质量水平 | 接入复杂度 |
|----------|---------|---------|---------|-----------|
| **Ollama** | 通用本地推理（代码补全、文本生成） | 8GB+ RAM，推荐 GPU | 中（7B-13B 模型） | ⭐ 一条命令 |
| **VoxCPM** | 中文对话、知识问答（清华 CPM 系列） | 16GB+ RAM，GPU 推荐 | 中-高（中文优势） | ⭐⭐ 需手动部署 |
| **LM Studio** | 图形界面本地模型管理 | 同 Ollama | 中 | ⭐ 一键安装 |
| **LocalAI** | OpenAI API 兼容层（支持多种模型） | 可变（取决于模型） | 可变 | ⭐⭐ Docker 部署 |

### Ollama 接入指南（推荐）

#### 安装 Ollama

**macOS / Linux**:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows**:
下载安装包：<https://ollama.com/download/windows>

#### 下载模型

```bash
# 推荐：CodeLlama 7B（代码任务）
ollama pull codellama:7b

# 推荐：Llama 3.2 3B（轻量通用）
ollama pull llama3.2:3b

# 推荐：Qwen2.5 Coder 7B（中文代码）
ollama pull qwen2.5-coder:7b
```

#### 配置 Claude Code

在 `~/.config/claude/config.toml`（Linux/macOS）或 `%APPDATA%\claude\config.toml`（Windows）添加：

```toml
[auth]
api_key = "not-needed"
base_url = "http://localhost:11434/v1"

[model]
default = "codellama:7b"
```

#### 验证

```bash
# 启动 Ollama 服务
ollama serve

# 测试模型
ollama run codellama:7b "Write a Python function to sort a list"
```

### 使用场景决策树

```
任务需要最高质量？
├── 是 → 云端主模型（Claude Opus / Sonnet）
└── 否 → 任务涉及敏感数据？
         ├── 是 → 端侧模型（数据不出本机）
         └── 否 → 任务复杂度？
                  ├── 简单（代码补全、格式化） → 端侧模型（成本 0）
                  └── 复杂（架构设计、调试） → 云端模型
```

### PilotDeck 的任务驱动自动部署模式（参考）

**原理**：系统自动判断任务类型，决定是否启动端侧模型。

**优势**：
- 用户无需手动切换模型
- 任务完成后自动卸载模型（节省资源）

**风险**：
- 算力预算控制（避免无限制启动模型）
- 模型质量基线（端侧模型失败时需 fallback 到云端）
- 初次部署时间长（模型下载可能数 GB）

**当前不建议借鉴原因**：
- 本项目 Agent 路由已通过 `intent-state.json` 实现
- 手动配置端侧模型（通过 `config.toml`）已满足需求
- 自动部署增加系统复杂度，暂无明确收益

### 成本对比

| 场景 | 云端模型（Claude Sonnet） | 端侧模型（Ollama） | 节省 |
|------|-------------------------|-------------------|------|
| 代码补全（1000 次/天） | ~$2/天 | $0 | 100% |
| 简单查询（500 次/天） | ~$1/天 | $0 | 100% |
| 复杂推理（100 次/天） | ~$5/天 | 质量不足，需云端 | 0% |

### 最佳实践

**推荐策略**：
1. **默认云端**：保证任务质量，使用 Claude Sonnet / Opus
2. **敏感数据场景**：强制本地（如代码审查包含 API Key、内部文档分析）
3. **开发测试**：用端侧模型快速迭代（prompt 调试、Skill 开发）

**不推荐**：
- 关键任务（生产部署、安全审计）使用端侧小模型
- 复杂多步骤任务（架构设计、SDD-RIPER）用端侧模型

### 验证清单

端侧模型接入后检查：
- [ ] 模型推理速度可接受（<5 秒首 token）
- [ ] 输出质量满足场景需求（代码可运行、逻辑正确）
- [ ] 资源消耗在预算内（RAM <16GB，GPU 利用率 <80%）
- [ ] 云端 fallback 机制可用（端侧失败时自动切换）

> 相关：`docs/API-KEYS-SETUP.md`（模型配置）、`docs/reports/AGENT-OS-LANDSCAPE-2026.md`（研究来源）

---

> 本节定义 Claude 何时主动检测并建议安装工具。协议也写入 `CLAUDE.md` §十二。

### 🆕 v1.1 协议升级：自动驱动（不再依赖用户主动提出）

**升级前的问题**：v1.0 协议是被动文档，Claude 只能等用户说"我要清理磁盘"才去查文档并推荐。需要用户**先知道**有这个工具才能获得引导。

**v1.1 协议**：检测信号 → 写 intent-state.json → 强制检查流程，全部自动化。

```
┌─────────────────────────────────────────────────────────────┐
│ 用户消息: "我想清理磁盘空间" │
└────────────────────┬────────────────────────────────────────┘
 │
 ▼
┌─────────────────────────────────────────────────────────────┐
│ UserPromptSubmit Hook │
│ 1. intent-detector.sh 自动运行 │
│ 2. 关键词匹配 config/keywords.json::external_tools │
│ 3. 命中 "清理磁盘" → 工具: system-cleaner, priority: high │
│ 4. 写入 ~/.claude/intent-state.json: │
│ { │
│ "intent": "general", │
│ "agent": "orchestrator", │
│ "tool_recommendation": { │
│ "tool": "system-cleaner", │
│ "priority": "high", │
│ "install_cmd": "npx skills add ..", │
│ "verify_cmd": "ls ~/.claude/skills/ ..", │
│ .. │
│ } │
│ } │
└────────────────────┬────────────────────────────────────────┘
 │
 ▼
┌─────────────────────────────────────────────────────────────┐
│ Claude 响应前强制检查 (CLAUDE.md §0.2 第 8 步) │
│ 1. 读取 intent-state.json │
│ 2. 检测到 tool_recommendation 非空 │
│ 3. 并行执行 verify_cmd 验证工具是否已安装 │
│ 4. 未安装 → 输出「外部工具引导话术模板」（install_cmd + │
│ verify_cmd + expected），等用户口头同意 │
│ 5. 用户同意 → 自动执行安装 + 验证 │
└─────────────────────────────────────────────────────────────┘
```

**关键改进**：
- 用户**无需**知道工具存在
- 关键词文件 `config/keywords.json::external_tools` 是**可扩展**的：新增工具只需添加一个 JSON 块
- 优先级机制（high/medium/low）避免低优先级误抢
- 优雅降级：辅助脚本/关键词文件缺失时静默跳过，不影响 Agent 调度主流程
- 触发频率受控：本会话内同一工具仅引导一次

### 协议维护指南

**新增工具的 3 步流程**：

1. **编辑 `config/keywords.json`** 在 `external_tools` 分类下新增条目：
 ```json
 "your-tool": {
 "keywords": ["触发词1", "触发词2"],
 "install_cmd": "npx skills add xxx/xxx -g -y",
 "verify_cmd": "which xxx 2>/dev/null || echo 'NOT_INSTALLED'",
 "expected": "输出xxx",
 "doc": "docs/TOOLS-ECOSYSTEM-GUIDE.md §X.X",
 "priority": "high|medium|low"
 }
 ```

2. **编辑 `hooks/detect-external-tool.py` 的 `TOOL_PRIORITY` 字典**：
 ```python
 TOOL_PRIORITY = {
 ..,
 "your-tool": "high", # 顺序决定匹配优先级
 }
 ```

3. **在 `docs/TOOLS-ECOSYSTEM-GUIDE.md` 添加工具章节**，包含安装命令、验证方法、典型使用场景。

**测试方法**：
```bash
# 单元测试钩子
echo '{"prompt":"你的测试输入"}' | bash hooks/intent-detector.sh
cat ~/.claude/intent-state.json | python -c "import json, sys; d=json.load(sys.stdin); print(d['tool_recommendation'])"
```

### 检测触发场景

| # | 检测信号 | 推荐工具 | 安装命令 | 预期效果 |
|---|---------|---------|---------|---------|
| 1 | 会话 token 消耗 >100K 且 `claude mcp list` 无 context-mode | **Context Mode** | `claude mcp add context-mode -- npx -y context-mode` | 后续工具输出压缩 ~98% |
| 2 | 代码探索 >20 次 Read/Grep 且 `codegraph --version` 失败 | **CodeGraph** | `npx @colbymchenry/codegraph && codegraph init -i` | 后续代码探索减少 ~92% 调用 |
| 3 | 用户询问 token 成本 / API 调用细节 / 想调试 Agent | **claude-tap** | `pip install claude-tap` | 可查看每次 API 请求的 token 明细 |
| 4 | 用户需要 SSH 连接多台服务器 / 提到远程服务器操作 | **SSH Skill** | `npx skills add badseal/ssh-skill -g -y` | 长连接 + 统一配置 |
| 5 | 用户需要构建 TypeScript Agent / 提到 Flue | **Flue Framework** | `npx skills add liangdabiao/flue-framework-skill -g -y` | TS Agent 开发指导 |
| 6 | 用户想清理磁盘 / 查找大文件 / 存储空间不足 | **System Cleaner** | `npx skills add KKKKhazix/khazix-skills -g -y` | 交互式磁盘清理报告 |
| 7 | 用户提到安全测试 / 漏洞挖掘 / 渗透测试 / 需要代理观察 AI 请求 | **Yakit MCP** | 见下方 §六 | HTTP 流量代理 + 数据包验证 + 防幻觉 |

### 推荐执行流程

```
1. 检测到触发场景
   ↓
2. 主动建议：
   "检测到 [场景描述]，建议安装 [工具名称]，可 [预期效果]。
    是否安装？（安装命令: `xxx`）"
   ↓
3a. 用户同意 → 直接执行安装命令 → 验证安装成功 → 报告结果
3b. 用户拒绝 → 记录偏好，同一会话不再重复推荐该工具
```

### 安装后验证清单

| 工具 | 验证命令 | 预期结果 |
|------|---------|---------|
| Context Mode | `claude mcp list` | 列表中包含 `context-mode` |
| CodeGraph | `codegraph --version` | 输出版本号 |
| RTK | `rtk --version` | 输出版本号 |
| claude-tap | `claude-tap --version` | 输出版本号 |
| SSH Skill | 检查 `.claude/skills/` 目录 | 存在 ssh-skill 相关文件 |
| Flue Framework | 检查 `.claude/skills/` 目录 | 存在 flue-framework 相关文件 |
| System Cleaner | 检查 `.claude/skills/` 目录 | 存在相关文件 |
| Knowledge Work Plugins | `claude plugin list` | 列表中包含已安装插件 |

---

## 工具选择决策树

```
你需要什么帮助？
│
├─ Token 消耗太快 / 成本太高？
│   ├─ 主要是 MCP 工具输出大？
│   │   └─ ✅ Context Mode
│   ├─ 主要是代码探索调用多？
│   │   └─ ✅ CodeGraph
│   ├─ 主要是 Bash 命令输出大？
│   │   └─ ✅ RTK
│   └─ 全都有 / 不确定？
│       └─ ✅ Context Mode + CodeGraph（推荐默认组合）
│
├─ 想了解 API 调用细节 / 调试 Agent 行为？
│   └─ ✅ claude-tap
│
├─ 需要特定职业角色辅助（销售/法务/HR/数据分析等）？
│   └─ ✅ Knowledge Work Plugins
│
├─ 需要构建 Agent 产品？
│   ├─ Python + 生产级 + Skill→SaaS？
│   │   └─ ✅ Claude Agent SDK（见 AGENT-FRAMEWORK-DECISION.md）
│   ├─ TypeScript + 轻量 + SSE 流式？
│   │   └─ ✅ Flue Framework
│   └─ 需要循环 + 检查点 + 人机交互？
│       └─ ✅ LangGraph（见 AGENT-FRAMEWORK-DECISION.md）
│
├─ 需要连接远程服务器？
│   └─ ✅ SSH Skill
│
└─ 想清理磁盘 / 优化存储？
    └─ ✅ System Cleaner Skill
```

---

## 多 AI Agent 工具 Skill 共享

> 适用于同时使用 Claude Code、Codex CLI、OpenCode、Hermes、OpenClaw 等多个 Agent 工具的用户。

**核心思路**：选一个工具作为 Skill 中心（推荐 Claude Code），其他工具全部指向它，避免多份维护。

### 各工具接入方式

| 工具 | 共享机制 | 操作 |
|------|---------|------|
| **Claude Code** | 中心（`~/.claude/skills/`） | 无需操作，天然主库 |
| **OpenCode** | 自动扫描 `~/.claude/skills/` | 零配置，直接读取 |
| **Codex CLI** | 逐个 Skill 软链接 | 见下方脚本 |
| **Hermes** | `external_dirs` 配置 | 编辑 `~/.hermes/config.yaml` |
| **OpenClaw** | 独立目录，可选软链接互通 | 按需决定是否统一 |

**Codex 接入（软链接脚本）**:
```bash
for skill in ~/.claude/skills/*/; do
  name=$(basename "$skill")
  [ -e ~/.codex/skills/"$name" ] || ln -s ~/.claude/skills/"$name" ~/.codex/skills/"$name"
done
```

**Hermes 接入（一行配置）**:
```yaml
# 编辑 ~/.hermes/config.yaml
skills:
  external_dirs: ["~/.claude/skills"]
```

**注意事项**：
- Skill 的 YAML frontmatter + Markdown 格式在所有工具间通用，无兼容问题
- 引用工具专属 API（如 OpenClaw 的 sessions_spawn）的 Skill 在其他工具里只能作参考文档
- Codex 内置 `~/.codex/skills/.system/` 不受软链接影响，双方共存

---

## 六、安全测试与可观测性工具

### 6.1 Yakit（HTTP 代理 + 数据包验证）

**项目**: [yaklang/yakit](https://github.com/yaklang/yakit)

**核心价值**: 将 Yakit 作为 MCP 代理，让 AI 生成的所有 HTTP 请求都经过 Yakit，实现流量观察、数据包验证、防幻觉。

**适用场景**:
- 安全测试 / 渗透测试 / 漏洞挖掘
- 验证 AI 生成的 HTTP 请求是否正确（防止 AI 幻觉生成错误请求）
- 需要观察 AI Agent 的网络行为

**工作原理**:

```
用户请求 → Claude Code → 生成 HTTP 请求
                ↓
            Yakit 代理（拦截、验证、记录）
                ↓
            目标服务器
```

#### 安装（Windows 示例）

1. 下载 Yakit: https://github.com/yaklang/yakit/releases
2. 启动 Yakit 并开启代理模式（默认端口 8083）
3. 配置 Claude Code 使用代理

#### 配置方式

**方法 A — 全局代理（所有 AI 请求走 Yakit）**:

```bash
# 在 ~/.claude/settings.json 中配置
{
  "env": {
    "HTTP_PROXY": "http://127.0.0.1:8083",
    "HTTPS_PROXY": "http://127.0.0.1:8083"
  }
}
```

**方法 B — Skill 级代理（仅安全测试 Skill 走 Yakit）**:

在 `.claude/skills/security-testing/SKILL.md` 中指定：

```markdown
## 执行环境

所有 HTTP 请求必须经过 Yakit 代理验证：
- 代理地址: http://127.0.0.1:8083
- 验证方法: 在 Yakit 中查看请求是否符合预期
- 如发现 AI 幻觉（生成不存在的端点/参数），立即停止并报告
```

#### 典型工作流

```markdown
用户: "帮我测试这个 API 的安全性"

Agent:
1. 加载安全测试 Skill
2. 生成测试请求（SQL 注入/XSS/未授权访问等）
3. 所有请求经过 Yakit 代理
4. 在 Yakit 中观察：
   - 请求是否符合预期格式？
   - 是否有 AI 幻觉（编造的 header/参数）？
   - 响应状态码和内容是否合理？
5. 根据 Yakit 记录生成安全报告
```

#### 防幻觉机制

Yakit 作为代理的最大价值：**实时验证 AI 生成的请求**

```
AI 生成请求 → Yakit 拦截
           ↓
  用户在 Yakit 中检查：
  - 这个端点真的存在吗？
  - 这个 Authorization header 格式对吗？
  - 这个参数是文档里有的还是 AI 编的？
           ↓
  确认无误 → 放行
  发现幻觉 → 拒绝 + 反馈给 AI 重新生成
```

#### 与其他工具的组合

| 工具组合 | 场景 | 效果 |
|---------|------|------|
| Yakit + CC Switch + DeepSeek | 成本敏感的安全测试 | DeepSeek 价格低，Yakit 保证质量 |
| Yakit + CTF Skills | CTF 挑战 | AI 生成 exploit，Yakit 验证请求 |
| Yakit + code-security-review Skill | 代码安全审计 + 动态验证 | 静态分析 + 动态测试结合 |

#### 注意事项

1. **Yakit 不是 MCP 服务器**：当前需要手动配置代理，未来可能有社区实现 Yakit MCP Server
2. **代理会增加延迟**：每个请求都经过 Yakit，适合安全测试场景，不适合高频 API 调用
3. **需要手动验证**：Yakit 只是拦截和记录，最终验证仍需人工判断

#### 相关 Agent

- `agents/security/security-analyst.md` — 安全分析 Agent
- `agents/security/security-audit.md` — 安全审计 Agent
- `.claude/skills/ctf-web/SKILL.md` — Web 安全 CTF Skill

---

## 相关文档

- `CLAUDE.md` §十二 — 主动推荐协议（摘要版）
- `docs/CONTEXT-ENGINEERING-GUIDE.md` — Token 优化工具速览
- `docs/BEST-PRACTICES.md` §4.1 — MCP 服务器列表
- `docs/BEST-PRACTICES.md` §8.2 — 成本控制
- `docs/BEST-PRACTICES.md` §10.2 — 调试技巧
- `docs/AGENT-FRAMEWORK-DECISION.md` — 框架选型（含 Flue）
- `docs/SKILLS-CATALOG.md` — 社区 Skills 列表
- `.claude/skills/INDEX.md` — 轻量索引
- `docs/mcp-configuration-guide.md` — MCP 配置详解

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

## 主动推荐协议

> 本节定义 Claude 何时主动检测并建议安装工具。协议也写入 `CLAUDE.md` §十二。

### 检测触发场景

| # | 检测信号 | 推荐工具 | 安装命令 | 预期效果 |
|---|---------|---------|---------|---------|
| 1 | 会话 token 消耗 >100K 且 `claude mcp list` 无 context-mode | **Context Mode** | `claude mcp add context-mode -- npx -y context-mode` | 后续工具输出压缩 ~98% |
| 2 | 代码探索 >20 次 Read/Grep 且 `codegraph --version` 失败 | **CodeGraph** | `npx @colbymchenry/codegraph && codegraph init -i` | 后续代码探索减少 ~92% 调用 |
| 3 | 用户询问 token 成本 / API 调用细节 / 想调试 Agent | **claude-tap** | `pip install claude-tap` | 可查看每次 API 请求的 token 明细 |
| 4 | 用户需要 SSH 连接多台服务器 / 提到远程服务器操作 | **SSH Skill** | `npx skills add badseal/ssh-skill -g -y` | 长连接 + 统一配置 |
| 5 | 用户需要构建 TypeScript Agent / 提到 Flue | **Flue Framework** | `npx skills add liangdabiao/flue-framework-skill -g -y` | TS Agent 开发指导 |
| 6 | 用户想清理磁盘 / 查找大文件 / 存储空间不足 | **System Cleaner** | `npx skills add KKKKhazix/khazix-skills -g -y` | 交互式磁盘清理报告 |

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

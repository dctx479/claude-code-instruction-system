# 变更日志

本文档记录太一元系统的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [1.4.0] - 2026-11-19

对照 Claude Code 官方 hooks 规范（CLI 2.1.x）做的一次可用性修复：此前自动化层（自动调度、Ralph 循环、自定义命令）在新机器上不会生效。

### 新增

- `scripts/install-global.py`：把仓库同步到 `~/.claude/` 并将 `hooks/hooks.json` 合并进 `~/.claude/settings.json`。可重复执行、覆盖前备份、不删除文件、保留用户自己的 hooks 和其他 settings 键；`commands/` 拍平安装以保证 `/ralph` 而不是 `/general:ralph`。规范见 `specs/SPEC-global-install.md`
- `.claude/context/resolutions/`：`test-integrations.sh` 检查的归档目录（此前因空目录未被 git 跟踪而缺失）

### 修复

- **Ralph 循环无法续跑**：Stop Hook 由 `exit 3` + stdout 改为 `exit 2` + stderr（`hooks/ralph-stop-interceptor.sh` v2.0.0）
- **Ralph 全局状态文件在 Windows 上读不到**：Git Bash 路径经 `cygpath -m` 转换后通过 argv 传给 Python，不再拼进代码；解析失败时显式告警而不是静默放行
- **全局 Ralph 状态拦住所有项目**：状态文件新增 `project_dir`，与当前项目不符时放行
- **命令安全校验可绕过**（`scripts/validate/validate-command.sh` v1.2.0）：无 jq 时命令在第一个转义引号处被截断；警告规则排在阻塞规则之前导致 `sudo mkfs ...` 只警告不拦截；格式化规则按子串匹配误拦 `grep fdisk`
- **`hooks/hooks.json` v4.0.0**：`timeout` 由毫秒值改为秒；脚本路径由 `./` 改为 `$HOME/.claude/...`；子代理 matcher 改为 `Agent|Task`；会话清理由 Stop 移到 SessionEnd；移除 handler 上的非标准 `description` 字段和无意义的 `echo` hooks
- `hooks/intent-detector.sh` v2.2.0：提示词含引号时不再被截断；`qa-fix` 规则不再被 `qa` 关键词抢先命中
- `hooks/agent-tracker.sh` v2.0.0：从 stdin 读取 `tool_name`（原先依赖不存在的 `TOOL_NAME` 环境变量，从未生效）
- `scripts/hooks/on-stop.sh`：移除 `rm -f /tmp/claude-*`、`rm -rf .claude-tmp`（违反 §七 禁止批量删除，且会删掉其他会话的文件）；通知脚本路径修正
- `scripts/hooks/post-edit.sh`：无 jq 时也能取到文件路径；不再 `touch` 刚编辑的文件
- `.claude/statusline/hud.sh`：Agent 名读取兼容带空格的 JSON；Ralph 状态路径与 Stop Hook 一致
- `scripts/test-integrations.sh`：`set -e` 使脚本在第一个失败项即退出；Skills 索引路径错误
- `scripts/validate/validate-config.py`：不再建议使用 `bash.exe` 绝对路径（该写法本身会失败），新增毫秒 timeout / 相对路径 / 非标准字段检查

### 文档

- `CLAUDE.md` v1.4：重写 Hook stdin 字段表（`tool_response`、Stop 有 stdin JSON），新增「Hook 退出码与 timeout 规范」和 hooks 加载位置说明；修正端口管理脚本路径；删除重复的知识资产审计条目
- `README.md` / `docs/QUICK-START.md` / `QUICK-REFERENCE.md` / `docs/CONFIG-FILES-GUIDE.md` / `scripts/README.md`：安装步骤改为使用安装脚本，示例中的 timeout、bash 路径、模型 ID 同步更新
- `docs/hud/*`：脚本名 `hud-v2.sh` 统一为实际存在的 `hud.sh`

### 清理

- `.claude/settings.local.json`：清空指向另一台机器（`C:/Users/ASUS`、`G:/`）的 19 条一次性权限
- 取消跟踪误提交的 8 个 `graph/__pycache__/*.pyc`

---

## [1.3.0] - 2026-06-16

### 新增功能

#### 思维工具链 Skills（ljg-skills / nuwa-skill / Supervisor-Skills）
- `CLAUDE.md` §十二 新增三条工具触发场景
  - **ljg-skills**（深度追问 / 伴读 / 圆桌讨论）
  - **nuwa-skill**（人物思维框架蒸馏 → 可用顾问）
  - **Supervisor-Skills**（CS/AI 研究生投稿前 AI 模拟审稿）
- `docs/SKILLS-CATALOG.md` 新增 §Supervisor-Skills 章节
  - AI Pre-Review 说明（投稿前模拟 reviewer 视角，初筛工具定位）
  - Vibe Research 理念与本项目科研支持系统对接表

#### 任务偏差根因六分类（R1-R6）
- `CLAUDE.md` §八 规则增长策略新增 R1-R6 根因分类表
  - R1-R4 触发规范进化；R5（代码 bug）/ R6（外部因素）不动规范
  - 返工 ≥2 次自动升级 D2 检查项规则
- `memory/best-practices.md` 新增 **BP-051**（VFM 88，本项目迄今最高频适用条目）

### 改进

- CLAUDE.md §十 科研支持：Vibe Researching 理念与 Supervisor-Skills 衔接
- 全局 `~/.claude/CLAUDE.md` 同步至 v1.3.0，补齐三条新工具触发规则和 R1-R6 表格

### BP 关系图（新增）

- BP-037（事故驱动增长）= "什么情况下加规则"
- BP-051（R1-R6 根因六分类）= "判断是否该加规则的方法"（操作手册）

---

## [1.2.0] - 2026-06-15

### 新增功能

#### Round 1：自我改进 Agent 体系（基于 Anthropic / SkillOpt 提炼）
- `docs/ORCHESTRATION-GUIDE.md` §自我改进 Agent 复利栈
  - 四层栈结构（Eval / Memory / Orchestration / Model）
  - 记忆五阶段（Fail → Investigate → Verify → Distill → Consult）
  - 独立 verifier 原则（maker 与 verifier 隔离上下文）
  - 模型分工表（Opus 决策 / Sonnet 主循环 / Haiku 工人 + 判官）
  - Vision 验 UI / Fallback 显式化（不静默失败）
- `docs/SKILLS-CATALOG.md` §Skill 优化六阶段管线（SkillOpt 借鉴）
  - Rollout → 反思 → 补丁 → 合并 → 排序 → 验证门控
  - 铁律：每次只改一个变量 / 候选必须过验证门
- `docs/QUICK-START.md` §Harness 渐进式搭建（五步增量法）
  - CLAUDE.md → SessionStart Hook → Skill → MCP → Sub-agent
  - 核心原则：规则放 CLAUDE.md，工作流放 Skill；每 Agent 限 3-5 个 MCP
- `memory/best-practices.md` 新增三条 BP 条目
  - **BP-047** 自我改进 Agent 复利栈（VFM 80）
  - **BP-048** SkillOpt 六阶段管线（VFM 72）
  - **BP-049** Harness 五步增量法（VFM 80）

#### Round 2：移动端接入 + 跨模型工作流 + 中文科研工具链
- `CLAUDE.md` §十二 新增两条工具触发场景
  - WeChat Claude Code（微信→CLI 桥接，移动端远程调用）
  - CNKI Research Toolkit（中文知网检索/Zotero 导入自动化）
- `README.md` 参考资源新增三条
  - claude-code-best-practice（57k+ Star 官方最佳实践集）
  - agent-designer（便携式 Skills 工作空间）
  - wechat-claude-code（微信→CLI 桥接方案）
- `docs/SKILLS-CATALOG.md` 三处扩展
  - §学术 PPT 一源多产链（单篇论文 → PPT / 海报 / 幻灯片 / polish / pptx）
  - §移动端与 IM 接入 Skills（WeChat Claude Code 五维评估表）
  - CNKI 科研工具补充至 claude-scientific-skills 小节
- `docs/BEST-PRACTICES.md` 两处扩展
  - §6.4 跨模型工作流（Plugin / MCP / Router 三模式对比表）
  - §1.5 分层加载规则（.claude/rules/ 机制说明）
- `docs/TOOLS-ECOSYSTEM-GUIDE.md` 概览表新增两行
  - WeChat Claude Code（移动端接入分类）
  - CNKI Research Toolkit（科研自动化分类）
- `memory/lessons-learned.md` 新增 #016
  - 二次审视学习价值：避免快筛丢失中等价值信号（含三步复盘协议）

#### Round 3：Skill 发布质量四阶梯
- `docs/SKILLS-CATALOG.md` 新增"Skill 发布质量四阶梯"章节
  - 四阶梯：能用 → 看懂 → 愿意安装 → 三分钟跑出闭环
  - 横向 6 维自检清单（命名钩子 / 首屏信任 / 安装摩擦 / 可验证产物 / 安全边界 / 生态兼容）
  - Darwin 评分铁律（实测表现权重最高）
- `.claude/skills/skill-creator/SKILL.md` Step 6 自检新增"发布质量"条目
- `memory/best-practices.md` 新增 BP-050
  - **BP-050** Skill 发布质量四阶梯（VFM 64）

### 改进

- 编排指南：从"六模式策略矩阵"扩展到"自我改进复利栈"，与 Ralph/Autopilot 互补
- Skill 目录：从"四要素契约化"扩展到"六阶段验证化 + 发布质量保障"，覆盖完整 Skill 生命周期
- 快速入门：新增 Harness 渐进式搭建，强化"按错误驱动补层"原则
- 工具生态：新增移动端（WeChat）和中文科研（CNKI）两个工具触发场景
- 最佳实践工程化：§6.4 跨模型协作 + §1.5 规则分层加载的工程化配套文档

### BP 关系图（本版本新增四条）

- BP-046（Karpathy 四原则）= "AI 做什么"
- BP-049（Harness 五步法）= "用什么工具做"
- BP-047（自我改进复利栈）= "怎么越用越聪明"
- BP-048（SkillOpt 六阶段管线）= "Skill 怎么持续优化"
- BP-050（发布质量四阶梯）= "Skill 怎么让别人也能用"

---

## [1.0.0] - 2026-03-01

### 首次公开发布

本版本为太一元系统的首次公开发布，对应内部构建版本 3.1.0。
核心特性详见 [docs/FEATURES.md](docs/FEATURES.md)。

---

## [3.1.0] - 2026-01-23

### 新增功能

#### 自主执行系统
- **Ralph Loop** - 自主循环执行，直到任务完成
- **Autopilot** - 全自主执行模式，5 阶段工作流（Planning → Specification → Development → QA → Delivery）

#### 可视化与监控
- **HUD Statusline** - 实时状态可视化
- **Intent Detector** - 智能意图识别，自动推荐 Agent 和 Skill
- **Performance Monitor** - 性能监控系统，数据驱动优化

#### 智能路由
- **Model Router** - 自动模型选择（Opus/Sonnet/Haiku）
- **Strategy Selector** - 智能编排策略选择

#### 记忆系统
- **Plan-Scoped Memory** - 计划级知识隔离
- **Context Archival** - 上下文归档系统

#### 科研支持
- **Research Parallel** - 科研并行工作流（SWARM/PARALLEL/HIERARCHICAL）
- **Literature-Mentor Skill** - 文献深度解读，支持交互模式和报告模式

#### 性能工具
- **HUD Renderer (Rust)** - 7-10x 性能提升
- **Git Info Collector (Rust)** - 5-8x 性能提升

#### 开发工具
- **Port Management** - 全局端口管理系统
- **TUI Config** - 交互式配置系统（Rust + ratatui）

#### 主题系统
- 支持 3 种主题：default, minimal, nerd
- 命令：`cc-patcher.sh theme <name>`

### 改进

#### Literature-Mentor Skill 增强
- 新增双模式支持：交互模式（Interactive Mode）+ 报告模式（Report Mode）
- 自动识别文献类型：Research Article vs Review Article
- 新增评分系统：多维度评分（创新性、严谨性、影响力、可复现性、写作质量）
- 新增 TODO List：三级结构（立即执行、短期计划、长期规划）
- 新增推荐阅读：必读段落和选读段落
- 创建两套完整模板：Template A (Research Article) 和 Template B (Review Article)

#### 命令系统
- 新增 `/literature-review-quick` - 快速文献精读
- 新增 `/literature-batch-review` - 批量文献精读（SWARM 模式）

#### 文档完善
- 更新 CLAUDE.md，添加 literature-mentor 使用说明
- 创建 agents/INDEX.md - Agent 索引（渐进式披露）
- 创建 skills/INDEX.md - Skills 索引（渐进式披露）
- 创建 config/keywords.json - 关键词配置
- 创建 config/mcp-servers.json - MCP 服务器配置
- 创建 .claude/context/ - 上下文归档目录结构

### 修复

- 修复文件路径不一致问题（全局目录 → 项目目录）
- 修复 Git 换行符问题（LF vs CRLF）
- 修复拼写错误（Recommand → Recommended）
- 删除不必要的文件（nul）
- 更新 .gitignore，排除运行时文件

### 已知问题

- 超长文献（>50页）可能导致报告生成超时
- 部分期刊格式可能无法自动识别
- Windows 环境下 Hooks 配置需要使用 Git Bash 路径

### 技术债务

- 需要创建更多 Agent 定义文件（部分 Agent 仅在 CLAUDE.md 中引用）
- 需要补充集成测试用例
- 需要添加性能基准测试

---

## [3.0.0] - 2026-01-15

### 新增功能

- 初始版本发布
- 自进化协议
- Agent 驾驭系统
- 质量保障系统（Spec-First + Self-Healing QA Loop）
- 科研支持系统（Vibe Researching）
- AI/ML 支持系统

### 架构设计

- 渐进式披露机制（Progressive Disclosure）
- 编排策略矩阵（6 种模式）
- 多层记忆协同（文件 + 图谱 + 性能数据）

---

## [未发布]

### 计划中的功能

- 支持更多文献类型（会议论文、书籍章节）
- 优化报告生成速度
- 添加多语言支持
- 创建架构图可视化工具
- 添加自动化文档验证

---

## 版本说明

- **主版本号（Major）**：不兼容的 API 变更
- **次版本号（Minor）**：向下兼容的功能性新增
- **修订号（Patch）**：向下兼容的问题修正

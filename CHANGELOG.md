# 变更日志

本文档记录太一元系统的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

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

# 记忆系统详细架构

> 索引见 `CLAUDE.md` 第九节。本文件提供各子系统的详细说明。

---

## 多层记忆架构

```
实时记忆 (当前对话)
    ↓ PreCompact Hook
上下文归档 (.claude/context/)
    ├── index.json       — 轻量级状态索引
    └── resolutions/     — 问题解决方案详情
    ↓ 定期同步
文件记忆 (memory/*.md) ←→ 知识图谱 (Graphiti) ←→ 性能数据库
```

---

## 9.2 性能监控系统

**核心 Agent**: `performance-monitor`, `auto-optimizer`

**监控指标**: 任务完成率、Token消耗、执行时间、用户满意度、成本效率

**命令**:
```bash
/performance-report daily|weekly|monthly
/optimize-system [cost|<agent-name>]
/agents performance-monitor "分析architect最近一周的表现"
/agents auto-optimizer "验证优化方案 #001 的效果"
```

**优化类型**: 模型选择优化 → Prompt优化 → 工作流优化 → 成本优化

**文件**:
- `memory/optimization-history.md`
- `memory/optimization-proposals/`
- `memory/performance-reports/`
- `commands/general/performance-report.md`
- `commands/general/optimize-system.md`

---

## 9.3 上下文归档系统

**核心理念**: 在上下文压缩前结构化沉淀对话关键信息，避免重复试错。

**文件结构**:
```
.claude/context/
├── index.json           — 项目状态、已验证事实、问题签名索引
├── resolutions/         — 问题解决方案 (NDJSON)
└── sessions/            — 完整会话归档（可选）
```

**index.json 包含**: 项目目标/状态 + 已验证事实 + 技术约束 + 下一步计划 + 问题索引

**resolution 包含**: 问题签名 + 根因分析 + 修复步骤 + 验证方法 + 反模式 + 相关文件

**渐进式注入流程**:
```
用户提出新需求 → 读取 index.json (<2KB)
    → 判断是否有相关历史
    → 如有 → 读取对应 resolution (详细)
    → 基于历史经验给出方案
```

**命令**:
```bash
/save-context "完成用户认证功能"
/read-context index
/read-context resolution res-001
/read-context list
```

**自动触发**: PreCompact Hook（`.claude/hooks/pre-compact.sh`）

**Agent**: `agents/ops/context-archivist.md`

---

## 9.4 知识图谱记忆（Graphiti）

**核心能力**: 跨会话知识持久化 + 语义搜索 + 自动关联发现 + 知识演化追踪

**使用方式**:
```markdown
存储实体: 名称/类型/属性 {"key": "value"}
创建关系: 源实体 → 关系类型 → 目标实体
检索: 关键词搜索 / 实体查询 / 时间范围
```

**详细文档**:
- `.claude/integrations/graphiti-setup.md`
- `.claude/memory/knowledge-strategy.md`
- `.claude/examples/graphiti-usage.md`

---

## 9.5 同步策略

| 频率 | 来源 → 目标 | 说明 |
|------|------------|------|
| 实时 | 对话 → .claude/context/ | PreCompact Hook 触发 |
| 每日 | .claude/context/ → memory/*.md | 结构化导入 |
| 每周 | memory/*.md → Graphiti | 知识图谱化 |
| 持续 | 性能数据 → agent-performance.md | 自动记录 |
| 按需 | Graphiti → memory/*.md | 生成报告 |

**冲突解决**: 以最新数据为准，重要变更手动确认。

---

## 上下文检索协议

**任务开始前**:
1. 自动读取 `.claude/context/index.json`
2. 了解项目状态和已验证事实
3. 检查是否有相关历史问题

**遇到问题时**:
1. 搜索 index 中的 `problem_signature`
2. 如有匹配 → 读取对应 resolution
3. 参考历史方案，避免重复试错

**提出方案时**:
1. 引用相关 resolution ID
2. 说明与历史方案的关系
3. 如有改进 → 记录到新 resolution

---

## 知识复利机制

> 详细指南: `docs/KNOWLEDGE-COMPOUNDING-GUIDE.md`

### 三层知识架构

```
Layer 1: 原始记录 → memory/lessons-learned.md, .claude/context/resolutions/
Layer 2: 策展知识 → memory/best-practices.md, memory/error-patterns.md, docs/*.md
Layer 3: 执行规则 → CLAUDE.md, agents/*.md, .claude/skills/*/SKILL.md
```

### 知识晋升流程

```
单次经验 → 通用模式 → 系统规则 → Agent/Skill 定义
  (2+ 次重复)  (跨场景验证)  (强制执行)   (领域专门化)
```

### 去重协议

新增知识条目前必须搜索现有内容，避免重复。详见 `memory/lessons-learned.md` 使用说明。

### 置信度标注

`[VERIFIED]` / `[INFERRED]` / `[AMBIGUOUS]` / `[UNVERIFIED]` — AI 参考知识时优先使用高置信度条目。

---

## 上下文注入模式（BP-025）

> 详见 `memory/best-practices.md` BP-025。

### 启动时注入 vs 按需查询

| 注入类型 | 时机 | 典型例子 |
|---------|------|---------|
| **启动时注入** | Agent 初始化时自动加载 | CLAUDE.md（高频全局规则）、intent-state.json（当前 intent） |
| **按需查询** | Agent 自主调用 `search_*` 工具 | `.claude/skills/INDEX.md` 概览 → 按需加载 SKILL.md |
| **Dependencies 注入** | 程序运行时动态注入 | Hook 环境变量、intent-state.json、上下文检索协议 |

### 何时用哪种

```
高频、稳定、跨任务都需要的规则     → 启动时注入（CLAUDE.md）
低频、任务相关、Agent 能判断       → 按需查询（search_* 工具）
运行时动态值（IP/租户ID/feature flag）→ Dependencies 注入（程序主动抓取）
```

### 太一元系统现有实现

| 机制 | 类型 | 说明 |
|------|------|------|
| `~/.claude/intent-state.json` | 启动时注入 | 每次响应前由 Hook 写入，触发 Agent 路由 |
| `.claude/skills/INDEX.md` | 按需查询 | 读取 ~600 token 概览后，按需加载具体 SKILL.md |
| `memory/` 索引协议 | 启动时注入 | 任务开始前读取 index.json，检查历史问题 |
| `~/.claude/settings.json` env 段 | Dependencies | 运行时动态配置，Hook 可访问 |
| Subagent 隔离 | 按需查询 | 探索性工作隔离在子上下文，只回传结论 |

### 知识源选择优先级

| 任务类型 | 首选 | 兜底 | 禁止 |
|---------|------|------|------|
| 项目内既有规则 | `memory/`、`docs/`、CLAUDE.md | Agent/Skill 回忆 | 直接 WebSearch |
| 最新外部事实/版本 | WebSearch/WebFetch | 专用 API | 仅靠模型知识 |
| 学术文献 | Zotero/真实文献库 | LLM 摘要和结构化 | 通用搜索 |
| 代码定位 | Grep/Glob/Read | Explore Agent | 不读直接猜 |
| 跨系统实时状态 | Subagent + query_<system> | 直接 API 调用 | 靠记忆 |

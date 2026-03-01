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

**Agent**: `agents/context-archivist.md`

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

# Commands 索引

> 31 个自定义命令，按场景分类。使用 `/command-name` 触发。

---

## 通用类 (General)

| 命令 | 文件 | 描述 | 典型场景 |
|------|------|------|---------|
| `/ralph` | general/ralph.md | 自主循环执行，Stop Hook 驱动的迭代任务 | 需要多轮自动执行的长任务 |
| `/autopilot` | general/autopilot.md | 全自主 5 阶段（规划/规范/开发/QA/交付） | 完整功能从零到一 |
| `/orchestrate` | general/orchestrate.md | 启动智能多 Agent 编排 | 复杂多步骤任务 |
| `/parallel` | general/parallel.md | 强制并行策略 | 多个独立子任务 |
| `/swarm` | general/swarm.md | 群体并行策略（批量处理 50+） | 大规模同质任务 |
| `/evolve` | general/evolve.md | 触发自进化流程，更新配置和最佳实践 | 任务失败后复盘 |
| `/commit` | general/commit.md | 标准化 Git 提交（��� changelog） | 代码提交 |
| `/fix-github-issue` | general/fix-github-issue.md | 自动修复 GitHub Issue | Bug 修复工作流 |
| `/optimize-system` | general/optimize-system.md | 系统配置自动优化 | 性能/成本优化 |
| `/performance-report` | general/performance-report.md | 生成 Agent 性能报告 | 监控分析 |
| `/read-context` | general/read-context.md | 读取并恢复会话上下文 | /compact 后恢复 |
| `/save-context` | general/save-context.md | 保存当前会话上下文 | /compact 前保存 |
| `/validate-config` | general/validate-config.md | 验证配置文件格式和完整性 | 配置变更后 |
| `/plan-to-issues` | general/plan-to-issues.md | 将计划转化为结构化 Issue CSV | 任务拆解 |
| `/issues-execute` | general/issues-execute.md | 按 Issue CSV 批量执行任务 | 结构化批量处理 |
| `/worktree-create` | general/worktree-create.md | 创建 Git Worktree 隔离工作区 | 多方案并行探索 |
| `/worktree-list` | general/worktree-list.md | 列出所有 Worktree 状态 | Worktree 管理 |
| `/worktree-cleanup` | general/worktree-cleanup.md | 清理完成/废弃的 Worktree | 工作区清理 |

---

## 开发类 (Development)

| 命令 | 文件 | 描述 | 典型场景 |
|------|------|------|---------|
| `/check` | dev/check.md | 快速代码检查（lint + type + test） | 提交前验证 |
| `/review` | dev/review.md | 触发 code-reviewer Agent 审查 | 代码审查 |
| `/spec-flow` | dev/spec-flow.md | 启动 Spec-First 完整工作流 | 新功能开发 |
| `/convert-openapi` | dev/convert-openapi.md | OpenAPI 规范转换与生成 | API 开发 |

---

## AI/Agent 类 (AI Agent)

| 命令 | 文件 | 描述 | 典型场景 |
|------|------|------|---------|
| `/create-agent` | ai-agent/create-agent.md | 创建新 Agent 定义文件 | 扩展 Agent 系统 |

---

## 科研类 (Research)

| 命令 | 文件 | 描述 | 典型场景 |
|------|------|------|---------|
| `/literature-review` | research/literature-review.md | 完整文献综述（Zotero 集成） | 学术调研 |
| `/literature-review-quick` | research/literature-review-quick.md | 快速文献综述 | 快速调研 |
| `/literature-batch-review` | research/literature-batch-review.md | 批量文献处理 | 大量文献筛选 |
| `/experiment-track` | research/experiment-track.md | 实验追踪（create/config/result/report/compare） | 科研实验记录 |

---

## 安全类 (Security)

| 命令 | 文件 | 描述 | 典型场景 |
|------|------|------|---------|
| `/audit` | security/audit.md | 启动代码安全审计工作流 | 安全审计 |
| `/ctf` | security/ctf.md | CTF 解题工作流（加载对应 CTF Skill） | CTF 竞赛 |

---

## 数据分析类 (Data Analysis)

| 命令 | 文件 | 描述 | 典型场景 |
|------|------|------|---------|
| `/eda` | data-analysis/eda.md | 探索性数据分析（EDA）工作流 | 数据探索 |
| `/sql` | data-analysis/sql.md | SQL 查询生成与优化 | 数据库查询 |

---

## 快速参考

### 最常用命令

```bash
/ralph "任务描述"         # 自主多轮执行
/autopilot "任务描述"     # 全自主端到端
/spec-flow               # Spec-First 新功能开发
/check                   # 提交前快速检查
/commit                  # 标准化提交
```

### 命令 vs Skill 的区别

| 维度 | 命令 (`/cmd`) | Skill (`/skillname`) |
|------|--------------|---------------------|
| 触发方式 | 用户主动调用 | 关键词匹配或主动调用 |
| 载体 | `commands/*.md` | `.claude/skills/*/SKILL.md` |
| 职责 | 工作流编排 | 领域能力封装 |
| 典型示例 | `/ralph`、`/autopilot` | `deep-research`、`sdd-riper` |
| 侧重 | 流程控制（做什么顺序） | 能力提供（怎么做） |

---

## 更新日志

### 2026-06-10
- 创建 commands/INDEX.md，整理 31 个命令
- 添加命令 vs Skill 对比说明

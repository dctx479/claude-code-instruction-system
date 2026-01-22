---
schema_version: 1.0
last_updated: 2026-01-16T00:00:00Z
worktrees: []
---

# 活动工作树追踪

此文件追踪所有活动的Git worktrees，支持并行任务管理和状态同步。

## 数据格式说明

每个worktree记录包含以下字段：

```yaml
- id: <task-id>              # 任务唯一标识符
  branch: <branch-name>       # Git分支名称
  path: <absolute-path>       # Worktree绝对路径
  status: <status>            # 任务状态
  agent: <agent-name>         # 分配的Agent
  created: <ISO-8601>         # 创建时间
  base_branch: <branch>       # 基准分支
  description: <text>         # 任务描述（可选）
  tags: [<tag1>, <tag2>]     # 标签（可选）
```

### 状态枚举 (status)
- `active`: 正在活跃开发
- `testing`: 开发完成，测试中
- `review`: 代码审查中
- `blocked`: 被阻塞，等待依赖
- `research`: 研究/实验阶段
- `completed`: 已完成（保留历史）

### Agent类型
- `coder`: 代码开发
- `debugger`: Bug修复
- `architect`: 架构设计
- `security-analyst`: 安全审计
- `data-scientist`: 数据分析
- `code-reviewer`: 代码审查

## 当前活动任务

*此区域由worktree命令自动更新*

---

## 示例记录

以下是示例格式，实际使用时请删除：

```yaml
worktrees:
  - id: task-001
    branch: feature-authentication
    path: G:/GitHub_local/worktrees/task-001
    status: active
    agent: coder
    created: 2026-01-16T09:15:00Z
    base_branch: main
    description: "实现JWT身份验证系统"
    tags: [security, backend]

  - id: bug-456
    branch: hotfix-memory-leak
    path: G:/GitHub_local/worktrees/bug-456
    status: testing
    agent: debugger
    created: 2026-01-16T11:30:00Z
    base_branch: develop
    description: "修复事件处理器内存泄漏"
    tags: [bugfix, performance]

  - id: exp-ai-agent
    branch: experimental-agent-system
    path: G:/GitHub_local/worktrees/exp-ai-agent
    status: research
    agent: architect
    created: 2026-01-10T14:00:00Z
    base_branch: main
    description: "探索AI Agent编排系统"
    tags: [experimental, ai, architecture]
```

---

## 历史记录（已完成）

### 2026-01 完成任务

```yaml
- id: task-000-example
  branch: feature-user-profile
  path: G:/GitHub_local/worktrees/task-000-example
  status: completed
  agent: coder
  created: 2026-01-10T10:00:00Z
  completed: 2026-01-12T16:30:00Z
  base_branch: main
  pr_url: https://github.com/org/repo/pull/123
  merged_to: main
  description: "用户资料管理功能"
```

---

## 维护指南

### 自动更新
- `/worktree-create` 创建新worktree时自动添加记录
- `/worktree-cleanup` 清理worktree时标记为completed
- `/worktree-list` 读取此文件展示状态

### 手动编辑
如需手动编辑，请遵循：
1. 保持YAML格式正确
2. 确保id唯一性
3. 使用ISO-8601时间格式
4. 路径使用绝对路径
5. 更新last_updated字段

### 数据验证
```bash
# 验证YAML格式
yamllint memory/active-worktrees.md

# 检查数据一致性
git worktree list  # 对比Git实际状态
```

### 同步策略
```bash
# 如果Git状态和此文件不同步，运行同步命令
/worktree-sync

# 或手动修复
git worktree prune  # 清理Git侧的过期引用
# 然后手动更新此文件
```

---

## 统计信息

*自动生成，每次运行/worktree-list时更新*

```yaml
statistics:
  total_active: 0
  total_completed: 0
  total_disk_usage_mb: 0
  average_age_days: 0
  by_status:
    active: 0
    testing: 0
    review: 0
    blocked: 0
    research: 0
  by_agent:
    coder: 0
    debugger: 0
    architect: 0
```

---

## 健康检查

### 每日检查项
- [ ] 是否有超过7天的活跃worktree？
- [ ] 是否有blocked状态超过2天的任务？
- [ ] 是否有未推送的重要更改？
- [ ] 总磁盘占用是否超过2GB？

### 清理建议
- 完成并合并的任务: 立即清理
- 超过14天未活动: 评估是否放弃
- 实验性任务: 定期评估价值

---

## 最佳实践

1. **及时更新**: 任何状态变化立即更新
2. **详细描述**: 为每个worktree添加清晰的description
3. **合理标签**: 使用tags便于分类和搜索
4. **保留历史**: completed的任务保留至少30天
5. **定期审计**: 每周审查一次所有活跃worktrees

---

## 自动化钩子

### Git Hooks集成
```bash
# .git/hooks/post-checkout
# 自动同步worktree状态
if [ -f memory/active-worktrees.md ]; then
    # 更新last_updated
    # 验证数据一致性
fi
```

### CI/CD集成
```yaml
# 在CI中验证worktree状态
- name: Validate worktrees
  run: |
    /worktree-list --format json > current.json
    # 验证所有活跃worktrees都有对应的open PR
```

---

## 故障恢复

### 如果文件损坏
```bash
# 从Git历史恢复
git show HEAD:memory/active-worktrees.md > memory/active-worktrees.md.backup

# 或从头重建
/worktree-rebuild-tracking
```

### 如果数据丢失
```bash
# 从Git worktree状态重建
git worktree list --porcelain | /worktree-import-from-git
```

---

*最后更新: 2026-01-16*
*Schema版本: 1.0*

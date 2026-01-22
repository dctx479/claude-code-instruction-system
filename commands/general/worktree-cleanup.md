# 清理并行工作树

完成任务后安全清理Git worktree，释放磁盘空间并保持仓库整洁。

## 用法

```bash
/worktree-cleanup <task-id> [--force] [--keep-branch]
```

## 参数说明

- `task-id`: 要清理的任务ID（必需）
- `--force`: 强制删除（即使有未提交的更改）
- `--keep-branch`: 保留分支不删除

## 工作流程

### 1. 验证任务状态
```bash
# 检查任务是否存在于追踪系统
grep "id: <task-id>" memory/active-worktrees.md

# 获取worktree信息
WORKTREE_PATH=$(grep -A 3 "id: <task-id>" memory/active-worktrees.md | grep "path:" | awk '{print $2}')
BRANCH_NAME=$(grep -A 3 "id: <task-id>" memory/active-worktrees.md | grep "branch:" | awk '{print $2}')
```

### 2. 检查合并状态
```bash
cd "$WORKTREE_PATH"

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️ 警告: Worktree有未提交的更改"
    git status --short

    # 如果没有--force标志，询问用户
    if [ "$FORCE" != "true" ]; then
        echo "❌ 拒绝清理。请先提交或使用 --force 强制删除"
        exit 1
    fi
fi

# 检查分支是否已合并到主分支
git fetch origin
MERGED=$(git branch --merged origin/main | grep "$BRANCH_NAME" || true)

if [ -z "$MERGED" ]; then
    echo "⚠️ 警告: 分支 '$BRANCH_NAME' 尚未合并到main"
    echo "💡 建议: 先完成PR合并或使用 --keep-branch 保留分支"
fi
```

### 3. 切换回主仓库
```bash
# 确保不在要删除的worktree中操作
cd "$MAIN_REPO_PATH"
```

### 4. 删除Worktree
```bash
# 标准删除
git worktree remove "$WORKTREE_PATH"

# 强制删除（如果有未提交更改）
git worktree remove --force "$WORKTREE_PATH"

# 成功输出:
# ✓ Removed worktree '../worktrees/task-001'
```

### 5. 清理本地分支（可选）
```bash
if [ "$KEEP_BRANCH" != "true" ]; then
    # 删除已合并的分支
    if [ -n "$MERGED" ]; then
        git branch -d "$BRANCH_NAME"
        echo "✓ 已删除本地分支: $BRANCH_NAME"
    else
        # 强制删除未合并的分支（需要确认）
        if [ "$FORCE" = "true" ]; then
            git branch -D "$BRANCH_NAME"
            echo "⚠️ 强制删除未合并分支: $BRANCH_NAME"
        else
            echo "💡 保留未合并分支: $BRANCH_NAME (使用 --force 强制删除)"
        fi
    fi
else
    echo "💾 保留分支: $BRANCH_NAME"
fi
```

### 6. 清理远程分支（可选）
```bash
# 如果分支已推送到远程且需要清理
if git show-ref --verify --quiet "refs/remotes/origin/$BRANCH_NAME"; then
    echo "🌐 远程分支存在: origin/$BRANCH_NAME"
    echo "💡 如需删除远程分支，运行: git push origin --delete $BRANCH_NAME"
fi
```

### 7. 更新任务追踪系统
```bash
# 从active-worktrees.md中移除记录
# 方式1: 标记为completed（保留历史）
sed -i "/id: $TASK_ID/,/^$/s/status: active/status: completed/" memory/active-worktrees.md
sed -i "/id: $TASK_ID/,/^$/s/$/\n  completed: $(date -Iseconds)/" memory/active-worktrees.md

# 方式2: 完全删除（不保留历史）
# sed -i "/id: $TASK_ID/,/^$/d" memory/active-worktrees.md
```

### 8. 输出清理报告
```markdown
✅ Worktree清理完成!

📁 已删除路径: <WORKTREE_PATH>
🌿 分支处理: <deleted/kept>
🆔 任务ID: <task-id>
💾 磁盘释放: <估算大小>

📊 清理摘要:
   - Worktree: ✓ 已删除
   - 本地分支: <状态>
   - 远程分支: <状态>
   - 追踪记录: ✓ 已更新
```

## 使用示例

### 示例1: 标准清理（任务已完成并合并）
```bash
/worktree-cleanup task-001
```

### 示例2: 强制清理（有未提交更改）
```bash
/worktree-cleanup bug-456 --force
```

### 示例3: 清理但保留分支
```bash
/worktree-cleanup feature-experimental --keep-branch
```

### 示例4: 完全清理（包括远程分支）
```bash
/worktree-cleanup task-002
# 然后手动清理远程
git push origin --delete feature-xxx
```

## 清理策略

### 自动清理条件
以下情况下可以安全地自动清理：
- ✅ 分支已合并到main/develop
- ✅ 没有未提交的更改
- ✅ PR已关闭或合并
- ✅ 没有未推送的commit

### 需要手动确认的情况
以下情况需要人工判断：
- ⚠️ 分支未合并
- ⚠️ 有未提交的更改
- ⚠️ 有未推送的commit
- ⚠️ PR仍在审查中

## 批量清理

### 清理所有已完成任务
```bash
# 列出所有已合并的worktrees
git worktree list
git branch --merged main

# 批量清理脚本
for task_id in $(grep "status: completed" memory/active-worktrees.md | awk '{print $2}'); do
    /worktree-cleanup "$task_id"
done
```

### 清理过期worktrees（超过30天）
```bash
# 查找超过30天未更新的worktrees
find ../worktrees -maxdepth 1 -type d -mtime +30

# 人工审查后批量清理
```

## 故障排除

### 问题1: Worktree正在使用中
```bash
# 错误: fatal: '<path>' is locked
# 原因: 可能有进程在worktree目录中运行

# 解决步骤:
1. 检查是否有进程占用
   lsof +D ../worktrees/task-001  # Linux/Mac

2. 关闭相关进程（编辑器、终端等）

3. 如果确认无进程，删除锁文件
   rm .git/worktrees/task-001/locked

4. 重试清理
```

### 问题2: 目录已删除但Git仍追踪
```bash
# 错误: worktree已从磁盘删除，但git worktree list仍显示

# 解决:
git worktree prune
# 清理Git内部的worktree引用
```

### 问题3: 分支无法删除
```bash
# 错误: error: The branch 'feature-x' is not fully merged

# 原因: 分支有未合并的提交

# 选项1: 确认后强制删除
git branch -D feature-x

# 选项2: 先合并再删除
git checkout main
git merge feature-x
git branch -d feature-x
```

### 问题4: 权限不足
```bash
# 错误: Permission denied

# 解决: 检查目录权限
ls -la ../worktrees/
chmod -R u+w ../worktrees/task-001  # 添加写权限
```

## 安全检查清单

清理前确认：
- [ ] 所有更改已提交
- [ ] 所有commit已推送到远程
- [ ] PR已合并或不再需要
- [ ] 没有其他开发者依赖此分支
- [ ] 重要代码已备份

## 最佳实践

### ✅ 推荐做法
1. **及时清理**: 任务完成并合并后立即清理
2. **保留历史**: 在active-worktrees.md中标记completed而非删除
3. **验证合并**: 确认PR已合并再清理
4. **定期审计**: 每周审查活动worktrees，清理僵尸任务

### ❌ 避免事项
1. **避免盲目强制**: 不确定时不要使用--force
2. **避免删除活跃任务**: 确认任务真正完成
3. **避免手动删除目录**: 始终使用git worktree remove
4. **避免清理共享分支**: 其他人可能依赖

## 与其他命令的集成

- **查看状态**: `/worktree-list` 查看哪些可以清理
- **批量操作**: `/orchestrate cleanup-old-worktrees` 智能批量清理
- **健康检查**: 定期运行`git worktree prune`清理过期引用

## 性能指标

- 清理时间: < 2秒
- 磁盘释放: 50-200MB/worktree
- 安全性: 多重检查防止误删
- 可恢复性: 分支保留30天（如未删除远程）

## 恢复误删除的Worktree

如果不小心删除了worktree：

```bash
# 1. 检查分支是否还在
git branch -a

# 2. 如果分支还在，重新创建worktree
/worktree-create <task-id> <branch-name>

# 3. 如果分支已删除但未推送，从reflog恢复
git reflog
git checkout -b <branch-name> <commit-hash>

# 4. 如果已推送到远程，从远程恢复
git checkout -b <branch-name> origin/<branch-name>
```

## 相关命令

- `/worktree-create` - 创建新的worktree
- `/worktree-list` - 列出所有活动worktrees
- `/orchestrate` - 智能管理worktree生命周期
- `git worktree prune` - 清理过期的worktree引用

## 自动化建议

### Git Hook集成
```bash
# .git/hooks/post-merge
# 自动提示清理已合并的worktrees

#!/bin/bash
MERGED_BRANCHES=$(git branch --merged main | grep -v "main")
if [ -n "$MERGED_BRANCHES" ]; then
    echo "💡 以下分支已合并，可以清理对应worktrees:"
    echo "$MERGED_BRANCHES"
fi
```

### CI/CD集成
```yaml
# 在PR合并后自动触发清理
on:
  pull_request:
    types: [closed]

jobs:
  cleanup:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - name: Cleanup worktree
        run: |
          /worktree-cleanup ${{ github.event.pull_request.head.ref }}
```

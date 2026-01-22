# 创建并行工作树

为并行任务开发创建一个新的Git worktree，实现零冲突的多任务同时进行。

## 用法

```bash
/worktree-create <task-id> <branch-name> [base-branch]
```

## 参数说明

- `task-id`: 任务唯一标识符（建议格式: task-001, feature-auth, bug-123）
- `branch-name`: 新分支名称（将在worktree中创建）
- `base-branch`: 基准分支（可选，默认为当前分支或main）

## 工作流程

### 1. 验证前置条件
```bash
# 检查主分支状态
git status
git fetch origin

# 确保没有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️ 警告: 当前分支有未提交的更改，请先处理"
    exit 1
fi
```

### 2. 创建Worktree目录结构
```bash
# 标准路径结构
BASE_DIR="../worktrees"
WORKTREE_PATH="$BASE_DIR/<task-id>"

# 确保worktrees目录存在
mkdir -p "$BASE_DIR"
```

### 3. 创建Git Worktree
```bash
# 基于指定分支创建worktree
git worktree add "$WORKTREE_PATH" -b "<branch-name>" [base-branch]

# 示例输出:
# Preparing worktree (new branch 'feature-authentication')
# HEAD is now at a1b2c3d Initial commit
```

### 4. 配置Worktree环境
```bash
cd "$WORKTREE_PATH"

# 设置上游分支（便于后续push）
git branch --set-upstream-to=origin/<branch-name> <branch-name>

# 配置worktree特定的git配置（可选）
git config core.worktree "$WORKTREE_PATH"
```

### 5. 记录到任务追踪系统
```yaml
# 追加到 memory/active-worktrees.md
- id: <task-id>
  branch: <branch-name>
  path: <WORKTREE_PATH>
  status: active
  created: <ISO-8601-timestamp>
  base_branch: <base-branch>
  agent: <assigned-agent>
```

### 6. 输出创建信息
```markdown
✅ Worktree创建成功!

📁 路径: <absolute-path>
🌿 分支: <branch-name>
🔗 基于: <base-branch>
🆔 任务ID: <task-id>

🚀 快速开始:
   cd <WORKTREE_PATH>
   # 开始你的并行开发
```

## 使用示例

### 示例1: 创建功能开发worktree
```bash
/worktree-create task-001 feature-authentication main
```

### 示例2: 创建Bug修复worktree
```bash
/worktree-create bug-456 hotfix-memory-leak develop
```

### 示例3: 创建实验性功能worktree
```bash
/worktree-create exp-ai-agent feature-experimental-ai
```

## 命名约定

### Task ID建议格式
- `task-NNN`: 通用任务（task-001, task-002）
- `feature-NAME`: 功能开发（feature-auth, feature-api）
- `bug-NNN`: Bug修复（bug-123, bug-456）
- `exp-NAME`: 实验性功能（exp-refactor, exp-optimization）
- `doc-NAME`: 文档任务（doc-api, doc-guide）

### Branch Name建议格式
- `feature/描述`: 功能分支
- `bugfix/描述`: Bug修复分支
- `hotfix/描述`: 紧急修复分支
- `experiment/描述`: 实验分支
- `refactor/描述`: 重构分支

## 最佳实践

### ✅ 推荐做法
1. **使用语义化命名**: task-id和branch-name要清晰表达任务目的
2. **保持独立性**: 每个worktree处理独立的功能或bug
3. **及时追踪**: 创建后立即记录到active-worktrees.md
4. **设置上游**: 始终配置remote tracking便于协作

### ❌ 避免事项
1. **避免重复ID**: 确保task-id在活动worktrees中唯一
2. **避免嵌套**: 不要在worktree内创建新的worktree
3. **避免共享文件冲突**: 多个worktree不应同时修改同一文件
4. **避免过多worktree**: 建议同时活跃的worktree不超过15个

## 故障排除

### 问题1: 分支已存在
```bash
# 错误: fatal: A branch named 'feature-auth' already exists
# 解决: 使用不同的分支名或删除旧分支
git branch -d feature-auth  # 如果已合并
git branch -D feature-auth  # 强制删除
```

### 问题2: 目录已存在
```bash
# 错误: fatal: '<path>' already exists
# 解决: 清理旧目录或使用不同的task-id
rm -rf ../worktrees/task-001
```

### 问题3: 磁盘空间不足
```bash
# 检查worktrees目录大小
du -sh ../worktrees/*

# 清理不需要的worktrees
/worktree-cleanup <old-task-id>
```

## 与其他命令的集成

- **配合使用**: `/worktree-list` 查看所有活动worktrees
- **任务完成后**: `/worktree-cleanup <task-id>` 清理worktree
- **并行编排**: `/orchestrate` 可以自动创建和管理多个worktrees
- **Swarm模式**: `/swarm` 自动为每个子任务创建独立worktree

## 技术细节

### Git Worktree原理
- Worktree共享.git目录，但有独立的工作区
- 每个worktree有独立的HEAD和index
- 可以同时在不同分支工作，无需切换
- 磁盘占用: 仅工作区文件，不重复.git对象

### 目录结构
```
project/
├── .git/              # 主仓库git目录
├── src/               # 主工作区
└── ../worktrees/      # Worktrees集合目录
    ├── task-001/      # Worktree 1
    ├── task-002/      # Worktree 2
    └── feature-xyz/   # Worktree 3
```

## 安全注意事项

1. **权限检查**: 确保有创建目录和分支的权限
2. **数据备份**: 重要更改应及时commit和push
3. **冲突预防**: 通过task-id和分支隔离避免冲突
4. **清理策略**: 定期清理已合并的worktrees释放空间

## 相关命令

- `/worktree-list` - 列出所有活动worktrees
- `/worktree-cleanup` - 清理指定worktree
- `/orchestrate` - 智能编排多任务（自动创建worktrees）
- `/parallel` - 并行执行多任务
- `/swarm` - 启动Agent群体并行开发

## 性能指标

- 创建时间: < 5秒（取决于仓库大小）
- 磁盘开销: 仅工作区文件大小（约50-200MB）
- 并发上限: 建议≤15个worktrees（基于性能和管理复杂度）
- 清理时间: < 2秒

# 列出并行工作树

列出所有活动的Git worktrees，提供状态概览和管理建议。

## 用法

```bash
/worktree-list [--all] [--format <simple|detailed|json>]
```

## 参数说明

- `--all`: 显示所有worktrees（包括已完成的历史记录）
- `--format`: 输出格式
  - `simple`: 简洁列表（默认）
  - `detailed`: 详细信息
  - `json`: JSON格式（便于脚本处理）

## 输出模式

### 模式1: Simple（简洁模式）
```bash
/worktree-list

📦 活动Worktrees (3个)

🆔 task-001    🌿 feature-auth         ✅ active    👤 coder       📅 2天前
🆔 bug-456     🌿 hotfix-memory-leak   🔧 testing   👤 debugger    📅 5小时前
🆔 exp-ai      🌿 experimental-agent   🔬 research  👤 architect   📅 1周前

💡 提示: 使用 /worktree-list --format detailed 查看更多信息
```

### 模式2: Detailed（详细模式）
```bash
/worktree-list --format detailed

╔═══════════════════════════════════════════════════════════════════════
║ 📦 Worktrees状态报告
║ 生成时间: 2026-01-16 14:30:00
║ 总计: 3个活动 | 5个历史
╚═══════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│ 🆔 Task ID: task-001                                                 │
│ 🌿 Branch: feature-authentication                                    │
│ 📁 Path: G:/worktrees/task-001                                       │
│ 📊 Status: active                                                    │
│ 👤 Agent: coder                                                      │
│ 🔗 Base: main                                                        │
│ 📅 Created: 2026-01-14 09:15:00 (2天前)                            │
│ 📝 Last Commit: Add JWT authentication                              │
│ 🔄 Changes: 12 modified, 3 new files                                │
│ ⚠️ Uncommitted: Yes (3 files)                                       │
│ 🌐 Remote: origin/feature-authentication (up-to-date)               │
│ 💾 Size: 156 MB                                                     │
│                                                                       │
│ 💡 建议: 有未提交更改，请及时提交                                    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ 🆔 Task ID: bug-456                                                  │
│ 🌿 Branch: hotfix-memory-leak                                        │
│ 📁 Path: G:/worktrees/bug-456                                        │
│ 📊 Status: testing                                                   │
│ 👤 Agent: debugger                                                   │
│ 🔗 Base: develop                                                     │
│ 📅 Created: 2026-01-16 09:00:00 (5小时前)                          │
│ 📝 Last Commit: Fix memory leak in event handlers                   │
│ 🔄 Changes: Clean working tree                                      │
│ ⚠️ Uncommitted: No                                                  │
│ 🌐 Remote: origin/hotfix-memory-leak (2 commits ahead)              │
│ 💾 Size: 143 MB                                                     │
│                                                                       │
│ 💡 建议: 已准备好合并，可以创建PR                                    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ 🆔 Task ID: exp-ai                                                   │
│ 🌿 Branch: experimental-agent                                        │
│ 📁 Path: G:/worktrees/exp-ai                                         │
│ 📊 Status: research                                                  │
│ 👤 Agent: architect                                                  │
│ 🔗 Base: main                                                        │
│ 📅 Created: 2026-01-09 11:00:00 (1周前)                            │
│ 📝 Last Commit: Prototype AI agent orchestration                    │
│ 🔄 Changes: 25 modified, 10 new files                               │
│ ⚠️ Uncommitted: Yes (8 files)                                       │
│ 🌐 Remote: Not pushed                                               │
│ 💾 Size: 201 MB                                                     │
│                                                                       │
│ ⚠️ 警告: 已超过7天，考虑合并或清理                                  │
└─────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════
║ 📊 统计摘要
╠═══════════════════════════════════════════════════════════════════════
║ 总磁盘占用: 500 MB
║ 平均年龄: 3.7天
║ 需要注意: 1个 (exp-ai超过7天)
║ 可以清理: 0个
╚═══════════════════════════════════════════════════════════════════════

💡 管理建议:
  • task-001: 提交未完成的更改
  • bug-456: 准备创建PR
  • exp-ai: 考虑合并或清理，已超期
```

### 模式3: JSON（机器可读格式）
```bash
/worktree-list --format json

{
  "timestamp": "2026-01-16T14:30:00Z",
  "summary": {
    "total_active": 3,
    "total_completed": 5,
    "total_disk_usage_mb": 500,
    "average_age_days": 3.7
  },
  "worktrees": [
    {
      "id": "task-001",
      "branch": "feature-authentication",
      "path": "/g/worktrees/task-001",
      "status": "active",
      "agent": "coder",
      "base_branch": "main",
      "created": "2026-01-14T09:15:00Z",
      "age_days": 2,
      "last_commit": "Add JWT authentication",
      "uncommitted_changes": true,
      "uncommitted_files": 3,
      "remote_status": "up-to-date",
      "size_mb": 156,
      "warnings": ["uncommitted_changes"]
    },
    {
      "id": "bug-456",
      "branch": "hotfix-memory-leak",
      "path": "/g/worktrees/bug-456",
      "status": "testing",
      "agent": "debugger",
      "base_branch": "develop",
      "created": "2026-01-16T09:00:00Z",
      "age_days": 0.2,
      "last_commit": "Fix memory leak in event handlers",
      "uncommitted_changes": false,
      "uncommitted_files": 0,
      "remote_status": "ahead_by_2",
      "size_mb": 143,
      "suggestions": ["ready_for_pr"]
    },
    {
      "id": "exp-ai",
      "branch": "experimental-agent",
      "path": "/g/worktrees/exp-ai",
      "status": "research",
      "agent": "architect",
      "base_branch": "main",
      "created": "2026-01-09T11:00:00Z",
      "age_days": 7,
      "last_commit": "Prototype AI agent orchestration",
      "uncommitted_changes": true,
      "uncommitted_files": 8,
      "remote_status": "not_pushed",
      "size_mb": 201,
      "warnings": ["overdue", "not_pushed"]
    }
  ]
}
```

## 数据来源

### 主要来源
1. **memory/active-worktrees.md**: 任务追踪元数据
2. **git worktree list**: Git原生worktree状态
3. **git status**: 工作区更改状态
4. **git log**: 最后提交信息
5. **du**: 磁盘使用情况

### 数据获取流程
```bash
# 1. 读取追踪文件
cat memory/active-worktrees.md

# 2. 获取Git worktree列表
git worktree list --porcelain

# 3. 对每个worktree执行详细检查
for worktree in $(git worktree list --porcelain | grep "worktree" | awk '{print $2}'); do
    cd "$worktree"

    # 检查状态
    git status --porcelain

    # 获取最后提交
    git log -1 --format="%s"

    # 检查远程状态
    git fetch origin
    git status --branch --porcelain=v2

    # 计算大小
    du -sh .
done

# 4. 合并数据并格式化输出
```

## 状态指示器

### 任务状态 (status)
- `active` ✅: 正在活跃开发
- `testing` 🔧: 开发完成，测试中
- `review` 👀: 代码审查中
- `blocked` 🚫: 被阻塞
- `research` 🔬: 研究/实验阶段
- `completed` ✓: 已完成（历史记录）

### 健康指标
- 🟢 健康: 一切正常
- 🟡 注意: 有小问题（如未提交更改）
- 🔴 警告: 有严重问题（如超期、冲突）

### 警告类型
- `uncommitted_changes`: 有未提交的更改
- `overdue`: 创建超过7天
- `not_pushed`: 有未推送的提交
- `conflicts`: 有合并冲突
- `large_size`: 磁盘占用过大（>300MB）

## 过滤和排序

### 按状态过滤
```bash
# 仅显示活跃的
/worktree-list --status active

# 显示需要注意的
/worktree-list --warnings-only
```

### 按时间排序
```bash
# 按创建时间排序（最新的在前）
/worktree-list --sort newest

# 按年龄排序（最旧的在前）
/worktree-list --sort oldest
```

### 按Agent过滤
```bash
# 显示特定Agent的worktrees
/worktree-list --agent coder
```

## 使用示例

### 示例1: 快速查看
```bash
/worktree-list
# 获取简洁概览
```

### 示例2: 详细审查
```bash
/worktree-list --format detailed
# 深入了解每个worktree状态
```

### 示例3: 导出JSON用于脚本
```bash
/worktree-list --format json > worktrees.json
# 用于自动化脚本处理
```

### 示例4: 查看历史记录
```bash
/worktree-list --all
# 包括已完成的worktrees
```

## 健康检查报告

自动识别需要注意的情况：

### 🟢 健康 (Green)
- 无未提交更改
- 与远程同步
- 年龄<7天
- 磁盘占用正常

### 🟡 注意 (Yellow)
- 有未提交更改
- 有未推送的提交
- 年龄7-14天
- 磁盘占用较大（200-300MB）

### 🔴 警告 (Red)
- 年龄>14天
- 有合并冲突
- 磁盘占用>300MB
- 远程分支已删除

## 智能建议

系统会根据状态提供自动建议：

| 条件 | 建议 |
|------|------|
| 无未提交更改 + 已推送 | "准备创建PR" |
| 有未提交更改 | "请及时提交" |
| 未推送 | "推送到远程备份" |
| 年龄>7天 | "考虑合并或清理" |
| 已合并到main | "可以安全清理" |
| 有冲突 | "需要解决冲突" |

## 与其他命令集成

### 配合cleanup使用
```bash
# 1. 列出所有worktrees
/worktree-list --format detailed

# 2. 识别可以清理的
# （系统会标记"可以清理"）

# 3. 清理已完成的
/worktree-cleanup task-001
```

### 配合orchestrate使用
```bash
# Orchestrator可以查询worktree状态
# 自动分配新任务到空闲worktree或创建新的
```

## 性能优化

- **缓存机制**: 5分钟内重复调用使用缓存
- **并行检查**: 同时检查多个worktrees状态
- **增量更新**: 只检查变化的worktrees
- **轻量模式**: simple格式只读取必要信息

## 故障排除

### 问题1: 数据不同步
```bash
# 如果git worktree list和active-worktrees.md不一致

# 1. 运行修复命令
git worktree prune  # 清理过期引用

# 2. 同步追踪文件
/worktree-sync  # 将Git状态同步到追踪文件
```

### 问题2: 显示过时数据
```bash
# 清除缓存
/worktree-list --no-cache

# 或等待5分钟缓存过期
```

### 问题3: 无法访问某些worktree
```bash
# 如果worktree目录被移动或删除

# 清理过期引用
git worktree prune

# 更新追踪文件
```

## 自动化脚本示例

### Bash脚本: 每日健康检查
```bash
#!/bin/bash
# daily-worktree-health-check.sh

REPORT=$(/worktree-list --format json)
WARNINGS=$(echo "$REPORT" | jq '[.worktrees[].warnings] | flatten | length')

if [ "$WARNINGS" -gt 0 ]; then
    echo "⚠️ 发现 $WARNINGS 个问题需要注意"
    echo "$REPORT" | jq '.worktrees[] | select(.warnings | length > 0)'

    # 发送通知
    notify-send "Worktree健康检查" "发现 $WARNINGS 个问题"
fi
```

### Python脚本: 自动清理
```python
#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime, timedelta

# 获取worktree列表
result = subprocess.run(['worktree-list', '--format', 'json'],
                       capture_output=True, text=True)
worktrees = json.loads(result.stdout)

# 找出超过14天且已合并的worktrees
now = datetime.now()
for wt in worktrees['worktrees']:
    created = datetime.fromisoformat(wt['created'])
    age = (now - created).days

    if age > 14 and wt.get('merged', False):
        print(f"清理过期worktree: {wt['id']}")
        subprocess.run(['worktree-cleanup', wt['id']])
```

## 相关命令

- `/worktree-create` - 创建新worktree
- `/worktree-cleanup` - 清理worktree
- `/orchestrate` - 智能管理worktrees
- `git worktree list` - Git原生命令
- `git worktree prune` - 清理过期引用

## 最佳实践

1. **定期检查**: 每天运行一次查看状态
2. **及时清理**: 发现可清理的立即处理
3. **监控健康**: 关注警告指标
4. **导出数据**: 定期导出JSON用于分析
5. **自动化**: 配置定时任务自动检查

## 输出示例（真实场景）

```bash
$ /worktree-list

📦 活动Worktrees (5个) | 🔴 1个需要注意

🆔 feature-api      🌿 feature-api-redesign    ✅ active    👤 coder        📅 1天前   🟢
🆔 bug-789          🌿 hotfix-validation       🔧 testing   👤 debugger     📅 3小时前 🟢
🆔 refactor-core    🌿 refactor-architecture   🔬 research  👤 architect    📅 10天前  🔴
🆔 doc-update       🌿 update-api-docs         ✅ active    👤 coder        📅 2天前   🟡
🆔 perf-optimize    🌿 optimize-db-queries     👀 review    👤 specialist   📅 1天前   🟢

💡 快速操作:
   • refactor-core: ⚠️ 已超期10天，建议处理
   • doc-update: 有3个未提交文件

📊 总览: 500MB磁盘占用 | 平均年龄3.4天
```

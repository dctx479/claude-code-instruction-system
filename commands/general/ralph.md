# /ralph - 自主循环执行命令

> **Ralph Loop**: 让 Claude 自主执行任务直到完成，无需持续人工干预

## 概述

`/ralph` 命令启动自主循环执行模式，Claude 会自动继续执行任务直到:
1. 任务完成
2. 遇到需要人工确认的决策
3. 达到最大迭代次数
4. 遇到致命错误

## 命名由来

"Ralph" 取自 **R**un **A**utonomously **L**oop **P**ersistently **H**ook 的首字母缩写，
也是对自主执行能力的友好称呼。

## 用法

### 基本用法

```bash
# 启动 Ralph 循环执行
/ralph <任务描述>

# 示例
/ralph "完成用户认证模块的所有待办事项"
/ralph "修复所有 lint 错误并提交代码"
/ralph "将项目迁移到 TypeScript"
```

### 高级选项

```bash
# 设置最大迭代次数
/ralph --max-iterations 20 <任务描述>

# 设置检查点（每N次迭代保存进度）
/ralph --checkpoint-interval 3 <任务描述>

# 安静模式（减少输出）
/ralph --quiet <任务描述>

# 强制重新开始（忽略之前的状态）
/ralph --restart <任务描述>
```

### 控制命令

```bash
# 查看当前状态
/ralph status

# 暂停执行
/ralph pause

# 恢复执行
/ralph resume

# 停止执行
/ralph stop

# 查看执行历史
/ralph history
```

## 工作原理

```
用户: /ralph "完成待办事项"
        │
        ▼
┌─────────────────────────┐
│   初始化 Ralph State    │
│   - 设置任务描述        │
│   - 重置迭代计数        │
│   - 激活循环模式        │
└─────────────┬───────────┘
              │
              ▼
┌─────────────────────────┐
│     执行任务迭代        │◄────────────┐
│   - 分析当前状态        │             │
│   - 执行下一步操作      │             │
│   - 更新进度            │             │
└─────────────┬───────────┘             │
              │                         │
              ▼                         │
        ┌───────────┐                   │
        │ 任务完成? │                   │
        └─────┬─────┘                   │
              │                         │
         NO   │   YES                   │
              │                         │
    ┌─────────┴─────────┐               │
    │                   │               │
    ▼                   ▼               │
┌────────┐        ┌──────────┐          │
│ 需确认?│        │  完成!   │          │
└────┬───┘        └──────────┘          │
     │                                  │
 NO  │  YES                             │
     │                                  │
     │   ┌─────────────┐                │
     │   │ 请求人工确认 │                │
     │   └─────────────┘                │
     │                                  │
     └──────────────────────────────────┘
              │
              ▼
        ┌───────────┐
        │ Stop Hook │
        │ 拦截检查   │
        └─────┬─────┘
              │
              ▼
        ┌───────────┐
        │ 继续/停止 │
        └───────────┘
```

## 状态文件

Ralph 使用 `memory/ralph-state.json` 跟踪执行状态:

```json
{
  "active": true,
  "iteration": 3,
  "max_iterations": 10,
  "completed": false,
  "fatal_error": false,
  "current_task": "user-auth-todos",
  "task_description": "完成用户认证模块的所有待办事项",
  "started_at": "2026-01-23T10:00:00Z",
  "last_updated": "2026-01-23T10:15:00Z",
  "checkpoints": [
    {
      "iteration": 1,
      "timestamp": "2026-01-23T10:05:00Z",
      "summary": "完成了登录功能"
    }
  ],
  "errors": [],
  "metrics": {
    "total_runs": 5,
    "successful_runs": 4,
    "failed_runs": 1,
    "total_iterations": 23
  }
}
```

## 安全机制

### 1. 迭代限制
默认最多执行 10 次迭代，防止无限循环。

### 2. 致命错误检测
遇到以下情况会自动停止:
- 编译错误
- 运行时崩溃
- 安全警告
- 资源耗尽

### 3. 确认请求
以下操作需要人工确认:
- 删除文件或数据
- 修改生产配置
- 引入新依赖
- 数据库 Schema 变更

### 4. 检查点恢复
定期保存进度，允许从中断处恢复。

## 示例场景

### 场景 1: 代码迁移

```bash
/ralph "将所有 .js 文件迁移到 TypeScript"

# Ralph 会自动:
# 1. 扫描所有 .js 文件
# 2. 逐个转换为 .ts
# 3. 修复类型错误
# 4. 运行测试验证
# 5. 循环直到全部完成
```

### 场景 2: Bug 修复

```bash
/ralph "修复所有 GitHub issues 中标记为 bug 的问题"

# Ralph 会自动:
# 1. 获取 bug 列表
# 2. 分析每个 bug
# 3. 实现修复
# 4. 编写测试
# 5. 提交代码
# 6. 循环直到全部修复
```

### 场景 3: 测试覆盖

```bash
/ralph "为所有未覆盖的函数编写单元测试"

# Ralph 会自动:
# 1. 运行覆盖率分析
# 2. 识别未覆盖函数
# 3. 生成测试用例
# 4. 运行测试
# 5. 循环直到覆盖率达标
```

## 与其他功能集成

### 与 HUD 集成
Ralph 执行状态会显示在 HUD 状态栏中。

### 与 Intent Detector 集成
Ralph 使用意图检测来理解任务完成条件。

### 与 Plan-Scoped Memory 集成
Ralph 的每次执行会创建独立的计划记忆空间。

## 最佳实践

1. **明确任务描述**: 越具体越好
2. **设置合理的迭代限制**: 复杂任务可增加
3. **使用检查点**: 长时间任务建议开启
4. **监控执行**: 通过 `/ralph status` 跟踪进度

## 故障排除

### Ralph 卡住
```bash
/ralph status  # 查看状态
/ralph stop    # 强制停止
```

### 意外停止
检查 `memory/ralph-state.json` 中的错误信息。

### 恢复执行
```bash
/ralph resume  # 从最后检查点恢复
```

## 相关文档

- `hooks/ralph-stop-interceptor.sh` - Stop Hook 实现
- `memory/ralph-state.json` - 状态文件
- `workflows/execution/ralph-manager.md` - 详细工作流

# Plan-Scoped Memory 工作流

> 计划级知识隔离系统 - 为每个开发计划创建独立的知识空间

## 概述

Plan-Scoped Memory 为每个开发任务/计划创建独立的知识上下文，避免不同任务之间的信息污染，提高上下文质量和相关性。

## 设计理念

```
传统模式:
┌─────────────────────────────────┐
│      全局上下文 (Global)         │
│  所有任务共享同一知识空间        │
│  - 信息污染                     │
│  - 上下文膨胀                   │
│  - 相关性降低                   │
└─────────────────────────────────┘

Plan-Scoped 模式:
┌─────────────────────────────────┐
│           Global Base           │
│     (项目配置、核心约束)        │
├─────────┬─────────┬─────────────┤
│ Plan A  │ Plan B  │  Plan C     │
│ 认证功能 │ API重构 │  性能优化   │
│ (隔离)  │ (隔离)  │  (隔离)     │
└─────────┴─────────┴─────────────┘
```

## 架构

```
.claude/context/
├── index.json              # 全局索引
├── resolutions/            # 全局问题解决方案
└── plans/                  # 计划级记忆
    ├── index.json          # 计划索引
    ├── plan-001/           # 计划 A
    │   ├── context.json    # 计划上下文
    │   ├── decisions.json  # 技术决策
    │   ├── progress.json   # 进度追踪
    │   └── learnings.json  # 学习沉淀
    ├── plan-002/           # 计划 B
    │   └── ...
    └── plan-003/           # 计划 C
        └── ...
```

## 核心组件

### 1. Plan Context (计划上下文)

```json
{
  "plan_id": "plan-001",
  "name": "用户认证系统",
  "description": "实现完整的用户认证功能",
  "created_at": "2026-01-23T10:00:00Z",
  "status": "active",
  "scope": {
    "files": ["src/auth/*", "src/middleware/auth.ts"],
    "modules": ["authentication", "authorization"],
    "dependencies": ["bcrypt", "jsonwebtoken"]
  },
  "goals": [
    "实现用户注册和登录",
    "支持 JWT 令牌认证",
    "实现密码重置流程"
  ],
  "constraints": [
    "必须支持 OAuth 2.0",
    "密码必须使用 bcrypt 加密",
    "Token 有效期 24 小时"
  ]
}
```

### 2. Technical Decisions (技术决策)

```json
{
  "plan_id": "plan-001",
  "decisions": [
    {
      "id": "dec-001",
      "timestamp": "2026-01-23T10:30:00Z",
      "topic": "密码存储方案",
      "context": "需要选择密码加密算法",
      "options": [
        {"name": "bcrypt", "pros": ["安全", "自动盐"], "cons": ["较慢"]},
        {"name": "argon2", "pros": ["更安全"], "cons": ["需要额外依赖"]}
      ],
      "decision": "bcrypt",
      "rationale": "已是项目依赖，性能可接受",
      "decided_by": "architect"
    }
  ]
}
```

### 3. Progress Tracking (进度追踪)

```json
{
  "plan_id": "plan-001",
  "total_tasks": 10,
  "completed_tasks": 4,
  "progress_percentage": 40,
  "milestones": [
    {
      "name": "基础认证",
      "status": "completed",
      "completed_at": "2026-01-23T12:00:00Z"
    },
    {
      "name": "OAuth 集成",
      "status": "in_progress",
      "estimated_completion": "2026-01-24T18:00:00Z"
    }
  ],
  "blockers": [],
  "next_steps": [
    "实现 Google OAuth",
    "添加 refresh token 机制"
  ]
}
```

### 4. Learnings (学习沉淀)

```json
{
  "plan_id": "plan-001",
  "learnings": [
    {
      "id": "learn-001",
      "timestamp": "2026-01-23T11:00:00Z",
      "type": "best_practice",
      "topic": "JWT 密钥管理",
      "content": "JWT 密钥应该从环境变量读取，不要硬编码",
      "source": "实现过程中发现安全问题"
    },
    {
      "id": "learn-002",
      "type": "gotcha",
      "topic": "bcrypt 异步",
      "content": "bcrypt.compare 是异步的，需要 await",
      "source": "调试登录功能时发现"
    }
  ]
}
```

## 工作流程

### 创建新计划

```bash
/plan create "用户认证系统" --scope "src/auth/*"
```

执行流程:
1. 生成唯一计划 ID
2. 创建计划目录和初始文件
3. 设置为活动计划
4. 加载计划上下文到会话

### 切换计划

```bash
/plan switch plan-002
```

执行流程:
1. 保存当前计划状态
2. 卸载当前计划上下文
3. 加载目标计划上下文
4. 恢复计划进度

### 归档计划

```bash
/plan archive plan-001
```

执行流程:
1. 保存最终状态
2. 生成计划总结
3. 提取可复用经验
4. 移动到归档目录

## 上下文注入策略

### 启动时

```
1. 读取 .claude/context/index.json (全局)
2. 检查是否有活动计划
3. 如有活动计划:
   - 加载 plans/{plan_id}/context.json
   - 加载 plans/{plan_id}/decisions.json (最近5条)
   - 加载 plans/{plan_id}/learnings.json (最近5条)
4. 设置上下文边界
```

### 执行时

```
1. 检查操作是否在计划范围内
2. 如果是:
   - 仅使用计划级上下文
   - 记录决策和学习
3. 如果不是:
   - 使用全局上下文
   - 提醒可能需要切换计划
```

### 完成时

```
1. 更新进度追踪
2. 保存新的学习
3. 同步到全局 (可选)
```

## 与其他系统集成

### 与 Context Archivist 集成

```
Context Archivist 负责:
- 在 /compact 前保存计划状态
- 提取计划级的问题解决方案
- 同步学习到全局

Plan-Scoped Memory 负责:
- 维护计划级知识
- 提供隔离的上下文
- 追踪计划进度
```

### 与 Ralph 集成

```
Ralph 循环执行时:
- 使用当前计划的上下文
- 更新计划进度
- 记录循环中的学习
```

### 与 Intent Detector 集成

```
Intent Detector 可以:
- 识别跨计划操作
- 建议切换到相关计划
- 防止意外的上下文污染
```

## 命令参考

```bash
# 计划管理
/plan create <name> [--scope <pattern>]  # 创建计划
/plan list                               # 列出所有计划
/plan switch <plan_id>                   # 切换计划
/plan status                             # 查看当前计划
/plan archive <plan_id>                  # 归档计划

# 决策管理
/plan decision add <topic>               # 记录决策
/plan decision list                      # 列出决策
/plan decision export                    # 导出决策文档

# 学习管理
/plan learn <content>                    # 记录学习
/plan learnings                          # 查看学习
/plan learnings sync                     # 同步到全局

# 进度管理
/plan progress                           # 查看进度
/plan milestone add <name>               # 添加里程碑
/plan milestone complete <name>          # 完成里程碑
```

## 最佳实践

### 1. 合理划分计划

```
好的计划划分:
- 用户认证 (独立功能)
- 订单管理 (独立功能)
- 性能优化 (独立目标)

不好的划分:
- 所有功能 (太大)
- 修复一个 bug (太小)
```

### 2. 及时记录决策

```
每个重要决策都应记录:
- 为什么选择这个方案?
- 考虑了哪些替代方案?
- 有什么权衡?
```

### 3. 沉淀学习

```
遇到以下情况要记录:
- 发现的坑
- 最佳实践
- 调试技巧
- 性能优化方法
```

### 4. 定期同步

```
计划完成后:
- 提取通用经验
- 同步到全局知识库
- 更新项目文档
```

## 配置选项

```json
{
  "plan_scoped_memory": {
    "enabled": true,
    "auto_create": false,
    "max_active_plans": 5,
    "context_injection": {
      "max_decisions": 5,
      "max_learnings": 5,
      "include_progress": true
    },
    "auto_sync": {
      "enabled": true,
      "interval": "on_milestone"
    },
    "archive": {
      "retention_days": 90,
      "compress": true
    }
  }
}
```

## 相关文档

- Context Archivist: `agents/context-archivist.md`
- 上下文归档: `docs/context-archival-guide.md`
- Ralph Manager: `workflows/ralph-manager.md`

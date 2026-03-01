# /autopilot - 全自主执行命令

> 端到端任务自动执行，从需求到交付全程自动化

## 概述

`/autopilot` 命令启动全自主执行模式，整合 Ralph Loop、Orchestrator 和 QA 系统，实现完整的开发周期自动化：

```
需求输入 → 规划 → 规范 → 开发 → 测试 → 交付
```

## 用法

### 基本用法

```bash
# 启动 autopilot
/autopilot "任务描述"

# 示例
/autopilot "开发用户认证系统，包含登录、注册、密码重置"
/autopilot "重构订单模块，提高性能 50%"
/autopilot "添加 GraphQL API 支持"
```

### 模式选择

```bash
# 完全自主模式 - 最少人工干预
/autopilot full "任务描述"

# 监督模式 - 每阶段审核
/autopilot supervised "任务描述"

# 步进模式 - 每步确认
/autopilot step "任务描述"
```

### 控制命令

```bash
/autopilot status          # 查看当前状态
/autopilot pause           # 暂停执行
/autopilot resume          # 恢复执行
/autopilot skip            # 跳过当前子任务
/autopilot rollback        # 回滚到上个检查点
/autopilot abort           # 终止执行
/autopilot history         # 查看执行历史
```

### 高级选项

```bash
# 跳过规范阶段（已有规范时）
/autopilot "任务" --skip-spec

# 跳过 QA 阶段（快速原型）
/autopilot "任务" --skip-qa

# 设置最大执行时间
/autopilot "任务" --timeout 4h

# 设置成本限制
/autopilot "任务" --max-cost $10

# 指定输出目录
/autopilot "任务" --output ./features/auth

# 使用特定规范文件
/autopilot "任务" --spec specs/SPEC-auth.md
```

## 执行流程

```
┌─────────────────────────────────────────────────────────────┐
│                      Autopilot Flow                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [1] Planning ──────────────────────────────────────►       │
│      ├── 意图识别                                           │
│      ├── 任务分解                                           │
│      ├── 策略选择                                           │
│      └── 资源分配                                           │
│                                                             │
│  [2] Specification ─────────────────────────────────►       │
│      ├── 功能规范 (spec-writer)                             │
│      ├── 技术设计 (architect)                               │
│      └── [审核点] (supervised/step 模式)                    │
│                                                             │
│  [3] Development ───────────────────────────────────►       │
│      ├── Ralph Loop 循环执行                                │
│      │   ├── Model Router 模型选择                          │
│      │   ├── 代码实现                                       │
│      │   └── 检查点保存                                     │
│      └── Plan-Scoped Memory 知识沉淀                        │
│                                                             │
│  [4] QA ────────────────────────────────────────────►       │
│      ├── qa-reviewer 代码审查                               │
│      ├── automated-testing 测试验证                         │
│      └── qa-fixer P2问题修复                                │
│          └── [循环直到通过]                                 │
│                                                             │
│  [5] Delivery ──────────────────────────────────────►       │
│      ├── 文档生成                                           │
│      ├── 变更记录                                           │
│      └── 发布准备                                           │
│                                                             │
│  [完成] ✓                                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 状态显示

执行过程中会显示实时状态：

```
╔═══════════════════════════════════════════════════════════════╗
║  AUTOPILOT: 开发用户认证系统                                   ║
╠═══════════════════════════════════════════════════════════════╣
║  模式: supervised                                              ║
║  阶段: [✓] Plan [✓] Spec [▶] Dev [ ] QA [ ] Deliver           ║
║                                                                ║
║  当前任务: 实现登录功能                                        ║
║  进度: [██████████░░░░░░░░░░] 50% (5/10 子任务)                ║
║                                                                ║
║  Ralph: 迭代 3/10 | 模型: Sonnet | Token: 45K                  ║
║  时间: 1h 15m | 预计剩余: 1h 30m                               ║
╚═══════════════════════════════════════════════════════════════╝
```

## 中断点处理

### 必须确认的操作

当遇到以下操作时，autopilot 会暂停并请求确认：

```
⚠️  AUTOPILOT PAUSED - 需要确认

检测到敏感操作：
  - 类型: 数据库 Schema 变更
  - 文件: migrations/002_add_auth_tables.sql
  - 影响: 添加 users, sessions, tokens 表

操作内容预览:
  CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    ...
  );

选项:
  [y] 确认执行
  [n] 跳过此操作
  [e] 编辑后执行
  [a] 终止 autopilot
```

### 阶段审核 (supervised 模式)

```
═══════════════════════════════════════════════════════════════
  PHASE REVIEW: Specification 阶段完成

  生成的文件:
    - specs/SPEC-user-auth.md

  技术方案摘要:
    - 架构: 分层架构 (Controller → Service → Repository)
    - 认证: JWT + Refresh Token
    - 存储: PostgreSQL + Redis (session cache)

  预计开发时间: 2-3 小时
  涉及文件: 15 个

  [c] 继续下一阶段
  [r] 查看详细规范
  [m] 修改规范
  [a] 终止 autopilot
═══════════════════════════════════════════════════════════════
```

## 模式对比

| 特性 | Full | Supervised | Step |
|------|------|------------|------|
| 规划阶段 | 自动 | 自动 | 确认 |
| 规范审核 | 跳过 | 确认 | 确认 |
| 架构审核 | 跳过 | 确认 | 确认 |
| 开发执行 | 自动 | 自动 | 每步确认 |
| QA 修复 | 自动 | 自动 | 确认 |
| 敏感操作 | 确认 | 确认 | 确认 |
| 适用场景 | 低风险 | 中风险 | 高风险 |

## 输出文件

Autopilot 执行完成后生成以下文件：

```
.autopilot/
├── session-20260123-001/
│   ├── plan.json           # 执行计划
│   ├── spec.md             # 功能规范
│   ├── design.md           # 技术设计
│   ├── progress.json       # 进度记录
│   ├── qa-report.md        # QA 报告
│   ├── fix-report.md       # 修复报告
│   ├── metrics.json        # 性能指标
│   └── lessons.md          # 经验总结
```

## 示例场景

### 场景 1: 功能开发

```bash
/autopilot supervised "开发商品搜索功能，支持关键词、分类、价格范围筛选"

# Autopilot 自动执行:
# 1. 分析需求，分解为 5 个子任务
# 2. 生成功能规范，请求审核
# 3. 设计技术方案（Elasticsearch + Redis 缓存）
# 4. 使用 Ralph Loop 实现代码
# 5. QA 审查，自动修复 3 个 P2 问题
# 6. 生成 API 文档和变更记录
```

### 场景 2: 重构

```bash
/autopilot step "重构支付模块，从同步改为异步处理"

# Autopilot 在每步暂停确认:
# 1. [确认] 分析现有代码结构
# 2. [确认] 设计异步架构
# 3. [确认] 创建消息队列配置
# 4. [确认] 修改订单服务
# 5. [确认] 修改支付网关接口
# 6. [确认] 更新测试用例
```

### 场景 3: 快速原型

```bash
/autopilot full "创建一个简单的待办事项 API" --skip-qa

# Autopilot 快速执行:
# 1. 自动规划和设计
# 2. 快速实现 CRUD 接口
# 3. 跳过 QA（快速原型）
# 4. 生成基本文档
# 耗时: 约 30 分钟
```

## 成本控制

### 设置成本限制

```bash
/autopilot "任务" --max-cost $5
```

### 成本估算

在开始前，autopilot 会估算成本：

```
成本估算:
  - 规划阶段: ~$0.50 (Opus)
  - 规范阶段: ~$1.00 (Opus + Sonnet)
  - 开发阶段: ~$3.00 (Sonnet + Haiku)
  - QA 阶段: ~$0.50 (Sonnet)
  总计: ~$5.00

是否继续? [y/n]
```

## 故障恢复

### 从检查点恢复

```bash
/autopilot resume --session ap-20260123-001
```

### 回滚到上个检查点

```bash
/autopilot rollback
```

### 查看失败原因

```bash
/autopilot status --verbose
```

## 配置选项

在 `config/autopilot.json` 中配置默认行为：

```json
{
  "default_mode": "supervised",
  "timeouts": {
    "planning": "5m",
    "specification": "15m",
    "development": "4h",
    "qa": "30m",
    "delivery": "10m"
  },
  "checkpoints": {
    "enabled": true,
    "interval": 3
  },
  "notifications": {
    "on_phase_complete": true,
    "on_intervention_needed": true
  },
  "limits": {
    "max_cost": 20,
    "max_iterations": 50,
    "max_retries": 3
  }
}
```

## 相关文档

- Agent 定义: `agents/ops/autopilot-orchestrator.md`
- 工作流: `workflows/execution/autopilot-flow.md`
- Ralph Loop: `commands/general/ralph.md`
- QA 系统: `QA-SYSTEM.md`
- 编排模式: `workflows/orchestration/orchestration-patterns.md`

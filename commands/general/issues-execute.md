# /issues-execute - Issues 闭环执行命令

> 以 Issues CSV 文件为唯一数据源，逐条执行每个 Issue，通过开发→审核→提交的闭环流程
> 确保任务完整交付，支持断点续传和阻塞处理。

## 概述

`/issues-execute` 命令将 Issues CSV（由 `/plan-to-issues` 生成）作为单一真相来源（SSOT），
按优先级和阶段顺序自动执行每个 Issue，每个 Issue 完成后立即更新 CSV 状态。

## 用法

```bash
# 基本用法（自动读取最新 issues/*.csv）
/issues-execute

# 指定 Issues 文件
/issues-execute issues/2026-03-01_10-30-00-user-auth.csv

# 从指定 Issue 开始（断点续传）
/issues-execute --from P2-003

# 仅执行指定阶段
/issues-execute --phase 2

# 仅执行指定优先级
/issues-execute --priority P0,P1

# 预演模式（不实际执行，只展示计划）
/issues-execute --dry-run

# 跳过审核（快速模式，仅用于非关键任务）
/issues-execute --skip-review
```

## 核心原则

### 单一数据源 (SSOT)

CSV 文件是唯一权威：
- 每次执行前读取 CSV 最新状态
- 每个 Issue 完成后**立即**更新 CSV
- 不在内存中维护状态，断电重启可续传
- `dev_state=DONE` 的 Issue 自动跳过

### 闭环执行模型

```
读取 Issue
    ↓
上下文收集 (context_gathering)
    ↓
实现开发 (implement)
    ↓
初次审核 (review_initial) ←── 如失败：返回 implement
    ↓
回归审核 (review_regression) ←── 如失败：返回 implement
    ↓
Git 提交 (git_commit) ←── 与 CSV 更新同一个提交
    ↓
标记 DONE，继续下一个 Issue
```

## 执行流程详解

### Step 1: 初始化

```markdown
1. 读取 CSV 文件（UTF-8 BOM 解码）
2. 过滤待执行 Issues（dev_state ≠ DONE）
3. 按优先级排序：P0 → P1 → P2 → P3
4. 同一优先级内按 id 排序
5. 输出执行计划摘要
```

### Step 2: 单 Issue 执行循环

#### 2.1 上下文收集 (context_gathering)

```markdown
目标：充分理解 Issue 后再动手

1. 读取 refs 中列出的相关文件
2. 检查 acceptance_criteria 的可验证性
3. 识别与其他 Issue 的依赖关系
4. 评估实现复杂度（简单/中等/复杂）
5. 如有 BLOCKED 依赖 → 跳过，设置 dev_state=BLOCKED
```

#### 2.2 实现开发 (implement)

```markdown
目标：完成 Issue 描述的功能

规则：
- 遵循项目代码规范（TypeScript strict, ESM, etc.）
- 每次只修改与当前 Issue 相关的文件
- 不引入与 Issue 无关的改动（避免 scope creep）
- 必须满足所有 acceptance_criteria

更新 CSV：dev_state → DOING
```

#### 2.3 初次审核 (review_initial)

```markdown
目标：验证实现是否满足验收标准

检查清单（对照 review_initial_requirements）：
□ 所有 acceptance_criteria 已满足
□ 代码无明显 bug 或安全问题
□ 无未处理的边界情况
□ 无不必要的依赖引入

结果：
- PASS → 进入回归审核
- FAIL → 返回 implement（最多重试 3 次）
         超过 3 次 → dev_state=BLOCKED，notes 记录原因

更新 CSV：review_initial_state → PASS/FAIL
```

#### 2.4 回归审核 (review_regression)

```markdown
目标：确保当前变更不破坏已有功能

检查清单（对照 review_regression_requirements）：
□ 现有测试仍然通过
□ 关联模块的接口未发生破坏性变更
□ 数据库 Schema 变更已有迁移脚本
□ 环境变量变更已更新 .env.example

结果：
- PASS → 进入 Git 提交
- FAIL → 返回 implement

更新 CSV：review_regression_state → PASS/FAIL
```

#### 2.5 Git 提交 (git_commit)

```markdown
目标：将 Issue 变更（含 CSV 更新）一起提交

提交步骤：
1. 更新 CSV：dev_state=DONE, git_state=COMMITTED
2. git add <修改的文件> <CSV文件>
3. git commit -m "<type>(<area>): <title>

Issue: <id>
Phase: <phase>

<description简短版>

Acceptance:
- <criteria 1>
- <criteria 2>"

4. 将 commit hash 写入 CSV git_state 字段
   格式：COMMITTED:<hash>

注意：CSV 文件必须在同一个 commit 中
```

### Step 3: 阻塞处理

```markdown
当 Issue 被阻塞时：
1. 设置 dev_state=BLOCKED
2. 在 notes 字段记录阻塞原因和依赖的 Issue ID
3. 跳过当前 Issue，继续下一个
4. 阻塞的 Issue 在依赖项完成后可以续传

阻塞原因示例：
- "BLOCKED: 依赖 P1-003 完成数据库 Schema"
- "BLOCKED: 需要用户确认 API 设计方案"
- "BLOCKED: 第三方 API 未就绪"
```

### Step 4: 进度报告

每完成 5 个 Issue 或每隔 30 分钟，输出进度报告：

```markdown
## 执行进度报告

### 总体进度
[████████░░] 8/10 (80%)

### 状态分布
- ✅ DONE: 8
- 🔄 DOING: 1
- ⏸ BLOCKED: 1
- ⬜ TODO: 0

### 阻塞项
- P2-003: 依赖 P1-005 的数据库 Schema

### 最近完成
- [10:45] P2-001 实现 /auth/login 端点 ✅
- [10:52] P2-002 实现 /auth/logout 端点 ✅
- [11:03] P2-004 实现 JWT refresh 机制 ✅
```

## 与其他系统的集成

### 与 Ralph Loop 集成

`/issues-execute` 是对 `/ralph` 的专业化扩展，针对 CSV 驱动的任务管理场景：

```markdown
/ralph 适合：          /issues-execute 适合：
- 开放式任务           - 已结构化的 Issues
- 模糊的完成条件       - 明确的 acceptance_criteria
- 单一连续任务         - 多个有序 Issues
- 无状态持久化需求     - 需要断点续传
```

### 与 QA 系统集成

`review_initial` 和 `review_regression` 阶段内部调用 QA 能力：

```markdown
review_initial_requirements 对应 qa-reviewer 的检查维度
review_regression_requirements 对应 qa-reviewer 的回归检查

如果项目有 spec-first 规范，自动加载对应 SPEC-*.md 进行验收对比
```

### 与 Autopilot 集成

在 Autopilot 的 Development 阶段，`/issues-execute` 作为核心执行引擎：

```markdown
## Autopilot Development 阶段

1. Plan → spec-writer 生成规范
2. 规范 → /plan-to-issues 生成 Issues
3. Issues → /issues-execute 闭环执行
4. 完成 → QA 阶段自动触发
```

## 续传机制

当执行中断（网络断开/上下文压缩/用户取消）时：

```bash
# 查看当前状态
cat issues/2026-03-01_10-30-00-user-auth.csv | grep -v "DONE"

# 从上次中断处继续
/issues-execute --from P2-003  # 从指定 Issue 开始
/issues-execute                # 自动跳过 DONE，从第一个非 DONE 开始
```

## 安全控制

### 需要用户确认的操作

以下操作会暂停并请求确认：
- 删除文件（`rm` 命令）
- 修改数据库 Schema
- 修改生产环境配置
- 引入新的外部依赖（npm install/pip install）
- 修改 `.env` 文件中的非测试配置

### 回滚机制

如果多个 Issue 执行后发现系统级问题：

```bash
# 查看提交历史（每个 Issue 一个 commit）
git log --oneline | head -20

# 回滚到指定 Issue 之前
git revert HEAD~3  # 回滚最近3个 Issue 的提交
```

## 输出格式

### 执行开始

```
🚀 Issues Execute 启动
📄 数据源: issues/2026-03-01_10-30-00-user-auth.csv
📊 待执行: 10 Issues (P0: 2, P1: 5, P2: 3)
🔄 执行顺序: P0 → P1 → P2

---
[P1-001] 初始化 JWT 认证模块
  优先级: P0 | 功能域: auth
```

### 单 Issue 执行

```
[P1-001] 开始执行...
  📖 上下文收集... 完成
  🔨 实现开发... dev_state → DOING
     修改: src/auth/jwt.ts (新建)
     修改: src/auth/jwt.test.ts (新建)
  ✅ 初次审核... PASS
  ✅ 回归审核... PASS
  📦 Git 提交... feat(auth): 初始化 JWT 认证模块
     Hash: abc1234
  ✅ P1-001 完成 (耗时: 8分钟)
```

### 阻塞处理

```
[P2-003] 检测到阻塞
  ⏸ 原因: 依赖 P1-005 (数据库 Schema) 尚未完成
  → 跳过，继续下一个 Issue
```

## 相关文档

- `commands/general/plan-to-issues.md` — Issues 生成命令
- `commands/general/ralph.md` — Ralph 自主循环执行
- `commands/general/autopilot.md` — Autopilot 全自主模式
- `agents/qa-reviewer.md` — QA 审查 Agent
- `agents/qa-fixer.md` — QA 修复 Agent

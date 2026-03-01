# /plan-to-issues - 计划转 Issues CSV 命令

> 读取最新的 `plan/*.md` 计划文件，将所有阶段和任务转换为结构化的 Issues CSV，
> 作为后续 `/issues-execute` 闭环执行的唯一数据源。

## 概述

`/plan-to-issues` 命令将开发计划的 Markdown 文档转化为可追踪的 Issues CSV 文件。
每个 Issue 代表一个可独立执行的工作单元，包含完整的执行状态追踪字段。

## 用法

```bash
# 基本用法（读取最新 plan 文件）
/plan-to-issues

# 指定计划文件
/plan-to-issues plan/2026-03-01_user-auth.md

# 指定输出文件名（否则自动生成时间戳名）
/plan-to-issues --output issues/my-sprint.csv

# 仅生成预览，不写入文件
/plan-to-issues --dry-run
```

## CSV 格式规范

### 文件命名

```
issues/YYYY-MM-DD_HH-mm-ss-<slug>.csv
```

示例：`issues/2026-03-01_10-30-00-user-auth-system.csv`

### 编码要求

- **编码**: UTF-8 with BOM (`\xEF\xBB\xBF`)
- **行分隔**: CRLF (`\r\n`)
- **字段分隔**: 逗号 `,`
- **文本引用**: 双引号 `"` 包裹（内容含逗号或换行时）
- **换行转义**: 字段内换行用 `\n` 表示

### CSV 字段定义

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | string | ✅ | 格式：`PHASE-NNN`，如 `P1-001`、`P2-003` |
| `priority` | enum | ✅ | `P0`/`P1`/`P2`/`P3` |
| `phase` | string | ✅ | 阶段名称，如 `1-setup`、`2-core`、`3-testing` |
| `area` | string | ✅ | 功能域，如 `auth`、`api`、`frontend`、`db` |
| `title` | string | ✅ | 简短标题（≤80字符） |
| `description` | string | ✅ | 详细描述（用`\n`表示换行） |
| `acceptance_criteria` | string | ✅ | 验收标准列表（用`\n`分隔） |
| `test_mcp` | string | ⬜ | 使用的测试 MCP 工具名称 |
| `review_initial_requirements` | string | ⬜ | 初审需核实的需求项 |
| `review_regression_requirements` | string | ⬜ | 回归审核的检查项 |
| `dev_state` | enum | ✅ | `TODO`/`DOING`/`BLOCKED`/`DONE` |
| `review_initial_state` | enum | ✅ | `TODO`/`DOING`/`BLOCKED`/`DONE`/`PASS`/`FAIL` |
| `review_regression_state` | enum | ✅ | `TODO`/`DOING`/`BLOCKED`/`DONE`/`PASS`/`FAIL` |
| `git_state` | enum | ✅ | `TODO`/`COMMITTED`/`SKIPPED` |
| `owner` | string | ⬜ | 负责人（Claude/User/Agent名称） |
| `refs` | string | ⬜ | 相关文件路径，用`\|`分隔 |
| `notes` | string | ⬜ | 备注说明 |

### 状态枚举说明

**`dev_state` / `review_*_state` 通用**：
- `TODO` — 未开始
- `DOING` — 执行中
- `BLOCKED` — 被阻塞（需在 `notes` 中说明原因）
- `DONE` — 完成

**`review_*_state` 额外枚举**：
- `PASS` — 审核通过
- `FAIL` — 审核失败（需在 `notes` 中说明失败原因）

**`git_state`**：
- `TODO` — 尚未提交
- `COMMITTED` — 已提交（填入 commit hash）
- `SKIPPED` — 跳过提交（如纯文档变更由后续统一提交）

## 工作流程

```
1. 读取 plan/*.md 文件
        ↓
2. 解析阶段和任务
   - 识别 ## Phase N: 标题
   - 识别每个 Phase 下的 - [ ] 任务项
   - 提取验收标准、依赖关系
        ↓
3. 生成 Issue 行
   - 自动生成 id（P{phase}-{seq:03d}）
   - 初始状态：dev_state=TODO, 其余=TODO
   - 根据任务内容推断 priority 和 area
        ↓
4. 写入 CSV 文件（UTF-8 BOM）
        ↓
5. 输出摘要报告
```

## 输出示例

```
✅ 已读取计划文件: plan/2026-03-01_user-auth.md
📊 解析结果:
   - 阶段数: 3
   - Issue 总数: 12
   - P0: 2, P1: 5, P2: 4, P3: 1

📄 已生成: issues/2026-03-01_10-30-00-user-auth.csv

预览（前3行）:
id,priority,phase,area,title,dev_state,...
P1-001,P0,1-setup,auth,初始化 JWT 认证模块,TODO,...
P1-002,P1,1-setup,db,创建 User 数据表 Schema,TODO,...
P2-001,P1,2-core,api,实现 /auth/login 端点,TODO,...

💡 下一步: 运行 /issues-execute 开始闭环执行
```

## plan/*.md 解析规则

命令支持以下计划文件格式：

### 格式1：阶段-任务结构（推荐）

```markdown
# 项目名称

## Phase 1: 基础设置
优先级: P0
功能域: setup

### 任务
- [ ] 初始化项目结构
  - 验收: package.json 存在，依赖已安装
- [ ] 配置 TypeScript
  - 验收: tsconfig.json 通过严格模式检查

## Phase 2: 核心功能
优先级: P1
功能域: core
```

### 格式2：简单列表（自动推断）

```markdown
# 开发计划

## 第一阶段
- [ ] 任务A
- [ ] 任务B
- [ ] 任务C

## 第二阶段
- [ ] 任务D
- [ ] 任务E
```

### 格式3：表格格式

```markdown
| 任务 | 优先级 | 功能域 | 验收标准 |
|------|--------|--------|----------|
| 初始化项目 | P0 | setup | 项目可运行 |
```

## 与其他命令的关系

```
/vision-builder → plan/*.md 愿景文档
                        ↓
/spec-first     → specs/*.md 功能规范
                        ↓
/plan-to-issues → issues/*.csv 可执行 Issues ← 当前命令
                        ↓
/issues-execute → 闭环执行每个 Issue
```

## 相关文档

- `commands/general/issues-execute.md` — Issues 闭环执行命令
- `.claude/skills/vision-builder/SKILL.md` — 愿景构建 Skill
- `.claude/skills/plan-review/SKILL.md` — 计划审查 Skill
- `memory/lessons-learned.md` — 经验教训库

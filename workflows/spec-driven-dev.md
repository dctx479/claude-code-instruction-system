# 规范驱动开发 (Spec-Driven Development) 工作流

## 概述

规范驱动开发 (SDD) 是 GitHub 开源的开发方法论，实现"规范即可执行"的范式转变。核心理念：**代码服务于规范，而非规范服务于代码**。

## 核心原则

### 权力倒置
- 规范不是实现指南，而是生成实现的源头
- 规范必须足够精确、完整和无歧义
- 关注 **WHAT** 和 **WHY**，绝不涉及 **HOW**

### 可执行规范
- 规范可直接生成功能系统
- 面向业务利益相关者编写
- 技术无关的成功标准

## SDD 工作流阶段

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Constitution│ →  │   Specify   │ →  │   Clarify   │
│  建立宪章   │    │  定义规范   │    │  澄清需求   │
└─────────────┘    └─────────────┘    └─────────────┘
                          ↓
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Implement  │ ←  │    Tasks    │ ←  │    Plan     │
│  实施开发   │    │  任务分解   │    │  技术规划   │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 阶段详解

### 阶段 1: 建立宪章 (Constitution)

建立项目不可协商的治理原则和架构指南。

**输出**: `/memory/constitution.md`

**示例原则**:
```markdown
# 项目宪章

## Article I: 模块化
每个特性都从独立模块开始，确保模块化。

## Article II: 接口优先
模块通过明确定义的接口公开功能。

## Article III: 测试驱动
测试先于实施，TDD 不可协商。

## Article IV: 简单性
优先选择简单解决方案，避免过度工程。
```

### 阶段 2: 定义规范 (Specify)

从自然语言描述创建功能规范。

**规范模板结构**:
```markdown
# 特性规范: [特性名称]

## 元信息
- 分支标识符: [###-feature-name]
- 创建日期: YYYY-MM-DD
- 状态: Draft

## 用户场景与测试

### US-001 [P1]: 用户登录
**描述**: 作为注册用户，我希望能够登录系统...

**验收场景**:
```
Given 用户已注册
When 用户输入正确的凭据并点击登录
Then 用户被重定向到仪表板
```

## 功能需求
- FR-001: 系统 MUST 支持邮箱/密码登录
- FR-002: 系统 MUST 在3次失败后锁定账户 [NEEDS CLARIFICATION]

## 成功标准
- SC-001: 登录响应时间 < 2秒 (95th percentile)
- SC-002: 登录成功率 > 99.5%
```

**关键规则**:
- 使用 `MUST/SHOULD/MAY` 语言
- 最多 3 个 `[NEEDS CLARIFICATION]` 标记
- 成功标准必须可测量

### 阶段 3: 澄清需求 (Clarify)

识别并解决规范中的歧义。

**九个评估维度**:
1. 功能范围与行为
2. 领域与数据模型
3. 交互与用户体验流程
4. 非功能质量属性
5. 集成与外部依赖
6. 边缘情况与故障处理
7. 约束与权衡
8. 术语与一致性
9. 完成信号

**输出格式**:
```markdown
## Clarifications

### Session 2024-01-15
- Q: 账户锁定时间是多长? → A: 30分钟后自动解锁
- Q: 是否支持 SSO? → A: MVP 阶段不支持，后续迭代添加
```

### 阶段 4: 技术规划 (Plan)

执行实施规划，生成设计工件。

**Phase 0: 研究与澄清**
```markdown
# research.md

## 决策: 认证方案
- **选择**: JWT + Refresh Token
- **理由**: 无状态、可扩展、行业标准
- **替代方案**:
  - Session-based: 需要共享存储
  - OAuth only: 过于复杂
```

**Phase 1: 设计与契约**

**数据模型** (`data-model.md`):
```markdown
## User
- id: UUID (主键)
- email: String (唯一)
- password_hash: String
- status: Enum [active, locked, suspended]
- login_attempts: Integer (default: 0)
- locked_until: Timestamp (nullable)
```

**API 契约** (`contracts/auth.yaml`):
```yaml
openapi: 3.0.0
paths:
  /auth/login:
    post:
      summary: 用户登录
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                password:
                  type: string
      responses:
        200:
          description: 登录成功
        401:
          description: 认证失败
```

### 阶段 5: 任务分解 (Tasks)

生成可操作的、依赖有序的任务列表。

**任务格式**:
```markdown
# tasks.md

## Phase 1: Setup
- [ ] T001 初始化项目结构 `/src`, `/tests`
- [ ] T002 配置数据库连接 `/src/config/database.ts`

## Phase 2: Foundation
- [ ] T003 创建 User 模型 `/src/models/user.ts`
- [ ] T004 [P] 编写 User 模型测试 `/tests/models/user.test.ts`

## Phase 3: User Story - 登录 [US-001]
- [ ] T005 [P] [US1] 编写登录 API 测试 `/tests/api/auth.test.ts`
- [ ] T006 [US1] 实现登录端点 `/src/api/auth/login.ts`
- [ ] T007 [US1] 实现账户锁定逻辑 `/src/services/auth.ts`

## Phase 4: Polish
- [ ] T008 添加登录日志 `/src/middleware/logging.ts`
- [ ] T009 性能优化
```

**任务标记说明**:
- `[P]`: 可并行执行
- `[US1]`: 关联用户故事

### 阶段 6: 实施 (Implement)

执行任务列表中定义的所有任务。

**执行流程**:
1. 验证检查清单完成状态
2. 加载上下文 (tasks.md, plan.md, data-model.md)
3. 验证项目设置
4. 按依赖顺序执行任务
5. 测试优先方法
6. 完成后标记 `[X]`

## 目录结构

```
specs/
├── constitution.md           # 项目宪章
└── ###-feature/
    ├── spec.md              # 功能规范
    ├── research.md          # 技术研究
    ├── plan.md              # 技术规划
    ├── data-model.md        # 数据模型
    ├── tasks.md             # 任务列表
    ├── quickstart.md        # 快速入门
    ├── contracts/           # API 契约
    │   └── api.yaml
    └── checklists/          # 检查清单
        └── requirements.md
```

## 在 Claude Code 中使用 SDD

### 自定义命令

创建 `.claude/commands/` 下的命令文件:

**specify.md**:
```markdown
基于以下描述创建功能规范: $ARGUMENTS

遵循 SDD 规范模板:
1. 定义用户场景和验收标准
2. 列出功能需求 (使用 MUST/SHOULD 语言)
3. 定义可测量的成功标准
4. 标记需要澄清的地方

输出到 specs/[分支名]/spec.md
```

**plan.md**:
```markdown
基于规范创建技术规划: $ARGUMENTS

1. 研究技术方案并记录决策
2. 设计数据模型
3. 定义 API 契约
4. 生成快速入门指南

输出到 specs/[分支名]/ 目录
```

**tasks.md**:
```markdown
基于规划生成任务列表: $ARGUMENTS

1. 解析技术栈和结构
2. 按用户故事组织任务
3. 标记可并行任务 [P]
4. 生成依赖图

输出到 specs/[分支名]/tasks.md
```

### 工作流示例

```
用户: 我想添加用户登录功能

Claude:
1. /project:specify 用户登录功能
   → 生成 specs/001-user-login/spec.md

2. /project:clarify
   → 识别并解决歧义

3. /project:plan
   → 生成 research.md, data-model.md, contracts/

4. /project:tasks
   → 生成 tasks.md

5. /project:implement
   → 按顺序执行任务
```

## 质量验证

### 分析命令

对规范工件执行跨工件验证:

**检测维度**:
- 重复检测
- 歧义检测 (模糊形容词)
- 规范不足
- 宪章对齐
- 覆盖差距
- 不一致检测

**严重性级别**:
- CRITICAL: 阻塞性问题
- HIGH: 必须修复
- MEDIUM: 应该修复
- LOW: 可选优化

### 检查清单

验证需求质量 (非实施正确性):

```markdown
## 需求质量检查清单

### 完整性
- [ ] 所有必要需求是否已记录?
- [ ] 是否涵盖所有用户角色?

### 清晰性
- [ ] 需求是否具体且无歧义?
- [ ] 术语是否一致使用?

### 可测量性
- [ ] 成功标准是否可客观验证?
- [ ] 性能指标是否有具体数值?
```

## 最佳实践

1. **规范先于代码**: 永远先完成规范再开始编码
2. **迭代细化**: 使用 clarify 阶段解决歧义
3. **测试驱动**: 规范中的验收标准即测试用例
4. **版本控制**: 规范与代码一起版本控制
5. **持续验证**: 使用 analyze 确保一致性
6. **技术无关**: 规范描述 WHAT，不涉及 HOW

## 参考资源

- [GitHub spec-kit](https://github.com/github/spec-kit)
- [Spec-Driven Development 博客](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)

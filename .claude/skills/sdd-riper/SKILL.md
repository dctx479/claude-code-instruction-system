---
name: sdd-riper
description: Spec-Driven Development + RIPER 五阶段流程，确保大模型编程质量可控
type: Heavy（重量级）
version: 1.1.0
trigger:
  - "/riper"
  - "/sdd-riper"
  - "中大型需求开发"
  - "需要写规范文档"
  - "复杂功能实现"
---

# SDD-RIPER Skill

## What（输入/输出）

**输入**：需求描述（自然语言）+ 可选的背景文档/代码库

**输出**：
- `mydocs/specs/<task>.md` — 完整 Spec 文档（8章节）
- `mydocs/codemap/<feature>.md` — 代码地图（可选）
- `mydocs/archive/<task>_human.md` + `_llm.md` — 知识沉淀

## How（判断框架）

**何时用标准版 vs 轻量版**：
- 预计 >500 行代码 或 涉及 >3 个文件 → 标准版（本 Skill）
- 简单 Bug 修复 / 小功能 / 熟练用户快速迭代 → `sdd-riper-light`

**五阶段时间分配**：Research 30% → Innovate 20% → Plan 20% → Execute 25% → Review 5%

**核心门禁**：Plan Approved 前禁止写代码；Spec 与代码冲突时以 Spec 为准

## When Done（验收标准）

- Spec 文档已完成 §1-§8 全部章节
- Plan Approved 门禁已通过（用户明确批准）
- Execute 阶段严格按 Plan 实现，无未记录的偏离
- Review 阶段完成三角验证（功能/测试/文档）

## What NOT（边界约束）

🚫 不做的事：
1. 不在 Plan Approved 前写任何实现代码
2. 不跳过 Research 阶段（即使"看起来很简单"）
3. 不在 Execute 阶段修改 Spec（发现问题先停止，更新 Spec，再继续）
4. 不替代 `sdd-riper-light`（简单任务用轻量版，不要用标准版增加负担）

---

## 核心理念

**Spec-Driven Development (SDD)**: 用输入 Token（1-10%成本）换输出 Token（100%成本），通过结构化文档降低试错成本。

**RIPER 五阶段流程**: Research → Innovate → Plan → Execute → Review

## 适用场景

- ✅ 中大型需求开发（预计 >500 行代码或涉及 >3 个文件）
- ✅ 复杂功能实现（需要架构设计或方案对比）
- ✅ 需要知识沉淀的场景（团队协作、技术传承）
- ❌ 简单 Bug 修复（<50 行代码改动）
- ❌ 配置文件调整（无需设计决策）

## 快速启动

### 1. 触发方式

```bash
# 方式 1: 直接描述需求（自动判断是否需要 RIPER）
"实现用户认证系统，支持 JWT + OAuth2"

# 方式 2: 显式启动 RIPER 流程
/riper "实现用户认证系统，支持 JWT + OAuth2"
```

### 2. 流程概览

```
┌─────────────┐
│  Research   │ 调研与事实锁定（30% 时间）
│  (调研阶段)  │ - 读取现有代码/文档
│             │ - 识别依赖和约束
└──────┬──────┘
       │
┌──────▼──────┐
│  Innovate   │ 方案设计与对比（20% 时间）
│  (创新阶段)  │ - 生成 2-3 个候选方案
│             │ - 多维度对比（性能/成本/风险）
└──────┬──────┘
       │
┌──────▼──────┐
│    Plan     │ 原子级规划（20% 时间）
│  (规划阶段)  │ - 拆解为原子任务
│             │ - 生成验收标准
│             │ ⚠️ Plan Approved 门禁
└──────┬──────┘
       │
┌──────▼──────┐
│  Execute    │ 按图施工（25% 时间）
│  (执行阶段)  │ - 严格按 Plan 实现
│             │ - 禁止偏离 Spec
└──────┬──────┘
       │
┌──────▼──────┐
│   Review    │ 验收闭环（5% 时间）
│  (复盘阶段)  │ - 验收标准检查
│             │ - 知识沉淀
└─────────────┘
```

## 核心原则

### 1. No Spec No Code
- 未完成 Plan Approved 前，禁止写代码
- Spec 是唯一的实现依据

### 2. Spec is Truth
- 代码与 Spec 冲突时，以 Spec 为准
- 需求变更必须先更新 Spec

### 3. Plan Approved 门禁
- Plan 阶段结束后，必须等待用户审批
- 用户可以：
  - ✅ 批准（进入 Execute）
  - 🔄 修改（返回 Innovate 或 Plan）
  - ❌ 拒绝（终止流程）

### 4. Reverse Sync（反向同步）
- Execute 阶段发现 Spec 错误时：
  1. 停止实现
  2. 更新 Spec
  3. 重新获得 Plan Approved
  4. 继续实现

## 输出产物

### 1. Spec 文档（核心）
```
mydocs/specs/<task>.md
├── §1 需求概述
├── §2 SDD-RIPER 流程记录
│   ├── §2.1 Research（调研记录）
│   ├── §2.2 Innovate（方案对比）
│   ├── §2.3 Plan（实现计划）
│   ├── §2.4 Execute（执行日志）
│   └── §2.5 Review（复盘总结）
├── §3 技术方案
├── §4 实现细节
├── §5 测试策略
├── §6 部署方案
├── §7 风险与应对
└── §8 附录
```

### 2. CodeMap（可选）
```
mydocs/codemap/<feature>.md
├── 架构概览
├── 模块依赖图
├── 关键路径标注
└── 接口定义
```

### 3. 知识沉淀（自动）
```
mydocs/archive/<task>_human.md  # 人类可读版本
mydocs/archive/<task>_llm.md    # LLM 可读版本（结构化）
```

## 详细流程

### Phase 1: Research（调研阶段）

**目标**: 锁定事实，避免幻觉

**步骤**:
1. 读取相关代码文件（使用 `codemap-builder` 生成代码地图）
2. 识别现有架构模式
3. 提取依赖和约束
4. 记录到 Spec §2.1

**输出**:
```markdown
## §2.1 Research

### 现有架构
- 认证模块: `src/auth/` (基于 Passport.js)
- 数据库: PostgreSQL + Prisma ORM
- API 框架: Express.js

### 依赖约束
- 必须兼容现有 Session 机制
- 需要支持移动端 Token 刷新

### 关键发现
- 现有 `User` 模型缺少 `refreshToken` 字段
- CORS 配置需要更新以支持 OAuth2 回调
```

### Phase 2: Innovate（创新阶段）

**目标**: 生成并对比多个方案

**步骤**:
1. 生成 2-3 个候选方案
2. 多维度对比（性能/成本/风险/复杂度）
3. 推荐最优方案
4. 记录到 Spec §2.2

**输出**:
```markdown
## §2.2 Innovate

### 方案 A: JWT + Passport-JWT
- 优点: 与现有 Passport 生态集成
- 缺点: 需要额外的 Token 黑名单机制
- 复杂度: ⭐⭐⭐

### 方案 B: 自研 JWT + Redis
- 优点: 完全控制，性能最优
- 缺点: 开发成本高，维护负担重
- 复杂度: ⭐⭐⭐⭐⭐

### 方案 C: Auth0 托管服务
- 优点: 零维护，企业级安全
- 缺点: 月费 $240，供应商锁定
- 复杂度: ⭐

### 推荐方案: A（JWT + Passport-JWT）
理由: 平衡开发成本和灵活性，团队已熟悉 Passport 生态
```

### Phase 3: Plan（规划阶段）

**目标**: 拆解为原子任务，生成验收标准

**步骤**:
1. 将方案拆解为原子任务（每个任务 <2 小时）
2. 为每个任务定义验收标准
3. 标注任务依赖关系
4. 记录到 Spec §2.3
5. **等待 Plan Approved**

**输出**:
```markdown
## §2.3 Plan

### 任务列表

#### Task 1: 数据库迁移
- 描述: 为 `User` 模型添加 `refreshToken` 字段
- 验收标准:
  - [ ] Prisma schema 已更新
  - [ ] 迁移脚本已生成并测试
  - [ ] 现有数据兼容性验证通过
- 依赖: 无
- 预计时间: 1h

#### Task 2: JWT 工具函数
- 描述: 实现 `generateToken()` 和 `verifyToken()`
- 验收标准:
  - [ ] 支持 Access Token（15min 过期）
  - [ ] 支持 Refresh Token（7d 过期）
  - [ ] 单元测试覆盖率 >90%
- 依赖: Task 1
- 预计时间: 2h

#### Task 3: Passport-JWT 策略
- 描述: 配置 Passport-JWT 中间件
- 验收标准:
  - [ ] 从 Authorization Header 提取 Token
  - [ ] 验证失败返回 401
  - [ ] 集成测试通过
- 依赖: Task 2
- 预计时间: 1.5h

### 总预计时间: 4.5h
```

**⚠️ Plan Approved 门禁**:
- 此时 Claude 会停止并等待用户审批
- 用户可以通过以下命令批准：
  ```bash
  /plan-approve
  # 或直接回复 "批准" / "approve"
  ```

### Phase 4: Execute（执行阶段）

**目标**: 严格按 Plan 实现，禁止偏离

**步骤**:
1. 按任务顺序依次实现
2. 每完成一个任务，更新 Spec §2.4
3. 遇到 Spec 错误时，触发 Reverse Sync

**输出**:
```markdown
## §2.4 Execute

### Task 1: 数据库迁移 ✅
- 实现时间: 2024-01-15 14:30
- 文件变更:
  - `prisma/schema.prisma`: 添加 `refreshToken String?`
  - `prisma/migrations/20240115_add_refresh_token.sql`
- 验收结果: 全部通过

### Task 2: JWT 工具函数 ✅
- 实现时间: 2024-01-15 16:00
- 文件变更:
  - `src/utils/jwt.ts`: 新增
  - `src/utils/jwt.test.ts`: 新增
- 验收结果: 单元测试覆盖率 94%

### Task 3: Passport-JWT 策略 🔄
- 实现时间: 2024-01-15 17:30
- 发现问题: Spec 中未考虑 CORS 预检请求（OPTIONS）
- 触发 Reverse Sync:
  1. 更新 Spec §2.3 Task 3 验收标准
  2. 添加 Task 3.1: CORS 配置更新
  3. 等待 Plan Approved
```

### Phase 5: Review（复盘阶段）

**目标**: 验收闭环，知识沉淀

**步骤**:
1. 检查所有验收标准
2. 运行完整测试套件
3. 生成复盘总结
4. 自动归档到 `mydocs/archive/`

**输出**:
```markdown
## §2.5 Review

### 验收结果
- ✅ 所有任务验收标准通过
- ✅ 单元测试覆盖率: 92%
- ✅ 集成测试: 15/15 通过
- ✅ 性能测试: Token 生成 <5ms

### 经验教训
- ✅ 做得好: 提前识别 CORS 问题，避免生产事故
- ⚠️ 可改进: Spec 初期应考虑跨域场景
- 📝 知识沉淀: JWT Refresh Token 最佳实践已归档

### 知识归档
- 人类版本: `mydocs/archive/auth-jwt_human.md`
- LLM 版本: `mydocs/archive/auth-jwt_llm.md`
```

## 集成 Agent

### codemap-builder
- 触发时机: Research 阶段开始前
- 用途: 生成项目级/功能级代码地图
- 输出: `mydocs/codemap/<feature>.md`

### qa-reviewer
- 触发时机: Execute 阶段每个任务完成后
- 用途: 自动验证验收标准
- 输出: 验收报告（记录到 Spec §2.4）

### qa-fixer
- 触发时机: qa-reviewer 发现问题时
- 用途: 自动修复常见问题
- 输出: 修复后的代码 + 修复日志

## 最佳实践

### 1. 何时使用 RIPER？
- ✅ 需求描述 >100 字
- ✅ 预计涉及 >3 个文件
- ✅ 需要架构设计或方案对比
- ❌ 简单 Bug 修复
- ❌ 配置文件调整

### 2. 如何写好 Spec？
- 使用具体数字（"<5ms" 而非 "快速"）
- 包含反例（"不支持 X" 而非只说 "支持 Y"）
- 验收标准可测试（避免主观描述）

### 3. Plan Approved 门禁的价值
- 避免方向性错误（用户可提前纠偏）
- 降低返工成本（Plan 阶段修改成本 <10% Execute 阶段）
- 提升协作效率（用户可并行准备测试数据）

### 4. Reverse Sync 的触发时机
- Spec 中的技术假设错误（如 API 不存在）
- 发现更优实现方案（需用户确认）
- 验收标准无法满足（需调整标准）

## 常见问题

### Q1: RIPER 会增加多少时间成本？
A: 前期投入 +30%，但可减少 50-70% 返工时间，总体节省 20-40% 时间。

### Q2: 简单需求也要走完整流程吗？
A: 不需要。Claude 会自动判断任务复杂度，简单任务会跳过 Innovate 阶段。

### Q3: Plan Approved 后发现需求变更怎么办？
A: 触发 Reverse Sync，更新 Spec 后重新获得 Plan Approved。

### Q4: 如何查看历史 Spec？
A: 所有 Spec 都在 `mydocs/specs/` 目录，按任务名称组织。

## 参考资料

- 完整指南: `docs/SDD-RIPER-GUIDE.md`
- Spec 模板: `specs/SPEC-TEMPLATE.md`
- 编排策略: `docs/ORCHESTRATION-GUIDE.md`

## 版本历史

- v1.0.0 (2024-01-15): 初始版本，支持完整 RIPER 流程

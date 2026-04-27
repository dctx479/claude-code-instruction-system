# SDD-RIPER 方法论指南

> **核心理念**: Spec-Driven Development + RIPER 五阶段流程 = 可控的大模型编程
> **适用场景**: 中大型需求开发、复杂功能实现、团队协作、知识沉淀

---

## 一、核心概念

### 1.1 什么是 SDD？

**Spec-Driven Development（规范驱动开发）** = 文档先行的开发方法论

核心原则：
```
Code is Cheap, Context is Expensive.
代码是廉价的消耗品，文档（Spec）才是昂贵的核心资产。
```

**三条铁律**：
1. **No Spec, No Code** — 没有文档，不准写代码
2. **Spec is Truth** — 文档和代码冲突时，错的一定是代码
3. **Reverse Sync** — 发现 Bug，先修文档，再修代码

### 1.2 什么是 RIPER？

**RIPER** = 五阶段状态机，约束 AI 的执行顺序和决策权限

```
Research → Innovate → Plan → Execute → Review
  调研      方案设计    规划    执行      验收
```

**核心价值**：
- 解决上下文腐烂（AI 遗忘前文约束）
- 解决审查瘫痪（AI 秒生成 500 行代码，人无法 Review）
- 解决维护断层（全是 AI 生成的陌生代码，不敢动）
- 解决代码不信任（不知道 AI 为什么这么写）

---

## 二、RIPER 五阶段详解

### 阶段 0：Pre-Research（准备输入）

**目标**：准备 AI 需要的"原材料"，降低幻觉，减少无效 Token 消耗

**可选命令**：

| 命令 | 作用 | 是否必须 |
|------|------|----------|
| `create_codemap` | 生成功能级/项目级代码地图 | 中大型任务强烈建议 |
| `build_context_bundle` | 整理需求文档、设计图、讨论记录 | 需求复杂时建议 |
| `sdd_bootstrap` | 收口所有输入，启动 RIPER 流程 | 建议必须 |

**示例**：
```bash
# 1. 生成代码地图（聚焦于本次任务相关的链路）
create_codemap: mode=feature, scope=用户权限模块, goal=梳理权限校验链路

# 2. 整理上下文包（可选）
build_context_bundle: ./mydocs/context/raw/permission-refactor

# 3. 启动 RIPER 流程
sdd_bootstrap:
- task=权限模块重构
- goal=统一权限校验入口，支持细粒度授权
- requirement=docs/prd/permission-v2.md
- codemap_ref=mydocs/codemap/permission-check.md
- context_ref=mydocs/context/permission-refactor_context_bundle.md
```

**产出物**：
- `mydocs/codemap/<feature>.md` — 代码地图（长期资产）
- `mydocs/context/<date>_<task>_context_bundle.md` — 上下文包（一次性）
- `mydocs/specs/<date>_<task>.md` — 首版 Spec（核心资产）

---

### 阶段 1：Research（调研与事实锁定）

**目标**：让 AI 查清代码现状，锁定事实，消除信息差。绝不允许 AI 瞎猜。

**核心原则**：
- ✅ 每个结论必须有代码出处（文件路径、函数名、行号）
- ❌ 不接受"我认为"、"通常来说"
- ✅ 让 AI 主动提问，把不确定的点暴露出来

**对话示例**：
```
你：请进入 Research 阶段。基于首版 Spec，逐条核查以下事实：
1. 权限校验的入口在哪里？有几个入口？
2. 当前的授权逻辑是怎么实现的？
3. 有没有历史遗留的特殊处理？
请给出每个结论的代码出处。

AI：[Research 模式]
1. 权限校验入口有 2 个：
   - `PermissionFilter.java:L28` — HTTP 请求拦截
   - `RpcPermissionInterceptor.java:L15` — RPC 调用拦截
2. 授权逻辑在 `AuthService.java:L45-L78`，通过 ...
3. 发现一个特殊处理：`LegacyAuthAdapter.java:L33` 有一个 ...

我的疑问：
- 入口 2 的 RPC 拦截是否还在使用？我没有找到调用方。
- Spec 中提到的"细粒度授权"，粒度到什么级别？字段级还是接口级？
```

**完成标准**：
- ✅ 入口、链路、依赖、风险全部锁定
- ✅ 每个结论有代码出处
- ✅ 不确定项已在 Spec 中显式标注
- ✅ AI 的疑问已全部回答或标记为 `[待确认]`

**注意事项**：
- 逼 AI 提问：如果 AI 没有提出任何疑问，说明它在敷衍
- 反向复述：让 AI 用自己的话复述需求，检查理解是否一致
- 所有发现必须回写 Spec：不要让信息散落在对话里

---

### 阶段 2：Innovate（方案设计与对比）

**目标**：逼 AI 给出 2-3 个方案，对比 Pros/Cons，人类拍板选哪个。

**核心原则**：
- ❌ 禁止只给一个方案 — 一个方案 = 没有选择 = 局部最优陷阱
- ✅ 每个方案必须说清：改哪些文件、影响范围、风险点、工作量估算
- ✅ 人类做决策，AI 做分析

**对话示例**：
```
你：请进入 Innovate 阶段。基于 Research 的发现，给出 2-3 个方案，
每个方案说清：
- 核心思路
- 需要改哪些文件
- Pros（优点）
- Cons（缺点）
- 风险点
- 工作量估算

AI：[Innovate 模式]
### 方案 A：统一入口 + 策略模式
- 核心思路：合并两个入口为一个 `UnifiedPermissionGateway`，用策略模式...
- 改动文件：`PermissionFilter.java`, `RpcPermissionInterceptor.java`, 新增 `UnifiedPermissionGateway.java`
- Pros：入口统一，后续维护成本低
- Cons：改动面大，需要回归测试
- 风险：RPC 拦截器的调用方需要确认
- 工作量：约 2 天

### 方案 B：适配器模式 + 渐进迁移
- 核心思路：保留两个入口，新增适配层...
- ...

### 推荐：方案 A
- 原因：虽然改动面大，但一步到位，避免长期维护两套逻辑...
```

**完成标准**：
- ✅ 至少 2 个方案
- ✅ 每个方案有清晰的 Pros/Cons
- ✅ 有明确的推荐和理由
- ✅ 选定方案后，必须回写 Spec

**注意事项**：
- 如果任务很简单（如改个配置），可以跳过 Innovate，在 Spec 中标注 `Innovate: Skipped, Reason: 单点修改，无需多方案对比`

---

### 阶段 3：Plan（原子级规划）

**目标**：把选定的方案拆解为原子级的实施清单，精确到文件路径和函数签名。

**这是整个流程的决胜点。Plan 看不懂 = 不准动手。**

**核心原则**：
- ✅ 每一步必须精确到：改哪个文件、改哪个函数、怎么改
- ✅ 必须包含函数签名（新增的函数/类）
- ✅ 必须有明确的执行顺序（依赖关系）

**对话示例**：
```
你：请进入 Plan 阶段。基于方案 A，输出原子级实施清单。
要求：
1. 精确到文件路径和函数签名
2. 标明执行顺序和依赖关系
3. 标明每一步的验证方式

AI：[Plan 模式]
### Implementation Checklist
- [ ] 1. 新建 `src/main/java/com/xxx/permission/UnifiedPermissionGateway.java`
  - `public class UnifiedPermissionGateway implements PermissionChecker`
  - `public boolean checkPermission(PermissionContext ctx)`
  - `private PermissionStrategy resolveStrategy(RequestType type)`

- [ ] 2. 修改 `src/main/java/com/xxx/filter/PermissionFilter.java`
  - 将 `doFilter()` 中的权限校验逻辑委托给 `UnifiedPermissionGateway`
  - 保留原有的异常处理逻辑

- [ ] 3. 修改 `src/main/java/com/xxx/rpc/RpcPermissionInterceptor.java`
  - 将 `invoke()` 中的权限校验逻辑委托给 `UnifiedPermissionGateway`

- [ ] 4. 新建 `src/test/java/com/xxx/permission/UnifiedPermissionGatewayTest.java`
  - 覆盖：HTTP 请求、RPC 请求、无权限、超级管理员四种场景

执行顺序：1 → 2 → 3 → 4（1 是基础，2/3 依赖 1，4 最后验证）
```

**完成标准**：
- ✅ Plan 必须人类审批
- ✅ 看不懂的地方，要求 AI 解释或细化
- ✅ 审批通过后，明确回复：**Plan Approved**
- ✅ Plan 回写 Spec：批准后的 Plan 必须完整记录在 Spec 中

**审批检查清单**：
- [ ] 每一步我都看得懂吗？
- [ ] 文件路径和函数签名是否正确？
- [ ] 执行顺序是否合理？
- [ ] 有没有遗漏的文件或步骤？
- [ ] 风险点是否已标注？

---

### 阶段 4：Execute（按图施工）

**目标**：AI 严格按照 Plan 逐步执行，生成代码。人类只需监督。

**核心原则**：
- ✅ AI 只能按 Plan 执行，不允许自由发挥
- ✅ 每完成一步，AI 应报告进度
- ❌ 如果执行中发现 Plan 有问题，必须停下来，回到 Plan 阶段修正，不能"偷偷改"

**对话示例**：
```
你：Plan Approved。请进入 Execute 阶段，严格按照 Plan 逐步执行。
每完成一步，报告进度。如果发现 Plan 有问题，立即停下来告诉我。

AI：[Execute 模式]
✅ Step 1/4：已创建 `UnifiedPermissionGateway.java`
  - 实现了 `checkPermission()` 和 `resolveStrategy()`
  - 代码已写入文件

🔄 正在执行 Step 2/4：修改 `PermissionFilter.java`...
```

**完成标准**：
- ✅ 所有 Plan 中的步骤已执行
- ✅ 每一步完成后，在 Spec 的 Execute Log 中打勾记录
- ✅ 编译通过，无语法错误

**注意事项**：
- ❌ 关闭 YOLO / 全自动模式：绝对禁止 AI "先斩后奏"
- ❌ 如果 AI 在执行中说"我觉得 Plan 可以优化"——拒绝。要么按 Plan 执行，要么回到 Plan 阶段重新审批
- ✅ 执行过程中的编译错误、类型不匹配等问题，AI 可以自行修复，但逻辑变更必须报告

---

### 阶段 5：Review（验收闭环）

**目标**：对照 Spec 验收代码，确保"文档说的 = 代码做的"。

**核心原则**：
- ✅ 三角定位：Spec（预期）vs 代码（实现）vs 执行日志（过程），三方交叉验证
- ✅ 发现偏差：先修 Spec，再修代码（Reverse Sync）
- ✅ 记录所有偏差和风险

**对话示例**：
```
你：请进入 Review 阶段。对照 Spec 逐条验收：
1. Spec 中的每个预期行为是否都已落地？
2. 有没有偏离 Plan 的地方？
3. 代码质量是否符合标准？

AI：[Review 模式]
### Review Checklist
✅ 功能完整性：4/4 目标行为已实现
✅ Plan 一致性：无偏差
⚠️ 代码质量：发现 1 处潜在问题

### 发现的问题
1. `UnifiedPermissionGateway.java:L52` 缺少空指针检查
   - 建议：添加 `Objects.requireNonNull(ctx)` 守卫

### 结论
整体通过，建议修复上述问题后上线。
```

**完成标准**：
- ✅ Review 结果必须回写 Spec（§6 Review Verdict）
- ✅ 如果不通过，回到 Plan 阶段重新规划
- ✅ Plan-Execution Diff 必须留底：任何偏离 Plan 的变动都要说明原因

---

### 阶段 6：Archive（知识沉淀）

**目标**：项目收尾时把中间产出的各种 Spec 进行精简合并，沉淀为团队的长期复用资产。

**核心原则**：
- ✅ 遗忘代表着资产的断供
- ✅ 沉淀两份资产：Human 视角版 + LLM 视角版

**执行命令**：
```bash
请执行 archive，将刚才此功能的规格和逻辑资产沉淀下来。
```

**产出物**：
- `mydocs/archive/<task>_human.md` — 人类可读的方案与汇报
- `mydocs/archive/<task>_llm.md` — 机器可读的上下文切片（下次接手项目的钥匙）

---

## 三、与现有系统的集成

### 3.1 与 Agent 编排系统的关系

RIPER 可以作为一种新的编排模式，加入现有的编排策略矩阵：

| 任务特征 | 推荐策略 | Agent配置 |
|----------|----------|-----------|
| 独立子任务 | PARALLEL | 多Worker同时执行 |
| 依赖链任务 | SEQUENTIAL | 管道式传递 |
| 复杂决策 | HIERARCHICAL | Specialist领导Worker |
| **中大型需求开发** | **RIPER** | **五阶段状态机** |

### 3.2 与 QA 系统的关系

RIPER 的 Review 阶段可以与现有的 QA 系统深度整合：

```
Execute 完成 → RIPER Review（三角验证）
                    ↓
              QA Reviewer（评分）
                    ↓
              ≥80分？
               ↓     ↓
              是     否 → 有P2？
               ↓           ↓
             发布      QA Fixer 自动修复
                           ↓
                      重新 Review
```

### 3.3 与 Spec 模板的关系

现有的 `specs/SPEC-TEMPLATE.md` 可以扩展为 RIPER 版本：

```markdown
# [功能名称] - SDD-RIPER 规范

## §1 需求概述
[现有内容保持不变]

## §2 Research Findings（新增）
[Research 阶段的发现]

## §3 Innovate Options（新增）
[方案对比]

## §4 Plan Checklist（新增）
[原子级实施清单]

## §5 Execute Log（新增）
[执行日志]

## §6 Review Verdict（新增）
[验收结论]

## §7 技术方案
[现有内容保持不变]
```

---

## 四、使用场景

### 场景 1：研发提效

**问题**：需求周期长（1-2 周），老项目不敢动

**解决方案**：
- 核心研发花 1-2 小时，对老项目执行 `create_codemap`，产出 Code Map
- 低经验同学用 SDD-RIPER 流程完成需求
- 核心研发只做两件事：审 Plan + 最终 Review

**效果**：
- 需求周期从 1-2 周压缩到 3-4 天
- 老项目 20 分钟就能重新进入状态

### 场景 2：人力解耦

**问题**：核心研发被老业务绑定，无法投入新业务

**解决方案**：
- 核心研发一次性沉淀 Code Map + Spec + 约束文档
- 低经验同学在 RIPER 流程约束下稳定交付老业务的日常迭代
- 全程有思考留痕、有阶段门禁、有 Review 闭环

**效果**：
- Bug 率不升反降 18% - 37%
- 核心人力从老需求中释放

### 场景 3：知识不随人走

**问题**：人员轮换、项目交割时，知识随人走

**解决方案**：
- Spec 把项目的知识资产从人脑里搬到文档里
- 交接变成"读 Spec → 按图施工"

**效果**：
- 接入周期从周级降到天级
- 无论谁来接手，上下文不丢失

---

## 五、常见问题

### Q1：Spec 怎么写？写多详细？

**A**：Spec 不是长文，最小结构只需要五个字段：

```
目标 / 范围 / 约束 / 风险 / Checklist
```

复杂需求可以扩展为完整 Spec（含 Research Findings、Innovate Options、Plan Checklist、Execute Log、Review Verdict），但先跑起来比写完美更重要。

### Q2：老项目 Research 太慢怎么办？

**A**：老项目启动慢是不可避免的阵痛。与其反复拖着痛，不如趁这个机会做一次"手术"：

- 专门花 1-2 天，让大模型系统性 Research 项目，沉淀 3-5 份高价值的 Code Map
- 按功能切片沉淀，每次做新需求时补一块，慢慢建起项目的知识图谱
- 这是一次性投入，后续所有人都能复用——越早做，复利越大

### Q3：SDD 协议会不会"污染"大模型的上下文窗口？

**A**：协议本身的静态开销极小（约 3,000 - 3,500 tokens），真正的上下文杀手是没有协议时的无序试错。

SDD-RIPER 内置了三层上下文管理机制：
1. **分层加载**：每轮只带当前阶段必需的最小信息
2. **落盘而非留在对话**：所有中间产物持久化到 `mydocs/` 目录
3. **轻重双轨分流**：简单任务用 Light 版，复杂任务用标准版

### Q4：为什么越复杂的项目，越需要 SDD-RIPER？

**A**：项目越小、链路越短，越容易靠个人经验和临时对话推进。但一旦进入复杂业务、多项目联动、多人协作、长期维护的状态，单靠聊天记录、口头同步和临场扫描代码，反而最容易失控。

复杂不是不适合 SDD-RIPER 的理由，复杂恰恰是更需要 SDD-RIPER 的理由。

---

## 六、参考资料

### 内部文档
- `docs/ORCHESTRATION-GUIDE.md` — 编排系统详细指南
- `docs/QA-SYSTEM.md` — 质量保障系统
- `docs/CONTEXT-ENGINEERING-GUIDE.md` — 上下文工程准则
- `specs/SPEC-TEMPLATE.md` — 规范模板

### 外部资源
- [SDD-RIPER 原始协议](https://example.com/sdd-riper)
- [Anthropic 官方会话管理实践](https://docs.anthropic.com)

---

**文档状态**: ✅ 已完成
**最后更新**: 2026-04-27
**维护者**: 太一元系统团队

# 最佳实践库 (Best Practices)

> 从成功经验中提炼的最佳实践，持续积累和更新

---

## Agent 编排最佳实践

### BP-001: 任务分解原则

**实践描述**:
复杂任务分解时遵循 MECE 原则 (相互独立、完全穷尽)

**适用场景**:
所有需要分解的复杂任务

**具体做法**:
```
1. 识别任务的主要组成部分
2. 确保各部分相互独立 (无重叠)
3. 确保所有部分覆盖完整任务 (无遗漏)
4. 评估各部分的依赖关系
5. 确定可并行的部分
```

**效果**:
- 减少任务冲突
- 提高并行度
- 更清晰的进度跟踪

---

### BP-002: 策略选择决策树

**实践描述**:
使用决策树快速选择最优编排策略

**决策流程**:
```
任务是否可分解?
├── 否 → 单Agent执行
└── 是 → 子任务间有依赖?
         ├── 完全独立 → PARALLEL
         ├── 链式依赖 → SEQUENTIAL
         └── 部分依赖 → 需要专家决策?
                        ├── 是 → HIERARCHICAL
                        └── 否 → 需要多视角?
                                 ├── 是 → COLLABORATIVE
                                 └── 否 → PARALLEL (分组)
```

---

### BP-003: Agent 能力匹配

**实践描述**:
根据任务类型选择最合适的Agent

**匹配规则**:
| 任务类型 | 首选Agent | 备选Agent |
|----------|-----------|-----------|
| 代码审查 | code-reviewer | architect |
| Bug修复 | debugger | code-reviewer |
| 安全检查 | security-analyst | code-reviewer |
| 数据分析 | data-scientist | - |
| 架构设计 | architect | - |
| 快速搜索 | explorer (haiku) | - |

---

### BP-004: 并行任务优化

**实践描述**:
最大化并行效率同时避免资源冲突

**具体做法**:
```
1. 分析任务资源依赖
2. 将任务分组:
   - 独立任务 → 立即并行
   - 冲突任务 → 串行队列
3. 设置合理的并行度 (通常3-5个)
4. 监控执行进度
5. 动态调整并行度
```

**注意事项**:
- 过高并行度可能导致资源竞争
- 文件修改任务需特别注意冲突

---

### BP-005: 结果整合策略

**实践描述**:
高效整合多Agent输出

**整合模式**:
| 情况 | 策略 |
|------|------|
| 输出互补 | 合并 (Merge) |
| 输出冲突 | 投票或专家裁决 |
| 输出重复 | 去重 (Dedupe) |
| 输出有序 | 按顺序组装 |

**质量验证**:
```
1. 检查输出完整性
2. 验证格式一致性
3. 确认无冲突
4. 测试最终结果
```

---

### BP-006: 错误恢复策略

**实践描述**:
优雅处理Agent失败

**恢复流程**:
```
Agent失败
├── 可重试错误 (超时、临时错误)
│   └── 重试 (最多3次，指数退避)
├── 可降级错误 (复杂度过高)
│   └── 分解任务或使用更强模型
└── 不可恢复错误
    ├── 保存已完成的工作
    ├── 记录错误详情
    └── 通知用户
```

---

### BP-007: 上下文管理

**实践描述**:
有效管理Agent上下文

**具体做法**:
```
1. 子Agent隔离上下文
   - 只传递必要信息
   - 避免上下文污染

2. 定期清理
   - 任务完成后/clear
   - 长对话分段处理

3. 上下文压缩
   - 总结长输出
   - 提取关键信息
```

---

### BP-008: 进度追踪

**实践描述**:
实时追踪复杂任务进度

**追踪机制**:
```markdown
## 任务进度

### 整体进度: [====>    ] 50%

### 子任务状态
| 任务 | Agent | 状态 | 进度 |
|------|-------|------|------|
| Task1 | code-reviewer | ✅ 完成 | 100% |
| Task2 | debugger | 🔄 进行中 | 60% |
| Task3 | architect | ⏳ 等待 | 0% |
```

---

## 领域最佳实践

### 软件开发
- 使用TDD工作流
- 代码审查后再提交
- 小步快跑，频繁验证

### Git 提交规范
- 提交信息**不需要**说明"全局 ~/.claude/CLAUDE.md 同步相同内容"——
  全局配置同步是隐含操作，不在项目提交范围内，无需体现在 commit message 中
- 同理，任何纯粹描述"两处保持一致"的冗余同步说明均可省略

### 网络安全
- 始终在授权范围内
- 先侦察后攻击
- 记录所有操作

### AI智能体
- 模块化设计
- 充分测试边界情况
- 监控成本和性能

### 数据分析
- 先探索后建模
- 验证数据质量
- 可视化驱动洞察

---

## 新增最佳实践

### BP-009: Skill UX 设计原则

**来源**: x-ai-topic-selector v1.0→v1.4 迭代经验

**核心原则**:

1. **并行输入 > 串行确认**
   - ❌ 5 个参数逐步确认，每次执行点 5 次
   - ✅ 一屏显示所有参数，一次选完再执行
   - 效果: 操作从 5 步缩到 1-2 步，配置自动保存供下次复用

2. **根据用户心智模型分离处理流**
   - 书签 = 已人工筛选过的内容 → 适合"分析 + 建议"流程
   - 信息流 = 海量原始内容 → 适合"过滤 + 排序"流程
   - 将两者混用同一逻辑是错误的；识别数据的心智模型，设计对应处理流

3. **输出质量与功能同等重要**
   - 功能跑通只是起点，报告不好读 = 用着别扭
   - 每次输出加"今日看点"摘要，一眼判断值不值得深读
   - 可视化（词云、关键词统计）让信号更清晰

4. **保存用户偏好，减少重复操作**
   - 自动记录上次配置，下次选"使用上次配置"一秒启动
   - 需要调整时展示上次值，方便对比修改

**迭代方法论**: 先跑通 → 实际使用 → 发现不爽 → 修复。不要坐着想"我应该加什么功能"，从自己用着的痛点出发才有价值。

---

### BP-010: Skill 商业化路径

**来源**: Seedance 2.0 系列 Skill 部署经验

**核心洞察**: Claude Code Skill 的用户基数有限（需会用 CC），通过平台部署可触达亿级用户:

```
Claude Code Skill（技术用户）
    ↓ 迁移
Coze 技能商店（豆包/Douyin 生态，亿级用户）
    + 搜索关键词优化（如"一键写好剧本"）
    + 免费开放降低使用门槛
```

**平台选择**:
- **Coze**: 与豆包同系统，直接接触 Douyin 生态用户；技能商店可被搜索发现
- **OpenClaw**: 面向 Claude 生态用户

**关键动作**: Skill 从 CC 迁移到 Coze 后，核心逻辑基本一致，主要工作是适配 Coze 的 skill 格式和发布到商店（填写名称、描述、关键词）。

---

### BP-011: 多模型任务分工原则

**来源**: AI 科研自动化实践经验

**核心洞察**: 没有万能模型，不同认知任务有最优模型分配：

| 任务类型 | 推荐模型 | 原因 |
|----------|---------|------|
| 论文写作/长文生成 | claude-opus-4-6 | 大上下文窗口，表达流畅 |
| 逻辑推理/数学 | claude-sonnet-4-6 | 推理能力强，性价比高 |
| 创意发散/Idea 生成 | grok 系列 | 发散思维强，出奇制胜 |
| 代码实现 | GPT 系列 / claude-sonnet | 代码基准分高 |
| 文献检索引用 | API 查询（非生成） | AI 幻觉问题，必须用真实数据源 |

**反模式（避免）**:
- ❌ 让单一模型包揽所有任务（质量下降 + 成本暴增）
- ❌ 用 LLM 自由生成文献引用（幻觉导致学术不端风险）
- ❌ 用低端模型做顶刊级创新（创新度不足）

**成本控制**: AI 科研全流程非常耗 token，单日千美元量级可能。建议：
- 先用小模型草稿，再用大模型精修
- 文献工作用 Zotero MCP 等工具替代生成
- 科研工作流需要多人协作，单人 ROI 有限

---

### BP-012: Anthropic 官方 Skills 设计最佳实践

**来源**: Anthropic Thariq (Claude Code 团队) 2026-03 公开分享，Anthropic 内部数百个 Skill 实践总结

**Skills 九大分类体系**:

| 分类 | 说明 | 示例 |
|------|------|------|
| **Library & API Reference** | 教模型正确使用库/CLI/SDK | billing-lib, internal-platform-cli |
| **Product Verification** | 测试/验证代码是否正常工作 | signup-flow-driver, checkout-verifier |
| **Data Fetching & Analysis** | 连接数据和监控系统 | funnel-query, grafana |
| **Business Process & Team Automation** | 重复性工作流自动化 | standup-post, weekly-recap |
| **Code Scaffolding & Templates** | 生成框架模板代码 | new-migration, create-app |
| **Code Quality & Review** | 推行代码质量标准 | adversarial-review, testing-practices |
| **CI/CD & Deployment** | 代码推送和部署 | babysit-pr, deploy-service, cherry-pick-prod |
| **Runbooks** | 多工具排查流程 | service-debugging, oncall-runner |
| **Infrastructure Operations** | 日常运维 | resource-orphans, cost-investigation |

**当前项目覆盖情况**:
- ✅ 已覆盖: Library/API (pytorch, pandas), Data Fetching (data-analysis, amazon-analyse), Code Quality (QA 系统)
- ⚠️ 部分覆盖: Business Automation (有 commit/standup 但不完善), Code Scaffolding (parallel-explore)
- ❌ 未覆盖: Product Verification, CI/CD & Deployment, Runbooks, Infrastructure Operations

**10 条 Skill 设计原则**:

1. **只写 Claude 不知道的东西** — Claude 对代码库已有了解，聚焦于能让它跳出常规思维的信息。示例: frontend-design Skill 专门避免"AI 味"（Inter 字体 + 紫色渐变）

2. **认真写 Gotchas 部分** — 任何 Skill 中信噪比最高的内容。从 Claude 反复踩的坑中积累，随时间持续更新

3. **文件系统 = 渐进式上下文** — Skill 是文件夹不只是 Markdown。用 `references/api.md`、`assets/template.md`、`scripts/` 实现按需加载

4. **给出信息但留出灵活度** — Skills 高度可复用，别把指令写得太死。给 Claude 需要的信息，也给它灵活调整的空间

5. **用 config.json 做初始化设置** — 需要用户上下文时，存到 Skill 目录下的 config.json。未配置时用 AskUserQuestion 主动问

6. **Description 是触发器不是摘要** — Claude 靠 description 判断"这个请求有没有对应的 Skill"。写法要像触发条件

7. **让 Skill 拥有记忆** — 用追加写入的日志文件或 JSON。`${CLAUDE_PLUGIN_DATA}` 是稳定数据目录，Skill 目录可能被升级覆盖

8. **给 Claude 可直接用的代码** — 提供脚本和函数库，让 Claude 花精力在组合和决策上而非从零重写

9. **善用 Skill 级别 Hooks** — Skills 可包含只在该 Skill 调用时激活的 hooks。适合放"平时不想开但有时很有用"的强约束（如 `/careful` 拦截危险命令、`/freeze` 锁定编辑范围）

10. **分享策略** — 小团队直接提交到 `.claude/skills/`；规模扩大用 plugin 市场分发。过多 Skills 增加上下文负担

**验证方法**: 对照现有 Skill 逐条审查，识别改进点（如缺少 Gotchas、Description 不够触发式等）

**案例引用**: Anthropic 内部数百个 Skill 实践，frontend-design Skill 消除 AI 味的迭代

---

### BP-013: 并行研究架构中的压缩与隔离权衡

**来源**: ODR (Open Deep Research) 架构分析，与 deep-research Skill 的 Lead Agent + Subagent 模式直接相关

**核心架构模式**:
```
Supervisor (Plan-and-Execute)
  ├─ think_tool → 反思/规划
  ├─ ConductResearch → 派发任务（×N 并行）
  └─ ResearchComplete → 判断信息足够
        ↓
Researcher (ReAct 循环)
  ├─ search → 搜索
  ├─ think_tool → 搜后反思
  └─ ResearchComplete → 信息足够退出
        ↓
compress_research → 保真去重，交回摘要
```

**关键设计洞察**:

1. **两层用不同模式**: Supervisor 用 Plan-and-Execute（可控性），Researcher 用 ReAct（灵活性）。搜索本质是探索性的，ReAct 适配
2. **"空工具"塑造角色**: think_tool 和 ResearchComplete 都是空壳（输入原样返回/终止信号），但定义了"想-做-停"的完整行为空间
3. **两个出口并存**: 模型信号（ResearchComplete）是正常出口，资源上限（max_tool_calls）是安全网
4. **搜-想节奏**: 每次搜索后必须 think_tool 反思（"搜到什么？还缺什么？够了吗？"），不允许连续搜索

**压缩的两层机制**:
- 第一层: 原始网页 → 预处理摘要（~25% 体量），保留 who/what/when/where/why
- 第二层: Researcher 工作历史 → compress_research 结构化摘要（保真去重，非总结）

**并行隔离的收益与代价**:

| 收益 | 代价 |
|------|------|
| 速度: 耗时≈最慢的单条线索 | 跨线索关联在压缩时不可见 |
| 聚焦: 每个 Researcher 上下文干净 | 做判断的模型不知道下游需要什么 |
| 容错: 单条线质量波动不传染 | 压缩是有损的 |
| 上下文效率: 最终能一次综合 | 关联细节可能被丢弃 |

**缓解机制**: 压缩的保真原则、Supervisor 多轮反思、Synthesizer 全局视野、prompt 显式告知隔离存在。每一层都依赖模型判断，是概率性缓解而非结构性保证。

**应用到 deep-research Skill**: 当研究问题本质是因果链而非独立线索时，需要格外关注 Subagent 间的信息传递完整性

**案例引用**: Anthropic Open Deep Research 开源项目架构

---

### BP-014: 极简 Skill 设计哲学

**来源**: liangdabiao simple-review-analyzer 项目，LinuxDo 开源社区

**核心理念**: "以至简达至繁" — 纯 Markdown 指令，不写 Python，不教 AI 做事，让 AI 按指导原则自主解决

**两种 Skill 设计风格对比**:

| 维度 | 结构化风格（当前项目） | 极简风格 |
|------|----------------------|---------|
| 实现方式 | 详细步骤 + 模板 + 脚本 | 纯 Markdown 指导原则 |
| 控制力 | 强（输出格式精确可控） | 弱（依赖 AI 自主判断） |
| 可维护性 | 需要维护脚本和模板 | 几乎零维护 |
| 一致性 | 高（模板保证） | 中（AI 每次可能不同） |
| 灵活性 | 低（模板限制） | 高（AI 自适应） |
| 适合场景 | 生产级、需要稳定输出 | 个人使用、快速迭代 |

**实践建议**: 不必二选一。核心生产 Skill 用结构化风格保证稳定输出；探索性/个人 Skill 可用极简风格快速验证。关键在于明确输入/输出契约和验收标准。

**案例引用**: simple-review-analyzer（GitHub: liangdabiao），buluslan/review-analyzer-skill（22 维度分析的结构化对照）

---

### BP-015: Context Hygiene — 上下文卫生实践

**来源**: Token 优化文章 + Everything Claude Code 上下文腐化分析 + CLAUDE.md 超限事件（lessons-learned #011）

**核心理念**: 上下文工程的核心指标是信噪比 (SNR)，而非总信息量。

**5 习惯**:

1. **精准加载，按需注入** — INDEX → 按需 SKILL.md，不一次性加载所有内容
   - Before: 启动时加载 50K tokens 的全部 Agent 定义
   - After: 加载 600 tokens INDEX，按需加载 3K tokens 单个 Agent

2. **压缩终端输出** — 工具调用后只保留对下一步有用的信息
   - Before: 500 行 npm test 输出全部注入上下文
   - After: "3 tests failed: auth.test.ts:45, user.test.ts:78, api.test.ts:112"

3. **单一事实源** — 每个概念只在一处权威定义，其他地方引用
   - Before: CLAUDE.md 和 docs/ 各写一份完整规则 → 修改时漏改一处 → 矛盾
   - After: CLAUDE.md 写 2-3 行摘要 + 指向 docs/X.md 的链接

4. **定期审计固定上下文税** — 每月审计 CLAUDE.md，目标 ≤39,500 chars
   - 触发条件: CLAUDE.md 接近 39K 或每月例行

5. **避免内容重复** — 重复 = 增大固定税 + 矛盾风险
   - 具体案例: lessons-learned #011 中 Bash 规则 section 嵌入已有 StatusLine 内容导致超限

**两大失效模式**:
- **上下文投毒**: 过时信息残留 → 产出偏差（检测: AI 引用废弃规则）
- **注意力漂移**: 批量任务 >30 项后遗忘约束（检测: 格式漂移/跳步）

**验证方法**: `wc -m CLAUDE.md` < 40000; 新增内容前检查是否已有重复

**案例引用**: lessons-learned.md #011（CLAUDE.md 超限）、#015（批量任务上下文丢失）、`docs/CONTEXT-ENGINEERING-GUIDE.md`

---

### BP-016: Phase-Gated Execution — 阶段门禁执行

**来源**: Superpowers 方法论 + SDD 阶段门禁规则 + 127 只股票批量分析中的格式漂移经验

**核心理念**: 每个阶段结束时都有可验证的验收标准，禁止"跳过规划直接实现"（除非小任务）。

**阶段序列**:

```
brainstorm → spec → plan → execute → review → finish
  (发散)    (定义)  (规划)  (实现)   (验证)   (收尾)
```

**任务规模-流程深度匹配表**:

| 规模 | 预估工时 | 流程 | 可跳过 |
|------|---------|------|--------|
| **小** | ≤1h | brainstorm → execute → finish | spec, plan, review |
| **中** | 1-4h | brainstorm → spec → execute → review → finish | 独立 plan |
| **大** | >4h | 全流程（不可跳过任何阶段） | 无 |

**每步验收标准示例**:

| 阶段 | Before（不合格） | After（合格） |
|------|-----------------|--------------|
| brainstorm | "可以用几种方案做" | "方案 A: JWT+Redis, 方案 B: Session+DB, 推荐 A 因为..." |
| spec | "实现用户认证" | SPEC-user-auth.md 包含 API 列表、数据模型、验收标准 |
| plan | "先做后端再做前端" | 任务拆分为 12 个子任务，有依赖图和时间估算 |
| execute | "代码写完了" | 所有测试通过 + lint 无错误 + 功能演示通过 |
| review | "看了一下没问题" | QA 评分 ≥80，P0/P1 问题清零 |

**禁止行为**:
- ❌ 大任务不经 spec 直接实现
- ❌ 跳过 review 直接发布
- ❌ brainstorm 只列方案不给推荐和理由

**验证方法**: 编排器在任务开始时评估规模 → 自动匹配流程深度 → 在每个门禁检查验收标准

**案例引用**: Superpowers 方法论、spec-writer Agent 的阶段门禁规则、批量股票分析中的格式漂移问题

---

### BP-017: AI 执行安全反模式

**来源**: Vibe Skills 项目实践 + 社区踩坑反馈

**核心洞察**: AI 在执行中容易陷入两类高风险行为，需通过硬性约束（guardrails）而非柔性建议来防治。

**反模式 1: 批量删除**

```
❌ AI 执行 rm *.log / rm -rf temp/ — 批量删除文件
✅ 只允许逐个文件删除，每次删除前确认文件内容
```

**根因**: AI 对文件系统的影响力不对称 — 一次批量删除可瞬间销毁大量数据，而恢复成本极高。AI 在理解"哪些文件可以删"上容易出错（误判临时文件、忽略备份依赖）。

**防治规则**:
- 禁止 `rm *`、`rm -rf`、`find -delete` 等批量删除命令
- 删除前必须逐个确认文件路径和内容摘要
- 特别警惕"清理临时文件"类任务中的误删

**反模式 2: 静默兜底机制**

```
❌ try: result = main_logic() except: result = default_value  # 静默吞掉错误
✅ try: result = main_logic() except Exception as e:
       logger.error(f"⚠️ 兜底机制触发: {e}")  # 必须显式警告
       result = default_value
```

**根因**: AI 倾向于写"保险"的兜底逻辑来确保程序不崩溃，但静默兜底会掩盖功能实现度不足的问题。AI 可能自信地报告"功能已完成"，实际上全是兜底在生效，核心逻辑未真正工作。

**防治规则**:
- 所有兜底机制必须包含 `⚠️ WARNING` 级别的日志输出
- 代码审查时重点检查 catch-all 异常处理是否隐藏了真实错误
- 验收测试必须验证主逻辑路径是否真正执行（而非只走 fallback）

**验证方法**: 对 AI 生成的代码做 grep 检查 — `grep -r "except:" --include="*.py"` 和 `grep -r "catch (" --include="*.ts"` 查找静默异常处理

**案例引用**: Vibe Skills 项目社区反馈 — "AI 喜欢写静默的兜底机制，然后早早的自信满满的给你说做好了，实际上全是兜底机制在发力，主要功能实现度很差"

---

### BP-018: 子代理并行时的 Skills 加载机制

**来源**: Vibe Skills 项目多代理并发编排经验 + 太一元系统编排指南缺失补充

**核心问题**: 当多个子代理并行执行时，每个子代理是否能正确加载所需的 Skills？当前编排指南只描述了 Agent 层级架构和渐进式披露，但完全没有子代理级别的 Skills 加载规范。

**问题场景**:

```
Orchestrator 分解任务为 3 个并行子任务:
├─ Worker-1: 前端开发 → 需要 frontend-design Skill
├─ Worker-2: 数据分析 → 需要 data-analysis Skill
└─ Worker-3: 安全审计 → 需要 security-audit Skill

如果每个 Worker 独立上下文:
- Worker-1 是否会自动读 INDEX.md 并匹配 frontend-design？
- 还是只会盲目执行，丢失专业指导？
```

**规范设计**:

| 层级 | Skills 加载策略 | 说明 |
|------|----------------|------|
| **Orchestrator** | 全量 INDEX.md | 需要全局视野来分配任务和 Skills |
| **Specialist** | 按任务匹配 INDEX + 加载对应 SKILL.md | 在任务分配时由 Orchestrator 指定所需 Skills |
| **Worker** | 继承 Specialist 指定的 SKILL.md | 只加载与当前任务直接相关的 Skills |

**编排器职责增强**:

1. **任务分解时**: 在子代理 prompt 中明确指定需要加载的 Skills（如 "你需要先读取 `.claude/skills/frontend-design/SKILL.md`"）
2. **Skills 传递**: 子代理 prompt 应包含 Skills 的关键约束摘要（即使子代理未读 SKILL.md，也能遵循核心规则）
3. **负向路由**: 明确告知子代理**不需要**加载的 Skills（减少上下文浪费）

**具体做法**:

```
# Orchestrator 分发任务时的 prompt 模板
你负责 {task_description}。
执行前，请先读取以下 Skills:
1. {skill_path_1} — 原因: {why_needed}
2. {skill_path_2} — 原因: {why_needed}

你不需要读取: {excluded_skills}（与当前任务无关）
```

**与上下文工程的协同**: 子代理天然获得独立上下文窗口（见 CONTEXT-ENGINEERING-GUIDE.md 会话管理框架），Skills 加载在独立上下文中进行，不污染父上下文。

**验证方法**: 在下次执行 PARALLEL/HIERARCHICAL 编排时，检查子代理 prompt 是否包含 Skills 指引

**案例引用**: Vibe Skills 项目 "在并行分发任务后，子代理能并行拉起各自任务的skills，实现多代理并发时，skills也会被正确拉起"

---

### BP-019: 长上下文下 Skills 路由失效防护

**来源**: Vibe Skills 项目 4.15 补丁更新 + 太一元系统上下文衰减分析

**核心问题**: 当上下文超过 300-400k tokens（见 CONTEXT-ENGINEERING-GUIDE.md 衰减阈值），Skills 路由匹配的约束力下降 — AI 可能不再按照 Skills 的指导工作，而是退化到"默认行为"。

**失效模式**:

```
正常: 用户请求 → INDEX.md 匹配 → 加载 SKILL.md → 按指导执行
失效: 用户请求 → AI 忽略 INDEX.md → 不加载 Skill → 自由发挥（质量下降）
```

**根因**: Skills 路由依赖 AI 在长上下文中仍然"注意到"路由规则的存在。上下文衰减导致 AI 注意力从系统约束转移到对话内容，路由规则被"挤出"注意力窗口。

**防护策略（三层防御）**:

| 层级 | 策略 | 实现 |
|------|------|------|
| **L1: 主动压缩** | 在 ~250k tokens 时 `/compact` 并附上未来方向 | 见会话管理决策框架 |
| **L2: 路由强化** | 在关键约束中重申 Skills 路由规则 | 关键约束写入 CLAUDE.md（固定上下文） |
| **L3: 执行验证** | 任务完成后检查是否调用了正确的 Skills | 在 review 阶段验证 |

**具体防护规则**:

1. **/compact 指令**: `/compact 保持 Skills 路由规则，保留待办任务列表和当前阶段`
2. **CLAUDE.md 中的路由强化**: 在固定上下文税中保留简短的路由提醒（如 "执行任务前先检查 INDEX.md 匹配 Skill"）
3. **Subagent 隔离**: 大量中间输出的工作交给 Subagent，避免撑大主上下文导致路由失效

**与现有机制的协同**:
- BP-015 Context Hygiene 的习惯 4（审计固定上下文税）— 确保路由提醒在固定税中
- BP-016 Phase-Gated 的 review 阶段 — 增加 Skills 调用验证
- CONTEXT-ENGINEERING-GUIDE.md 的上下文衰减防治 — 量化阈值 + 主动压缩

**验证方法**: 在长会话（>250k tokens）后检查 AI 是否仍然正确匹配和调用 Skills

**案例引用**: Vibe Skills 项目 "防止在超长上下文下，vibe的调用路由因为约束不足而失效的问题"

---

### BP-020: 文件目录语义治理规范

**来源**: Vibe Skills 项目文件语义治理实践 + 太一元系统目录约定散乱现状

**核心问题**: 当前目录结构约定散见于各文件，缺乏统一的语义命名规范。新对话的 AI 需要重新理解"什么目录存什么"，容易遗漏细节导致工作衔接问题。

**Vibe Skills 的四层语义模型**:

| 目录 | 语义层 | 存什么 | 不存什么 |
|------|--------|--------|---------|
| `docs/` | 解释层 | 说明文档、指南、架构设计 | 运行时产物、临时文件 |
| `config/` | 合同层 | 配置文件、路由规则、Agent 定义 | 脚本、代码 |
| `scripts/` | 执行层 | 可执行脚本、工具、自动化 | 文档、配置 |
| `references/` | 长期资产层 | 模板、参考数据、知识库 | 运行时状态 |
| `outputs/runtime/` | 运行证据层 | 日志、执行记录、临时输出 | 源代码、配置 |

**太一元系统现有目录对照**:

| 语义层 | Vibe 目录 | 太一现有目录 | 差距 |
|--------|----------|-------------|------|
| 解释层 | `docs/` | `docs/` | ✅ 一致 |
| 合同层 | `config/` | `config/` + `.claude/settings.json` | ⚠️ Agent 定义在 `agents/`，分散 |
| 执行层 | `scripts/` | `hooks/` + `scripts/` | ✅ 基本一致 |
| 长期资产层 | `references/` | `memory/` + `.claude/skills/` | ⚠️ memory 含运行时状态 |
| 运行证据层 | `outputs/runtime/` | 无统一目录 | ❌ 散落各处 |

**建议改进（低优先级，避免破坏现有结构）**:

1. **运行时产物与长期资产分离**: Vibe 项目的做法 — 工作区运行时文件放到 `.vibeskills/`（或 `.taiyi/runtime/`），和核心项目根目录文档分离
2. **新增目录时的语义审批**: 确认新目录属于哪一语义层，避免层间混用
3. **AI 接手工作区时的快速理解**: 在项目根目录的 README 或 CLAUDE.md 中用 5 行说明目录语义

**关键原则**: 文件目录语义治理的核心目标是让**新的 AI 对话**能快速理解工作区结构，减少"重新理解"的成本和遗漏。

**案例引用**: Vibe Skills 项目 "按固定化的架构存储文件，让下一个新的对话的AI明白什么什么目录下存储什么什么文件" + "修复工作区记忆和核心区的文件杂糅的问题"


# 记忆与 Skill 盘点结论（2026-11-21）

## 范围与判定边界

本轮对两本记忆库做全量结构扫描，以下目录覆盖 57 个 BP 与 25 个经验条目。
“保留历史参考”不等于证明原文至今正确；未把年龄、篇幅或缺少观测当作删除依据。
两本文件入口已明确历史证据与当前执行规则的区别，当前行为仍以 AGENTS.md、当前 Spec 和实现为准。

- 已局部替代：BP-041 的旧同步方向、标题“CLAUDE.md 超过 40k 字符阈值”的旧预算建议。
- 原有废弃记录保留；历史重号不重新编号，查找时使用日期与完整标题。
- 全部历史正文保留，没有批量补造 UNVERIFIED、验证次数或置信度。
- 精确检索可用 rg 搜索下表完整标题，再读取对应条目；不把两本书默认灌入上下文。
- 本表是结构盘点与治理结论，不是全库外部事实复核证明；外部实验数字不被提升为本项目验收阈值。

## Skill 结构与使用证据

全部 57 个 Skill 可移植 YAML 检查通过；architecture-copilot 补齐原先缺失的头部。
自定义 version/trigger/type 等移入 metadata，迁移时 57 份正文逐一哈希核对未变；
之后创作模板、流程边界及失效导航指针另作明确修正，防止继续生成无效字段或读取已移除的章节；对应改动见 diff。
保留合法 compatibility 字段；旧版 Codex quick_validate 的五字段限制不用于删除标准支持的环境说明。

仅扫描本项目目录中的 11 份会话 JSONL，显式 Skill 工具调用观测为 0。
这不是 0% 激活率：slash 展开、直接读取角色和其他会话可能不在该观测内。
因此本轮不据此停用或拆卸任何 Skill；该项以“证据不足，不作破坏性优化”结案。
没有导出提示词、会话正文或其他项目日志。

## 条目目录

状态仅表示本轮处置，不表示事实置信度。路径和完整标题用于定位，行号省略以避免后续插入造成漂移。

| 库 | 完整标题 | 本轮处置 |
|----|----------|----------|
| best-practices.md | BP-001: 任务分解原则 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-002: 策略选择决策树 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-003: Agent 能力匹配 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-004: 并行任务优化 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-005: 结果整合策略 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-006: 错误恢复策略 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-007: 上下文管理 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-008: 进度追踪 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-009: Skill UX 设计原则 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-010: Skill 商业化路径 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-011: 多模型任务分工原则 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-012: Anthropic 官方 Skills 设计最佳实践 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-013: 并行研究架构中的压缩与隔离权衡 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-014: 极简 Skill 设计哲学 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-015: Context Hygiene — 上下文卫生实践 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-016: Phase-Gated Execution — 阶段门禁执行 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-017: AI 执行安全反模式 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-018: 子代理并行时的 Skills 加载机制 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-019: 长上下文下 Skills 路由失效防护 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-020: 文件目录语义治理规范 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-021: Agent 协作协议与任务地图 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-022: 第三方 Skill/Agent 引入前审查 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-023: AI 协作中的效率幻觉防护 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-024: 能力路由优先于工具堆叠 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-025: 上下文注入模式——启动注入 vs 按需查询 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-026: CLAUDE.md 规则提炼原则——好规则是摔出来的 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-028: 失败归因协议——分清谁的错 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-027: 经验录入标准——从具体翻车现场来，不从推测来 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-029: 自进化闭环执行保障——五断裂点防治 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-030: UI-First 开发方法论——视觉验证优先于文字规范 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-031: 科研论文工具链——Nature 期刊标准参考 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-032: VFM 评分模型——经验晋升的量化门槛 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-033: 四类工程偏差诊断框架 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-034: Tavily MCP 搜索能力路由——与 WebSearch/Exa 的分工 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-035: 假闭环诊断清单（Self-Evolution Loop Integrity Check） | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-036: 防御纵深模型——CLAUDE.md 在保障栈中的位置 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-037: 事故驱动规则增长——不从推测来 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-038: 视觉验证反馈环——看比读快 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-039: 对话历史作为知识资产——会话即文档 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-040: 一源多产模式——单一资产的多格式输出 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-041: 全局/项目配置同步策略——分层归属 + diff 优先 | 局部替代，原案例保留 |
| best-practices.md | BP-042: Pairwise Skills 模式——精确率从 21% 跃升至 95% 的关键设计 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-043: 知识域 Skill 离线评估协议——持续确保准确率不回退 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-044: 主动知识库自修复——定时 Agent 扫描纠错信号自动开 PR | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-045: 创作类长任务 Skill 工作流——模型选型与分阶段迭代原则 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-046: Karpathy 规则——AI 协作的四条行为约束 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-047: 自我改进 Agent 复利栈——模型不变，环境变聪明 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-048: SkillOpt 六阶段管线——把 Skill 当神经网络权重训练 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-049: Harness 五步增量法——按错误驱动补层，不要一次搭满 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-050: Skill 发布质量四阶梯——从"能用"到"能发布" | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-051: 任务偏差根因六分类（R1-R6）——规范进化的合法依据 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-052: AI 时代 Review 按风险分层——别再"所有 PR 一视同仁" | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-053: Agent 时代必须显式恢复"意图"——diff 不带推理，Reviewer 没法重建 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-054: 自进化的样本隔离纪律——训练 / 验证 / 测试三段不可互通 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-055: PM 头脑风暴反模式黑名单——8 个常见陷阱 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-056: 多模型 Fusion 协作模式——单模型不是终点 | 保留历史参考，复用前核对现状 |
| best-practices.md | BP-057: AutoResearch 三层协议——可执行检查清单 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-03-02] Ralph Stop Interceptor 三大 Bug 修复 #013 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-02-21] statusline 不显示 - session_id 检测误杀 Stop 事件 #012 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-02-20] statusline 竖排显示 - 启动时 JSON 无 cost 字段导致误渲染 #011 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-02-20] hud-v2.sh 数据源全面错误 + 跨会话 Edit 陷阱 #010 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-02-20] Windows Hooks/Statusline 静默失败三连击 #009 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-01-24] Stop Hook 执行失败 - Bash 脚本错误处理 #008 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [初始化] 系统启动 #000 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-01-23] OpenAPI 转换器 Windows 编码问题修复 #001 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-01-23] OpenAPI 转换器成功集成 TikHub API #002 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-01-24] 全局 Hooks 配置 Matcher 格式错误 #004 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-01-24] ⚠️ **已废弃** - Hooks 配置格式误解 #003 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-01-24] Hooks 配置统一格式规范 #005 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-01-24] Git Bash 路径配置错误导致 Hooks 执行失败 #006 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-01-24] Statusline 不显示 - 缺少全局配置 #007 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-01-24] 配置文件位置混淆导致多次错误尝试 #008 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-01-26] Skills/Pipeline 设计模式学习与融合 #009 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-02-20] StatusLine 对话启动时竖排显示 #010 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-02-20] CLAUDE.md 超过 40k 字符阈值 #011 | 局部替代，原案例保留 |
| lessons-learned.md | [2026-03-02] 外部 Claude Code Agent 项目学习：互联网指标缺口与 SWARM 模式 #013 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-03-11] 产品设计系统案例学习：半自动复盘与知识质量控制 #014 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-03-13] 大批量任务的认知上下文持久化：planning-with-files 模式 #015 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | [2026-06-16] 二次审视学习价值：避免「快筛」丢失中等价值信号 #016 | 保留历史参考，复用前核对现状 |
| lessons-learned.md | 2026-06-28 经验条目 #compass-handoff | 保留历史参考，复用前核对现状 |
| lessons-learned.md | 2026-06-28 经验条目 #llm-wiki | 保留历史参考，复用前核对现状 |
| lessons-learned.md | 2026-11-19 经验条目 #hooks-spec-drift | 保留历史参考，复用前核对现状 |

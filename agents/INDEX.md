# Agent 路由索引

由 `python scripts/build-agent-index.py` 生成；按任务选择一项，再读取对应文件。

| Agent | 用途 | 定义 |
|---|---|---|
| deep-learning | 深度学习专家（Deep Learning Agent），负责神经网络设计、模型训练、超参数优化和模型部署。 | [ai/deep-learning.md](ai/deep-learning.md) |
| model-interpretability | 模型可解释性专家（Model Interpretability Agent），负责模型解释、特征重要性分析、决策可视化和公平性审计。 | [ai/model-interpretability.md](ai/model-interpretability.md) |
| reinforcement-learning | 强化学习专家（Reinforcement Learning Agent），负责环境建模、策略设计、训练优化和智能体部署。 | [ai/reinforcement-learning.md](ai/reinforcement-learning.md) |
| time-series-analysis | 时间序列分析专家（Time Series Analysis Agent），负责时间序列预测、异常检测、趋势分析和因果推断。 | [ai/time-series-analysis.md](ai/time-series-analysis.md) |
| architect | 软件架构师，用于系统设计、架构决策和技术方案规划。进行架构级别工作时主动使用。 | [architect.md](architect.md) |
| code-reviewer | 专业代码审查员。在编写或修改代码后主动使用此代理进行代码审查。 | [code-reviewer.md](code-reviewer.md) |
| codemap-builder | 构建代码地图，生成结构化的代码库导航文档 | [codemap-builder.md](codemap-builder.md) |
| data-warehouse-analyst | 数据仓库查询分析师，专注于将用户问题精确映射到数据仓库实体，采用 Anthropic Pairwise Skills 设计模式。适用于数据平台/BI 系统/多维分析场景。 | [data/data-warehouse-analyst.md](data/data-warehouse-analyst.md) |
| data-scientist | 数据科学专家，用于SQL查询、数据分析和洞察提取。进行数据分析任务时主动使用。 | [data-scientist.md](data-scientist.md) |
| debugger | 调试专家，用于处理错误、测试失败和异常行为。遇到任何问题时主动使用此代理。 | [debugger.md](debugger.md) |
| god-consensus | God Committee Consensus Engine - Facilitates deliberation, manages voting, and record… | [god-committee/god-consensus.md](god-committee/god-consensus.md) |
| god-intervention | God Committee Intervention Executor - Executes approved interventions, manages snapsh… | [god-committee/god-intervention.md](god-committee/god-intervention.md) |
| god-member | God Committee Member - Independent oversight agent responsible for system monitoring,… | [god-committee/god-member.md](god-committee/god-member.md) |
| auto-optimizer | 基于性能数据自动优化系统配置和Agent表现 | [ops/auto-optimizer.md](ops/auto-optimizer.md) |
| autopilot-orchestrator | 全自主编排器 (Autonomous Orchestrator)，整合 Ralph Loop、Orchestrator 和 QA 系统，实现端到端任务自动执行。 | [ops/autopilot-orchestrator.md](ops/autopilot-orchestrator.md) |
| context-archivist | 对话归档器（Conversation Archivist），负责将长对话提炼为可复用的工程上下文。 | [ops/context-archivist.md](ops/context-archivist.md) |
| performance-monitor | 监控和分析Agent性能数据，生成洞察报告 | [ops/performance-monitor.md](ops/performance-monitor.md) |
| strategy-selector | 分析任务特征并推荐最优编排策略的决策专家 | [ops/strategy-selector.md](ops/strategy-selector.md) |
| orchestrator | 元编排者 - 负责任务分解、Agent调度、策略选择和结果整合。处理复杂多步骤任务时自动激活。 | [orchestrator.md](orchestrator.md) |
| qa-fixer | 自动修复QA Reviewer发现的问题 | [qa-fixer.md](qa-fixer.md) |
| qa-reviewer | 按任务风险核对验收标准、测试证据和阻塞缺陷 | [qa-reviewer.md](qa-reviewer.md) |
| requirements-analyst | Use this agent when you need to analyze software requirements, break down complex use… | [requirements-analyst.md](requirements-analyst.md) |
| data-analyst | 数据分析专家（Data Analyst），负责实验数据分析、可视化、统计检验和结果解读。 | [research/data-analyst.md](research/data-analyst.md) |
| experiment-logger | 实验记录专家（Experiment Logger），负责结构化实验记录、参数管理、结果追踪和复现指南生成。 | [research/experiment-logger.md](research/experiment-logger.md) |
| literature-manager | 文献管理专家（Literature Manager），负责文献导入、分类、摘要、推荐和引用图谱构建。 | [research/literature-manager.md](research/literature-manager.md) |
| paper-writing-assistant | 论文写作助手（Paper Writing Assistant），基于 Vibe Researching 理念，辅助完成文献综述和研究论文的写作。 | [research/paper-writing-assistant.md](research/paper-writing-assistant.md) |
| router | 你是 Router Agent，系统的统一入口和任务分发中心。你不执行具体任务，而是理解用户意图，匹配最合适的 Agent/Skill 组合，并进行智能调度。 | [router.md](router.md) |
| sdd-riper-orchestrator | SDD-RIPER 编排者 - 负责执行 Spec-Driven Development + RIPER 五阶段流程，确保大模型编程的质量可控、过程可追溯。 | [sdd-riper-orchestrator.md](sdd-riper-orchestrator.md) |
| security-analyst | 安全分析专家，用于代码安全审计、漏洞分析和安全建议。处理安全相关任务时主动使用。 | [security/security-analyst.md](security/security-analyst.md) |
| security-audit | 安全审计专家（Security Audit Agent），负责代码安全审计、漏洞扫描、安全配置检查和合规性验证。 | [security/security-audit.md](security/security-audit.md) |
| senior-code-architect | Use this agent when you need expert-level code review, architecture decisions, or fra… | [senior-code-architect.md](senior-code-architect.md) |
| spec-writer | 生成详细的功能规范文档 | [spec-writer.md](spec-writer.md) |
| tech-mentor | Use this agent when you need comprehensive technical guidance, full-stack architectur… | [tech-mentor.md](tech-mentor.md) |
| automated-testing | 自动化测试专家（Automated Testing Agent），负责测试策略设计、测试用例生成、测试执行和覆盖率分析。 | [testing/automated-testing.md](testing/automated-testing.md) |
| data-visualization | 数据可视化专家（Data Visualization Agent），负责数据探索、图表设计、交互式可视化和报告生成。 | [visualization/data-visualization.md](visualization/data-visualization.md) |
| vitest-tester | Use this agent when you need to create, review, or debug tests using the Vitest testi… | [vitest-tester.md](vitest-tester.md) |

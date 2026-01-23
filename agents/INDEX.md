# Agent索引 - 渐进式披露系统

> **设计理念**: 仅在需要时加载完整Agent定义，节省60-80% Token开销

## 使用说明

### 加载策略
1. **首次阅读**: 仅读取本INDEX.md，了解可用Agent概览
2. **按需加载**: 根据任务需求，加载对应Agent的完整定义文件
3. **智能匹配**: 根据任务特征自动选择最合适的Agent

### 性能优化
- **Token节省**: INDEX文件 ~500 tokens vs 所有Agent ~6000 tokens
- **加载时间**: 减少90%的初始上下文加载时间
- **精准匹配**: 避免无关Agent信息干扰

---

## Agent目录

### 规划类 (Planning)

#### orchestrator
```yaml
文件: agents/orchestrator.md
模型: opus
工具: Read, Write, Edit, Bash, Grep, Glob, Task
描述: 元编排者 - 负责任务分解、Agent调度、策略选择和结果整合
适用: 复杂多步骤任务、需要多Agent协作的场景
专长:
  - 任务分解与依赖分析
  - 编排策略选择(并行/串行/层级/协作/竞争/群体)
  - Agent调度与负载均衡
  - 结果整合与质量控制
触发: 自动激活于复杂任务
```

#### architect
```yaml
文件: agents/architect.md
模型: opus
工具: Read, Grep, Glob, Bash
描述: 软件架构师 - 系统设计、架构决策和技术方案规划
适用: 架构设计、技术选型、系统重构
专长:
  - 需求分析与架构建模
  - 设计模式应用(分层/微服务/事件驱动)
  - 技术选型矩阵分析
  - 可扩展性与安全架构设计
触发: 需要架构级别决策时
```

---

### 开发类 (Development)

#### code-reviewer
```yaml
文件: agents/code-reviewer.md
模型: sonnet
工具: Read, Grep, Glob, Bash
描述: 专业代码审查员 - 确保代码质量和安全性
适用: 代码提交前审查、重构建议
专长:
  - 代码质量检查(可读性/规范/重复代码)
  - 安全性审计(密钥泄露/注入风险/XSS)
  - 性能优化建议
  - 测试覆盖度评估
触发: 编写或修改代码后主动使用
```

#### debugger
```yaml
文件: agents/debugger.md
模型: sonnet
工具: Read, Edit, Bash, Grep, Glob
描述: 调试专家 - 处理错误、测试失败和异常行为
适用: Bug修复、错误诊断、问题排查
专长:
  - 根本原因分析(RCA)
  - 运行时/逻辑/并发/集成问题定位
  - 最小修复方案
  - 防御性代码添加
触发: 遇到任何问题时主动使用
```

---

### 质量类 (Quality)

#### security-analyst
```yaml
文件: agents/security-analyst.md
模型: sonnet
工具: Read, Grep, Glob, Bash
描述: 安全分析专家 - 代码安全审计、漏洞分析和安全建议
适用: 安全审计、漏洞扫描、合规检查
专长:
  - OWASP Top 10检查
  - 依赖漏洞扫描(CVE)
  - 危险代码模式识别
  - 安全配置验证
触发: 处理安全相关任务时
```

---

### 专业类 (Specialized)

#### data-scientist
```yaml
文件: agents/data-scientist.md
模型: sonnet
工具: Bash, Read, Write
描述: 数据科学专家 - SQL查询、数据分析和洞察提取
适用: 数据分析、SQL优化、统计分析
专长:
  - SQL查询编写与优化
  - 数据探索与质量分析
  - 统计方法应用(假设检验/相关性分析)
  - 可视化建议
触发: 数据分析任务时
```

#### strategy-selector
```yaml
文件: agents/strategy-selector.md
模型: sonnet
工具: Read, Grep, Glob
描述: 策略选择专家 - 分析任务特征并推荐最优编排策略
适用: 复杂任务规划、编排策略决策
专长:
  - 任务特征分析(复杂度/依赖/领域/规模)
  - 编排策略推荐(PARALLEL/SEQUENTIAL/HIERARCHICAL等)
  - 性能预测与成本估算
触发: orchestrator调用或手动策略选择
```

#### spec-writer
```yaml
文件: agents/spec-writer.md
模型: sonnet
工具: Read, Glob, Grep, Write
描述: 规范编写专家 - 生成详细的功能规范文档
适用: 新功能开发、需求文档化
专长:
  - 需求分析与澄清
  - 技术方案设计
  - 验收标准定义
  - 风险识别
触发: Spec-First开发流程
```

#### qa-reviewer
```yaml
文件: agents/qa-reviewer.md
模型: sonnet
工具: Read, Grep, Glob, Bash
描述: 质量审查专家 - 验证代码是否满足验收标准
适用: 开发完成后的质量验证
专长:
  - 功能完整性验证
  - 代码质量评估
  - 测试覆盖率检查
  - 性能和安全指标验证
触发: 开发完成后自动或手动触发
```

#### qa-fixer
```yaml
文件: agents/qa-fixer.md
模型: sonnet
工具: Read, Edit, Write, Bash
描述: 自动修复专家 - 修复QA Reviewer发现的问题
适用: 自动修复低风险问题
专长:
  - 问题解析与分类
  - 自动修复(格式/类型/简单逻辑)
  - 修复验证
触发: QA Reviewer发现P2问题时
```

#### performance-monitor
```yaml
文件: agents/performance-monitor.md
模型: sonnet
工具: Read, Write, Glob, Bash
描述: 性能监控专家 - 监控和分析Agent性能数据
适用: 性能分析、趋势识别、异常检测
专长:
  - 性能数据收集与分析
  - 趋势分析和异常检测
  - 性能报告生成
触发: 定期或按需生成性能报告
```

#### auto-optimizer
```yaml
文件: agents/auto-optimizer.md
模型: sonnet
工具: Read, Edit, Write, Glob
描述: 自动优化专家 - 基于性能数据优化系统配置
适用: 系统优化、成本降低、性能提升
专长:
  - 优化机会识别
  - 优化方案设计
  - A/B测试与效果验证
触发: 性能监控发现优化机会时
```

#### context-archivist
```yaml
文件: agents/context-archivist.md
模型: sonnet
工具: Read, Write, Grep, Glob
描述: 上下文归档专家 - 提炼对话中的关键信息并结构化沉淀
适用: 上下文压缩前、项目状态记录
专长:
  - 关键信息提炼
  - 问题解决方案归档
  - 渐进式上下文注入
触发: PreCompact Hook或手动保存
```

---

### 科研类 (Research)

#### literature-manager
```yaml
文件: agents/research/literature-manager.md
模型: sonnet
工具: Read, Grep, Glob, Bash
描述: 文献管理专家 - 文献导入、分类、摘要提取
适用: 学术研究、文献综述
专长:
  - 文献导入和分类
  - 智能摘要提取
  - 引用图谱构建
  - 相关文献推荐
集成: Zotero-MCP, arXiv/PubMed MCP
触发: 文献管理任务
```

#### paper-writing-assistant
```yaml
文件: agents/research/paper-writing-assistant.md
模型: opus
工具: Read, Write, Grep, Glob
描述: 论文写作助手 - 文献综述生成、研究论文撰写
适用: 学术论文写作、综述生成
专长:
  - 文献综述生成
  - 写作风格学习
  - 自动引用管理
  - 论文结构优化
触发: 论文写作任务
```

#### experiment-logger
```yaml
文件: agents/research/experiment-logger.md
模型: sonnet
工具: Read, Write, Bash
描述: 实验记录专家 - 结构化实验记录和追踪
适用: 实验管理、结果追踪
专长:
  - 结构化实验记录
  - 参数和配置管理
  - 结果追踪和对比
  - 复现指南生成
触发: 实验追踪任务
```

#### data-analyst (research)
```yaml
文件: agents/research/data-analyst.md
模型: sonnet
工具: Bash, Read, Write
描述: 数据分析专家 - 数据预处理、统计分析、可视化
适用: 科研数据分析、结果解读
专长:
  - 数据预处理和清洗
  - 统计分析和假设检验
  - 高质量可视化
  - 结果解读
集成: Jupyter Notebook, LaTeX
触发: 数据分析任务
```

---

### AI/ML类 (AI/ML)

#### deep-learning
```yaml
文件: agents/ai/deep-learning.md
模型: sonnet
工具: Bash, Read, Write
描述: 深度学习专家 - 模型架构设计、训练和部署
适用: 深度学习模型开发
专长:
  - 模型架构设计(CNN/RNN/Transformer/GAN)
  - 模型训练和超参数优化
  - 模型评估和部署
集成: PyTorch, TensorFlow, Hugging Face
触发: 深度学习任务
```

#### reinforcement-learning
```yaml
文件: agents/ai/reinforcement-learning.md
模型: sonnet
工具: Bash, Read, Write
描述: 强化学习专家 - 环境建模、策略设计、算法实现
适用: 强化学习问题
专长:
  - 环境建模和策略设计
  - 算法实现(DQN/PPO/SAC/MADDPG)
  - 训练优化和性能评估
集成: Stable-Baselines3, RLlib, OpenAI Gym
触发: 强化学习任务
```

#### time-series-analysis
```yaml
文件: agents/ai/time-series-analysis.md
模型: sonnet
工具: Bash, Read, Write
描述: 时间序列分析专家 - 预测、异常检测、趋势分析
适用: 时间序列数据分析
专长:
  - 时间序列预测(ARIMA/Prophet/LSTM)
  - 异常检测和趋势分析
  - 因果推断
集成: statsmodels, Prophet, PyTorch Forecasting
触发: 时间序列分析任务
```

#### model-interpretability
```yaml
文件: agents/ai/model-interpretability.md
模型: sonnet
工具: Bash, Read, Write
描述: 模型可解释性专家 - 模型解释、调试、公平性审计
适用: 模型可解释性分析
专长:
  - 全局和局部可解释性(SHAP/LIME)
  - 模型调试和公平性审计
  - 可解释性报告生成
集成: SHAP, LIME, Captum, Fairlearn
触发: 模型可解释性任务
```

---

### 测试类 (Testing)

#### automated-testing
```yaml
文件: agents/testing/automated-testing.md
模型: sonnet
工具: Bash, Read, Write
描述: 自动化测试专家 - 测试策略设计和用例生成
适用: 测试用例生成、测试执行
专长:
  - 测试策略设计
  - 测试用例生成
  - 测试执行和覆盖率分析
集成: pytest, Jest, coverage.py
触发: 测试任务
```

---

### 可视化类 (Visualization)

#### data-visualization
```yaml
文件: agents/visualization/data-visualization.md
模型: sonnet
工具: Bash, Read, Write
描述: 数据可视化专家 - 数据探索和图表设计
适用: 数据可视化、报告生成
专长:
  - 数据探索和图表设计
  - 交互式可视化
  - 报告生成
集成: matplotlib, plotly, seaborn
触发: 数据可视化任务
```

---

### 安全类 (Security)

#### security-audit
```yaml
文件: agents/security/security-audit.md
模型: sonnet
工具: Bash, Read, Write
描述: 安全审计专家 - 代码安全审计、依赖扫描、合规验证
适用: 安全审计、漏洞扫描
专长:
  - 代码安全审计(SQL注入/XSS/CSRF)
  - 依赖安全扫描
  - 合规性验证(GDPR/HIPAA)
集成: Bandit, Snyk, TruffleHog
触发: 安全审计任务
```

---

## 编排策略速查

| 任务特征 | 推荐策略 | 使用Agent |
|----------|----------|-----------|
| 独立子任务 | **PARALLEL** | 多个同类Agent并行 |
| 依赖链任务 | **SEQUENTIAL** | 按顺序传递 |
| 复杂决策 | **HIERARCHICAL** | architect/orchestrator领导 |
| 跨领域问题 | **COLLABORATIVE** | 多专家Agent讨论 |
| 探索性任务 | **COMPETITIVE** | 多Agent方案竞争 |
| 大规模任务 | **SWARM** | 大量Worker协作 |

---

## 智能加载指引

### 场景1: 代码审查
```markdown
需要加载: code-reviewer.md
可选加载: security-analyst.md (如涉及安全)
```

### 场景2: 系统设计
```markdown
必须加载: architect.md
可选加载: orchestrator.md (大型项目)
```

### 场景3: Bug修复
```markdown
需要加载: debugger.md
后续加载: code-reviewer.md (修复后审查)
```

### 场景4: 复杂任务
```markdown
首先加载: orchestrator.md
由orchestrator决定加载其他Agent
```

---

## 模型选择建议

| 模型 | 适用场景 | Token成本 | 速度 |
|------|----------|-----------|------|
| **opus** | 复杂决策、架构设计、编排任务 | 高 | 慢 |
| **sonnet** | 代码实现、审查、调试、分析 | 中 | 中 |
| **haiku** | 快速搜索、简单查询 | 低 | 快 |

---

## 更新日志

### 2026-01-23
- 扩展到25个Agent，覆盖所有专业领域
- 新增分类: 科研类、AI/ML类、测试类、可视化类、安全类
- 完善渐进式披露机制，支持100+ Agent扩展

### 2026-01-16
- 初始版本创建
- 包含6个核心Agent: orchestrator, architect, code-reviewer, debugger, security-analyst, data-scientist
- 实施渐进式披露机制

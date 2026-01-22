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

### 2026-01-16
- 初始版本创建
- 包含6个核心Agent: orchestrator, architect, code-reviewer, debugger, security-analyst, data-scientist
- 实施渐进式披露机制

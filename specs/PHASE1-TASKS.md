# Phase 1 实施任务清单

> 2026-11-23 实现状态见 [实施与验收记录](../docs/IMPROVEMENT-IMPLEMENTATION.md)，执行接口以 [运行时契约](SPEC-improvement-runtime.md) 为准。下文保留原始方案背景；示例路径、自动执行、外部安装与收益数字不视为已验证事实。

本文档列出短期（1-2个月）实施的具体任务，可直接转换为GitHub Issues。

## 🎯 总体目标

在2个月内完成三个轻量级方案的核心实现：
1. 上下文优化系统（节省30%+ token）
2. 双系统决策机制（常规决策<1秒）
3. 证据驱动验证（所有新记忆带证据）

---

## 📋 任务列表

### 模块1: 上下文优化系统

#### Task 1.1: 决策路由Hook
**优先级**: P0\
**预估**: 2天\
**负责人**: TBD

**交付物**:
- `.claude/hooks/pre-tool-call.py` - 工具调用前路由判断
- `.claude/hooks/post-tool-call.py` - 结果摘要注入

**验收标准**:
- [ ] 识别批量Read模式（连续3次同目录）
- [ ] 识别重复Grep（连续3次）
- [ ] 大文件（>100KB）建议流式处理
- [ ] 单元测试覆盖率>80%

**依赖**: 无

---

#### Task 1.2: 记忆快速检索
**优先级**: P1\
**预估**: 1天\
**负责人**: TBD

**交付物**:
- `memory/.cache/index.db` - SQLite FTS5索引
- `commands/memory/quick-search.py` - 检索接口
- `scripts/rebuild-memory-index.py` - 索引重建工具

**验收标准**:
- [ ] 索引所有memory/*.md文件
- [ ] 检索延迟<200ms
- [ ] 支持模糊匹配（Levenshtein距离）
- [ ] 自动检测索引版本不一致

**依赖**: 无

---

#### Task 1.3: 集成测试
**优先级**: P1\
**预估**: 1天\
**负责人**: TBD

**交付物**:
- `tests/context/test_routing.py` - 路由测试
- `tests/context/test_memory_search.py` - 检索测试
- `scripts/measure-token-savings.py` - Token节省率测量

**验收标准**:
- [ ] 10个典型场景全部通过
- [ ] 实际测量Token节省率>30%
- [ ] 无误判导致任务失败

**依赖**: Task 1.1, 1.2

---

### 模块2: 双系统决策机制

#### Task 2.1: 决策路由引擎
**优先级**: P0\
**预估**: 2天\
**负责人**: TBD

**交付物**:
- `.claude/agents/router/decision_engine.py` - 核心引擎
- `.claude/agents/router/pattern_matcher.py` - 模式匹配
- `.claude/agents/router/similarity.py` - 相似度计算

**验收标准**:
- [ ] 实现4层决策树（简单命令/Playbook/历史任务/兜底）
- [ ] 简单命令匹配准确率>90%
- [ ] 决策延迟<100ms（规则匹配）
- [ ] 决策延迟<1s（Playbook匹配）

**依赖**: 无

---

#### Task 2.2: Playbook系统
**优先级**: P0\
**预估**: 1天\
**负责人**: TBD

**交付物**:
- `memory/playbooks/install-global/latest.md`
- `memory/playbooks/backup-strategy/latest.md`
- `memory/playbooks/rule-audit/latest.md`
- `memory/playbooks/loader.py` - 加载器

**验收标准**:
- [ ] 迁移3个现有流程到Playbook
- [ ] 支持关键词匹配
- [ ] 记录成功率（success_rate字段）
- [ ] Playbook可版本化管理

**依赖**: 无

---

#### Task 2.3: 失败记忆系统
**优先级**: P1\
**预估**: 1天\
**负责人**: TBD

**交付物**:
- `memory/failures/backup-collision.md`
- `memory/failures/windows-path-encoding.md`
- `memory/failures/permission-denied.md`
- `.claude/hooks/on-task-failure.py` - 自动记录Hook

**验收标准**:
- [ ] 迁移3个已知失败案例
- [ ] 失败模式可正则匹配
- [ ] 记录触发条件和解决方案
- [ ] 100%阻止已知错误重现

**依赖**: 无

---

#### Task 2.4: 决策日志收集
**优先级**: P1\
**预估**: 1天\
**负责人**: TBD

**交付物**:
- `.claude/hooks/post-decision.py` - 日志记录
- `memory/decisions/decision-log.jsonl` - 日志文件
- `scripts/analyze-decisions.py` - 分析工具

**验收标准**:
- [ ] 记录每次决策及结果
- [ ] 包含task/decision/outcome/duration/cost
- [ ] 分析工具可计算准确率
- [ ] 识别高频模式

**依赖**: Task 2.1

---

#### Task 2.5: 集成测试
**优先级**: P1\
**预估**: 1天\
**负责人**: TBD

**交付物**:
- `tests/decision/test_router.py`
- `tests/decision/test_playbook.py`
- `scripts/test-decision-scenarios.py` - 10个场景

**验收标准**:
- [ ] 10个典型场景全部通过
- [ ] 决策准确率>85%
- [ ] 重复任务执行时间减少>40%

**依赖**: Task 2.1-2.4

---

### 模块3: 证据驱动验证

#### Task 3.1: 证据Schema设计
**优先级**: P0\
**预估**: 1天\
**负责人**: TBD

**交付物**:
- `memory/schemas/evidence-v1.yaml` - Schema定义
- `memory/schemas/validator.py` - 验证器
- `docs/EVIDENCE-GUIDE.md` - 使用文档

**验收标准**:
- [ ] 定义5种证据类型（test/commit/measurement/observation/documentation）
- [ ] 验证器可检查格式正确性
- [ ] 文档包含示例和最佳实践

**依赖**: 无

---

#### Task 3.2: 查询接口
**优先级**: P0\
**预估**: 2天\
**负责人**: TBD

**交付物**:
- `memory/evidence/query.py` - EvidenceQuery类
- `scripts/evidence-cli.py` - 命令行工具

**验收标准**:
- [ ] 加载记忆及其证据
- [ ] 按置信度筛选
- [ ] 追溯证据链（递归）
- [ ] 验证证据有效性
- [ ] 查询延迟<100ms

**依赖**: Task 3.1

---

#### Task 3.3: 可视化Skill
**优先级**: P1\
**预估**: 1天\
**负责人**: TBD

**交付物**:
- `.claude/skills/evidence-trace.md` - Skill定义
- 示例输出（格式化的证据链）

**验收标准**:
- [ ] 回答"这个规则基于什么证据"
- [ ] 显示置信度评级（⭐）
- [ ] 显示证据验证状态（✅/❌/⚠️）
- [ ] 递归显示关联证据

**依赖**: Task 3.2

---

#### Task 3.4: 审计工具
**优先级**: P1\
**预估**: 1天\
**负责人**: TBD

**交付物**:
- `scripts/audit-evidence.py` - 审计脚本

**验收标准**:
- [ ] 检查所有记忆的证据完整性
- [ ] 识别无证据记忆
- [ ] 识别低置信度记忆（<0.6）
- [ ] 识别证据失效的记忆
- [ ] 生成汇总报告

**依赖**: Task 3.2

---

#### Task 3.5: 迁移现有记忆
**优先级**: P1\
**预估**: 2天\
**负责人**: TBD

**交付物**:
- 10条核心记忆迁移到新格式：
  1. fix-backup-collision
  2. windows-path-encoding
  3. hook-execution-safety
  4. memory-compact-strategy
  5. agent-decision-routing
  6. rule-deprecation-lifecycle
  7. qa-scoring-method
  8. global-install-procedure
  9. skill-loading-pattern
  10. context-budget-management

**验收标准**:
- [ ] 所有记忆包含至少1个证据
- [ ] 置信度≥0.8
- [ ] 通过audit-evidence.py检查
- [ ] 更新MEMORY.md索引

**依赖**: Task 3.1, 3.2

---

#### Task 3.6: 集成测试
**优先级**: P1\
**预估**: 1天\
**负责人**: TBD

**交付物**:
- `tests/evidence/test_query.py`
- `tests/evidence/test_validation.py`
- `tests/evidence/test_integration.py`

**验收标准**:
- [ ] 单元测试覆盖率>85%
- [ ] 集成测试覆盖3个场景（新人onboarding/规则审计/规则演化）
- [ ] 向后兼容（旧格式记忆仍可读取）

**依赖**: Task 3.1-3.5

---

### 模块4: 文档与集成

#### Task 4.1: 更新项目文档
**优先级**: P2\
**预估**: 1天\
**负责人**: TBD

**交付物**:
- 更新`README.md`（新增功能说明）
- 更新`AGENTS.md`（新增决策路由说明）
- 更新`docs/MEMORY-GUIDE.md`（证据系统使用）
- 创建`docs/CONTEXT-OPTIMIZATION.md`

**验收标准**:
- [ ] 文档清晰易懂
- [ ] 包含使用示例
- [ ] 包含常见问题（FAQ）

**依赖**: Task 1.1-3.6

---

#### Task 4.2: 集成到现有工作流
**优先级**: P1\
**预估**: 1天\
**负责人**: TBD

**交付物**:
- `/rule-audit`显示证据状态
- `/evolve`要求提供证据
- `/skill`自动查询Playbook

**验收标准**:
- [ ] 现有命令正常工作
- [ ] 新功能无缝集成
- [ ] 无回归问题

**依赖**: Task 1.1-3.6

---

#### Task 4.3: 回归测试套件
**优先级**: P0\
**预估**: 1天\
**负责人**: TBD

**交付物**:
- `scripts/run-all-tests.sh` - 一键测试脚本
- CI配置更新

**验收标准**:
- [ ] 包含所有现有测试
- [ ] 包含新增功能测试
- [ ] 测试总耗时<5分钟
- [ ] 100%测试通过

**依赖**: Task 1.1-3.6

---

#### Task 4.4: 性能基准测试
**优先级**: P2\
**预估**: 1天\
**负责人**: TBD

**交付物**:
- `scripts/benchmark.py` - 基准测试脚本
- `docs/PERFORMANCE-BASELINE.md` - 基线报告

**测试场景**:
1. 文档分析任务（大文件读取+摘要）
2. 代码审查任务（多文件扫描）
3. 重复任务（Playbook匹配）
4. 决策路由（1000次决策延迟）
5. 证据查询（100次查询延迟）

**验收标准**:
- [ ] Token节省率>30%（场景1-2）
- [ ] 决策延迟<1s（场景3-4）
- [ ] 查询延迟<200ms（场景5）

**依赖**: Task 1.1-3.6

---

## 📅 时间规划

### Week 1-2: 核心实现
- Day 1-2: Task 1.1 (上下文路由)
- Day 3: Task 1.2 (记忆检索)
- Day 4-5: Task 2.1 (决策引擎)
- Day 6: Task 2.2 (Playbook)
- Day 7: Task 2.3 (失败记忆)
- Day 8: Task 3.1 (证据Schema)
- Day 9-10: Task 3.2 (查询接口)

### Week 3: 功能完善
- Day 11: Task 2.4 (决策日志)
- Day 12: Task 3.3 (可视化)
- Day 13: Task 3.4 (审计工具)
- Day 14-15: Task 3.5 (迁移记忆)

### Week 4: 测试与集成
- Day 16: Task 1.3 (上下文测试)
- Day 17: Task 2.5 (决策测试)
- Day 18: Task 3.6 (证据测试)
- Day 19: Task 4.2 (工作流集成)
- Day 20: Task 4.3 (回归测试)

### Week 5-6: 优化与文档
- Day 21: Task 4.4 (性能基准)
- Day 22: Task 4.1 (文档更新)
- Day 23-25: Bug修复与优化
- Day 26-30: 在真实项目试用，收集反馈

---

## 🎯 里程碑

### Milestone 1: 核心功能可用（Week 2结束）
- [ ] 决策路由基本工作
- [ ] Playbook可管理3个流程
- [ ] 证据系统可查询

### Milestone 2: 功能完整（Week 3结束）
- [ ] 所有核心功能实现完成
- [ ] 10条记忆迁移到新格式
- [ ] 决策日志开始收集

### Milestone 3: 测试通过（Week 4结束）
- [ ] 所有单元测试通过
- [ ] 集成测试通过
- [ ] 回归测试无问题

### Milestone 4: 生产就绪（Week 6结束）
- [ ] 性能达标（Token节省>30%，决策<1s）
- [ ] 文档完整
- [ ] 在3个真实项目验证

---

## 🚨 风险与依赖

### 关键路径
```
Task 1.1 → Task 1.3 → Task 4.3 → Milestone 3
Task 2.1 → Task 2.4 → Task 2.5 → Task 4.3 → Milestone 3
Task 3.1 → Task 3.2 → Task 3.5 → Task 3.6 → Task 4.3 → Milestone 3
```

### 高风险任务
- **Task 2.1**: 决策引擎复杂度高，可能需要额外时间
- **Task 3.5**: 记忆迁移可能发现格式不一致，需要调整Schema

### 应对策略
- 高风险任务预留20%缓冲时间
- 每日站会同步进度，遇阻塞及时调整
- 准备降级方案（如Playbook数量从3个降到2个）

---

## 📊 验收标准（总体）

### 功能完整性
- [ ] 三个模块的核心功能全部实现
- [ ] 所有任务的验收标准通过
- [ ] 无P0/P1缺陷

### 性能指标
- [ ] Token节省率>30%（真实场景测量）
- [ ] 决策延迟<1s（常规任务）
- [ ] 证据查询延迟<200ms

### 质量指标
- [ ] 单元测试覆盖率>80%
- [ ] 集成测试覆盖3大场景
- [ ] 回归测试100%通过

### 用户验证
- [ ] 在3个真实项目试用
- [ ] 收集用户反馈（误判率、干扰程度）
- [ ] 无负面反馈

---

## 🔄 每日站会模板

### 格式
**时间**: 每天上午10:00\
**时长**: 15分钟

### 议程
1. 昨天完成了什么？
2. 今天计划做什么？
3. 遇到什么阻塞？

### 示例
```
张三:
- 昨天: 完成Task 1.1的70%，pre-tool-call.py基本逻辑完成
- 今天: 完成剩余30%，编写单元测试
- 阻塞: 无

李四:
- 昨天: 完成Task 2.1的决策树设计
- 今天: 实现pattern_matcher.py
- 阻塞: 需要确认简单命令的匹配规则（等待张三的反馈）
```

---

## 📮 沟通渠道

### 技术问题
- GitHub Issues（bug报告、功能请求）
- 技术讨论群（实时沟通）

### 进度同步
- 每日站会（同步进度、识别阻塞）
- 周会（Review里程碑、调整计划）

### 文档协作
- Google Docs（方案讨论、设计评审）
- GitHub PR（代码审查）

---

## 📚 参考资料

### SPEC文档
- `specs/SPEC-context-optimization.md`
- `specs/SPEC-dual-system-decision.md`
- `specs/SPEC-evidence-driven-verification.md`
- `specs/IMPROVEMENT-OVERVIEW.md`

### 现有文档
- `AGENTS.md` - 仓库工作约定
- `docs/QA-SYSTEM.md` - 质量保证体系
- `docs/RULE-EVOLUTION.md` - 规则演化生命周期

### 验证脚本
- `scripts/audit-rules.py --strict`
- `scripts/audit-skills.py`
- `python -m unittest discover -s tests`

---

**文档版本**: v1.0\
**创建日期**: 2024-01-20\
**维护者**: 太一元系统团队

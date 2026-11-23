# 项目完善方案实施指南

> 2026-11-23 实现状态见 [实施与验收记录](../docs/IMPROVEMENT-IMPLEMENTATION.md)，执行接口以 [运行时契约](SPEC-improvement-runtime.md) 为准。下文保留原始方案背景；示例路径、自动执行、外部安装与收益数字不视为已验证事实。

本文档为项目完善方案的快速导航和实施指南。

## 📖 文档结构

```
specs/
├── IMPROVEMENT-OVERVIEW.md          # 总览：所有改进方向对比
├── SPEC-context-optimization.md     # 详细方案：上下文优化
├── SPEC-dual-system-decision.md     # 详细方案：双系统决策
├── SPEC-evidence-driven-verification.md  # 详细方案：证据驱动验证
├── PHASE1-TASKS.md                  # 实施任务清单（GitHub Issues就绪）
└── IMPLEMENTATION-GUIDE.md          # 本文档
```

---

## 🎯 核心改进方向

我们从三个开源项目中提取了核心理念，设计了三个轻量级方案：

### 1. 上下文优化系统
**参考**: Context Mode\
**核心价值**: 节省30-50% token，延长会话时长\
**关键机制**:
- 决策路由：批量操作 → 脚本聚合
- 结果摘要：大输出 → 关键信息
- 记忆检索：SQLite FTS5快速查询

**详见**: `SPEC-context-optimization.md`

---

### 2. 双系统决策机制
**参考**: Agnes Harness\
**核心价值**: 常规决策<1秒，重复任务成功率80%+\
**关键机制**:
- 规则引擎：简单命令直接执行
- Playbook系统：版本化流程复用
- 失败记忆：已知错误不重犯
- 经验积累：决策日志 → 自动优化

**详见**: `SPEC-dual-system-decision.md`

---

### 3. 证据驱动验证系统
**参考**: Craft Anything\
**核心价值**: 所有结论可追溯、可量化、可验证\
**关键机制**:
- 结构化证据：5种类型（test/commit/measurement/observation/documentation）
- 置信度量化：0.0-1.0评分
- 证据链追溯：递归查询关联证据
- 自动审计：发现无证据/低置信度/失效证据

**详见**: `SPEC-evidence-driven-verification.md`

---

## 🚀 快速开始

### 第一步：理解现状
阅读总览文档了解三个方案的对比：
```bash
# 总览文档（20分钟阅读）
cat specs/IMPROVEMENT-OVERVIEW.md
```

### 第二步：深入方案
根据兴趣选择一个方向深入阅读：
```bash
# 上下文优化（30分钟）
cat specs/SPEC-context-optimization.md

# 决策加速（40分钟）
cat specs/SPEC-dual-system-decision.md

# 证据管理（35分钟）
cat specs/SPEC-evidence-driven-verification.md
```

### 第三步：查看任务
了解具体实施任务：
```bash
# 实施任务清单（25分钟）
cat specs/PHASE1-TASKS.md
```

### 第四步：开始实施
根据任务清单开始开发（详见下文"实施流程"）

---

## 📊 方案对比速查表

| 维度 | 上下文优化 | 决策加速 | 证据管理 |
|------|-----------|---------|---------|
| **核心问题** | Token浪费 | 决策慢、无记忆 | 证据分散、不可追溯 |
| **预期收益** | 节省30-50% token | 决策<1s | 提升可信度 |
| **实施难度** | 低 | 中 | 低 |
| **投入时间** | 2-3天 | 3-5天 | 3-5天 |
| **依赖项** | 无 | 无 | 无 |
| **风险等级** | MEDIUM | MEDIUM | LOW |
| **优先级** | HIGH | HIGH | HIGH |

---

## 🛠️ 实施流程

### Phase 0: 准备阶段（1天）

#### 0.1 环境准备
```bash
# 确认Python版本
python --version  # 需要3.10+

# 确认Git状态
git status  # 确保工作区干净

# 创建功能分支
git checkout -b feature/improvement-phase1
```

#### 0.2 团队对齐
- [ ] 团队成员阅读IMPROVEMENT-OVERVIEW.md
- [ ] 技术方案评审会（1小时）
- [ ] 确认优先级和资源分配
- [ ] 创建GitHub Project看板

#### 0.3 任务分解
```bash
# 将PHASE1-TASKS.md转换为GitHub Issues
# 建议使用脚本或手动创建

# 示例Issue模板：
# Title: [模块1] Task 1.1: 决策路由Hook
# Labels: P0, enhancement, phase1
# Assignee: TBD
# Milestone: Milestone 1 (Week 2)
```

---

### Phase 1: 核心实现（Week 1-2）

#### 并行开发
三个模块可并行开发，互不阻塞：

**Track 1: 上下文优化**
- Day 1-2: 实现pre/post-tool-call.py
- Day 3: 实现memory索引

**Track 2: 决策加速**
- Day 1-2: 实现decision_engine.py
- Day 3: 创建Playbook模板
- Day 4: 实现失败记忆

**Track 3: 证据管理**
- Day 1: 设计证据Schema
- Day 2-3: 实现查询接口

#### 每日检查清单
- [ ] 代码提交到功能分支
- [ ] 编写单元测试（覆盖率>80%）
- [ ] 更新任务状态（GitHub Issue）
- [ ] 参加每日站会（15分钟）

---

### Phase 2: 功能完善（Week 3）

#### 2.1 补充周边功能
- 决策日志收集
- 证据可视化Skill
- 审计工具

#### 2.2 迁移现有数据
- 3个Playbook
- 10条记忆（带证据）
- 3个失败案例

#### 2.3 代码审查
每个PR需要：
- [ ] 至少1人Review
- [ ] 单元测试通过
- [ ] 代码风格检查通过
- [ ] 文档更新

---

### Phase 3: 测试与集成（Week 4）

#### 3.1 单元测试
```bash
# 运行所有单元测试
python -m pytest tests/ -v --cov=.claude --cov-report=html

# 目标：覆盖率>80%
```

#### 3.2 集成测试
```bash
# 运行集成测试
python scripts/test-decision-scenarios.py
python scripts/measure-token-savings.py

# 验证指标
# - Token节省率>30%
# - 决策准确率>85%
# - 查询延迟<200ms
```

#### 3.3 回归测试
```bash
# 确保现有功能不受影响
python scripts/audit-rules.py --strict
python scripts/audit-skills.py
bash scripts/test-all-intents.sh
```

---

### Phase 4: 优化与发布（Week 5-6）

#### 4.1 性能优化
- 识别性能瓶颈（profiling）
- 优化慢查询
- 添加缓存

#### 4.2 真实场景验证
选择3个真实项目试用：
1. 自身项目（太一元系统）
2. 中型项目（1000-5000行代码）
3. 大型项目（5000+行代码）

#### 4.3 文档完善
- [ ] 更新README.md
- [ ] 编写使用指南
- [ ] 记录常见问题（FAQ）
- [ ] 录制演示视频（可选）

#### 4.4 发布准备
```bash
# 合并到main分支
git checkout main
git merge feature/improvement-phase1

# 打标签
git tag -a v1.1.0 -m "Phase 1: Context optimization, dual-system decision, evidence system"

# 推送
git push origin main --tags
```

---

## 📋 检查清单

### 功能完整性
- [ ] 上下文优化
  - [ ] 决策路由Hook
  - [ ] 记忆快速检索
  - [ ] Token节省率>30%

- [ ] 决策加速
  - [ ] 决策路由引擎
  - [ ] 3个Playbook
  - [ ] 失败记忆系统
  - [ ] 决策日志收集
  - [ ] 决策延迟<1s

- [ ] 证据管理
  - [ ] 证据Schema
  - [ ] 查询接口
  - [ ] 可视化Skill
  - [ ] 审计工具
  - [ ] 10条记忆迁移
  - [ ] 查询延迟<200ms

### 质量保证
- [ ] 单元测试覆盖率>80%
- [ ] 集成测试通过
- [ ] 回归测试无问题
- [ ] 代码审查完成
- [ ] 文档完整

### 用户验证
- [ ] 3个真实项目试用
- [ ] 收集用户反馈
- [ ] 无负面反馈
- [ ] 识别改进点

---

## 🎯 验收标准

### 必达指标
1. **Token节省率**: >30%（5个真实任务平均）
2. **决策延迟**: 常规任务<1秒
3. **决策准确率**: >85%
4. **证据覆盖率**: 新记忆100%带证据
5. **测试覆盖率**: >80%

### 期望指标
1. **会话时长延长**: >1.5倍
2. **重复任务加速**: >40%
3. **高置信度记忆**: >80%置信度>0.8
4. **用户满意度**: 无负面反馈

---

## ⚠️ 风险管理

### 高风险项
1. **决策引擎复杂度**
   - 风险：实现时间超预期
   - 缓解：预留20%缓冲，准备降级方案

2. **记忆迁移格式不一致**
   - 风险：发现旧记忆无法迁移
   - 缓解：先迁移3条验证格式，再批量迁移

3. **性能不达标**
   - 风险：实际节省率<30%
   - 缓解：准备多个优化方案（缓存、索引、并行）

### 应对策略
- 每日站会识别阻塞
- 周会Review里程碑进度
- 灵活调整任务优先级
- 保持功能分支可随时回滚

---

## 📈 后续迭代

### 短期（3个月内）
- 收集500+决策日志
- 识别10+高频Playbook
- 证据覆盖率>90%
- 根据数据优化路由规则

### 中期（6个月内）
- 评估是否需要训练轻量决策模型
- 实现任务自动复盘
- 证据关系图可视化
- 自适应路由（根据反馈自动调整）

### 长期（12个月内）
- 评估是否引入完整系统
- 决策树：
  - Token消耗仍高 → Context Mode
  - 决策准确率低 → 训练专用模型
  - 硬件集成需求 → Agnes Harness
  - 二进制分析需求 → Craft Anything部分工具

---

## 🤝 团队协作

### 角色分工
- **Tech Lead**: 技术方案评审、难点攻关、代码审查
- **Developer**: 功能实现、单元测试、文档编写
- **QA**: 测试用例设计、集成测试、性能测试
- **PM**: 进度跟踪、风险管理、用户验证

### 会议节奏
- **每日站会**: 15分钟，同步进度
- **周会**: 1小时，Review里程碑
- **技术评审**: 按需，重大决策前
- **复盘会**: Phase结束后，总结经验

### 沟通渠道
- **GitHub Issues**: 任务跟踪、bug报告
- **GitHub PR**: 代码审查
- **技术群**: 实时沟通
- **文档**: 方案讨论、设计评审

---

## 📚 参考资源

### 内部文档
- `AGENTS.md` - 仓库工作约定
- `docs/QA-SYSTEM.md` - 质量保证
- `docs/RULE-EVOLUTION.md` - 规则演化
- `docs/ORCHESTRATION-GUIDE.md` - 编排指南

### 外部项目
- Context Mode: https://github.com/mksglu/context-mode
- Agnes Harness: https://github.com/AgnesAI-Labs/agnes-harness
- Craft Anything: https://github.com/storytold/craft-anything

### 技术报告
- Agnes Sys1: https://github.com/AgnesAI-Labs/Agnes-Sys1-1.0-Technical-Report
- Agnes Harness: https://github.com/AgnesAI-Labs/Agnes-Harness-Technical-Report-Nov-2026

---

## 💡 最佳实践

### 开发原则
1. **简单优先**: 能用规则解决就不用模型
2. **证据驱动**: 所有决策基于数据/测试
3. **按需加载**: 不因功能酷炫就盲目引入
4. **渐进式**: 小步快跑，快速验证

### 代码规范
1. **类型注解**: 所有函数添加类型注解
2. **文档字符串**: 复杂函数添加docstring
3. **错误处理**: 预期的异常要捕获
4. **日志记录**: 关键路径添加日志

### 测试策略
1. **单元测试**: 覆盖核心逻辑
2. **集成测试**: 覆盖端到端场景
3. **回归测试**: 确保不破坏现有功能
4. **性能测试**: 验证关键指标

---

## 🎓 学习路径

### 新成员onboarding
1. 阅读`IMPROVEMENT-OVERVIEW.md`（20分钟）
2. 选择一个模块深入阅读SPEC（30分钟）
3. 运行现有测试，理解代码结构（1小时）
4. 认领一个小任务（如文档更新）（2小时）
5. 参加每日站会，了解进度（持续）

### 技能要求
- **必需**: Python 3.10+, Git, 单元测试
- **推荐**: SQLite, YAML, 正则表达式
- **加分**: 机器学习基础（决策模型训练）

---

## 📞 获取帮助

### 技术问题
1. 先查阅SPEC文档和代码注释
2. 搜索GitHub Issues（可能已有答案）
3. 在技术群提问（附上错误日志）
4. 创建GitHub Issue（详细描述问题）

### 进度阻塞
1. 在每日站会提出
2. Tech Lead评估影响
3. 调整任务优先级或增加资源

### 方案争议
1. 在技术群讨论
2. 必要时召开技术评审会
3. 决策记录到文档

---

## ✅ 成功标准

### Phase 1成功定义
- [ ] 三个模块核心功能全部实现
- [ ] 性能指标达标（Token节省>30%，决策<1s）
- [ ] 质量指标达标（测试覆盖率>80%）
- [ ] 用户验证通过（3个项目，无负面反馈）
- [ ] 文档完整（README/SPEC/FAQ）

### 项目成功定义
- [ ] 持续运行3个月无重大问题
- [ ] 决策准确率>80%
- [ ] 证据覆盖率>90%
- [ ] 识别出10+高频Playbook
- [ ] 积累500+决策日志
- [ ] 团队认可度高（愿意持续使用）

---

## 🎉 下一步行动

### 立即行动（今天）
1. [ ] 团队成员阅读本文档
2. [ ] 创建GitHub Project看板
3. [ ] 分配初始任务

### 本周行动
1. [ ] 召开技术方案评审会
2. [ ] 转换PHASE1-TASKS.md为Issues
3. [ ] 开始Track 1-3并行开发

### 本月行动
1. [ ] 完成Milestone 1（核心功能）
2. [ ] 完成Milestone 2（功能完整）
3. [ ] 准备Milestone 3（测试）

---

**祝实施顺利！** 🚀

有任何问题请参考SPEC文档或联系团队。

---

**文档版本**: v1.0\
**创建日期**: 2024-01-20\
**维护者**: 太一元系统团队\
**最后更新**: 2024-01-20

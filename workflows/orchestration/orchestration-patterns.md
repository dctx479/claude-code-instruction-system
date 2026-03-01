# Agent 编排模式库

## 概述

本文档定义了6种核心编排模式，每种模式包含完整的实现指南、适用场景和性能特征。

---

## 目录

1. [PARALLEL - 并行模式](#1-parallel---并行模式)
2. [SEQUENTIAL - 串行模式](#2-sequential---串行模式)
3. [HIERARCHICAL - 层级模式](#3-hierarchical---层级模式)
4. [COLLABORATIVE - 协作模式](#4-collaborative---协作模式)
5. [COMPETITIVE - 竞争模式](#5-competitive---竞争模式)
6. [SWARM - 群体模式](#6-swarm---群体模式)
7. [HYBRID - 混合模式](#7-hybrid---混合模式)

---

## 1. PARALLEL - 并行模式

### 适用场景

**最佳适用**:
- 独立子任务，无依赖关系
- 可同时执行的操作
- 时间敏感任务
- 数据分区处理

**实际案例**:
- 审查多个独立文件
- 并行搜索多个目录
- 批量数据转换
- 多个API端点实现

### 架构模式

```
┌─────────────┐
│    Task     │
└──────┬──────┘
       │
   Decompose
       │
   ┌───┴───┬───────┬───────┐
   │       │       │       │
   ▼       ▼       ▼       ▼
┌──────┐┌──────┐┌──────┐┌──────┐
│Agent1││Agent2││Agent3││Agent4│
└───┬──┘└───┬──┘└───┬──┘└───┬──┘
    │       │       │       │
    └───────┴───────┴───────┘
              │
              ▼
        ┌──────────┐
        │  Merge   │
        └──────────┘
```

### 实现方式

#### 伪代码
```python
def parallel_pattern(task, subtasks):
    """并行执行多个独立子任务"""

    # 1. 任务分解
    agents = []
    for subtask in subtasks:
        agent = select_agent(subtask)
        agents.append({
            'agent': agent,
            'task': subtask,
            'status': 'pending'
        })

    # 2. 并行执行
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(agent['agent'].execute, agent['task'])
            for agent in agents
        ]

        # 3. 收集结果
        for future in as_completed(futures):
            try:
                result = future.result(timeout=120)
                results.append(result)
            except TimeoutError:
                results.append({'status': 'timeout'})
            except Exception as e:
                results.append({'status': 'error', 'error': str(e)})

    # 4. 合并结果
    final_result = merge_results(results)
    return final_result

def merge_results(results):
    """合并多个Agent的输出"""
    success = [r for r in results if r.get('status') == 'success']
    failed = [r for r in results if r.get('status') in ['error', 'timeout']]

    return {
        'success_count': len(success),
        'failed_count': len(failed),
        'results': success,
        'failures': failed
    }
```

#### Claude Code 实现
```markdown
## 并行执行计划

### 任务分组
- **Group 1**: 审查 `auth.ts` → 分配给 code-reviewer#1
- **Group 2**: 审查 `api.ts` → 分配给 code-reviewer#2
- **Group 3**: 审查 `utils.ts` → 分配给 code-reviewer#3
- **Group 4**: 审查 `db.ts` → 分配给 code-reviewer#4

### 执行配置
- 并行度: 4
- 超时: 120s/任务
- 重试: 2次
- 失败策略: 记录并继续

### 合并策略
收集所有审查结果后:
1. 聚合发现的问题
2. 去重相似问题
3. 按严重程度排序
4. 生成综合报告
```

### 性能特征

| 指标 | 数值 |
|-----|-----|
| 预期加速比 | 3-5x |
| 最大并行度 | 5 (可配置) |
| 单任务超时 | 120s |
| 重试次数 | 2 |
| 适用规模 | 2-20个子任务 |

### 配置参数

```yaml
parallel_config:
  max_workers: 5           # 最大并行Agent数
  timeout_per_task: 120    # 单任务超时(秒)
  retry_attempts: 2        # 失败重试次数
  fail_strategy: "continue" # 失败策略: continue/abort
  merge_strategy: "aggregate" # 合并策略
```

### 使用示例

#### 示例1: 多文件代码审查
```markdown
任务: 审查10个文件

执行:
1. 分解为10个独立审查任务
2. 并行启动5个 code-reviewer Agent
3. 分两批执行 (5+5)
4. 聚合所有发现的问题
5. 生成综合报告

预期时间: 2分钟 (单Agent需10分钟)
加速: 5x
```

#### 示例2: 多目录搜索
```markdown
任务: 在5个目录中搜索特定模式

执行:
1. 为每个目录分配一个 explorer Agent
2. 同时启动5个搜索
3. 收集所有匹配结果
4. 去重并排序

预期时间: 15秒 (顺序需75秒)
加速: 5x
```

### 注意事项

**优势**:
- 最大化执行效率
- 简单易实现
- 适合大多数场景

**限制**:
- 子任务必须独立
- 结果合并可能复杂
- 并发数受资源限制

**常见陷阱**:
- 依赖未正确识别导致结果错误
- 过多并发导致资源耗尽
- 合并逻辑不完善导致遗漏

---

## 2. SEQUENTIAL - 串行模式

### 适用场景

**最佳适用**:
- 强依赖关系的任务链
- 管道式数据处理
- 每步需验证的流程
- 状态累积的过程

**实际案例**:
- 需求分析 → 设计 → 实现
- 数据提取 → 清洗 → 分析
- 测试失败 → 修复 → 重测
- 代码 → 编译 → 测试 → 部署

### 架构模式

```
┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
│ Agent1 │───▶│ Agent2 │───▶│ Agent3 │───▶│ Agent4 │
└────────┘    └────────┘    └────────┘    └────────┘
    │             │             │             │
    ▼             ▼             ▼             ▼
 Result1 ─────▶ Result2 ─────▶ Result3 ───▶ Final
```

### 实现方式

#### 伪代码
```python
def sequential_pattern(task, pipeline):
    """串行执行依赖任务链"""

    context = {'initial_input': task}
    results = []

    for step in pipeline:
        agent = step['agent']

        # 使用前一步的输出作为输入
        input_data = prepare_input(context, step)

        try:
            # 执行当前步骤
            result = agent.execute(input_data)

            # 验证输出
            if not validate_step_output(result, step):
                raise ValueError(f"Step {step['name']} output invalid")

            # 更新上下文
            context[step['name']] = result
            results.append(result)

        except Exception as e:
            # 失败时决定是否继续
            if step.get('critical', True):
                raise  # 关键步骤失败则终止
            else:
                results.append({'status': 'skipped', 'reason': str(e)})

    return aggregate_pipeline_results(results)

def prepare_input(context, step):
    """从上下文准备当前步骤的输入"""
    dependencies = step.get('dependencies', [])
    input_data = {
        'task': step['description']
    }

    for dep in dependencies:
        if dep in context:
            input_data[dep] = context[dep]

    return input_data
```

#### Claude Code 实现
```markdown
## 串行执行管道

### 步骤1: 需求分析
- Agent: architect
- 输入: 用户需求描述
- 输出: 需求文档
- 验证: 确保需求明确且可实现

### 步骤2: 架构设计
- Agent: architect
- 输入: 需求文档(来自步骤1)
- 输出: 架构设计方案
- 验证: 检查技术可行性

### 步骤3: 代码实现
- Agent: developer
- 输入: 架构设计方案(来自步骤2)
- 输出: 实现代码
- 验证: 编译通过

### 步骤4: 测试验证
- Agent: code-reviewer
- 输入: 实现代码(来自步骤3)
- 输出: 测试报告
- 验证: 所有测试通过

### 依赖链
步骤1 → 步骤2 → 步骤3 → 步骤4
```

### 性能特征

| 指标 | 数值 |
|-----|-----|
| 预期加速比 | 1x (保证正确性) |
| 并行度 | 1 |
| 失败影响 | 阻断后续步骤 |
| 适用规模 | 2-10个步骤 |

### 配置参数

```yaml
sequential_config:
  validate_each_step: true      # 验证每步输出
  fail_strategy: "abort"        # 失败策略: abort/continue
  save_intermediate: true       # 保存中间结果
  rollback_on_failure: false    # 失败是否回滚
```

### 使用示例

#### 示例1: 特性开发流程
```markdown
任务: 开发新特性

管道:
1. architect: 分析需求，输出需求文档
2. architect: 设计技术方案，输出设计文档
3. developer: 实现后端API
4. developer: 实现前端UI
5. code-reviewer: 代码审查和优化建议
6. debugger: 测试并修复问题

预期时间: 60分钟 (累积)
优势: 保证每步质量
```

#### 示例2: 数据处理管道
```markdown
任务: 处理和分析数据

管道:
1. 提取数据 (data-scientist)
2. 清洗数据 (data-scientist)
3. 转换格式 (data-scientist)
4. 统计分析 (data-scientist)
5. 生成可视化 (data-scientist)
6. 撰写报告 (data-scientist)
```

### 注意事项

**优势**:
- 保证执行顺序
- 每步可验证
- 易于调试
- 支持状态传递

**限制**:
- 无法并行加速
- 一步失败影响全局
- 总时间是各步之和

**最佳实践**:
- 明确定义每步输入输出
- 设置合理的验证点
- 保存中间结果便于回溯
- 关键步骤设置重试

---

## 3. HIERARCHICAL - 层级模式

### 适用场景

**最佳适用**:
- 需要专家决策的复杂任务
- 可分解为子任务，但需统一协调
- 分层处理的问题
- 需要审核机制的流程

**实际案例**:
- 系统开发: 架构师指导多个开发者
- 项目管理: 项目经理协调多个任务组
- 代码重构: 高级工程师设计，初级实现
- 研究项目: 研究员设计实验，助手执行

### 架构模式

```
              ┌──────────────┐
              │  Specialist  │ (决策层)
              │   (Opus)     │
              └───────┬──────┘
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
┌──────────┐    ┌──────────┐  ┌──────────┐
│ Worker 1 │    │ Worker 2 │  │ Worker 3 │ (执行层)
│ (Sonnet) │    │ (Sonnet) │  │ (Sonnet) │
└─────┬────┘    └─────┬────┘  └─────┬────┘
      │               │              │
      └───────────────┴──────────────┘
                      │
                      ▼
              ┌──────────────┐
              │  Specialist  │ (审核层)
              │   (Review)   │
              └──────────────┘
```

### 实现方式

#### 伪代码
```python
def hierarchical_pattern(task):
    """层级编排: 专家指导 + 工作者执行"""

    # Phase 1: 专家分析和决策
    specialist = get_specialist_agent(task.domain)
    analysis = specialist.analyze(task)

    plan = {
        'subtasks': analysis['subtasks'],
        'dependencies': analysis['dependencies'],
        'guidelines': analysis['guidelines']
    }

    # Phase 2: 分配给Workers并行执行
    workers = []
    for subtask in plan['subtasks']:
        worker = select_worker_agent(subtask)
        workers.append({
            'agent': worker,
            'task': subtask,
            'guidelines': plan['guidelines']
        })

    # 并行执行工作者任务
    worker_results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(
                w['agent'].execute,
                w['task'],
                guidelines=w['guidelines']
            )
            for w in workers
        ]

        for future in as_completed(futures):
            worker_results.append(future.result())

    # Phase 3: 专家审核和整合
    final_result = specialist.review_and_integrate(
        worker_results,
        original_task=task
    )

    return final_result

def get_specialist_agent(domain):
    """根据领域选择专家Agent"""
    specialists = {
        'architecture': 'architect',
        'security': 'security-analyst',
        'data': 'data-scientist'
    }
    return specialists.get(domain, 'architect')
```

#### Claude Code 实现
```markdown
## 层级执行计划

### Phase 1: 专家决策 (Specialist)
**Agent**: architect (opus)
**任务**:
1. 分析用户需求
2. 设计技术架构
3. 分解为可执行子任务
4. 制定实施指南

**输出**:
- 架构设计文档
- 子任务清单
- 实施指南
- 验收标准

---

### Phase 2: 并行执行 (Workers)

#### Worker 1: 后端开发
- Agent: developer (sonnet)
- 任务: 实现API端点
- 指南: 遵循架构设计中的API规范
- 预期: 2小时

#### Worker 2: 前端开发
- Agent: developer (sonnet)
- 任务: 实现UI组件
- 指南: 使用设计系统，遵循组件规范
- 预期: 2小时

#### Worker 3: 数据库设计
- Agent: data-scientist (sonnet)
- 任务: 设计数据模型
- 指南: 遵循架构设计中的数据规范
- 预期: 1.5小时

**并行执行**: 3个Worker同时工作
**预期总时间**: 2小时 (最长Worker时间)

---

### Phase 3: 专家审核 (Specialist)
**Agent**: architect (opus)
**任务**:
1. 审核各Worker的输出
2. 检查一致性和集成点
3. 识别潜在问题
4. 整合为最终方案
5. 生成交付文档

**输出**:
- 集成后的完整方案
- 审核报告
- 遗留问题清单
- 后续建议
```

### 性能特征

| 指标 | 数值 |
|-----|-----|
| 预期加速比 | 2-3x |
| 决策质量 | 高 (Opus专家) |
| 执行并行度 | 3-5 |
| 适用规模 | 3-8个子任务 |

### 配置参数

```yaml
hierarchical_config:
  specialist_model: "opus"        # 专家模型
  worker_model: "sonnet"          # 工作者模型
  max_workers: 5                  # 最大并行工作者
  review_required: true           # 是否需要审核
  iteration_allowed: true         # 是否允许迭代改进
  max_iterations: 2               # 最大迭代次数
```

### 使用示例

#### 示例1: Web应用开发
```markdown
任务: 开发完整的用户管理系统

Phase 1: 架构设计 (architect)
- 设计系统架构
- 定义API接口
- 规划数据模型
- 制定开发规范
时间: 30分钟

Phase 2: 并行开发 (Workers)
- Worker1: 用户注册API (developer)
- Worker2: 用户登录API (developer)
- Worker3: 权限管理API (developer)
- Worker4: 前端用户界面 (developer)
时间: 2小时 (并行)

Phase 3: 审核整合 (architect)
- 审核代码质量
- 测试集成点
- 优化性能
- 生成文档
时间: 30分钟

总时间: 3小时
vs 串行: 8小时
加速: 2.7x
```

#### 示例2: 安全审计
```markdown
任务: 全面安全审计

Phase 1: 规划 (security-analyst)
- 确定审计范围
- 制定检查清单
- 分配审计任务

Phase 2: 并行审计 (Workers)
- Worker1: 代码漏洞扫描
- Worker2: 依赖安全检查
- Worker3: 配置审查
- Worker4: 权限验证

Phase 3: 综合评估 (security-analyst)
- 整合发现
- 风险评级
- 修复建议
- 生成报告
```

### 注意事项

**优势**:
- 专家保证决策质量
- Workers并行提高效率
- 统一的审核机制
- 适合复杂项目

**限制**:
- 专家可能成为瓶颈
- 需要良好的任务分解
- 成本相对较高 (Opus)

**最佳实践**:
- 专家专注于决策和审核，不执行细节
- Workers遵循专家的指南
- 设置清晰的验收标准
- 允许适度迭代改进

---

## 4. COLLABORATIVE - 协作模式

### 适用场景

**最佳适用**:
- 跨领域复杂问题
- 需要多专家视角
- 需要讨论和共识
- 创新性问题求解

**实际案例**:
- 技术选型: 架构+安全+性能专家讨论
- 系统优化: 多角度综合优化
- 问题诊断: 多专家协同排查
- 方案评审: 多维度评估

### 架构模式

```
                ┌──────────────┐
                │     Task     │
                └───────┬──────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
         ▼              ▼              ▼
    ┌─────────┐    ┌─────────┐  ┌─────────┐
    │Expert 1 │◄──▶│Expert 2 │◄─▶│Expert 3 │
    │(架构)   │    │(安全)   │   │(性能)   │
    └────┬────┘    └────┬────┘  └────┬────┘
         │              │              │
         └──────────────┼──────────────┘
                        │
                        ▼
                 ┌─────────────┐
                 │  Synthesis  │
                 │   (共识)    │
                 └─────────────┘
```

### 实现方式

#### 伪代码
```python
def collaborative_pattern(task, experts):
    """多专家协作模式"""

    # Round 1: 各专家独立分析
    analyses = {}
    for expert in experts:
        analysis = expert.analyze(task)
        analyses[expert.domain] = analysis

    # Round 2: 交换观点
    shared_context = {
        'task': task,
        'all_analyses': analyses
    }

    discussions = {}
    for expert in experts:
        # 每个专家查看其他专家的分析
        other_views = {
            k: v for k, v in analyses.items()
            if k != expert.domain
        }

        # 提出反馈和建议
        discussion = expert.discuss(
            own_analysis=analyses[expert.domain],
            other_analyses=other_views
        )
        discussions[expert.domain] = discussion

    # Round 3: 达成共识
    consensus = synthesize_consensus(
        analyses=analyses,
        discussions=discussions,
        task=task
    )

    # Optional Round 4: 冲突解决
    if has_conflicts(consensus):
        consensus = resolve_conflicts(
            consensus,
            experts,
            facilitator=get_senior_expert()
        )

    return consensus

def synthesize_consensus(analyses, discussions, task):
    """综合各专家意见达成共识"""

    # 提取共同点
    common_ground = find_agreements(analyses)

    # 识别分歧
    conflicts = find_disagreements(discussions)

    # 整合方案
    integrated_solution = {
        'agreed_aspects': common_ground,
        'trade_offs': resolve_trade_offs(conflicts),
        'final_recommendation': merge_recommendations(analyses),
        'confidence': calculate_consensus_confidence(discussions)
    }

    return integrated_solution
```

#### Claude Code 实现
```markdown
## 协作执行计划

### Round 1: 独立分析

#### Expert 1: 架构视角 (architect)
**任务**: 分析技术架构合理性
**关注点**:
- 模块划分
- 接口设计
- 可扩展性
- 技术债务

#### Expert 2: 安全视角 (security-analyst)
**任务**: 分析安全风险
**关注点**:
- 漏洞扫描
- 权限设计
- 数据保护
- 合规性

#### Expert 3: 性能视角 (performance-expert)
**任务**: 分析性能问题
**关注点**:
- 响应时间
- 资源使用
- 瓶颈识别
- 优化机会

**执行**: 三位专家并行分析 (15分钟)

---

### Round 2: 交换观点

#### 协作讨论
每位专家查看其他专家的分析后:

**architect 的反馈**:
- 对 security-analyst: "建议的加密方案会增加30%延迟"
- 对 performance-expert: "建议的缓存策略需要考虑一致性"

**security-analyst 的反馈**:
- 对 architect: "当前架构缺少审计日志"
- 对 performance-expert: "缓存敏感数据需要加密"

**performance-expert 的反馈**:
- 对 architect: "建议异步处理降低响应时间"
- 对 security-analyst: "加密开销可通过硬件加速优化"

**执行**: 交换意见并讨论 (20分钟)

---

### Round 3: 达成共识

**Facilitator**: architect (作为主持人)

**共识内容**:
1. **架构调整**:
   - 采用异步处理 (performance建议)
   - 增加审计日志模块 (security建议)

2. **安全方案**:
   - 使用硬件加速的AES加密 (trade-off)
   - 敏感数据缓存加密 (security要求)

3. **性能优化**:
   - 多层缓存策略 (performance建议)
   - 缓存一致性保证 (architect要求)

4. **实施优先级**:
   1. 高优先级: 审计日志 + 加密
   2. 中优先级: 异步处理
   3. 低优先级: 多层缓存

**执行**: 整合方案 (10分钟)

---

### 输出

**综合方案**:
- 平衡了安全、性能、架构三个维度
- 明确了trade-offs
- 提供了实施路线图
- 各专家签字确认

**总时间**: 45分钟
**决策质量**: 高 (多视角验证)
```

### 性能特征

| 指标 | 数值 |
|-----|-----|
| 预期加速比 | 2.8-4.4x |
| 决策质量 | 极高 (多专家) |
| 适用专家数 | 2-4人 |
| 协作轮数 | 2-3轮 |

### 配置参数

```yaml
collaborative_config:
  expert_count: 3              # 专家数量
  rounds: 3                    # 协作轮数
  conflict_resolution: "facilitator"  # 冲突解决方式
  consensus_threshold: 0.75    # 共识阈值
  allow_minority_report: true  # 允许少数意见报告
```

### 使用示例

#### 示例1: 技术选型
```markdown
任务: 为新项目选择技术栈

专家团队:
- architect: 评估架构适配性
- performance-expert: 评估性能指标
- cost-analyst: 评估成本效益
- dev-experience: 评估开发体验

Round 1: 各自评估候选方案 (A/B/C)
Round 2: 讨论各方案的trade-offs
Round 3: 投票并达成共识

结果: 方案B (综合评分最高)
时间: 1小时
质量: 全面评估，风险低
```

#### 示例2: 性能优化方案
```markdown
任务: 解决系统性能问题

专家团队:
- performance-expert: 识别瓶颈
- architect: 评估架构影响
- security-analyst: 评估安全风险
- cost-analyst: 评估实施成本

协作过程:
1. performance-expert 诊断: "数据库是主要瓶颈"
2. architect 建议: "引入缓存层"
3. security-analyst 提醒: "缓存需考虑敏感数据"
4. cost-analyst 分析: "Redis成本可接受"

共识: 引入Redis缓存 + 敏感数据加密
```

### 注意事项

**优势**:
- 多视角全面分析
- 降低决策风险
- 识别潜在冲突
- 提高方案质量

**限制**:
- 协调成本较高
- 可能出现意见冲突
- 时间相对较长

**最佳实践**:
- 选择互补领域的专家
- 设置明确的协作规则
- 指定facilitator协调
- 记录所有trade-offs
- 允许少数意见保留

---

## 5. COMPETITIVE - 竞争模式

### 适用场景

**最佳适用**:
- 探索性任务
- 需要创新方案
- 多种实现路径
- 质量优先于速度

**实际案例**:
- 算法优化: 多种算法比较
- UI设计: 多个设计方案
- 问题解决: 不同解决思路
- 性能调优: 多种优化策略

### 架构模式

```
                ┌──────────┐
                │   Task   │
                └────┬─────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
      ▼              ▼              ▼
┌──────────┐   ┌──────────┐  ┌──────────┐
│ Agent 1  │   │ Agent 2  │  │ Agent 3  │
│(Approach)│   │(Approach)│  │(Approach)│
│    A     │   │    B     │  │    C     │
└─────┬────┘   └─────┬────┘  └─────┬────┘
      │              │              │
      ▼              ▼              ▼
┌──────────┐   ┌──────────┐  ┌──────────┐
│Solution A│   │Solution B│  │Solution C│
└─────┬────┘   └─────┬────┘  └─────┬────┘
      │              │              │
      └──────────────┼──────────────┘
                     │
                     ▼
              ┌─────────────┐
              │  Evaluate   │
              │  & Select   │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │ Best Solution│
              └─────────────┘
```

### 实现方式

#### 伪代码
```python
def competitive_pattern(task, competitors):
    """竞争模式: 多Agent产出方案并评选最佳"""

    # Phase 1: 并行生成方案
    solutions = []
    with ThreadPoolExecutor(max_workers=len(competitors)) as executor:
        futures = []
        for agent in competitors:
            future = executor.submit(
                agent.solve,
                task,
                approach=agent.preferred_approach
            )
            futures.append((agent, future))

        for agent, future in futures:
            try:
                solution = future.result(timeout=300)
                solutions.append({
                    'agent': agent.name,
                    'solution': solution,
                    'approach': agent.preferred_approach
                })
            except Exception as e:
                solutions.append({
                    'agent': agent.name,
                    'status': 'failed',
                    'error': str(e)
                })

    # Phase 2: 评估方案
    evaluations = []
    for solution in solutions:
        if solution.get('status') != 'failed':
            score = evaluate_solution(
                solution['solution'],
                criteria=['correctness', 'performance', 'maintainability']
            )
            evaluations.append({
                **solution,
                'score': score
            })

    # Phase 3: 选择最佳方案
    best_solution = max(evaluations, key=lambda x: x['score']['total'])

    # Optional Phase 4: 组合方案
    hybrid_solution = combine_best_aspects(evaluations)

    return {
        'best_solution': best_solution,
        'all_solutions': evaluations,
        'hybrid_option': hybrid_solution
    }

def evaluate_solution(solution, criteria):
    """多维度评估方案"""
    scores = {}

    for criterion in criteria:
        evaluator = get_evaluator(criterion)
        score = evaluator.evaluate(solution)
        scores[criterion] = score

    # 加权计算总分
    weights = {
        'correctness': 0.4,
        'performance': 0.3,
        'maintainability': 0.3
    }

    total = sum(scores[k] * weights[k] for k in criteria)
    scores['total'] = total

    return scores
```

#### Claude Code 实现
```markdown
## 竞争执行计划

### Phase 1: 并行方案生成

#### Competitor 1: 算法A (Agent: optimizer-1)
**方案**: 基于哈希表的快速查找
**预期**: 时间复杂度 O(1)，空间 O(n)

#### Competitor 2: 算法B (Agent: optimizer-2)
**方案**: 基于二分搜索的优化查找
**预期**: 时间复杂度 O(log n)，空间 O(1)

#### Competitor 3: 算法C (Agent: optimizer-3)
**方案**: 基于布隆过滤器的概率查找
**预期**: 时间复杂度 O(1)，空间 O(m)，假阳性率可控

**执行**: 三个Agent并行实现 (30分钟)

---

### Phase 2: 方案评估

#### 评估维度
1. **正确性** (权重: 40%)
   - 功能完整性
   - 边界情况处理
   - 错误处理

2. **性能** (权重: 30%)
   - 时间复杂度
   - 空间复杂度
   - 实际运行时间

3. **可维护性** (权重: 30%)
   - 代码清晰度
   - 扩展性
   - 文档完整性

#### 评估结果

| 方案 | 正确性 | 性能 | 可维护性 | 总分 |
|-----|-------|------|---------|------|
| A   | 95    | 90   | 85      | 90.5 |
| B   | 95    | 75   | 90      | 87.5 |
| C   | 90    | 95   | 70      | 85.5 |

**执行**: 自动化评估 (10分钟)

---

### Phase 3: 选择最佳

**获胜方案**: 算法A (哈希表方案)

**理由**:
- 正确性: 完全正确，边界情况处理完善
- 性能: O(1)查找，实测性能优异
- 可维护性: 代码清晰，易于理解

**次优方案**: 算法B
- 优势: 空间效率高，代码最易维护
- 劣势: 查找速度相对慢

---

### Phase 4: 混合优化(可选)

**混合方案**: 结合A和B的优点
- 小数据集(<100): 使用算法B (节省空间)
- 大数据集(≥100): 使用算法A (快速查找)
- 自适应切换阈值

**最终交付**:
- 主方案: 算法A
- 备选: 算法B
- 混合: 自适应方案
- 完整评估报告

**总时间**: 40分钟
```

### 性能特征

| 指标 | 数值 |
|-----|-----|
| 预期加速比 | 1.5-2x |
| 方案质量 | 最优 |
| 竞争者数量 | 2-4个 |
| 评估时间 | 10-15% |

### 配置参数

```yaml
competitive_config:
  competitor_count: 3              # 竞争者数量
  evaluation_criteria:             # 评估标准
    - correctness: 0.4
    - performance: 0.3
    - maintainability: 0.3
  allow_hybrid: true               # 允许混合方案
  timeout_per_competitor: 300      # 单竞争者超时(秒)
```

### 使用示例

#### 示例1: 性能优化竞赛
```markdown
任务: 优化数据处理性能

竞争者:
- Agent1: 多线程并行方案
- Agent2: 异步IO方案
- Agent3: 批处理优化方案

结果:
- Agent2 获胜: 异步IO方案性能提升5x
- Agent1 次优: 多线程方案提升3x
- Agent3 备选: 批处理适合特定场景

选择: Agent2主方案，Agent3作为备选
```

#### 示例2: UI设计比较
```markdown
任务: 设计用户登录界面

竞争者:
- Designer1: 简约现代风格
- Designer2: 专业商务风格
- Designer3: 友好活泼风格

评估:
- 用户测试评分
- 可用性指标
- 美观度评分

结果: Designer1方案获胜
理由: 用户测试评分最高，转化率提升15%
```

### 注意事项

**优势**:
- 获得最优解
- 多方案备选
- 识别不同方法优劣
- 激励创新

**限制**:
- 时间成本是单方案的N倍
- 评估需要标准
- 可能出现平局

**最佳实践**:
- 明确评估标准和权重
- 允许不同实现路径
- 保留次优方案作为备选
- 考虑混合方案的可能性
- 量化评估结果

---

## 6. SWARM - 群体模式

### 适用场景

**最佳适用**:
- 大规模批量任务
- 独立重复操作
- 需要广泛覆盖
- 可分区并行

**实际案例**:
- 批量文件迁移
- 大规模代码重构
- 批量数据处理
- 全项目依赖更新

### 架构模式

```
                    ┌────────────┐
                    │    Task    │
                    └──────┬─────┘
                           │
                    Decompose to
                     N subtasks
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
    ▼                      ▼                      ▼
┌────────┐  ┌────────┐  ┌────────┐          ┌────────┐
│Worker 1│  │Worker 2│  │Worker 3│   ...    │Worker N│
└───┬────┘  └───┬────┘  └───┬────┘          └───┬────┘
    │           │           │                    │
    └───────────┴───────────┴────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Coordinator │
                    │  (Monitor &  │
                    │   Aggregate) │
                    └──────┬───────┘
                           │
                    ┌──────▼──────┐
                    │   Results   │
                    └─────────────┘
```

### 实现方式

#### 伪代码
```python
def swarm_pattern(task, subtasks):
    """群体模式: 大规模并行处理"""

    # 配置
    MAX_WORKERS = 10
    BATCH_SIZE = 50

    # 分批处理
    batches = [subtasks[i:i+BATCH_SIZE]
               for i in range(0, len(subtasks), BATCH_SIZE)]

    all_results = []

    for batch_num, batch in enumerate(batches):
        print(f"Processing batch {batch_num+1}/{len(batches)}")

        # 为当前批次创建workers
        workers = []
        for subtask in batch:
            worker = create_lightweight_worker(subtask)
            workers.append(worker)

        # 并行执行当前批次
        batch_results = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(worker.execute)
                for worker in workers[:MAX_WORKERS]
            ]

            # 进度监控
            completed = 0
            for future in as_completed(futures):
                result = future.result()
                batch_results.append(result)
                completed += 1

                # 实时进度报告
                progress = (completed / len(batch)) * 100
                print(f"Progress: {progress:.1f}%")

        all_results.extend(batch_results)

        # 批次间短暂休息(可选)
        if batch_num < len(batches) - 1:
            time.sleep(1)

    # 聚合所有结果
    summary = aggregate_swarm_results(all_results)

    return summary

def create_lightweight_worker(subtask):
    """创建轻量级工作者"""
    return Agent(
        model="haiku",  # 使用快速廉价模型
        task=subtask,
        timeout=60,
        retry=1
    )

def aggregate_swarm_results(results):
    """聚合群体执行结果"""
    success = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'failed']

    return {
        'total': len(results),
        'success_count': len(success),
        'failed_count': len(failed),
        'success_rate': len(success) / len(results),
        'results': results,
        'failed_tasks': [r['task'] for r in failed]
    }
```

#### Claude Code 实现
```markdown
## 群体执行计划

### 任务概览
**总任务**: 将200个文件从CommonJS迁移到ES Modules
**策略**: SWARM
**批次**: 4批 (50文件/批)
**并行度**: 10 workers/批

---

### 配置

```yaml
swarm_config:
  total_tasks: 200
  batch_size: 50
  max_workers: 10
  worker_model: "haiku"
  timeout_per_task: 60
  retry_attempts: 1
  fail_strategy: "log_and_continue"
```

---

### 执行流程

#### Batch 1: 文件 1-50
```
Workers: 10 (Haiku agents)
任务: 迁移 src/utils/*.js (50个文件)

进度监控:
[████████░░] 80% (40/50 completed)
- 成功: 39
- 失败: 1 (utils/legacy.js - 需手动处理)
- 进行中: 10

预计时间: 5分钟
```

#### Batch 2: 文件 51-100
```
Workers: 10 (Haiku agents)
任务: 迁移 src/components/*.js (50个文件)

进度监控:
[██████████] 100% (50/50 completed)
- 成功: 50
- 失败: 0

完成时间: 4.5分钟
```

#### Batch 3: 文件 101-150
```
Workers: 10 (Haiku agents)
任务: 迁移 src/services/*.js (50个文件)

进度监控:
[██████████] 100% (50/50 completed)
- 成功: 48
- 失败: 2 (需要额外处理)

完成时间: 5分钟
```

#### Batch 4: 文件 151-200
```
Workers: 10 (Haiku agents)
任务: 迁移 src/lib/*.js (50个文件)

进度监控:
[██████████] 100% (50/50 completed)
- 成功: 50
- 失败: 0

完成时间: 4.5分钟
```

---

### 聚合结果

**总体统计**:
```
总文件数: 200
成功迁移: 187
失败: 3
跳过: 10 (已是ES Modules)
成功率: 93.5%
总时间: 19分钟
```

**失败详情**:
1. `src/utils/legacy.js` - 复杂依赖，需手动处理
2. `src/services/old-api.js` - 使用动态require
3. `src/services/deprecated.js` - 已废弃，建议删除

**后续行动**:
- [ ] 手动处理3个失败文件
- [ ] 运行测试验证迁移
- [ ] 更新文档

---

### 性能对比

| 方式 | 时间 | 成本 |
|-----|------|------|
| 手动迁移 | ~40小时 | 高 |
| 单Agent串行 | ~6.7小时 | 中 |
| SWARM并行 | ~19分钟 | 低 |

**加速**: 21x vs 单Agent，126x vs 手动
```

### 性能特征

| 指标 | 数值 |
|-----|-----|
| 预期加速比 | 5-10x (vs 单Agent) |
| 最大并行度 | 10-20 |
| 单任务超时 | 30-60s |
| 批次大小 | 50 |
| 成本效率 | 高(使用Haiku) |

### 配置参数

```yaml
swarm_config:
  max_workers: 10              # 最大并行workers
  batch_size: 50               # 每批任务数
  worker_model: "haiku"        # 使用轻量模型
  timeout_per_task: 60         # 单任务超时
  retry_attempts: 1            # 重试次数
  fail_strategy: "continue"    # 失败后继续
  progress_reporting: true     # 实时进度
  checkpoint_interval: 10      # 进度保存间隔
```

### 使用示例

#### 示例1: 代码格式化
```markdown
任务: 格式化1000个代码文件

配置:
- 批次: 20批 (50文件/批)
- Workers: 10
- 模型: Haiku
- 超时: 30s

执行:
Batch 1/20: [████] 100% - 2.5min
Batch 2/20: [████] 100% - 2.3min
...
Batch 20/20: [████] 100% - 2.4min

结果:
- 成功: 998
- 失败: 2 (语法错误文件)
- 总时间: 50分钟
- 单Agent需: 8.3小时
- 加速: 10x
```

#### 示例2: 依赖更新
```markdown
任务: 更新500个package.json中的依赖版本

配置:
- 批次: 10批 (50文件/批)
- Workers: 10
- 模型: Haiku

执行:
[██████████] 100% (500/500)
成功: 495
失败: 5 (版本冲突)

总时间: 25分钟
vs 手动: 估计20小时
```

### 注意事项

**优势**:
- 极高并行度
- 适合大规模任务
- 成本效率高
- 实时进度可见

**限制**:
- 仅适用于独立任务
- 需要良好的任务分解
- 可能需要后处理

**最佳实践**:
- 使用轻量级模型(Haiku)
- 设置合理的批次大小
- 实时监控进度
- 记录失败任务便于重试
- 设置检查点支持断点续传

---

## 7. HYBRID - 混合模式

### 适用场景

当任务包含多种特征，需要组合多种策略时使用混合模式。

### 架构模式

```
Task
 ├─ Phase 1: SEQUENTIAL
 │   ├─ 需求分析
 │   └─ 架构设计
 ├─ Phase 2: PARALLEL
 │   ├─ 前端开发
 │   ├─ 后端开发
 │   └─ 数据库设计
 ├─ Phase 3: COLLABORATIVE
 │   ├─ 集成测试
 │   └─ 安全审查
 └─ Phase 4: SEQUENTIAL
     ├─ 修复问题
     └─ 部署上线
```

### 实现示例

```markdown
## 混合执行计划

### Phase 1: 准备阶段 (SEQUENTIAL)
1. architect: 需求分析
2. architect: 架构设计

### Phase 2: 开发阶段 (HIERARCHICAL + PARALLEL)
architect领导:
- developer#1: 前端开发
- developer#2: 后端开发
- data-scientist: 数据库设计

### Phase 3: 审查阶段 (COLLABORATIVE)
多专家协作:
- security-analyst: 安全审查
- performance-expert: 性能审查
- code-reviewer: 代码审查

### Phase 4: 收尾阶段 (SEQUENTIAL)
1. debugger: 修复发现的问题
2. architect: 最终验收和部署
```

---

## 性能对比总结

| 模式 | 加速比 | 质量 | 成本 | 适用规模 |
|-----|--------|------|------|---------|
| PARALLEL | 3-5x | 中 | 中 | 小-中 |
| SEQUENTIAL | 1x | 高 | 低 | 小 |
| HIERARCHICAL | 2-3x | 高 | 高 | 中 |
| COLLABORATIVE | 2.8-4.4x | 极高 | 高 | 中 |
| COMPETITIVE | 1.5-2x | 最优 | 高 | 小 |
| SWARM | 5-10x | 中 | 低 | 大 |
| HYBRID | 变化 | 高 | 中-高 | 变化 |

---

## 选择指南

```
独立任务? ────YES───▶ PARALLEL
    │
    NO
    │
大规模(50+)? ──YES───▶ SWARM
    │
    NO
    │
强依赖链? ────YES───▶ SEQUENTIAL
    │
    NO
    │
需要专家? ────YES───▶ HIERARCHICAL
    │
    NO
    │
跨领域? ──────YES───▶ COLLABORATIVE
    │
    NO
    │
探索性? ──────YES───▶ COMPETITIVE
    │
    NO
    │
复杂任务? ────YES───▶ HYBRID
    │
    NO
    │
默认 ─────────────▶ PARALLEL
```

---

**使用建议**:
1. 优先考虑PARALLEL和SWARM获得最大效率
2. 复杂决策使用HIERARCHICAL或COLLABORATIVE
3. 质量优先使用COMPETITIVE
4. 实际项目常用HYBRID组合多种模式

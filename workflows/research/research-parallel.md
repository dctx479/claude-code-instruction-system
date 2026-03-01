# Research Parallel Workflow

> 多 Scientist Agent 并行工作的科研工作流

## 概述

Research Parallel Workflow 实现了科研任务的高效并行执行，多个专家 Agent 可以同时进行文献综述、实验设计、数据分析等任务。

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                  Research Orchestrator                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    ┌─────────────┐                          │
│                    │  Research   │                          │
│                    │   Task      │                          │
│                    └──────┬──────┘                          │
│                           │                                 │
│                    Task Decomposition                       │
│                           │                                 │
│           ┌───────────────┼───────────────┐                │
│           │               │               │                │
│           ▼               ▼               ▼                │
│    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │
│    │ Literature   │ │ Experiment   │ │ Data         │      │
│    │ Manager      │ │ Logger       │ │ Analyst      │      │
│    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘      │
│           │               │               │                │
│           │   PARALLEL    │   PARALLEL    │                │
│           │               │               │                │
│           ▼               ▼               ▼                │
│    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │
│    │ Literature   │ │ Experiment   │ │ Statistical  │      │
│    │ Review       │ │ Design       │ │ Analysis     │      │
│    └──────────────┘ └──────────────┘ └──────────────┘      │
│           │               │               │                │
│           └───────────────┼───────────────┘                │
│                           │                                 │
│                    ┌──────▼──────┐                          │
│                    │   Merge &   │                          │
│                    │   Synthesis │                          │
│                    └──────┬──────┘                          │
│                           │                                 │
│                    ┌──────▼──────┐                          │
│                    │   Paper     │                          │
│                    │   Writing   │                          │
│                    └─────────────┘                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 并行执行策略

### 1. 文献综述并行化

```yaml
literature_review_parallel:
  strategy: SWARM
  workers: 5
  distribution:
    - worker_1: "Background & Motivation (20 papers)"
    - worker_2: "Methodology Review (25 papers)"
    - worker_3: "Dataset & Benchmark (15 papers)"
    - worker_4: "State-of-the-Art (30 papers)"
    - worker_5: "Future Directions (10 papers)"
  merge_strategy: section_assembly
  quality_check: cross_reference_validation
```

### 2. 实验并行化

```yaml
experiment_parallel:
  strategy: PARALLEL
  experiments:
    - exp_001:
        name: "Baseline Model"
        agent: experiment-logger
        model: sonnet
    - exp_002:
        name: "Proposed Method A"
        agent: experiment-logger
        model: sonnet
    - exp_003:
        name: "Proposed Method B"
        agent: experiment-logger
        model: sonnet
    - exp_004:
        name: "Ablation Study"
        agent: experiment-logger
        model: sonnet
  sync_points:
    - hyperparameter_sharing
    - intermediate_results_comparison
  merge_strategy: results_aggregation
```

### 3. 数据分析并行化

```yaml
data_analysis_parallel:
  strategy: HIERARCHICAL
  lead: data-analyst (opus)
  workers:
    - worker_1: "Descriptive Statistics"
    - worker_2: "Correlation Analysis"
    - worker_3: "Hypothesis Testing"
    - worker_4: "Visualization Generation"
  coordination:
    - lead_reviews_results
    - workers_refine_analysis
  output: unified_analysis_report
```

## 工作流定义

### Phase 1: 研究规划

```python
def research_planning(research_question):
    # 1. 分析研究问题
    analysis = analyze_research_question(research_question)

    # 2. 确定研究类型
    research_type = classify_research(analysis)
    # - literature_review_only
    # - experimental_study
    # - data_analysis_study
    # - mixed_methods

    # 3. 分配任务
    tasks = allocate_research_tasks(research_type)

    # 4. 选择并行策略
    strategy = select_parallel_strategy(tasks)

    return ResearchPlan(tasks=tasks, strategy=strategy)
```

### Phase 2: 并行执行

```python
async def parallel_execution(plan):
    results = {}

    # 创建并行任务组
    task_groups = create_task_groups(plan)

    for group in task_groups:
        # 并行执行组内任务
        group_results = await asyncio.gather(*[
            execute_research_task(task)
            for task in group.tasks
        ])

        # 合并组结果
        results[group.name] = merge_group_results(group_results)

        # 同步点检查
        if group.has_sync_point:
            await sync_and_validate(results)

    return results
```

### Phase 3: 结果综合

```python
def synthesize_results(parallel_results):
    # 1. 收集所有结果
    literature = parallel_results['literature']
    experiments = parallel_results['experiments']
    analysis = parallel_results['analysis']

    # 2. 交叉验证
    cross_validate(literature, experiments, analysis)

    # 3. 综合撰写
    synthesis = paper_writing_assistant.synthesize(
        literature=literature,
        experiments=experiments,
        analysis=analysis
    )

    return synthesis
```

## Agent 配置

### Literature Manager (并行模式)

```yaml
name: literature-manager-parallel
model: sonnet
parallel_config:
  max_workers: 5
  batch_size: 20
  timeout_per_batch: 30m
tasks:
  - search_papers
  - extract_summaries
  - build_citation_graph
  - generate_section_draft
output:
  - literature_database.json
  - section_drafts/
  - citation_graph.json
```

### Experiment Logger (并行模式)

```yaml
name: experiment-logger-parallel
model: sonnet
parallel_config:
  max_experiments: 4
  shared_resources:
    - config_templates
    - baseline_results
  isolation: true  # 每个实验独立 worktree
tasks:
  - setup_experiment
  - run_training
  - collect_metrics
  - generate_report
output:
  - experiments/
    - exp_001/
    - exp_002/
    - ...
```

### Data Analyst (并行模式)

```yaml
name: data-analyst-parallel
model: sonnet
parallel_config:
  analysis_types:
    - descriptive
    - inferential
    - visualization
  coordination: hierarchical
tasks:
  - load_data
  - run_analysis
  - generate_figures
  - write_analysis_section
output:
  - analysis_report.md
  - figures/
  - statistical_tables/
```

## 同步机制

### 同步点定义

```yaml
sync_points:
  literature_complete:
    trigger: all_sections_drafted
    action: cross_reference_check
    participants: [all_literature_workers]

  baseline_established:
    trigger: baseline_experiment_complete
    action: share_baseline_metrics
    participants: [all_experiment_workers]

  analysis_validated:
    trigger: statistical_tests_complete
    action: lead_review
    participants: [lead_analyst, workers]
```

### 冲突解决

```yaml
conflict_resolution:
  citation_conflicts:
    strategy: authoritative_source
    fallback: human_review

  metric_discrepancies:
    strategy: statistical_test
    threshold: 0.05

  interpretation_differences:
    strategy: lead_decision
    escalation: human_review
```

## 使用示例

### 示例 1: 完整文献综述

```bash
/literature-review "Deep Learning for Medical Image Segmentation" \
  --parallel \
  --workers 5 \
  --zotero-collection "Medical Imaging" \
  --output ./reviews/medical-imaging-review/
```

执行流程:
```
[00:00] 启动并行文献综述
[00:01] 分配 5 个 workers
        - Worker 1: Background (20 papers)
        - Worker 2: Methods (25 papers)
        - Worker 3: Datasets (15 papers)
        - Worker 4: SOTA (30 papers)
        - Worker 5: Future (10 papers)
[00:30] Worker 3 完成 (最快)
[00:45] Worker 1, 5 完成
[01:00] Worker 2, 4 完成
[01:05] 开始交叉引用验证
[01:15] 合并各章节
[01:30] 生成完整综述
[01:45] 完成！
```

### 示例 2: 并行实验

```bash
/experiment-track parallel \
  --config experiments/config.yaml \
  --workers 4 \
  --shared-baseline
```

执行流程:
```
[00:00] 启动并行实验
[00:05] 运行 baseline (共享)
[00:30] Baseline 完成，分享到所有 workers
[00:31] 并行启动 4 个实验
        - Exp 1: Method A (GPU 0)
        - Exp 2: Method B (GPU 1)
        - Exp 3: Method C (GPU 2)
        - Exp 4: Ablation (GPU 3)
[02:00] Exp 4 完成 (最快)
[03:00] Exp 1, 2 完成
[03:30] Exp 3 完成
[03:35] 汇总结果
[03:45] 生成对比报告
[04:00] 完成！
```

### 示例 3: 协作数据分析

```bash
/agents data-analyst "分析用户行为数据" \
  --parallel \
  --lead-model opus \
  --worker-model sonnet
```

执行流程:
```
[00:00] Lead Analyst 规划分析任务
[00:05] 分配给 4 个 workers
        - Descriptive: 基础统计
        - Correlation: 相关性分析
        - Testing: 假设检验
        - Visualization: 图表生成
[00:10] Workers 并行执行
[00:25] 初步结果汇总
[00:30] Lead 审核，发现异常
[00:35] Worker 2 重新分析
[00:45] 最终审核通过
[00:50] 生成综合报告
[01:00] 完成！
```

## 性能指标

| 场景 | 串行时间 | 并行时间 | 加速比 |
|------|----------|----------|--------|
| 100 篇文献综述 | 5 小时 | 1.5 小时 | 3.3x |
| 4 组实验 | 8 小时 | 3.5 小时 | 2.3x |
| 完整数据分析 | 2 小时 | 45 分钟 | 2.7x |

## 配置文件

```json
{
  "research_parallel": {
    "enabled": true,
    "default_strategy": "PARALLEL",
    "max_workers": {
      "literature": 5,
      "experiments": 4,
      "analysis": 4
    },
    "sync_timeout": "5m",
    "retry_policy": {
      "max_retries": 2,
      "backoff": "exponential"
    },
    "resource_limits": {
      "max_memory_per_worker": "4GB",
      "max_gpu_per_worker": 1
    }
  }
}
```

## 相关文档

- 文献综述命令: `commands/research/literature-review.md`
- 实验追踪命令: `commands/research/experiment-track.md`
- 科研 Agent: `agents/research/`
- 编排模式: `workflows/orchestration/orchestration-patterns.md`

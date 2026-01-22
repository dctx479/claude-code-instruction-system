# 编排监控与结果整合系统

## 概述

本文档定义了Agent编排过程中的监控机制、进度追踪、异常处理和结果整合策略。

---

## 目录

1. [监控机制](#1-监控机制)
2. [进度追踪](#2-进度追踪)
3. [异常检测与处理](#3-异常检测与处理)
4. [结果整合策略](#4-结果整合策略)
5. [性能分析](#5-性能分析)
6. [日志与审计](#6-日志与审计)

---

## 1. 监控机制

### 1.1 实时状态监控

#### 监控维度

```yaml
agent_monitoring:
  health:                       # 健康状态
    - agent_responsive           # Agent是否响应
    - resource_usage             # 资源使用情况
    - error_rate                 # 错误率

  progress:                     # 进度状态
    - tasks_completed            # 已完成任务数
    - tasks_in_progress          # 进行中任务数
    - tasks_pending              # 待处理任务数

  performance:                  # 性能指标
    - avg_response_time          # 平均响应时间
    - throughput                 # 吞吐量
    - success_rate               # 成功率

  quality:                      # 质量指标
    - output_quality_score       # 输出质量评分
    - retry_count                # 重试次数
    - validation_pass_rate       # 验证通过率
```

#### 监控实现

```python
class AgentMonitor:
    """Agent监控器"""

    def __init__(self):
        self.agents = {}
        self.metrics = {}
        self.alerts = []

    def register_agent(self, agent_id, agent_info):
        """注册Agent到监控系统"""
        self.agents[agent_id] = {
            'info': agent_info,
            'status': 'idle',
            'start_time': None,
            'metrics': self.init_metrics()
        }

    def init_metrics(self):
        """初始化指标"""
        return {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_response_time': 0,
            'error_count': 0,
            'last_heartbeat': time.time()
        }

    def update_status(self, agent_id, status, task_info=None):
        """更新Agent状态"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not registered")

        agent = self.agents[agent_id]
        agent['status'] = status
        agent['last_update'] = time.time()

        if status == 'working':
            agent['start_time'] = time.time()
            agent['current_task'] = task_info

        elif status == 'completed':
            duration = time.time() - agent['start_time']
            agent['metrics']['tasks_completed'] += 1
            agent['metrics']['total_response_time'] += duration

        elif status == 'failed':
            agent['metrics']['tasks_failed'] += 1
            agent['metrics']['error_count'] += 1
            self.trigger_alert(agent_id, 'task_failed')

    def check_health(self):
        """健康检查"""
        unhealthy_agents = []

        for agent_id, agent in self.agents.items():
            # 检查心跳
            last_heartbeat = agent['metrics']['last_heartbeat']
            if time.time() - last_heartbeat > 60:  # 60秒无响应
                unhealthy_agents.append({
                    'agent_id': agent_id,
                    'reason': 'no_heartbeat',
                    'last_seen': last_heartbeat
                })
                continue

            # 检查错误率
            metrics = agent['metrics']
            total_tasks = metrics['tasks_completed'] + metrics['tasks_failed']
            if total_tasks > 0:
                error_rate = metrics['tasks_failed'] / total_tasks
                if error_rate > 0.3:  # 错误率 > 30%
                    unhealthy_agents.append({
                        'agent_id': agent_id,
                        'reason': 'high_error_rate',
                        'error_rate': error_rate
                    })

        return unhealthy_agents

    def get_statistics(self):
        """获取统计信息"""
        total_completed = sum(
            a['metrics']['tasks_completed']
            for a in self.agents.values()
        )
        total_failed = sum(
            a['metrics']['tasks_failed']
            for a in self.agents.values()
        )

        return {
            'total_agents': len(self.agents),
            'active_agents': sum(
                1 for a in self.agents.values()
                if a['status'] == 'working'
            ),
            'total_completed': total_completed,
            'total_failed': total_failed,
            'success_rate': (
                total_completed / (total_completed + total_failed)
                if (total_completed + total_failed) > 0
                else 0
            )
        }
```

### 1.2 可视化监控界面

#### 终端输出格式

```markdown
┌─────────────────────────────────────────────────────────┐
│  Agent 编排监控面板                                     │
│  时间: 2026-01-16 14:30:45                              │
└─────────────────────────────────────────────────────────┘

策略: HIERARCHICAL          状态: 运行中
总任务: 10                  进度: 70% [███████░░░]

┌─ Agents ────────────────────────────────────────────────┐
│ ID        │ 状态      │ 任务    │ 成功率  │ 响应时间    │
│───────────│───────────│─────────│─────────│─────────────│
│ architect │ working   │ T1      │ 100%    │ 45s         │
│ worker-1  │ completed │ T2      │ 100%    │ 120s        │
│ worker-2  │ working   │ T3      │ 100%    │ 85s         │
│ worker-3  │ failed    │ T4      │ 50%     │ N/A         │
└─────────────────────────────────────────────────────────┘

┌─ 最近事件 ──────────────────────────────────────────────┐
│ [14:30:40] ✓ worker-1 完成任务 T2                       │
│ [14:30:35] ⚠ worker-3 任务 T4 失败，正在重试           │
│ [14:30:20] → worker-2 开始任务 T3                       │
│ [14:30:15] ✓ worker-1 完成任务 T1                       │
└─────────────────────────────────────────────────────────┘

总览: 成功 7 | 失败 1 | 进行中 2 | 待处理 3
```

### 1.3 告警机制

#### 告警规则

```yaml
alert_rules:
  agent_unresponsive:
    condition: "heartbeat_timeout > 60s"
    severity: "high"
    action: "restart_agent"

  high_error_rate:
    condition: "error_rate > 0.3"
    severity: "medium"
    action: "switch_to_backup_agent"

  task_timeout:
    condition: "task_duration > timeout_threshold"
    severity: "medium"
    action: "terminate_and_retry"

  resource_exhaustion:
    condition: "memory_usage > 90%"
    severity: "high"
    action: "pause_new_tasks"
```

#### 告警处理

```python
class AlertHandler:
    """告警处理器"""

    def __init__(self, monitor):
        self.monitor = monitor
        self.handlers = {
            'agent_unresponsive': self.handle_unresponsive,
            'high_error_rate': self.handle_high_errors,
            'task_timeout': self.handle_timeout
        }

    def trigger_alert(self, alert_type, agent_id, details):
        """触发告警"""
        alert = {
            'type': alert_type,
            'agent_id': agent_id,
            'timestamp': time.time(),
            'details': details,
            'status': 'new'
        }

        # 记录告警
        self.monitor.alerts.append(alert)

        # 执行告警处理
        if alert_type in self.handlers:
            self.handlers[alert_type](agent_id, details)

    def handle_unresponsive(self, agent_id, details):
        """处理无响应Agent"""
        print(f"⚠ Agent {agent_id} 无响应，尝试重启...")

        # 1. 保存当前状态
        agent_state = self.monitor.agents[agent_id]

        # 2. 尝试重启
        try:
            restart_agent(agent_id)
            print(f"✓ Agent {agent_id} 重启成功")
        except Exception as e:
            print(f"✗ Agent {agent_id} 重启失败: {e}")

            # 3. 切换到备用Agent
            backup_agent = self.get_backup_agent(agent_id)
            if backup_agent:
                self.transfer_task(agent_id, backup_agent)

    def handle_high_errors(self, agent_id, details):
        """处理高错误率"""
        print(f"⚠ Agent {agent_id} 错误率过高: {details['error_rate']:.1%}")

        # 1. 分析错误模式
        error_pattern = self.analyze_errors(agent_id)

        # 2. 根据模式采取行动
        if error_pattern == 'model_capability':
            # 升级到更强模型
            self.upgrade_agent_model(agent_id)
        elif error_pattern == 'input_quality':
            # 改进输入质量
            self.enhance_task_description(agent_id)

    def handle_timeout(self, agent_id, details):
        """处理超时"""
        print(f"⚠ Agent {agent_id} 任务超时")

        # 1. 终止当前任务
        terminate_agent_task(agent_id)

        # 2. 重新分配任务
        task = details['task']
        self.reassign_task(task, exclude=[agent_id])
```

---

## 2. 进度追踪

### 2.1 任务状态模型

```python
class TaskStatus:
    """任务状态定义"""
    PENDING = 'pending'           # 待处理
    QUEUED = 'queued'            # 已排队
    ASSIGNED = 'assigned'         # 已分配
    IN_PROGRESS = 'in_progress'   # 进行中
    COMPLETED = 'completed'       # 已完成
    FAILED = 'failed'            # 失败
    RETRYING = 'retrying'        # 重试中
    CANCELLED = 'cancelled'      # 已取消

class Task:
    """任务对象"""

    def __init__(self, task_id, description):
        self.id = task_id
        self.description = description
        self.status = TaskStatus.PENDING
        self.agent_id = None
        self.start_time = None
        self.end_time = None
        self.result = None
        self.error = None
        self.retry_count = 0

    def assign_to(self, agent_id):
        """分配给Agent"""
        self.agent_id = agent_id
        self.status = TaskStatus.ASSIGNED

    def start(self):
        """开始执行"""
        self.status = TaskStatus.IN_PROGRESS
        self.start_time = time.time()

    def complete(self, result):
        """完成"""
        self.status = TaskStatus.COMPLETED
        self.end_time = time.time()
        self.result = result

    def fail(self, error):
        """失败"""
        self.status = TaskStatus.FAILED
        self.end_time = time.time()
        self.error = error

    def retry(self):
        """重试"""
        self.retry_count += 1
        self.status = TaskStatus.RETRYING

    def duration(self):
        """执行时长"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
```

### 2.2 进度计算

```python
class ProgressTracker:
    """进度追踪器"""

    def __init__(self, tasks):
        self.tasks = {t.id: t for t in tasks}
        self.total = len(tasks)

    def get_progress(self):
        """获取进度"""
        status_counts = {
            TaskStatus.COMPLETED: 0,
            TaskStatus.FAILED: 0,
            TaskStatus.IN_PROGRESS: 0,
            TaskStatus.PENDING: 0
        }

        for task in self.tasks.values():
            status_counts[task.status] = status_counts.get(task.status, 0) + 1

        completed = status_counts[TaskStatus.COMPLETED]
        failed = status_counts[TaskStatus.FAILED]
        in_progress = status_counts[TaskStatus.IN_PROGRESS]
        pending = self.total - completed - failed - in_progress

        return {
            'total': self.total,
            'completed': completed,
            'failed': failed,
            'in_progress': in_progress,
            'pending': pending,
            'percentage': (completed / self.total * 100) if self.total > 0 else 0,
            'success_rate': (
                completed / (completed + failed)
                if (completed + failed) > 0
                else 0
            )
        }

    def estimate_remaining_time(self):
        """估算剩余时间"""
        completed_tasks = [
            t for t in self.tasks.values()
            if t.status == TaskStatus.COMPLETED
        ]

        if not completed_tasks:
            return None

        # 计算平均完成时间
        avg_duration = sum(t.duration() for t in completed_tasks) / len(completed_tasks)

        # 计算剩余任务数
        remaining = sum(
            1 for t in self.tasks.values()
            if t.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]
        )

        return avg_duration * remaining

    def get_visual_progress(self, width=50):
        """生成可视化进度条"""
        progress = self.get_progress()
        percentage = progress['percentage']

        filled = int(width * percentage / 100)
        empty = width - filled

        bar = '█' * filled + '░' * empty
        return f"[{bar}] {percentage:.1f}%"
```

### 2.3 里程碑与检查点

```python
class Milestone:
    """里程碑"""

    def __init__(self, name, required_tasks):
        self.name = name
        self.required_tasks = required_tasks
        self.status = 'pending'
        self.completion_time = None

    def check_completion(self, completed_tasks):
        """检查是否完成"""
        if all(task_id in completed_tasks for task_id in self.required_tasks):
            self.status = 'completed'
            self.completion_time = time.time()
            return True
        return False

class CheckpointManager:
    """检查点管理器"""

    def __init__(self, milestones):
        self.milestones = milestones
        self.checkpoints = []

    def evaluate_milestones(self, tracker):
        """评估里程碑"""
        completed_task_ids = [
            tid for tid, t in tracker.tasks.items()
            if t.status == TaskStatus.COMPLETED
        ]

        newly_completed = []
        for milestone in self.milestones:
            if milestone.status == 'pending':
                if milestone.check_completion(completed_task_ids):
                    newly_completed.append(milestone)
                    self.save_checkpoint(milestone)

        return newly_completed

    def save_checkpoint(self, milestone):
        """保存检查点"""
        checkpoint = {
            'milestone': milestone.name,
            'timestamp': time.time(),
            'state_snapshot': self.capture_state()
        }
        self.checkpoints.append(checkpoint)
        print(f"✓ 里程碑达成: {milestone.name}")
```

---

## 3. 异常检测与处理

### 3.1 异常类型

```python
class OrchestrationException:
    """编排异常基类"""

class AgentException(OrchestrationException):
    """Agent异常"""
    UNRESPONSIVE = 'unresponsive'      # 无响应
    OVERLOADED = 'overloaded'          # 过载
    CRASHED = 'crashed'                # 崩溃
    RATE_LIMITED = 'rate_limited'      # 速率限制

class TaskException(OrchestrationException):
    """任务异常"""
    TIMEOUT = 'timeout'                # 超时
    VALIDATION_FAILED = 'validation_failed'  # 验证失败
    DEPENDENCY_FAILED = 'dependency_failed'  # 依赖失败
    INVALID_INPUT = 'invalid_input'    # 输入无效

class SystemException(OrchestrationException):
    """系统异常"""
    RESOURCE_EXHAUSTED = 'resource_exhausted'  # 资源耗尽
    NETWORK_ERROR = 'network_error'    # 网络错误
    QUOTA_EXCEEDED = 'quota_exceeded'  # 配额超限
```

### 3.2 异常处理策略

```python
class ExceptionHandler:
    """异常处理器"""

    def __init__(self):
        self.strategies = {
            AgentException.UNRESPONSIVE: self.handle_unresponsive,
            AgentException.OVERLOADED: self.handle_overloaded,
            TaskException.TIMEOUT: self.handle_timeout,
            TaskException.VALIDATION_FAILED: self.handle_validation_failed,
            SystemException.RESOURCE_EXHAUSTED: self.handle_resource_exhausted
        }
        self.max_retries = 3

    def handle_exception(self, exception_type, context):
        """处理异常"""
        if exception_type in self.strategies:
            return self.strategies[exception_type](context)
        else:
            return self.default_handler(exception_type, context)

    def handle_unresponsive(self, context):
        """处理无响应"""
        agent_id = context['agent_id']
        task = context['task']

        # 策略1: 重试
        if task.retry_count < self.max_retries:
            print(f"→ 重试任务 {task.id} (尝试 {task.retry_count + 1})")
            task.retry()
            return {'action': 'retry', 'agent_id': agent_id}

        # 策略2: 切换Agent
        print(f"→ 切换到备用Agent")
        backup_agent = self.find_backup_agent(agent_id)
        return {'action': 'reassign', 'new_agent_id': backup_agent}

    def handle_overloaded(self, context):
        """处理过载"""
        agent_id = context['agent_id']

        # 策略1: 减少并发
        print(f"→ Agent {agent_id} 过载，降低并发度")
        reduce_concurrency(agent_id)

        # 策略2: 扩展Agent池
        print(f"→ 启动额外的Agent实例")
        spawn_additional_agents()

        return {'action': 'scale_up'}

    def handle_timeout(self, context):
        """处理超时"""
        task = context['task']

        # 策略1: 增加超时时间重试
        if task.retry_count < 2:
            new_timeout = context['timeout'] * 1.5
            print(f"→ 增加超时时间至 {new_timeout}s 并重试")
            return {'action': 'retry', 'timeout': new_timeout}

        # 策略2: 分解任务
        print(f"→ 任务过于复杂，尝试分解")
        return {'action': 'decompose', 'task': task}

    def handle_validation_failed(self, context):
        """处理验证失败"""
        task = context['task']
        validation_error = context['error']

        print(f"⚠ 任务 {task.id} 输出验证失败: {validation_error}")

        # 策略1: 修正并重试
        if task.retry_count < self.max_retries:
            enhanced_task = self.enhance_task_with_feedback(
                task,
                validation_error
            )
            return {'action': 'retry', 'task': enhanced_task}

        # 策略2: 人工介入
        return {'action': 'manual_review', 'task': task}

    def handle_resource_exhausted(self, context):
        """处理资源耗尽"""
        # 策略: 暂停新任务，等待资源释放
        print("⚠ 资源耗尽，暂停新任务")
        return {
            'action': 'pause',
            'wait_duration': 60,
            'retry_condition': 'resource_available'
        }
```

### 3.3 故障恢复

```python
class FailoverManager:
    """故障转移管理器"""

    def __init__(self):
        self.backup_agents = {}
        self.recovery_strategies = {}

    def register_backup(self, primary_agent, backup_agent):
        """注册备用Agent"""
        self.backup_agents[primary_agent] = backup_agent

    def failover(self, failed_agent_id, tasks):
        """故障转移"""
        # 1. 获取备用Agent
        backup_agent = self.backup_agents.get(failed_agent_id)

        if not backup_agent:
            # 动态创建备用Agent
            backup_agent = self.create_backup_agent(failed_agent_id)

        # 2. 转移任务
        for task in tasks:
            task.assign_to(backup_agent)
            print(f"→ 任务 {task.id} 转移至 {backup_agent}")

        # 3. 记录故障转移
        self.log_failover(failed_agent_id, backup_agent, len(tasks))

        return backup_agent

    def create_backup_agent(self, failed_agent_id):
        """创建备用Agent"""
        # 基于失败Agent的配置创建新实例
        original_config = get_agent_config(failed_agent_id)

        backup_config = {
            **original_config,
            'agent_id': f"{failed_agent_id}_backup",
            'priority': 'high'
        }

        backup_agent = spawn_agent(backup_config)
        return backup_agent.id
```

---

## 4. 结果整合策略

### 4.1 结果收集

```python
class ResultCollector:
    """结果收集器"""

    def __init__(self, expected_results):
        self.expected = expected_results
        self.results = {}
        self.metadata = {}

    def add_result(self, task_id, result, metadata=None):
        """添加结果"""
        self.results[task_id] = result
        if metadata:
            self.metadata[task_id] = metadata

    def is_complete(self):
        """检查是否收集完整"""
        return len(self.results) == self.expected

    def get_results(self):
        """获取所有结果"""
        return self.results
```

### 4.2 冲突解决

```python
class ConflictResolver:
    """冲突解决器"""

    def __init__(self):
        self.resolution_strategies = {
            'priority': self.resolve_by_priority,
            'voting': self.resolve_by_voting,
            'expert': self.resolve_by_expert,
            'merge': self.resolve_by_merge
        }

    def detect_conflicts(self, results):
        """检测冲突"""
        conflicts = []

        # 检查输出不一致
        if len(set(str(r) for r in results.values())) > 1:
            conflicts.append({
                'type': 'output_mismatch',
                'results': results
            })

        return conflicts

    def resolve_by_priority(self, conflict):
        """基于优先级解决"""
        # 选择最高优先级Agent的结果
        results = conflict['results']
        priorities = {
            task_id: self.get_agent_priority(task_id)
            for task_id in results.keys()
        }

        winner = max(priorities, key=priorities.get)
        return results[winner]

    def resolve_by_voting(self, conflict):
        """基于投票解决"""
        results = conflict['results']

        # 统计相同结果的数量
        vote_counts = {}
        for result in results.values():
            key = str(result)
            vote_counts[key] = vote_counts.get(key, 0) + 1

        # 选择多数结果
        winner_key = max(vote_counts, key=vote_counts.get)

        for result in results.values():
            if str(result) == winner_key:
                return result

    def resolve_by_expert(self, conflict):
        """由专家Agent裁决"""
        results = conflict['results']

        # 提交给专家Agent审核
        expert_agent = get_expert_agent()
        decision = expert_agent.review(results)

        return decision['selected_result']

    def resolve_by_merge(self, conflict):
        """合并结果"""
        results = conflict['results']

        # 提取各结果的优点并合并
        merged = {}
        for task_id, result in results.items():
            for key, value in result.items():
                if key not in merged:
                    merged[key] = value
                else:
                    # 冲突时选择更好的值
                    merged[key] = self.select_better_value(
                        merged[key],
                        value
                    )

        return merged
```

### 4.3 结果聚合

```python
class ResultAggregator:
    """结果聚合器"""

    def __init__(self, strategy):
        self.strategy = strategy
        self.aggregation_methods = {
            'concat': self.concat_results,
            'merge': self.merge_results,
            'select_best': self.select_best_result,
            'summarize': self.summarize_results
        }

    def aggregate(self, results):
        """聚合结果"""
        if self.strategy in self.aggregation_methods:
            return self.aggregation_methods[self.strategy](results)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

    def concat_results(self, results):
        """连接结果"""
        # 适用于: 多文件审查、批量处理
        aggregated = []
        for task_id, result in sorted(results.items()):
            aggregated.append({
                'task': task_id,
                'result': result
            })
        return aggregated

    def merge_results(self, results):
        """合并结果"""
        # 适用于: 分布式搜索、并行分析
        merged = {}
        for result in results.values():
            for key, value in result.items():
                if key not in merged:
                    merged[key] = []
                if isinstance(value, list):
                    merged[key].extend(value)
                else:
                    merged[key].append(value)

        # 去重
        for key in merged:
            merged[key] = list(set(merged[key]))

        return merged

    def select_best_result(self, results):
        """选择最佳结果"""
        # 适用于: 竞争模式
        best = None
        best_score = -1

        for task_id, result in results.items():
            score = self.evaluate_result(result)
            if score > best_score:
                best_score = score
                best = result

        return {
            'best_result': best,
            'score': best_score,
            'all_results': results
        }

    def summarize_results(self, results):
        """总结结果"""
        # 适用于: 多专家协作
        summary = {
            'total_tasks': len(results),
            'key_findings': self.extract_key_findings(results),
            'common_themes': self.find_common_themes(results),
            'recommendations': self.generate_recommendations(results)
        }
        return summary
```

### 4.4 质量验证

```python
class QualityValidator:
    """质量验证器"""

    def __init__(self, criteria):
        self.criteria = criteria

    def validate_result(self, result, task):
        """验证结果质量"""
        validation_report = {
            'passed': True,
            'checks': []
        }

        for criterion in self.criteria:
            check_result = self.apply_criterion(criterion, result, task)
            validation_report['checks'].append(check_result)

            if not check_result['passed']:
                validation_report['passed'] = False

        return validation_report

    def apply_criterion(self, criterion, result, task):
        """应用验证标准"""
        if criterion == 'completeness':
            return self.check_completeness(result, task)
        elif criterion == 'correctness':
            return self.check_correctness(result, task)
        elif criterion == 'format':
            return self.check_format(result, task)
        else:
            return {'criterion': criterion, 'passed': True}

    def check_completeness(self, result, task):
        """检查完整性"""
        required_fields = task.get('required_fields', [])
        missing_fields = [
            field for field in required_fields
            if field not in result
        ]

        return {
            'criterion': 'completeness',
            'passed': len(missing_fields) == 0,
            'missing_fields': missing_fields
        }

    def check_correctness(self, result, task):
        """检查正确性"""
        # 执行测试或验证逻辑
        test_cases = task.get('test_cases', [])
        passed_tests = 0

        for test in test_cases:
            if self.run_test(test, result):
                passed_tests += 1

        pass_rate = passed_tests / len(test_cases) if test_cases else 1.0

        return {
            'criterion': 'correctness',
            'passed': pass_rate >= 0.9,
            'pass_rate': pass_rate
        }

    def check_format(self, result, task):
        """检查格式"""
        expected_format = task.get('expected_format')

        if expected_format:
            format_valid = self.validate_format(result, expected_format)
        else:
            format_valid = True

        return {
            'criterion': 'format',
            'passed': format_valid
        }
```

---

## 5. 性能分析

### 5.1 性能指标

```python
class PerformanceAnalyzer:
    """性能分析器"""

    def analyze(self, orchestration_session):
        """分析编排性能"""
        metrics = {
            'total_duration': self.calculate_total_duration(session),
            'parallel_efficiency': self.calculate_parallel_efficiency(session),
            'agent_utilization': self.calculate_agent_utilization(session),
            'speedup_ratio': self.calculate_speedup(session),
            'cost_efficiency': self.calculate_cost_efficiency(session)
        }

        return metrics

    def calculate_parallel_efficiency(self, session):
        """计算并行效率"""
        # 并行效率 = 实际加速比 / 理论加速比
        actual_speedup = session.baseline_duration / session.actual_duration
        theoretical_speedup = session.max_parallelism

        efficiency = actual_speedup / theoretical_speedup
        return efficiency

    def calculate_agent_utilization(self, session):
        """计算Agent利用率"""
        utilization = {}

        for agent_id, agent_data in session.agents.items():
            working_time = agent_data['total_working_time']
            total_time = session.actual_duration

            utilization[agent_id] = working_time / total_time

        return utilization
```

### 5.2 瓶颈识别

```python
class BottleneckDetector:
    """瓶颈检测器"""

    def detect_bottlenecks(self, session):
        """检测瓶颈"""
        bottlenecks = []

        # 检测慢Agent
        slow_agents = self.find_slow_agents(session)
        if slow_agents:
            bottlenecks.append({
                'type': 'slow_agent',
                'agents': slow_agents
            })

        # 检测任务依赖瓶颈
        dependency_bottlenecks = self.find_dependency_bottlenecks(session)
        if dependency_bottlenecks:
            bottlenecks.append({
                'type': 'dependency',
                'tasks': dependency_bottlenecks
            })

        # 检测资源瓶颈
        resource_bottlenecks = self.find_resource_bottlenecks(session)
        if resource_bottlenecks:
            bottlenecks.append({
                'type': 'resource',
                'details': resource_bottlenecks
            })

        return bottlenecks
```

---

## 6. 日志与审计

### 6.1 日志记录

```python
class OrchestrationLogger:
    """编排日志记录器"""

    def __init__(self, log_file):
        self.log_file = log_file
        self.log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']

    def log(self, level, message, context=None):
        """记录日志"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'context': context
        }

        # 写入日志文件
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def log_task_start(self, task):
        """记录任务开始"""
        self.log('INFO', f"Task {task.id} started", {
            'task_id': task.id,
            'agent_id': task.agent_id,
            'description': task.description
        })

    def log_task_complete(self, task):
        """记录任务完成"""
        self.log('INFO', f"Task {task.id} completed", {
            'task_id': task.id,
            'duration': task.duration(),
            'status': 'success'
        })

    def log_task_failed(self, task, error):
        """记录任务失败"""
        self.log('ERROR', f"Task {task.id} failed", {
            'task_id': task.id,
            'error': str(error),
            'retry_count': task.retry_count
        })
```

### 6.2 审计追踪

```yaml
audit_trail:
  orchestration_session:
    session_id: "orch-2026-01-16-001"
    start_time: "2026-01-16 14:30:00"
    end_time: "2026-01-16 14:45:30"
    strategy: "HIERARCHICAL"
    total_tasks: 10

  agents:
    - agent_id: "architect"
      model: "opus"
      tasks_assigned: 3
      tasks_completed: 3
      total_duration: 450s

    - agent_id: "worker-1"
      model: "sonnet"
      tasks_assigned: 3
      tasks_completed: 2
      tasks_failed: 1
      total_duration: 380s

  tasks:
    - task_id: "T1"
      agent: "architect"
      status: "completed"
      duration: 120s
      result_hash: "abc123..."

    - task_id: "T2"
      agent: "worker-1"
      status: "completed"
      duration: 180s
      result_hash: "def456..."

  events:
    - timestamp: "2026-01-16 14:32:15"
      type: "task_failed"
      task_id: "T4"
      agent_id: "worker-3"
      reason: "timeout"

    - timestamp: "2026-01-16 14:32:20"
      type: "task_retry"
      task_id: "T4"
      agent_id: "worker-3"
      attempt: 2

  summary:
    success_rate: 90%
    total_duration: 930s
    cost: $0.45
    speedup: 2.8x
```

---

## 总结

完整的监控与整合系统包括:

1. **实时监控**: 健康检查、状态追踪、告警机制
2. **进度管理**: 任务状态、进度计算、里程碑追踪
3. **异常处理**: 异常检测、故障转移、恢复策略
4. **结果整合**: 冲突解决、结果聚合、质量验证
5. **性能分析**: 指标计算、瓶颈识别、效率评估
6. **日志审计**: 完整记录、可追溯性、合规性

这些机制共同确保Agent编排系统的可靠性、可观察性和可维护性。

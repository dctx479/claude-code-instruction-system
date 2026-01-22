# Agent 性能报告模板

> 此模板用于生成标准化的性能报告

---

## 报告类型

### 日报模板 (daily-YYYY-MM-DD.md)
### 周报模板 (weekly-YYYY-WXX.md)
### 月报模板 (monthly-YYYY-MM.md)

---

## 日报模板

```markdown
# Agent 性能日报

**日期**: {date}
**星期**: {weekday}
**任务总数**: {total_tasks}
**总体成功率**: {success_rate}%
**总Token消耗**: {total_tokens:,}
**总成本**: ${total_cost}

---

## 关键指标概览

| Agent | 任务数 | 成功率 | 平均Token | 平均时长 | 用户评分 | 状态 |
|-------|--------|--------|-----------|----------|---------|------|
| architect | {count} | {rate}% | {tokens} | {time}s | {rating} | {status} |
| code-reviewer | {count} | {rate}% | {tokens} | {time}s | {rating} | {status} |
| debugger | {count} | {rate}% | {tokens} | {time}s | {rating} | {status} |
| security-analyst | {count} | {rate}% | {tokens} | {time}s | {rating} | {status} |
| data-scientist | {count} | {rate}% | {tokens} | {time}s | {rating} | {status} |
| orchestrator | {count} | {rate}% | {tokens} | {time}s | {rating} | {status} |

**状态说明**:
- ✅ 正常 - 所有指标在正常范围
- ⚠️ 警告 - 有指标超出阈值
- ❌ 异常 - 关键指标严重偏离

---

## 详细分析

### 最佳表现
1. **{agent_name}**: {highlight}
2. **{agent_name}**: {highlight}

### 需要关注
1. **{agent_name}**: {concern}
2. **{agent_name}**: {concern}

---

## 异常事件

### 执行失败 ({count}次)
- [{time}] {agent_name} - {task_type}: {error_message}
- [{time}] {agent_name} - {task_type}: {error_message}

### 性能异常 ({count}次)
- [{time}] {agent_name} Token消耗异常: {tokens} (阈值: {threshold})
- [{time}] {agent_name} 执行超时: {duration}s (阈值: {threshold}s)

### 质量问题 ({count}次)
- [{time}] {agent_name} 用户评分低: {rating} (任务: {task_id})

---

## 趋势提示

### 🔺 上升趋势
- {agent_name} {metric} 上升 {percentage}%

### 🔻 下降趋势
- {agent_name} {metric} 下降 {percentage}%

### ➡️ 稳定趋势
- {agent_name} 各项指标保持稳定

---

## 今日建议

1. **{建议1}**
   - 原因: {reason}
   - 优先级: {priority}

2. **{建议2}**
   - 原因: {reason}
   - 优先级: {priority}

---

## 附录

### 任务类型分布
| 类型 | 数量 | 占比 |
|------|------|------|
| {type} | {count} | {percentage}% |

### 成本分布
| Agent | 成本 | 占比 |
|-------|------|------|
| {agent} | ${cost} | {percentage}% |

---

**报告生成时间**: {timestamp}
**数据来源**: memory/agent-performance.md
**生成者**: performance-monitor Agent
```

---

## 周报模板

```markdown
# Agent 性能周报

**周期**: {start_date} - {end_date}
**周次**: {year} 年第 {week} 周
**任务总数**: {total_tasks}
**总成本**: ${total_cost}
**成本效率**: 比目标 {comparison} {percentage}%

---

## 执行摘要

### 关键成果
- ✅ 总体成功率: {rate}% (目标: >95%)
- ✅ 平均执行时间: {time}s (目标: <180s)
- ✅ 用户满意度: {rating} (目标: >4.5)

### 本周亮点
1. {highlight_1}
2. {highlight_2}
3. {highlight_3}

### 需要改进
1. {issue_1}
2. {issue_2}

---

## 总体趋势

### 成功率趋势
```
周一: {rate}% ████████████████░░░░
周二: {rate}% ██████████████████░░
周三: {rate}% ███████████████████░
周四: {rate}% ████████████████████
周五: {rate}% ███████████████████░
周六: {rate}% ██████████████████░░
周日: {rate}% █████████████████░░░

平均: {avg_rate}%
趋势: {trend} ({change}%)
```

### Token消耗趋势
```
周一: {tokens} ████████████░░░░░░░░
周二: {tokens} ██████████████░░░░░░
周三: {tokens} ███████████████░░░░░
周四: {tokens} ████████████████████
周五: {tokens} ██████████████░░░░░░
周六: {tokens} ███████████░░░░░░░░░
周日: {tokens} ██████████░░░░░░░░░░

平均: {avg_tokens}
趋势: {trend} ({change}%)
```

---

## 各Agent详细报告

### architect
**任务数**: {count} | **成功率**: {rate}% | **评分**: {rating}

| 指标 | 本周 | 上周 | 变化 | 趋势 |
|------|------|------|------|------|
| 成功率 | {rate}% | {rate}% | {change}% | {trend} |
| 平均Token | {tokens} | {tokens} | {change}% | {trend} |
| 平均时长 | {time}s | {time}s | {change}% | {trend} |
| 用户评分 | {rating} | {rating} | {change} | {trend} |
| 平均成本 | ${cost} | ${cost} | {change}% | {trend} |

**表现分析**:
{analysis_text}

**优化建议**:
1. {suggestion_1}
2. {suggestion_2}

---

[对其他Agent重复相同格式]

---

## 策略效果统计

### 并行策略 (PARALLEL)
- **使用次数**: {count}
- **成功率**: {rate}%
- **效率提升**: {improvement}%
- **最佳场景**: {scenario}

### 串行策略 (SEQUENTIAL)
- **使用次数**: {count}
- **成功率**: {rate}%
- **最佳场景**: {scenario}

### 层级策略 (HIERARCHICAL)
- **使用次数**: {count}
- **成功率**: {rate}%
- **效率提升**: {improvement}%
- **最佳场景**: {scenario}

### 协作策略 (COLLABORATIVE)
- **使用次数**: {count}
- **成功率**: {rate}%
- **最佳场景**: {scenario}

---

## 本周亮点

### 🏆 最佳表现
1. **{agent_name}** - {achievement}
2. **{agent_name}** - {achievement}

### 📈 最大进步
1. **{agent_name}** - {metric} 提升 {improvement}%
2. **{agent_name}** - {metric} 提升 {improvement}%

### 💡 创新实践
1. {innovation}
2. {innovation}

---

## 需要关注的问题

### ⚠️ 性能下降
1. **{agent_name}**: {metric} 下降 {percentage}%
   - 可能原因: {reason}
   - 建议措施: {action}

### ⚠️ 成本上升
1. **{agent_name}**: 成本上升 {percentage}%
   - 可能原因: {reason}
   - 建议措施: {action}

### ⚠️ 质量问题
1. **{agent_name}**: 用户评分下降至 {rating}
   - 可能原因: {reason}
   - 建议措施: {action}

---

## 成本分析

### 本周成本结构
| Agent | 成本 | 占比 | 环比 |
|-------|------|------|------|
| {agent} | ${cost} | {percentage}% | {change}% |

### 成本趋势
- 本周总成本: ${total_cost}
- 上周总成本: ${prev_cost}
- 变化: {change}%
- 每任务平均成本: ${avg_cost}

---

## 下周优化计划

### 高优先级
1. **{optimization_1}**
   - 目标: {target}
   - 预期收益: {benefit}
   - 负责: {owner}

### 中优先级
1. **{optimization_2}**
   - 目标: {target}
   - 预期收益: {benefit}

### 持续监控
1. {monitoring_item_1}
2. {monitoring_item_2}

---

## 附录

### 任务类型分布
| 类型 | 本周 | 上周 | 变化 |
|------|------|------|------|
| {type} | {count} | {count} | {change}% |

### 时段分布
| 时段 | 任务数 | 成功率 |
|------|--------|--------|
| 00:00-06:00 | {count} | {rate}% |
| 06:00-12:00 | {count} | {rate}% |
| 12:00-18:00 | {count} | {rate}% |
| 18:00-24:00 | {count} | {rate}% |

---

**报告生成时间**: {timestamp}
**数据来源**: memory/agent-performance.md
**生成者**: performance-monitor Agent
```

---

## 月报模板

```markdown
# Agent 性能月报

**月份**: {year} 年 {month} 月
**任务总数**: {total_tasks}
**总成本**: ${total_cost}
**成本效率**: 比行业基准优 {percentage}%

---

## 执行摘要

{summary_paragraph}

**关键数字**:
- 总任务数: {total_tasks} (环比 {change}%)
- 总体成功率: {success_rate}% (目标: >95%)
- 平均用户评分: {avg_rating} (目标: >4.5)
- 总成本: ${total_cost} (预算: ${budget})
- 成本效率: 优于目标 {percentage}%

---

## 关键成果

### 🎯 目标达成情况
| 目标 | 目标值 | 实际值 | 达成率 | 状态 |
|------|--------|--------|--------|------|
| 成功率 | >95% | {rate}% | {achievement}% | {status} |
| 用户满意度 | >4.5 | {rating} | {achievement}% | {status} |
| 平均Token | <15000 | {tokens} | {achievement}% | {status} |
| 总成本 | <${budget} | ${cost} | {achievement}% | {status} |

### 🏆 重要里程碑
1. {milestone_1}
2. {milestone_2}
3. {milestone_3}

---

## 月度趋势

### 各周对比
| 周 | 任务数 | 成功率 | 平均Token | 总成本 | 评分 |
|----|--------|--------|-----------|--------|------|
| W1 | {count} | {rate}% | {tokens} | ${cost} | {rating} |
| W2 | {count} | {rate}% | {tokens} | ${cost} | {rating} |
| W3 | {count} | {rate}% | {tokens} | ${cost} | {rating} |
| W4 | {count} | {rate}% | {tokens} | ${cost} | {rating} |
| W5 | {count} | {rate}% | {tokens} | ${cost} | {rating} |

**趋势分析**:
{trend_analysis}

---

## Agent排行榜

### 综合表现 TOP 3 (基于成功率、效率、质量、成本)
1. 🥇 **{agent_name}** - 综合评分: {score}/100
   - 成功率: {rate}% | Token效率: {efficiency} | 用户评分: {rating}

2. 🥈 **{agent_name}** - 综合评分: {score}/100
   - 成功率: {rate}% | Token效率: {efficiency} | 用户评分: {rating}

3. 🥉 **{agent_name}** - 综合评分: {score}/100
   - 成功率: {rate}% | Token效率: {efficiency} | 用户评分: {rating}

### 单项冠军
- 🎯 **最高成功率**: {agent_name} ({rate}%)
- ⚡ **最快速度**: {agent_name} (平均 {time}s)
- 💰 **最佳成本效率**: {agent_name} (${cost}/任务)
- ⭐ **最高用户满意度**: {agent_name} ({rating}分)

### 需要改进
1. **{agent_name}** - {issue}
   - 当前状态: {current_status}
   - 改进目标: {target}
   - 计划措施: {action}

---

## 优化成果

### 本月实施的优化
| 优化项 | 实施日期 | 目标 | 实际效果 | 状态 |
|--------|----------|------|----------|------|
| {optimization} | {date} | {target} | {actual} | {status} |

### 累计收益
- **成本节省**: ${savings} (比优化前降低 {percentage}%)
- **效率提升**: 平均执行时间缩短 {percentage}%
- **质量改善**: 成功率提升 {percentage} 个百分点

### 优化案例

#### 案例1: {title}
- **问题**: {problem}
- **方案**: {solution}
- **效果**: {result}
- **可复用性**: {reusability}

[更多案例...]

---

## 成本深度分析

### 成本结构
```
架构设计 (architect): ${cost} ({percentage}%) ███████████████
代码审查 (code-reviewer): ${cost} ({percentage}%) ████████████
调试修复 (debugger): ${cost} ({percentage}%) ██████████
安全审计 (security-analyst): ${cost} ({percentage}%) ████████
数据分析 (data-scientist): ${cost} ({percentage}%) ██████
编排调度 (orchestrator): ${cost} ({percentage}%) ████
```

### 成本优化机会
1. {opportunity_1}: 潜在节省 ${savings}
2. {opportunity_2}: 潜在节省 ${savings}

---

## 下月目标

### 性能目标
- 成功率: 提升至 {target}%
- 平均Token: 降低至 {target}
- 用户满意度: 达到 {target}分
- 总成本: 控制在 ${target} 以内

### 优化计划
1. **{plan_1}**
   - 预期收益: {benefit}
   - 责任人: {owner}
   - 完成时间: {deadline}

2. **{plan_2}**
   - 预期收益: {benefit}
   - 责任人: {owner}
   - 完成时间: {deadline}

### 新功能规划
1. {feature_1}
2. {feature_2}

---

## 战略建议

### 短期建议 (1-3个月)
1. {recommendation_1}
2. {recommendation_2}

### 中期建议 (3-6个月)
1. {recommendation_1}
2. {recommendation_2}

### 长期建议 (6-12个月)
1. {recommendation_1}
2. {recommendation_2}

---

## 风险与挑战

### 识别的风险
1. **{risk_1}**
   - 影响: {impact}
   - 缓解措施: {mitigation}

### 面临的挑战
1. **{challenge_1}**
   - 解决方案: {solution}

---

## 附录

### 完整数据表
[详细的月度数据表格]

### 图表
[性能趋势图、成本分布图等]

### 技术指标
[详细的技术性能指标]

---

**报告生成时间**: {timestamp}
**数据来源**: memory/agent-performance.md
**生成者**: performance-monitor Agent
**审核者**: auto-optimizer Agent
```

---

## 使用说明

### 1. 自动生成
- 日报: 每天23:00自动生成 (任务数≥10)
- 周报: 每周一09:00自动生成
- 月报: 每月1号09:00自动生成

### 2. 手动生成
```bash
/performance-report daily    # 生成日报
/performance-report weekly   # 生成周报
/performance-report monthly  # 生成月报
```

### 3. 定制报告
- 可指定日期范围
- 可指定特定Agent
- 可定制报告格式

---

**版本**: 1.0
**最后更新**: 2026-01-16
**维护者**: performance-monitor Agent

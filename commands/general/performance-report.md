# 生成性能报告

调用 performance-monitor Agent 生成指定时期的性能分析报告。

## 用法

```bash
/performance-report [period] [agent_name]
```

## 参数

- **period** (可选): 报告周期
  - `daily` - 日报 (默认: 今日)
  - `weekly` - 周报 (默认: 本周)
  - `monthly` - 月报 (默认: 本月)
  - `YYYY-MM-DD` - 指定日期的报告

- **agent_name** (可选): 特定Agent名称
  - 不指定则生成所有Agent的报告
  - 例如: `architect`, `code-reviewer`, `debugger`

## 示例

### 生成今日报告
```bash
/performance-report daily
```

### 生成本周报告
```bash
/performance-report weekly
```

### 生成architect的周报
```bash
/performance-report weekly architect
```

### 生成指定日期的报告
```bash
/performance-report 2026-01-15
```

## 输出

报告将保存至 `memory/performance-reports/` 目录:
- 日报: `daily-YYYY-MM-DD.md`
- 周报: `weekly-YYYY-WXX.md`
- 月报: `monthly-YYYY-MM.md`

## 报告内容

### 日报包含
- 当日任务数和总体成功率
- 各Agent关键指标
- 异常事件列表
- 趋势提示

### 周报包含
- 周任务统计和总成本
- 成功率和Token消耗趋势
- 各Agent详细表现分析
- 策略效果统计
- 本周亮点和问题
- 下周优化计划

### 月报包含
- 月度执行摘要
- 关键成果总结
- 各周对比
- Agent排行榜
- 优化成果记录
- 下月目标
- 战略建议

## 相关命令

- `/optimize-system` - 触发系统优化分析
- `/agents performance-monitor` - 直接调用性能监控Agent

## 注意事项

- 日报需要至少10个任务才会生成
- 周报在每周一 09:00 自动生成
- 月报在每月1号 09:00 自动生成
- 首次使用需要积累性能数据

## 技术细节

此命令将调用 `performance-monitor` Agent 执行以下操作:
1. 从 `memory/agent-performance.md` 读取性能数据
2. 计算指定周期的统计指标
3. 生成趋势分析和洞察
4. 输出格式化的Markdown报告
5. 保存至指定目录

---

**维护者**: performance-monitor Agent
**最后更新**: 2026-01-16

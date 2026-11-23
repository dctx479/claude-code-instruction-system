# Memory 文件索引

> 8 个知识文件，各司其职。写入前先查索引，找准归属，避免重复。

---

## 文件清单

| 文件 | 条目类型 | 写入时机 | 当前规模 |
|------|---------|---------|---------|
| [best-practices.md](best-practices.md) | 策展型 BP 条目 | 经验验证≥3次后晋升 | 57 个 BP（BP-001～BP-057；2026-11-21 核对） |
| [lessons-learned.md](lessons-learned.md) | 任务经验（UNVERIFIED） | 任务完成复盘时 | 持续增长 |
| [error-patterns.md](error-patterns.md) | 错误模式和修复 | 发现新错误模式时 | 持续增长 |
| [agent-performance.md](agent-performance.md) | Agent 性能数据 | 性能监控报告后 | 定期更新 |
| [optimization-history.md](optimization-history.md) | 优化操作历史 | 系统配置变更后 | 按时间序 |
| [knowledge-strategy.md](knowledge-strategy.md) | 知识管理策略 | 策略调整时 | 相对稳定 |
| [active-worktrees.md](active-worktrees.md) | 活跃 Worktree 状态 | Worktree 创建/关闭时 | 动态维护 |
| [performance-reports/TEMPLATE.md](performance-reports/TEMPLATE.md) | 性能报告模板 | 报告生成参考 | 静态模板 |

Detailed write formats and historical audit guidance: [../docs/MEMORY-INDEX-DETAILS.md](../docs/MEMORY-INDEX-DETAILS.md).

Historical records are evidence only; do not delete or relabel them based on age. Search the target file before adding an entry. New decisions include a date, evidence pointer and active/superseded status.

## 可执行检索与策展索引

- `python scripts/taiyi-tool.py search <查询>` 返回最多 3 个有来源片段；索引在 `memory/.cache/`，内容变化自动重建。
- [curated/](curated/) 是 10 条当前仓库来源的证据索引；不替换上表中的历史记忆。新结构化记录使用 JSON frontmatter 或相邻 `.evidence.json` 台账，先查重再验证。
- [playbooks/REGISTRY.json](playbooks/REGISTRY.json) 注册 3 个版本化流程；latest 由 JSON 选择，成功率来自真实反馈。
- [failures/REGISTRY.json](failures/REGISTRY.json) 是错误特征和处理建议，不自动阻断任务。
- 格式与验证状态见 [证据指南](../docs/EVIDENCE-GUIDE.md)；运行时不会把来源存在写成测试通过。

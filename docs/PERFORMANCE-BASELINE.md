# 改进运行时本地基准

测量日期：2026-11-23。Windows，仓库既有 validation-venv。命令：

```bash
python scripts/benchmark.py --output .claude-tmp/improvement-benchmark.json
python scripts/test-decision-scenarios.py
```

以下为当前工作树的一次实测；模块内耗时不包括 Python 进程启动或模型推理。

| 操作 | 样本数 | 中位数 ms | p95 ms |
|---|---:|---:|---:|
| 机械路由 | 1000 | 0.018 | 0.024 |
| Playbook 匹配 | 100 | 0.301 | 0.524 |
| 证据引用验证 | 100 | 5.607 | 7.158 |
| 记忆检索，含内容指纹检查 | 100 | 18.423 | 21.903 |

冷启动索引 25 个 Markdown：113.617ms。10 条标签路由 fixture：10/10；这不是真实 Agent 路由准确率。

合成日志 fixture：29,000 → 760 字节，减少 97.38%。50 个合成源码文件的行数聚合：55,000 → 3,608 字节，减少 93.44%。这是有损输出聚合；要求任务先明确只需计数/摘要，必要时补读原始来源。

没有真实 token 计数，因此 token 节省率未验证；也未验证会话延长、重复任务耗时改善、三个外部项目或分支覆盖率。CLI/Hook 的进程启动、磁盘争用和新场景成本另需采样，不用此表保证所有调用 <100ms。

实测 token 数据用 `scripts/measure-token-savings.py` 的 JSONL 接口计算，必须包含完整任务成本和一致的任务结果；字节减少不能换算成固定 token 比例。

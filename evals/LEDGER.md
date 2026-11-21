# 评估台账（只追加）

| 日期 | 层级 | 变更/版本 | 证据 | 结果/决定 |
|---|---|---|---|---|
| 2026-11-21 | T1 | vNext 结构、profile、Hook、检查点 | docs/audits/evidence/vnext-checks-2026-11-21.json | 本地命令通过，60 项回归；保留 |
| 2026-11-21 | T2a | 自动描述词重叠，10 个描述 | scripts/eval-skills.py | 0 hints；只作静态提示，不是路由分数 |
| 2026-11-21 | T2b | CLI 2.1.330，core，15 案例，内置 Skill 参与竞争 | docs/audits/evidence/vnext-routing-2026-11-21.json | 11 PASS / 2 错误或遗漏 / 2 INCOMPLETE；保留失败，不继续叠加自然语言正则 |
| 2026-11-21 | 权限 | CLI 2.1.330，隔离候选模板 | docs/audits/evidence/vnext-guardrails-2026-11-21.json | ask/deny 无害命令拒绝观察成功；交互、bypass、PowerShell 等未全验 |
| 2026-11-21 | T3 | workflow 行为目录 | evals/behavior/workflows.json | NOT_RUN；不作为发布通过证据 |
| 2026-11-21 | T1/跨平台 | checkpoint 根路径规范化、shell 边界回归；CLI runner 失败注释 | docs/audits/evidence/vnext-ci-local-2026-11-21.json；vnext-ci-2026-11-21.json | 本地 61 项通过；46f6d3d 远端 6/6 success，保留首轮 Windows 失败 |

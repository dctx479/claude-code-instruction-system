# 评估台账（只追加）

| 日期 | 层级 | 变更/版本 | 证据 | 结果/决定 |
|---|---|---|---|---|
| 2026-11-21 | T1 | vNext 结构、profile、Hook、检查点 | docs/audits/evidence/vnext-checks-2026-11-21.json | 本地命令通过，60 项回归；保留 |
| 2026-11-21 | T2a | 自动描述词重叠，10 个描述 | scripts/eval-skills.py | 0 hints；只作静态提示，不是路由分数 |
| 2026-11-21 | T2b | CLI 2.1.330，core，15 案例，内置 Skill 参与竞争 | docs/audits/evidence/vnext-routing-2026-11-21.json | 11 PASS / 2 错误或遗漏 / 2 INCOMPLETE；保留失败，不继续叠加自然语言正则 |
| 2026-11-21 | 权限 | CLI 2.1.330，隔离候选模板 | docs/audits/evidence/vnext-guardrails-2026-11-21.json | ask/deny 无害命令拒绝观察成功；交互、bypass、PowerShell 等未全验 |
| 2026-11-21 | T3 | workflow 行为目录 | evals/behavior/workflows.json | NOT_RUN；不作为发布通过证据 |
| 2026-11-21 | T1/跨平台 | checkpoint 根路径规范化、shell 边界回归；CLI runner 失败注释 | docs/audits/evidence/vnext-ci-local-2026-11-21.json；vnext-ci-2026-11-21.json | 本地 61 项通过；46f6d3d 远端 6/6 success，保留首轮 Windows 失败 |
| 2026-11-22 | T3 | CLI 2.1.330，19 个 core-workflow 真实隔离产物场景 | docs/audits/evidence/vnext-behavior-summary-2026-11-22.json | 19/19 场景通过；保留初始失败、CLI 权限阻塞与修正后的复测，不代表任意项目保证 |
| 2026-11-22 | T2b | 自动描述边界、真实 CSV、Read/Skill 与合理预算 | docs/audits/evidence/vnext-routing-2026-11-22.json | 15/15；内置 Skill 仍参与竞争，原 11/15 基线保留 |
| 2026-11-22 | 独立评审 | 检查点仓库相对路径、深 JSON 与 Windows/schema 边界 | docs/audits/evidence/vnext-checkpoint-review-initial-2026-11-22.json；vnext-checkpoint-review-final-2026-11-22.json | FAIL → 回归先红后绿 → 独立复评 PASS |
| 2026-11-22 | 权限/部署 | 无害替身 16 类、真实交互拒绝、core 全局迁移与最小调用记录 | docs/audits/evidence/vnext-permissions-summary-2026-11-22.json；vnext-global-deployment-2026-11-22.json | 已枚举边界通过，全局启用，四周观察到期 2026-12-20；不是 OS 沙箱 |

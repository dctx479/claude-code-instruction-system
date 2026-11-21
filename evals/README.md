# 评估入口

- T1：规则/Skill/命令/profile/文档事实检查，在 CI 运行。
- T2a：`python scripts/eval-skills.py` 输出描述词重叠，仅作 WARNING，不代表模型路由命中率。
- T2b：`routing/core.json` 为 4 个自动 core Skill 各提供 3 个正例；其他 owner 的案例为反例。显式工作流使用 `/命令`，不考核自动触发。
- T3：`behavior/workflows.json` 的行为契约，使用隔离 fixture 运行并检查实际工具记录。未执行不得标 PASS。

真实模型评估需在临时配置目录安装选定 profile，禁用通知和原有 Hook，不读真实项目数据。
记录 CLI 版本、profile、案例、实际 Skill 工具调用、退出码及费用；只看模型自述不算证据。
API key 只经环境传给进程，不写入评估产物。真实模型评估不放 CI，也不把第三方阈值搬到本仓库。

`LEDGER.md` 只追加，区分代码回归、真实路由和工作流行为评估。

真实路由入口：`python scripts/eval-routing.py --run --output .claude-tmp/routing.json`。每案例配置 $0.10 CLI 预算，最后一次请求可能略超出；保存实际费用与未完成状态。该工具只开放 Skill，保留 CLI 自带 Skill 的竞争，不代表完整工作流行为测试。

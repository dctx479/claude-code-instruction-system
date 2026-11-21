# 评估入口

- T1：规则/Skill/命令/profile/文档事实检查，在 CI 运行。
- T2a：`python scripts/eval-skills.py` 输出描述词重叠，仅作 WARNING，不代表模型路由命中率。
- T2b：`routing/core.json` 为 4 个自动 core Skill 各提供 3 个正例；其他 owner 的案例为反例。显式工作流使用 `/命令`，不考核自动触发。
- T3：`behavior/workflows.json` 的行为契约，使用隔离 fixture 运行并检查实际工具记录。未执行不得标 PASS。

真实模型评估需在临时配置目录安装选定 profile，禁用通知和原有 Hook，不读真实项目数据。
记录 CLI 版本、profile、案例、实际 Skill 工具调用、退出码及费用；只看模型自述不算证据。
API key 只经环境传给进程，不写入评估产物。真实模型评估不放 CI，也不把第三方阈值搬到本仓库。

`LEDGER.md` 只追加，区分代码回归、真实路由和工作流行为评估。

真实路由入口：`python scripts/eval-routing.py --run --output .claude-tmp/routing.json`。每案例配置 $0.25 CLI 预算，最后一次请求可能略超出；开放 Read/Skill 并提供小型 CSV 实物，保留 CLI 自带 Skill 的竞争。保存实际费用与未完成状态，不代表完整工作流行为测试。

真实行为入口：`python scripts/eval-workflows.py --run --output .claude-tmp/behavior.json`，`--skills` 可选择复测。每个案例有独立安装与临时 git 仓库；检查真实文件、哈希、测试结果和工具调用，而非只看总结。skill-creator 的项目 Skill 写入在该 CLI 会触发受保护路径确认，因此此项仅在一次性 fixture 中使用显式 bypass，其余案例保持 default；这不放宽真实全局设置。
`python scripts/probe-permission-boundaries.py --run --output .claude-tmp/permissions.json` 使用无害替身验证权限；`--interactive` 查看真实确认并选择拒绝。PowerShell 工具仅在测试进程中显式启用。禁用 bypass 可能降级为普通模式，按 ask 是否仍被拒绝判定，不用启动退出码误判。

`python scripts/probe-discovery.py --profile core,ctf` 在仓库外查看 `/skills` 和 `/context`；`--global-install` 复制真实发现资产到临时配置，只读检查，不复制凭据文件或个人记忆。

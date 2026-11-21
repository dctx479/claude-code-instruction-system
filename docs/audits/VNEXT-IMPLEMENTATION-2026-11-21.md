# vNext 实施台账

日期：2026-11-21 · 整体 RISK-HIGH，按主题可回滚。
依据：[原规格](../../specs/SPEC-taiyi-vnext.md)、[执行差量](../../specs/SPEC-taiyi-vnext--execution.md)、[权限边界](../../specs/SPEC-vnext-guardrails.md)。

## 已落地

| 原问题 | 实施结果 | 验证/限制 |
|---|---|---|
| P0 分叉/未提交 | fetch 后再次确认两个树相同；原 HEAD 留 `backup/pre-vnext-20261121`，soft reset 对齐；原改动分为 6 个主题提交 | 无强推、未丢弃工作区；后续修复另行提交 |
| P1 CI 缺项 | Ubuntu/Windows × Python 3.10/3.11/3.12，补 intent、配置、3 个 JSON、临时目标 dry-run 和新生成检查 | 远端结果单独追加，不能用本地结果替代 |
| P1 旧引用/入口预算 | 活动规范/文档检查旧 CLAUDE 章节引用；内联路径与 Markdown 链接的 INDEX 预算 150 行 | 坏样例先失败后通过；历史 reports/archive/hud 不改写 |
| A1 自动改写 | lint-feedback 显式可选；只用本地工具，传 no-fix；不跑 npm、npx、Black/Prettier | 参数与文件不变回归；没有声称任意第三方 linter 都无副作用 |
| A2 diff 备份 | session-backup 默认关闭，自有补丁保留 14 天/50 MiB；不再自动发结束通知 | 期限/容量/非自有文件测试；安装备份只留 5 份尚未做，避免批量删历史 |
| A3 权限/命令 | opt-in 权限合并，禁用 bypass；补充检查 rm 参数变体、git -C force push，不回显命令 | 真实 CLI 无害 ask/deny 拒绝已观察；不是 shell 沙箱，边界未全验 |
| A4 端口开销 | 容器命令才启动独立端口 helper | 普通命令不调用 helper 的回归通过；无性能百分比主张 |
| A5 空 PreCompact | 退出默认事件注册 | 默认安装设置测试 |
| A6 路由误判 | 自然语言不输出建议；只识别开头 @agent 与 /命令；普通轮次清空旧建议 | 原角色文本全部变成 abstain 回归，显式角色仍覆盖；真实误判加入 fixture |
| A7 双安装入口 | cc-patcher 转交唯一安装器；旧配置明确改为 .example | 不再单独写 settings；保留主题功能 |
| B1/B2/B5 加载 | 官方字段审计、顶层调用控制；core 与 7 个领域包；God 与栈专用 Agent 不默认安装 | profile 完整性/安装/幂等验证；旧目标残留只报告，不删除 |
| B3 命令描述 | 命令补 description，设为显式调用 | 缺描述/调用策略由事实检查阻止 |
| B4 安装面 | Hook 文件和运行依赖使用显式白名单；工作流工具随 commands 安装 | 临时安装与已安装 Hook 烟测通过；个人混合 Hook 组保留测试 |
| B6 索引/长 Skill | Agent 索引由 frontmatter 生成，42 行；长 Skill 条件细节移入 references | 索引漂移检查；保留正文、资源与引用，不按过期删除 |
| C1 嵌套审计 Skill | Java/PHP 增加顶层入口，嵌套定义仍作路径参考 | 59 个顶层 Skill 审计与可选包安装通过；交互 /skills 仍待人工核对 |
| C2 假闭环风险 | 只标注原始数据缺口/示例用途，监控与优化 Agent 不得据示例生成趋势 | 未伪造历史状态；usage 次数不能替代质量/耗时/成本 |
| C3 God Committee | 作为 multi-model 可选包保留 | 无删除，默认 core 不装 |
| D 未引用模块/重复规范 | 保留；归档重新开启条件写入 out-of-scope | 未引用不等于没用；规范合并来源仍待逐项决定 |
| D5 数字同步 | profile 和生成能力表单一来源，检查重复/漏配；入口去掉失效数量 | 不宣称检查了所有历史报告数字 |
| E1 评估 | 离线重叠检查、真实路由 fixture/runner、行为契约目录和追加台账 | 真实路由有失败/未完成，见下文；行为目录不等于已执行 |
| E2/E5 检查优先 | evolve 先分流；新增规则仍需两次独立证据 | 坏样例测试；不阻止一次已复现缺陷的修复 |
| E3 交接 | worktree 本地原子检查点、工具计算哈希、0/2/1 区分有效/缺失/损坏 | stdin/stdout、文件变化、损坏、越界与 linked-worktree 测试 |
| E4 知识 | 日期/证据/active-superseded 的增量约定，单份决策日志与 out-of-scope | 历史案例保留，不建 wiki |
| E6 debug | 修改前要求稳定失败命令，修复后同一命令转绿 | 工作流契约已更新；不声称已执行全部模型行为评估 |
| E7/E8 评审/spec | 评审输入隔离、最多 3 轮；批准 spec 用差量扩展 | 实际独立工作流评审尚未跑；不标全流程 PASS |

## 本地验证

[命令与输出](evidence/vnext-checks-2026-11-21.json)：规则审计 0 findings，Skill 59/59；索引/命令/profile/事实检查通过；单元测试 60 项通过；intent 脚本、配置检查（0 errors/0 warnings）、3 个 JSON、临时 dry-run、实际安装和安装副本烟测通过。
`git diff --check` 无格式错误。未安装新的运行时依赖。

静态描述基线来自 `c9473b8`：57 个 Skill / 7833 字符；新 core 23 个 Skill、20 个 Agent，自动 Skill 描述为 672 字符。Agent 索引 788 → 42 行。
这些是文件统计；没有声称 token 节省百分比或完成交互 `/context` 实测。

## 真实 CLI 证据

[权限探测](evidence/vnext-guardrails-2026-11-21.json)：CLI 2.1.330，临时配置，无害 printf 命令，在 allow Bash 前提下观察 ask/deny 拒绝。ask 使用无头自动拒绝，没有测试交互弹窗；模板禁用 bypass，不宣称 bypass 下 ask 有效。

[模型路由基线](evidence/vnext-routing-2026-11-21.json)：15 案例，11 项通过、2 项误路由/漏调用、2 项预算/轮次耗尽而未完成。
其中 dashboard 被选到 CLI 自带 dataviz；sales-table 案例没有调用 Skill。另两项首个调用虽符合 owner，但运行未完成，保留 INCOMPLETE。CLI 自带 Skill 仍参与竞争。
实际总费用约 $0.8194；这是路由基线，不是端到端行为验证，也不把第三方 95% 阈值搬来当本项目门禁。

## 真实小切片与未完成项

交接需求使用原 vNext 规格中的行为定义，并补 [检查点规格](../../specs/SPEC-worktree-checkpoint.md)、[本地票](../../issues/worktree-checkpoint.csv)、真实工具/回归结果。
依赖图、缺失/损坏/文件变化/worktree 隔离已实测；独立评审字段保持 TODO。未将这个示范写成“完整工作流已全绿”。

- 个人全局 settings 未合并新权限模板；新的持续 usage/备份/通知未启用。
- 未执行未知用途模块和历史报告的归档，未删除外部克隆。
- `/context`、交互 `/skills`、交互权限确认、PowerShell/复合命令与完整绕过边界仍待验证。
- 调用记录 4 周观察尚未开始；不能提供使用排名或据此删除能力。
- T3 全部 workflow 行为评估尚未执行。已有目录/契约/台账不会冒充实测。

## 远端 CI

首轮 [44920596287](https://github.com/dctx479/claude-code-instruction-system/actions/runs/44920596287)：Ubuntu 三组通过，Windows 单元测试失败，其余 Windows 被 fail-fast 取消。
补充公开失败注释后，确认 Windows TEMP 短路径别名使 checkpoint 根目录与已规范化文件路径比较不一致。新增回归先红后绿，并统一规范化根目录；同时补测相邻 shell 分隔符与 echo/后续命令误拦问题。

修复提交 `46f6d3d` 的 [远端运行 44921111015](https://github.com/dctx479/claude-code-instruction-system/actions/runs/44921111015) **6/6 success**：Ubuntu/Windows × Python 3.10/3.11/3.12，含全部检查和安装 dry-run。
[远端证据](evidence/vnext-ci-2026-11-21.json) 与 [修复后本地 61 项回归](evidence/vnext-ci-local-2026-11-21.json) 单独保存，早期失败与 60 项基线没有覆盖或改写。

CI 保留完整矩阵（fail-fast=false），失败输出 Actions 注释。远端还暴露旧 Action 的 Node 20 告警，已使用官方发布的 [checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1) 和 [setup-python v7.1.0](https://github.com/actions/setup-python/releases/tag/v7.1.0) 复跑通过。
本节后的证据文档提交不改变上述已验证实现；对应新运行状态以最终交付链接为准。

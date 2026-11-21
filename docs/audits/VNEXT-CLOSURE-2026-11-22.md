# vNext 修复收尾与全局部署

日期：2026-11-22 · 承接 [前轮台账](VNEXT-IMPLEMENTATION-2026-11-21.md) 与 [收尾规格](../../specs/SPEC-taiyi-vnext--closure.md)。
用户明确授权全局同步并启用本机调用记录；提交和正常推送沿用已有授权。

## 修复闭环

| 遗留 | 本轮处理与证据 |
|---|---|
| 真正的 T3 行为验证缺失 | 新增隔离真实 CLI runner，19 个 core-workflow 各有一个产物场景，检查真实文件、哈希、退出码和工具轨迹；[最终汇总](evidence/vnext-behavior-summary-2026-11-22.json) 19/19，保留原失败/阻塞记录。不是任意项目上的通用正确性保证。 |
| 旧 SDD/复盘/拆票/Skill 创建规则冲突 | SDD 与 Light 统一本地 specs 和风险分档，不再强制 mydocs、章节数量、行数阈值或重复审批；reflection 不凑经验数量；task-decompose 以纵向切片和本地依赖为准；skill-creator 按实际项目生成 verify 并执行。 |
| observability 要求记录私密推理 | 改为可核验的执行证据和简明决策摘要，不索取或保存私密思维、原始提示词、凭据，不据模板推导质量。原行为测试被服务拒绝，修正后真实场景通过，未抹掉失败。 |
| 路由 11/15，样例缺真实数据、预算不足 | 补 CSV 实物、Read 工具和合理轮次，描述明确 UI 布局与数据图表边界；[复测](evidence/vnext-routing-2026-11-22.json) 15/15，仍有内置 Skill 竞争，不将该有限集分数当生产准确率。 |
| 检查点独立评审未做 | 第一轮[评审 FAIL](evidence/vnext-checkpoint-review-initial-2026-11-22.json)：子目录误解析路径、深 JSON 异常、Windows 设备名和松 schema。回归先红后绿，修复后[复评 PASS](evidence/vnext-checkpoint-review-final-2026-11-22.json)，未提供实现者结论。 |
| 权限边界只测 headless printf | [16 类结果](evidence/vnext-permissions-summary-2026-11-22.json)：普通、push、git -C（含无尾随参数）、compound、force、rm 参数、reset、checkout、clean、PowerShell 和 bypass 降级；实际 PTY 看到确认弹窗并选 No。所有危险命令用无害替身，未执行真实删除/推送。 |
| PowerShell/禁用 bypass 探测误判 | PowerShell 工具需在测试进程显式启用；禁用 bypass 会降级，不一定启动失败。保留初始失败和复测，按实际拒绝证据判断。 |
| 安装备份无限增长 | 新快照带 owner/completed/hash 清单，默认留最近 5 个完整未改写托管快照。仅过期精确已验证文件；旧无标记、改写、未知或链接内容不删。保留期/回滚/未知文件测试通过。 |
| 旧全量安装无迁移工具 | 增加 plan/apply/restore；只归档与当前或指定历史托管源码一致的 profile 外能力。个人改写/链接保留并 WARNING；计划后变更与恢复冲突均拒绝。实际迁移 52 项，可恢复，项目源码不动。 |
| 只记工具漏掉显式 slash | usage 同时记录注册命令/Skill 的 slash 展开，仅保存 ts/tool/name，内置 /context 和消息中间文本不计。真实新会话 /debug 产生一条记录，无参数/提示词；[实测](evidence/vnext-global-usage-2026-11-22.json)。 |
| 部分 Agent YAML 已坏却未被审计 | requirements-analyst、tech-mentor、senior-code-architect、vitest-tester 的 description 含未引用冒号；修正引号，事实检查现真正解析全部 Agent frontmatter，增加坏样例测试。 |
| /skills、/context 未检查 | 仓库外隔离交互确认 java-audit/php-audit 可见且 user-only；/context 仅列 4 个自动用户 Skill，领域包没有进入自动描述。快照见[部署记录](evidence/vnext-global-deployment-2026-11-22.json)。 |

行为验证中的 skill-creator 因 CLI 受保护路径提示，在 default/acceptEdits 下阻止写入，不属于 Skill 假成功；最终只在一次性测试配置中使用已授权 bypass 完成创建与真实验证。真实全局禁用 bypass，并未因此放宽。
plan-review 初测返回 CHANGES_REQUIRED 和真实阻塞发现，旧 harness 只接受 FAIL/BLOCKED/INCOMPLETE；修正等价结果判定并真实复测，不改案例迎合输出。

## 全局部署与回滚

[部署记录](evidence/vnext-global-deployment-2026-11-22.json) 保存发现清单、迁移 manifest 与校验。
原 57 个全局 Skill 的自动描述为 7833 字符；当前 core 23 个 Skill、20 个有效 Agent，自动描述 1083 字符。描述为了纠正真实路由边界有所增加，仍远低于旧全量；不把字符换算成未经测量的 token 节省率。
实际设置保留 env 与个人配置，新增权限与 usage Hook；自动修复、备份、通知仍关闭。新会话才加载更新。

回滚先恢复 `~/.claude/backups/taiyi-install-20261122-004533-1795279533314538400/settings.json`，再按需要恢复对应托管文件；用部署记录里的 manifest 执行 `python scripts/migrate-install.py --restore <manifest>`。冲突时停止，不覆盖当前个人文件；重启会话。

## 有意保留与日历观察

未知用途模块、历史报告、外部克隆与内容不同的规范不删除，也不伪称已完成逐项内容合并。它们不属于默认能力加载路径；保留的决策见 `docs/out-of-scope/automatic-archive.md`。God Committee 在可选包中保留。没有用途证据的归档不是修复前置条件。
使用记录从 2026-11-22 起真实启用，四周复核日 **2026-12-20**。届时运行 `python scripts/usage-report.py --days 28`。当前不能声称已经观察四周，不能据缺历史数据删除 Skill。
权限仅覆盖已枚举命令形式，不是 OS 沙箱，任意解释器/编码绕过的绝对保证不属于本次可实现承诺。

## 验证

本轮[本地证据](evidence/vnext-closure-checks-2026-11-22.json)：74 项测试通过；规则 0 findings、Skill 59/59、索引/profile/Agent YAML/配置检查通过；全局真实安装与已安装 Hook 烟测通过，profile 无残留。远端矩阵结果在最终交付中列出；原始证据保留在本目录 evidence，未执行的项目不标通过。

# 当前 Statusline 实现与检查结果

2026-11-23，RISK-MEDIUM。实际默认入口为 `python -S "$HOME/.claude/statusline/hud.py" render`，保留 `hud.sh` 作为兼容 CLI。独立 Rust 工具和 `statusline/statusline.py` 不在当前安装调用链中。

## 已修复的问题

| 问题 | 当前行为 |
|---|---|
| 合法 JSON 有空格时整行空白 | JSON 一次解析，紧凑/格式化/Unicode 输入一致 |
| 按 cost>0 推断 Stop 事件 | 默认显示已有信息；零费用也显示。可显式设 display.hide_zero_cost=true 保留旧行为 |
| 固定 200K 窗口、从 transcript 正则抓 token | 优先使用 context_window.used_percentage/总计；缺少百分比时按 current_usage 与实际窗口大小计算 |
| 缺少指标却显示 0 或默认 orchestrator | 指标用 ?，无匹配 Agent/命令不显示，不制造数据 |
| enabled=false、主题和宽度不生效 | 尊重布尔值与优先级，按 COLUMNS 预留 4 列，按 Unicode 显示列宽裁剪 |
| 深蓝背景上模型名称不可辨认 | 模型默认亮白加粗；空白名称回退实际 id，窄屏先让项目/Git 标签腾出空间 |
| 跨项目复用 Git/project 缓存 | 项目名即时计算；Git 缓存按规范化 cwd 的 SHA-256 分区，TTL/缓存开关生效 |
| 读取别的会话 Agent/Ralph | Agent/命令须匹配会话和目录；Agent Hook 附来源标识。Ralph 优先项目状态，带 session_id 时须匹配，全局还须匹配项目 |
| 多次启动 jq/grep/git，错误静默降级 | 标准库单进程，Git 单次 porcelain，故障 WARNING；禁用/隐藏模块不采集 |
| cache-clear 批量删除共享缓存 | 仅逐项删除自有标识的 HUD JSON，保留其他文件、旧缓存和链接 |

配置位置为 `~/.claude/hud-config.json`，或 HUD_CONFIG_FILE 指定路径。安装器保留已有个人配置。ENV 的 HUD_THEME/HUD_WIDTH 优先；NO_COLOR 可禁用 ANSI。模型默认高对比亮白加粗，可用 modules.model.high_contrast=false 恢复模型家族配色。窄屏按模块优先级选择，较低优先级可能不显示，不能据此认为数据缺失。CTX 是当前上下文窗口使用百分比，包含对话、代码与工具结果等当前工作信息。

performance 模块只显示显式提供的 response_time_ms/success_rate，不把 API 累计时间或示例值当作实时指标。旧 project_ttl/performance_ttl 配置保留兼容，但廉价项目名与输入指标无需持久化缓存；当前持久化缓存仅用于 Git。未提供或未实现的趋势数据不声称已测得。

## 验证

- `python -m unittest discover -s tests -p "test_statusline.py" -v`：截图反馈修复后 27 项通过，新增模型亮白加粗、空白名称回退与窄屏保护验证。
- `python scripts/ci-tests.py`：推送前最终全量 138 项全部通过，无跳过，包含 statusline 的 27 项回归。
- `bash -n .claude/statusline/hud.sh`、规则审计、能力事实检查通过。
- 全局同步前 dry-run：新增 hud.py、更新 hud.sh；保留个人 hud-config。只更新与仓库旧版一致的托管 HUD 与 Agent 状态脚本，既有其他设置不变。
- `verify-global-install.py --components statusline,hooks,usage,context-optimization --smoke-hook`：25 个托管文件对齐，临时 HOME 的已安装 Hook 烟测通过。

源接口：[Claude Code 官方 statusline 文档](https://code.claude.com/docs/en/statusline)，本轮通过 HTTPS 获取。官方说明 statusline 在启动、消息和 compact 等情况下更新，费用并非事件类型；输出用于 UI，不消耗 API token。

## 本机性能

Windows，20 次进程调用，使用既有验证 Python，缓存热样本 19 次。输入为明确标注的会话 fixture，Git 在当前仓库读取；不包含模型请求。

| 入口 | 冷启动 ms | 热中位数 ms | 热 p95 ms |
|---|---:|---:|---:|
| 默认 Python -S 入口 | 147.840 | 67.269 | 75.776 |
| 兼容 Bash 入口 | 155.844 | 100.439 | 110.310 |

旧版完整 Bash 渲染约 1,368ms。100ms 热调用目标由默认入口满足；冷启动与兼容 Bash p95 未满足。不能用内部采集预算保证所有机器、所有冷调用或 Claude UI 调度时间低于 100ms；官方更新另有 300ms debounce。

## 全局核对与回滚

已核对真实 `~/.claude/settings.json` 默认入口并完成安装烟测：格式化/紧凑 JSON、零费用、85% 上下文、中文路径与匹配 Agent 均显示正确。个人 HUD 配置、权限和其他 Hook 保留。旧匿名 Agent 状态会省略，下一次带来源的 Agent Hook 或显式路由会更新它。

备份：`~/.claude/backups/taiyi-install-20261123-160554-09758035f91c4477ab30c9c9e88735b4/`，含原 statusline/hud.sh、hooks/agent-state.py 和 settings.json。需要回滚时逐项恢复这些文件；保留新增 hud.py 和缓存也不会被旧命令调用。

本轮没有运行新的真实 Claude 会话，因此 UI 热加载表现未验证；已验证实际配置命令与真实已安装文件，烟测状态在临时项目中，不写真实项目状态。

截图反馈后仅更新已安装的 hud.py，模型可见性烟测确认亮白加粗和 CTX 保留。个人 settings/hud-config 未改变；该次原渲染器备份在 `backups/taiyi-install-20261123-163939-a985c31d19864c8d94b57e780b413119/`。

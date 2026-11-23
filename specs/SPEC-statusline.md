# Statusline 实现与验收契约

2026-11-23，RISK-MEDIUM。保留兼容入口 `.claude/statusline/hud.sh`，安装器默认直调 `python -S hud.py` 以减少 Shell 开销；不将独立 Rust 工具或旧 `statusline/statusline.py` 当作真实调用链。

## 要求

- stdin 按 JSON 一次解析，接受空格、换行、Unicode、零费用和不完整字段；优先读取官方 context_window/cost/workspace 数据，不读取整份 transcript，不固定 200K 上下文窗口。缺失指标显示未知，不填假 0。
- 默认展示合法会话已有信息；旧版 cost>0 门禁可通过 display.hide_zero_cost 明确开启。费用不代表 Stop 事件。格式错误 WARNING，stdout 不泄露原始输入。
- 所有模块 enabled/priority、主题、颜色、宽度、Git 子选项、进度条和缓存开关生效。窄窗口按优先级选择，使用显示列宽裁剪；只采集显示所需数据。
- 模型默认亮白加粗以适应深色终端；modules.model.high_contrast=false 时恢复原模型配色。空白/控制字符名称回退到真实 id；窄窗口先省略项目、Git 和次要信息，保护模型名称与 CTX。
- Git 使用单次 porcelain 调用，缓存按规范化当前工作目录隔离，TTL 来自配置。非 Git 目录正常省略；失败/损坏/超时必须 WARNING，不能伪造干净仓库。
- Agent/命令只从匹配 session_id 和 cwd 的路由状态读取，不默认 orchestrator。Agent Hook 增加 session/project 来源字段；匿名旧状态不冒充当前会话。Ralph 项目状态优先，全局状态必须匹配项目，带会话标识的状态须匹配会话。
- 保留 render/full/config/theme/cache-clear/version/help CLI 与 HUD_* 环境入口；非渲染命令不读 stdin。缓存清理只逐项处理 renderer 自有文件，保留其他工具缓存和链接，异常 WARNING。
- 使用 Python 标准库作为一次启动的实现，Shell 只转交；不依赖 jq/timeout，不引入依赖。max_execution_time 是本地采集预算，不声称能限制进程启动/所有系统的耗时。

## 验收与回滚

真实输入输出测试覆盖漂亮/紧凑 JSON、缺失/零指标、1M 窗口、配置 false、跨目录/会话缓存、恶意控制字符、损坏配置和缓存、Git 干净/脏/无上游/分离 HEAD、禁用模块不采集、Unicode 列宽和缓存清理边界；临时 target 安装与既有 Hook/安装器回归。

基准分别记录 Python 与实际 Shell 入口冷/热耗时，100ms 为需求目标；未达到时明确说明。安装器保留个人 hud-config.json 与其他设置，覆盖托管脚本前保留备份。真实全局同步/推送只在对应用户授权范围内执行，不能把上一轮 context-optimization 的授权扩大成任意个人设置替换。

官方接口来源：https://code.claude.com/docs/en/statusline （2026-11-23 获取）。旧 docs/hud 文档仅保留历史观测，当前使用与实测记录放 docs/STATUSLINE.md。

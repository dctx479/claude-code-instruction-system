# 规则治理改造与最终验收

日期：2026-11-21。范围：本仓库文件、全局安装、真实 CLI 生命周期、跨平台测试与三套外部工作流对照；不把所给文章的版本号或外部团队案例当作实测结论。

## 最终结果

| 项目 | 结果 |
|------|------|
| 规则入口 | AGENTS.md 67 行；CLAUDE.md 20 行；全局模板 14 行；严格静态审计 0 findings |
| Skill | 57/57 可移植 YAML 检查通过；修复 architecture-copilot 缺头；四个核心 Skill 的本机官方 quick_validate 通过 |
| 真实 CLI | 已安装 UserPromptSubmit 返回 0，Stop 先返回 2 接续、再返回 0 结束；最终 COMPLETED、iteration=1；真实用户快照未变 |
| Windows | 独立验证 venv，46 tests 全部通过，无 skip |
| Linux | WSL Ubuntu 24.04 独立验证 venv，46 tests 全部通过，无 skip；规则/Skill 审计通过 |
| 记忆 | 57 BP + 25 经验条目结构盘点，历史与现行规则分离；两条旧建议局部替代，保留案例 |
| 路由 | 本次 4 条真实请求做回归，通用项目分析不再误派数据分析角色；不宣称普遍准确率 |
| 三套工作流 | 已读取固定 commit 并记录采用/不采用的机制，未安装平行框架 |
| 远端 Actions | 未运行，不能冒充远端绿灯；当前工作区未提交，main 的本地跟踪状态 ahead 1/behind 1，不能擅自提交、推送或合并分叉 |

## 核对结果

| 项目 | 本轮核对 |
|------|----------|
| 原项目 CLAUDE.md | 806 行，26,529 字符，41,723 字节；不能称为再次超过 40,000 字符 |
| 真实全局入口 | 改造前与原项目入口的规范化 SHA-256 相同；第二阶段已迁移到独立模板 |
| 根目录技术栈 | 无 package.json，不能把 npm 检查当默认流程；子项目另有 manifest |
| 改造前历史记忆 | lessons 1,619 行、best-practices 2,565 行，规模不足以直接证明条目过期 |
| 仓库 Skill 文件 | 57 个直接子目录 SKILL.md；这不是全局安装数，也不是激活率 |

## 已落地到工作区

### 入口与安装

- AGENTS.md：67 行，4,137 字节，跨工具项目约定的单一来源。
- CLAUDE.md：20 行，1,225 字节，引用 AGENTS.md，只留 Claude 专用入口。
- config/claude-global.md：14 行，894 字节，作为全局安装源。
- .claude/rules/hooks.md：27 行，1,825 字节，按路径限定 Hook/安装约束。
- 原入口的废弃协议和 R1-R6 放 docs/RULE-EVOLUTION.md；角色、命令及 Ralph schema 改为按需查阅。
- core 安装不再复制项目入口。已知旧版和托管模板会先备份后迁移；自定义全局内容保留，显式 --replace-global-rules 才替换。

### 规则体检

- scripts/audit-rules.py：只读清单、行数/字节、@ 导入、循环/悬空导入、目录链预算、部分路径和显式命令核对。
- 200/60 行是项目预算；32 KiB 检查按 AGENTS 目录链计算，不汇总互不相关的子目录。
- 含糊路径/外部导入只标 review；不自动删除，不执行从规则提取的命令。
- /rule-audit 补足语义分类、冲突审查和 diff；/check 调用真实项目检查。
- 新增 Windows/Linux CI 配置，自动运行静态审计与回归测试；远端结果仍需实际 CI 运行确认。

### 路由与 QA

- Hook 使用 JSON 解析器，忽略 Markdown 引用、代码块；长粘贴仅采用最后短段落或默认角色。
- 路由 stdout 直接进入本轮上下文；session_id + cwd 哈希隔离状态，原子写入。
- 全局快照仅供旧 HUD 展示，仍为最后写入者覆盖；它不能再用于调度决策。
- 解析、配置和可选工具检测失败有 WARNING；不再把整条用户消息写日志。
- QA 按 LOW/MEDIUM/HIGH 风险选择投入，用逐项证据判定 PASS/FAIL/INCOMPLETE，取消固定 80 分发布门槛。
- 复盘和 /evolve 要求两次独立事故证据、优先硬保障、最小 diff 与反驳检查。
- 移除自动修复示例的 git checkout . 和批量删 import，防止覆盖用户修改。

## 验证记录

- 严格规则审计：4 个规则文件，0 findings。
- 配置检查：4 个 JSON 配置通过，0 错误、0 告警。
- 完整回归运行：22 tests，全部通过；随后新增的非 UTF-8 默认编码回归独立运行通过，合计 23 个测试方法已有通过记录。
- 自动测试覆盖审计的坏夹具、只读性、目录链预算、override 优先级、全局重复对照。
- 安装测试覆盖 core 与完整沙箱安装、重复安装、文件内容/mtime 幂等、自定义配置保留、显式替换及旧版迁移备份。
- 路由测试覆盖原有 34 个角色/回归输入，另覆盖文章粘贴、代码引用、坏 JSON、手动指定、空输入、会话隔离与坏关键词配置。
- 补充验证：强制 PYTHONIOENCODING=cp1252 时，中文 stdin 路由和带中文的工具推荐仍走 UTF-8 协议。
- Bash 语法和 Python 编译检查用于补充验证，不能代替上述行为测试。
- 第一阶段的官方 Skill quick_validate 因缺 PyYAML 未运行；最终阶段已在独立 venv 安装验证依赖并通过四个核心 Skill 检查。全库以六字段标准保留合法 compatibility，57/57 通过。

## 边界与阶段性说明

- 第一阶段仅验证沙箱；第二阶段已按 dry-run 计划同步相关全局组件，原文件有备份，settings.json 保持完全一致。
- 真实 `/context` 加载、已安装 Hook 直接调用和真实 CLI 两轮生命周期均已验证。没有人工点击 `/hooks` 菜单；用运行时事件证明注册与执行，不能把两者混称。
- 路由仍是启发式；短文本中未标记的引用、复杂混合意图可能误判，结果必须按当前请求复核。
- 机器审计不覆盖任意 shell 别名、Make/Cargo/CI 的全部语义，也不能证明自然语言规则相容。
- 历史报告、示例和记忆未全库改写；其中旧评分仅供追溯，当前 QA 依据 docs/QA-SYSTEM.md。

## 原计划逐项处置

| 优先级 | 工作 | 验收证据 |
|--------|------|----------|
| P0 激活验证 | 已完成真实加载、已安装副本与 CLI 两轮生命周期 | 原会话缓存不会被强制终止；新会话已验证 |
| P1 记忆策展 | 已扫描 82 条结构、修正索引与旧建议，明确历史内容不是现行指令 | 未将历史外部数字升级为本项目事实，不伪造置信度 |
| P1 路由评估 | 已加入 4 条本任务真实请求，修正裸“分析”触发数据角色的问题 | 夹具有来源；小样本通过不代表普遍准确率 |
| P2 Skill 盘点 | 57 个结构通过；11 份本项目会话缺少可用激活观测，决定不擅自停用 | 0 次观测不等于 0% 使用率，此假设不作为删除依据 |
| P2 外部工作流借鉴 | 三个固定 commit 已对照，采用硬检查、按需指针、真实界面验证 | 不叠加第三方权限、强制多 Agent、Wiki 或全任务 PR 仪式 |

激活时先运行 python scripts/install-global.py --dry-run 审阅计划；全量安装会同步其他组件，
应根据要生效的改动选择组件。仓库级工作已保存为未提交 diff，没有 commit、push 或 PR。

## 第二阶段：全局激活与防回流（用户要求继续推进）

- 同步组件：core、agents、commands、hooks、skills、knowledge；不改 statusline、权限、凭据。
- 首次激活新增 7、更新 22、未变 483 个文件；被覆盖文件备份目录：`~/.claude/backups/taiyi-install-20261121-210927/`。
- settings.json 同步前后内容完全一致，非托管设置摘要哈希也一致。
- 三份全局 memory 与 HEAD 中旧仓库版本逐字一致后，才备份并更新对应源；不覆盖增量个人经验，安装器默认 KEEP 策略仍然保留。
- 历史 #011 的 40K 目标和 BP-041 的旧同步方向作局部废弃标记，保留原案例；修正 memory 索引的 46→57 条 BP，并提示历史重号需用日期和完整标题检索。
- neat 从全库遍读改为当前任务影响范围，取消 40K 预算及强迫每层追加内容；同步修正配置指南。

### 真实 CLI 加载证据

本机 Claude Code 2.1.330，使用内置 `/context`；禁用诊断会话全部 Hook、禁用模型工具和 MCP，不调用模型生成，不发送通知。返回 cost=0。

| 目录 | 实际 Memory Files |
|------|---------------------|
| 本仓库 | 全局 CLAUDE.md 约 106 tokens；项目 CLAUDE.md 约 226；AGENTS.md 约 710；合计约 1K |
| 仓库外临时目录 | 仅全局 CLAUDE.md 约 106 tokens；不含本仓库 CLAUDE.md/AGENTS.md |

另一次“空 setting-sources”的诊断未列出 Memory Files，因此未用它作为加载成功证据；以上数字来自默认配置来源的诊断。

### 已安装副本验证

- 已直接调用真实安装目录的 Hook，在临时 HOME 验证路由 stdout、快照和会话状态，不改真实用户状态。
- 新增 scripts/verify-global-install.py：比较托管源文件、设置和实际安装副本；有状态知识源跳过，差异只报告不修复。
- 旧 verify-agent-dispatch.sh 改为校验器入口，取消 sleep、真实全局写入及无条件“验证成功”。
- 校验器实际识别到新脚本缺失和旧 wrapper 差异，返回 1；只有同步并重验后才可以记录为通过。
- 完成同步后重新校验：504 个托管文件一致、0 problems；已安装 Hook 临时 HOME 烟测 PASS，校验器退出码 0。
- 最终完整回归：26 tests 全部通过；覆盖新增校验器的缺失/差异、坏设置及烟测失败分支。
- 第二次增量同步及单位更正备份位于 `~/.claude/backups/taiyi-install-20261121-211551/`、`taiyi-install-20261121-211552/`；settings.json 字节不变。
- 三份 memory 的本次局部维护完成；尚未对全库条目作真实性复核，未批量删除或重标置信度。

## 最终阶段：真实生命周期与跨平台收口

### 修复真实代码问题

- Ralph 旧实现遇到无 project_dir 的全局状态仍可能拦住其他项目；某些完成/暂停/续跑分支用 `update_state ... || true` 吞掉写失败，可能在没有落盘时声称完成或继续。
- 现改为 hooks/ralph-state.py 的纯状态转移与原子写入，Bash 仅处理解释器和参数。全局归属、可选会话归属、格式和指标类型均在边界验证。
- 写入失败返回放行与 WARNING，不能报告 COMPLETED、不能返回继续信号；临时文件使用唯一名称，避免固定 .tmp 相互覆盖。
- 补 14 个 Ralph 行为测试，覆盖正常两轮、最大轮数、暂停、致命错误、跨项目/会话、坏输入和写失败。
- 零基计数还有一个实际越界：iteration=1、max_iterations=2 且本轮完成时，旧实现仍返回 2 启动第三轮。新增回归先复现失败，再修正为预算耗尽立即停止；不能多启一轮后才检查。
- 解释器缺文件和 argparse 参数错误也可能产生 2；入口现在检查 helper 是否存在，并把参数解析错误转换为 WARNING + 放行，避免误认成已持久化的续跑信号。
- 清理 active 文档中旧 CLAUDE 章节号、强制读全局快照、40K 预算和固定 QA 80 分门槛；历史报告与版本历史保留，不改写当时记录。

### 真实 CLI 证据

在临时项目、独立 HOME/config 目录运行受限 Claude；只有 Read/Write/Edit，禁用 MCP、外部通知及其他 Hook。
认证沿用已有配置，仅放在子进程内存，不写到诊断文件。模型只改临时状态，不能访问本仓库或运行命令。

事件顺序：UserPromptSubmit exit 0（debugger 建议）→ Stop exit 2 → 模型读取 iteration=1 → Stop exit 0。
最终状态：active=false、status=COMPLETED、total_iterations=1、successful_runs=1；真实用户 intent 快照哈希未变。
最终完整双 Hook 用例的 CLI 报告成本约 $0.033712；这次行为测试不是零 token 的 /context 诊断。

首轮排除用户设置时没有获得认证，未调用模型；随后在内存复用已有配置。
另一个隔离 HOME 的夹具最初没有把 $HOME 代码路径重定向到真实安装目录，出现 127，该轮记为失败；修正夹具路径后上述真实事件全通过，不能拿失败输出声称生产 Hook 成功。

### CI 与权限边界

独立验证环境安装 scripts/requirements-validation.txt，运行规则审计、Skill 审计及全部测试；Windows Python 3.14 和 Linux Python 3.12 各 46/46 通过。
Workflow YAML 触发器、双系统矩阵及只读权限检查通过，增加手动 workflow_dispatch 入口。
尝试 Docker Python 3.11 精确镜像时 registry 认证端点返回 EOF，未取得镜像；实际 Linux 验证使用 WSL，不冒充 Docker 或 GitHub runner。
远端 Actions 的执行前提是发布包含此 workflow 的提交。仓库 AGENTS.md 要求明确的提交/推送授权，且当前分支分叉，因此本轮没有擅自改远端或宣称远端 CI 已绿。

详细盘点与来源：MEMORY-CURATION-2026-11-21.md、WORKFLOW-COMPARISON-2026-11-21.md。

最终部署核对：510 个托管文件一致、0 problems；有状态知识源按保护策略跳过，个人设置字节不变。备份保留在 ~/.claude/backups/ 下。
最终 /context 还确认 architecture-copilot 已可发现，入口 tokens 为全局 106、项目 CLAUDE 226、AGENTS 728。
机器可读证据见 evidence/rule-governance-2026-11-21.json；没有将未执行的远端 Actions 标为成功。

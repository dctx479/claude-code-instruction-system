# 改进方案实现与验收状态

2026-11-23，RISK-MEDIUM。实现遵循 [运行时契约](../specs/SPEC-improvement-runtime.md)，交付推荐的三个轻量方案和 Playbook 版本管理。原始 7 份规划保持为设计背景；其中示例路径、自动执行和收益估计由本契约及当前实测校正。

## 任务映射

| 原规划任务 | 实现入口 | 状态 |
|---|---|---|
| 1.1 上下文路由 Hook | hooks/context-optimizer.py、scripts/taiyi/context.py | 完成；只建议，PostToolUse 不替换输出 |
| 1.2 记忆快速检索 | scripts/taiyi/search.py、rebuild-memory-index.py、taiyi-tool.py search | 完成；递归、内容指纹、FTS5/子串/纠错 |
| 1.3 上下文集成测量 | tests/test_improvement_runtime.py、measure-token-savings.py | 回归完成；真实 token 收益待采样 |
| 2.1 决策引擎 | scripts/taiyi/decision.py、/route | 完成；机械/Playbook/历史/模型兜底，失败优先 |
| 2.2 Playbook | memory/playbooks/REGISTRY.json 与 3 个 v1.0 流程 | 完成；无符号链接，显式版本选择 |
| 2.3 失败记忆 | memory/failures/REGISTRY.json、失败 Hook 事件 | 完成；3 个来源明确的提示，不硬拦截 |
| 2.4 决策日志 | scripts/taiyi/state.py、route --record、record、analyze | 完成；实际反馈、未知指标为 null |
| 2.5 决策集成 | 10 条标签 fixture 和回归 | 完成；10/10 fixture，真实任务准确率待采样 |
| 3.1 证据 Schema | memory/schemas/evidence-v1.json、scripts/taiyi/evidence.py | 完成；5 种类型、JSON frontmatter/sidecar |
| 3.2 证据查询 | taiyi-tool.py evidence trace/verify/find | 完成；来源范围、哈希、循环和链大小边界 |
| 3.3 追溯 Skill | .claude/skills/evidence-trace/SKILL.md | 完成；按需来源/置信度/验证状态展示 |
| 3.4 审计 | scripts/audit-evidence.py、taiyi-tool.py audit | 完成；错误非零，legacy 与未核实状态分列 |
| 3.5 记忆迁移 | memory/curated 的 10 条策展记录 | 完成来源索引；历史原文保留，未伪造不存在的事故 |
| 3.6 证据集成 | 新增回归、严格策展审计、既有规则工作流 | 完成；静态验证不冒充测试执行 |
| 4.1 文档 | CONTEXT-OPTIMIZATION、EVIDENCE-GUIDE、本文及各导航 | 完成；AGENTS.md 单一来源保持不变 |
| 4.2 工作流集成 | /rule-audit、/evolve、router、/memory-search、Skill profile | 完成；不扩大自动授权 |
| 4.3 回归与 CI | 原有 scripts/ci-tests.py 与 rules.yml | 完成；复用现有发现入口，加入场景/证据检查 |
| 4.4 性能基准 | scripts/benchmark.py、PERFORMANCE-BASELINE.md | 本地延迟/字节实测完成；真实会话指标待观测 |

规划中的 `.claude/hooks`、`.claude/agents/router`、memory 中的 Python 模块等示例路径不适配现有安装布局，统一归入 `hooks/` 和 `scripts/taiyi/`。不复制同一功能到两个目录。新 Memory Markdown 均附结构化证据或相邻台账；原有 9 个历史 Markdown 仍原样可读。

## 使用与验证

主接口 `python scripts/taiyi-tool.py --help`；[上下文优化指南](CONTEXT-OPTIMIZATION.md)、[证据指南](EVIDENCE-GUIDE.md)。默认安装不会启用优化 Hook，显式组件是 context-optimization；首次实现仅在临时 target 测试，本轮已按用户授权完成真实全局部署。

首次实现时，使用既有 `.claude-tmp/validation-venv/Scripts/python.exe`：

- `scripts/ci-tests.py`：105 项通过，其中新增 29 项；无跳过。后续受影响改动以新增回归复核。
- `scripts/test-decision-scenarios.py`：10/10 本地标签 fixture。
- `scripts/audit-evidence.py --memory memory/curated --strict`：10 条策展记录无失效来源。
- `scripts/audit-rules.py --strict`：0 findings；`audit-skills.py`：60/60；`check-doc-facts.py`、`build-agent-index.py --check` 均通过。
- `scripts/eval-skills.py`：静态描述检查通过，真实模型路由 NOT_RUN。
- `scripts/validate/validate-config.py`：4 份配置通过，0 告警。
- `bash scripts/test-all-intents.sh`：8 项通过；7 份相关 JSON 解析通过；`git diff --check` 无空白错误，Git 仅提示既有 CRLF/LF 规范化。
- 默认组件与 hooks,commands,context-optimization 两种临时 target 的安装 dry-run 均为退出码 0；`validate-issues.py issues/worktree-checkpoint.csv` 通过。
- skill-creator quick_validate：用 Python `-X utf8` 后通过；工具默认 GBK 读中文文件的失败属于验证工具编码问题。
- 安装器回归检查临时 target、幂等、个人 Hook/权限保留与组件撤销。真实 HOME 未改写，无提交、推送、PR 或真实通知。

全量回归默认 Python 初次运行缺少 PyYAML，出现 1 个环境错误；切换到仓库现有验证 venv 后原有 76 项通过。没有新增运行时依赖或为此安装包。

基准结果和未验证项见 [性能基线](PERFORMANCE-BASELINE.md)。覆盖率未测，不能声称达到 80%/85%。长期成功率和会话收益不以 fixture 代替。

## 全局启用与 Hook 优化（2026-11-23）

用户随后明确授权优化 Hook、修改真实全局配置并推送。本轮将连续提醒缩减到第 3、6、9 次及之后每 9 次，有 limit 的分段读取不提醒；无关工具、无匹配反馈不写状态，事件/反馈合并写入。目录/文件计数键哈希化，编辑路径只保存项目相对路径。修复 Windows 锁删除期间的短暂 PermissionError，持续权限错误仍在 500ms 预算内失败并 WARNING。

优化后 `scripts/ci-tests.py`：111 项全部通过（运行时测试 35 项），没有跳过；10 个路由 fixture、规则、Skill、能力索引和证据检查通过。先完成真实目标 dry-run，再仅增量安装 context-optimization；新增 36 个组件文件，settings 只更新 hooks，已有安全 Hook、usage、权限及其他个人配置经逐项对照均保留。

实际全局 `~/.claude/settings.json` 已注册 5 个优化事件。`verify-global-install.py --components context-optimization` 验证 11 个托管代码文件对齐；以 Git Bash 执行实际安装命令，在临时项目测试大文件提醒、正常工具反馈、失败脱敏、PreCompact 快照和 compact SessionStart 恢复，全部通过。重复安装未改变设置。此烟测不修改真实项目状态，也不发送通知。

安装备份：`~/.claude/backups/taiyi-install-20261123-152906-34548bddf5af4f7eb9c7e6fbfa8fb637/settings.json`。本轮保留已有安装快照；回滚可恢复该文件并重启 Claude Code。新会话加载实际配置，旧会话是否热加载未验证。真实个人 settings 和运行态不进入仓库提交。

## 完整外部系统备选

| 系统 | 适用触发 | 评估与接入边界 |
|---|---|---|
| Context Mode | 真实采样显示本地聚合仍占大量上下文，或需要执行工具与文档服务 | 核实当前版本/许可/官方插件接口，用独立测试项目验证权限、compact 与工具路由；保留本地 CLI 作为后备，不双重拦截相同调用 |
| Agentero / 原草案中的 Agnes Harness | 标签规则覆盖不足且模型路由成为实际瓶颈 | 用户 URL 是 poco-ai/Agentero，草案引用的 Agnes 仓库尚未证实对应关系；先核实身份、模型/协议、许可证和真实日志，测同一任务结果；训练/下载模型不属于本次轻量实现 |
| Craft Anything | 明确的、已授权软件分析或视觉对比需求 | 独立项目按需开放所需工具；Clean room 不视为 OS 沙箱；核对适配器、资源、许可与构建反馈，不将逆向工具默认加入通用编排 |

没有安装或下载上述系统，也没有确认文章中的许可、版本、GPU 成本、98% 或 14 倍数字。原草案中的外部安装片段仅作背景，不能作为可直接执行的安装指南。决定接入时先得到具体、可复验的 A/B 数据，再按授权在隔离目标安装。

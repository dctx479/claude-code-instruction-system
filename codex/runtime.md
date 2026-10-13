# Codex 运行适配协议

本协议用于在 Codex 中复用太一元系统的命令、角色和知识资源。源文档中的 Claude 专用约定须按下面的规则解释；用户指令和实际运行环境的约束优先。

## 资源定位与加载

直接使用本仓库时，资源根目录是仓库根目录。通过安装器安装后，资源根目录是项目或用户 `.agents/taiyi-system/`；相对于任意已安装 Skill 目录为 `../../taiyi-system/`。资源快照保留原有目录结构，更新后需要重新安装。

1. 明确用户的任务、目标项目和授权范围。代码变更作用于目标项目，系统资源目录仅提供指导。
2. 命令从 `commands/` 按需读取；`$ARGUMENTS` 表示用户在 Skill 名称后给出的文本，不是 shell 环境变量，也不自动执行。
3. 专家角色从 `agents/` 读取。可以根据任务查询 `agents/INDEX.md`，每次只加载需要的角色。`@architect` 等文本可解释为选择角色的请求，但不是 Codex 原生注册语法。
4. 领域 Skill 从 `.claude/skills/` 按需读取；安装的 `$taiyi-skill-…` 包装入口提供对应路径。相对脚本、模板和引用路径以原始 Skill 目录为基准。不要批量加载全部资料。
5. 原文中的 `~/.claude/agents`、`~/.claude/commands`、`~/.claude/skills` 引用对应资源根目录的 `agents`、`commands`、`.claude/skills`。脚本内的硬编码路径不会自动改写，执行前检查参数、依赖和写入位置。

## 平台差异

| 原文约定 | Codex 中的处理 |
|----------|----------------|
| `Read`、`Grep`、`Glob`、`Bash`、`Edit`、`Write` | 使用环境实际提供的读写和执行工具；搜索优先 `rg`，编辑遵守所在项目规范 |
| `Task`、`Agent`、`SendMessage`、`TeamCreate` | 只有当前环境提供相应工具且用户请求协作时才使用；否则由当前智能体按阶段执行，并说明限制 |
| Agent YAML 的 `tools`、`model: opus/sonnet/haiku` | 角色资料，不会授予工具权限或切换 Codex 模型；沿用当前配置 |
| `/review`、`/autopilot` 等 Claude 自定义命令 | 使用 `$taiyi-review`、`$taiyi-autopilot`；原文斜杠语法仅说明工作流意图 |
| `UserPromptSubmit`、`PreCompact`、`Stop` 等 Claude Hook | 不加载 Claude 的 Hook JSON，不依赖 `intent-state.json`，不注册后台自动任务 |
| HUD、Claude 费用和上下文状态文件 | 不接入 Claude 状态栏，不推算不存在的 Codex 费用或状态数据 |
| MCP JSON、`mcp__…` 工具名 | 通过 Codex 实际已注册的 MCP 工具执行；缺失时说明具体依赖，参照 Codex MCP 配置而非复制 Claude JSON |

## 执行与质量

使用规划 → 规范 → 实现 → 验证 → 交付的工作流时，按任务规模裁剪步骤。保持修改聚焦，使用项目已有测试；交付时报告实际执行的验证，不能把文档中的预期分数、加速比或成功示例当成实测结果。

`$taiyi-ralph` 表示当前会话中的有界迭代：先确定完成条件及最大迭代次数（用户未指定时为 10），每轮根据验证结果修复。达成目标、用户停止、达到上限或无法继续时结束并报告未完成项。`status/pause/resume/stop/history` 等子命令没有 Claude 后台状态机；只可基于实际会话记录解释，不能声称 Hook 会继续执行。

Autopilot、编排及 QA 文档中的发布、提交、推送、外部服务写入等动作，必须在用户授权范围内执行。工作流名称和角色说明不扩大授权，也不自动安装推荐工具。

上下文保存、经验沉淀和恢复仅在任务需要或用户要求时进行。使用目标项目允许的文件位置，不读写 Claude 的全局运行状态，不存储密钥。自动压缩前归档、退出拦截和跨会话恢复不由本适配层实现。

## 外部依赖

安装器只安装指令与资源，不安装 Python/Node/Rust 包，不设置 API Key，也不启用 MCP。科研、安全或数据工具可能需要额外依赖。先检查是否可用；缺失时提供具体的配置或安装步骤，避免把工具名称替换当成可运行的集成。

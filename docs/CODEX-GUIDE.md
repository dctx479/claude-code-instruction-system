# Codex 使用指南

Codex 兼容层通过 `AGENTS.md` 和原生 Skills 复用太一元系统。Claude Code 的配置保持独立；无需复制 `CLAUDE.md` 或修改 Codex 模型、认证、审批与沙箱配置。

## 安装

前提：已安装并登录 Codex CLI、Git、Python 3.8+。安装器仅使用 Python 标准库，无需安装依赖。

```bash
git clone https://github.com/dctx479/claude-code-instruction-system.git
cd claude-code-instruction-system
python3 scripts/codex/install.py --dry-run
python3 scripts/codex/install.py
codex
```

默认安装到本仓库 `.agents/`，包含 32 个 Skills（核心入口 + 31 个命令）。Codex 从仓库的 `AGENTS.md` 加载项目规则，从 `.agents/skills/` 发现 Skills。新安装入口未出现时重新启动 Codex；也可用 `/skills` 检查。

安装到其他项目：

```bash
python3 scripts/codex/install.py --project /path/to/your-project
```

目标项目原有 `AGENTS.md` 保持不变；通过 `$taiyi-core` 或具体 Skill 加载协议。若希望每次任务都启用太一，可自行将下面一行加入目标项目的 `AGENTS.md`：

```markdown
使用太一元系统时，读取 `.agents/taiyi-system/codex/runtime.md`，再按需读取相关资料。
```

用户级安装适用于所有项目：

```bash
python3 scripts/codex/install.py --user
```

该选项安装到 `~/.agents/`，不修改 `~/.codex/AGENTS.md` 或 `config.toml`。按照当前官方文档，用户级 Skills 位于 `~/.agents/skills/`，与 `CODEX_HOME` 的配置目录分开。

要在所有项目中默认启用太一运行规则，使用一键全局安装：

```bash
python3 scripts/codex/install.py --global --with-agents --with-skills --dry-run
python3 scripts/codex/install.py --global --with-agents --with-skills
```

`--global` 将 Skills 安装到 `~/.agents/skills/`，并在实际 `CODEX_HOME`（默认 `~/.codex`）的 `AGENTS.md` 追加带标记的太一入口，保留原有规则。若存在 `AGENTS.override.md`，则在该文件中追加以保证入口生效。修改前自动备份到配置目录的 `taiyi-backups/<UTC时间>/`；重复安装不会重复追加。项目自己的具体指令仍优先，认证、模型与 `config.toml` 保持不变。

`--global`、`--user` 与 `--project` 互斥。只希望全局提供 Skills 而不默认加载规则时使用 `--user`；全局启用后需重新启动 Codex 会话。更新全局安装时沿用 `--global` 及原有可选参数，资源发生变化时加 `--force`。卸载全局规则时只移除两条 `taiyi-codex-global` 标记之间的区块，不删除原有全局规则。

按需增加领域或专家入口：

```bash
python3 scripts/codex/install.py --skill debug --skill literature-mentor
python3 scripts/codex/install.py --with-agents
python3 scripts/codex/install.py --with-agents --with-skills
```

`--skill` 可重复，参数为原始 Skill 所在目录的名称；嵌套目录中的 `php-sql-audit` 等也可直接选择。全量安装包含 169 个入口，容易增加发现阶段的上下文成本，建议日常使用按需安装。默认快照已包含领域资源，可由核心入口按需读取；上述选项控制它们是否作为独立 Skills 展示。

## 使用

以下文本在 Codex 对话中输入，不是在 shell 中执行：

```text
$taiyi-core 为当前任务选择工作流
$taiyi-review 审查当前未提交的更改
$taiyi-check 运行项目已有的质量检查
$taiyi-autopilot 实现用户认证，先检查现有设计
$taiyi-ralph 修复现有测试失败，最多迭代 5 次
$taiyi-agent-architect 分析这个服务的扩展方案
$taiyi-skill-debug 定位这个报错的根因
```

最后两个示例分别需要 `--with-agents` 和 `--skill debug`。Skill 名称采用命名空间，避免与 Codex 原生命令或用户已有 Skills 重名。原来 Claude 的 `/review` 在这里使用 `$taiyi-review`；Codex 原生 `/review` 仍由 Codex 自己处理。

安装器保留命令、角色、脚本、模板与引用的原始目录结构。每个入口先读取运行协议，再读取对应的源文件；`$ARGUMENTS` 解释为用户随 Skill 提供的文本。资料中的工具名需要适配当前环境，脚本本身不会自动改写或自动运行。

## 兼容范围

| 功能 | Codex 支持方式 | 限制 |
|------|----------------|------|
| 核心指令 | 仓库 `AGENTS.md` + 运行协议 | 不加载 Claude 的全局状态 |
| 31 个自定义命令 | `$taiyi-命令名` Skills | Claude 斜杠语法不注册到 Codex |
| 专家角色 | 按需读取；可选 `$taiyi-agent-…` | 角色不是原生子智能体配置，不继承模型与工具权限 |
| 领域 Skills | 可选 `$taiyi-skill-…`；保留原资源 | 外部脚本和依赖需要单独验证 |
| Autopilot / QA | 在当前会话执行对应阶段 | 自动执行受用户授权与实际工具能力限制 |
| Ralph | 有完成条件和次数上限的会话内迭代 | 无 Stop Hook、后台状态机或自动续跑 |
| 多智能体编排 | 用户请求且环境提供工具时使用 | 无工具时由当前智能体按阶段执行 |
| 文件记忆 | 按需读取并在目标项目保存 | 不自动注册 PreCompact 归档或退出拦截 |
| MCP | 使用 Codex 已配置的服务 | 不复制 Claude JSON，不自动安装服务 |
| HUD / Claude Hooks | 未迁移 | 仍仅适用于 Claude Code |

原命令中的后台控制子命令、费用报告、自动状态追踪等会受到上述限制。包装为 Skill 表示指导资料可发现，不能据此声称所有 Claude 功能都已实现。

## MCP 配置

MCP 需按 Codex 的 TOML 或 `codex mcp add` 方式单独配置。先检查已有服务：

```bash
codex mcp list
```

例如按实际需求配置官方文档服务：

```bash
codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp
```

需要密钥的服务通过环境变量或其认证机制设置，不能直接把 `config/mcp-servers.json` 的 `${…}` 占位符当成 Codex TOML 中的变量替换。该安装器不启用任何 MCP 服务。

## 更新、备份与卸载

安装内容是快照，源文件更新后重新运行安装器。同内容安装不写入文件。发现同名但内容不同的文件时，默认在写入前终止；确认需要更新后使用：

```bash
python3 scripts/codex/install.py --force
```

被替换的文件先保存到 `.agents/taiyi-backups/<UTC时间>/`。`--dry-run --force` 可预览更新且不写入。更新时继续使用原先的 `--project`、`--user` 和可选安装参数。部分安装不会删除先前可选的入口，清单保留其记录。

卸载时根据 `.agents/taiyi-system/install-manifest.json` 的 `files` 清单检查并删除安装器管理的文件，然后移除清单。不要直接删除整个 `.agents/skills/`，其中可能包含其他用户 Skills；备份需单独保留或处理。

## 验证

```bash
python3 -m unittest discover -s tests/codex -v
python3 scripts/codex/install.py --dry-run --with-agents --with-skills
```

安装后在 Codex 中输入 `$taiyi-core 列出当前可用的太一入口及兼容限制`，再用 `$taiyi-review` 执行一次实际审查。自动测试验证安装与资源引用，不代表已验证每个领域工具、外部 MCP 或模型执行结果。

## 官方依据

- [Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md)：项目指令、全局指令及目录覆盖；默认项目指令预算为 32 KiB。
- [Codex Skills](https://developers.openai.com/codex/skills)：`.agents/skills/` 发现机制、`SKILL.md` 格式与 `$skill-name` 调用。
- [Codex MCP](https://developers.openai.com/codex/mcp)：TOML 配置与 `codex mcp` 命令。

文档核对日期：2026-10-13。本适配层使用指令与 Skills 接口，不依赖某个模型名称。

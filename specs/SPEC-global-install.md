# 全局安装脚本（install-global）- 技术规范

> 状态: 已实现 | 日期: 2026-11-19 | 复杂度: 低（单脚本，无新依赖）

## 1. 背景

本仓库是太一元系统的"源"，实际生效位置是 `~/.claude/`。此前同步靠手工 `cp`（见 `docs/audits/CONFIG-SYNC-AUDIT-2026-06-10.md` 记录的多处失同步），并且存在三个结构性问题：

- `hooks/hooks.json` 不会被 Claude Code 自动加载，hooks 必须写进 `settings.json`
- 根目录的 `commands/`、`agents/` 不会被发现，必须位于 `~/.claude/commands/`、`~/.claude/agents/`（或项目 `.claude/` 下）
- 换机器后（本次：新 Windows 机器）全局目录为空，整套自动化不生效

## 2. What（输入 / 输出）

**输入**：仓库工作区；目标目录（默认 `~/.claude`，`--target` 可覆盖）。

**输出**：

| 源 | 目标 | 策略 |
|----|------|------|
| `CLAUDE.md` | `CLAUDE.md` | 覆盖 |
| `agents/` `hooks/` `scripts/` `config/` `workflows/` `docs/` `specs/` | 同名目录 | 覆盖 |
| `commands/<分类>/<名字>.md` | `commands/<名字>.md` | 覆盖，**拍平子目录**（否则注册成 `/general:ralph` 而不是 `/ralph`）；拍平后重名视为错误 |
| `.claude/skills/` `.claude/statusline/` `.claude/reference/` `.claude/prompts/` | `skills/` `statusline/` `reference/` `prompts/` | 覆盖 |
| `memory/`、`config/port-registry.json`、`.claude/hud-config.json` | 同名 | **仅在目标不存在时复制**（有状态文件，不覆盖已积累的内容） |
| `hooks/hooks.json` 的 `hooks` 块 | 合并进 `settings.json` | 替换本系统旧条目，保留用户其他 hooks |
| statusLine | `settings.json` | 仅在未设置或已是本系统的 `hud.sh` 时写入 |

## 3. How（行为）

1. 读取并校验现有 `settings.json`；JSON 非法则中止，不做任何写入
2. 复制文件。目标已存在且内容不同 → 先备份到 `backups/taiyi-install-<时间戳>/` 再覆盖
3. 合并 hooks：以命令中含 `/.claude/hooks/` 或 `/.claude/scripts/` 识别"本系统条目"，先全部移除再写入当前版本（幂等，可重复执行；事件迁移如 Stop→SessionEnd 不留残余）
4. 写 `settings.json`（先备份，原子替换），保留 `env`、`permissions` 等其他键
5. 自检：每条 hook 命令指向的脚本在目标目录下存在；`settings.json` 可解析

**排除**：`__pycache__/`、`*.pyc`、`*.log`、`*.tmp`、`memory/` 下的点文件和 `ralph-state.json`（项目级运行态）、`commands/INDEX.md`（否则会变成 `/INDEX` 命令）。

**选项**：`--dry-run`（只打印计划）、`--target DIR`、`--components a,b`（`core,agents,commands,hooks,skills,statusline,knowledge`，默认全部）。

## 4. When done（验收标准）

- [ ] `--dry-run` 不产生任何写入
- [ ] 在沙箱目标目录安装后：hook 脚本齐全、`settings.json` 合法、原有 `env` 等键原样保留
- [ ] 连续执行两次，第二次报告 0 个文件变更，`settings.json` 的 hooks 不重复
- [ ] 沙箱内 `scripts/test-all-intents.sh` 全部通过
- [ ] 沙箱内用真实 `claude -p` 验证：UserPromptSubmit 写出 `intent-state.json`；Stop hook 能让 Ralph 续跑到 `max_iterations`

## 5. What NOT（边界）

- 不删除目标目录中的任何文件（卸载/清理不在范围内）
- 不修改 `settings.json` 中 `hooks`、`statusLine` 之外的键
- 不安装外部依赖（jq、PyYAML 等），不配置 MCP 服务器（需要用户自己的 API Key）
- 不处理 `~/.claude.json`（Claude Code 自动管理）

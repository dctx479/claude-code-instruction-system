# 太一元系统：Codex 项目指令

本仓库同时支持 Claude Code 与 Codex。默认用中文沟通，遵循用户要求及所在目录更具体的指令。

## Codex 入口

- 开始使用本系统时，读取 `codex/runtime.md`；只在任务需要时读取对应命令、角色或领域资料。
- `CLAUDE.md`、`.claude/settings.json`、`hooks/` 属于 Claude Code 集成，不作为 Codex 的运行配置。
- 在仓库根目录运行 `python3 scripts/codex/install.py`，将命令安装到 `.agents/skills/`。通过 `$taiyi-core`、`$taiyi-review` 等调用，详见 `docs/CODEX-GUIDE.md`。
- 专家定义是可复用的角色资料；读取角色文件不会创建子智能体。仅在用户要求且当前环境支持时进行多智能体协作。

## 修改与验证

- 保留现有 Claude Code 使用方式；平台差异放在 Codex 适配层。
- 新增安装功能使用 Python 标准库，避免安装时下载依赖、修改认证信息或覆盖用户已有配置。
- 修改 Codex 安装器后运行 `python3 -m unittest discover -s tests/codex -v`。
- 修改 Markdown 时核对资源路径及使用示例；安装器改动还需验证 dry-run、重复安装和冲突备份。

## 完成标准

说明实际修改、验证结果及兼容边界。只根据当前环境真实提供的能力执行，不能把 Claude Hook、模型名、工具权限或状态栏当成 Codex 已具备的功能。

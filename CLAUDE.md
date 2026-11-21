# 太一元系统：Claude Code 项目入口

@AGENTS.md

## 按需加载

- 任务明确时直接执行；需要专长时查 `agents/INDEX.md`，只加载相关定义。
- Skill 从 `.claude/skills/INDEX.md` 匹配，只读本次需要的完整 SKILL.md。
- UserPromptSubmit 输出的 intent / agent / tool_recommendation 是建议；先核对当前请求。
- 不必每轮读取全局 intent-state.json；它只是旧 HUD 的显示快照，可能来自别的会话。
- 用户以 `@{agent-id}` 开头时优先使用指定角色；角色不存在时说明并保持默认行为。
- 工具推荐不代表安装授权；先判断必要性、验证是否安装，再按用户授权处理。

## 自动化边界

- hooks/hooks.json 是安装模板，项目根的 hooks/ 和 agents/ 不会自动成为全局配置。
- 全局安装方法与备份策略见 `specs/SPEC-global-install.md`；先运行 dry-run。
- Ralph 的初始化字段、project_dir 隔离及停止信号见 `commands/general/ralph.md`。
- Hook 代码约束按路径加载 `.claude/rules/hooks.md`；修改后验证配置、执行效果和平台兼容性。
- `/rule-audit` 只提出证据和 diff；`/evolve` 先核对事故证据，再建议保障方式。

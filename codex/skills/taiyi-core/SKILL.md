---
name: taiyi-core
description: 在 Codex 中使用太一元系统，选择其命令、专家角色或领域知识，并解释 Claude Code 与 Codex 的平台差异。
---

# 太一元系统 Codex 入口

读取相对于本 Skill 目录的 `../../taiyi-system/codex/runtime.md`，按需加载资源。

- 查询命令时读取 `../../taiyi-system/commands/INDEX.md`，使用已安装的 `$taiyi-命令名`。
- 查询专家角色时读取 `../../taiyi-system/agents/INDEX.md`；角色以参考资料方式使用，原文工具权限与模型配置不生效。
- 查询领域能力时读取 `../../taiyi-system/docs/SKILLS-CATALOG.md`；依赖工具必须在当前环境实际可用。

处理用户当前目标项目中的任务，避免将资源快照误作目标代码。只加载当前任务需要的资料。

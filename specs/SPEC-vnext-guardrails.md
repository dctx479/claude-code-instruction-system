# vNext Hook 与权限变更

状态：实施中 · RISK-HIGH · 2026-11-21

用户已授权全面推进 vNext；本次只修改仓库模板和临时安装目标，不修改真实全局设置。

## 接口与边界

- 默认 Hook 不自动改写编辑文件、不保存项目 diff、不发外部通知，不注册空 PreCompact。
- lint-feedback、session-backup、usage、notifications 为独立可选组件。
- `--with-guardrails` 显式合并权限模板，保留个人条目，不添加 allow。
- 模板禁用 bypass；ask 不能用作 bypass 下的保证。模板与补充 Hook 都不是 OS 沙箱，不能防御任意解释器、别名或编码绕过。
- 不把 AGENTS.md 的授权约定替换为“由权限保证”。真实 CLI 的确认/拒绝、复合命令、git -C、PowerShell 必须另验。
- 补充命令检查拒绝明显危险的递归删除与磁盘格式化；不输出原始命令，避免秘密泄露。
- 缺工具、输入错误、状态写入失败都输出 WARNING；不回报假成功。

## 验收

临时目标验证设置合并、幂等、保留个人权限；Hook stdin 传入坏 JSON、危险参数变体、普通命令；lint 文件哈希不变；备份保留期与容量边界。
真实 Claude 会话验收未完成前，模板标记为候选，不能声称安全边界验证完成。

## 回滚

仓库变更按主题 revert。实际安装前备份 settings；恢复对应 `backups/taiyi-install-*/settings.json` 并重启会话。
切换 profile 不删除已有全局能力；旧安装的额外文件只报告，待审阅迁移，不批量删除。

## 文档依据

- https://code.claude.com/docs/en/permissions
- https://code.claude.com/docs/en/skills

读取日期 2026-11-21。实现验证与真实 CLI 验证分开记录。

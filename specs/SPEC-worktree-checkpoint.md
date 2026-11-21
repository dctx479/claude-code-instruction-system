# Worktree 交接检查点

状态：implemented，验收证据见 vNext 实施报告 · 2026-11-21 · RISK-MEDIUM

## 问题与行为

自由文本交接无法区分“没有记录”和“记录损坏”，也不能发现交接后文件变化。
提供 save/verify/show 接口，在当前 worktree 的 git 状态目录保存单一 JSON。
输入含 goal、done、next、evidence 和仓库相对文件清单；由工具计算 SHA-256，原子替换写入。

## 验收

- 新仓库 verify 返回 2；保存后返回 0。
- 修改任一记录文件后返回 1；损坏 JSON 也返回 1 并含 WARNING。
- 路径越界和 .git 路径不读取；不同 worktree 的记录互不覆盖。
- 记录不提交，不执行 evidence 中的命令，不自动修改历史记忆。

## 回滚

停止使用检查点，保留旧记录作参考；revert 工具及其命令入口。没有用户数据迁移或删除。

---
name: evidence-trace
description: 追溯太一仓库规则或记忆的来源、置信度和验证状态，适用于询问“这条规则基于什么证据”。
---

# 证据追溯

选择用户指定的记忆，先搜索名称，再只读取相关证据链。仓库内用 `python scripts/taiyi-tool.py evidence trace curated/<name>`；全局安装用 `$HOME/.claude/scripts/taiyi-tool.py --root <项目或知识根> evidence trace curated/<name>`。

运行工具需安装 commands 或 context-optimization 组件。目标仓库来源由 `--root` 指定，知识由 `--memory` 指定，不能用别的项目验证本仓库测试引用。工具不存在时按相关文档手动核对，并报告 WARNING 和未验证项。

以来源、方法、作者置信度、验证状态和关联链回答。`reference_valid` 只证明引用存在；不能写成测试通过。`invalid`、`changed`、`cycle` 或 `unverifiable` 要明确列出。旧记忆是历史证据，不自动重写或补造可信度。

新增规则仍须两次独立事故证据；两份文件或一个 commit 与其测试不自动算两次事件。追溯不执行证据里的任意命令。

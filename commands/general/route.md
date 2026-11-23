---
description: 机械任务、Playbook 和历史任务的轻量建议路由
disable-model-invocation: true
---

为 $ARGUMENTS 选择可复用处理方式。运行 `python scripts/taiyi-tool.py route <任务描述>`，全局安装用 `$HOME/.claude/scripts/taiyi-tool.py`。任务文本作为一个参数传递，不拼接成 Shell 命令。

按结果读取匹配 Playbook 或使用聚合工具。它只推荐操作，不执行命令或调用模型；兜底由当前 Agent 判断。不要自动转交子代理。

需要记录时显式加 `--root <项目> --session <会话标识>` 和 route 的 `--record`；完成后用 record 的决策 id、success/failure/rejected 回填真实结果，再用 analyze 查看复盘。未知成本/耗时保持空值。不要记录密钥或完整提示词。

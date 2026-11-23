---
description: 递归检索本地记忆并返回有来源的短片段
disable-model-invocation: true
---

运行 `python scripts/taiyi-tool.py search <查询>`，仅按需读取命中的来源。全局安装使用 `$HOME/.claude/scripts/taiyi-tool.py`，必要时指定 `--memory <记忆目录>`。

查询作为一个参数传递；默认最多 3 个片段。自动检查内容指纹，可用 rebuild 手动重建。FTS5 缺失会 WARNING 后降级；空结果不是已证明不存在。历史记忆不能代替当前项目规则。

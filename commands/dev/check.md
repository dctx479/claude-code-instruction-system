---
description: check
disable-model-invocation: true
---

对当前项目运行与变更相关的检查，不修改代码。

1. 先读项目指令、git diff、manifest 和 CI，确认技术栈及包管理器。
2. 如果是太一规则仓库，从根目录按变更选择：

```bash
python scripts/audit-rules.py --strict
python -m unittest discover -s tests -p "test_*.py"
bash scripts/test-all-intents.sh
python scripts/validate/validate-config.py
python -m json.tool hooks/hooks.json
python -m json.tool config/keywords.json
python scripts/install-global.py --dry-run
```

3. 其他项目只运行其 manifest / CI 中确实存在的检查；不依次尝试 npm/pnpm/yarn。
4. 没有配置的 lint/类型/性能检查标“不适用”；工具缺失标“未验证”，不自动安装。
5. 输出 检查项｜命令与运行目录｜退出码/证据｜结果（通过/失败/未验证/不适用）。
6. 区分已有失败与本次回归；任何必需检查失败均不能报告全通过。

语义规则审查用 /rule-audit；机器审计不能判断所有规则是否过期。

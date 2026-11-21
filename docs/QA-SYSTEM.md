# 按风险验收的质量保障流程

本页是太一 QA 的当前执行标准。历史示例中的 100 分制和 ≥80 发布门槛不再作为验收门禁。

## 选择流程

任务风险使用 RISK-LOW / MEDIUM / HIGH，与缺陷严重度 P0/P1/P2 区分：

| 风险 | 典型改动 | 设计要求 | 验收证据 |
|------|----------|----------|----------|
| LOW | 普通文档、无行为变化的整理 | 目标与范围即可，不强制新 Spec | diff、引用和必要格式检查 |
| MEDIUM | Hook、配置、路由、安装器 | 简短计划；复杂行为用短 Spec/复用现有 Spec | 正常与失败分支、回归测试 |
| HIGH | 权限、安全边界、生产/破坏性操作 | Spec、权限边界、回滚与风险方案 | 边界测试、人工审查、实际授权 |

规则文字若改变执行或安全行为也可能为 MEDIUM/HIGH。行数少不代表风险低。
显式调用 /spec-first 时走规范流程；普通 LOW 改动不强制走它。
既有验收标准足够时直接复用，不再为同一需求制造平行文档。

## 执行闭环

需求/验收标准 → 按风险确定方案 → 实现 → qa-reviewer 核对证据 → 修复 → 重验。

- qa-reviewer 读取需求和 diff，检查实际接口与边界，不套用 Web 应用模板。
- qa-fixer 只修其授权范围内的低风险问题；修复后重跑相关检查。
- 任何失败的必需验收项、未解决 P0/P1 都阻止 PASS。
- 缺少必需证据时判 INCOMPLETE，明确补什么；没有测过不能打勾。
- N/A 须说明原因，不伪造覆盖率、性能数字或“未发现漏洞”的结论。
- 合并/发布由用户授权决定，QA 结论本身不是执行授权。

## 命令选择

先读当前项目的 manifest / CI / 规则，确认运行目录及包管理器。
太一仓库从根目录按改动运行：

```bash
python scripts/audit-rules.py --strict
python -m unittest discover -s tests -p "test_*.py"
bash scripts/test-all-intents.sh
python scripts/validate/validate-config.py
python -m json.tool hooks/hooks.json
python scripts/install-global.py --dry-run
```

不在仓库根盲跑 npm。子项目有自己的 manifest 时，只使用其中已定义的脚本。
工具缺失先报告；不要自动装依赖、修改全局配置或用静默 fallback 把失败变成成功。
安装验证使用临时 --target；验证合并设置、备份、幂等与自定义指令保留。

## 交付

LOW 任务在回复中附证据即可。复杂任务可用 QA-REPORT.md，包含：
- 目标、风险档位、变更范围与关键决策。
- 每个必需验收项的实现位置、实际命令、运行目录、退出码和结果。
- 已有失败与本次回归、缺陷严重度、未验证项与人工操作。
- PASS / FAIL / INCOMPLETE 结论。

历史报告和记忆保留原有评分供追溯；不批量改写历史结论。
角色：agents/qa-reviewer.md、agents/qa-fixer.md。
完整规范流程：.claude/skills/spec-first/SKILL.md。

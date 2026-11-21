# 太一元系统：仓库工作约定

## 范围与工作方式

- 本仓库维护 Agent、命令、Skill、Hook 与安装工具；不要假定根目录是 Node/TypeScript 应用。
- 先检查 git status、目标文件和调用者；保留用户未提交的修改。
- 改动应对应明确需求，沿用邻近风格；不顺手扩展功能、引入依赖或重排无关文件。
- 多步任务先列简短计划及验收点；影响实现的重要假设要说明，能用仓库证据确定的先查证。
- 不提交、不推送、不创建 PR、不操作生产环境，除非用户明确要求。
- 依赖安装、公共 API/数据库破坏性变更、删除现有功能需有相应授权。
- 不批量删除文件；异常和降级必须有 `WARNING` 日志，不用假成功掩盖失败。

## 风险与验收

任务风险使用 RISK-LOW / RISK-MEDIUM / RISK-HIGH，避免与缺陷严重度 P0/P1/P2 混用。

| 档位 | 例子 | 必需交付 |
|------|------|----------|
| LOW | 文档、局部无行为变化的整理 | 目的、diff、相关链接/格式检查 |
| MEDIUM | Hook、路由、安装器、配置行为 | 简短计划、受影响接口、回归测试及输出 |
| HIGH | 权限、安全边界、生产或破坏性操作 | Spec、风险/回滚方案、边界验证；执行需符合用户授权 |

- 依爆炸半径分档，不单凭行数；文档中改变安全或执行规则也要升级风险。
- LOW 不强制新建 Spec、不打 QA 分；MEDIUM 可复用现有 Spec，复杂行为用短 Spec。
- 验收看需求与证据：失败的验收项和未解决的阻塞缺陷不能被总分抵消。
- 交付说明改了什么、跑了哪些命令及结果、未验证项；未跑过的检查不能写成通过。
- 性能、覆盖率指标来自当前需求，不能把示例应用的阈值套给所有项目。
- 详细 QA 流程见 `docs/QA-SYSTEM.md`，角色定义见 `agents/qa-reviewer.md`。

## 本仓库验证入口

从仓库根目录运行（Python 3.10+；Hook 运行时只用标准库；完整验证环境见 scripts/README.md，Shell 测试需要兼容 Bash）：

```bash
python scripts/audit-rules.py --strict
python scripts/audit-skills.py
python -m unittest discover -s tests -p "test_*.py"
bash scripts/test-all-intents.sh
python scripts/validate/validate-config.py
python -m json.tool hooks/hooks.json
python -m json.tool config/keywords.json
python scripts/install-global.py --dry-run
```

- 只对相关改动运行对应检查；配置检查器的既有告警要与本次回归区分。
- 子项目命令以其 manifest / CI 为准；不要在根目录盲跑 npm 或轮流试包管理器。
- 语法检查不能替代 Hook 的 stdin/stdout、状态文件和失败分支测试。
- 安装器测试使用临时 --target；不为测试覆盖真实 ~/.claude 或发送真实通知。

## 规则、记忆与知识维护

- AGENTS.md 是跨工具项目约定的单一来源，CLAUDE.md 只保留 Claude 专用入口。
- `config/claude-global.md` 仅放跨项目偏好；项目规则不得由安装器写入全局入口。
- 入口各不超过 200 行；细节按需放 docs、子目录规则或已有 Skill，不能靠自动导入绕过预算。
- 审计用 /rule-audit：证据不足的条目标记“需人工确认”，默认不写规则。
- 重复事故先核对两次独立证据，再比较 lint/测试/hook/权限；新增规则须可从 diff 验证。
- 用 /evolve 提出最小 diff，评估误伤、冲突和过期风险，同时寻找可合并的旧条目。
- 历史记忆不因“太长”或“看起来旧”就删除，也不能批量伪造 UNVERIFIED 状态。
- 经验先查重，保留案例、验证方法和置信度；只加载与当前任务相关的条目。
- 废弃生命周期及根因 R1-R6 见 `docs/RULE-EVOLUTION.md`；复杂任务可按需复盘、整理。

## 导航

- Agent 与 Skill：`agents/INDEX.md`、`.claude/skills/INDEX.md`
- 命令与编排：`commands/INDEX.md`、`docs/ORCHESTRATION-GUIDE.md`
- 上下文与记忆：`docs/CONTEXT-ENGINEERING-GUIDE.md`、`memory/INDEX.md`
- 安装与安全：`specs/SPEC-global-install.md`、`docs/SECURITY.md`

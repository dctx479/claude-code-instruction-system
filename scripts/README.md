# Hook、安装与验证工具

Hook 运行时只依赖 Python 标准库与 Bash。开发验证使用 Python 3.10+ 和独立 venv：

```bash
python -m venv .claude-tmp/validation-venv
python -m pip install -r scripts/requirements-validation.txt
```

先激活 venv；Windows 的解释器是 `.claude-tmp/validation-venv/Scripts/python.exe`，其他系统是 `bin/python`。

## 安装

```bash
python scripts/install-global.py --dry-run --target <临时目录>
python scripts/install-global.py --profile core
python scripts/install-global.py --profile core,research,ctf
python scripts/install-global.py --profile all
```

默认只安装 core 能力；清单唯一来源为 `config/profiles.json`。安装不会删除旧目标中的领域能力，不能以重新安装 core 宣称旧全量安装已精简。
默认 Hook 是命令补充检查、Agent 状态、显式路由、流程选择卡和 Ralph Stop。只有命令含 docker/compose/podman 才启动独立端口检查。

可选组件显式加入 `--components`（该参数是完整组件集合，不是追加）：

```bash
python scripts/install-global.py --components core,agents,commands,hooks,skills,knowledge,usage
python scripts/install-global.py --components core,hooks,lint-feedback,session-backup
python scripts/install-global.py --components hooks,notifications
```

- lint-feedback：Edit/Write/MultiEdit 后只运行本地 ESLint 或 Ruff，显式禁止 fix；不运行 npm scripts、npx、Black 或 Prettier。
- session-backup：只备份受跟踪文件相对 HEAD 的 diff，不含未跟踪文件；保留 14 天、总量 50 MiB，只轮转自有补丁。补丁可能包含敏感内容，按需启用。
- usage：只记 `{ts, tool, name}`，保留 90 天；包括 Skill/Agent 工具调用，以及注册 Skill/命令的显式 slash 展开；不记提示词、参数、响应或项目路径。`python scripts/usage-report.py --days 28` 统计。锁冲突/损坏输出 WARNING，不冒充成功。
- notifications：只有明确启用才发送通知；测试不得启用真实通知。

`--with-guardrails` 单独合并 `config/settings-guardrails.json`，保留个人 allow/ask/deny。冲突在复制前报错，不覆盖个人权限。
模板禁用 bypass；ask 在 bypass 下不是保证。边界和回滚见 `specs/SPEC-vnext-guardrails.md`。
覆盖前保留安装备份。新备份有完成标记与文件哈希，默认保留最近 5 份，可用 `--backup-retention N` 调整。只逐项过期完整且未被改写的托管快照；历史无标记、未知文件、链接或改写过的备份保留并报告。恢复对应 settings 后重启会话。
`tools/cc-patcher.sh hooks` 只是兼容转交，不独立写 settings。

旧全量安装可运行 `python scripts/migrate-install.py` 审阅计划，确认后加 `--apply`。仅将与当前/历史托管源码一致的 profile 外能力移入目标的 `.taiyi-migrations/`；个人改写、未知文件或链接不迁移。`--restore <manifest.json>` 可恢复，存在活动文件冲突则停止，不覆盖。该命令不清理项目源码或历史记忆。
`python scripts/discover-capabilities.py` 校验实际安装的发现元数据与描述体积。

## 验证

```bash
python scripts/audit-rules.py --strict
python scripts/audit-skills.py
python scripts/build-agent-index.py --check
python scripts/check-doc-facts.py
python scripts/eval-skills.py
python -m unittest discover -s tests -p 'test_*.py' -v
bash scripts/test-all-intents.sh
python scripts/validate/validate-config.py
python -m json.tool hooks/hooks.json
python -m json.tool config/keywords.json
python -m json.tool config/settings-guardrails.json
python scripts/install-global.py --dry-run --target <临时目录>
python scripts/verify-global-install.py --target <已安装临时目录> --profile core --smoke-hook
```

`verify-global-install.py` 的 components/profile/with-guardrails 必须与安装时一致。Hook 烟测使用临时 HOME，不修改真实用户运行态。
`audit-skills.py` 区分通用标准与 Claude 扩展字段，调用控制字段必须在顶层；超过 500 行报 WARNING。
`audit-rules.py` 检查活动文档中的旧章节引用；reports/archive/hud 历史报告保留原貌，不作为活动规范检查。入口链接的 INDEX 预算为 150 行。
`review` finding 需人工确认，不自动删除文件；`--strict` 对 error/warning 非零退出。
机器检查不涵盖完整语义、所有 shell 语法或模型真实决策。评估说明见 `evals/README.md`。

## 工作流工具

`python scripts/checkpoint.py save|verify|show` 使用 worktree 本地检查点；0 有效、2 缺失、1 损坏或过期。
`python scripts/validate-issues.py issues/<name>.csv` 检查依赖存在性、环路和启动顺序，不执行 CSV 中的命令。
流程单一来源为 `docs/VNEXT-WORKFLOW.md`，历史记忆数据不会因本次迁移删除。

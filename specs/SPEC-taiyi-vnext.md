# 太一 vNext：问题修复与工作流设计

> 状态：草稿，待用户逐项确认 · 日期：2026-11-21 · 风险：整体 HIGH（含权限边界），各阶段单独分档
> 依据：本仓库 2026-11-21 只读扫描；三套外部工作流在固定 commit 的阅读结论
> （addyosmani/agent-skills `8c99fa3`、michael-denyer/pstack-claude `97d2ba2`、mattpocock/skills `abeeaf9`），
> 详见 `docs/audits/WORKFLOW-COMPARISON-2026-11-21.md`。外部仓库的效果数字均为作者自述，不作为本项目验收阈值。

## 0. 一句话

把「写在文字里希望模型遵守」的东西，尽量换成**权限、可失败的检查和按需加载**；
工作流按风险分三档，每档只产出必要的工件，文档只存一处、只追加，不建 wiki。

## 1. 设计原则（每条都可从 diff 或测试验证）

| # | 原则 | 来源 | 如何验证 |
|---|------|------|----------|
| P1 | 必须拦住的动作交给权限规则，Hook 只作第二层，文字规则只作说明 | 第一篇文章；matt 自己冻结 grep 护栏 | 沙箱触发 deny/ask 的测试 |
| P2 | 每条「必须」都有一个能失败的检查，并有坏样例证明它会失败 | pstack `tests/invariants` | 每个检查对应一个失败夹具 |
| P3 | 按调用方式分层：工作流类只能用户调用，参考类可由模型调用，原则类不注册为 Skill、按路径读取 | matt `disable-model-invocation`；pstack 隐藏原则类 | 新会话 `/context` 中 Skill 描述体积 |
| P4 | 单一来源：每个事实只存一处，数量和列表由脚本生成或校验，不手工多处同步 | addy "link don't restate"；trellis 教训 | 文档事实检查 |
| P5 | 验收看证据：先有能变红的命令，再改；在真实产物上验证 | matt diagnosing-bugs；pstack verify | 交付说明里的命令与输出 |
| P6 | 不可逆和对外动作由人决定；自主循环必须有停止条件 | 本仓库 AGENTS.md；拒绝 pstack 的「不要问、不要停」 | Ralph 测试；权限 ask |
| P7 | 先收集使用数据，再做去留；没有数据不删除 | 本仓库记忆治理原则 | 调用记录 |

## 2. 目标结构

```
入口层   config/claude-global.md（全局，≤60 行）  AGENTS.md（项目约定）  CLAUDE.md（Claude 入口）
          SessionStart 注入一张 ≤20 行的「流程选择卡」，替代逐轮正则猜意图
能力层   workflow Skill/命令（用户调用）  reference Skill（模型可调用，少量）  principles/（按路径读取）
          安装按 profile：core 默认；ctf / research / ecommerce / media / data 为可选包
保障层   permissions(deny/ask) → PreToolUse Hook → 测试/CI → audit-rules / audit-skills / doc-facts
证据层   specs/  issues/*.csv  docs/decisions/  .git/taiyi/checkpoint.json  ~/.claude/taiyi/usage.jsonl
```

## 3. 工作流设计（三档）

先按 AGENTS.md 的 RISK 档位选流程，不让所有任务走同一套仪式。

### 3.1 LOW：直接做

改动 → 跑与改动相关的检查 → 交付 diff 和命令输出。不写 Spec，不评分。

### 3.2 MEDIUM：功能 / 行为变更

| 阶段 | 入口 | 产出（只存一处） | 完成条件 | 借鉴 |
|------|------|------------------|----------|------|
| 1 澄清 | `/grill`（新，由 demand-detective 收敛而来） | 决策写进 spec 草稿 | 最多 **8 个问题**，一次只问一个，可回答「按默认」 | matt grilling，加上限 |
| 2 规格 | `/spec-flow` | `specs/SPEC-<feature>.md`；已批准的 spec 不改，变更写 `SPEC-<feature>--<change>.md` 并标 `Status` | 验收条件可执行 | addy delta spec |
| 3 拆票 | `/plan-to-issues`（现有） | `issues/<feature>.csv`，每票为纵向切片，写明 `blocked_by`，不写文件路径 | 每票可独立验收 | matt to-tickets |
| 4 实现 | `/issues-execute`（现有） | 每票一个干净上下文；playbook 步骤写进待办，不做的步骤写 `skip: 原因` | 票内验收命令通过 | pstack playbook |
| 5 验证 | `verify`（项目级 Skill，见 §6.4） | 证据：命令、输出、截图或录屏路径 | 在真实产物上跑通 | pstack create-verification-skill |
| 6 评审 | `qa-reviewer`（改为隔离模式） | 发现列表 | 只传产物和验收条件，不传实现者的结论；最多 3 轮 | addy doubt-driven |
| 7 复盘 | `/evolve`（先分流） | 机械问题 → lint/hook/CI；判断问题 → 规则或决策记录 | 有两次独立证据才写规则 | matt retro + 本仓库门槛 |

### 3.3 HIGH：权限、安全、生产、破坏性操作

在 MEDIUM 的基础上增加：Spec 里写风险和回滚；每阶段人工批准；边界验证（拒绝分支必须测试）；执行前再确认授权。

### 3.4 Bug 专线（`debug` Skill 改写）

1. **复现**：第一阶段结束时必须有一条能稳定变红的命令，否则停下报告缺什么。
2. **隔离 → 假设 → 验证**：每个假设都对应一条命令。
3. **修复 + 回归测试**：同一条命令转绿，回归测试入库。
4. **防复发**：把问题交给 `/evolve` 分流。

### 3.5 交接

`handoff` 统一负责交接，`save-context` 和 `read-context` 在确认后改为它的别名。

- 写入：`.git/taiyi/checkpoint.json`，不进入提交。字段为 `goal`、`done`、`next`、`evidence[]`（只放路径和命令）、`files_sha256`、`created_at`。
- 读取的退出码：`0` 表示检查点有效；`2` 表示没有检查点；`1` 表示检查点损坏或文件哈希不匹配，并给出原因。

## 4. 问题修复清单

编号沿用上一轮的问题清单。「确认」列标 ✋ 的条目需要用户先确认再改。

### 4.1 全局 Hook（Phase 1，HIGH，需先在沙箱验证）

| # | 现状 | 修复 | 验收 | 确认 |
|---|------|------|------|------|
| A1 | `post-edit.sh` 在任何项目都会运行 `npm run lint`、`npx eslint --fix`、`ruff check --fix`，并用 `\|\| true` 吞掉错误 | 改为只检查：只调用本地已安装的工具（`ruff check`、`node_modules/.bin/eslint`），不加 `--fix`，不执行 `npm run`，不用 `npx`。matcher 改为 `Edit\|Write\|MultiEdit`；有问题时通过 PostToolUse 反馈给模型。改为可选组件 `lint-feedback`，默认不装 | 临时项目编辑后文件哈希不变；有 lint 问题时模型能收到；没装 linter 时静默放行并记 WARNING | ✋ 是否本来就想要自动修复 |
| A2 | `on-stop.sh` 在每个项目会话结束时把 `git diff` 写进 `~/.claude/backups/`，没有保留期 | 改为可选组件 `session-backup`，默认不装；启用时保留 14 天、总量 50MB 以内。安装器备份只保留最近 5 份 | 保留期测试；超过上限时删除最旧的一份（只限该目录） | ✋ |
| A3 | `validate-command.sh` 是黑名单，`rm -fr` / `rm -r -f` 可能绕过，没覆盖 git 危险操作，还会回显完整命令 | 主防线改为 §5 的权限规则；脚本保留为第二层，参数归一化后再匹配，回显截断到 80 字符；为绕过写法加失败夹具 | `rm -fr /`、`rm -r -f ~`、`git -C x push -f` 的夹具被拦截 | |
| A4 | `port-check-hook.py` 在每条 Bash 命令前都启动一次 Python | 合进 `validate-command.sh`：命令含 `docker\|compose\|podman` 时才调用 Python；hooks.json 里删掉这一项 | 普通 Bash 命令不再启动 Python（计时对比） | |
| A5 | `pre-compact.sh` 只打印一句提示 | 从默认 hooks 移除；如需要，改为提示运行 `handoff` | hooks.json 不再含 PreCompact | |
| A6 | 正则意图路由在本会话误判多次：「改进方案」判成 review，「输出方案」判成 debug | 见 §4.3 | 误判用例全部加入夹具 | |
| A7 | `tools/cc-patcher.sh` 也会合并 hooks，`scripts/hooks-config.json` 是第二份 hook 配置 | 删掉 cc-patcher 的 hooks 安装功能（主题功能保留）；`hooks-config.json` 改名为 `.example` 或删除 | 只有 install-global.py 会写 settings | ✋ 删除 |

### 4.2 加载面（Phase 2，MEDIUM）

| # | 修复 | 验收 |
|---|------|------|
| B2 | `audit-skills.py` 放开 Claude Code 官方字段：`disable-model-invocation`、`user-invocable`、`argument-hint`、`model`、`allowed-tools`，未知字段仍报错；把 ctf 系列写在 metadata 里不生效的 `user-invocable` 移回顶层，或者删掉 | 新增字段测试；ctf 夹具 |
| B1 | 按 §6.1 给 Skill 分类并设置 `disable-model-invocation` | 仓库外新会话 `/context` 的 Skill 描述体积下降（记录前后数值）；`/skill名` 手动调用仍可用 |
| B3 | 32 个命令补全 `description`，并设 `disable-model-invocation: true` | 审计：命令缺少 description 时报错 |
| B4 | hooks 组件只安装运行所需文件（白名单，见 §6.3） | `verify-global-install.py` 核对文件清单 |
| B5 | Agent 也按 profile 安装：`vitest-tester`、`senior-code-architect`、research 类、god-committee 进可选包 | 仓库外 `/agents` 列表变短 |
| B6 | `agents/INDEX.md` 从 788 行改成一行一个 Agent 的表（≤150 行），由脚本根据 frontmatter 生成；超过 500 行的 SKILL.md 把细节拆到 `references/` | audit-rules 检查入口预算；audit-skills 对超过 500 行的 SKILL.md 报 warning |
| C1 | `java-audit/`、`php-audit/` 下没有顶层 SKILL.md，真正的文件在子目录里 | 先用 `/skills` 确认是否可见；不可见就改成平铺目录；audit-skills 对「目录里没有 SKILL.md」报错 |

### 4.3 路由（Phase 3，MEDIUM）

- `intent-detector.sh` 缩为只处理两类：开头是 `@agent-id`，以及显式的 `/命令`。其他情况**不输出建议**，因为模型自身的 Skill 匹配加上流程选择卡已经够用。三套外部工作流都没有逐轮正则路由，addy 还明确说明不加第二层路由。
- 新增 `hooks/session-start.sh`：在 SessionStart 时注入 `config/flow-card.md`（≤20 行），内容是 LOW/MEDIUM/HIGH/Bug 四种情况各用什么入口、何时停下问人。
- HUD 快照保留，但只显示 `@agent` 或命令。
- 验收：
  - 本会话的真实误判（review、debug、orchestrator）加入夹具，预期为「无建议」。
  - 34 条旧路由用例中的 `@agent` 类全部保留。
  - 去掉的启发式类用例写明删除原因。

### 4.4 知识与清理（Phase 4，逐项确认）

| # | 对象 | 处理方式 | 确认 |
|---|------|----------|------|
| C2 | `memory/agent-performance.md`、`optimization-history.md`、`active-worktrees.md` | 先查是否有真实数据。没有就标记为「模板、无数据源」，并给依赖它们的 performance-monitor、auto-optimizer 加说明；有数据就改为从使用日志生成 | ✋ |
| C3 | God Committee（3 个 Agent、`.god/`、god-oversight） | 移入可选包，不默认安装 | ✋ 是否还在用 |
| D1 | 没有任何引用的模块：`graph/`、`recommend/`、`mcp/context-tools/`、`scripts/utils/`、`scripts/context/`、`.claude/PRD.md`，以及 `tools/` 下的三个 Rust 项目 | 打 tag `pre-vnext-archive` 后移到 `archive/`，保留历史，不直接删除 | ✋ 逐项 |
| D2 | `validate-config-old.py` | 确认没有调用方后移到 archive | ✋ |
| D3 | coding-standards、best-practices 各有三份且内容不同 | 合并为 `docs/` 下的一份，其余改为一行指针 | ✋ 以哪份为准 |
| D4 | `docs/hud/` 10 份、`docs/reports/` 19 份、`analysis/` 4 份历史报告 | 移到 `docs/archive/`，INDEX 只保留一行说明 | ✋ |
| D5 | 文档里写死的数量，例如「57 个 Skill」「31 个命令」 | 新增 `scripts/check-doc-facts.py` 校验，或者改为不写数量 | |

### 4.5 落盘与 CI（Phase 0，需授权）

- **分叉**：本地 `2786194` 和远端 `55466fb` 的文件树完全相同，用 `git reset --soft origin/main` 对齐。工作区不变，不需要强推。
- **拆分提交**：按主题拆分，每个提交都能单独回滚。
- **CI 补齐**：加上 `test-all-intents.sh`、`validate-config.py`、三个 `json.tool`、`install-global.py --dry-run --target <tmp>`；Python 矩阵加 3.10 和 3.12。
- **验收**：远端 CI 全绿后，才把「远端 CI 未运行」从报告中移除。

## 5. 权限护栏设计（Phase 1，HIGH）

安装模板为 `config/settings-guardrails.json`。只在安装时显式传 `--with-guardrails` 才合并进 settings，并先备份；
不覆盖用户已有的 permissions 条目，只追加缺少的。

```json
{
  "permissions": {
    "deny": [
      "Bash(git push --force *)", "Bash(git push -f *)",
      "Bash(rm -rf / *)", "Bash(rm -rf ~ *)"
    ],
    "ask": [
      "Bash(git push *)", "Bash(git commit *)",
      "Bash(git reset --hard *)", "Bash(git checkout -- *)", "Bash(git checkout . *)",
      "Bash(git restore *)", "Bash(git clean *)", "Bash(git rebase *)",
      "Bash(rm -rf *)"
    ]
  }
}
```

- 规则写法以本机 Claude Code 2.1.330 文档为准，先在沙箱里实测；与文档不符就改规则，不改测试。
- **必须实测的边界**：
  - `bypassPermissions` 模式下 deny 和 ask 是否仍生效；
  - 复合命令 `a && git push` 是否会被匹配；
  - `git -C dir push` 这种写法是否会被匹配；
  - PowerShell 工具是否需要一套对应规则。
- **回滚**：恢复安装器备份的 `settings.json`，并用 `verify-global-install.py` 核对恢复结果。
- AGENTS.md 里「不提交、不推送」那几行改成一句：「由权限规则保证；规则未覆盖的情况仍需确认」。

## 6. 能力层规范

### 6.1 Skill 分类草案（待使用数据校正）

| 类别 | frontmatter | 成员（草案） |
|------|-------------|--------------|
| **core-reference**（模型可调用，默认安装） | 默认 | debug、code-security-review、frontend-design、data-analysis |
| **core-workflow**（只能用户调用，默认安装） | `disable-model-invocation: true` | spec-first、sdd-riper、sdd-riper-light、neat、reflection、handoff、prime、pr-prep、plan-review、task-decompose、parallel-explore、brainstorming、demand-detective、vision-builder、question-refiner、architecture-copilot、skill-creator、ai-pr-review、observability |
| **pack:ctf** | 用户调用 | ctf-* 共 10 个、wxmini-security-audit、java-audit、php-audit |
| **pack:research** | 用户调用 | deep-research、exa-research、literature-mentor、paper-revision、source-evaluator、hv-analysis-enhanced、llm-wiki |
| **pack:ecommerce/market** | 用户调用 | amazon-analyse、brightdata-research、social-media-research、market-insight |
| **pack:media** | 用户调用 | seedance-prompt、seedance-storyboard |
| **pack:data** | 模型可调用 | pandas、pytorch、schedule-analyzer |
| **pack:frontend** | 模型可调用 | react-best-practices、ui-ux-pro-max、web-artifacts-builder |
| **pack:multi-model** | 用户调用 | collaborating-with-codex、collaborating-with-gemini、claude-agent-sdk、god-oversight |

### 6.2 写法规范（由 audit-skills 强制）

- `description` 不超过 1024 字符，写「做什么 + Use when … + 不用于 …」，不写流程步骤。
- SKILL.md 超过 500 行报 warning，细节放 `references/`，按路径读取。
- 原则类内容不注册为 Skill，放 `principles/*.md`，由工作流 Skill 按需引用。
- Skill 之间调用时写明「调用 X Skill」，不靠模型自己猜。

### 6.3 安装 profile

```
install-global.py --profile core                 # 默认
install-global.py --profile core,ctf,research    # 叠加可选包
install-global.py --with-guardrails              # 合并权限模板（HIGH，单独授权）
install-global.py --components lint-feedback,session-backup   # 可选 Hook
```

- profile 和 Skill 的对应关系存在 `config/profiles.json`，这是唯一来源；INDEX 和 README 的列表由脚本生成。
- hooks 组件改用白名单只装运行所需的文件：`hooks/*`、`scripts/validate/validate-command.sh`、`scripts/port-management/port-check-hook.py`、`scripts/hooks/notify.sh`、`config/keywords.json`、`config/flow-card.md`。

### 6.4 项目级 verify Skill

改造 `skill-creator`，新增一个模式：为目标项目生成 `.claude/skills/verify/SKILL.md`，包含启动、自检、驱动、取证、清理五段和功能地图。
生成后要亲手跑通一遍才算交付；后续维护只输出 `clean`、`changed`、`blocked` 三种结论（参照 pstack）。

## 7. 评估体系

| 层级 | 内容 | 频率 | 成本 |
|------|------|------|------|
| T1 结构 | audit-rules（新增：旧章节引用、入口预算）、audit-skills（新增：官方字段、目录缺 SKILL.md、500 行）、check-doc-facts | 每次 CI | 0 token |
| T1' 不变量 | 每个检查都有 `tests/fixtures/bad-*` 证明它会失败 | 每次 CI | 0 token |
| T2a 描述冲突 | Skill 描述两两相似度 ≥0.75 时报警（只做提示，因为 TF-IDF 与真实路由不一致，这是 addy 已暴露的问题） | 每次 CI | 0 token |
| T2b 真实路由 | `evals/routing/*.json`：每个 core Skill 配 3 条正例、2 条反例，反例写明 `owner`；用无头 `claude -p` 跑，记录首位命中率 | 升级 CLI 或改描述时手动跑 | 少量 token |
| T3 行为 | `evals/behavior/`：每个 core-workflow Skill 配 1 个 fixture 仓库和 `expectations[]`，按转录中的实际动作判分，不看模型自述 | 发布前手动跑 | 中等 |
| 台账 | `evals/LEDGER.md`，只追加：改了什么、前后数据、保留还是否决 | 每次评估 | — |

CLI 版本升级可能让路由命中率下降（addy 记录过 6/6 掉到 1/6），所以 T2b 要绑定 CLI 版本号记录。

## 8. 知识与记忆

- **新条目格式**：`日期 | 结论 | 证据指针（commit/PR/会话） | 状态 active/superseded | 替代者`。旧条目不改写；audit 只检查新增条目有没有日期和证据。
- **决策记录**：重大决策用 `docs/decisions/ADR-*.md`（已有模板）；小决策追加到 `docs/decisions/LOG.md`，每条一行。
- **不做的事**：放 `docs/out-of-scope/<概念>.md`，每份写理由和触发它的证据。`/evolve` 和拆票前先查这里，避免同一个提议反复出现。
- **使用数据**：可选的 PostToolUse Hook 匹配 `Skill|Agent`，追加 `{ts, tool, name, project_hash}` 到 `~/.claude/taiyi/usage.jsonl`，不记录提示词，保留 90 天。`scripts/usage-report.py` 输出各 Skill 和 Agent 的调用次数，作为 §6.1 调整的依据。
- **不建 wiki**，不设「多处必须同步」的规则；需要列表时由脚本从 frontmatter 生成。

## 9. 明确不做

- 不照搬 pstack 的「不要问、不要停」、每个 Agent 默认全权限、每个 Agent 一个 worktree，也不照搬强调式注入标签。
- 不照搬 addy 的「只要有 1% 可能就调用 Skill」和全任务强制走 spec。
- 不照搬 matt 依赖 GitHub issue 的 triage 和 wayfinder、不限问题数的拷问、grep 黑名单护栏，以及 docs/router/README 多处同步。
- 不把离线路由分数当作真实命中率；不因为缺少观测数据就删除 Skill。
- 不安装任何第三方插件，也不执行它们的脚本或 Hook。

## 10. 路线图与验收

| 阶段 | 内容 | 风险 | 前置 | 验收 | 回滚 |
|------|------|------|------|------|------|
| 0 | §4.5 落盘、CI 补齐 | — | **提交/推送授权** | 远端 CI 全绿 | revert 对应提交 |
| 1 | §4.1、§5 Hook 与权限 | HIGH | 本 Spec 第 4.1、5 节获批 | 沙箱中拒绝、确认、放行三类分支都有测试；在别的项目编辑文件后哈希不变 | 恢复 settings 备份；卸载可选组件 |
| 2 | §4.2、§6 加载面 | MEDIUM | 阶段 1 | `/context` 前后对比；手动调用可用；审计无报错 | `--profile` 回到全量 |
| 3 | §4.3 路由与流程选择卡、使用数据 | MEDIUM | 阶段 2 | 误判夹具全部通过；SessionStart 注入 ≤20 行 | 恢复旧的 intent-detector |
| 4 | §4.4 清理 | 逐项 ✋ | 用户确认清单 | 审计无孤立文件和重复文件；tag 可恢复 | 从 tag 恢复 |
| 5 | §3 工作流改造（grill、delta spec、issues、verify、隔离评审、evolve 分流、debug 门槛、handoff 检查点）、§7 T2b/T3 | MEDIUM | 阶段 3 | 用一个真实小需求完整跑一遍 MEDIUM 流程，留下全部工件；T3 基线写进台账 | 各 Skill 单独 revert |

每个阶段交付三样东西：diff、实际运行的命令和输出、未验证项。未运行的检查不写成通过。

## 11. 待用户决定

1. 阶段 0 的提交和推送授权。
2. A1、A2 的自动修复和会话备份是有意要的吗？还是按本方案改成可选组件、默认关闭？
3. 权限模板只放进仓库，还是也合并进你的全局 settings（`--with-guardrails`）？
4. C2、C3、D1–D4 每一项保留还是归档；D3 以哪份为准。
5. §6.1 的分类草案是否认可，比如 debug、frontend-design 是否保留为模型可调用。
6. 新工作流放在太一里，还是拆成一个独立的插件仓库（方便在别的项目单独启用）。
7. 是否启用 §8 的调用记录（只写本机）。

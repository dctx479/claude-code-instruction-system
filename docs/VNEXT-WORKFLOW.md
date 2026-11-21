# 风险分档工作流

本页是流程的单一来源，命令和 Skill 只补充各自的输入输出。借鉴依据见 [三家比较](audits/WORKFLOW-COMPARISON-2026-11-21.md)。

## 选择流程

LOW：直接实施、相关检查、交付 diff。无需额外 Spec 或评分。
MEDIUM：按下表执行，可复用现有已满足条件的产物；不为流程重新写一份。
HIGH：增加风险、回滚和安全边界验证。授权沿用会话记录；只有新增且未获授权的外部或不可逆动作才停下。
用户未授权委派时不自动创建子 Agent。清洁上下文可通过新的会话与检查点实现。

| 阶段 | 入口 | 产物与完成条件 |
|---|---|---|
| 澄清 | `/grill` | 先查仓库和已有回答；最多 8 个必要问题，答案直接进入 spec 草稿 |
| 规格 | `/spec-flow` 或 spec-first | 本地 `specs/SPEC-<feature>.md`；范围、非目标、风险、可执行验收 |
| 拆票 | `/plan-to-issues` | `issues/*.csv`；纵向切片，`blocked_by` 引用本地 ID，每票有验收命令 |
| 实现 | `/issues-execute` | 只选依赖已 DONE 的票；步骤写入待办，跳过写原因；保持票内上下文 |
| 验证 | 项目 verify Skill | 执行真实产物上的命令，保存退出码及输出；不能只靠语法检查 |
| 评审 | qa-reviewer | 仅传产物、diff 和验收条件，不传实现者结论；最多 3 轮，仍失败则列阻塞 |
| 复盘 | `/evolve` | 先区分机械问题/判断问题；机械的做检查，文字规则仍需两次独立证据 |

## 产物纪律

- Spec 描述行为和验收，不把当前实现路径当成需求。必要的接口/数据格式写入契约。
- 批准后的 Spec 保留原文，变更写 `SPEC-<feature>--<change>.md`，注明替代范围与状态。
- 票的 `refs` 可指向实现证据；需求描述不绑定某一实现文件。旧 CSV 可保持兼容，新票用 `blocked_by`。
- 不自动创建 GitHub issue，不自动开 PR。提交、推送沿用用户已有授权。
- 重大决定使用现有 ADR；小决定只追加到 `docs/decisions/LOG.md`。不另建 wiki。
- 机械检查必须有坏样例能失败；行为评估记录 CLI 版本和实际工具动作，未运行记 `NOT_RUN`。

## Bug 与交接

Bug 第一阶段产出稳定失败的命令（输出、退出码、环境）。无法稳定复现则报告证据缺口；可继续诊断，不凭猜测改实现。
修复后同一命令转绿，并运行相关回归。

handoff 使用 `python scripts/checkpoint.py save|verify|show`，由 git 定位每个 worktree 的检查点。
保存 JSON 输入：`goal`、`done[]`、`next[]`、`evidence[]`、`files[]`（仓库相对路径）。哈希由脚本生成，不由模型填写。
读取退出码：0 有效、2 不存在、1 损坏/过期。过期时先核对变化，再继续；不得当作“无检查点”丢失证据。

## 项目 verify Skill

skill-creator 可为目标项目生成 `.claude/skills/verify/SKILL.md`，内容是启动、自检、驱动、取证、清理及实际功能入口。
命令从 manifest/CI 取得，不猜包管理器。临时产物放隔离目录，不覆盖真实用户数据、不发送通知。
交付前运行一次完整流程；结果为 `clean`、`changed`、`blocked`，附真实输出。

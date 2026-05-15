---
name: pr-prep
description: PR 提交前结构化检查仪式，确保测试通过、文档更新、无调试代码、commit 规范、影响范围清晰，让每个 PR 都能一次通过 Review
version: 1.0.0
license: MIT
metadata:
  category: development
  tags: [pr, git, review, checklist, quality, commit, ci]
  requires: [bash]
  optional: [code-reviewer]
trigger:
  - "/pr-prep"
  - "PR 准备"
  - "提交 PR 前"
  - "PR 检查清单"
  - "准备合并"
---

# PR Prep Skill

## 契约定义

### What（输入/输出）

**输入**：
- 当前 git 分支（自动检测）
- 可选：目标分支（默认 main/master）
- 可选：PR 标题草稿

**输出**：
- 结构化检查报告（通过/警告/阻塞）
- 自动修复建议（可执行命令）
- PR 标题 + 描述草稿（Conventional Commits 格式）

### When Done（验收标准）

- 所有 🔴 阻塞项已解决
- 测试套件通过（或有明确的跳过理由）
- commit 历史干净（无 WIP/fixup/temp 提交）
- PR 描述包含：变更摘要 + 测试计划 + 影响范围 + QA Evidence
- 中大型需求已对照任务地图确认交付物和验收证据闭环

### What NOT（边界约束）

- **禁止跳过阻塞项**：🔴 项必须解决，不能以"后续修复"为由跳过
- **禁止自动 push**：检查完成后由用户决定是否推送
- **禁止修改 main/master**：只检查当前功能分支
- **禁止忽略测试失败**：测试失败必须标记为阻塞，不能降级为警告

---

## 五步检查流程

### Step 1: 分支状态检查

```bash
git status                          # 未提交变更
git log main..HEAD --oneline        # 本 PR 的 commit 列表
git diff main...HEAD --stat         # 变更文件统计
```

**检查项**：
- [ ] 无未提交的变更（或已暂存）
- [ ] 无 WIP / fixup / temp / debug 提交
- [ ] commit 消息符合 Conventional Commits（feat/fix/docs/refactor/test/chore）
- [ ] 分支名称有意义（非 patch-1、test-branch 等）

### Step 2: 代码质量检查

```bash
# 搜索调试代码残留
grep -rn "console\.log\|debugger\|TODO\|FIXME\|HACK\|XXX\|print(" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.py" \
  $(git diff main...HEAD --name-only)
```

**检查项**：
- [ ] 无 `console.log` / `debugger` / `print(` 调试语句
- [ ] 无未处理的 TODO/FIXME（或已转为 issue）
- [ ] 无注释掉的大段代码块
- [ ] 无硬编码的密钥、密码、token

### Step 2.5: 工程偏差检查

常见四类 Agent 工程偏差，按类核查：

| 偏差类型 | 典型表现 | 检查方法 |
|---------|---------|---------|
| **静默假设** | 任务边界不清时就开工，按自己的假设填补空白 | 变更描述是否覆盖所有条件？是否有未说明的先验假设？ |
| **过度复杂** | 超出任务范围，加入"应该有用"的功能 | git diff 文件数量是否合理？有无改动无关模块？ |
| **无关改动** | 没先读周边代码，在新文件里重复造轮子 | 是否存在与旧函数功能重复的新函数？import 顺序是否异常？ |
| **没验证就宣布完成** | 测试没跑/结果未确认就说"已修复"/"已完成" | 有无 `npm test` / `pytest` 等验证命令输出？Done Evidence 是否缺失？ |

> 任何一类偏差出现，都应作为 🟡 警告项标记，必要时升级为 🔴 阻塞。

### Step 3: 测试覆盖检查

```bash
# 运行测试（根据项目类型选择）
npm test / pytest / go test ./... / cargo test
```

**检查项**：
- [ ] 所有现有测试通过
- [ ] 新功能有对应测试（或有明确理由说明为何不需要）
- [ ] 修复的 bug 有回归测试
- [ ] 测试覆盖率未下降（如项目有覆盖率要求）

### Step 3.5: 静默完成检测（False Completion）

在测试通过的情况下，进一步检查三类静默失败：

**检查项**：

| 静默完成类型 | 检测方法 | 通过条件 |
|-------------|---------|---------|
| **测试绿≠功能对** | 抽查关键 AC 的测试是否真实覆盖了 Spec 中的条件分支 | 存在 Spec 条款无对应测试 → 🟡 |
| **脚本报告"完成"** | 检查脚本/命令输出是否仅含 "Done"/"Success"，而日志中含 ERROR/Exception | 输出声明成功但日志有异常 → 🔴 |
| **异常藏在日志深处** | 用 `grep -i "error\|exception\|failed\|warn" <logfile>` 检查日志尾部 20 行 | 日志有未处理异常 → 🟡 |

> 静默完成是最高质量的缺陷——看起来完成了，实际埋了雷。发现任何一类都要在报告中显式声明。

**检查命令**：

```bash
# 扫描日志文件是否有深层异常（以项目常见日志路径为例）
grep -i "error\|exception\|failed\|warn" \
  $(find . -name "*.log" -o -name "npm-debug.log*" -o -name "*.stderr" 2>/dev/null) \
  | tail -20
```

### Step 4: 文档同步检查

**检查项**：
- [ ] README 已更新（如有新功能/配置项变更）
- [ ] API 文档已更新（如有接口变更）
- [ ] CHANGELOG 已更新（如项目维护 changelog）
- [ ] 类型定义已更新（TypeScript 项目）
- [ ] 新增/修改第三方 Skill、Agent、Hook、MCP 或浏览器控制能力时，PR 描述包含 `docs/SECURITY.md` 审查结论

### Step 5: PR 描述生成

根据 `git log` 和 `git diff --stat` 自动生成：

```markdown
## Summary
- [变更点 1]
- [变更点 2]

## Changes
- `src/foo.ts`: [具体变更说明]
- `tests/foo.test.ts`: [测试说明]

## Test Plan
- [ ] 单元测试通过
- [ ] 手动测试：[具体步骤]

## QA Evidence
- 已运行：[命令或检查项]
- 已验证：[主路径、边界条件、影响范围]
- 未验证：[未覆盖项及原因]
- 阻塞项：[失败测试、缺失证据或待人工确认项]
- 置信度声明：
  - 整体完成置信度 — [高/中/低]（[判断依据]）
  - 主路径覆盖置信度 — [高/中/低]（[是否遍历了关键路径]）
  - 未验证项风险 — [高/中/低]（[未覆盖项对交付的影响]）

## Impact
- 影响范围：[模块/功能]
- 任务地图覆盖：[已覆盖/未覆盖的任务、依赖、责任 Agent、交付物]
- Breaking Change：是/否
- 需要数据库迁移：是/否
```

---

## 检查报告格式

```
PR Prep Report — feat/my-feature → main
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 阻塞 (必须修复)
  ✗ 测试失败：3 个测试未通过
  ✗ 发现调试代码：src/api.ts:42 console.log("debug")

🟡 警告 (建议修复)
  ⚠ commit 消息不规范：2 个 commit 缺少类型前缀
  ⚠ 未更新 README（新增了配置项 MAX_RETRY）

✅ 通过
  ✓ 无未提交变更
  ✓ 无硬编码密钥
  ✓ 分支名称规范

结论：❌ 未就绪（2 个阻塞项需解决）
```

---

## 快速修复命令

| 问题 | 修复命令 |
|------|---------|
| 修改最后一个 commit 消息 | `git commit --amend -m "fix(auth): ..."` |
| 合并 fixup commit | `git rebase -i main` |
| 删除调试语句 | Grep 定位后手动删除 |
| 暂存未提交变更 | `git stash` 或 `git add && git commit` |

---

## 与其他 Skill 的协作

- **code-reviewer**: PR Prep 完成后可调用进行深度代码审查
- **sdd-riper**: 规范驱动开发流程的最后一步
- **spec-first**: QA 流程的收尾环节

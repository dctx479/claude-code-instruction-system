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
- PR 描述包含：变更摘要 + 测试计划 + 影响范围

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

### Step 4: 文档同步检查

**检查项**：
- [ ] README 已更新（如有新功能/配置项变更）
- [ ] API 文档已更新（如有接口变更）
- [ ] CHANGELOG 已更新（如项目维护 changelog）
- [ ] 类型定义已更新（TypeScript 项目）

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

## Impact
- 影响范围：[模块/功能]
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

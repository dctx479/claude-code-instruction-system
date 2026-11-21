# 三套工作流与本项目的取舍

本轮实际读取 README 和相关 Skill 文件；只对照本次已证实的问题，不把任何一套整体安装成平行治理层。
下面是阅读快照，不声称它们是当下“最火”的排行，也不把作者的效果宣传当成本项目实测。

## 固定来源

| 仓库 | 读取的 commit | 主要阅读文件 |
|------|----------------|--------------|
| addyosmani/agent-skills | `8c99fa36d90068c82d547f7c12a9d67a3e95f4ee` | README、skills/context-engineering、constraint-driven-development、code-review-and-quality、evals/README |
| michael-denyer/pstack-claude | `97d2ba2790822939ee43db0d7856219ea96c450d` | README、plugins/pstack/skills/poteto-mode/SKILL.md、playbooks/bug-fix.md |
| mattpocock/skills | `abeeaf95660ba9e8b7c753eb38f441ca707a8823` | skills/productivity/writing-for-agents、skills/engineering/retro |

仓库地址（固定 commit 下按表内路径可复查）：
`https://github.com/addyosmani/agent-skills`；
`https://github.com/michael-denyer/pstack-claude`；
`https://github.com/mattpocock/skills`。

## 对本项目有价值的部分

| 来源 | 适合借鉴的机制 | 本项目的对应取舍与证据 |
|------|------------------|--------------------------|
| Addy | 区分固定上下文、任务资料与验证；把结构、触发、行为评估分开 | 规则入口瘦身；audit-skills 检查 57 个结构；真实请求路由夹具；真实 Ralph 行为测试。三类证据不互相冒充 |
| pstack | 明确所有权和边界；在真实出错界面验证；把操作做成可重复工具 | Ralph 将纯状态转移与文件/CLI 边界分开，补全局无归属、跨会话和写失败测试；真实 Stop 返回 2 后继续、返回 0 后完成 |
| Matt | 精确的按需指针；复盘优先补自动检查，文字标准用于判断问题 | neat 只查本次影响范围；/evolve 先评估硬保障；指令通过当前 manifest/Spec 和脚本定位，避免全库遍读 |

这些是与本次实现的对照，其中部分在前两阶段已完成；不把阅读之后的描述倒推成全部改造的唯一来源。

## 刻意不照搬的部分

- 不复制 React/npm 示例到以 Markdown、Python、Shell 为主的根目录。
- 不增加一份 CONSTRAINTS.md 与 AGENTS.md、Spec 重复维护同一门禁。
- 不把多 Agent 评审、自动 PR、分支或发布仪式强加给所有小改动。
- 不因第三方 Skill 写了广泛自主权限就扩大当前会话授权；不执行其安装脚本或加载其 Hook。
- 不把手工工况测试、词法路由样本通过率和模型行为泛化率混成一个“准确率”。
- 不因为 11 份会话未观测到 Skill 调用就卸载 57 个 Skill。

## 最终保留的最短流程

目标与验收证据 → 按风险选择设计深度 → 实现 → 对应自动检查/真实行为验证 → 人审阅差异。

新增的长期检查只有规则审计、Skill schema 审计和安装副本验证；
它们替代人工重复核对。没有再叠加一个必须维护的 Wiki、任务状态库或第三方编排框架。

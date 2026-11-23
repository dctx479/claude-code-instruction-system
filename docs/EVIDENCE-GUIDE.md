# 证据台账使用指南

证据给出可核对来源，不保证结论正确。confidence 是作者判断，不能当作校准过的概率；新规则仍要求两次独立事故证据。

## 格式

新记录使用 JSON frontmatter（JSON 是 YAML 兼容子集），或在旧 Markdown 旁创建同名 `.evidence.json` 台账。旧记忆不重写；结构化 YAML 证据需转换到相邻 JSON 台账，运行时不会自行引入 YAML 库。

```markdown
---
{"name":"example","description":"备份需要唯一标识","metadata":{"confidence":0.8,"related":[],"evidence":[{"id":"ev-1","type":"test","source":"tests/test_closure.py:test_backup_identifiers_stay_unique_with_frozen_wall_clock","method":"测试引用核对；执行结果另附","confidence":0.8,"date":"2026-11-23","verified_by":"tool"}]}}
---
记录案例、适用条件和验证方法。
```

sidecar 使用相同顶层 name、description、metadata 字段。JSON Schema 在 `memory/schemas/evidence-v1.json`，标准库校验实现在 `scripts/taiyi/evidence.py`。

5 种类型：test / commit / measurement / observation / documentation。每条要求 id、type、source、method、confidence、date、verified_by。可附 metrics 和 sha256（UTF-8 文本经通用换行规范化后的 SHA-256）。related 是相对 memory 根的记录路径，不是 Shell 命令。

## 查询和解释

```bash
python scripts/taiyi-tool.py evidence trace curated/fix-backup-collision
python scripts/taiyi-tool.py evidence verify curated/fix-backup-collision
python scripts/taiyi-tool.py evidence find --min-confidence 0.8
python scripts/taiyi-tool.py audit
python scripts/taiyi-tool.py --memory memory/curated audit --strict
```

`--root` 定位证据来源仓库，`--memory` 定位知识。全局安装后检查太一证据，root 应指向太一仓库或含相应来源的安装根；不能用任意当前项目的测试证明本仓库记忆。

| 状态 | 含义 |
|---|---|
| reference_valid | 文件/行范围/函数或 git commit 对象存在；未执行测试 |
| invalid | 格式、范围、路径、符号或 commit 不成立 |
| changed | 可选内容哈希变化，需重审 |
| unverifiable | 外部 URL 或观测/测量不能静态证实 |
| legacy | 历史 Markdown 没有结构化台账，保留原貌 |
| cycle / depth_limit / node_limit | 关联链循环、深度超过 12 或节点超过 100，需整理 |

普通 audit 对 invalid/changed/坏关联链返回非零，旧格式列在 legacy。strict 还对旧格式、低置信度和未核实来源返回非零；它是审计模式，不能据此批量把历史记忆改成 UNVERIFIED。

静态验证不会执行来源文件中任意命令。实际测试结果必须来自独立运行输出，写入相应报告；一个存在的测试函数不等于一次已通过的测试，更不等于两次独立事故。

`/evidence-trace` 按需加载相关来源，`/rule-audit` 和 `/evolve` 已接入查询建议。与既有规则演化、记忆查重和人工审核流程共同使用。

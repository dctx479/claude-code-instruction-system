---
name: wxmini-security-audit
description: 微信小程序全自动安全审计 Skill。使用 Agent Teams 编排 Agent，分阶段完成从反编译到报告生成的全流程静态安全分析。覆盖敏感信息泄露、API接口提取、加解密算法分析、漏洞分析四大维度。采用"脚本预扫描 + LLM智能分析"双层架构，脚本保证覆盖率，LLM保证准确率。
metadata:
  version: 1.0.0
  tags:
  - security
  - wechat
  - miniprogram
  - audit
  - static-analysis
  platform: windows
  tools_required:
  - unveilr.exe (内置于 tools/ 目录)
  - Python 3.x (系统环境，仅使用标准库)
  - grep / glob / view (CLI 内置)
  - create / edit (CLI 内置)
  trigger:
  - /wxmini-security-audit
  - 微信小程序安全审计
  - 小程序漏洞分析
  - wxapkg 审计
  - 小程序安全检查
disable-model-invocation: true
---

# Skill: wxmini-security-audit — 微信小程序安全审计

## 核心原则（所有 Agent 必须遵守）

1. **纯静态分析，严禁发送任何网络请求**
   - 禁止使用 curl、wget、fetch、Invoke-WebRequest 等工具发送任何 HTTP/HTTPS 请求
   - 禁止验证发现的密钥、Token、API 接口是否有效
   - 禁止连接任何数据库、Redis、消息队列等远程服务
   - 禁止下载或更新任何远程资源（npm 包信息、漏洞数据库等）
   - 所有分析必须且只能基于本地文件内容完成

2. **不生成任何攻击性代码**
   - 不生成 PoC（Proof of Concept）漏洞利用脚本
   - 不生成自动化攻击工具
   - 分析结果仅供安全审计和防御参考

3. **最小权限原则**
   - 仅读取 `{target_dir}` 下的源码文件
   - 仅在 `{output_dir}` 下写入分析结果文件
   - 不修改、不删除任何原有文件

4. **完整流程优先**
   - 必须完整执行 Phase 0 → Phase 1 → Phase 1.5 → Phase 2（全部4个Agent） → Phase 2.5（条件触发） → Phase 3 的标准分析流程
   - 不允许跳过、合并或改变任何阶段的执行顺序

## 编排铁律（Orchestrator 禁令，硬性约束）

> ⛔ 以下规则是不可违反的底线。违反任意一条等同于审计失败。

1. **严禁代劳** — Orchestrator 自身**严禁**直接创建任何 `*_analysis.json`、`*_report.json`、`security_report.md` 等输出文件。所有分析输出**必须且只能**由对应的子 Agent 生成。Orchestrator 唯一允许写入的文件是 Phase 1.5 中通过执行 Python 脚本间接生成的 `raw_*.json`。

2. **严禁跳阶段** — 每个 Phase 必须按序执行，不得以"已知结果"、"时间不够"、"Agent 太慢"为由跳过任何 Phase。Phase 2.5 的触发条件是 `custom_requests.has_custom_requests == true`，一旦满足，**必须启动 agent-07**，不得自行替代。

3. **严禁截留信息** — Orchestrator 在执行过程中获取的所有外部数据（Burp MCP 抓包数据、用户补充信息、其他 MCP 工具返回的数据）**必须完整传入**对应 Agent 的 prompt 中，不得仅留在 Orchestrator 上下文中。特别是 Phase 2.5 启动 agent-07 时，Burp 数据必须作为 prompt 的一部分传给 Agent。

4. **严禁提前终止** — 在等待 Phase 2 四个 Agent 返回期间，Orchestrator **禁止**分析代码、处理用户需求、生成任何结果。唯一允许的操作是等待和检查 Agent 完成状态。

5. **报告完整性** — Reporter Agent（agent-06）生成的输出中，**所有敏感信息发现和所有 API 接口必须被完整记录，严禁丢失任何数据**。主报告（`security_report.md`）中列出关键/高危发现，全量数据分别输出到独立文档（`api_endpoints_full.md` 和 `secrets_full.md`）。漏洞和加解密分析仍在主报告中完整展示。

## 描述
微信小程序全自动安全审计 Skill。使用 Agent Teams 编排多个 Agent，分阶段完成从反编译到报告生成的全流程静态安全分析。

**架构亮点**：
- **脚本 + LLM 双层架构**：Python 脚本通过正则保证 100% 规则覆盖率，LLM Agent 基于脚本结果做智能分析（误报过滤、BaseURL 关联、风险评级）
- **接口-文件映射**：按 JS 文件分组输出接口，LLM 可批量分析同一文件的所有发现
- **用户需求前置解析**：Phase 0 即解析用户特殊需求，Phase 2 完成后条件触发 CustomAnalyzer
- **支持外部工具集成**：可接收 Burp 等抓包工具的信息进行关联分析

覆盖维度：敏感信息泄露、API接口提取、加解密算法分析、漏洞分析。

## 触发方式
当用户请求分析微信小程序时触发。

- "帮我分析这个小程序 D:\wechat\miniapp\wxapkg_files"
- "审计这个小程序 C:\miniprogram\target"
- "分析一下这个微信小程序 {目录路径}"
- "帮我分析这个小程序 {目录路径}，重点看一下 /api/user/login 接口"
- "审计这个小程序 {目录路径}，Burp 抓包发现 /api/pay 接口的 amount 参数可以篡改"
- "分析这个小程序 {目录路径}，关注支付安全和越权风险"

从用户输入中提取 `{target_dir}`（小程序目录路径）。

## 变量定义

| 变量 | 含义 | 说明 |
|------|------|------|
| `{target_dir}` | 用户提供的小程序目录路径 | 从用户输入中提取，仅用于读取源码 |
| `{output_dir}` | 审计结果输出目录 | 在用户当前工作区下自动创建，所有分析输出文件写入此目录 |
| `{skill_dir}` | 本 Skill 的安装目录 | 即 `skill.md` 所在的目录路径，由编排器在运行时自动解析 |

**`{output_dir}` 创建规则**：在用户当前工作目录（CWD）下新建目录 `wxaudit-output`，即 `{output_dir}` = `{CWD}\wxaudit-output`。如果该目录已存在，则在名称后追加时间戳（如 `wxaudit-output-20240101-120000`）。所有 Agent 的分析结果文件、报告文件均输出到此目录，**不得写入 `{target_dir}`（源码目录）**。

**`{skill_dir}` 解析规则**：编排器（主 Agent）读取本 `skill.md` 时，取该文件所在目录的绝对路径作为 `{skill_dir}`。后续启动子 Agent 时，须将提示词中的 `{skill_dir}` 替换为实际路径。

## 工具依赖
- `unveilr.exe` — 位于 `{skill_dir}\tools\unveilr.exe`，用于反编译 wxapkg
- `endpoint_extractor.py` — 位于 `{skill_dir}\tools\scripts\endpoint_extractor.py`，用于正则提取接口
- `secret_scanner.py` — 位于 `{skill_dir}\tools\scripts\secret_scanner.py`，用于正则提取敏感信息
- `grep` / `glob` / `view` — 用于文件搜索和内容分析
- `create` / `edit` — 用于生成报告和JSON文件

## Agent 文件索引

所有 Agent 提示词文件位于 `{skill_dir}\agents\` 目录：

| Agent | 文件 | 阶段 | 职责 |
|-------|------|------|------|
| Decompiler | `agent-01-decompiler.md` | Phase 1 | 反编译与文件资产清单（支持多子目录） |
| SecretScanner | `agent-02-secret-scanner.md` | Phase 2 | 基于脚本结果的敏感信息智能分析 |
| EndpointMiner | `agent-03-endpoint-miner.md` | Phase 2 | 基于脚本结果的接口智能关联分析 |
| CryptoAnalyzer | `agent-04-crypto-analyzer.md` | Phase 2 | 加解密算法分析（纯LLM） |
| VulnAnalyzer | `agent-05-vuln-analyzer.md` | Phase 2 | 漏洞分析（七大维度，纯LLM） |
| Reporter | `agent-06-reporter.md` | Phase 3 | 报告生成 |
| CustomAnalyzer | `agent-07-custom-analyzer.md` | Phase 2.5 | 用户自定义需求深度分析（条件触发） |


## Extended procedure

Read [references/extended-guide.md](references/extended-guide.md) for the remaining modes, examples, and checks. Resource paths in that guide are relative to this skill directory.

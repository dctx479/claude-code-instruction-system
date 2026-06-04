# Skills 系统完整目录

> Skills 是自动激活的能力扩展单元。设计原则见 `CLAUDE.md` 第四节。

---

## Skills vs Agents vs Commands

| 类型 | 职责 | 触发方式 | 示例 |
|------|------|----------|------|
| **Skills** | 知识包，能力增强 | 自动发现 | PyTorch, pandas, SHAP |
| **Agents** | 执行单元，任务处理 | Orchestrator 调度 | spec-writer, qa-reviewer |
| **Commands** | 显式用户操作 | 手动调用 | /commit, /review |

---

## 核心研究 Skills

| Skill | 描述 | 触发词 |
|-------|------|--------|
| **deep-research** | Lead Agent + Subagent 并行调研，支持创新组合发现与结构化报告 | `deep-research <主题>` |
| **question-refiner** | 研究查询精炼器，结构化模糊查询并补足创新 brief | `澄清研究方向`, `结构化研究问题` |
| **stock-research** *(planned)* | 8阶段股票投资尽调框架，模拟巴菲特式理性投资分析 | `/stock-research <股票代码>`, `分析股票` |
| **market-insight** | 三段式用户画像与产品机会分析 | `/insight <产品描述>` |
| **exa-research** | 企业与市场研究，基于 Exa 搜索引擎 | `研究竞争对手`, `分析行业` |
| **brightdata-research** | 电商平台深度调研，反反爬虫支持 | `电商调研`, `畅销排行` |
| **amazon-analyse** | 亚马逊竞品 Listing 全维度穿透分析，基于 Sorftime MCP | `/amazon-analyse <ASIN> <市场>` |
| **social-media-research** | 跨平台社媒研究，12+ 平台覆盖 | `舆情监控`, `KOL 分析` |
| **literature-mentor** | 文献深度解读，交互/报告双模式 | `解读这篇论文`, `生成精读报告` |
| **paper-revision** | 论文风格修改，技术准确性保持，英文 Nature 标准润色 | `修改论文风格`, `英文润色`, `nature-polish` |

---

## AI 视频创作 Skills

| Skill | 描述 | 触发词 | 适用场景 |
|-------|------|--------|----------|
| **seedance-prompt** | Seedance 2.0 分镜提示词生成 | `生成视频提示词`, `分镜提示词` | 15s 内短片分镜 |
| **seedance-storyboard** | 小说/故事转多集视频剧本 | `写剧本`, `生成分镜`, `/seedance` | 短剧/电影完整制作 |
| **seedance-prompt-ads** *(planned)* | 视频广告 Seedance 提示词生成 | `视频广告`, `品牌TVC`, `带货广告` | 品牌广告/电商带货 |

**seedance-prompt-ads 说明**: 上传产品素材和广告诉求，生成结构化视频提示词。支持两种模式:
- **品牌 TVC 广告**: 16:9 横屏，专业电影感，情感共鸣叙事
- **带货广告**: 9:16 竖屏，UGC 真实感，核心信任建立 + 紧迫感

开源地址: [make-prompt-seedance2](https://github.com/liangdabiao/make-prompt-seedance2)

---

## 开发工作流 Skills

会话生命周期：`/prime` → 执行 → `/reflection` → `/handoff` → `/neat` → /compact

| Skill | 描述 | 触发词 |
|-------|------|--------|
| **prime** | 会话预热仪式，读取 git 状态 + 检索记忆 + 输出状态摘要 | `/prime`, `新会话开始`, `上次做到哪了` |
| **debug** | 结构化调试五步工作流（复现→隔离→假设→验证→防复发） | `/debug`, `帮我调试`, `这个报错怎么回事` |
| **handoff** | 上下文交接仪式，/compact 前将进度/决策/下一步写入 memory/handoff.md | `/handoff`, `准备 compact`, `交接一下` |
| **neat** | 任务收尾洁癖审查，五步法同步 docs/CLAUDE.md/memory 三层知识 | `/neat`, `整理一下`, `收尾` |
| **reflection** | 任务复盘提炼器，萃取 3-5 条可复用经验，两步链 Ingest 写入知识库 | `/reflection`, `复盘一下`, `总结经验` |
| **skill-creator** | Skill 元创建器，按契约（五要素：What/How/When Done/What NOT/Extractable）生成高质量 SKILL.md，含 Skill→SaaS 可提取性评估 | `/skill-creator`, `创建一个 Skill`, `封装成 Skill` |
| **spec-first** | 完整 QA 工作流编排器，串联 spec-writer→开发→qa-reviewer→qa-fixer | `/spec-first`, `先写规范再开发`, `需要质量保障` |
| **pr-prep** | PR 提交前五步检查仪式，确保每个 PR 一次通过 Review | `/pr-prep`, `准备提 PR`, `PR 检查清单` |
| **task-decompose** | 任务分解器，三层拆解（Epic→Story→Task）+ 依赖图 + 并行化建议 | `/task-decompose`, `任务拆解`, `需求分解` |
| **sdd-riper** | Spec-Driven Development + RIPER 五阶段流程，中大型需求（>500行/3+文件） | `/riper`, `/sdd-riper`, `中大型需求开发` |
| **sdd-riper-light** | SDD-RIPER 轻量版，简单任务（<500行/<3文件），快速迭代 | `/riper-light`, `/sdd-light`, `简单 bug 修复` |
| **claude-agent-sdk** | 将任何 Skill 封装为 Claude Agent SDK Web 应用，五步法 + 代码模板 + 安全部署 | `用 claude-agent-sdk 建立 webapp`, `把 skill 转为 web 应用` |

---

## Agent 部署安全

| 文档 | 描述 | 触发条件 |
|-----|------|----------|
| **agent-deployment/SECURITY-GUIDE.md** | 五层防御方案（L1权限隔离→L5 LlamaFirewall）+ API 网关 + 成本控制 + 上线检查清单 | 对外部署 Agent、开放 Web 服务 |
| **AGENT-FRAMEWORK-DECISION.md** | 四大框架（Claude Code/LangGraph/CrewAI/DeerFlow）对比 + 决策树 + Skill→SaaS 路径图 + 编排映射 | 框架选型、技术方案对比 |

---

## 前端设计与开发 Skills

| Skill | 描述 | 触发词 |
|-------|------|--------|
| **frontend-design** | 布局/交互/配色/可访问性审查 | `设计页面`, `审查UI` |
| **ui-ux-pro-max** | 57+风格/97配色/57字体知识库 | `推荐UI风格`, `配色方案` |
| **react-best-practices** | Vercel 官方 React 性能优化 45+ 规则 | `优化React`, `消除waterfall` |
| **web-artifacts-builder** | React+TypeScript+Tailwind 单页应用 | `构建Web应用`, `创建Artifact` |

---

## 安全审计 Skills

| Skill | 描述 | 触发词 |
|-------|------|--------|
| **code-security-review** | 通用代码安全审计，三阶段 audit-filter-report，19 条误报排除规则 | `代码安全审计`, `安全漏洞扫描`, `security review` |
| **php-audit** | PHP 白盒代码审计集合（30+ 子 Skill），证据契约驱动，支持 Laravel/ThinkPHP 等框架 | `PHP 安全审计`, `PHP 代码审计` |
| **java-audit** | Java 白盒代码审计集合，route-mapper + route-tracer + pipeline 架构 | `Java 安全审计`, `Spring 反序列化` |
| **wxmini-security-audit** | 微信小程序全自动安全审计，7 Agent 协作 + 脚本/LLM 双层架构 | `小程序安全审计`, `wxapkg 审计`, `微信小程序漏洞` |

---

## CTF Skills

| Skill | 描述 | 触发词 |
|-------|------|--------|
| **ctf-crypto** | 密码学攻击：RSA/AES/ECC/格密码/PRNG/签名伪造 | CTF 密码学题目 |
| **ctf-forensics** | 数字取证：磁盘镜像/内存转储/网络抓包/隐写术 | CTF 取证题目 |
| **ctf-pwn** | 二进制漏洞利用：栈溢出/堆利用/ROP/内核提权 | CTF PWN 题目 |
| **ctf-reverse** | 逆向工程：二进制分析/反调试绕过/自定义VM | CTF 逆向题目 |
| **ctf-web** | Web 安全：XSS/SQLi/SSTI/SSRF/JWT/原型链污染 | CTF Web 安全题目 |
| **ctf-osint** | 开源情报：社交媒体/地理定位/DNS/反向图片搜索 | CTF OSINT 题目 |
| **ctf-malware** | 恶意软件分析：混淆脚本/C2流量/PE分析 | CTF 恶意软件分析题目 |
| **ctf-misc** | 杂项：编码解谜/Python沙箱逃逸/Z3约束求解 | CTF 杂项题目 |
| **ctf-ai-ml** | AI/ML 攻击：对抗样本/模型窃取/提示注入/LLM 越狱 | CTF AI/ML 题目 |
| **ctf-writeup** | 标准化 CTF 解题报告生成器，赛事提交格式 | CTF 解题报告, `生成解题报告` |

来源: [ljagiello/ctf-skills](https://github.com/ljagiello/ctf-skills) (1627⭐)

---

## claude-scientific-skills（140+ 科研技能）

来源: [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills)

| 类别 | 技能 |
|------|------|
| ML & AI | 机器学习算法、模型训练、超参数优化 |
| Deep Learning | CNN、RNN、Transformer、GAN |
| Reinforcement Learning | DQN、PPO、SAC、MADDPG |
| Time Series | ARIMA、Prophet、LSTM |
| Interpretability | SHAP、LIME、Captum、Fairlearn |
| Data Analysis | pandas、numpy、matplotlib、plotly |
| Python Packages (55+) | PyTorch、scikit-learn、TensorFlow |

---

## Skill 组合模式

| 组合 | 用途 |
|------|------|
| 社媒 + 深度调研 | 社媒调研智能体 |
| 社媒 + 市场洞察 | 消费者画像 |
| 电商 + 企业研究 | 全链路竞争分析 |
| amazon-analyse + market-insight | 亚马逊选品决策闭环（竞品数据 → 用户需求洞察） |
| brightdata-research + amazon-analyse | 双渠道电商情报（平台爬取 + MCP 官方数据） |
| stock-research + data-analysis | 指数成分股批量分析（恒生科技/科创50/创业板50） |
| stock-research + exa-research | 股票基本面 + 行业竞争格局深度分析 |
| deep-research + Tavily MCP | 深度调研增强（域名限定+时间过滤+批量内容提取） |
| literature-mentor + paper-writing-assistant | 文献综述写作 |
| literature-mentor + deep-research | 文献拆解 + 创新组合发现 |
| literature-mentor + experiment-logger | 实验设计与执行 |
| seedance-prompt + seedance-storyboard | AI 短剧全流程制作 |
| frontend-design + ui-ux-pro-max | 专业级 UI 设计系统 |
| react-best-practices + web-artifacts-builder | 高性能 Web 应用 |
| prime → 执行 → reflection → neat | 完整会话生命周期（知识不丢失） |
| handoff → neat → /compact | 上下文压缩前的安全收尾三步 |
| task-decompose → sdd-riper → pr-prep | 需求到 PR 的完整开发闭环 |
| spec-first + code-security-review | 规范驱动开发 + 安全审计双保险 |
| ctf-reverse + ctf-pwn | 逆向分析 + 漏洞利用联合攻击 |
| ctf-web + ctf-crypto | Web 漏洞 + 密码学联合 CTF 解题 |

---

## 渐进式披露

```
会话启动: 加载所有 Skills metadata (~100 tokens/skill)
任务匹配: Claude 分析请求，匹配相关 Skills
按需加载: 仅加载激活 Skills 完整内容 (~2K tokens/skill)
节省率: 98%（INDEX.md ~600 tokens vs 所有 Skill ~46K tokens）
```

详细文档: `.claude/skills/README.md`, `.claude/skills/INDEX.md`
MCP 集成配置: `.claude/integrations/`

---

## 社区 Skills（第三方）

通过 `npx skills add {user}/{skill} -g -y` 一键安装:

| Skill | 描述 | 安装命令 |
|-------|------|---------|
| **x-ai-topic-selector** | 推特信息流选题助手，Chrome CDP 抓取 + AI 评分，支持扫描/书签两种模式 | `npx skills add vigorX777/x-ai-topic-selector -g -y` |
| **knowledge-work-plugins** | Anthropic 官方 Cowork 插件库，20+ 职业角色（销售/法务/HR/数据等），纯 Markdown+JSON | `claude plugin marketplace add anthropics/knowledge-work-plugins` |
| **ssh-skill** | 企业级 SSH 管理，长连接守护进程 + 超大文件传输 + Paramiko 密码认证 + 隧道管理 | `npx skills add badseal/ssh-skill -g -y` |
| **system-cleaner** | 桌面磁盘清理，绿/黄/红安全分级 + 交互式 HTML 报告，Mac/Windows 均支持 | `npx skills add KKKKhazix/khazix-skills -g -y` |
| **flue-framework** | 轻量 TypeScript Agent 脚手架（createAgent/defineTool/routing/SSE 流式） | `npx skills add liangdabiao/flue-framework-skill -g -y` |

**knowledge-work-plugins 说明**: Anthropic 官方开源，17K+ Stars。每个插件含 Skills（自动调用）+ Commands（斜杠命令）+ Connectors（MCP 协议对接外部工具）。覆盖 engineering、sales、product、data、marketing、legal、finance、HR、design、bio-research 等角色。安装后使用 `claude plugin install <name>@knowledge-work-plugins` 选择性安装具体角色。

**ssh-skill 说明**: 半年实战验证。调用原生 OpenSSH，配置格式兼容终端直接使用（`ssh server1`）。Windows 原生 SSH 适配（自动定位 `%SystemRoot%\System32\OpenSSH\ssh.exe`）。支持 Passphrase 密钥通过 SSH Agent 无感使用。

**system-cleaner 说明**: 全程只读扫描，在浏览器中打开交互式 HTML 报告。绿灯（纯缓存/可安全删除）支持一键操作；黄灯（需人工判断）仅提供"在 Finder 中打开"；红灯（系统文件）仅展示说明。所有删除操作都有二次确认弹窗。

**flue-framework 说明**: 轻量替代 Claude Agent SDK 的 TypeScript 方案。SSE 流式输出内置，适合前端团队主导的 Agent 项目。详细框架对比见 `docs/AGENT-FRAMEWORK-DECISION.md`。

---

## 推荐外部工具（非 Skill）

> 以下工具不是 Skill 架构，而是 Claude Code 的增强工具/插件/MCP 服务器，提升效率和可观测性。
> 检测到适用场景时应主动推荐安装。完整安装指南: `docs/TOOLS-ECOSYSTEM-GUIDE.md`

| 工具 | 类别 | 核心价值 | 快速安装 | 主动推荐触发 |
|------|------|---------|---------|-------------|
| **Context Mode** | Token 优化 | MCP 输出沙箱压缩，~98% 节省 | `claude mcp add context-mode -- npx -y context-mode` | token >100K 且未安装 |
| **CodeGraph** | Token 优化 | 代码知识图谱，~92% tool call 减少 | `npx @colbymchenry/codegraph` | 代码探索 >20 次且未安装 |
| **RTK** | Token 优化 | Rust CLI 代理，Bash 输出压缩 60-90% | `brew install rtk` / [Releases](https://github.com/rtk-ai/rtk/releases) | 配合前两者使用 |
| **claude-tap** | 可观测性 | API 流量检查 + token 用量明细 + 系统提示词查看 | `pip install claude-tap` | 用户询问 token 成本/调试 Agent |

---

## Skill ↔ Agent 职责矩阵

> **原则**: Skill = 方法论/知识库（What to do），Agent = 执行角色（Who does it）。
> Skill 提供流程和标准，Agent 以特定角色身份执行任务。

### 核心职责边界

| 领域 | Skill（方法论） | Agent（执行者） | 协作模式 |
|------|----------------|-----------------|---------|
| **调试** | `debug`（五步工作流） | `debugger`（调试角色） | Skill 定义流程，Agent 执行诊断 |
| **安全审计** | `code-security-review`（审计规则） | `security-analyst` + `security-audit` | Skill 提供规则库，Agent 执行扫描和报告 |
| **QA 工作流** | `spec-first`（编排流程） | `spec-writer` + `qa-reviewer` + `qa-fixer` | Skill 串联三个 Agent 的工作 |
| **需求开发** | `sdd-riper`（五阶段流程） | `sdd-riper-orchestrator` | Skill 定义状态机，Agent 驱动执行 |
| **代码审查** | `pr-prep`（检查清单） | `code-reviewer` | Skill 做预检，Agent 做深度审查 |
| **前端设计** | `frontend-design`（设计规范） | —（无对应 Agent） | 纯 Skill，知识库驱动 |
| **文献研究** | `literature-mentor`（精读流程） | `literature-manager`（导入分类） | Skill 负责解读，Agent 负责管理 |
| **会话生命周期** | `prime` → `handoff` → `neat` | —（无对应 Agent） | 纯 Skill，系统仪式 |

### 路由决策规则

1. **Intent 检测结果是 Agent** → 加载 Agent 角色执行（CLAUDE.md §0）
2. **任务匹配到 Skill** → 加载 Skill 方法论指导
3. **两者都匹配** → Agent 角色 + Skill 方法论同时激活（如 debugger Agent + debug Skill）
4. **冲突时** → Agent 优先（执行身份），Skill 提供补充知识

---

## 内建 Skill 集成建议

> Claude Code 自带的内建 Skills 中，以下 7 个尚未被项目工作流引用，建议按下表集成。

| 内建 Skill | 能力描述 | 建议集成点 | 集成方式 |
|------------|---------|-----------|---------|
| **karpathy-guidelines** | LLM 编码防错准则，减少常见 AI 编码错误 | `code-reviewer` Agent、QA 流程 | Agent 执行审查时自动参考 |
| **brainstorming** | 创意头脑风暴，将模糊想法转化为经过验证的设计 | `vision-builder` Skill 前置 | 需求模糊时先 brainstorming → 再 vision-builder |
| **documentation** | 文档生成工作流（API/架构/README） | `pr-prep` Skill Step 4 | PR 文档检查时触发文档生成 |
| **playwright-skill** | Playwright E2E 测试框架集成 | `automated-testing` Agent | 前端项目测试时自动激活 |
| **analyze-project** | 分析 Antigravity 会话的根本原因 | `prime` Skill | 新项目初始会话时使用 |
| **context-compression** | 压缩会话历史以管理 token | `handoff` → `neat` 生命周期 | 上下文 >250K 时自动建议 |
| **claude-code-guide** | Claude Code 配置和使用参考 | `tech-mentor` Agent | 用户询问 Claude Code 使用时引用 |

### 推荐的增强工作流

```
# 需求阶段增强
brainstorming → vision-builder → task-decompose

# 代码审查增强
karpathy-guidelines + code-reviewer Agent + pr-prep Skill

# 测试增强
automated-testing Agent + playwright-skill（前端）

# 上下文管理增强
handoff → neat → context-compression → /compact
```

---

## 场景速查表

### 按业务阶段

| 阶段 | 可用 Skill | 说明 |
|------|-----------|------|
| **需求** | vision-builder, question-refiner | 从模糊需求到清晰目标 |
| **调研** | deep-research, exa-research, brightdata-research, social-media-research, literature-mentor | 信息收集和分析 |
| **方案** | plan-review, parallel-explore, spec-writer (Agent) | 方案设计和评审 |
| **开发** | react-best-practices, web-artifacts-builder, collaborating-with-codex, collaborating-with-gemini | 代码实现 |
| **测试** | QA 系统 (qa-reviewer + qa-fixer Agent) | 质量验证 |
| **PR 提交** | pr-prep | 提交前五步检查 |
| **Agent 封装** | claude-agent-sdk | Skill → Web SaaS 转换 |
| **复盘** | reflection | 萃取可复用经验 |
| **收尾** | neat | 三层知识同步 |
| **Skill 化** | skill-creator | 高频流程封装 |
| **会话预热** | prime | 建立项目上下文 |
| **上下文交接** | handoff | /compact 前保存进度 |

### 现象驱动路由

| 我观察到… | 推荐 Skill | 说明 |
|-----------|-----------|------|
| 文档和代码对不上，AI 行为越来越奇怪 | **neat** | 三层知识失同步 |
| 刚完成一个复杂任务，想把经验留下来 | **reflection** | 萃取经验 → 写入 lessons-learned |
| 同一个流程已经做了 3 次以上 | **skill-creator** | 高频流程值得封装 |
| 研究问题太模糊，不知道从哪里搜 | **question-refiner** | 先精炼查询再调研 |
| 需要对比多个技术方案 | **parallel-explore** | 独立 worktree 标准化评估 |
| 需求描述很模糊 | **vision-builder** | 引导式提问输出 VISION.md |
| 计划写好了想检查漏洞 | **plan-review** | 10 维度评估 |
| 上下文快满了（>250K tokens） | **handoff** → **neat** → /compact | 安全收尾三步 |
| 新会话开始不知道上次做到哪了 | **prime** | git 状态 + 记忆检索 |
| 遇到报错/异常行为 | **debug** | 五步系统排查 |
| 新功能开发想确保质量 | **spec-first** | 规范驱动 QA 闭环 |
| 需求模糊不知道怎么拆任务 | **task-decompose** | 三层拆解 + 依赖图 |
| 功能写完准备提 PR | **pr-prep** | 五步检查仪式 |
| 想把 Skill 对外开放成 Web 服务 | **claude-agent-sdk** | 五步法封装 |
| Token 烧太快 / 成本太高 | **Context Mode** + **CodeGraph** | 安装后自动压缩，详见 `docs/TOOLS-ECOSYSTEM-GUIDE.md` |
| 不清楚 API 调用细节 / 想调试 Agent | **claude-tap** | `pip install claude-tap && claude-tap --tap-live` |
| 需要连接多台远程服务器 | **ssh-skill** | 长连接 + 统一 SSH 配置 |

---

## 更新日志

### 2026-06-04
- 新增 4 个社区 Skills（knowledge-work-plugins / ssh-skill / system-cleaner / flue-framework）
- 新增"推荐外部工具（非 Skill）"节（Context Mode / CodeGraph / RTK / claude-tap）
- 场景速查表追加 3 个现象驱动路由（Token 成本 / 调试 Agent / 远程服务器）
- 创建 `docs/TOOLS-ECOSYSTEM-GUIDE.md` 外部工具生态集中指南

### 2026-05-29
- **P1**: INDEX.md 从 1007 行精简至 116 行（减少 89%），回归纯索引定位
- **P2**: 确立三文件职责——INDEX.md=轻量索引、SKILLS-CATALOG.md=详细文档、README.md=设计规范
- **P3**: 新增 Skill↔Agent 职责矩阵，明确方法论 vs 执行角色的边界
- **P4**: 新增 7 个内建 Skill 集成建议（karpathy-guidelines/brainstorming/documentation/playwright-skill/analyze-project/context-compression/claude-code-guide）
- Changelog 和场景速查表从 INDEX.md 迁移至本文件

### 2026-04-30
- 新增 task-decompose、pr-prep Skills
- 新增 handoff、spec-first Skills
- sdd-riper/sdd-riper-light 升级至 v1.1
- 新增 prime、debug、reflection、skill-creator Skills
- 新增 observability 升级至 v1.1

### 2026-04-21
- 新增代码安全审计类：code-security-review、php-audit、java-audit、wxmini-security-audit
- 补齐 CTF skills：ctf-ai-ml、ctf-writeup

### 2026-04-15
- 迁入 schedule-analyzer 和 8 类 CTF Skills

### 2026-03-17
- amazon-analyse 升级至 v1.1.0（三模块架构）

### 2026-03-11
- 新增 stock-research 扩展（deep-research 领域扩展）

### 2026-03-08
- deep-research 升级至 v1.2.0 + 新增 question-refiner

### 2026-03-06
- paper-revision 升级至 v1.1.0（四模式）

### 2026-03-01
- 新增 collaborating-with-codex、collaborating-with-gemini
- 创建 INDEX.md 渐进式披露机制

### 2026-02-20
- 新增 seedance-prompt、seedance-storyboard、frontend-design、ui-ux-pro-max、react-best-practices、web-artifacts-builder

### 2026-02-04
- 新增 vision-builder、plan-review、parallel-explore、observability、deep-research、exa-research、brightdata-research、social-media-research、market-insight

### 2026-01-23
- 初始版本：pytorch、pandas、data-analysis、literature-mentor、paper-revision、god-oversight

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
| **stock-research** | 8阶段股票投资尽调框架，模拟巴菲特式理性投资分析 | `/stock-research <股票代码>`, `分析股票` |
| **market-insight** | 三段式用户画像与产品机会分析 | `/insight <产品描述>` |
| **exa-research** | 企业与市场研究，基于 Exa 搜索引擎 | `研究竞争对手`, `分析行业` |
| **brightdata-research** | 电商平台深度调研，反反爬虫支持 | `电商调研`, `畅销排行` |
| **amazon-analyse** | 亚马逊竞品 Listing 全维度穿透分析，基于 Sorftime MCP | `/amazon-analyse <ASIN> <市场>` |
| **social-media-research** | 跨平台社媒研究，12+ 平台覆盖 | `舆情监控`, `KOL 分析` |
| **literature-mentor** | 文献深度解读，交互/报告双模式 | `解读这篇论文`, `生成精读报告` |
| **paper-revision** | 论文风格修改，技术准确性保持 | `修改论文风格` |

---

## AI 视频创作 Skills

| Skill | 描述 | 触发词 | 适用场景 |
|-------|------|--------|----------|
| **seedance-prompt** | Seedance 2.0 分镜提示词生成 | `生成视频提示词`, `分镜提示词` | 15s 内短片分镜 |
| **seedance-storyboard** | 小说/故事转多集视频剧本 | `写剧本`, `生成分镜`, `/seedance` | 短剧/电影完整制作 |
| **seedance-prompt-ads** | 视频广告 Seedance 提示词生成 | `视频广告`, `品牌TVC`, `带货广告` | 品牌广告/电商带货 |

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
| **skill-creator** | Skill 元创建器，按契约四要素生成高质量 SKILL.md | `/skill-creator`, `创建一个 Skill`, `封装成 Skill` |
| **spec-first** | 完整 QA 工作流编排器，串联 spec-writer→开发→qa-reviewer→qa-fixer | `/spec-first`, `先写规范再开发`, `需要质量保障` |
| **pr-prep** | PR 提交前五步检查仪式，确保每个 PR 一次通过 Review | `/pr-prep`, `准备提 PR`, `PR 检查清单` |
| **task-decompose** | 任务分解器，三层拆解（Epic→Story→Task）+ 依赖图 + 并行化建议 | `/task-decompose`, `任务拆解`, `需求分解` |
| **sdd-riper** | Spec-Driven Development + RIPER 五阶段流程，中大型需求（>500行/3+文件） | `/riper`, `/sdd-riper`, `中大型需求开发` |
| **sdd-riper-light** | SDD-RIPER 轻量版，简单任务（<500行/<3文件），快速迭代 | `/riper-light`, `/sdd-light`, `简单 bug 修复` |

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

**x-ai-topic-selector 说明**: 启动后输入 `/select-topics`。需 Chrome 登录推特账号 + Gemini API Key（可换 DeepSeek）。两种模式:
- **扫描模式**: 批量抓取信息流 → AI 评分 → Top N 精选
- **书签模式**: 分析已收藏内容 → 生成摘要 + 选题建议（不做排序）

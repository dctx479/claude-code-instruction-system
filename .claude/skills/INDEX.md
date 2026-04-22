# Skills 索引 - 渐进式披露系统

> **设计理念**: 仅在需要时加载完整 Skill 定义，节省 70-90% Token 开销

## 使用说明

### 加载策略
1. **首次阅读**: 仅读取本 INDEX.md，了解可用 Skill 概览（~600 tokens）
2. **按需加载**: 根据任务需求，读取对应 Skill 的完整 SKILL.md（~2K tokens/个）
3. **智能匹配**: 根据任务特征和触发条件自动选择最合适的 Skill

### 性能优化
- **Token节省**: INDEX 文件 ~600 tokens vs 所有 Skill ~46K tokens，节省 **98%**
- **精准激活**: 避免无关 Skill 内容干扰上下文
- **分层文档**: 核心能力在 SKILL.md，详细参考在 REFERENCE.md（部分 Skill）

---

## Skill 目录

### 系统类 (System)

#### observability
```yaml
文件: .claude/skills/observability/SKILL.md
描述: AI 思维日志可观测性系统，实时记录推理过程、决策点和执行状态
适用: 复杂多步骤任务、需要可追溯决策过程、调试异常行为时
专长:
  - 实时记录 TaskStart/DecisionPoint/Discovery/Error/Recovery/TaskComplete
  - 输出到 logs/ai-thoughts.md，支持日志轮转
  - 与 Context Archival、Ralph Loop、Autopilot 深度集成
触发: 任务开始、遇到决策点、发生错误时自动记录
集成: [context-archivist, ralph-loop, autopilot]
```

---

### 规划类 (Planning)

#### vision-builder
```yaml
文件: .claude/skills/vision-builder/SKILL.md
描述: 愿景构建器，将模糊需求转化为清晰的项目愿景文档
适用: 新项目启动、需求模糊时、Autopilot Planning 阶段开始前
专长:
  - 引导式提问澄清需求（5W1H 分析框架）
  - SMART 目标设定
  - 风险识别与范围定义
输出: VISION.md 愿景文档
触发: 模糊需求描述时、/autopilot 规划阶段
集成: [autopilot, architect, spec-writer]
```

#### plan-review
```yaml
文件: .claude/skills/plan-review/SKILL.md
描述: 计划审查器，对实现计划进行多维度评估，识别风险和改进点
适用: 实现计划完成后、Autopilot Planning 阶段结束前、architect 输出后
专长:
  - 10 维度评估（完整性/可行性/清晰度/依赖性/风险性/测试性/可维护性/扩展性/安全性/文档性）
  - 3 阶段审查（结构检查/深度评估/综合建议）
  - 问题分级（红/黄/绿）
输出: PLAN-REVIEW.md 审查报告（≥70 分通过）
触发: 计划文档编写完成后
集成: [autopilot, spec-writer, qa-reviewer, god-committee]
```

---

### 开发类 (Development)

#### parallel-explore
```yaml
文件: .claude/skills/parallel-explore/SKILL.md
描述: Git Worktree 并行探索，为多方案决策创建独立工作树，标准化评估选最优方案
适用: 需要对比多个技术方案、架构选型、有明确评估维度的决策点
专长:
  - 为每个候选方案创建独立 Git Worktree
  - 完整实现每个方案（非 mock）
  - 标准化 10 分制多维度评估报告
  - 自动合并最优方案并清理其余工作树
触发: 出现 2-4 个可行技术方案需要对比时
集成: [orchestrator COMPETITIVE 策略, autopilot]
```

#### collaborating-with-codex
```yaml
文件: .claude/skills/collaborating-with-codex/SKILL.md
描述: 多模型协作，通过后台 Bash 子进程调用 Codex CLI 并行实现代码，Claude 融合审查
适用: 代码实现任务、样板生成、API 示例、测试用例编写
专长:
  - 非阻塞后台调用 OpenAI Codex CLI
  - Claude 并行分析同一任务
  - 读取结果文件进行融合，取长补短
  - 适合 Claude 擅长理解规划、Codex 擅长代码生成的场景
触发: 代码实现任务，需要借助 Codex 提升效率时
集成: [orchestrator COLLABORATIVE 策略, ralph-loop, autopilot]
```

#### collaborating-with-gemini
```yaml
文件: .claude/skills/collaborating-with-gemini/SKILL.md
描述: 多模型协作，通过后台 Bash 子进程调用 Gemini CLI，利用其超长上下文窗口
适用: 整个代码库扫描、大型文档处理（>100K tokens）、跨文件 bug 追踪
专长:
  - 非阻塞后台调用 Google Gemini CLI
  - 利用 Gemini 100万+ tokens 上下文窗口
  - 适合整体代码库分析、大型迁移分析、多文件一致性检查
  - Claude 负责规划和最终融合
触发: 任务涉及超大上下文或整体代码库理解时
集成: [orchestrator COLLABORATIVE 策略]
```

#### react-best-practices
```yaml
文件: .claude/skills/react-best-practices/SKILL.md
描述: Vercel 官方 React + Next.js 性能优化宝典，45+ 条规则按影响力排序
适用: React/Next.js 项目开发、代码审查、性能优化
专长:
  - 消除 Waterfall 请求
  - 减少 Bundle 体积
  - 优化 Core Web Vitals（LCP/CLS/FID）
  - 8 大规则类别，支持代码审查和新功能开发两种模式
触发: React/Next.js 相关任务时
```

#### web-artifacts-builder
```yaml
文件: .claude/skills/web-artifacts-builder/SKILL.md
描述: Anthropic 官方 Web Artifacts 构建器，生成可交互的单文件 HTML 应用
适用: 需要快速构建交互式 Demo、原型、可视化组件时
专长:
  - React 18 + TypeScript + Vite + Tailwind + shadcn/ui
  - 40+ 预装 shadcn/ui 组件
  - 打包为单文件 bundle.html，无需服务器
  - 支持复杂状态管理
触发: 需要构建可交互 Web 组件或 Demo 时
```

---

### 设计类 (Design)

#### frontend-design
```yaml
文件: .claude/skills/frontend-design/SKILL.md
描述: 前端设计与 UI/UX 指导专家，AI 前端开发的「设计总监」
适用: 前端开发中需要设计指导、UI 审查、交互规范时
专长:
  - 视觉层次、间距系统、配色策略、字体规范
  - 交互规范（动画曲线、表单设计、响应式布局）
  - 可访问性检查（WCAG 2.1 AA）
  - 组件选型建议
触发: 前端 UI 开发、设计审查时
```

#### ui-ux-pro-max
```yaml
文件: .claude/skills/ui-ux-pro-max/SKILL.md
描述: 最强前端设计知识库，包含 57+ UI 风格、97 配色方案、57 字体搭配
适用: 需要专业级 UI 设计、精确风格控制、多技术栈支持时
专长:
  - 57+ UI 风格（Glassmorphism/Neumorphism/Brutalism 等）
  - 97 配色方案 + 57 字体搭配组合
  - 25+ 图表类型、98 UX 规范
  - BM25 智能推荐引擎
  - 11 技术栈支持（React/Vue/Svelte/SwiftUI/Flutter 等）
触发: 需要精确 UI 风格控制、专业设计输出时
```

---

### 研究类 (Research)

#### deep-research
```yaml
文件: .claude/skills/deep-research/SKILL.md
描述: 深度研究技能 v1.2，Lead Agent + Subagent 架构并行调研，支持引用验证、置信度评分、创新组合发现和领域扩展
适用: 需要全面深入的主题研究、市场分析、技术调研、创新方向探索
专长:
  - Lead Agent 规划 + 多 Subagent 并行搜索
  - 多维度交叉验证 + 矛盾解决矩阵 + 发现置信度评分
  - 可选 Citation Validation（深度模式）
  - 创新组合模式：候选池构建、机制抽取、组合假设、shortlist 筛选
  - 领域扩展协议（叠加式增强特定领域）
  - 自动生成带数据点和引用的结构化报告
触发: 需要深度调研、创新方向探索、无法通过单次搜索得出结论时
```

#### stock-research (deep-research 扩展)
```yaml
文件: .claude/skills/deep-research/extensions/stock-research.md
描述: 8阶段股票投资尽调框架，模拟巴菲特式理性投资分析（大量阅读、多空平衡）
适用: 个股分析、指数成分股批量研究、投资决策支持
专长:
  - 8阶段顺序管道（公司底座→行业周期→业务拆解→财务质量→股权治理→市场分歧→估值护城河→执行摘要）
  - 投资信号评级（6维度评分 + 建议仓位）
  - 多空平衡矩阵（强制呈现Bull/Bear两面）
  - 财务概览仪表盘（核心指标 + 估值指标 + 杜邦分解）
  - 快速/标准/完整三种模式（4-22个Subagent）
触发: /stock-research <股票代码>，分析股票、投资研究任务
实践: 1000+ 次使用，已验证恒生科技/科创50/创业板50/纳斯达克金龙指数成分股批量分析
```

#### question-refiner
```yaml
文件: .claude/skills/question-refiner/SKILL.md
描述: 研究查询精炼器，验证和结构化用户查询，输出标准化 Structured Research Prompt
适用: 研究查询模糊或不完整时，作为 research 类 Skill 的可选前置网关
专长:
  - 7 项验证清单（意图/范围/信息类型/可操作性/无歧义/粒度/前提）
  - 快速通过机制（≥5/7 通过则零追问直接精炼）
  - 引导式澄清（最多 3 个问题）
  - 标准化输出可被所有 research 类 Skill 消费
触发: 研究查询不清晰、范围过宽、用户请求帮助澄清时
集成: [deep-research, exa-research, brightdata-research, social-media-research]
```

#### exa-research
```yaml
文件: .claude/skills/exa-research/SKILL.md
描述: 企业与市场研究技能，基于 Exa 搜索引擎进行公司情报和竞争对手分析
适用: 公司背景调查、竞争对手分析、市场规模研究
专长:
  - Exa MCP 语义搜索（比关键词搜索更精准）
  - 通过 Task Agent 隔离搜索避免上下文污染
  - 自动提炼关键数据点
集成: Exa MCP
触发: 企业/市场调研任务
```

#### brightdata-research
```yaml
文件: .claude/skills/brightdata-research/SKILL.md
描述: 电商平台深度调研，基于 Bright Data MCP 的反反爬虫市场情报收集
适用: 电商平台数据采集、商品价格监控、销量趋势分析
专长:
  - Quick/Standard/Deep 三种调研模式
  - 绕过反爬虫限制（Bright Data 代理网络）
  - 结构化电商数据提取（价格/评分/销量/评论）
集成: Bright Data MCP
触发: 电商平台数据调研任务
```

#### amazon-analyse
```yaml
文件: .claude/skills/amazon-analyse/SKILL.md
描述: 亚马逊选品全维度分析工具集（三模块），基于 Sorftime MCP 获取官方数据
适用: 亚马逊选品决策、竞品 Listing 分析、关键词深度调研、差评痛点挖掘、广告投放词库
专长:
  - 模块 A - Listing 穿透分析：六大维度（产品/关键词/评论/排名/竞争/市场）
  - 模块 B - 关键词深度调研：三阶段流水线，2000+ 词库，7 类分类，CSV/HTML Dashboard
  - 模块 C - 差评痛点分析：6 维痛点框架（电子/结构/设计/外观/描述/服务），三级严重度
  - Quick/Standard/Deep 三种分析深度
  - 真实 API 数据（非爬取），支持 US/DE/UK/JP 等多市场
集成: Sorftime MCP
触发: /amazon-analyse | /keyword-research | /review-analysis <ASIN> <MARKETPLACE>
```

#### social-media-research
```yaml
文件: .claude/skills/social-media-research/SKILL.md
描述: 跨平台社媒数据研究，基于 TikHub MCP 的舆情监控和 KOL 分析
适用: 社交媒体趋势分析、KOL 影响力研究、品牌舆情监控
专长:
  - 12+ 平台支持（TikTok/Instagram/YouTube/Twitter 等）
  - KOL 数据采集与影响力分析
  - 内容趋势洞察
集成: TikHub MCP
触发: 社媒数据分析、舆情监控任务
```

#### literature-mentor
```yaml
文件: .claude/skills/literature-mentor/SKILL.md
描述: 文献深度解读助手，像研究生导师一样交互式解读学术论文
适用: 学术论文精读、文献综述、研究方法理解
专长:
  - 分层解读（摘要→方法→结果→讨论）
  - 批判性分析（局限性/创新点识别）
  - 与 Zotero MCP 集成获取全文
  - 交互式问答深化理解
集成: Zotero MCP
触发: 学术论文阅读、文献研究任务
```

#### paper-revision
```yaml
文件: .claude/skills/paper-revision/SKILL.md
描述: 论文/技术文档全流程写作助手，覆盖大纲审核、结构仿写、润色、去AI化四种模式
适用: 论文大纲检查、AI写作痕迹消除、文风仿写改写、学术文本润色
专长:
  - 大纲审核（逻辑/完整性/层级三维评分 + 修改建议大纲）
  - 去AI化（识别8类AI特征句式并改写为自然表达）
  - 结构仿写（提取参考段落逻辑骨架，套用到用户内容）
  - 润色（改写措辞风格，更解释性、通俗化，保持技术准确）
触发: 大纲审核/去AI化/仿写/论文润色修改任务
集成: [paper-writing-assistant, literature-review, qa-reviewer]
```

---

### AI/ML 类 (AI/ML)

#### pytorch
```yaml
文件: .claude/skills/pytorch/SKILL.md
描述: PyTorch 深度学习框架知识库，用于构建和训练神经网络模型
适用: 深度学习模型开发、训练流程设计、模型调试
专长:
  - 模型架构设计（CNN/RNN/Transformer/GAN）
  - 训练循环、损失函数、优化器配置
  - 模型保存/加载/部署最佳实践
触发: PyTorch 相关深度学习任务
```

#### pandas
```yaml
文件: .claude/skills/pandas/SKILL.md
描述: pandas 数据分析库知识库，用于数据处理、清洗和分析
适用: 结构化数据处理、数据清洗、特征工程
专长:
  - DataFrame 操作和数据转换
  - 数据清洗（缺失值/异常值处理）
  - 分组聚合、透视表、时间序列处理
触发: pandas 数据处理任务
```

#### data-analysis
```yaml
文件: .claude/skills/data-analysis/SKILL.md
描述: 通用数据分析技能，包括统计分析、数据可视化和洞察提取
适用: 探索性数据分析、统计检验、结果可视化
专长:
  - 描述性统计和分布分析
  - 假设检验（t-test/ANOVA/相关性）
  - matplotlib/seaborn/plotly 可视化
触发: 数据分析、统计研究任务
```

---

### 产品类 (Product)

#### market-insight
```yaml
文件: .claude/skills/market-insight/SKILL.md
描述: 市场洞察分析助手，三段式框架快速识别用户画像、情绪动机和产品机会
适用: 产品方向验证、用户需求分析、市场机会识别
专长:
  - 用户画像识别（Who + Pain Points）
  - 情绪动机分析（Why they care）
  - 产品机会提炼（可验证的方向）
触发: 产品方向分析、市场调研任务
```

---

### 创意类 (Creative)

#### seedance-prompt
```yaml
文件: .claude/skills/seedance-prompt/SKILL.md
描述: Seedance 2.0 分镜提示词生成专家，将想法/图片转化为 AI 视频结构化提示词
适用: Seedance 2.0 视频生成、分镜提示词创作
专长:
  - 10+ 风格声明（电影写实/水墨/赛博朋克/动漫等）
  - 完整镜头语言库（景别/运动/角度）
  - 时间轴格式分镜（精确到秒）
  - 16+ 模板分类，支持看图说故事
触发: Seedance 视频生成、分镜创作任务
```

#### seedance-storyboard
```yaml
文件: .claude/skills/seedance-storyboard/SKILL.md
描述: Seedance 2.0 剧本分镜生成器，将小说/故事转化为多集视频剧本和分镜脚本
适用: 多集视频系列创作、故事改编为视频脚本
专长:
  - 四幕结构剧本创作（起承转合）
  - 编号素材清单（角色C/场景S/道具P + 英文提示词）
  - Seedance 时间轴格式分镜脚本
  - 视频延长链式方案（集间无缝衔接）
触发: 多集视频剧本创作、故事改编任务
```

---

### 治理类 (Governance)

#### god-oversight
```yaml
文件: .claude/skills/god-oversight/SKILL.md
描述: God Committee 监督能力，独立监控、异常检测和治理干预
适用: 系统状态监控、高风险操作审议、异常行为检测
专长:
  - 独立系统状态观察与快照
  - 代码质量/安全/性能三维评估
  - 投票审议机制（god-member/consensus/intervention 三层）
  - 5 级干预能力（L1 观察 → L5 紧急停止）
触发: 定期监控、里程碑完成、检测到异常时
集成: [god-member, god-consensus, god-intervention]
```

---

### 工具类 (Utility)

#### schedule-analyzer
```yaml
文件: .claude/skills/schedule-analyzer/SKILL.md
描述: 课表空课查找统计分析，批量 OCR 提取课表数据、解析周次、分组统计、差异分析
适用: 多人课表空课时间统计、排课协调、会议时间查找
专长:
  - 批量 OCR 提取课表图片（Vision API）
  - 周次解析（单双周/逗号分隔/范围表达）
  - 分组空课统计 + 黄金时段识别（88% 阈值）
  - 周次差异分析 + Markdown 报告生成
触发: 课表分析、空课查找、排课统计任务
```

---

### 安全类 (Security/CTF)

#### solve-challenge (CTF 编排器)
```yaml
文件: .claude/skills/solve-challenge/SKILL.md (如有)
描述: CTF 挑战解题编排器，分析题目类型并调度对应 CTF 技能
适用: CTF 竞赛解题、安全挑战分析
专长:
  - 自动识别题目类型（pwn/crypto/web/reverse/forensics/osint/malware/misc）
  - 调度对应类别 CTF 技能
触发: CTF 挑战题目分析和解题
集成: [ctf-crypto, ctf-forensics, ctf-malware, ctf-misc, ctf-osint, ctf-pwn, ctf-reverse, ctf-web]
```

#### ctf-crypto
```yaml
文件: .claude/skills/ctf-crypto/SKILL.md
描述: 密码学攻击技术，RSA/AES/ECC/格密码/PRNG/签名伪造
触发: CTF 密码学题目
```

#### ctf-forensics
```yaml
文件: .claude/skills/ctf-forensics/SKILL.md
描述: 数字取证与信号分析，磁盘镜像/内存转储/网络抓包/隐写术
触发: CTF 取证题目
```

#### ctf-malware
```yaml
文件: .claude/skills/ctf-malware/SKILL.md
描述: 恶意软件分析，混淆脚本/C2流量/PE分析/反分析绕过
触发: CTF 恶意软件分析题目
```

#### ctf-misc
```yaml
文件: .claude/skills/ctf-misc/SKILL.md
描述: 杂项技术，编码解谜/Python沙箱逃逸/RF信号处理/Z3约束求解
触发: CTF 杂项题目
```

#### ctf-osint
```yaml
文件: .claude/skills/ctf-osint/SKILL.md
描述: 开源情报收集，社交媒体/地理定位/DNS记录/反向图片搜索
触发: CTF OSINT 题目
```

#### ctf-pwn
```yaml
文件: .claude/skills/ctf-pwn/SKILL.md
描述: 二进制漏洞利用，栈溢出/堆利用/ROP/内核提权/沙箱逃逸
触发: CTF PWN 题目
```

#### ctf-reverse
```yaml
文件: .claude/skills/ctf-reverse/SKILL.md
描述: 逆向工程，二进制分析/反调试绕过/自定义VM/多平台逆向
触发: CTF 逆向题目
```

#### ctf-web
```yaml
文件: .claude/skills/ctf-web/SKILL.md
描述: Web 安全漏洞利用，XSS/SQLi/SSTI/SSRF/JWT/原型链污染
触发: CTF Web 安全题目
```

#### ctf-ai-ml
```yaml
文件: .claude/skills/ctf-ai-ml/SKILL.md
描述: AI/ML 攻击技术，对抗样本/模型窃取/提示注入/成员推断/LoRA 利用/LLM 越狱
附加资源: adversarial-ml.md, llm-attacks.md, model-attacks.md
触发: CTF AI/ML 题目，攻击 ML 模型/LLM
来源: ljagiello/ctf-skills (1627⭐)
```

#### ctf-writeup
```yaml
文件: .claude/skills/ctf-writeup/SKILL.md
描述: 标准化 CTF 解题报告生成器，用于赛事提交和组织者复核
触发: 解决 CTF 挑战后，需要规范化记录解题步骤/工具/经验教训
来源: ljagiello/ctf-skills (1627⭐)
```

---

### 代码安全审计类 (Code Security Audit)

#### code-security-review
```yaml
文件: .claude/skills/code-security-review/SKILL.md
描述: 通用代码安全审计，三阶段 audit-filter-report 流程，内置 19 条误报排除规则 + 17 条先例
适用: 任何语言代码审计、漏洞扫描、PR 安全检查
资源: audit-prompt.md / filtering-rules.md / hard-exclusion-patterns.md / customization-guide.md
触发: 安全审计、漏洞扫描、代码安全检查
集成: 增强 agents/security/security-audit.md 的误报过滤能力
来源: ez-lbz/claude-code-security-skills (提炼自 anthropics 官方)
```

#### php-audit (子 skill 集合)
```yaml
目录: .claude/skills/php-audit/
描述: PHP 白盒代码审计 skill 集合，证据契约驱动（EVID_* 证据点）
核心流水线: php-route-mapper → php-route-tracer → php-*-audit → php-exploit-chain-audit
漏洞子 skill (30+): sql/nosql/cmd/ssrf/xss/file-read/file-upload/file-write/archive-extract/xxe/deser/tpl/ldap/expr/auth/csrf/open-redirect/crlf/session-cookie/config/crypto/logic/logging
框架专项: laravel / symfony / yii / thinkphp / wordpress / codeigniter
证据契约: shared/EVIDENCE_POINT_IDS.md + IO_PATH_CONVENTION.md + PHP_SINK_REFERENCE.md + SEVERITY_RATING.md
触发: PHP 项目安全审计、上线前评估、修复回归验证
来源: 0xShe/PHP-Code-Audit-Skill (272⭐)
```

#### java-audit (子 skill 集合)
```yaml
目录: .claude/skills/java-audit/
描述: Java 白盒代码审计 skill 集合，与 php-audit 同架构（route-mapper + route-tracer + pipeline）
核心 skill: java-route-mapper / java-route-tracer / java-audit-pipeline
漏洞子 skill: sql-audit / auth-audit / xxe-audit / file-read-audit / file-upload-audit / vuln-scanner
共享契约: java-shared/DECOMPILE_STRATEGY.md + OUTPUT_STANDARD.md + SEVERITY_RATING.md
触发: Java 项目安全审计、Spring/Struts/MyBatis 反序列化链分析
来源: RuoJi6/java-audit-skills (580⭐)
```

#### wxmini-security-audit
```yaml
文件: .claude/skills/wxmini-security-audit/SKILL.md
描述: 微信小程序全自动安全审计 Agent Teams，7 Agent 协作 + 脚本/LLM 双层架构 + 4 路并行
覆盖维度: 敏感信息泄露 / API 接口提取 / 加解密算法 / 漏洞分析（认证/数据/注入/越权/支付/信息泄露/配置）
Agent 分工: agent-01 反编译 → agent-02~05 并行分析 → agent-06 报告 + agent-07 自定义分析
工具脚本: tools/scripts/endpoint_extractor.py + secret_scanner.py（正则预扫描）
依赖: unveilr.exe (wxapkg 反编译，需独立下载) + Windows 平台
触发: 微信小程序 .wxapkg 安全审计、上线前合规检查
来源: sssmmmwww/wxmini-security-audit (193⭐)
```

---

## 场景速查：该加载哪个 Skill？

### 按业务阶段速查

| 阶段 | 可用 Skill | 说明 |
|------|-----------|------|
| **需求** | vision-builder, question-refiner | 从模糊需求到清晰目标 |
| **调研** | deep-research, exa-research, brightdata-research, social-media-research, literature-mentor | 信息收集和分析 |
| **方案** | plan-review, parallel-explore, spec-writer (Agent) | 方案设计和评审 |
| **开发** | react-best-practices, web-artifacts-builder, collaborating-with-codex, collaborating-with-gemini | 代码实现 |
| **测试** | QA 系统 (qa-reviewer + qa-fixer Agent) | 质量验证 |
| **沉淀** | observability, paper-revision | 记录和总结 |

### 按场景速查

| 场景 | 优先加载 | 可选加载 |
|------|----------|----------|
| 新项目启动 | vision-builder | plan-review |
| 实现计划审查 | plan-review | — |
| 技术方案选型 | parallel-explore | plan-review |
| React/Next.js 开发 | react-best-practices | frontend-design |
| 前端 UI 设计 | frontend-design | ui-ux-pro-max |
| 精确风格控制 | ui-ux-pro-max | frontend-design |
| 快速构建 Demo | web-artifacts-builder | — |
| 深度主题研究 | deep-research | exa-research |
| 研究问题不清晰 | question-refiner | deep-research |
| 深度研究需引用验证 | deep-research（深度模式） | — |
| **股票投资分析** | stock-research（完整模式） | exa-research |
| **快速筛选股票** | stock-research（快速模式） | — |
| **指数成分股批量分析** | stock-research + data-analysis | — |
| 企业/竞品调研 | exa-research | — |
| 电商数据采集 | brightdata-research | amazon-analyse |
| 亚马逊竞品分析 | amazon-analyse | market-insight |
| **亚马逊关键词调研** | amazon-analyse（/keyword-research） | — |
| **亚马逊差评痛点挖掘** | amazon-analyse（/review-analysis） | market-insight |
| **亚马逊选品全流程** | amazon-analyse → /keyword-research → /review-analysis | spec-writer |
| **亚马逊选品深度调研** | amazon-analyse（/product-research，规划中 v1.2.0） | market-insight, deep-research |
| **亚马逊广告词库** | amazon-analyse（/keyword-research） | — |
| 社媒舆情分析 | social-media-research | — |
| **论文大纲检查** | paper-revision（大纲审核模式） | — |
| **论文写作润色** | paper-revision（润色模式） | — |
| **去AI化/降AIGC率** | paper-revision（去AI化模式） | — |
| **学习参考论文写法** | paper-revision（结构仿写模式） | — |
| **论文精读/文献理解** | literature-mentor | — |
| **论文全流程写作** | paper-revision | literature-mentor |
| 数据分析 | data-analysis / pandas | — |
| 深度学习任务 | pytorch | data-analysis |
| 代码实现加速 | collaborating-with-codex | — |
| 大规模代码库分析 | collaborating-with-gemini | — |
| 视频分镜创作 | seedance-prompt | seedance-storyboard |
| 多集视频剧本 | seedance-storyboard | seedance-prompt |
| 产品方向验证 | market-insight | exa-research |
| 任务可追溯性 | observability | — |
| 系统监控 | god-oversight | — |
| **课表空课统计** | schedule-analyzer | — |
| **CTF 解题** | solve-challenge | ctf-* (按题目类型) |
| **密码学攻击** | ctf-crypto | — |
| **数字取证** | ctf-forensics | — |
| **二进制漏洞利用** | ctf-pwn | ctf-reverse |
| **逆向工程** | ctf-reverse | ctf-pwn |
| **Web 安全** | ctf-web | — |

---

## 更新日志

### 2026-04-21
- 新增代码安全审计类 (Code Security Audit) 分类，引入 4 个外部 skill
- `code-security-review`：来自 ez-lbz/claude-code-security-skills（提炼自 anthropics 官方），19+17 条误报过滤规则，三阶段 audit-filter-report 流程
- `php-audit`：35 子 skill 集合，来自 0xShe/PHP-Code-Audit-Skill (272⭐)，证据契约驱动 + Laravel/Symfony/Yii/ThinkPHP/WordPress/CodeIgniter 框架专项
- `java-audit`：10 子 skill 集合，来自 RuoJi6/java-audit-skills (580⭐)，route-mapper + route-tracer + pipeline 架构
- `wxmini-security-audit`：来自 sssmmmwww/wxmini-security-audit (193⭐)，7 Agent 协作 + 脚本/LLM 双层 + 4 路并行，覆盖微信小程序反编译到报告的全流程
- 补齐 CTF skills：新增 `ctf-ai-ml`（AI/ML 攻击）和 `ctf-writeup`（赛事标准化报告），来自 ljagiello/ctf-skills (1627⭐)

### 2026-04-15
- 从全局配置迁入 schedule-analyzer Skill（课表空课分析）
- 从全局配置迁入 8 类 CTF Skills（crypto/forensics/malware/misc/osint/pwn/reverse/web，共 77 个文件）
- 新增 solve-challenge CTF 编排器条目
- 场景速查表新增 7 个场景：课表统计/CTF解题/密码学/取证/PWN/逆向/Web安全
- 新增工具类 (Utility) 和安全类 (Security/CTF) 分类

### 2026-03-17
- amazon-analyse 升级至 v1.1.0（三模块架构）
- 新增模块 B：关键词深度调研（`/keyword-research`），三阶段流水线，2000+ 词库，7 类分类
- 新增模块 C：差评痛点分析（`/review-analysis`），6 维痛点框架，三级严重度
- 场景速查表新增 4 个场景：关键词调研/差评痛点/选品全流程/广告词库
- 新增三模块协同数据流和推荐组合用法

### 2026-03-11
- 新增 stock-research 扩展（deep-research 领域扩展，8阶段股票投资尽调框架）
- 场景速查表新增 3 个股票研究场景：股票投资分析/快速筛选股票/指数成分股批量分析
- SKILLS-CATALOG.md 新增 stock-research 组合模式（stock-research + data-analysis/exa-research）

### 2026-03-08
- deep-research 升级至 v1.2.0（Question Refiner 集成 + 引用验证 + 置信度评分 + 领域扩展协议）
- 新增 question-refiner Skill（研究查询精炼器，7 项验证 + 快速通过 + 引导澄清）
- 场景速查表新增 2 个场景：研究问题不清晰 / 深度研究需引用验证

### 2026-03-06
- paper-revision 升级至 v1.1.0（四模式：润色/大纲审核/去AI化/结构仿写）
- 场景速查表补充论文全流程 6 个场景，每种模式独立映射

### 2026-03-01
- 创建 INDEX.md，实现真正的渐进式披露（节省 98% Token）
- 新增 collaborating-with-codex、collaborating-with-gemini（多模型协作）

### 2026-02-20
- 新增 seedance-prompt、seedance-storyboard（视频创作）
- 新增 frontend-design、ui-ux-pro-max（设计类）
- 新增 react-best-practices、web-artifacts-builder（开发类）

### 2026-02-04
- 新增 vision-builder、plan-review（规划类，Aha-Loop 方法论）
- 新增 parallel-explore、observability（开发类）
- 新增 social-media-research、exa-research、brightdata-research、deep-research（研究类）
- 新增 market-insight（产品类）

### 2026-01-23
- 初始版本：pytorch、pandas、data-analysis、literature-mentor、paper-revision
- 新增 god-oversight（治理类）

---

## 相关文档

- **Agent 索引**: `agents/INDEX.md`
- **Skills 集成指南**: `.claude/skills/README.md`
- **编排模式**: `workflows/orchestration/orchestration-patterns.md`
- **策展型最佳实践条目库**: `memory/best-practices.md`

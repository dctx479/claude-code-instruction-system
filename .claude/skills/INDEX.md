# Skills 索引

> 轻量索引，仅供任务匹配。详细文档: `docs/SKILLS-CATALOG.md` | 设计规范: `.claude/skills/README.md`

## 加载协议

1. 读本文件匹配 Skill（~80 行）
2. 按需读取对应 `SKILL.md`（~2K tokens/个）
3. Heavy 类型 Skill 需要时再读 `REFERENCE.md`

---

## 系统类 (System)

| Skill | 描述 | 路径 | 协作 Agent |
|-------|------|------|-----------|
| neat | 任务收尾五步法，同步 docs/CLAUDE.md/memory 三层知识 | neat/ | — |
| reflection | 任务复盘提炼器，萃取经验 + Ingest 去重写入 | reflection/ | — |
| skill-creator | Skill 元创建器，契约四要素 + 单一职责 | skill-creator/ | — |
| prime | 会话预热仪式，git 状态 + 记忆检索 + 状态摘要 | prime/ | — |
| debug | 结构化调试五步工作流（复现→隔离→假设→验证→防复发） | debug/ | debugger |
| observability | AI 思维日志，记录推理过程和决策点 | observability/ | context-archivist |
| handoff | 上下文交接，/compact 前写入进度和下一步 | handoff/ | — |

## 开发类 (Development)

| Skill | 描述 | 路径 | 协作 Agent |
|-------|------|------|-----------|
| sdd-riper | SDD + RIPER 五阶段，中大型需求（>500行/3+文件）[Heavy] | sdd-riper/ | sdd-riper-orchestrator |
| sdd-riper-light | SDD-RIPER 轻量版（<500行/<3文件） | sdd-riper-light/ | — |
| spec-first | QA 工作流编排：spec-writer→开发→qa-reviewer→qa-fixer | spec-first/ | spec-writer, qa-reviewer, qa-fixer |
| task-decompose | 任务分解器，三层拆解 + 依赖图 + 并行化建议 | task-decompose/ | — |
| pr-prep | PR 提交前五步检查仪式 | pr-prep/ | code-reviewer |
| parallel-explore | Git Worktree 多方案并行实现 + 标准化评估 | parallel-explore/ | — |
| collaborating-with-codex | 多模型协作，后台调用 Codex CLI 并行实现 | collaborating-with-codex/ | — |
| collaborating-with-gemini | 多模型协作，利用 Gemini 超长上下文窗口 | collaborating-with-gemini/ | — |
| claude-agent-sdk | Skill→Web SaaS 五步法封装 [Heavy] | claude-agent-sdk/ | — |

## 前端设计类 (Frontend & Design)

| Skill | 描述 | 路径 |
|-------|------|------|
| react-best-practices | Vercel 官方 React/Next.js 45+ 性能优化规则 | react-best-practices/ |
| web-artifacts-builder | React+Tailwind+shadcn/ui 单文件 HTML 应用 | web-artifacts-builder/ |
| frontend-design | 布局/交互/配色/可访问性设计指导 | frontend-design/ |
| ui-ux-pro-max | 57+ UI 风格、97 配色、57 字体知识库 | ui-ux-pro-max/ |

## 规划类 (Planning)

| Skill | 描述 | 路径 | 协作 Agent |
|-------|------|------|-----------|
| vision-builder | 模糊需求→清晰愿景文档（5W1H + SMART） | vision-builder/ | architect |
| plan-review | 计划 10 维度评估，识别风险和改进点 | plan-review/ | — |

## 研究类 (Research)

| Skill | 描述 | 路径 | 依赖 MCP |
|-------|------|------|---------|
| deep-research | Lead+Subagent 并行调研，引用验证 + 置信度评分 | deep-research/ | — |
| question-refiner | 研究查询精炼器，7 项验证 + 标准化输出 | question-refiner/ | — |
| exa-research | 企业与市场研究，语义搜索 | exa-research/ | Exa |
| brightdata-research | 电商平台深度调研，反反爬虫 | brightdata-research/ | Bright Data |
| amazon-analyse | 亚马逊选品三模块（Listing/关键词/差评） | amazon-analyse/ | Sorftime |
| social-media-research | 跨平台社媒 12+ 平台覆盖 | social-media-research/ | TikHub |
| literature-mentor | 文献深度解读，交互式论文精读 | literature-mentor/ | Zotero |
| paper-revision | 论文四模式（润色/大纲审核/去AI化/仿写） | paper-revision/ | — |
| market-insight | 三段式用户画像与产品机会分析 | market-insight/ | — |

## AI/ML 类 (AI/ML)

| Skill | 描述 | 路径 |
|-------|------|------|
| pytorch | PyTorch 深度学习框架知识库 | pytorch/ |
| pandas | pandas 数据处理知识库 | pandas/ |
| data-analysis | 通用统计分析与可视化 | data-analysis/ |

## 创意类 (Creative)

| Skill | 描述 | 路径 |
|-------|------|------|
| seedance-prompt | Seedance 2.0 分镜提示词，10+ 风格 + 镜头语言库 | seedance-prompt/ |
| seedance-storyboard | 小说→多集视频剧本 + 分镜脚本 | seedance-storyboard/ |

## 安全审计类 (Security Audit)

| Skill | 描述 | 路径 | 协作 Agent |
|-------|------|------|-----------|
| code-security-review | 通用代码安全审计，19 条误报排除规则 | code-security-review/ | security-analyst, security-audit |
| wxmini-security-audit | 微信小程序 7 Agent 全自动安全审计 | wxmini-security-audit/ | — |

## CTF 类 (CTF)

| Skill | 描述 | 路径 |
|-------|------|------|
| ctf-crypto | 密码学攻击（RSA/AES/ECC） | ctf-crypto/ |
| ctf-forensics | 数字取证（磁盘/内存/网络/隐写） | ctf-forensics/ |
| ctf-malware | 恶意软件分析 | ctf-malware/ |
| ctf-misc | 杂项（编码/沙箱逃逸/Z3） | ctf-misc/ |
| ctf-osint | 开源情报收集 | ctf-osint/ |
| ctf-pwn | 二进制漏洞利用（栈/堆/ROP） | ctf-pwn/ |
| ctf-reverse | 逆向工程 | ctf-reverse/ |
| ctf-web | Web 安全（XSS/SQLi/SSTI） | ctf-web/ |
| ctf-ai-ml | AI/ML 攻击（对抗样本/提示注入） | ctf-ai-ml/ |
| ctf-writeup | CTF 解题报告生成器 | ctf-writeup/ |

## 治理类 (Governance)

| Skill | 描述 | 路径 | 协作 Agent |
|-------|------|------|-----------|
| god-oversight | God Committee 监控、异常检测、治理干预 | god-oversight/ | god-member, god-consensus, god-intervention |

## 工具类 (Utility)

| Skill | 描述 | 路径 |
|-------|------|------|
| schedule-analyzer | 课表空课查找统计，批量 OCR + 周次分析 | schedule-analyzer/ |

## 推荐外部工具 (External Tools)

> 非 Skill 架构，但与 Skill 工作流深度互补。检测到适用场景时应主动推荐安装。
> 完整指南: `docs/TOOLS-ECOSYSTEM-GUIDE.md`

| 工具 | 描述 | 类型 | 快速安装 |
|------|------|------|---------|
| Context Mode | MCP 输出压缩，~98% token 节省 | MCP/Plugin | `claude mcp add context-mode -- npx -y context-mode` |
| CodeGraph | tree-sitter 代码知识图谱，~92% tool call 减少 | MCP 工具 | `npx @colbymchenry/codegraph` |
| claude-tap | API 流量检查 + token 用量分析 + 系统提示词查看 | CLI 工具 | `pip install claude-tap` |
| Knowledge Work Plugins | Anthropic 官方 20+ 职业角色插件库 | Plugin 库 | `claude plugin marketplace add anthropics/knowledge-work-plugins` |

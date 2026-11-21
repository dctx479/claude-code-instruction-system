---
name: llm-wiki
description: 多源内容 → 结构化 Wiki → 静态知识库站点。将网页/PDF/本地文件/RSS 等素材自动整理成带索引的 Markdown Wiki，可选生成 Quartz 静态站点，可选通过 claude-agent-sdk 暴露为 RAG API
license: MIT
metadata:
  category: research
  tags:
  - wiki
  - knowledge-base
  - static-site
  - quartz
  - rag
  - content-pipeline
  - llm-wiki
  requires: []
  optional:
  - claude-agent-sdk
  - deep-research
  - literature-mentor
  version: 1.0.0
  trigger:
  - /llm-wiki
  - 建知识库
  - wiki化
  - 整理成 wiki
  - 生成静态知识站
  - 把资料整理成知识库
  - Quartz 知识站
disable-model-invocation: true
---

# LLM Wiki Skill

> 把任意素材源变成可检索、可发布、可 API 化的结构化知识库。

## 设计动机

| 痛点 | 典型表现 | 后果 |
|------|---------|------|
| 资料分散 | 周报/PDF/网页/笔记散落各处 | 检索困难，知识孤岛 |
| 重复阅读 | 每次都要重新翻原始材料 | 时间浪费 |
| 无法 API 化 | 知识只在本地，无法给 Agent 调用 | 知识不可复用 |
| AI 生成无结构 | 直接让 AI 总结 → 一大段文字 | 无法导航和检索 |

**核心洞察**（来自 Karpathy llm-wiki 方法论）：AI 不应该替代你阅读，而应该帮你把阅读过的内容变成结构化的"第二大脑"。

---

## What（输入/输出）

**输入**：
- 素材源（必选其一或多个）：
  - 本地文件目录（Markdown/TXT/PDF）
  - URL 列表（网页/RSS/公众号/知乎/小红书）
  - 已有 Markdown 文档集合
- 输出目标（必选其一）：
  - `wiki`：仅生成结构化 Markdown Wiki 目录
  - `site`：生成 Wiki + Quartz 静态站点配置
  - `api`：生成 Wiki + claude-agent-sdk RAG API

**输出**：
- `wiki/` — 结构化 Markdown 文件树（带索引页）
- （site 模式）`quartz.config.ts` + 发布脚本
- （api 模式）RAG API 服务代码（基于 claude-agent-sdk）

---

## When Done（验收标准）

- [ ] `wiki/index.md` 存在，包含完整目录导航
- [ ] 每个 Wiki 页面有：标题、摘要（≤3 句）、关键词标签、原始来源链接
- [ ] 跨文章内链正确（`[[页面名]]` 或 `[标题](相对路径)`）
- [ ] 索引页按主题分类，不是按时间堆砌
- [ ] （site 模式）`npm run build` 能成功生成静态站点
- [ ] （api 模式）RAG endpoint 能返回相关段落

---

## What NOT（边界约束）

- **不替代阅读**：Wiki 是导航层，不是替代原文的摘要
- **不创造内容**：Wiki 条目必须有来源，禁止 AI 凭空补充
- **不过度压缩**：每条条目保留足够细节，不变成"一句话总结"
- **不忽略去重**：同一知识点跨多个来源时，合并而非重复

---

## How（四阶段流程）

### Phase 1：素材摄入（Ingest）

```
输入素材
  ↓
┌─────────────────────────────────────┐
│ 按类型路由                           │
├──────────┬──────────┬───────────────┤
│ 本地文件  │ URL 列表  │ 已有 Markdown │
│ Read 工具 │ WebFetch  │ 直接处理      │
└──────────┴──────────┴───────────────┘
  ↓
为每条素材生成摄入记录：
  - 原始标题
  - 来源 URL / 文件路径
  - 摄入时间
  - 原始内容摘录（前 500 字）
```

**大批量处理规则**（≥20 条素材）：
- 先生成素材清单让用户确认范围
- 分批处理，每批 10-20 条
- 输出进度：`[15/47] 正在处理: 阮一峰周报 #456`

### Phase 2：结构化分析（Structure）

对每条素材提取：

```markdown
## 条目模板

**标题**: {原始标题或 AI 生成标题}
**来源**: [{URL 或文件名}]({链接})
**日期**: {发布日期或摄入日期}
**标签**: #{主题1} #{主题2} #{主题3}
**摘要**: {2-3 句话，保留原文关键词}

### 核心内容
{结构化要点，保留具体数据/项目名/人名}

### 关联条目
- [[{相关 Wiki 页面 1}]]
- [[{相关 Wiki 页面 2}]]
```

**标签体系构建规则**：
- 从内容中归纳，不预设分类
- 同义标签合并（`AI工具` = `AI Tools` = `人工智能工具`）
- 标签粒度：不超过 3 层（`#技术/前端/React`）

### Phase 3：Wiki 组织（Organize）

**索引页结构**（`wiki/index.md`）：

```markdown
# {知识库名称}

> {一句话描述这个知识库的内容和用途}
> 最后更新: {日期} | 条目数: {N}

## 目录

### {主题分类 1}
- [[条目 A]] — {一句话说明}
- [[条目 B]] — {一句话说明}

### {主题分类 2}
...

## 标签索引
#{标签1}: [[条目X]], [[条目Y]]
#{标签2}: [[条目Z]]

## 最近更新
| 日期 | 条目 | 变更 |
|------|------|------|
```

**文件树规范**：
```
wiki/
├── index.md          # 主索引（必须）
├── _tags/            # 标签索引页
│   ├── AI工具.md
│   └── 前端.md
├── {主题分类}/
│   ├── {条目1}.md
│   └── {条目2}.md
└── _sources.md       # 所有来源记录（审计用）
```

### Phase 4：发布（可选）

#### site 模式 — Quartz 静态站点

```bash
# 前置要求
git clone https://github.com/jackyzha0/quartz
cd quartz && npm install

# 将 wiki/ 内容复制到 content/
cp -r wiki/* content/

# 生成站点
npx quartz build

# 本地预览
npx quartz build --serve

# 部署到 Cloudflare Pages / GitHub Pages
# 将 public/ 目录上传
```

**Nginx 伪静态配置**（部署到自有服务器时）：
```nginx
location / {
    try_files $uri $uri/ $uri.html =404;
}
```

#### api 模式 — RAG API（基于 claude-agent-sdk）

调用 `claude-agent-sdk` Skill 生成 RAG 服务：
- 输入：`wiki/` 目录
- 输出：向量化索引 + HTTP API endpoint
- 查询方式：`POST /query {"q": "React hooks 用法"}`

---

## 典型用例

### 用例 1：阮一峰周报 → 可搜索知识站

```bash
# 1. 下载素材
git clone https://github.com/ruanyf/weekly

# 2. 执行 Wiki 化
/llm-wiki --source weekly/ --output wiki --mode site

# 3. 发布
npx quartz build && deploy public/ to Cloudflare Pages
```

**预期输出**：
- ~400+ Wiki 条目（按工具/技术/资讯分类）
- 带搜索功能的静态站点
- 每条目有来源期号链接

### 用例 2：Zotero 文献库 → 研究知识库

```bash
/llm-wiki --source zotero-export.bib --output wiki --mode api
```

与 `literature-mentor` 协作：literature-mentor 负责深度解读，llm-wiki 负责结构化存档。

### 用例 3：个人笔记 → 第二大脑

```bash
/llm-wiki --source ~/notes/ --output wiki --mode wiki
```

---

## 与其他 Skill 的协作

| Skill | 集成方式 |
|-------|---------|
| **deep-research** | deep-research 的调研报告可直接作为 llm-wiki 的素材输入 |
| **literature-mentor** | 文献解读结果 → llm-wiki 存档为可检索条目 |
| **claude-agent-sdk** | api 模式下调用 claude-agent-sdk 生成 RAG 服务 |
| **handoff** | 大批量 wiki 化任务跨会话时，用 handoff new-window 模式传递进度 |

---

## 版本历史

- **v1.0.0** (2026-06-28): 初版。填补「多源内容 → 结构化 Wiki → 静态站点」空白。灵感来源：liangdabiao/llm-wiki + Karpathy llm-wiki 方法论（github.com/liangdabiao/llm-wiki）

# Garden Skills 集成指南

> 来源: ConardLi 开源项目 [garden-skills](https://github.com/ConardLi/garden-skills)（7K+ Stars）  
> 三个内容创作类 Skill：网页视频制作 / 网页设计 / GPT Image2 图片生成

---

## 快速集成

### 方法一：Git Clone（推荐）

```bash
# 克隆仓库到临时目录
git clone https://github.com/ConardLi/garden-skills.git /tmp/garden-skills

# 复制三个 Skill 到项目
cp -r /tmp/garden-skills/skills/web-video-presentation ~/.claude/skills/
cp -r /tmp/garden-skills/skills/web-design-engineer ~/.claude/skills/
cp -r /tmp/garden-skills/skills/gpt-image-2 ~/.claude/skills/

# 验证安装
ls ~/.claude/skills/ | grep -E "web-video|web-design|gpt-image"
```

### 方法二：Submodule（适合长期跟踪更新）

```bash
cd /path/to/claude-code-instruction-system

# 添加为 git submodule
git submodule add https://github.com/ConardLi/garden-skills.git external/garden-skills

# 软链接到 Skills 目录
ln -s $(pwd)/external/garden-skills/skills/web-video-presentation ~/.claude/skills/
ln -s $(pwd)/external/garden-skills/skills/web-design-engineer ~/.claude/skills/
ln -s $(pwd)/external/garden-skills/skills/gpt-image-2 ~/.claude/skills/

# 更新时拉取最新版本
git submodule update --remote external/garden-skills
```

---

## 三大 Skill 详细说明

### 1. web-video-presentation（网页视频制作）

**功能**：把文章/脚本/课程/产品 Demo 转化为基于网页的演示视频。

**核心特性**：
- 25+ 套内置主题（bold-signal / terminal-green / newsroom / electric-studio 等）
- 可插拔 TTS（支持 MiniMax CLI、OpenAI TTS、ElevenLabs、edge-tts）
- 章节化管理，支持局部迭代修改
- 录屏即视频（无需传统视频编辑工具）

**在线预览**：https://mmh1.top/#/ai-application/web-video-presentation

**使用场景**：
- 技术文章视频化
- 产品功能演示
- 课程讲解
- 发布会式演示（Keynote 风格）

**关键工作流**（见 `memory/best-practices.md` BP-045）：
1. 第一轮确认：脚本 + 主题 + 章节大纲 + 视觉方向
2. 整体跑通：生成完整版本
3. 局部迭代：针对不满意的章节单独反馈

---

### 2. web-design-engineer（网页设计）

**功能**：生成专业级网页设计，消除"AI 味"（大渐变/玻璃卡片/发光边框/过度圆角）。

**核心特性**：
- 25 套设计风格（linear / raycast / aesop / tufte-dataink / balenciaga-post-2017 等）
- 反 AI 味规则库（避免常见的 AI 审美陷阱）
- 信息密度控制（紧凑 vs 留白）
- 视觉层级设计（而非平铺元素）

**在线预览**：https://mmh1.top/#/ai-application/web-design-engineer

**使用场景**：
- B2B SaaS 官网
- 落地页
- Dashboard
- 活动页
- 作品集

**设计流程**：
1. 判断产品类型和受众
2. 确定视觉方向、信息层级、排版节奏
3. 选择设计风格主题
4. 局部调整组件密度和交互细节

---

### 3. gpt-image-2（GPT Image2 图片生成）

**功能**：面向 GPT Image 2 和 OpenAI 兼容图像 API 的结构化图片生成。

**核心特性**：
- 18 大类 / 79 个结构化 Prompt 模板
- 三种运行模式：
  - 本地模式（直接调接口出图）
  - 宿主工具模式（交给当前 Agent 的图像工具）
  - 顾问模式（无图像工具时，输出可执行 Prompt）
- 支持海报/UI Mockup/产品图/信息图/论文图/技术架构图/漫画/头像/分镜/品牌板

**在线预览**：https://gpt-image2.mmh1.top/

**使用场景**：
- 社交媒体海报
- 产品原型图
- 技术架构图
- 论文配图
- 品牌视觉设计

**关键设计原则**：
- 结构化任务描述 > 单纯风格词（见 BP-045）
- 明确画面目标/主体关系/构图/材质/光线/字体限制/输出尺寸/后续编辑空间

---

## 推荐配置

### 模型选型

根据 ConardLi 实战验证，**Opus 4.7** 在创作类长任务中表现最优：
- 审美判断更准确
- 章节规划更合理
- 代码实现更稳定
- 返工决策更精准

较小模型处理复杂创作任务时结果差异大（见 `memory/best-practices.md` BP-045）。

### 环境变量

如果使用本地模式生成图片，需要配置 API Key：

```bash
# OpenAI 兼容接口
export OPENAI_API_KEY="sk-..."
export OPENAI_BASE_URL="https://api.openai.com/v1"  # 可选

# MiniMax TTS（用于 web-video-presentation）
export MINIMAX_API_KEY="..."
export MINIMAX_GROUP_ID="..."
```

---

## 集成验证

```bash
# 验证 Skills 已加载
claude code  # 启动 Claude Code
# 在对话中输入：
"列出所有可用的 Skill"

# 应该看到：
# - web-video-presentation
# - web-design-engineer
# - gpt-image-2

# 测试 Skill 激活
"使用 web-design-engineer 设计一个 SaaS 官网"
```

---

## 更新策略

### Git Clone 方式

手动拉取最新版本：
```bash
cd /tmp/garden-skills
git pull origin main
cp -r skills/* ~/.claude/skills/
```

### Submodule 方式

自动跟踪更新：
```bash
cd /path/to/claude-code-instruction-system
git submodule update --remote external/garden-skills
```

---

## 已知限制

1. **web-video-presentation**：
   - TTS 生成需要外部 API（MiniMax/OpenAI/ElevenLabs）
   - 录屏需要手动操作（使用 OBS / QuickTime 等工具）

2. **web-design-engineer**：
   - 25 套主题覆盖常见场景，但特殊行业（如医疗/金融）可能需要自定义

3. **gpt-image-2**：
   - 依赖 GPT Image 2 模型能力，不支持 Stable Diffusion 等其他模型
   - 本地模式需要自己提供 API Key

---

## 相关文档

- `docs/SKILLS-CATALOG.md` — Garden Skills 的目录条目和触发词
- `memory/best-practices.md` BP-045 — 创作类长任务 Skill 工作流
- Garden Skills 官方文档：https://github.com/ConardLi/garden-skills
- 在线预览网站：https://mmh1.top

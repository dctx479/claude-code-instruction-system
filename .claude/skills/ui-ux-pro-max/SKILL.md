---
name: ui-ux-pro-max
description: 最强前端设计知识库，包含 57+ UI 风格、97 配色方案、57 字体搭配、25+ 图表类型和 98 UX 规范，让 AI 生成「能见客户」的专业界面
version: 1.0.0
license: MIT
metadata:
  category: design
  tags: [ui, ux, design-system, styles, colors, fonts, charts, glassmorphism, brutalism]
  requires: []
  optional: [frontend-design]
  source: nextlevelbuilder/ui-ux-pro-max-skill
trigger:
  - "/ui-ux-pro-max"
  - "专业 UI 设计"
  - "精确风格控制"
  - "配色方案"
  - "Glassmorphism"
  - "设计系统"
---

# UI/UX Pro Max Skill

## 契约定义

### What（输入/输出）

**输入**：
- 产品类型和目标用户
- UI/UX 任务（构建/设计/创建/实现/审查/修复/改进）
- 可选：行业（SaaS/电商/医疗/金融/教育等）
- 可选：技术栈（React/Vue/Svelte/SwiftUI/Flutter 等）

**输出**：
- 自动生成的设计系统（Design System）
- 智能推荐的风格、配色、字体组合
- 带正确颜色、字体、间距的实现代码
- 行业最佳实践和反面案例警告

### When Done（验收标准）

- 设计系统包含完整的颜色体系、字体方案、间距规则
- 风格选择有具体理由（不是随机选择）
- 代码实现可直接运行
- 符合目标行业的设计规范

### What NOT（边界约束）

- **禁止风格不匹配**：银行不用 Brutalism，医疗不用暗黑风
- **禁止忽略行业规范**：金融要严肃、教育要友好
- **禁止过度设计**：为了炫技使用不适合的风格

---

## 核心数据库

### 57+ UI 风格

**热门风格**：

| 风格 | 特征 | 适用场景 |
|------|------|----------|
| **Glassmorphism** | 毛玻璃效果、半透明、模糊背景 | 现代科技产品、仪表盘 |
| **Neumorphism** | 柔和凸起/凹陷、同色系阴影 | 设置面板、计算器 |
| **Claymorphism** | 3D 黏土质感、柔和阴影 | 儿童产品、游戏界面 |
| **Brutalism** | 粗犷、原始、大胆色彩 | 创意机构、艺术网站 |
| **Minimalism** | 极简、留白、克制用色 | 高端品牌、阅读产品 |
| **Bento Grid** | 网格卡片布局、多尺寸混排 | 功能展示、产品页面 |
| **Dark Mode** | 深色背景、低对比度、护眼 | 开发工具、媒体播放 |
| **Gradient Mesh** | 渐变网格、有机色彩流动 | 创意落地页、品牌页 |
| **Editorial Grid** | 杂志式排版、多栏布局 | 新闻、博客、内容平台 |
| **Retro/Vintage** | 复古色调、老式字体 | 咖啡店、手工品牌 |

**2025/2026 新趋势**：
- Anti-Polish（反精致）
- Tactile Digital（触觉数字化）
- Nature Distilled（自然提炼）
- Interactive Cursor（交互光标）
- Voice-First（语音优先）
- 3D Product Preview（3D 产品预览）
- Chromatic Aberration（色差效果）
- Vintage Analog（复古模拟）

### 97 配色方案

**按行业分类**：

| 行业 | 主色系 | 情绪 | 示例 |
|------|--------|------|------|
| SaaS | 蓝紫色系 | 信任、专业 | #6366F1 + #8B5CF6 |
| 电商 | 橙红色系 | 活力、紧迫感 | #F97316 + #EF4444 |
| 医疗 | 蓝绿色系 | 安全、清洁 | #06B6D4 + #10B981 |
| 金融 | 深蓝色系 | 稳重、可靠 | #1E3A5F + #2563EB |
| 教育 | 绿蓝色系 | 成长、知识 | #22C55E + #3B82F6 |
| 美妆 | 粉金色系 | 优雅、女性化 | #EC4899 + #F59E0B |
| 游戏 | 霓虹色系 | 刺激、沉浸 | #A855F7 + #06FFA5 |
| 餐饮 | 暖色系 | 温馨、食欲 | #DC2626 + #F59E0B |

### 57 字体搭配

**经典组合**：

| 搭配 | 标题字体 | 正文字体 | 适用风格 |
|------|----------|----------|----------|
| 现代专业 | Inter | System UI | SaaS/工具 |
| 优雅editorial | Playfair Display | Source Sans Pro | 杂志/品牌 |
| 技术感 | JetBrains Mono | Inter | 开发工具 |
| 中文优雅 | 思源宋体 | 思源黑体 | 中文内容 |
| 柔和友好 | Nunito | Open Sans | 教育/儿童 |

### 25+ 图表类型

适用于 Dashboard 场景：
- 折线图、柱状图、饼图、环形图
- 散点图、面积图、热力图
- 桑基图、树状图、雷达图
- K线图、漏斗图、瀑布图
- 气泡图、极坐标图

### 98 UX 规范

覆盖最佳实践、反面案例、可访问性：
- 表单设计规范
- 导航模式
- 加载状态处理
- 错误信息展示
- 空状态设计
- 通知系统
- 搜索体验
- 分页与无限滚动

---

## 11 技术栈支持

| 技术栈 | 组件库 | CSS 方案 |
|--------|--------|----------|
| React | shadcn/ui | Tailwind CSS |
| Next.js | shadcn/ui | Tailwind CSS |
| Vue 3 | Naive UI | UnoCSS |
| Nuxt | Nuxt UI | Tailwind CSS |
| Svelte | Skeleton | Tailwind CSS |
| SwiftUI | 原生组件 | SwiftUI |
| React Native | React Native Paper | StyleSheet |
| Flutter | Material 3 | Theme |
| HTML | - | Tailwind CSS |
| Jetpack Compose | Material 3 | Compose Theme |
| Angular | Angular Material | SCSS |

---

## 智能推荐引擎

Skill 使用 BM25 概率排名算法，根据产品类型自动推荐：

1. **分析需求**：产品类型、目标用户、行业
2. **匹配风格**：从 57+ 风格中推荐最佳 3 个
3. **选择配色**：根据行业和情绪匹配配色方案
4. **搭配字体**：推荐标题+正文字体组合
5. **生成设计系统**：输出完整的 Design System 配置

---

## 使用指南

### 触发场景

- 「为我的 SaaS 产品设计一个 Dashboard」
- 「用 Glassmorphism 风格设计登录页」
- 「为电商网站选择配色方案」
- 「审查这个页面的 UI 设计」
- 「为 React 项目建立设计系统」

### 反面案例检查

Skill 会主动警告不适合的风格选择：
- 银行/金融 → 不推荐 Brutalism、Claymorphism
- 医疗/健康 → 不推荐 Dark Mode、霓虹色
- 儿童/教育 → 不推荐 极简黑白、复杂布局
- 企业/政府 → 不推荐 过度动画、鲜艳渐变

---

## 参考资源

- [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- [官方文档](https://ui-ux-pro-max-skill.nextlevelbuilder.io/)

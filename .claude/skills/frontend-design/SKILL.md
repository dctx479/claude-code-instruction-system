---
name: frontend-design
description: 前端设计与 UI/UX 指导专家，提供布局思路、组件选型、交互规范、颜色、间距、动画和可访问性检查，是 AI 前端开发的「设计总监」
version: 1.0.0
license: MIT
metadata:
  category: design
  tags: [frontend, design, ui, ux, accessibility, layout, interaction]
  requires: []
  optional: []
  source: anthropics/skills
trigger:
  - "/frontend-design"
  - "UI 设计建议"
  - "前端布局"
  - "组件选型"
  - "可访问性检查"
  - "交互规范"
---

# Frontend Design Skill

## 契约定义

### What（输入/输出）

**输入**：
- UI/UX 设计需求（布局、组件、交互、品牌风格）
- 可选：现有代码（用于审查和优化）
- 可选：目标平台（Web/Mobile/Desktop）
- 可选：设计系统约束（Material/Ant Design/自定义）

**输出**：
- 设计决策建议（布局、配色、字体、间距）
- 交互规范（动画、过渡、响应式策略）
- 可访问性检查清单
- 具体实现代码（HTML/CSS/React 组件）

### When Done（验收标准）

- 设计方案视觉上专业、一致
- 遵循可访问性标准（WCAG 2.1 AA）
- 响应式适配至少 3 个断点（移动/平板/桌面）
- 无「AI 通病」：不使用过度居中布局、紫色渐变、千篇一律的圆角、Inter 字体
- 配色具有足够的对比度（至少 4.5:1 文本对比度）

### What NOT（边界约束）

- **禁止通用模板化**：每个设计必须针对具体场景定制
- **禁止「AI Slop」风格**：避免过度居中布局、紫色渐变、统一圆角、Inter 字体滥用
- **禁止忽略可访问性**：所有交互元素必须可键盘操作
- **禁止抄袭**：创建原创视觉设计，不复制现有艺术家作品

---

## 核心能力

### 1. 设计原则

**视觉层次 (Visual Hierarchy)**：
- 使用大小、颜色、对比度建立信息层次
- 重要元素突出，次要元素弱化
- F 型或 Z 型阅读模式引导

**间距系统 (Spacing System)**：
- 基于 4px/8px 网格系统
- 一致的 padding/margin 规则
- 呼吸感：留白 > 拥挤

**配色策略**：
- 主色 (Primary) + 辅助色 (Secondary) + 强调色 (Accent)
- 语义色：Success/Warning/Error/Info
- 深色/浅色模式双套方案

**字体规范**：
- 标题和正文字体搭配（至多 2 种字体家族）
- 字重层次：Regular(400) / Medium(500) / Bold(700)
- 行高：正文 1.5-1.75，标题 1.2-1.4

### 2. 交互规范

**动画原则**：
- 持续时间：150ms-300ms（微交互），300ms-500ms（页面过渡）
- 缓动函数：ease-out 进入，ease-in 退出
- 遵循 prefers-reduced-motion 偏好

**表单设计**：
- 标签始终可见（不用 placeholder 代替 label）
- 实时验证 + 清晰的错误提示
- Tab 顺序合理

**响应式策略**：
- Mobile First 设计
- 断点：640px / 768px / 1024px / 1280px
- 触摸目标最小 44px × 44px

### 3. 可访问性检查

- 颜色对比度 ≥ 4.5:1（正文）/ 3:1（大文本）
- 所有图片有 alt 文本
- 表单元素有 label 关联
- 键盘可完全操作
- ARIA 属性正确使用
- 焦点可见且样式明显

### 4. 设计审查

对现有 UI 代码提供审查：
- 一致性检查（间距、颜色、字体是否统一）
- 可访问性扫描
- 响应式问题
- 性能优化（CSS 效率、动画性能）
- UX 合理性（信息架构、用户流程）

---

## 使用指南

### 触发场景

- 「设计一个登录页面」
- 「审查这个组件的 UI」
- 「优化这个页面的用户体验」
- 「建立项目的设计系统」
- 「检查这个页面的可访问性」

### 输出格式

设计建议包含：
1. **设计决策**：为什么选择这个方案
2. **具体参数**：颜色值、间距值、字体大小
3. **代码实现**：可直接使用的 CSS/组件代码
4. **注意事项**：潜在问题和替代方案

---

## 参考资源

- [anthropics/skills - frontend-design](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md)
- [WCAG 2.1 Guidelines](https://www.w3.org/TR/WCAG21/)

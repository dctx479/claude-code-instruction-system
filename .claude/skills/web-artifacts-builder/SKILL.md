---
name: web-artifacts-builder
description: Anthropic 官方 Web Artifacts 构建器，用 React + TypeScript + Tailwind + shadcn/ui 生成可交互的单文件 HTML 应用，支持复杂状态管理和 40+ 预装组件
version: 1.0.0
license: MIT
metadata:
  category: development
  tags: [artifacts, react, html, vite, tailwind, shadcn-ui, single-file, web-app]
  requires: [bash]
  optional: [frontend-design, ui-ux-pro-max]
  source: anthropics/skills
trigger:
  - "/web-artifacts"
  - "构建交互式 Demo"
  - "生成单文件 HTML"
  - "快速原型"
  - "可交互组件"
---

# Web Artifacts Builder Skill

## 契约定义

### What（输入/输出）

**输入**：
- 交互式 Web 应用需求描述
- 可选：设计偏好
- 可选：组件需求（表单/表格/图表/Dashboard 等）

**输出**：
- 完整的 React + TypeScript 项目
- 使用 Tailwind CSS + shadcn/ui 组件
- 最终打包为单个 `bundle.html` 文件
- 可直接在浏览器运行或作为 Artifact 分享

### When Done（验收标准）

- 项目可成功构建为 `bundle.html`
- 所有交互功能正常工作
- 视觉设计专业、不呈现「AI Slop」风格
- 响应式适配基本断点
- 代码结构清晰，使用 TypeScript 类型

### What NOT（边界约束）

- **禁止简单需求使用**：单文件 HTML/JSX 不需要此 Skill
- **禁止 AI Slop 风格**：不使用过度居中布局、紫色渐变、统一圆角、Inter 字体
- **禁止前期测试**：先构建输出，有问题再调试（减少延迟）
- **禁止抄袭设计**：创建原创视觉作品

---

## 核心工作流

### Step 1: 初始化项目

```bash
bash scripts/init-artifact.sh <project-name>
```

自动创建包含：
- React 18 + TypeScript（via Vite）
- Tailwind CSS 3.4.1 + shadcn/ui 主题系统
- 路径别名（`@/`）
- **40+ shadcn/ui 组件预装**（Button, Card, Dialog, Table, Form, Chart...）
- 所有 Radix UI 依赖
- Parcel 打包配置

### Step 2: 开发

使用 React 组件和 hooks 开发：

```tsx
// src/App.tsx
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useState } from "react";

export default function App() {
  const [count, setCount] = useState(0);

  return (
    <Card className="max-w-md mx-auto mt-8">
      <CardHeader>
        <CardTitle>Counter App</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-2xl font-bold mb-4">{count}</p>
        <Button onClick={() => setCount(c => c + 1)}>
          Increment
        </Button>
      </CardContent>
    </Card>
  );
}
```

### Step 3: 打包

```bash
bash scripts/bundle-artifact.sh
```

产出 `bundle.html`：
- 所有 JS/CSS 内联到单个 HTML 文件
- 零外部依赖
- 可直接在浏览器打开或分享

---

## 预装组件 (40+)

### 布局组件
- Card, Accordion, Tabs, Sheet, Dialog, Drawer
- Collapsible, ScrollArea, Separator, AspectRatio

### 表单组件
- Button, Input, Textarea, Select, Checkbox, Radio
- Switch, Slider, DatePicker, Form (react-hook-form)
- Label, Toggle, ToggleGroup

### 数据展示
- Table, DataTable, Badge, Avatar, Progress
- Skeleton, Alert, Toast, Tooltip, Popover
- HoverCard, Command (cmdk), Carousel

### 导航
- NavigationMenu, Breadcrumb, Pagination
- Menubar, ContextMenu, DropdownMenu

### 反馈
- AlertDialog, Dialog, Toast, Sonner
- Progress, Skeleton

---

## 技术栈详解

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.x | UI 框架 |
| TypeScript | 5.x | 类型安全 |
| Vite | 5.x / 6.x | 开发服务器 |
| Tailwind CSS | 3.4.1 | 样式系统 |
| shadcn/ui | latest | 组件库 |
| Radix UI | latest | 无障碍原语 |
| Parcel | latest | 生产打包 |
| html-inline | latest | 单文件内联 |

---

## 项目结构

```
project-name/
├── index.html              # 入口
├── vite.config.ts          # Vite 配置
├── tsconfig.json           # TypeScript 配置
├── tailwind.config.js      # Tailwind 配置
├── postcss.config.js       # PostCSS 配置
├── components.json         # shadcn/ui 元数据
├── package.json
└── src/
    ├── main.tsx            # 应用入口
    ├── App.tsx             # 主应用组件
    ├── index.css           # 全局样式
    ├── lib/
    │   └── utils.ts        # 工具函数 (cn)
    └── components/
        └── ui/             # shadcn/ui 组件
            ├── button.tsx
            ├── card.tsx
            ├── dialog.tsx
            └── ...
```

---

## 适用场景

- **复杂交互 Demo**：Dashboard、数据可视化
- **工具页面**：计算器、转换器、编辑器
- **原型展示**：产品原型、交互概念验证
- **单页应用**：需要路由和状态管理的应用
- **Artifact 分享**：生成可在 Claude 对话中运行的应用

### 不适用场景

- 简单静态 HTML（直接写 HTML 即可）
- 单组件展示（不需要完整项目结构）
- 纯文本内容（不需要交互）

---

## 设计指南

### 避免 AI Slop

- 不使用 Inter 作为唯一字体
- 不使用紫色渐变作为默认配色
- 不使用千篇一律的 rounded-2xl
- 不使用过度居中的单列布局
- 每个设计都应该独特且有目的性

### 专业设计原则

- 使用有意义的配色（不是随机渐变）
- 建立清晰的视觉层次
- 响应式设计（至少适配移动端和桌面）
- 合理的间距和留白
- 一致的组件风格

---

## 参考资源

- [anthropics/skills - web-artifacts-builder](https://github.com/anthropics/skills/blob/main/skills/web-artifacts-builder/SKILL.md)
- [Artifacts Builder 详解](https://deepwiki.com/anthropics/skills/3.2.1-artifacts-builder)
- [Claude Skills Hub](https://claudeskills.info/skill/artifacts-builder/)

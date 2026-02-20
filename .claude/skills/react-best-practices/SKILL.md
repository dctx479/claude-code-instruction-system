---
name: react-best-practices
description: Vercel 官方 React + Next.js 性能优化宝典，包含 45+ 条规则（按影响力排序），消除 waterfall 请求、减少 bundle 体积、优化 Core Web Vitals
version: 1.0.0
license: MIT
metadata:
  category: development
  tags: [react, nextjs, performance, optimization, vercel, bundle-size, waterfall, core-web-vitals]
  requires: []
  optional: [frontend-design]
  source: vercel-labs/agent-skills
---

# React Best Practices Skill

## 契约定义

### What（输入/输出）

**输入**：
- React/Next.js 代码（组件、页面、hooks）
- 可选：性能问题描述
- 可选：Core Web Vitals 指标

**输出**：
- 按影响力排序的优化建议
- 具体代码修改方案（Before/After 对比）
- 每条规则的性能影响说明

### When Done（验收标准）

- 所有 Critical 级别问题已解决
- 无 async waterfall 请求
- Client bundle 中无不必要的大型依赖
- Server Components 和 Client Components 正确划分
- Core Web Vitals 指标在合理范围内

### What NOT（边界约束）

- **禁止过度优化**：只优化有实际影响的问题
- **禁止破坏功能**：优化不能改变业务逻辑
- **禁止忽略 DX**：保持代码可读性和可维护性

---

## 核心规则（按影响力排序）

### Critical Priority（关键）

#### 1. 消除 Async Waterfalls

**问题**：连续的 await 调用导致请求瀑布流
```tsx
// Bad: Sequential waterfall
const user = await getUser();
const posts = await getPosts(user.id);
const comments = await getComments(posts[0].id);

// Good: Parallel when possible
const [user, posts] = await Promise.all([
  getUser(),
  getPosts(userId),
]);
```

**影响**：可减少 50-80% 数据加载时间

#### 2. 减少 Client Bundle Size

**问题**：大型库被打包到客户端
```tsx
// Bad: Entire library imported client-side
'use client'
import { format } from 'date-fns'; // 72KB

// Good: Server Component or dynamic import
import { format } from 'date-fns'; // Server Component, 0KB client
```

**影响**：减少 TTI (Time to Interactive)

### High Priority（高）

#### 3. 正确使用 Server/Client Components

```tsx
// Server Component (default) - 数据获取、无交互
export default async function Page() {
  const data = await fetchData(); // Server-side
  return <ClientInteraction data={data} />;
}

// Client Component - 仅交互部分
'use client'
function ClientInteraction({ data }) {
  const [state, setState] = useState(data);
  // ...
}
```

#### 4. Streaming 与 Suspense

```tsx
// 使用 Suspense 实现流式渲染
export default function Page() {
  return (
    <div>
      <Header /> {/* 立即渲染 */}
      <Suspense fallback={<Skeleton />}>
        <SlowDataComponent /> {/* 流式加载 */}
      </Suspense>
    </div>
  );
}
```

#### 5. Image 优化

```tsx
// 使用 next/image 自动优化
import Image from 'next/image';

<Image
  src="/hero.jpg"
  width={1200}
  height={630}
  alt="Hero image"
  priority // LCP 图片加 priority
  placeholder="blur"
/>
```

### Medium Priority（中）

#### 6. 路由预获取和预加载
#### 7. 合理的缓存策略
#### 8. 避免不必要的 Re-render
#### 9. 动态导入大型组件
#### 10. 优化字体加载

---

## 8 大规则类别

| 类别 | 规则数 | 核心关注 |
|------|--------|----------|
| **Request Waterfalls** | 6 | 消除串行请求 |
| **Bundle Size** | 7 | 减少客户端代码 |
| **Data Fetching** | 6 | 服务端/客户端数据获取 |
| **Rendering** | 5 | Server/Client Components |
| **Caching** | 5 | 缓存策略 |
| **Core Web Vitals** | 6 | LCP/FID/CLS 优化 |
| **Code Organization** | 5 | 代码结构最佳实践 |
| **DX & Maintainability** | 5 | 开发体验 |

---

## 使用指南

### 触发场景

- 「Review this React component for performance issues」
- 「Help me optimize this Next.js page」
- 「Check this code for waterfalls」
- 「审查这个 React 组件的性能」
- 「优化这个 Next.js 页面的加载速度」

### 代码审查模式

当审查代码时，Skill 会：
1. 扫描 Critical 问题（waterfalls、bundle bloat）
2. 检查 Server/Client 边界
3. 验证数据获取模式
4. 评估缓存策略
5. 按影响力排序输出建议

### 新功能开发模式

当写新代码时，Skill 会：
1. 默认使用 Server Components
2. 仅在需要交互时标记 `'use client'`
3. 并行化所有可并行的数据获取
4. 使用 Suspense 包裹慢加载部分
5. 优化图片和字体加载

---

## 参考资源

- [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills/blob/main/skills/react-best-practices/SKILL.md)
- [Vercel Blog: Introducing React Best Practices](https://vercel.com/blog/introducing-react-best-practices)
- [React Best Practices 详解](https://blog.devgenius.io/inside-vercels-react-best-practices-40-rules-your-ai-copilot-now-knows-cdfbfb5eeb53)

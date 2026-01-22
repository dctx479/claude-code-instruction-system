# CLAUDE.md - 软件开发专用模板

## 项目信息
- **项目名称**: [项目名]
- **项目类型**: [Web应用/API服务/CLI工具/库...]
- **主要语言**: [TypeScript/Python/Go/Rust...]

## 技术架构

### 前端 (如适用)
- 框架: Next.js 14 / React 18
- 状态管理: Zustand / TanStack Query
- 样式: Tailwind CSS
- 组件库: shadcn/ui

### 后端 (如适用)
- 框架: FastAPI / Express / Go Fiber
- 数据库: PostgreSQL + Prisma ORM
- 缓存: Redis
- 消息队列: Bull / RabbitMQ

### DevOps
- CI/CD: GitHub Actions
- 容器: Docker + docker-compose
- 部署: Vercel / AWS / GCP

## 核心命令

```bash
# 开发
pnpm dev                 # 启动开发服务器
pnpm build              # 生产构建
pnpm start              # 启动生产服务器

# 测试
pnpm test               # 运行单元测试
pnpm test:e2e           # E2E 测试
pnpm test:coverage      # 测试覆盖率

# 代码质量
pnpm lint               # ESLint 检查
pnpm lint:fix           # 自动修复
pnpm typecheck          # TypeScript 类型检查
pnpm format             # Prettier 格式化

# 数据库
pnpm db:migrate         # 运行迁移
pnpm db:seed            # 填充测试数据
pnpm db:studio          # 打开 Prisma Studio
```

## 代码规范

### 文件组织
```
src/
├── app/                 # Next.js App Router 页面
├── components/
│   ├── ui/             # 基础 UI 组件
│   └── features/       # 业务功能组件
├── lib/                # 共享库和工具
├── hooks/              # 自定义 React Hooks
├── services/           # API 调用和业务逻辑
├── types/              # TypeScript 类型定义
└── constants/          # 常量和配置
```

### 命名规范
- **文件**: kebab-case (`user-profile.tsx`)
- **组件**: PascalCase (`UserProfile`)
- **函数/变量**: camelCase (`getUserProfile`)
- **常量**: UPPER_SNAKE_CASE (`API_BASE_URL`)
- **类型**: PascalCase (`UserProfile`)

### 组件规范
```typescript
// 推荐的组件结构
interface Props {
  title: string;
  onSubmit: (data: FormData) => void;
}

export function MyComponent({ title, onSubmit }: Props) {
  // 1. hooks
  const [state, setState] = useState();

  // 2. 派生状态
  const derivedValue = useMemo(() => {}, []);

  // 3. 副作用
  useEffect(() => {}, []);

  // 4. 事件处理
  const handleClick = useCallback(() => {}, []);

  // 5. 渲染
  return <div>{title}</div>;
}
```

### API 规范
- RESTful 设计原则
- 统一错误响应格式
- 请求/响应类型完整定义
- 适当的 HTTP 状态码

## Git 工作流

### 分支命名
- `feature/xxx` - 新功能
- `fix/xxx` - Bug 修复
- `refactor/xxx` - 重构
- `docs/xxx` - 文档更新

### Commit 规范
```
<type>(<scope>): <description>

feat: 新功能
fix: Bug 修复
docs: 文档更新
style: 格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具变更
```

## 测试策略

### 单元测试
- 覆盖核心业务逻辑
- 测试边界条件
- Mock 外部依赖

### 集成测试
- API 端点测试
- 数据库操作测试

### E2E 测试
- 关键用户流程
- 跨浏览器兼容性

## 性能优化清单
- [ ] 图片优化 (next/image)
- [ ] 代码分割 (dynamic imports)
- [ ] 缓存策略 (SWR/React Query)
- [ ] 虚拟列表 (大数据量)
- [ ] Web Vitals 监控

## 安全清单
- [ ] 输入验证 (zod/yup)
- [ ] XSS 防护
- [ ] CSRF 保护
- [ ] 敏感数据加密
- [ ] 依赖安全扫描

## 自主决策授权
✅ 可自主执行:
- 代码重构和优化
- 添加错误处理
- 补充类型定义
- 编写测试用例
- 性能优化

❌ 需要确认:
- 修改公共 API
- 引入新依赖
- 数据库 Schema 变更
- 删除现有功能
- 架构级别改动

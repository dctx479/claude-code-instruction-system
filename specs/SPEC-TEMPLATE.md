# [功能名称] - 技术规范

> **规范编号**: SPEC-[feature-name]
> **创建时间**: [YYYY-MM-DD]
> **负责人**: [姓名]
> **状态**: 草稿 / 审核中 / 已批准 / 已实现
> **优先级**: P0 (紧急) / P1 (高) / P2 (中) / P3 (低)

---

## 1. 需求概述

### 1.1 背景
[为什么需要这个功能？解决什么问题？]

### 1.2 目标
[功能的核心目标，用1-3句话概括]

**业务目标**:
- 目标1: [具体的业务指标]
- 目标2: [用户价值]
- 目标3: [商业价值]

**技术目标**:
- 目标1: [性能指标]
- 目标2: [可扩展性]
- 目标3: [可维护性]

### 1.3 范围
**包含** (In Scope):
- [ ] 功能点1
- [ ] 功能点2
- [ ] 功能点3

**不包含** (Out of Scope):
- 功能点X: [说明为何不在范围内]
- 功能点Y: [可能在未来版本实现]

### 1.4 用户故事
```
作为 [角色]
我想要 [功能]
以便 [价值]
```

**示例**:
```
作为 网站用户
我想要 使用邮箱和密码注册账号
以便 访问个性化内容和服务
```

---

## 2. 技术方案

### 2.1 架构设计

#### 2.1.1 系统架构图
```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   前端UI    │ ───→ │  API网关    │ ───→ │  后端服务   │
│  (React)    │ ←─── │  (Express)  │ ←─── │ (Node.js)   │
└─────────────┘      └─────────────┘      └─────────────┘
                              │
                              ↓
                     ┌─────────────┐
                     │   数据库    │
                     │ (PostgreSQL)│
                     └─────────────┘
```

#### 2.1.2 技术栈
- **前端**: React 18, TypeScript, Tailwind CSS
- **后端**: Node.js, Express, TypeScript
- **数据库**: PostgreSQL 14
- **缓存**: Redis
- **认证**: JWT
- **其他**: [列出其他技术]

#### 2.1.3 依赖关系
```
本功能依赖:
- [依赖功能1]: [依赖原因]
- [依赖功能2]: [依赖原因]

被以下功能依赖:
- [功能1]: [依赖原因]
```

---

### 2.2 数据模型设计

#### 2.2.1 数据库表结构

**表名: `users`**
```sql
CREATE TABLE users (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email           VARCHAR(255) UNIQUE NOT NULL,
  password_hash   VARCHAR(255) NOT NULL,
  username        VARCHAR(50) UNIQUE NOT NULL,
  full_name       VARCHAR(100),
  avatar_url      TEXT,
  email_verified  BOOLEAN DEFAULT FALSE,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login_at   TIMESTAMP,
  status          VARCHAR(20) DEFAULT 'active',

  CONSTRAINT check_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
  CONSTRAINT check_status CHECK (status IN ('active', 'suspended', 'deleted'))
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);
```

**表名: `user_sessions`**
```sql
CREATE TABLE user_sessions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash      VARCHAR(255) NOT NULL,
  ip_address      INET,
  user_agent      TEXT,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at      TIMESTAMP NOT NULL,

  CONSTRAINT check_expires CHECK (expires_at > created_at)
);

-- 索引
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(token_hash);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
```

#### 2.2.2 实体关系图 (ERD)
```
users (1) ──────< (N) user_sessions
  │
  │
  └──────< (N) user_profiles
```

#### 2.2.3 TypeScript类型定义
```typescript
// src/types/user.types.ts

export interface User {
  id: string;
  email: string;
  username: string;
  fullName?: string;
  avatarUrl?: string;
  emailVerified: boolean;
  createdAt: Date;
  updatedAt: Date;
  lastLoginAt?: Date;
  status: UserStatus;
}

export type UserStatus = 'active' | 'suspended' | 'deleted';

export interface CreateUserDto {
  email: string;
  password: string;
  username: string;
  fullName?: string;
}

export interface UpdateUserDto {
  fullName?: string;
  avatarUrl?: string;
}

export interface UserSession {
  id: string;
  userId: string;
  tokenHash: string;
  ipAddress?: string;
  userAgent?: string;
  createdAt: Date;
  expiresAt: Date;
}
```

#### 2.2.4 数据验证规则
```typescript
// 使用 Zod 进行数据验证

import { z } from 'zod';

export const userSchema = z.object({
  email: z.string().email('无效的邮箱格式'),
  password: z.string()
    .min(8, '密码至少8个字符')
    .regex(/[A-Z]/, '密码必须包含大写字母')
    .regex(/[a-z]/, '密码必须包含小写字母')
    .regex(/[0-9]/, '密码必须包含数字'),
  username: z.string()
    .min(3, '用户名至少3个字符')
    .max(50, '用户名最多50个字符')
    .regex(/^[a-zA-Z0-9_]+$/, '用户名只能包含字母、数字和下划线'),
  fullName: z.string().max(100).optional(),
});
```

---

### 2.3 API设计

#### 2.3.1 API端点列表

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | `/api/auth/register` | 用户注册 | 否 |
| POST | `/api/auth/login` | 用户登录 | 否 |
| POST | `/api/auth/logout` | 用户登出 | 是 |
| GET | `/api/auth/me` | 获取当前用户信息 | 是 |
| PUT | `/api/users/:id` | 更新用户信息 | 是 |
| POST | `/api/auth/refresh` | 刷新Token | 是 |

#### 2.3.2 API详细规范

**注册接口**

```http
POST /api/auth/register
Content-Type: application/json

Request Body:
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "username": "john_doe",
  "fullName": "John Doe"
}

Success Response (201 Created):
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "username": "john_doe",
      "fullName": "John Doe",
      "emailVerified": false,
      "createdAt": "2024-01-15T10:30:00Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}

Error Response (400 Bad Request):
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "邮箱格式无效",
    "fields": {
      "email": "无效的邮箱格式"
    }
  }
}

Error Response (409 Conflict):
{
  "success": false,
  "error": {
    "code": "EMAIL_EXISTS",
    "message": "该邮箱已被注册"
  }
}
```

**登录接口**

```http
POST /api/auth/login
Content-Type: application/json

Request Body:
{
  "email": "user@example.com",
  "password": "SecurePass123"
}

Success Response (200 OK):
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "username": "john_doe",
      "fullName": "John Doe"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 3600
  }
}

Error Response (401 Unauthorized):
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "邮箱或密码错误"
  }
}
```

#### 2.3.3 错误码定义

| 错误码 | HTTP状态 | 描述 | 解决方案 |
|--------|----------|------|----------|
| VALIDATION_ERROR | 400 | 请求参数验证失败 | 检查请求参数格式 |
| EMAIL_EXISTS | 409 | 邮箱已被注册 | 使用其他邮箱 |
| USERNAME_EXISTS | 409 | 用户名已存在 | 使用其他用户名 |
| INVALID_CREDENTIALS | 401 | 登录凭证无效 | 检查邮箱和密码 |
| TOKEN_EXPIRED | 401 | Token已过期 | 重新登录或刷新Token |
| UNAUTHORIZED | 401 | 未授权访问 | 提供有效的认证Token |
| FORBIDDEN | 403 | 无权限执行操作 | 检查用户权限 |
| NOT_FOUND | 404 | 资源不存在 | 检查资源ID |
| INTERNAL_ERROR | 500 | 服务器内部错误 | 联系技术支持 |

#### 2.3.4 认证机制

**JWT Token结构**:
```typescript
interface JWTPayload {
  userId: string;
  email: string;
  username: string;
  iat: number;  // issued at
  exp: number;  // expires at
}
```

**Token使用方式**:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token过期策略**:
- Access Token: 1小时
- Refresh Token: 7天
- 支持Token刷新机制

---

### 2.4 前端组件设计

#### 2.4.1 组件树结构
```
App
├── AuthProvider
│   ├── LoginPage
│   │   ├── LoginForm
│   │   └── SocialLogin
│   ├── RegisterPage
│   │   ├── RegisterForm
│   │   └── EmailVerification
│   └── ProfilePage
│       ├── UserInfo
│       ├── AvatarUpload
│       └── SecuritySettings
└── ProtectedRoute
```

#### 2.4.2 关键组件规范

**LoginForm组件**
```typescript
// src/components/auth/LoginForm.tsx

interface LoginFormProps {
  onSuccess?: (user: User) => void;
  onError?: (error: Error) => void;
  redirectTo?: string;
}

export const LoginForm: React.FC<LoginFormProps> = ({
  onSuccess,
  onError,
  redirectTo = '/dashboard'
}) => {
  // 组件实现
};
```

**状态管理**
```typescript
// src/store/auth.store.ts

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (credentials: LoginDto) => Promise<void>;
  register: (data: CreateUserDto) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}
```

#### 2.4.3 路由配置
```typescript
// src/routes/index.tsx

const routes = [
  {
    path: '/auth/login',
    element: <LoginPage />,
    public: true
  },
  {
    path: '/auth/register',
    element: <RegisterPage />,
    public: true
  },
  {
    path: '/profile',
    element: <ProtectedRoute><ProfilePage /></ProtectedRoute>,
    public: false
  }
];
```

---

## 3. 实现计划

### 3.1 任务拆分

#### 阶段1: 数据层 (2小时)
- [ ] 创建数据库表结构 (30分钟)
- [ ] 编写数据库迁移脚本 (30分钟)
- [ ] 创建TypeScript类型定义 (30分钟)
- [ ] 编写数据访问层(DAO) (30分钟)

#### 阶段2: 后端API (4小时)
- [ ] 实现用户注册逻辑 (1小时)
- [ ] 实现登录认证逻辑 (1小时)
- [ ] 实现JWT生成和验证 (1小时)
- [ ] 添加API错误处理 (30分钟)
- [ ] 编写API单元测试 (30分钟)

#### 阶段3: 前端UI (4小时)
- [ ] 创建登录表单组件 (1小时)
- [ ] 创建注册表单组件 (1小时)
- [ ] 实现状态管理 (1小时)
- [ ] 实现路由保护 (30分钟)
- [ ] 添加表单验证 (30分钟)

#### 阶段4: 集成与测试 (2小时)
- [ ] 前后端集成 (1小时)
- [ ] 端到端测试 (30分钟)
- [ ] 性能测试 (30分钟)

**总计: 12小时**

### 3.2 依赖关系
```
数据层 → 后端API → 前端UI → 集成测试
```

### 3.3 里程碑

| 里程碑 | 交付物 | 截止日期 |
|--------|--------|----------|
| M1: 数据层完成 | 数据库表+类型定义 | Day 1 |
| M2: API完成 | 所有接口+测试 | Day 2 |
| M3: UI完成 | 所有组件+样式 | Day 3 |
| M4: 发布就绪 | 完整功能+文档 | Day 4 |

---

## 4. 验收标准

### 4.1 功能验收

#### 用户注册
- [ ] 可以使用邮箱、密码、用户名成功注册
- [ ] 邮箱格式验证正确
- [ ] 密码强度验证正确
- [ ] 用户名唯一性检查正确
- [ ] 注册成功后自动登录
- [ ] 重复邮箱注册返回明确错误

#### 用户登录
- [ ] 可以使用邮箱和密码登录
- [ ] 登录成功返回有效Token
- [ ] 错误的凭证返回明确错误
- [ ] Token过期后无法访问受保护资源
- [ ] 支持刷新Token

#### 权限控制
- [ ] 未登录用户无法访问受保护页面
- [ ] 已登录用户可以访问个人资料
- [ ] 登出后Token失效

### 4.2 性能指标

| 指标 | 目标值 | 测量方法 |
|------|--------|----------|
| 注册接口响应时间 | < 200ms (P95) | 负载测试 |
| 登录接口响应时间 | < 150ms (P95) | 负载测试 |
| 并发用户数 | ≥ 1000 | 压力测试 |
| 数据库连接池 | 20-50 | 监控面板 |
| Token验证时间 | < 10ms | 单元测试 |

### 4.3 安全要求

- [ ] 密码使用bcrypt加密存储 (rounds ≥ 10)
- [ ] 防止SQL注入 (使用参数化查询)
- [ ] 防止XSS攻击 (输入验证和转义)
- [ ] 防止CSRF攻击 (使用CSRF Token)
- [ ] HTTPS强制 (生产环境)
- [ ] 密码尝试次数限制 (5次/15分钟)
- [ ] Token签名验证
- [ ] 敏感信息不记录日志

### 4.4 测试覆盖

- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 关键路径集成测试覆盖
- [ ] 边界条件测试
- [ ] 错误场景测试
- [ ] 性能基准测试

### 4.5 代码质量

- [ ] TypeScript类型完整无any
- [ ] ESLint无错误和警告
- [ ] 代码格式符合Prettier
- [ ] 函数圈复杂度 < 10
- [ ] 代码审查通过

---

## 5. 风险与对策

### 5.1 技术风险

| 风险 | 影响 | 概率 | 对策 |
|------|------|------|------|
| 密码加密性能问题 | 高 | 中 | 使用bcrypt的异步方法，避免阻塞 |
| Token过期处理复杂 | 中 | 高 | 实现完善的刷新Token机制 |
| 并发注册重复用户 | 高 | 低 | 数据库唯一约束 + 事务处理 |
| Session管理复杂 | 中 | 中 | 使用成熟的JWT库 |

### 5.2 业务风险

| 风险 | 影响 | 概率 | 对策 |
|------|------|------|------|
| 用户流失(注册复杂) | 高 | 中 | 简化注册流程，支持社交登录 |
| 账号安全问题 | 高 | 低 | 实施多重安全措施 |
| 邮件验证延迟 | 中 | 中 | 使用可靠的邮件服务商 |

### 5.3 依赖风险

| 依赖 | 风险 | 对策 |
|------|------|------|
| PostgreSQL | 数据库宕机 | 主从复制 + 定期备份 |
| JWT库 | 安全漏洞 | 定期更新依赖 |
| Redis | 缓存失效 | 优雅降级机制 |

---

## 6. 附录

### 6.1 参考资料
- [JWT最佳实践](https://datatracker.ietf.org/doc/html/rfc8725)
- [OWASP认证备忘单](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [PostgreSQL官方文档](https://www.postgresql.org/docs/)

### 6.2 相关规范
- `SPEC-user-profile.md` - 用户资料管理
- `SPEC-email-verification.md` - 邮箱验证
- `SPEC-password-reset.md` - 密码重置

### 6.3 变更历史

| 版本 | 日期 | 变更内容 | 负责人 |
|------|------|----------|--------|
| 1.0 | 2024-01-15 | 初始版本 | [姓名] |
| 1.1 | 2024-01-20 | 添加刷新Token机制 | [姓名] |

### 6.4 审批记录

| 角色 | 姓名 | 审批状态 | 日期 | 备注 |
|------|------|----------|------|------|
| 产品经理 | | ⏳ 待审批 | | |
| 技术负责人 | | ⏳ 待审批 | | |
| 安全专家 | | ⏳ 待审批 | | |

---

## 7. 问答区

**Q: 为什么选择JWT而不是Session？**
A: JWT无状态，便于横向扩展；适合前后端分离架构；减少数据库查询。

**Q: 密码加密为什么选择bcrypt？**
A: bcrypt是专门为密码设计的哈希算法，具有自适应性，可防御暴力破解。

**Q: Token过期时间为什么是1小时？**
A: 平衡安全性和用户体验，1小时内用户不需要重新登录，过期后可通过刷新Token延长。

---

**规范状态**: ⏳ 草稿
**最后更新**: [YYYY-MM-DD]
**下次审查**: [YYYY-MM-DD]

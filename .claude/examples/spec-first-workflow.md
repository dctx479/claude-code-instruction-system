# Spec-First工作流示例

## 场景: 实现用户认证功能

本示例展示完整的Spec-First开发流程，从规范编写到代码实现和质量验证。

---

## 阶段1: 规范编写 (Spec Writer)

### 1.1 触发规范编写
```bash
用户需求: "我需要一个用户认证系统，支持邮箱注册和登录"

# 启动spec-writer agent
/agent spec-writer "用户认证系统"
```

### 1.2 Spec Writer工作流程

#### 步骤1: 需求分析 (5分钟)
```markdown
Spec Writer分析:

核心需求:
- 用户注册 (邮箱+密码)
- 用户登录 (邮箱+密码)
- 会话管理 (JWT)
- 密码安全 (加密存储)

隐含需求:
- 邮箱验证
- 密码强度要求
- 重复注册防护
- 并发登录管理

边界条件:
- 邮箱格式验证
- 密码长度限制
- Token过期处理

需澄清:
- 是否需要社交登录？
- 是否需要手机号注册？
- Token过期时间？
```

**输出**: 需求澄清问题列表

#### 步骤2: 技术调研 (10分钟)
```markdown
Spec Writer分析代码库:

现有技术栈:
- 后端: Node.js + Express + TypeScript
- 数据库: PostgreSQL
- 前端: React + TypeScript

可复用组件:
- 数据库连接池 (src/db/pool.ts)
- 错误处理中间件 (src/middleware/errorHandler.ts)
- 日志系统 (src/utils/logger.ts)

技术方案:
- 使用bcrypt加密密码
- 使用jsonwebtoken生成JWT
- 使用Zod进行数据验证
- 使用PostgreSQL存储用户数据

潜在风险:
- 密码加密性能问题 → 使用异步方法
- 并发注册重复用户 → 数据库唯一约束
```

**输出**: 技术方案草案

#### 步骤3: 架构设计 (20分钟)
```markdown
数据模型:
- users表: 存储用户基本信息
- user_sessions表: 存储会话信息

API接口:
- POST /api/auth/register - 注册
- POST /api/auth/login - 登录
- POST /api/auth/logout - 登出
- GET /api/auth/me - 获取当前用户
- POST /api/auth/refresh - 刷新Token

前端组件:
- LoginForm - 登录表单
- RegisterForm - 注册表单
- AuthProvider - 认证上下文
- ProtectedRoute - 路由保护

状态管理:
- 使用Zustand管理认证状态
- 持久化Token到localStorage
```

**输出**: 详细架构设计

#### 步骤4: 编写规范 (30分钟)
```markdown
生成文件: specs/SPEC-user-authentication.md

包含章节:
1. 需求概述
   - 背景: 用户需要账号系统访问个性化功能
   - 目标: 实现安全的用户认证机制
   - 范围: 邮箱注册登录，不包含社交登录

2. 技术方案
   2.1 架构设计
   2.2 数据模型 (users表 + user_sessions表)
   2.3 API设计 (5个接口详细定义)
   2.4 前端组件 (3个组件 + 状态管理)

3. 实现计划
   - 阶段1: 数据层 (2小时)
   - 阶段2: 后端API (4小时)
   - 阶段3: 前端UI (4小时)
   - 阶段4: 集成测试 (2小时)
   总计: 12小时

4. 验收标准
   功能完整性:
   - [x] 用户可以注册
   - [x] 用户可以登录
   - [x] 邮箱格式验证
   - [x] 密码强度验证

   性能指标:
   - 注册响应时间 < 200ms
   - 登录响应时间 < 150ms

   安全要求:
   - 密码bcrypt加密
   - JWT签名验证
   - HTTPS强制

5. 风险与对策
   - 密码加密性能 → 使用异步方法
   - 并发注册 → 数据库唯一约束
   - Token安全 → 短过期时间 + 刷新机制
```

**输出**: 完整的规范文档

#### 步骤5: 定义验收标准 (10分钟)
```markdown
可测试的验收清单:

功能验收:
- [ ] 使用有效邮箱和密码可以注册成功
- [ ] 重复邮箱注册返回错误
- [ ] 邮箱格式错误返回明确提示
- [ ] 密码长度<8返回错误
- [ ] 注册成功后自动登录
- [ ] 使用正确凭证可以登录
- [ ] 错误的密码返回明确错误
- [ ] 登录成功返回有效Token
- [ ] Token过期后无法访问受保护资源
- [ ] 登出后Token失效

性能验证:
- [ ] 注册接口P95 < 200ms
- [ ] 登录接口P95 < 150ms
- [ ] 支持100并发用户

安全验证:
- [ ] 密码不以明文存储
- [ ] Token使用HS256签名
- [ ] 防止SQL注入
- [ ] 防止XSS攻击
```

**输出**: specs/SPEC-user-authentication.md (完整规范)

### 1.3 规范审查
```markdown
技术负责人审查清单:
✅ 需求是否明确？
✅ 技术方案是否可行？
✅ API设计是否合理？
✅ 验收标准是否可测试？
✅ 风险是否识别充分？

审批: ✅ 已批准
状态: 可以开始开发
```

---

## 阶段2: 代码实现 (Developer)

### 2.1 数据层实现 (2小时)

#### 创建数据库迁移
```sql
-- migrations/001_create_users.sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  username VARCHAR(50) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

#### 创建类型定义
```typescript
// src/types/user.types.ts
export interface User {
  id: string;
  email: string;
  username: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateUserDto {
  email: string;
  password: string;
  username: string;
}
```

#### 创建数据访问层
```typescript
// src/dao/user.dao.ts
export class UserDao {
  async create(data: CreateUserDto): Promise<User> {
    // 实现创建用户
  }

  async findByEmail(email: string): Promise<User | null> {
    // 实现查询用户
  }
}
```

### 2.2 后端API实现 (4小时)

#### 实现注册逻辑
```typescript
// src/services/auth.service.ts
export class AuthService {
  async register(data: CreateUserDto): Promise<{ user: User; token: string }> {
    // 1. 验证邮箱格式
    // 2. 检查邮箱是否已存在
    // 3. 加密密码
    // 4. 创建用户
    // 5. 生成Token
    // 6. 返回用户和Token
  }

  async login(email: string, password: string): Promise<{ user: User; token: string }> {
    // 1. 查找用户
    // 2. 验证密码
    // 3. 生成Token
    // 4. 返回用户和Token
  }
}
```

#### 实现API路由
```typescript
// src/routes/auth.routes.ts
router.post('/register', async (req, res) => {
  const { email, password, username } = req.body;
  const result = await authService.register({ email, password, username });
  res.status(201).json({ success: true, data: result });
});

router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  const result = await authService.login(email, password);
  res.json({ success: true, data: result });
});
```

### 2.3 前端UI实现 (4小时)

#### 创建登录表单
```typescript
// src/components/auth/LoginForm.tsx
export const LoginForm: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await login(email, password);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button type="submit">登录</button>
    </form>
  );
};
```

#### 实现状态管理
```typescript
// src/store/auth.store.ts
export const useAuthStore = create<AuthState & AuthActions>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,

  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    set({ user: response.data.user, token: response.data.token, isAuthenticated: true });
  },

  logout: () => {
    set({ user: null, token: null, isAuthenticated: false });
  }
}));
```

---

## 阶段3: 质量验证 (QA Reviewer)

### 3.1 触发QA审查
```bash
# 开发完成，提交代码
git commit -m "feat: 实现用户认证功能"

# 触发QA审查
/agent qa-reviewer "验证用户认证功能"
```

### 3.2 QA Reviewer工作流程

#### 步骤1: 读取规范
```markdown
读取: specs/SPEC-user-authentication.md

提取验收标准:
- 10个功能验收项
- 3个性能指标
- 4个安全要求
```

#### 步骤2: 代码审查
```markdown
检查:
✅ 文件结构符合规范
✅ 数据模型实现正确
✅ API实现与规范一致
✅ 前端组件完整
⚠️ 部分函数缺少错误处理
⚠️ 未添加请求频率限制
```

#### 步骤3: 测试验证
```bash
npm run test
  ✓ user.service.test.ts (8/8)
  ✓ auth.service.test.ts (6/6)
  ✗ password.service.test.ts (3/4)

Coverage: 75% (目标: ≥80%)
```

#### 步骤4: 生成QA报告
```markdown
生成: QA-REPORT.md

总体评分: 75/100

| 类别 | 得分 | 满分 | 通过 |
|------|------|------|------|
| 功能完整性 | 35 | 40 | ❌ |
| 代码质量 | 25 | 30 | ⚠️ |
| 测试覆盖 | 15 | 20 | ❌ |
| 性能指标 | 5 | 5 | ✅ |
| 安全检查 | 4 | 5 | ⚠️ |

结论: FAIL (未达到80分通过线)

发现问题:
🔴 P0 - 严重问题 (2个)
  - 密码重置功能缺失
  - 缺少请求频率限制

🟡 P1 - 重要问题 (3个)
  - 测试覆盖率不足
  - 部分错误处理缺失
  - 首屏加载时间超标

🟢 P2 - 轻微问题 (8个)
  - 代码格式问题 (5个文件)
  - 缺少类型标注 (3处)
```

---

## 阶段4: 自动修复 (QA Fixer)

### 4.1 触发自动修复
```bash
# QA Reviewer检测到P2问题，自动触发QA Fixer
/agent qa-fixer "修复QA报告中的问题"
```

### 4.2 QA Fixer工作流程

#### 步骤1: 过滤可修复问题
```markdown
分析QA-REPORT.md:

可自动修复 (8个P2问题):
✅ 代码格式问题 (5个文件)
✅ 缺少类型标注 (3处)

需人工处理 (5个P0/P1问题):
❌ 密码重置功能缺失 (P0)
❌ 请求频率限制 (P0)
❌ 测试覆盖率不足 (P1)
❌ 错误处理缺失 (P1)
❌ 首屏性能 (P1)
```

#### 步骤2: 执行自动修复
```bash
修复1: 代码格式
npm run lint -- --fix
✅ 成功修复5个文件

修复2: 类型标注
添加类型标注到3处函数参数
✅ 成功修复

修复3: 未使用的导入
移除2个未使用的导入
✅ 成功修复
```

#### 步骤3: 验证修复效果
```bash
npm run test
  ✓ All tests passed (24/24)
  Coverage: 78% (+3%)

npm run typecheck
  ✓ No errors

npm run lint
  ✓ No errors
```

#### 步骤4: 生成修复报告
```markdown
生成: FIX-REPORT.md

修复统计:
- 总问题: 13个
- 已修复: 8个 (P2)
- 需人工: 5个 (P0/P1)
- 失败: 0个

修复成功率: 100% (8/8可修复问题)

已修复问题:
✅ 代码格式问题 (5个文件)
✅ 缺少类型标注 (3处)
✅ 未使用的导入 (2处)

需人工处理:
⚠️ 密码重置功能 (P0) - 需实现邮件发送
⚠️ 请求频率限制 (P0) - 需添加中间件
⚠️ 测试覆盖率 (P1) - 需补充测试用例
⚠️ 错误处理 (P1) - 需添加try-catch
⚠️ 首屏性能 (P1) - 需优化打包

下一步: 人工修复P0/P1问题后，重新QA审查
```

### 4.3 重新审查
```bash
# 自动触发重新审查
/agent qa-reviewer "重新验证"

# 输出
QA审查结果: 82/100 (提升7分)

变化:
- 代码质量: 25 → 30 (+5分)
- 测试覆盖: 15 → 17 (+2分)

仍存在问题: 5个P0/P1问题需人工处理

建议: 修复P0问题后可发布
```

---

## 阶段5: 人工修复与最终验证

### 5.1 人工修复P0问题
```bash
开发人员修复:
1. 实现密码重置功能 (2小时)
2. 添加请求频率限制 (1小时)

提交代码:
git commit -m "fix: 添加密码重置和频率限制"
```

### 5.2 最终QA验证
```bash
/agent qa-reviewer "最终验证"

# 输出
✅ QA审查通过
评分: 88/100

| 类别 | 得分 | 满分 | 通过 |
|------|------|------|------|
| 功能完整性 | 38 | 40 | ✅ |
| 代码质量 | 28 | 30 | ✅ |
| 测试覆盖 | 17 | 20 | ⚠️ |
| 性能指标 | 5 | 5 | ✅ |
| 安全检查 | 5 | 5 | ✅ |

结论: PASS - 可以发布

改进建议:
- 继续提升测试覆盖率至80%以上
- 优化首屏加载时间
```

---

## 总结

### 完整流程时间线
```
Day 1 (上午):
  09:00-10:15  规范编写 (Spec Writer) - 75分钟
  10:15-10:30  规范审查 - 15分钟

Day 1 (下午):
  13:00-15:00  数据层实现 - 2小时
  15:00-19:00  后端API实现 - 4小时

Day 2 (上午):
  09:00-13:00  前端UI实现 - 4小时

Day 2 (下午):
  13:00-13:10  QA审查 (首次) - 10分钟
  13:10-13:40  自动修复 - 30分钟
  13:40-13:50  QA审查 (第二次) - 10分钟
  14:00-17:00  人工修复P0问题 - 3小时
  17:00-17:10  QA审查 (最终) - 10分钟

总计: ~14小时
```

### 关键收益

#### 1. 需求明确
- ✅ 规范作为单一事实来源
- ✅ 减少沟通成本
- ✅ 避免理解偏差

#### 2. 质量保障
- ✅ 自动化质量检查
- ✅ 70%问题自动修复
- ✅ 明确的验收标准

#### 3. 效率提升
- ✅ 减少返工时间
- ✅ 并行开发可能
- ✅ 快速迭代

#### 4. 知识沉淀
- ✅ 规范文档可复用
- ✅ 问题模式库积累
- ✅ 最佳实践固化

### 经验教训

#### 成功因素
1. 规范详细完整
2. 验收标准可测试
3. 自动化修复及时
4. 人机协作清晰

#### 可改进点
1. 测试覆盖率仍需提升
2. 性能优化可前置
3. 规范编写可更高效

---

**参考资料**:
- 规范模板: `specs/SPEC-TEMPLATE.md`
- QA流程: `workflows/quality/self-healing.md`
- Agent定义: `agents/spec-writer.md`, `agents/qa-reviewer.md`, `agents/qa-fixer.md`

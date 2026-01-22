# Apollo系统代码规范

> 本规范定义Apollo自进化元系统的编码标准和质量要求

---

## 一、通用原则

### 1.1 SOLID原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **S**ingle Responsibility | 单一职责 | 每个类/函数只做一件事 |
| **O**pen/Closed | 开放封闭 | 对扩展开放，对修改封闭 |
| **L**iskov Substitution | 里氏替换 | 子类可替换父类 |
| **I**nterface Segregation | 接口隔离 | 客户端不依赖不需要的接口 |
| **D**ependency Inversion | 依赖倒置 | 依赖抽象而非具体实现 |

### 1.2 其他核心原则

- **DRY** (Don't Repeat Yourself): 不要重复自己
- **KISS** (Keep It Simple, Stupid): 保持简单
- **YAGNI** (You Aren't Gonna Need It): 你不会需要它
- **Separation of Concerns**: 关注点分离
- **Composition over Inheritance**: 组合优于继承

---

## 二、TypeScript规范

### 2.1 基础规范

#### 模块系统
```typescript
// ✅ 推荐: ES Modules
import { functionName } from './module';
export { functionName };

// ❌ 避免: CommonJS (除非必要)
const module = require('./module');
module.exports = { functionName };
```

#### 类型定义
```typescript
// ✅ 推荐: 优先使用 interface
interface User {
  id: string;
  name: string;
  email: string;
}

// ⚠️ 仅在需要联合类型或工具类型时使用 type
type ID = string | number;
type ReadonlyUser = Readonly<User>;
```

#### 空值处理
```typescript
// ✅ 推荐: 使用可选链和空值合并
const userName = user?.profile?.name ?? 'Anonymous';

// ❌ 避免: 多层条件判断
const userName = user && user.profile && user.profile.name
  ? user.profile.name
  : 'Anonymous';
```

### 2.2 命名约定

| 类型 | 规则 | 示例 |
|------|------|------|
| 变量/函数 | camelCase | `getUserById`, `userCount` |
| 类/接口 | PascalCase | `UserService`, `IUserRepository` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `API_BASE_URL` |
| 枚举 | PascalCase (键也用PascalCase) | `enum Status { Active, Inactive }` |
| 私有成员 | 前缀 `_` 或 `#` | `_privateMethod()`, `#privateField` |
| 泛型参数 | 单个大写字母或描述性名称 | `T`, `TUser`, `TResponse` |

### 2.3 函数设计

```typescript
// ✅ 推荐: 纯函数，无副作用
function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// ❌ 避免: 修改参数或外部状态
function calculateTotal(items: Item[]): number {
  let total = 0;
  items.forEach(item => {
    item.processed = true; // ❌ 修改了参数
    total += item.price;
  });
  globalTotal = total; // ❌ 修改了外部状态
  return total;
}
```

### 2.4 异步处理

```typescript
// ✅ 推荐: async/await
async function fetchUser(id: string): Promise<User> {
  try {
    const response = await fetch(`/api/users/${id}`);
    return await response.json();
  } catch (error) {
    throw new Error(`Failed to fetch user: ${error.message}`);
  }
}

// ⚠️ 避免: Promise链 (除非必要)
function fetchUser(id: string): Promise<User> {
  return fetch(`/api/users/${id}`)
    .then(response => response.json())
    .catch(error => {
      throw new Error(`Failed to fetch user: ${error.message}`);
    });
}
```

---

## 三、Python规范

### 3.1 基础规范

遵循 **PEP 8** 标准

#### 导入顺序
```python
# 1. 标准库
import os
import sys

# 2. 第三方库
import numpy as np
import pandas as pd

# 3. 本地模块
from .models import User
from .utils import validate_email
```

#### 类型注解
```python
# ✅ 推荐: 使用类型注解
def get_user_by_id(user_id: int) -> User | None:
    """获取用户信息

    Args:
        user_id: 用户ID

    Returns:
        User对象或None
    """
    return database.query(User).filter(User.id == user_id).first()

# ❌ 避免: 无类型注解
def get_user_by_id(user_id):
    return database.query(User).filter(User.id == user_id).first()
```

### 3.2 命名约定

| 类型 | 规则 | 示例 |
|------|------|------|
| 变量/函数 | snake_case | `get_user_by_id`, `user_count` |
| 类 | PascalCase | `UserService`, `DatabaseConnection` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `API_BASE_URL` |
| 私有成员 | 前缀 `_` | `_private_method()`, `_internal_state` |
| 双下划线 | 名称改写 | `__mangled` |

### 3.3 上下文管理器

```python
# ✅ 推荐: 使用 with 语句
with open('file.txt', 'r') as f:
    content = f.read()

# ❌ 避免: 手动管理资源
f = open('file.txt', 'r')
content = f.read()
f.close()
```

---

## 四、错误处理

### 4.1 TypeScript错误处理

```typescript
// ✅ 推荐: 自定义错误类
class ValidationError extends Error {
  constructor(
    message: string,
    public field: string,
    public value: unknown
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

// 使用
async function createUser(data: UserInput): Promise<User> {
  if (!isValidEmail(data.email)) {
    throw new ValidationError(
      'Invalid email format',
      'email',
      data.email
    );
  }

  try {
    return await userRepository.create(data);
  } catch (error) {
    if (error instanceof DatabaseError) {
      // 处理数据库错误
      throw new Error(`Database error: ${error.message}`);
    }
    throw error; // 重新抛出未知错误
  }
}
```

### 4.2 Python错误处理

```python
# ✅ 推荐: 具体的异常类型
class ValidationError(Exception):
    """验证错误"""
    def __init__(self, message: str, field: str, value: any):
        super().__init__(message)
        self.field = field
        self.value = value

# 使用
def create_user(data: dict) -> User:
    if not is_valid_email(data['email']):
        raise ValidationError(
            'Invalid email format',
            field='email',
            value=data['email']
        )

    try:
        return user_repository.create(data)
    except DatabaseError as e:
        # 处理特定错误
        raise Exception(f"Database error: {str(e)}") from e
    except Exception:
        # 记录并重新抛出
        logger.exception("Unexpected error in create_user")
        raise
```

---

## 五、测试规范

### 5.1 目录结构

```
src/
├── module/
│   ├── service.ts
│   ├── service.test.ts      # ✅ 同目录测试
│   ├── repository.ts
│   └── repository.test.ts
```

### 5.2 测试命名

```typescript
// ✅ 推荐: 描述性测试名称
describe('UserService', () => {
  describe('createUser', () => {
    it('should create user with valid data', async () => {
      // Arrange
      const userData = { name: 'John', email: 'john@example.com' };

      // Act
      const user = await userService.createUser(userData);

      // Assert
      expect(user.id).toBeDefined();
      expect(user.name).toBe('John');
    });

    it('should throw ValidationError when email is invalid', async () => {
      // Arrange
      const userData = { name: 'John', email: 'invalid' };

      // Act & Assert
      await expect(userService.createUser(userData))
        .rejects
        .toThrow(ValidationError);
    });
  });
});
```

### 5.3 测试覆盖要求

| 代码类型 | 覆盖率要求 | 说明 |
|----------|-----------|------|
| 核心业务逻辑 | ≥90% | 必须全面测试 |
| API接口 | ≥80% | 覆盖主要路径 |
| 工具函数 | ≥85% | 包含边界情况 |
| UI组件 | ≥70% | 关键交互测试 |

---

## 六、文档规范

### 6.1 代码注释

```typescript
/**
 * 根据ID获取用户信息
 *
 * @param userId - 用户ID
 * @param options - 查询选项
 * @param options.includeDeleted - 是否包含已删除用户
 * @returns 用户对象，如果不存在返回null
 * @throws {ValidationError} 当userId无效时
 * @throws {DatabaseError} 当数据库查询失败时
 *
 * @example
 * ```typescript
 * const user = await getUserById('123');
 * if (user) {
 *   console.log(user.name);
 * }
 * ```
 */
async function getUserById(
  userId: string,
  options?: { includeDeleted?: boolean }
): Promise<User | null> {
  // 实现...
}
```

### 6.2 README结构

```markdown
# 项目名称

简短描述 (1-2句话)

## 功能特性

- 特性1
- 特性2

## 快速开始

### 安装
\`\`\`bash
npm install
\`\`\`

### 运行
\`\`\`bash
npm start
\`\`\`

## API文档

[链接或简要说明]

## 开发

### 技术栈
- TypeScript 5.x
- Node.js 20.x

### 项目结构
[说明]

### 测试
\`\`\`bash
npm test
\`\`\`

## 许可证

MIT
```

---

## 七、性能优化

### 7.1 TypeScript性能

```typescript
// ✅ 推荐: 避免不必要的计算
const MemoizedComponent = React.memo(({ data }) => {
  const processedData = useMemo(() => {
    return expensiveOperation(data);
  }, [data]);

  return <div>{processedData}</div>;
});

// ❌ 避免: 每次渲染都重新计算
const Component = ({ data }) => {
  const processedData = expensiveOperation(data); // 性能问题
  return <div>{processedData}</div>;
};
```

### 7.2 数据库查询优化

```typescript
// ✅ 推荐: 批量查询
async function getUsersWithPosts(userIds: string[]): Promise<User[]> {
  return await database.query(User)
    .whereIn('id', userIds)
    .include('posts') // 使用关联加载，避免N+1问题
    .execute();
}

// ❌ 避免: N+1查询
async function getUsersWithPosts(userIds: string[]): Promise<User[]> {
  const users = await database.query(User).whereIn('id', userIds).execute();

  for (const user of users) {
    user.posts = await database.query(Post).where('userId', user.id).execute();
    // ❌ 每个用户都触发一次查询
  }

  return users;
}
```

---

## 八、安全规范

### 8.1 输入验证

```typescript
// ✅ 推荐: 使用验证库
import { z } from 'zod';

const UserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().int().min(0).max(120).optional(),
});

async function createUser(input: unknown): Promise<User> {
  const data = UserSchema.parse(input); // 自动验证和类型推断
  return await userRepository.create(data);
}
```

### 8.2 敏感信息处理

```typescript
// ✅ 推荐: 从环境变量读取
const config = {
  database: {
    host: process.env.DB_HOST,
    password: process.env.DB_PASSWORD, // 永远不硬编码
  },
  apiKey: process.env.API_KEY,
};

// ❌ 禁止: 硬编码敏感信息
const config = {
  apiKey: 'sk-1234567890abcdef', // ❌ 安全风险
};
```

### 8.3 SQL注入防护

```typescript
// ✅ 推荐: 参数化查询
async function getUserByEmail(email: string): Promise<User | null> {
  return await database.query(
    'SELECT * FROM users WHERE email = $1',
    [email] // 参数化
  );
}

// ❌ 禁止: 字符串拼接
async function getUserByEmail(email: string): Promise<User | null> {
  return await database.query(
    `SELECT * FROM users WHERE email = '${email}'` // ❌ SQL注入风险
  );
}
```

---

## 九、Git规范

### 9.1 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type类型**:
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式(不影响逻辑)
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具配置

**示例**:
```
feat(auth): add JWT authentication

- Implement JWT token generation
- Add refresh token mechanism
- Update user login flow

Closes #123
```

### 9.2 分支策略

```
main          # 生产环境
  ↑
develop       # 开发主分支
  ↑
  ├── feature/user-auth    # 功能分支
  ├── bugfix/login-error   # Bug修复分支
  └── hotfix/security-fix  # 紧急修复分支
```

---

## 十、代码审查清单

### 10.1 必查项

- [ ] 代码符合本规范
- [ ] 测试覆盖率达标
- [ ] 无安全漏洞
- [ ] 无性能问题
- [ ] 文档已更新
- [ ] 提交信息清晰

### 10.2 推荐工具

| 工具 | 用途 |
|------|------|
| ESLint | TypeScript/JavaScript代码检查 |
| Prettier | 代码格式化 |
| Husky | Git hooks |
| Jest | 测试框架 |
| SonarQube | 代码质量分析 |

---

## 附录: 快速参考

### TypeScript
```typescript
// 类型定义
interface User { id: string; name: string; }

// 函数
async function fetchUser(id: string): Promise<User> { }

// 错误处理
try { } catch (error) { }
```

### Python
```python
# 类型注解
def get_user(user_id: int) -> User | None:
    pass

# 上下文管理
with open('file.txt') as f:
    content = f.read()
```

### Git
```bash
# 提交
git commit -m "feat(module): add feature"

# 分支
git checkout -b feature/new-feature
```

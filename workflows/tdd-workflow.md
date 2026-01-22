# 测试驱动开发 (TDD) 工作流

## 概述
测试驱动开发是一种先写测试、后写实现的开发方法。

## TDD 循环

```
┌──────────────┐
│   编写测试   │ ← 红色: 测试失败
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   编写代码   │ ← 绿色: 测试通过
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   重构代码   │ ← 蓝色: 保持测试通过
└──────┬───────┘
       │
       └────────→ 重复
```

## 工作流步骤

### 1. 红色阶段 - 编写失败的测试

```typescript
// 1. 先编写测试
describe('Calculator', () => {
  it('should add two numbers', () => {
    const calc = new Calculator();
    expect(calc.add(2, 3)).toBe(5);
  });
});
```

执行验证:
```bash
npm test -- --watch
# 确认测试失败
```

### 2. 绿色阶段 - 实现功能

```typescript
// 2. 编写最简实现
class Calculator {
  add(a: number, b: number): number {
    return a + b;
  }
}
```

执行验证:
```bash
npm test
# 确认测试通过
```

### 3. 蓝色阶段 - 重构

```typescript
// 3. 优化代码 (保持测试通过)
class Calculator {
  add(...numbers: number[]): number {
    return numbers.reduce((sum, n) => sum + n, 0);
  }
}
```

## 使用 Claude Code 的 TDD 流程

### 启动 TDD 模式
```
我想使用 TDD 开发 [功能描述]。请先帮我编写测试用例。
```

### Claude 的响应模式

1. **分析需求** - 理解功能需求
2. **设计测试用例** - 覆盖正常路径和边界情况
3. **编写测试代码** - 创建测试文件
4. **验证测试失败** - 运行测试确认红色状态
5. **编写实现** - 最小化实现
6. **验证测试通过** - 运行测试确认绿色状态
7. **重构** - 优化代码结构

## 测试类型

### 单元测试
```typescript
describe('UserService', () => {
  let service: UserService;
  let mockRepo: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockRepo = createMock<UserRepository>();
    service = new UserService(mockRepo);
  });

  it('should create user', async () => {
    mockRepo.save.mockResolvedValue({ id: 1, name: 'Test' });

    const result = await service.createUser({ name: 'Test' });

    expect(result.id).toBe(1);
    expect(mockRepo.save).toHaveBeenCalledWith({ name: 'Test' });
  });
});
```

### 集成测试
```typescript
describe('API Integration', () => {
  it('POST /users should create user', async () => {
    const response = await request(app)
      .post('/users')
      .send({ name: 'Test', email: 'test@example.com' });

    expect(response.status).toBe(201);
    expect(response.body.id).toBeDefined();
  });
});
```

### E2E 测试
```typescript
describe('User Registration Flow', () => {
  it('should complete registration', async () => {
    await page.goto('/register');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'SecurePass123!');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/dashboard');
  });
});
```

## 测试覆盖率目标

| 指标 | 最低要求 | 推荐目标 |
|------|----------|----------|
| 行覆盖率 | 70% | 85%+ |
| 分支覆盖率 | 60% | 80%+ |
| 函数覆盖率 | 80% | 90%+ |

## 常用测试模式

### Arrange-Act-Assert
```typescript
it('should update user name', () => {
  // Arrange
  const user = new User('old-name');

  // Act
  user.updateName('new-name');

  // Assert
  expect(user.name).toBe('new-name');
});
```

### Given-When-Then
```typescript
it('given valid credentials, when login, then return token', async () => {
  // Given
  const credentials = { email: 'user@test.com', password: 'pass' };

  // When
  const result = await authService.login(credentials);

  // Then
  expect(result.token).toBeDefined();
});
```

## 注意事项

1. **测试应该独立** - 测试之间不应有依赖
2. **测试应该快速** - 单元测试应在毫秒级完成
3. **测试应该可重复** - 每次运行结果一致
4. **测试命名要清晰** - 描述测试的目的和预期
5. **避免测试实现细节** - 测试行为,不测试实现

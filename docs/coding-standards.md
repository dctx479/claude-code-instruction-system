# 代码规范

## TypeScript

### 模块系统
- 使用 ES modules (`import`/`export`)
- 避免使用 CommonJS (`require`)

### 类型定义
- 优先使用 `interface` 而非 `type`
- 启用严格模式: `"strict": true`
- 为所有函数参数和返回值添加类型注解

### 命名规范
- 文件: kebab-case (e.g., `user-service.ts`)
- 类: PascalCase (e.g., `UserService`)
- 函数: camelCase (e.g., `getUserById`)
- 常量: UPPER_SNAKE_CASE (e.g., `MAX_RETRY_COUNT`)
- 接口: PascalCase, 不使用 `I` 前缀 (e.g., `User`, not `IUser`)

### 示例

```typescript
// ✅ 推荐
interface User {
  id: string;
  name: string;
  email: string;
}

export function getUserById(id: string): Promise<User> {
  // ...
}

// ❌ 避免
type User = {
  id: string;
  name: string;
  email: string;
}

export function getUserById(id) {
  // ...
}
```

---

## 测试

### 测试文件组织
- 测试文件: 同目录 `*.test.ts`
- 覆盖率目标: >80%
- TDD 优先

### 测试框架
- 单元测试: Vitest
- 集成测试: Vitest
- E2E 测试: Playwright

### 示例

```typescript
// user-service.ts
export class UserService {
  async getUserById(id: string): Promise<User> {
    // ...
  }
}

// user-service.test.ts
import { describe, it, expect } from 'vitest';
import { UserService } from './user-service';

describe('UserService', () => {
  it('should get user by id', async () => {
    const service = new UserService();
    const user = await service.getUserById('123');
    expect(user.id).toBe('123');
  });
});
```

---

## Markdown

### 文档结构
- 使用 ATX 风格标题 (`#`, `##`, `###`)
- 代码块使用语言标识符
- 链接使用相对路径

### 示例

```markdown
# 标题

## 子标题

代码示例：

\`\`\`typescript
const foo = 'bar';
\`\`\`

参见: [相关文档](./related.md)
```

---

## Shell 脚本

### 最佳实践
- 使用 `#!/bin/bash` shebang
- 启用错误检查: `set -e`
- 引用所有变量: `"$VAR"`
- 使用 `shellcheck` 验证

### 示例

```bash
#!/bin/bash
set -e

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

main() {
  local input="$1"
  echo "Processing: $input"
}

main "$@"
```

---

## Python

### 代码风格
- 遵循 PEP 8
- 使用类型提示 (Python 3.9+)
- 使用 `black` 格式化
- 使用 `pylint` 检查

### 示例

```python
from typing import List, Optional

def get_user_by_id(user_id: str) -> Optional[dict]:
    """获取用户信息

    Args:
        user_id: 用户 ID

    Returns:
        用户信息字典，如果不存在返回 None
    """
    # ...
    pass
```

---

## Git 提交规范

### 提交消息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具链

### 示例

```
feat(auth): add user authentication

- Implement JWT token generation
- Add login/logout endpoints
- Add authentication middleware

Closes #123
```

---

## 详细参考

更多详细规范参见:
- TypeScript: `.claude/reference/typescript-style-guide.md`
- Testing: `.claude/reference/testing-guide.md`
- Git: `.claude/reference/git-workflow.md`

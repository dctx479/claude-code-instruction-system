---
name: two-stage-output
description: 两阶段输出规范 - 策划稿确认后再生成实现稿，避免无效迭代
license: MIT
metadata:
  category: system
  tags:
  - output-standard
  - planning
  - implementation
  - confirmation
  integration:
  - spec-writer
  - code-generator
  version: 1.0.0
  trigger:
  - /two-stage
  - 分阶段输出
  - 策划稿
disable-model-invocation: false
---

# Two-Stage Output Skill

> 灵感来源: AI PPT Agent 的策划与设计分离
> 
> 核心理念: **先策划后实现**，策划稿确认后再动手

## 功能概述

将 Agent 输出分为两个阶段：
1. **策划稿**（Plain Design）- 结构规划，无具体实现
2. **实现稿**（Full Implementation）- 完整代码和设计

---

## 核心理念

### 为什么要分两阶段？

**传统方式的问题**:
```
用户: 实现用户列表页面
Agent: [直接生成 500 行代码]
用户: 不对，我要的是另一种布局
Agent: [重新生成 500 行代码]
用户: 还是不对...
```

**两阶段方式**:
```
用户: 实现用户列表页面
Agent: [生成策划稿，30 行结构说明]
用户: 布局改成这样...
Agent: [更新策划稿]
用户: OK，可以实现了
Agent: [生成 500 行完整代码，一次到位]
```

**优势**:
- ✅ **降低沟通成本** - 策划稿简洁，快速确认
- ✅ **减少无效迭代** - 结构确认后再写代码
- ✅ **提高质量** - 策划清晰，实现不偏离
- ✅ **节省 token** - 避免反复生成大量代码

---

## 阶段定义

### Stage 1: 策划稿（Plain Design）

**目的**: 确认需求理解和整体结构

**内容**:
1. **结构规划** - 整体布局和组件划分
2. **数据流设计** - 数据来源和状态管理
3. **交互逻辑** - 用户操作和系统响应
4. **技术选型** - 关键技术决策
5. **验收标准** - 如何验证功能完成

**格式**: 简洁的 Markdown，无代码细节

**示例**:
```markdown
## 策划稿：用户列表页面

### 1. 结构规划

#### 布局（三区域）
┌─────────────────────────────────┐
│ 顶部栏: 搜索 + 筛选 + 新增按钮  │
├─────────────────────────────────┤
│ 主体: 用户表格                  │
│ - 列: 头像/姓名/邮箱/状态/操作  │
│ - 分页: 底部分页器              │
├─────────────────────────────────┤
│ 底部: 状态栏（已选/总数）       │
└─────────────────────────────────┘

#### 组件划分
- UserListPage（容器组件）
  - SearchBar（搜索栏）
  - FilterPanel（筛选面板）
  - UserTable（用户表格）
  - Pagination（分页器）

### 2. 数据流设计

#### 数据来源
- API: `GET /api/users?page=1&limit=20&search=&status=`
- 状态管理: React useState

#### 状态定义
```typescript
interface State {
  users: User[]
  loading: boolean
  error: Error | null
  pagination: {
    page: number
    limit: number
    total: number
  }
  filters: {
    search: string
    status: 'all' | 'active' | 'inactive'
  }
}
```

### 3. 交互逻辑

#### 用户操作
1. 搜索: 输入 → 防抖 500ms → 请求 API
2. 筛选: 选择状态 → 立即请求 API
3. 分页: 点击页码 → 请求对应页
4. 点击行: 跳转用户详情页
5. 操作: 编辑/删除 → 确认 → API 请求

#### 加载状态
- 初始加载: 显示骨架屏
- 搜索/筛选: 表格 loading 遮罩
- 操作失败: Toast 提示

### 4. 技术选型

- 框架: React 18 + TypeScript
- 状态: useState（无需 Redux，状态简单）
- UI 库: Ant Design (Table + Pagination)
- 请求: axios + React Query (缓存 + 重试)

### 5. 验收标准

- [ ] 页面正常加载，显示用户列表
- [ ] 搜索功能正常，500ms 防抖
- [ ] 筛选功能正常，状态切换即时
- [ ] 分页功能正常，页码显示准确
- [ ] 点击行跳转正确
- [ ] 编辑/删除操作正常
- [ ] 加载和错误状态正确显示
- [ ] 响应式布局，移动端可用

---

**请确认以上策划稿是否符合您的需求。**
**确认后，我将生成完整的实现代码。**
```

### Stage 2: 实现稿（Full Implementation）

**目的**: 生成可直接使用的完整代码

**内容**:
1. **完整代码** - 所有组件、样式、类型定义
2. **配置文件** - 路由、API 配置等
3. **测试用例** - 单元测试和集成测试
4. **使用文档** - 如何运行和部署

**格式**: 完整的代码文件，可直接运行

---

## 输出模板

### 策划稿模板

```markdown
# 策划稿：[功能名称]

## 1. 结构规划

### 整体布局
[ASCII 图或描述]

### 组件划分
- 组件树结构
- 各组件职责

### 目录结构
```
src/
  components/
    [组件名]/
  pages/
    [页面名]/
  hooks/
    [钩子名].ts
```

## 2. 数据流设计

### 数据来源
- API 端点
- 请求参数
- 响应格式

### 状态管理
- 全局状态
- 本地状态
- 状态更新逻辑

### 数据流向
[数据流图]

## 3. 交互逻辑

### 用户操作
1. 操作 A → 系统响应
2. 操作 B → 系统响应

### 状态转换
[状态转换图]

### 错误处理
- 网络错误
- 业务错误
- 边界情况

## 4. 技术选型

### 核心技术
- 框架: [...]
- 语言: [...]
- 库: [...]

### 选型理由
- 技术 A: 理由...
- 技术 B: 理由...

### 技术风险
- 风险 1: 缓解措施...

## 5. 验收标准

### 功能验收
- [ ] 功能点 1
- [ ] 功能点 2

### 质量验收
- [ ] 代码覆盖率 > 80%
- [ ] 无 TypeScript 错误
- [ ] 通过 ESLint

### 性能验收
- [ ] 首屏加载 < 2s
- [ ] 交互响应 < 100ms

---

**确认点**:
1. 结构是否符合预期？
2. 技术选型是否合适？
3. 验收标准是否明确？

**请确认后，我将生成实现稿。**
```

### 实现稿模板

```markdown
# 实现稿：[功能名称]

## 文件清单

```
src/
  components/
    UserList/
      index.tsx           # 主组件
      UserList.module.css # 样式
      UserList.test.tsx   # 测试
  types/
    user.ts               # 类型定义
  api/
    users.ts              # API 接口
  hooks/
    useUsers.ts           # 自定义钩子
```

## 代码实现

### 1. 类型定义 (types/user.ts)

```typescript
[完整代码]
```

### 2. API 接口 (api/users.ts)

```typescript
[完整代码]
```

### 3. 自定义钩子 (hooks/useUsers.ts)

```typescript
[完整代码]
```

### 4. 主组件 (components/UserList/index.tsx)

```typescript
[完整代码]
```

### 5. 样式 (components/UserList/UserList.module.css)

```css
[完整代码]
```

### 6. 测试 (components/UserList/UserList.test.tsx)

```typescript
[完整代码]
```

## 使用说明

### 安装依赖

```bash
npm install axios react-query
```

### 使用方式

```tsx
import UserList from '@/components/UserList';

function App() {
  return <UserList />;
}
```

### 环境变量

```env
REACT_APP_API_BASE_URL=https://api.example.com
```

### 运行测试

```bash
npm test -- UserList.test.tsx
```

## 验收确认

请按策划稿中的验收标准逐项测试：

- [ ] 功能验收（5/5 项通过）
- [ ] 质量验收（3/3 项通过）
- [ ] 性能验收（2/2 项通过）

---

**实现完成！**
```

---

## 使用流程

### 完整流程

```
用户请求
   ↓
Agent 生成策划稿
   ↓
用户审查策划稿
   ↓
   ├─ 不满意 → 修改策划稿 → 重新审查
   └─ 满意 ✓
       ↓
   用户确认（明确说"可以"/"确认"/"OK"）
       ↓
   Agent 生成实现稿
       ↓
   交付完成
```

### 关键确认点

**策划稿确认**:
- 结构是否符合预期？
- 技术选型是否合适？
- 验收标准是否明确？

**只有用户明确确认后，才生成实现稿！**

---

## 适用场景

### 适合使用两阶段的场景

✅ **复杂功能** - 结构复杂，需要仔细规划
✅ **新需求** - 用户需求不明确，需要对齐理解
✅ **大型重构** - 影响范围广，需要先确认方案
✅ **技术选型** - 多个方案可选，需要讨论决策
✅ **团队协作** - 多人参与，需要统一思路

### 不必使用两阶段的场景

❌ **简单修改** - 改个文案、调个颜色
❌ **明确需求** - 用户已经说得很清楚
❌ **标准功能** - CRUD、登录等标准功能
❌ **紧急修复** - Bug 修复，快速上线

**原则**: 策划阶段的沟通成本 < 重复实现的成本 → 使用两阶段

---

## 与其他 Skill 集成

### 与 spec-writer 集成

```
spec-research (需求调研)
   ↓
spec-writer (编写 Spec)
   ↓
two-stage-output (分阶段实现)
   ├─ Stage 1: 策划稿
   └─ Stage 2: 实现稿
```

### 与 code-generator 集成

```
用户: 生成用户管理模块
   ↓
code-generator 识别到复杂功能
   ↓
自动切换到两阶段模式
   ├─ Stage 1: 生成架构设计
   └─ Stage 2: 生成完整代码
```

---

## 最佳实践

### 1. 策划稿要简洁

❌ **过于详细**:
```markdown
## 组件代码
```tsx
function UserList() {
  const [users, setUsers] = useState([]);
  // ... 100 行代码
}
```
```

✅ **恰到好处**:
```markdown
## 组件设计
- UserList: 容器组件，管理用户列表状态
- 状态: users, loading, error
- 交互: 搜索、筛选、分页
```

### 2. 确认点要明确

❌ **模糊**:
```
请确认是否可以？
```

✅ **具体**:
```
请确认：
1. 布局是否符合预期？
2. 技术选型是否合适？
3. 验收标准是否明确？
```

### 3. 等待明确确认

❌ **自作主张**:
```
[策划稿]
我猜你应该满意，开始实现...
```

✅ **等待确认**:
```
[策划稿]
请确认后，我再生成实现稿。
[等待用户回复]
```

---

## 注意事项

### 1. 不要跳过策划稿

即使你觉得需求很明确，也要先生成策划稿给用户确认。
用户的"明确需求"可能跟你理解的不一样。

### 2. 策划稿不是伪代码

策划稿是给人看的结构说明，不是给机器看的伪代码。
用自然语言 + 简单图示，不要写接近真实代码的伪代码。

### 3. 实现稿要完整

既然用户已经确认了策划稿，实现稿就要一次到位，不要留半成品。

---

## 相关文档

- **灵感来源**: `analysis/ai-ppt-agent-analysis.md`
- **方法论**: 策划与设计分离
- **集成 Skill**: `spec-writer`, `code-generator`

---

**版本**: v1.0.0  
**创建日期**: 2025-01-23  
**维护者**: Taiyi System Team

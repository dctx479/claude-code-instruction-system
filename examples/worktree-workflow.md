# Git Worktree工作流完整示例

真实场景的完整演示，展示如何使用Worktree实现并行开发。

## 场景背景

**项目**: 电商平台API
**Sprint目标**: 实现用户认证、商品管理、订单系统三个模块
**团队**: 3个开发者（或3个AI Agent）
**时间**: 2周Sprint
**挑战**: 三个模块需要同时开发，但有部分依赖关系

---

## 第一天：Sprint启动

### 09:00 - Sprint规划会议

```markdown
## Sprint Backlog

1. **任务A**: 用户认证系统 (task-001)
   - JWT token生成和验证
   - 用户登录/登出API
   - 优先级: 高（其他模块依赖）
   - 预估: 3天
   - 负责人: Agent-Coder-1

2. **任务B**: 商品管理模块 (task-002)
   - 商品CRUD API
   - 图片上传
   - 优先级: 中
   - 预估: 5天
   - 负责人: Agent-Coder-2

3. **任务C**: 订单系统 (task-003)
   - 订单创建和查询
   - 支付集成
   - 优先级: 高
   - 预估: 5天
   - 负责人: Agent-Coder-3
```

### 09:30 - 创建Worktrees

```bash
# 初始化项目结构
cd /workspace/ecommerce-api
git checkout main
git pull origin main

# Agent-Coder-1: 创建认证模块worktree
/worktree-create task-001 feature-authentication main

# 输出:
# ✅ Worktree创建成功!
# 📁 路径: /workspace/worktrees/task-001
# 🌿 分支: feature-authentication
# 🆔 任务ID: task-001

# Agent-Coder-2: 创建商品管理worktree
/worktree-create task-002 feature-product-management main

# Agent-Coder-3: 创建订单系统worktree
/worktree-create task-003 feature-order-system main

# 查看所有worktrees
/worktree-list
```

**输出**:
```
📦 活动Worktrees (3个)

🆔 task-001    🌿 feature-authentication      ✅ active    👤 coder-1    📅 刚刚
🆔 task-002    🌿 feature-product-management  ✅ active    👤 coder-2    📅 刚刚
🆔 task-003    🌿 feature-order-system        ✅ active    👤 coder-3    📅 刚刚

💡 提示: 所有worktrees已就绪，可以开始并行开发
```

### 10:00 - 配置开发环境

```bash
# Agent-Coder-1: 配置task-001环境
cd /workspace/worktrees/task-001

# 安装依赖
npm install

# 配置环境变量
cat > .env.local <<EOF
DATABASE_URL=postgresql://localhost:5432/ecom_auth
JWT_SECRET=dev-secret-001
PORT=3001
EOF

# 启动开发服务器
npm run dev -- --port 3001 &

# Agent-Coder-2和3做类似配置，使用不同端口
# task-002: port 3002
# task-003: port 3003
```

---

## 第一天下午：并行开发

### 14:00 - Agent-Coder-1 (task-001)

```bash
cd /workspace/worktrees/task-001

# 创建认证模块结构
mkdir -p src/auth
touch src/auth/jwt.service.ts
touch src/auth/auth.controller.ts
touch src/auth/auth.module.ts

# 实现JWT服务
cat > src/auth/jwt.service.ts <<EOF
import jwt from 'jsonwebtoken';

export class JwtService {
  private secret = process.env.JWT_SECRET || 'default-secret';

  generateToken(userId: string): string {
    return jwt.sign({ userId }, this.secret, { expiresIn: '7d' });
  }

  verifyToken(token: string): { userId: string } | null {
    try {
      return jwt.verify(token, this.secret) as { userId: string };
    } catch {
      return null;
    }
  }
}
EOF

# 提交第一个功能
git add src/auth/
git commit -m "feat(auth): implement JWT service"

# 推送到远程
git push -u origin feature-authentication
```

### 14:30 - Agent-Coder-2 (task-002)

```bash
cd /workspace/worktrees/task-002

# 创建商品管理模块
mkdir -p src/products
touch src/products/product.entity.ts
touch src/products/product.controller.ts
touch src/products/product.service.ts

# 实现Product实体
cat > src/products/product.entity.ts <<EOF
export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  imageUrl?: string;
  createdAt: Date;
  updatedAt: Date;
}
EOF

git add src/products/
git commit -m "feat(products): define product entity"
git push -u origin feature-product-management
```

### 15:00 - Agent-Coder-3 (task-003)

```bash
cd /workspace/worktrees/task-003

# 创建订单系统模块
mkdir -p src/orders
touch src/orders/order.entity.ts
touch src/orders/order.controller.ts
touch src/orders/order.service.ts

# 实现Order实体
# ... 类似的开发过程 ...

git add src/orders/
git commit -m "feat(orders): define order entity"
git push -u origin feature-order-system
```

---

## 第二天：处理依赖

### 09:00 - 认证模块完成

```bash
# Agent-Coder-1完成认证功能
cd /workspace/worktrees/task-001

# 最后的提交
git add .
git commit -m "feat(auth): complete authentication APIs"
git push

# 创建Pull Request
gh pr create \
  --title "feat: User authentication system" \
  --body "实现JWT认证，包括登录、登出和token验证" \
  --base main \
  --head feature-authentication

# PR URL: https://github.com/org/ecommerce-api/pull/101
```

### 10:00 - 其他模块需要认证功能

```bash
# Agent-Coder-2: 商品管理需要认证
cd /workspace/worktrees/task-002

# 方案1: Cherry-pick认证相关commits
git fetch origin feature-authentication
git cherry-pick <auth-commit-hash>

# 方案2: 临时合并（用于测试）
git merge --no-commit origin/feature-authentication
# 测试通过后
git merge --abort  # 回滚，等待正式合并

# 方案3（推荐）: 等待认证PR合并后同步
# 认证PR被合并到main后
git fetch origin main
git rebase origin/main

# 现在可以使用认证功能了
```

---

## 第三天：并行测试

### 11:00 - 同时运行三个测试套件

```bash
# 终端1: 测试task-001
cd /workspace/worktrees/task-001
npm test -- --watch

# 终端2: 测试task-002
cd /workspace/worktrees/task-002
npm test -- --watch

# 终端3: 测试task-003
cd /workspace/worktrees/task-003
npm test -- --watch

# 三个测试套件完全隔离，互不干扰
```

### 14:00 - 集成测试

```bash
# 创建临时集成测试worktree
git worktree add /workspace/worktrees/integration-test -b test-integration

cd /workspace/worktrees/integration-test

# 合并所有功能分支
git merge --no-ff origin/feature-authentication
git merge --no-ff origin/feature-product-management
git merge --no-ff origin/feature-order-system

# 运行集成测试
npm run test:integration

# 测试通过后，推送或创建PR
# 测试失败则返回各worktree修复
```

---

## 第五天：处理Bug

### 紧急Bug报告

```
生产环境Bug: 内存泄漏导致服务崩溃
需要立即修复
```

### 10:00 - 创建Hotfix Worktree

```bash
# 不影响现有开发，创建独立hotfix worktree
git worktree add /workspace/worktrees/hotfix-memory-leak -b hotfix-memory-leak production

cd /workspace/worktrees/hotfix-memory-leak

# 诊断和修复
# ... 调试过程 ...

# 修复完成
git add .
git commit -m "fix: resolve memory leak in event handlers"
git push origin hotfix-memory-leak

# 快速合并到production和main
git checkout production
git merge hotfix-memory-leak
git push origin production

git checkout main
git merge hotfix-memory-leak
git push origin main

# 清理hotfix worktree
cd /workspace/ecommerce-api
git worktree remove /workspace/worktrees/hotfix-memory-leak
```

**关键点**:
- ✅ 其他三个开发worktrees完全不受影响
- ✅ 并行开发继续进行
- ✅ Hotfix独立完成和部署

---

## 第八天：功能合并

### 商品管理功能完成

```bash
# Agent-Coder-2完成开发
cd /workspace/worktrees/task-002

# 最后同步main分支
git fetch origin main
git rebase origin/main

# 解决可能的冲突
# ... 冲突解决 ...

# 运行最终测试
npm test
npm run test:e2e

# 创建PR
gh pr create \
  --title "feat: Product management system" \
  --body "完整的商品CRUD API，支持图片上传" \
  --base main \
  --head feature-product-management

# PR合并后，清理worktree
cd /workspace/ecommerce-api
/worktree-cleanup task-002
```

---

## 第十天：Sprint回顾

### 查看最终状态

```bash
/worktree-list --format detailed
```

**输出**:
```
╔═══════════════════════════════════════════════════════════════════════
║ 📦 Worktrees状态报告
║ 生成时间: 2026-01-26 16:00:00
║ 总计: 1个活动 | 2个已完成
╚═══════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│ 🆔 Task ID: task-003 (仍在进行中)                                    │
│ 🌿 Branch: feature-order-system                                      │
│ 📊 Status: active                                                    │
│ 📅 Age: 10天                                                         │
│ 💡 建议: 接近完成，预计明天可以合并                                  │
└─────────────────────────────────────────────────────────────────────┘

📊 Sprint统计:
- ✅ 已完成: 2个功能 (认证、商品管理)
- 🚧 进行中: 1个功能 (订单系统)
- 🐛 Hotfix: 1个紧急修复
- 💾 释放磁盘: 400MB (清理2个worktrees)
```

---

## 实用技巧总结

### 1. 快速切换Worktree

```bash
# 创建shell函数
wt() {
  cd /workspace/worktrees/$1
}

# 使用
wt task-001  # 立即切换到task-001
wt task-002  # 立即切换到task-002
```

### 2. 统一操作所有Worktrees

```bash
# 批量同步main分支
for wt in /workspace/worktrees/task-*; do
  cd "$wt"
  echo "同步 $(basename $wt)..."
  git fetch origin main
  git rebase origin/main
done
```

### 3. 并行构建

```bash
# 同时构建所有worktrees
for wt in /workspace/worktrees/task-*; do
  (cd "$wt" && npm run build) &
done
wait
echo "所有构建完成"
```

### 4. 状态监控

```bash
# 定时检查worktree状态
watch -n 300 '/worktree-list'  # 每5分钟刷新
```

### 5. 自动化清理

```bash
# 每周清理已合并的worktrees
#!/bin/bash
# cleanup-merged.sh

for wt in /workspace/worktrees/*; do
  cd "$wt"
  BRANCH=$(git branch --show-current)

  # 检查是否已合并到main
  MERGED=$(git branch --merged origin/main | grep "$BRANCH" || true)

  if [ -n "$MERGED" ]; then
    TASK_ID=$(basename "$wt")
    echo "清理已合并的worktree: $TASK_ID"
    cd /workspace/ecommerce-api
    /worktree-cleanup "$TASK_ID"
  fi
done
```

---

## 性能对比

### 传统方式 vs Worktree方式

| 操作 | 传统方式 | Worktree方式 | 改进 |
|------|----------|--------------|------|
| 切换任务 | 15-30秒 | 0秒（直接cd） | ∞ |
| 同时开发3个功能 | 不可能 | 轻松实现 | 300% |
| 紧急Hotfix | 需要暂停工作 | 独立worktree | 0影响 |
| 并行测试 | 串行执行 | 并行执行 | 3x速度 |
| 构建时间 | 每次切换都重新构建 | 保持构建结果 | 节省60% |

### 实际收益

**本Sprint统计**:
- 节省切换时间: ~2小时/天 × 10天 = 20小时
- 并行效率提升: 3个功能同时开发，缩短40%时间
- Hotfix无中断: 紧急修复不影响开发，节省1天
- **总计**: 节省约3-4天开发时间（提升30-40%效率）

---

## 完整命令参考

### 基础操作
```bash
# 创建
/worktree-create <task-id> <branch-name> [base-branch]

# 列出
/worktree-list [--all] [--format detailed|simple|json]

# 清理
/worktree-cleanup <task-id> [--force] [--keep-branch]
```

### Git原生命令
```bash
# 列出所有worktrees
git worktree list

# 移动worktree
git worktree move <old-path> <new-path>

# 锁定worktree（防止删除）
git worktree lock <path>

# 解锁
git worktree unlock <path>

# 清理过期引用
git worktree prune
```

---

## 下一步

现在你已经了解完整的Worktree工作流，可以：

1. **开始第一个任务**
   ```bash
   /worktree-create my-first-task feature-my-feature main
   ```

2. **配置自动化**
   - 设置shell别名和函数
   - 配置IDE支持多worktrees
   - 创建定时清理脚本

3. **探索高级功能**
   - 阅读 `workflows/execution/parallel-development.md`
   - 尝试 `/orchestrate` 自动化编排
   - 使用 `/swarm` 大规模并行

4. **加入团队实践**
   - 制定团队worktree命名规范
   - 设置共享worktrees目录
   - 配置CI/CD支持worktrees

---

**Happy Parallel Coding! 🚀**

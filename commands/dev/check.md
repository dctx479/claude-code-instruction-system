运行完整的项目检查流程。

## 检查步骤

### 1. 代码质量
```bash
# Lint 检查
npm run lint || pnpm lint || yarn lint

# 类型检查
npm run typecheck || tsc --noEmit

# 格式检查
npm run format:check || prettier --check .
```

### 2. 测试
```bash
# 单元测试
npm test

# 测试覆盖率
npm run test:coverage
```

### 3. 构建验证
```bash
# 生产构建
npm run build
```

### 4. 安全检查
```bash
# 依赖安全
npm audit

# 密钥扫描 (如可用)
gitleaks detect --source . --no-git
```

### 5. 依赖检查
```bash
# 过时依赖
npm outdated

# 未使用依赖 (如可用)
depcheck
```

## 输出报告

### 检查结果汇总

| 检查项 | 状态 | 详情 |
|--------|------|------|
| Lint | ✅/❌ | |
| 类型检查 | ✅/❌ | |
| 测试 | ✅/❌ | |
| 构建 | ✅/❌ | |
| 安全 | ✅/❌ | |

### 问题列表
[需要解决的问题]

### 建议
[改进建议]

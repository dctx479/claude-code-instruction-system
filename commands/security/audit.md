对 $ARGUMENTS 执行安全审计。

## 审计范围
- 如果参数为空：审计整个项目
- 如果参数为文件/目录：审计指定范围

## 审计流程

### 1. 依赖安全检查
```bash
# Node.js
npm audit --json

# Python
pip-audit || safety check

# 通用
snyk test (如可用)
```

### 2. 静态代码分析
```bash
# 使用 semgrep
semgrep --config=auto $TARGET

# Python 特定
bandit -r $TARGET -f json

# JavaScript 特定
eslint --plugin security $TARGET
```

### 3. 密钥泄露检查
```bash
# 检查硬编码密钥
gitleaks detect --source $TARGET

# 检查常见模式
grep -rn "password\|secret\|api_key\|token" $TARGET
```

### 4. 代码模式检查
检查以下危险模式：
- SQL 拼接
- 命令注入
- 不安全的反序列化
- XSS 漏洞
- 不安全的随机数生成

## 输出报告

### 漏洞汇总

| 严重程度 | 数量 | 需要行动 |
|----------|------|----------|
| Critical | | 立即修复 |
| High | | 优先修复 |
| Medium | | 计划修复 |
| Low | | 评估后决定 |

### 详细发现
[按严重程度排序的漏洞列表]

### 修复建议
[针对每个漏洞的修复方案]

### 后续步骤
[建议的安全改进措施]

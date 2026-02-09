# 安全指南

## 概述

本文档描述太一元系统的安全最佳实践和配置指南。

---

## 环境变量管理

### API 密钥配置

**✅ 推荐做法**:
```bash
# 在 ~/.bashrc 或 ~/.zshrc 中设置
export ZOTERO_API_KEY="your-key-here"
export BRIGHTDATA_API_TOKEN="your-token-here"
export TIKHUB_API_TOKEN="your-token-here"
export ANTHROPIC_AUTH_TOKEN="your-token-here"
```

**❌ 避免做法**:
- 不要在代码中硬编码 API 密钥
- 不要将包含密钥的配置文件提交到 Git
- 不要在日志中记录完整的 API 密钥

### 验证环境变量

在使用 MCP 服务器前，验证必需的环境变量：

```bash
# 检查环境变量是否设置
if [ -z "$ZOTERO_API_KEY" ]; then
  echo "错误: ZOTERO_API_KEY 未设置"
  exit 1
fi
```

---

## 日志安全

### 敏感信息过滤

**原则**: 日志中不应包含：
- API 密钥和令牌
- 用户密码
- 个人身份信息 (PII)
- 完整的文件路径（可能泄露用户名）

**实现**:
```bash
# 过滤敏感信息
log_safe() {
  local message="$1"
  # 移除可能的 API 密钥模式
  message=$(echo "$message" | sed 's/\(api[_-]key\|token\)=[^ ]*/\1=***REDACTED***/gi')
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $message" >> "$LOG_FILE"
}
```

### 日志文件权限

```bash
# 限制日志文件权限
chmod 600 logs/*.log
```

---

## 路径安全

### 路径遍历防护

**问题**: 用户可控的路径可能导致路径遍历攻击

**解决方案**:
```bash
# 验证路径在允许的目录内
validate_path() {
  local input_path="$1"
  local base_dir="$2"

  # 解析为绝对路径
  local abs_path=$(realpath "$input_path" 2>/dev/null)
  local abs_base=$(realpath "$base_dir")

  # 检查是否在基础目录内
  if [[ "$abs_path" != "$abs_base"* ]]; then
    echo "错误: 路径不在允许的目录内"
    return 1
  fi

  return 0
}
```

### 文件操作安全

```bash
# 安全的文件复制
safe_copy() {
  local src="$1"
  local dst="$2"

  # 验证源文件存在
  if [ ! -f "$src" ]; then
    echo "错误: 源文件不存在"
    return 1
  fi

  # 验证目标路径
  validate_path "$dst" "$PROJECT_ROOT" || return 1

  # 执行复制
  cp "$src" "$dst"
}
```

---

## 命令注入防护

### 输入验证

**问题**: 用户输入可能包含恶意命令

**解决方案**:
```bash
# 严格的输入验证
validate_input() {
  local input="$1"
  local pattern="$2"

  if ! [[ "$input" =~ ^${pattern}$ ]]; then
    echo "错误: 输入格式无效"
    return 1
  fi

  return 0
}

# 示例: 验证 Agent 名称
validate_agent_name() {
  local name="$1"
  # 只允许字母、数字、连字符和下划线
  validate_input "$name" "[a-zA-Z0-9_-]+"
}
```

### 安全的命令执行

```bash
# 使用数组避免命令注入
safe_execute() {
  local cmd=("$@")
  "${cmd[@]}"
}

# 错误示例（易受注入攻击）
# eval "$user_input"

# 正确示例
safe_execute git status
```

---

## 依赖安全

### 定期扫描

```bash
# 扫描 npm 依赖漏洞
npm audit

# 修复可自动修复的漏洞
npm audit fix

# 查看详细报告
npm audit --json
```

### 锁定依赖版本

**package.json**:
```json
{
  "dependencies": {
    "express": "4.18.2",  // 精确版本
    "lodash": "~4.17.21"  // 补丁版本
  }
}
```

---

## Git 安全

### 敏感文件保护

**.gitignore**:
```
# 环境变量
.env
.env.local
.env.*.local

# API 密钥
**/secrets/
**/*-key.json
**/*-credentials.json

# 日志文件
logs/
*.log

# 临时文件
tmp/
temp/
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# 检查是否包含敏感信息
if git diff --cached | grep -E "(api[_-]key|password|secret|token)" -i; then
  echo "警告: 检测到可能的敏感信息"
  echo "请检查并移除后再提交"
  exit 1
fi
```

---

## 网络安全

### HTTPS 强制

```bash
# 确保使用 HTTPS
if [[ "$API_URL" != https://* ]]; then
  echo "错误: 必须使用 HTTPS"
  exit 1
fi
```

### 超时设置

```bash
# 设置合理的超时
curl --max-time 30 "$API_URL"
```

---

## 权限管理

### 文件权限

```bash
# 脚本文件
chmod 755 scripts/*.sh

# 配置文件
chmod 644 config/*.json

# 敏感文件
chmod 600 .env
```

### 用户权限

- 不要以 root 用户运行脚本
- 使用最小权限原则
- 定期审查文件权限

---

## 安全检查清单

### 开发阶段

- [ ] 所有 API 密钥使用环境变量
- [ ] 输入验证已实施
- [ ] 日志不包含敏感信息
- [ ] 路径遍历防护已添加
- [ ] 命令注入防护已实施

### 部署阶段

- [ ] 依赖漏洞已扫描
- [ ] 文件权限已正确设置
- [ ] .gitignore 已配置
- [ ] Pre-commit hook 已安装
- [ ] HTTPS 已强制启用

### 运维阶段

- [ ] 定期更新依赖
- [ ] 定期审查日志
- [ ] 定期备份数据
- [ ] 定期安全审计

---

## 事件响应

### 密钥泄露

1. **立即撤销** 泄露的密钥
2. **生成新密钥** 并更新配置
3. **审查日志** 查找异常活动
4. **通知相关方** 如果有数据泄露

### 安全漏洞

1. **评估影响** 确定漏洞严重程度
2. **隔离系统** 如果需要
3. **应用补丁** 修复漏洞
4. **验证修复** 确保问题解决
5. **记录事件** 更新安全文档

---

## 参考资源

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [npm Security Best Practices](https://docs.npmjs.com/security-best-practices)
- [Git Security](https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage)

---

## 联系方式

如发现安全问题，请通过以下方式报告：
- GitHub Issues (标记为 security)
- 邮件: security@example.com

**请勿公开披露安全漏洞，直到我们有机会修复。**

# 端口管理系统集成方案

> **版本**: 2.0.0  
> **日期**: 2026-01-24

---

## 1. Docker Compose 集成

### 1.1 自动端口分配

使用 `docker-compose-sync.py` 脚本自动处理端口:

```bash
# 检查 docker-compose.yml 中的端口冲突
python scripts/port-management/docker-compose-sync.py check ./docker-compose.yml

# 自动分配可用端口并更新 .env
python scripts/port-management/docker-compose-sync.py sync ./docker-compose.yml

# 从 docker-compose.yml 导入端口到注册表
python scripts/port-management/docker-compose-sync.py import ./docker-compose.yml --project myproject
```

### 1.2 docker-compose.yml 最佳实践

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    ports:
      - "${MYSQL_PORT:-3306}:3306"
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    # 端口管理元数据 (可选)
    x-port-manager:
      service: mysql
      description: 主数据库
      auto-assign: true

  redis:
    image: redis:7
    ports:
      - "${REDIS_PORT:-6379}:6379"
    x-port-manager:
      service: redis

  api:
    build: .
    ports:
      - "${API_PORT:-8000}:8000"
    depends_on:
      - mysql
      - redis
    x-port-manager:
      service: api
      description: 后端 API
```

### 1.3 .env 文件示例

```bash
# Port Configuration - Managed by port-manager
# Project: ecommerce-backend
# Generated: 2026-01-24T10:00:00Z

# Database Ports
MYSQL_PORT=3307
REDIS_PORT=6380

# Application Ports
API_PORT=8001

# Database Credentials
MYSQL_ROOT_PASSWORD=your_password
```

---

## 2. Git 集成

### 2.1 Pre-commit Hook

创建 `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Port conflict check before commit

# 检查端口配置文件变更
if git diff --cached --name-only | grep -qE '\.env|docker-compose\.yml|port-registry\.json'; then
    echo "Checking port configuration..."
    
    # 运行端口冲突检测
    python scripts/port-manager.py conflicts --quiet
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Port conflict detected!"
        echo "Please resolve conflicts before committing."
        echo "Run: python scripts/port-manager.py conflicts"
        exit 1
    fi
    
    echo "Port configuration OK"
fi

exit 0
```

### 2.2 启用 Hook

```bash
chmod +x .git/hooks/pre-commit
```

---

## 3. Claude Code 集成

### 3.1 PreToolUse Hook

在 `hooks/hooks.json` 中添加:

```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "python scripts/port-management/port-check-hook.py",
          "description": "检查 Docker/Compose 命令的端口冲突",
          "timeout": 5000
        }
      ]
    }
  ]
}
```

### 3.2 Hook 脚本

`scripts/port-management/port-check-hook.py` 会:
1. 解析即将执行的命令
2. 检测 docker-compose up/docker run 中的端口
3. 验证端口是否已注册或被占用
4. 提供警告或建议

---

## 4. IDE 集成

### 4.1 VS Code 扩展 (计划中)

功能:
- 端口状态侧边栏
- .env 文件端口补全
- docker-compose.yml 端口验证
- 快速注册/注销端口

### 4.2 JetBrains 插件 (计划中)

类似功能的 IntelliJ/PyCharm 插件

---

## 5. CI/CD 集成

### 5.1 GitHub Actions

```yaml
name: Port Validation

on:
  pull_request:
    paths:
      - '.env*'
      - 'docker-compose*.yml'
      - 'config/port-registry.json'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Validate ports
        run: |
          python scripts/port-manager.py conflicts --ci
```

### 5.2 GitLab CI

```yaml
port-validation:
  stage: validate
  script:
    - python scripts/port-manager.py conflicts --ci
  only:
    changes:
      - .env*
      - docker-compose*.yml
      - config/port-registry.json
```

---

## 6. 项目模板集成

### 6.1 项目初始化脚本

创建 `scripts/init-project.sh`:

```bash
#!/bin/bash
# 项目初始化脚本

PROJECT_NAME=$1

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: ./init-project.sh <project-name>"
    exit 1
fi

echo "Initializing project: $PROJECT_NAME"

# 分配端口
MYSQL_PORT=$(python scripts/port-manager.py suggest mysql --json | jq -r '.port')
REDIS_PORT=$(python scripts/port-manager.py suggest redis --json | jq -r '.port')
API_PORT=$(python scripts/port-manager.py suggest api --json | jq -r '.port')

# 注册端口
python scripts/port-manager.py register $MYSQL_PORT $PROJECT_NAME mysql -d "主数据库"
python scripts/port-manager.py register $REDIS_PORT $PROJECT_NAME redis -d "缓存"
python scripts/port-manager.py register $API_PORT $PROJECT_NAME api -d "后端API"

# 生成 .env
cat > .env << ENVEOF
# Project: $PROJECT_NAME
# Generated: $(date -Iseconds)

MYSQL_PORT=$MYSQL_PORT
REDIS_PORT=$REDIS_PORT
API_PORT=$API_PORT
ENVEOF

echo "Project initialized with ports:"
echo "  MySQL: $MYSQL_PORT"
echo "  Redis: $REDIS_PORT"
echo "  API: $API_PORT"
```

---

## 7. 故障排除

### 7.1 常见问题

**问题**: Docker Compose 启动失败，端口被占用

**解决**:
```bash
# 1. 检查冲突
python scripts/port-manager.py conflicts

# 2. 查看占用进程
python scripts/port-manager.py check <port>

# 3. 重新分配端口
python scripts/port-management/docker-compose-sync.py sync ./docker-compose.yml
```

**问题**: Hook 执行超时

**解决**:
- 检查网络连接
- 增加 hooks.json 中的 timeout 值
- 使用 --quick 参数跳过实时端口扫描

---

## 参考文档

- [架构设计](PORT-MANAGEMENT-ARCHITECTURE.md)
- [使用指南](PORT-MANAGEMENT-GUIDE.md)

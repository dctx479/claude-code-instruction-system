# 端口管理系统使用指南

> **版本**: 2.0.0  
> **日期**: 2026-01-24

---

## 快速开始

### 1. 基本使用

```bash
# 查看所有已注册端口
python scripts/port-manager.py list

# 注册端口
python scripts/port-manager.py register 3307 myproject mysql -d "主数据库"

# 查看端口详情
python scripts/port-manager.py check 3307

# 推荐可用端口
python scripts/port-manager.py suggest mysql

# 检测端口冲突
python scripts/port-manager.py conflicts
```

### 2. 项目管理

```bash
# 列出所有项目
python scripts/port-manager.py projects

# 查看项目端口
python scripts/port-manager.py list --project myproject

# 导出项目配置到 .env
python scripts/port-manager.py export myproject -o .env
```

---

## 端口范围策略

### 默认服务端口范围

| 服务类型 | 端口范围 | 默认端口 | 说明 |
|----------|----------|----------|------|
| MySQL | 3306-3399 | 3306 | 关系型数据库 |
| PostgreSQL | 5432-5499 | 5432 | 关系型数据库 |
| Redis | 6379-6449 | 6379 | 缓存/消息队列 |
| MongoDB | 27017-27099 | 27017 | 文档数据库 |
| Web | 3000-3999 | 3000 | 前端开发服务器 |
| API | 8000-8999 | 8000 | 后端 API |
| WebSocket | 9000-9099 | 9000 | WebSocket |
| Custom | 10000-19999 | - | 自定义服务 |

### 端口命名规范

推荐在 .env 文件中使用以下命名:

```bash
# 数据库
MYSQL_PORT=3307
POSTGRESQL_PORT=5433
REDIS_PORT=6380
MONGODB_PORT=27018

# 应用
API_PORT=8001
WEB_PORT=3001
ADMIN_PORT=8081
```

---

## 最佳实践

### 1. 项目初始化时注册端口

在新项目开始时，先查询并注册所需端口:

```bash
# 1. 查看推荐端口
python scripts/port-manager.py suggest mysql
python scripts/port-manager.py suggest redis
python scripts/port-manager.py suggest api

# 2. 注册端口
python scripts/port-manager.py register 3307 myproject mysql -d "主数据库"
python scripts/port-manager.py register 6380 myproject redis -d "缓存"
python scripts/port-manager.py register 8001 myproject api -d "后端API"

# 3. 导出配置
python scripts/port-manager.py export myproject -o .env
```

### 2. 使用环境变量

在 docker-compose.yml 中使用环境变量:

```yaml
services:
  mysql:
    image: mysql:8.0
    ports:
      - "${MYSQL_PORT:-3306}:3306"
```

### 3. 定期清理

```bash
# 查看端口使用统计
python scripts/port-manager.py stats

# 检测长期未使用的端口
python scripts/port-manager.py cleanup --dry-run --inactive-days 30
```

### 4. 解决冲突

```bash
# 检测冲突
python scripts/port-manager.py conflicts

# 迁移到新端口
python scripts/port-manager.py migrate 3306 3307 --project myproject
```

---

## 常见问题

### Q: 端口被占用但不知道是哪个进程?

```bash
# 检查端口详情，会显示占用进程
python scripts/port-manager.py check 3306
```

### Q: 如何批量导入现有项目的端口?

```bash
# 从 docker-compose.yml 导入
python scripts/port-management/docker-compose-sync.py import ./docker-compose.yml --project myproject
```

### Q: 如何在团队中共享端口配置?

将 `config/port-registry.json` 加入版本控制，或配置远程注册表。

---

## 相关命令

| 命令 | 说明 |
|------|------|
| `register` | 注册端口 |
| `unregister` | 注销端口 |
| `list` | 列出端口 |
| `check` | 检查端口 |
| `suggest` | 推荐端口 |
| `conflicts` | 检测冲突 |
| `projects` | 列出项目 |
| `export` | 导出配置 |

---

## 参考文档

- [架构设计](PORT-MANAGEMENT-ARCHITECTURE.md)
- [集成方案](PORT-INTEGRATION.md)

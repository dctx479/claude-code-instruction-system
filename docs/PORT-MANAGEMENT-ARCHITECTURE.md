# 端口管理系统架构设计文档

> **版本**: 2.0.0  
> **日期**: 2026-01-24  
> **作者**: Taiyi System Architect

---

## 1. 概述

### 1.1 背景

在多项目开发环境中，端口冲突是一个常见且令人头疼的问题。尤其是当开发者同时运行多个项目、多个数据库实例、多个 Web 服务时，端口 3306 (MySQL)、5432 (PostgreSQL)、6379 (Redis)、8080 (Web) 等常用端口经常发生冲突。

本系统旨在提供一个全局的、智能的端口管理解决方案，实现：
- 端口的集中注册和追踪
- 冲突的自动检测和预防
- 与 Docker/Docker Compose 的深度集成
- 多机器、多环境的统一管理

### 1.2 目标

| 目标 | 描述 | 优先级 |
|------|------|--------|
| 冲突预防 | 在端口分配前检测潜在冲突 | P0 |
| 自动化集成 | 与 Docker Compose、.env 文件自动同步 | P0 |
| 可视化管理 | 提供清晰的端口使用视图 | P1 |
| 多环境支持 | 支持开发、测试、生产等多环境 | P1 |
| 智能推荐 | 根据服务类型智能推荐可用端口 | P2 |

### 1.3 范围

**包含**:
- 本地开发环境端口管理
- Docker/Docker Compose 集成
- 项目配置文件自动更新
- 端口使用统计和清理建议

**不包含**:
- 云服务端口管理 (AWS Security Groups 等)
- 网络防火墙规则管理
- 生产环境端口自动分配

---

## 2. 系统架构

### 2.1 架构概览

```
+-----------------------------------------------------------------------------+
|                           Port Management System                             |
|                              (端口管理系统)                                   |
+-----------------------------------------------------------------------------+
                                      |
           +--------------------------+---------------------------+
           |                          |                           |
           v                          v                           v
+---------------------+  +---------------------+  +---------------------+
|    CLI Interface    |  |   Hook Integration  |  |    API Interface    |
|   (命令行接口)       |  |   (钩子集成)        |  |    (API 接口)       |
|                     |  |                     |  |                     |
| - register          |  | - PreToolUse        |  | - REST API          |
| - unregister        |  | - Git Pre-commit    |  | - MCP Server        |
| - list/check        |  | - Docker Compose    |  | - VS Code LSP       |
| - suggest           |  | - Project Init      |  |                     |
| - migrate           |  |                     |  |                     |
+---------------------+  +---------------------+  +---------------------+
           |                          |                           |
           +--------------------------+---------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
|                           Port Manager Core                                  |
|                            (端口管理器核心)                                   |
|                                                                              |
|  +------------------+  +------------------+  +------------------+            |
|  | Port Registry    |  | Conflict Detector|  | Port Allocator   |            |
|  | (端口注册表)      |  | (冲突检测器)      |  | (端口分配器)      |            |
|  +------------------+  +------------------+  +------------------+            |
|                                                                              |
|  +------------------+  +------------------+  +------------------+            |
|  | Range Manager    |  | Usage Analyzer   |  | Config Generator |            |
|  | (范围管理器)      |  | (使用分析器)      |  | (配置生成器)      |            |
|  +------------------+  +------------------+  +------------------+            |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
|                           Storage Layer (存储层)                             |
|                                                                              |
|  +--------------------------+  +------------------------------+              |
|  | Local Registry           |  | Remote Registry (可选)        |              |
|  | config/port-registry.json|  | Redis/PostgreSQL/API Server  |              |
|  +--------------------------+  +------------------------------+              |
+-----------------------------------------------------------------------------+
```

### 2.2 组件设计

#### 2.2.1 Port Registry (端口注册表)

**职责**:
- 存储所有已注册端口的元数据
- 支持按项目、服务类型、环境筛选
- 维护端口历史记录

#### 2.2.2 Conflict Detector (冲突检测器)

**职责**:
- 实时检测端口占用状态
- 分析潜在冲突
- 提供冲突解决建议

#### 2.2.3 Port Allocator (端口分配器)

**职责**:
- 根据服务类型智能分配端口
- 遵循团队/项目端口范围策略
- 确保分配的端口可用

#### 2.2.4 Range Manager (范围管理器)

**职责**:
- 管理端口范围分配策略
- 支持团队/项目级别的范围隔离
- 防止范围重叠

**默认端口范围**:

| 服务类型 | 端口范围 | 说明 |
|----------|----------|------|
| MySQL | 3306 - 3399 | 3306 保留为默认 |
| PostgreSQL | 5432 - 5499 | 5432 保留为默认 |
| Redis | 6379 - 6449 | 6379 保留为默认 |
| MongoDB | 27017 - 27099 | 27017 保留为默认 |
| Web (Dev) | 3000 - 3999 | 前端开发服务器 |
| API | 8000 - 8999 | 后端 API 服务 |
| WebSocket | 9000 - 9099 | WebSocket 服务 |
| gRPC | 50000 - 50099 | gRPC 服务 |
| Custom | 10000 - 19999 | 自定义服务 |
| Testing | 20000 - 29999 | 测试环境专用 |

#### 2.2.5 Usage Analyzer (使用分析器)

**职责**:
- 统计端口使用情况
- 识别长期未使用的端口
- 生成使用报告和清理建议

#### 2.2.6 Config Generator (配置生成器)

**职责**:
- 生成 .env 文件
- 生成 docker-compose.yml 端口映射
- 同步多个配置文件

---

## 3. 数据设计

### 3.1 注册表数据结构 (v2.0)

```json
{
  "version": "2.0.0",
  "last_updated": "2026-01-24T10:00:00Z",
  "ports": {
    "3307": {
      "port": 3307,
      "project": "ecommerce-backend",
      "service": "mysql",
      "environment": "development",
      "description": "主数据库",
      "registered_at": "2026-01-20T10:00:00Z",
      "last_active": "2026-01-24T09:30:00Z",
      "container_name": "ecommerce-mysql",
      "auto_assigned": true,
      "tags": ["database", "critical"]
    }
  },
  "projects": {
    "ecommerce-backend": {
      "path": "/home/user/projects/ecommerce-backend",
      "ports": [3307, 6380, 8001],
      "environment": "development"
    }
  },
  "ranges": {
    "team-backend": {"start": 8000, "end": 8099, "owner": "backend-team"},
    "team-frontend": {"start": 3000, "end": 3099, "owner": "frontend-team"}
  },
  "reserved": [22, 80, 443, 3306, 5432, 6379],
  "history": []
}
```

---

## 4. 接口设计

### 4.1 CLI 接口

```bash
# 基础操作
port-manager register <port> <project> <service> [options]
port-manager unregister <port>
port-manager list [--project <name>] [--service <type>]
port-manager check <port>
port-manager suggest <service>

# 范围管理
port-manager range add <name> <start> <end> [--owner <team>]
port-manager range list
port-manager range remove <name>

# 冲突检测
port-manager conflicts [--project <name>]
port-manager scan [--range <start>-<end>]

# 配置同步
port-manager sync <project-path>
port-manager export <project> [--format env|docker|json]
port-manager import <file>

# 迁移工具
port-manager migrate <old-port> <new-port> [--project <name>]
port-manager migrate-batch <mapping-file>

# 分析和报告
port-manager report [--format text|json|html]
port-manager cleanup [--dry-run] [--inactive-days <days>]
port-manager stats
```

---

## 5. 集成设计

### 5.1 Docker Compose 集成

自动端口分配流程:
1. 解析 docker-compose.yml
2. 检测端口冲突
3. 分配/替换端口
4. 更新 .env 文件
5. 注册端口

### 5.2 Git 集成

Pre-commit Hook 检查端口配置变更

### 5.3 Claude Code 集成

PreToolUse Hook 检查 Docker/Compose 命令

---

## 6. 实施计划

### Phase 1: 核心功能增强 (1 周)
- 端口范围管理
- 端口预留机制
- 使用统计

### Phase 2: 集成开发 (1 周)
- Docker Compose 自动分配脚本
- Git pre-commit hook
- Claude Code PreToolUse hook

### Phase 3: 高级功能 (1 周)
- 端口迁移工具
- 批量导入/导出
- 使用报告和清理建议

---

## 7. 相关文档

- 使用指南: docs/PORT-MANAGEMENT-GUIDE.md
- 集成方案: docs/PORT-INTEGRATION.md
- API 参考: docs/PORT-MANAGEMENT-API.md

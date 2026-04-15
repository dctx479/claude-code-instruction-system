# Claude Code MCP 配置指南

## 概述

Model Context Protocol (MCP) 允许 Claude Code 连接外部工具和服务。本指南提供配置 MCP 服务器的最佳实践。

## 配置文件位置

Claude Code 支持三种配置作用域：

| 作用域 | 文件位置 | 用途 | 版本控制 |
|--------|----------|------|----------|
| **User scope** | `~/.claude.json` | 所有项目可用 | ❌ 不提交 |
| **Project scope** | `.mcp.json` | 仅当前项目 | ✅ 可提交 |
| **Local scope** | `~/.claude.json` | 同 User scope | ❌ 不提交 |

### 作用域选择建议

**User scope** - 推荐用于：
- 个人工具（Zotero、数据库连接）
- 包含敏感信息的配置（API Keys）
- 需要在所有项目中使用的服务

**Project scope** - 推荐用于：
- 团队共享的工具
- 项目特定的 API 服务
- 需要版本控制的配置

## 配置方法

### 方法 1: 使用 CLI 命令（推荐）

```bash
# 添加 User scope MCP 服务器
claude mcp add --transport stdio --scope user <server-name> -- npx -y <package-name>

# 添加 Project scope MCP 服务器
claude mcp add --transport stdio --scope project <server-name> -- npx -y <package-name>

# 添加带环境变量的服务器
claude mcp add --transport stdio --scope user <server-name> \
  --env API_KEY=xxx --env USER_ID=yyy \
  -- npx -y <package-name>

# 列出所有配置的服务器
claude mcp list

# 查看特定服务器详情
claude mcp get <server-name>

# 删除服务器
claude mcp remove <server-name>
```

### 方法 2: 手动编辑配置文件

#### 步骤 1: 检查现有配置

```bash
# User scope
test -f ~/.claude.json && echo "User config exists" || echo "Not found"

# Project scope
test -f .mcp.json && echo "Project config exists" || echo "Not found"
```

#### 步骤 2: 读取现有配置

```bash
# 读取 User scope 配置
cat ~/.claude.json

# 读取 Project scope 配置
cat .mcp.json
```

#### 步骤 3: 添加 MCP 服务器配置

**User scope** (`~/.claude.json`):
```json
{
  "mcpServers": {
    "server-name": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": {
        "API_KEY": "your-api-key",
        "USER_ID": "your-user-id"
      }
    }
  },
  "numStartups": 967,
  "installMethod": "global",
  ...
}
```

**Project scope** (`.mcp.json`):
```json
{
  "mcpServers": {
    "server-name": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": {
        "API_KEY": "${API_KEY}",
        "USER_ID": "${USER_ID}"
      }
    }
  }
}
```

#### 步骤 4: 验证配置

```bash
# 重启 Claude Code CLI
# 然后运行
/mcp
```

## 配置示例

### Zotero MCP

```bash
# 方法 1: CLI 命令
claude mcp add --transport stdio --scope user zotero \
  --env ZOTERO_API_KEY=xxx --env ZOTERO_USER_ID=yyy \
  -- npx -y mcp-zotero

# 方法 2: 手动配置 ~/.claude.json
{
  "mcpServers": {
    "zotero": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "mcp-zotero"],
      "env": {
        "ZOTERO_API_KEY": "your-api-key",
        "ZOTERO_USER_ID": "your-user-id"
      }
    }
  }
}
```

### 数据库连接

```bash
# PostgreSQL
claude mcp add --transport stdio --scope user postgres \
  --env DATABASE_URL=postgresql://... \
  -- npx -y @modelcontextprotocol/server-postgres

# SQLite
claude mcp add --transport stdio --scope project sqlite \
  -- npx -y @modelcontextprotocol/server-sqlite -- /path/to/database.db
```

### HTTP MCP 服务器

```bash
# GitHub Copilot
claude mcp add --transport http --scope project github \
  https://api.githubcopilot.com/mcp/
```

## 配置流程图

```
用户请求配置 MCP
    ↓
确定作用域（User/Project）
    ↓
检查现有配置文件
    ├─ User: 读取 ~/.claude.json
    └─ Project: 检查 .mcp.json
    ↓
选择配置方法
    ├─ CLI 命令（推荐）
    └─ 手动编辑
    ↓
添加/更新 mcpServers 配置
    ↓
验证 JSON 格式
    ↓
重启 Claude Code CLI
    ↓
运行 /mcp 验证
    ↓
测试服务器功能
```

## 最佳实践

### ✅ 推荐做法

1. **优先使用 CLI 命令**
   - 自动处理文件位置
   - 自动验证 JSON 格式
   - 减少人为错误

2. **选择合适的作用域**
   - 个人工具 → User scope
   - 团队工具 → Project scope

3. **配置前先检查**
   - 读取现有配置文件
   - 避免覆盖已有配置

4. **配置后立即验证**
   - 运行 `/mcp` 命令
   - 测试实际功能
   - 确认后再告知用户

5. **环境变量管理**
   - User scope: 直接写入值
   - Project scope: 使用 `${VAR}` 引用

6. **安全性**
   - 不在 Project scope 中硬编码敏感信息
   - User scope 配置不提交到 Git
   - 定期轮换 API Keys

### ❌ 避免做法

1. **不要猜测配置文件位置**
   - 错误：`~/.claude/config.json`
   - 错误：`~/.config/claude-code/mcp_settings.json`
   - 正确：`~/.claude.json` 或 `.mcp.json`

2. **不要跳过验证步骤**
   - 配置后必须运行 `/mcp`
   - 测试实际功能
   - 不要假设配置成功

3. **不要混淆作用域**
   - 个人工具不要用 Project scope
   - 团队工具不要用 User scope

4. **不要忽略错误**
   - JSON 格式错误
   - 包名错误
   - 环境变量缺失

## 故障排查

### 问题 1: `/mcp` 显示 "No MCP servers configured"

**可能原因**：
- 配置文件位置错误
- 配置文件名错误
- JSON 格式错误
- 未重启 CLI

**解决方法**：
```bash
# 检查配置文件是否存在
test -f ~/.claude.json && echo "Found" || echo "Not found"
test -f .mcp.json && echo "Found" || echo "Not found"

# 验证 JSON 格式
cat ~/.claude.json | python -m json.tool

# 重启 Claude Code CLI
```

### 问题 2: MCP 服务器启动失败

**可能原因**：
- 包未安装
- 环境变量缺失
- 命令路径错误

**解决方法**：
```bash
# 手动测试 MCP 服务器
npx -y mcp-zotero

# 检查环境变量
echo $ZOTERO_API_KEY
echo $ZOTERO_USER_ID

# 全局安装包
npm install -g mcp-zotero
```

### 问题 3: Project scope 服务器需要批准

**现象**：首次使用 Project scope 服务器时需要用户批准

**解决方法**：
- 运行 `/mcp` 查看待批准的服务器
- 批准后即可使用
- 重置批准：`claude mcp reset-project-choices`

## 常用 MCP 服务器

| 服务器 | 包名 | 用途 |
|--------|------|------|
| Zotero | `mcp-zotero` | 文献管理 |
| PostgreSQL | `@modelcontextprotocol/server-postgres` | 数据库查询 |
| SQLite | `@modelcontextprotocol/server-sqlite` | 本地数据库 |
| Filesystem | `@modelcontextprotocol/server-filesystem` | 文件系统访问 |
| GitHub | `@modelcontextprotocol/server-github` | GitHub API |
| Brave Search | `@modelcontextprotocol/server-brave-search` | 网络搜索 |

## 相关资源

- [Claude Code MCP 官方文档](https://code.claude.com/docs/en/mcp)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [MCP 服务器列表](https://github.com/modelcontextprotocol/servers)
- [Zotero MCP](https://github.com/kaliaboi/mcp-zotero)

## 更新日志

- **2026-01-22**: 创建初始版本，基于 Zotero-MCP 配置经验

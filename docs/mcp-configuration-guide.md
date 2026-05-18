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

### Tavily MCP（AI 搜索引擎）

Tavily 提供四合一能力：搜索 + 内容提取 + 网站地图 + 深度爬取。适合需要域名限定、时间过滤或批量内容提取的深度研究场景。

**方法 1: OAuth 认证（推荐，免密）**

```bash
claude mcp add tavily-remote-mcp --transport http https://mcp.tavily.com/mcp/
```

首次使用时会自动弹出浏览器完成 OAuth 认证，之后无需再次登录。

**方法 2: API Key 认证**

```bash
# 步骤 1: 注册获取 API Key
# 访问 https://tavily.com 注册账号（有免费额度）
# 在 Dashboard 获取 API Key（格式: tvly-xxxxxxxx）

# 步骤 2: 添加 MCP 服务器
claude mcp add tavily --transport http \
  "https://mcp.tavily.com/mcp/?tavilyApiKey=tvly-YOUR_API_KEY"
```

**方法 3: 本地安装（需要 Node.js v20+）**

```bash
claude mcp add --transport stdio --scope user tavily \
  --env TAVILY_API_KEY=tvly-YOUR_API_KEY \
  -- npx -y tavily-mcp@latest
```

**可用工具**:

| 工具 | 功能 | 典型用途 |
|------|------|---------|
| `tavily-search` | 实时网络搜索 | 域名限定搜索、时间范围过滤、新闻检索 |
| `tavily-extract` | 从 URL 提取内容 | 批量提取（最多 20 个 URL）、markdown 格式输出 |
| `tavily-map` | 网站结构发现 | 获取网站所有页面 URL 列表 |
| `tavily-crawl` | 深度爬取 | 语义过滤爬取、文档站内容提取 |

**关键参数速查**:

```
tavily-search:
  query          — 搜索查询（必填）
  search_depth   — basic(1 credit) / advanced(2 credits)
  topic          — general / news
  time_range     — day / week / month / year
  max_results    — 0-20（默认 5）
  include_domains — 限定域名列表（最多 300 个）
  exclude_domains — 排除域名列表（最多 150 个）
  include_answer  — true/advanced（AI 生成摘要答案）

tavily-extract:
  urls           — 单个 URL 或列表（最多 20 个）
  format         — markdown / text
  extract_depth  — basic / advanced（含表格和嵌入内容）

tavily-crawl:
  url            — 起始 URL
  max_depth      — 爬取深度（建议从 1 开始）
  max_breadth    — 每页跟踪链接数
  instructions   — 语义过滤指令（自然语言）
```

**与现有工具的分工**:

| 场景 | 首选 | 说明 |
|------|------|------|
| 快速事实问答 | WebSearch（内置） | 零配置，最快 |
| 限定域名搜索 | Tavily search | include_domains 精确过滤 |
| 时间范围过滤 | Tavily search | time_range/start_date/end_date |
| 批量 URL 提取 | Tavily extract | 一次最多 20 个 URL |
| 企业/市场研究 | Exa | 企业信息专长 |
| 电商数据 | Bright Data | 反爬虫能力 |

**验证配置**:

```bash
# 检查 Tavily 是否已配置
claude mcp list | grep tavily

# 在对话中测试
# 输入: "用 tavily-search 搜索最近一周的 AI agent 框架进展"
```

**成本说明**: basic search = 1 credit/次, advanced = 2 credits/次。免费账号有月度额度，足够个人研究使用。

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

| 服务器 | 包名/URL | 用途 | 传输方式 |
|--------|---------|------|---------|
| Zotero | `mcp-zotero` | 文献管理 | stdio |
| Tavily | `https://mcp.tavily.com/mcp/` | AI 搜索+提取+爬取 | http (OAuth) |
| Exa | `https://mcp.exa.ai/mcp` | 企业与市场研究 | http |
| PostgreSQL | `@modelcontextprotocol/server-postgres` | 数据库查询 | stdio |
| SQLite | `@modelcontextprotocol/server-sqlite` | 本地数据库 | stdio |
| Filesystem | `@modelcontextprotocol/server-filesystem` | 文件系统访问 | stdio |
| GitHub | `@modelcontextprotocol/server-github` | GitHub API | stdio |
| Bright Data | `@anthropic/mcp-server-brightdata` | 电商数据采集 | stdio |
| TikHub | `@tikhub/mcp-server` | 社媒数据采集 | stdio |

## 相关资源

- [Claude Code MCP 官方文档](https://code.claude.com/docs/en/mcp)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [MCP 服务器列表](https://github.com/modelcontextprotocol/servers)
- [Tavily MCP](https://github.com/tavily-ai/tavily-mcp) — AI 搜索引擎（搜索+提取+爬取）
- [Tavily 官方文档](https://docs.tavily.com/guides/mcp)
- [Zotero MCP](https://github.com/kaliaboi/mcp-zotero)
- [Exa MCP](https://exa.ai) — 企业与市场研究

## 更新日志

- **2026-01-22**: 创建初始版本，基于 Zotero-MCP 配置经验

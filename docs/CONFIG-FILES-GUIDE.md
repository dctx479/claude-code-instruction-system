# 配置文件完整指南

## 目录

1. [配置文件概述](#配置文件概述)
2. [全局配置文件详解](#全局配置文件详解)
3. [项目配置文件详解](#项目配置文件详解)
4. [配置优先级和覆盖规则](#配置优先级和覆盖规则)
5. [常见配置示例](#常见配置示例)
6. [故障排查指南](#故障排查指南)

---

## 配置文件概述

太一元系统使用多层配置文件架构，支持全局和项目级别的灵活配置。配置文件分为两大类：

### 配置文件类型

| 类型 | 用途 | 管理方式 |
|------|------|---------|
| **用户配置** | 定义系统行为（hooks、statusLine、环境变量） | 手动编辑 |
| **系统数据** | 存储运行时数据（启动次数、历史记录） | 自动管理 |

### 配置层级

```
全局配置 (~/.claude/)
    ↓ 覆盖
项目配置 (.claude/)
    ↓ 覆盖
默认配置
```

---

## 全局配置文件详解

### 1. `~/.claude/settings.json`

**用途**：全局用户配置文件，定义系统行为

**是否手动编辑**：✅ 是

**配置项**：

#### 基本配置

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your-token",
    "ANTHROPIC_BASE_URL": "https://api.anthropic.com/"
  },
  "permissions": {
    "defaultMode": "default"
  }
}
```

**说明**：
- `model`: 默认使用的 Claude 模型
- `env`: 环境变量配置
  - `ANTHROPIC_AUTH_TOKEN`: API 认证令牌
  - `ANTHROPIC_BASE_URL`: API 基础 URL
- `permissions`: 权限设置
  - `defaultMode`: 默认权限模式（`default` / `strict` / `permissive`）

#### StatusLine 配置

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline/hud.sh render"
  }
}
```

**说明**：
- `type`: 状态栏类型（`command` / `static` / `disabled`）
- `command`: 执行的命令（生成状态栏内容）

**Windows 兼容性**：
```json
{
  "statusLine": {
    "type": "command",
    "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"~/.claude/statusline/hud.sh\" render"
  }
}
```

#### Hooks 配置

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python \"~/.claude/hooks/pre-bash.py\"",
            "timeout": 3000
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"~/.claude/hooks/on-stop.sh\""
          }
        ]
      }
    ]
  }
}
```

**说明**：
- `PreToolUse`: 工具使用前触发的钩子
  - `matcher`: 匹配的工具名称（支持正则表达式）
  - `hooks`: 钩子列表
    - `type`: 钩子类型（`command`）
    - `command`: 执行的命令
    - `timeout`: 超时时间（毫秒）
- `Stop`: 会话结束时触发的钩子

**Matcher 格式**：
- 精确匹配：`"Bash"`, `"Write"`, `"Edit"`
- 正则表达式：`"/Bash|Write/"`
- 多工具匹配：`"Write|Edit"`
- 通配符：`"*"`

#### MCP 服务器配置

```json
{
  "mcpServers": {
    "exa": {
      "transport": "http",
      "url": "https://mcp.exa.ai/mcp?tools=web_search_advanced_exa"
    },
    "brightdata": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-brightdata"],
      "env": {
        "BRIGHTDATA_API_TOKEN": "your-token"
      }
    }
  }
}
```

**说明**：
- `transport`: 传输协议（`http` / `stdio`）
- `url`: HTTP 服务器 URL
- `command`: 启动命令
- `args`: 命令参数
- `env`: 环境变量

### 2. `~/.claude.json`

**用途**：系统运行时数据文件

**是否手动编辑**：❌ 否（自动管理）

**内容示例**：

```json
{
  "launchCount": 42,
  "projectHistory": [
    {
      "path": "/path/to/project",
      "lastAccessed": "2026-02-08T10:30:00Z"
    }
  ],
  "promptHistory": [
    "帮我设计一个用户认证系统",
    "优化这段代码的性能"
  ]
}
```

**说明**：
- `launchCount`: 启动次数
- `projectHistory`: 项目访问历史
- `promptHistory`: 提示词历史

**⚠️ 重要提示**：
- 此文件由 Claude Code 自动管理
- 手动编辑可能导致数据损坏
- 如需重置，删除文件后重启 Claude Code

---

## 项目配置文件详解

### 1. `.claude/settings.json`

**用途**：项目级配置文件，覆盖全局配置

**是否提交到 Git**：✅ 可选（推荐提交）

**配置项**：

#### 基本配置

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash ./.claude/statusline/hud.sh render"
  }
}
```

**说明**：
- 项目级配置会覆盖全局配置
- 通常用于项目特定的 statusLine 和 hooks

#### 项目特定 Hooks

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash ./scripts/validate-write.sh",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

### 2. `hooks/hooks.json`

**用途**：项目特定的 hooks 配置

**是否提交到 Git**：✅ 推荐

**配置示例**：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ./hooks/pre-bash.sh",
            "timeout": 3000
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ./hooks/on-stop.sh"
          }
        ]
      }
    ]
  }
}
```

**说明**：
- Matcher 格式与全局配置完全相同
- 支持精确匹配、正则表达式、通配符

**Windows 兼容性**：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"./hooks/validate.sh\"",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

---

## 配置优先级和覆盖规则

### 优先级顺序

```
项目级 .claude/settings.json (最高优先级)
    ↓ 覆盖
项目级 hooks/hooks.json
    ↓ 覆盖
全局级 ~/.claude/settings.json
    ↓ 覆盖
默认配置 (最低优先级)
```

### 覆盖规则

#### 1. 完全覆盖

项目配置会完全覆盖全局配置的同名字段：

**全局配置**：
```json
{
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline/hud.sh render"
  }
}
```

**项目配置**：
```json
{
  "statusLine": {
    "type": "static",
    "content": "Project Mode"
  }
}
```

**最终生效**：项目配置（完全覆盖）

#### 2. 合并规则

Hooks 配置会合并（不是覆盖）：

**全局配置**：
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": "global-hook.sh"}]
      }
    ]
  }
}
```

**项目配置**：
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [{"type": "command", "command": "project-hook.sh"}]
      }
    ]
  }
}
```

**最终生效**：两个 hooks 都会执行

#### 3. 环境变量覆盖

环境变量优先级：

```
命令行环境变量 (最高)
    ↓
项目级 .claude/settings.json
    ↓
全局级 ~/.claude/settings.json
    ↓
系统环境变量 (最低)
```

---

## 常见配置示例

### 示例 1: 基础开发环境

**全局配置** (`~/.claude/settings.json`):

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "sk-ant-xxx"
  },
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline/hud.sh render"
  },
  "permissions": {
    "defaultMode": "default"
  }
}
```

### 示例 2: 科研项目配置

**项目配置** (`.claude/settings.json`):

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash ./.claude/statusline/research-hud.sh render"
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash ./hooks/validate-research-output.sh",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

**Hooks 配置** (`hooks/hooks.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash ./hooks/check-experiment-env.sh",
            "timeout": 3000
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ./hooks/save-research-context.sh"
          }
        ]
      }
    ]
  }
}
```

### 示例 3: 多 MCP 服务器配置

**全局配置** (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "exa": {
      "transport": "http",
      "url": "https://mcp.exa.ai/mcp?tools=web_search_advanced_exa"
    },
    "brightdata": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-brightdata"],
      "env": {
        "BRIGHTDATA_API_TOKEN": "your-token"
      }
    },
    "tikhub": {
      "command": "npx",
      "args": ["-y", "@tikhub/mcp-server"],
      "env": {
        "TIKHUB_API_TOKEN": "your-token"
      }
    }
  }
}
```

### 示例 4: Windows 环境配置

**全局配置** (`~/.claude/settings.json`):

```json
{
  "statusLine": {
    "type": "command",
    "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"~/.claude/statusline/hud.sh\" render"
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"~/.claude/hooks/pre-bash.sh\"",
            "timeout": 3000
          }
        ]
      }
    ]
  }
}
```

### 示例 5: 端口管理集成

**项目配置** (`hooks/hooks.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python ./scripts/port-manager.py check-docker-command",
            "timeout": 3000
          }
        ]
      }
    ]
  }
}
```

---

## 故障排查指南

### 问题 1: 配置不生效

**症状**：修改配置后，系统行为没有变化

**排查步骤**：

1. **检查配置文件位置**：
   ```bash
   # 全局配置
   ls -la ~/.claude/settings.json

   # 项目配置
   ls -la .claude/settings.json
   ls -la hooks/hooks.json
   ```

2. **验证 JSON 格式**：
   ```bash
   # 使用 Python 验证
   python -m json.tool ~/.claude/settings.json > /dev/null

   # 使用 jq 验证
   jq empty ~/.claude/settings.json
   ```

3. **检查配置优先级**：
   - 项目配置会覆盖全局配置
   - 确认是否在正确的文件中修改

4. **重启 Claude Code**：
   - 配置变更需要重启才能生效

### 问题 2: Hooks 不执行

**症状**：配置的 hooks 没有被触发

**排查步骤**：

1. **检查 Matcher 格式**：
   ```json
   // ✅ 正确
   "matcher": "Bash"

   // ❌ 错误
   "matcher": {"tool": "Bash"}
   ```

2. **检查命令路径**：
   ```bash
   # 测试命令是否可执行
   bash ./hooks/pre-bash.sh
   ```

3. **检查超时设置**：
   ```json
   {
     "timeout": 3000  // 3 秒超时
   }
   ```

4. **查看 Hook 日志**：
   - 检查 Claude Code 输出日志
   - 查看 hook 脚本的错误输出

### 问题 3: Windows 路径问题

**症状**：在 Windows 上 hooks 或 statusLine 不工作

**解决方案**：

1. **使用 Git Bash 绝对路径**：
   ```json
   {
     "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"./script.sh\""
   }
   ```

2. **避免直接使用 `./script.sh`**：
   ```json
   // ❌ 在 Windows 上不工作
   "command": "./script.sh"

   // ✅ 正确
   "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"./script.sh\""
   ```

3. **使用 WSL（备选）**：
   ```json
   {
     "command": "wsl bash /mnt/c/path/to/script.sh"
   }
   ```

### 问题 4: MCP 服务器连接失败

**症状**：MCP 服务器无法连接

**排查步骤**：

1. **检查 API Token**：
   ```json
   {
     "env": {
       "BRIGHTDATA_API_TOKEN": "your-token"
     }
   }
   ```

2. **测试网络连接**：
   ```bash
   curl https://mcp.exa.ai/mcp?tools=web_search_advanced_exa
   ```

3. **检查 MCP 服务器状态**：
   ```bash
   # 测试 stdio 服务器
   npx -y @anthropic/mcp-server-brightdata
   ```

4. **查看错误日志**：
   - 检查 Claude Code 输出
   - 查看 MCP 服务器日志

### 问题 5: 配置文件冲突

**症状**：多个配置文件导致行为不一致

**解决方案**：

1. **确认配置优先级**：
   ```
   项目级 .claude/settings.json (最高)
       ↓
   项目级 hooks/hooks.json
       ↓
   全局级 ~/.claude/settings.json (最低)
   ```

2. **检查配置合并**：
   - Hooks 会合并（不覆盖）
   - 其他配置会覆盖

3. **使用配置验证脚本**：
   ```bash
   bash ./scripts/test-integrations.sh
   ```

### 问题 6: 环境变量不生效

**症状**：配置的环境变量无法访问

**排查步骤**：

1. **检查环境变量优先级**：
   ```
   命令行环境变量 (最高)
       ↓
   项目级配置
       ↓
   全局级配置
       ↓
   系统环境变量 (最低)
   ```

2. **验证环境变量**：
   ```bash
   # 在 hook 中打印环境变量
   echo $ANTHROPIC_AUTH_TOKEN
   ```

3. **检查配置格式**：
   ```json
   {
     "env": {
       "KEY": "value"
     }
   }
   ```

---

## 配置文件检查清单

### 提交前检查

- [ ] JSON 格式验证通过
- [ ] Hooks matcher 格式正确
- [ ] Windows 路径使用绝对路径
- [ ] 敏感信息已移除（API Token）
- [ ] 配置文件已同步更新

### 跨平台测试

- [ ] 在 Windows 上测试
- [ ] 在 Linux/macOS 上测试
- [ ] 验证路径兼容性
- [ ] 测试 hooks 实际执行

### 文档同步

- [ ] `hooks/hooks.json` 已更新
- [ ] `QUICK-REFERENCE.md` 已更新
- [ ] `CLAUDE.md` 已更新（如有规范变更）
- [ ] 相关文档中的示例代码已更新

---

## 相关文档

- **核心配置**：`CLAUDE.md` - 配置文件说明章节
- **快速参考**：`QUICK-REFERENCE.md` - 常用配置示例
- **Hooks 指南**：`docs/HOOKS-GUIDE.md` - Hooks 详细文档
- **经验教训**：`memory/lessons-learned.md` - 配置相关问题记录

---

## 版本历史

- **v1.0.0** (2026-02-08): 初始版本
  - 完整的配置文件说明
  - 全局和项目配置详解
  - 常见配置示例
  - 故障排查指南

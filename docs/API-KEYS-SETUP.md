# API 密钥配置指南

本文档说明如何为 Codex CLI 和 Gemini CLI 配置 API 密钥。

## Codex CLI (OpenAI)

### 方法 1: 登录认证（推荐）

```bash
codex login
```

这会打开浏览器进行 OAuth 认证，凭证会自动保存到 `~/.codex/config.toml`。

### 方法 2: 配置文件

创建或编辑 `~/.codex/config.toml`：

```toml
# Codex CLI 配置文件

[auth]
# OpenAI API 密钥
api_key = "sk-proj-..."

[model]
# 默认模型
default = "gpt-4o"

[sandbox]
# 沙箱模式: read-only, workspace-write, danger-full-access
default_mode = "workspace-write"
```

**配置文件位置**：
- Windows: `C:\Users\<用户名>\.codex\config.toml`
- Linux/Mac: `~/.codex/config.toml`

### 方法 3: 环境变量

```bash
export OPENAI_API_KEY="sk-..."
```

### 验证配置

```bash
codex exec "Hello, test connection"
```

---

## Gemini CLI (Google)

### 方法 1: 配置文件（推荐）

创建 `~/.config/gemini-cli/config.json`：

```json
{
  "apiKey": "AIza...",
  "model": "gemini-2.0-flash-exp",
  "approvalMode": "default",
  "sandbox": false
}
```

**配置文件位置**：
- Windows: `C:\Users\<用户名>\.config\gemini-cli\config.json`
- Linux/Mac: `~/.config/gemini-cli/config.json`

**配置选项说明**：
- `apiKey`: Google AI API 密钥
- `model`: 默认使用的模型
- `approvalMode`: 批准模式（`default`, `auto_edit`, `yolo`）
- `sandbox`: 是否启用沙箱模式

### 方法 2: 环境变量

```bash
export GOOGLE_API_KEY="AIza..."
# 或
export GEMINI_API_KEY="AIza..."
```

**注意**：环境变量优先级高于配置文件。如果同时设置了环境变量和配置文件，将使用环境变量。

### 验证配置

```bash
gemini "Hello, test connection"
```

---

## 第三方服务配置（OpenAI 兼容 API）

### Codex CLI - 第三方服务

编辑 `~/.codex/config.toml`，添加 `base_url` 配置：

```toml
[auth]
api_key = "your-api-key"
base_url = "https://your-service.com/v1"

[model]
default = "your-model-name"
```

**常见第三方服务示例**：

#### OpenRouter
```toml
[auth]
api_key = "sk-or-v1-..."
base_url = "https://openrouter.ai/api/v1"

[model]
default = "anthropic/claude-3.5-sonnet"
```

#### Together AI
```toml
[auth]
api_key = "..."
base_url = "https://api.together.xyz/v1"

[model]
default = "meta-llama/Llama-3-70b-chat-hf"
```

#### 本地 LM Studio
```toml
[auth]
api_key = "not-needed"
base_url = "http://localhost:1234/v1"

[model]
default = "local-model"
```

#### Ollama
```toml
[auth]
api_key = "not-needed"
base_url = "http://localhost:11434/v1"

[model]
default = "llama2"
```

### Gemini CLI - 第三方服务

**✅ gemini-cli-openai fork 版本支持第三方 API**

如果你使用的是 `dctx-team/gemini-cli-openai` fork 版本（支持 OpenAI 兼容 API），可以配置第三方服务。

**配置文件位置**: `~/.gemini/settings.json`（注意：不是 `~/.config/gemini-cli/config.json`）

```json
{
  "api": {
    "baseUrl": "https://your-service.com/v1",
    "format": "openai"
  },
  "model": {
    "name": "your-model-name"
  }
}
```

**环境变量方式**:
```bash
export GEMINI_API_KEY="your-api-key"
export GEMINI_BASE_URL="https://your-service.com/v1"
```

**常见第三方服务示例**：

#### OpenRouter
```json
{
  "api": {
    "baseUrl": "https://openrouter.ai/api/v1",
    "format": "openai"
  },
  "model": {
    "name": "google/gemini-2.0-flash-exp"
  }
}
```

#### Together AI
```json
{
  "api": {
    "baseUrl": "https://api.together.xyz/v1",
    "format": "openai"
  },
  "model": {
    "name": "google/gemini-2.0-flash-exp"
  }
}
```

#### 本地服务
```json
{
  "api": {
    "baseUrl": "http://localhost:1234/v1",
    "format": "openai"
  },
  "model": {
    "name": "local-model"
  }
}
```

**⚠️ 重要提示**：

- **官方 Google Gemini CLI** 不支持自定义第三方 API 端点
- 只有 **gemini-cli-openai fork** 版本支持（通过 OpenAI 兼容层）
- 检查你的版本：`gemini --version` 应该显示来自 `dctx-team/gemini-cli-openai` 的版本
- 如果使用官方版本，只能连接 Google Gemini API

### 环境变量方式（适用于两个 CLI）

```bash
# Codex CLI
export OPENAI_API_KEY="your-key"
export OPENAI_BASE_URL="https://your-service.com/v1"

# Gemini CLI
export GOOGLE_API_KEY="your-key"
export GEMINI_BASE_URL="https://your-service.com"
```

**注意**：环境变量优先级高于配置文件。

---

## 获取 API 密钥

### OpenAI API Key

1. 访问 https://platform.openai.com/api-keys
2. 登录你的 OpenAI 账户
3. 点击 "Create new secret key"
4. 复制密钥（只显示一次）

### Google AI API Key

1. 访问 https://aistudio.google.com/app/apikey
2. 登录你的 Google 账户
3. 点击 "Create API key"
4. 复制密钥

---

## 持久化配置（Windows）

### 设置永久环境变量

**方法 1: 系统设置**
1. 右键"此电脑" → 属性 → 高级系统设置
2. 环境变量 → 用户变量 → 新建
3. 变量名: `OPENAI_API_KEY` 或 `GOOGLE_API_KEY`
4. 变量值: 你的 API 密钥

**方法 2: PowerShell**
```powershell
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-...', 'User')
[System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', 'AIza...', 'User')
```

**方法 3: Git Bash 配置文件**

编辑 `~/.bashrc` 或 `~/.bash_profile`：

```bash
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="AIza..."
```

然后重新加载：
```bash
source ~/.bashrc
```

---

## 安全建议

1. **不要提交密钥到 Git**
   - 将密钥文件添加到 `.gitignore`
   - 使用环境变量而非硬编码

2. **定期轮换密钥**
   - 每 3-6 个月更换一次
   - 发现泄露立即撤销

3. **限制密钥权限**
   - OpenAI: 设置使用限额和速率限制
   - Google: 限制 API 密钥的使用范围

4. **使用密钥管理工具**
   - 考虑使用 1Password、Bitwarden 等密码管理器
   - 或使用系统密钥链（macOS Keychain、Windows Credential Manager）

---

## 故障排查

### Codex CLI 认证失败

```bash
# 检查配置
cat ~/.codex/config.toml

# 重新登录
codex logout
codex login
```

### Gemini CLI 认证失败

```bash
# 检查环境变量
echo $GOOGLE_API_KEY
echo $GEMINI_API_KEY

# 测试 API 密钥
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=$GOOGLE_API_KEY"
```

---

## 更新日志

### 2026-03-10
- 初始版本创建
- 添加 Codex 和 Gemini CLI 配置说明
- 添加 Windows 环境持久化配置方法
- 添加第三方服务配置支持（OpenRouter、Together AI、本地服务等）
- 添加自定义 API 端点（base_url）配置说明

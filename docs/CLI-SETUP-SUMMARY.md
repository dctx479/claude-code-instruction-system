# CLI 工具安装与配置总结

**日期**: 2026-03-10
**状态**: ✅ 安装完成，⚠️ 需要配置 API 密钥

---

## 安装状态

### ✅ Codex CLI
- **版本**: 0.112.0
- **安装路径**: 全局 npm 包
- **命令**: `codex`
- **状态**: 已安装并可用

### ✅ Gemini CLI
- **版本**: 0.21.0-nightly.20251202.2d935b379
- **安装路径**: 全局 npm 包
- **命令**: `gemini`
- **状态**: 已安装并可用

---

## ✅ 配置完成状态

### Codex CLI (OpenAI)

**状态**: ✅ 配置成功，支持第三方 API

**配置文件**: `~/.codex/config.toml`
```toml
[auth]
api_key = "your-openai-api-key-here"
base_url = "https://api.daiju.live/v1"  # 注意：是 base_url，不是 baseUrl

model = "gpt-5.3-codex"

[sandbox]
default_mode = "workspace-write"
```

**环境变量方式**（优先级更高）:
```bash
export OPENAI_BASE_URL="https://api.daiju.live/v1"
export OPENAI_API_KEY="your-openai-api-key-here"
```

**支持功能**:
- ✅ 第三方 API 端点（base_url）
- ✅ 自定义模型名称
- ✅ OpenAI 兼容的 API 服务
- ✅ 环境变量配置

**验证命令**:
```bash
codex exec --skip-git-repo-check "Hello, test connection"
```

**当前状态**: ⚠️ API 服务器 (api.daiju.live) 返回 502 错误，等待服务恢复

---

### Gemini CLI (gemini-cli-openai fork)

**状态**: ✅ 配置成功，支持第三方 API

**配置文件**: `~/.gemini/settings.json`（注意：不是 `~/.config/gemini-cli/config.json`）
```json
{
  "api": {
    "baseUrl": "https://stephecurry.asia/v1",
    "format": "openai"
  },
  "model": {
    "name": "gemini-3-pro-preview"
  }
}
```

**环境变量方式**:
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
export GEMINI_BASE_URL="https://stephecurry.asia/v1"
```

**支持功能**:
- ✅ 第三方 API 端点（api.baseUrl）
- ✅ OpenAI 兼容格式（api.format: "openai"）
- ✅ 自定义模型名称
- ✅ 环境变量配置

**验证命令**:
```bash
gemini "Hello, test connection"
```

**当前状态**: ⚠️ API 服务器 (stephecurry.asia) CPU 过载，等待服务恢复

---

### 重要说明

**官方 Google Gemini CLI 不支持第三方 API**。你当前使用的是 `dctx-team/gemini-cli-openai` fork 版本，它添加了 OpenAI 兼容层。

**两个 CLI 的配置差异**:

| 项目 | Codex CLI | Gemini CLI (fork) |
|------|-----------|-------------------|
| 配置文件 | `~/.codex/config.toml` | `~/.gemini/settings.json` |
| base_url 字段 | `[auth]` 下的 `base_url` | `api.baseUrl` |
| 格式声明 | 不需要 | 需要 `api.format = "openai"` |
| 环境变量 | `OPENAI_BASE_URL` | `GEMINI_BASE_URL` |

---

## 文档更新

### ✅ 已更新的文件

1. **API 密钥配置指南**
   - 文件: `~/.claude/skills/API-KEYS-SETUP.md`
   - 内容: 详细的 API 密钥获取和配置说明

2. **Codex 协作技能**
   - 文件: `~/.claude/skills/collaborating-with-codex/SKILL.md`
   - 更新: 修正 CLI 语法（`codex exec` + stdin）
   - 更新: 所有模板示例

3. **Gemini 协作技能**
   - 文件: `~/.claude/skills/collaborating-with-gemini/SKILL.md`
   - 更新: 修正 CLI 语法（位置参数 + stdin）
   - 更新: 所有模板示例

### 主要语法变更

#### Codex CLI
```bash
# ❌ 旧语法（文档中的错误）
codex --model gpt-4o --input file.txt --output result.txt

# ✅ 新语法（实际可用）
cat file.txt | codex exec -m gpt-4o - > result.txt
# 或
codex exec -m gpt-4o "prompt text" > result.txt
```

#### Gemini CLI
```bash
# ❌ 旧语法（文档中的错误）
gemini --model gemini-2.0-flash-exp --prompt-file file.txt --file src/

# ✅ 新语法（实际可用）
cat file.txt | gemini -m gemini-2.0-flash-exp > result.txt
# 或
gemini -m gemini-2.0-flash-exp "prompt text" > result.txt
```

---

## 获取 API 密钥

### OpenAI API Key
1. 访问: https://platform.openai.com/api-keys
2. 登录账户
3. 点击 "Create new secret key"
4. 复制密钥（只显示一次）

### Google AI API Key
1. 访问: https://aistudio.google.com/app/apikey
2. 登录 Google 账户
3. 点击 "Create API key"
4. 复制密钥

---

## 下一步操作

1. **配置 API 密钥**（必需）
   - 选择上述任一方式配置 Codex 和 Gemini 的 API 密钥
   - 验证配置是否成功

2. **测试协作技能**（可选）
   ```bash
   # 测试 Codex
   codex exec "Write a hello world function in TypeScript"

   # 测试 Gemini
   gemini "Explain the concept of async/await in JavaScript"
   ```

3. **阅读详细文档**（推荐）
   - API 密钥配置: `~/.claude/skills/API-KEYS-SETUP.md`
   - Codex 协作: `~/.claude/skills/collaborating-with-codex/SKILL.md`
   - Gemini 协作: `~/.claude/skills/collaborating-with-gemini/SKILL.md`

---

## 故障排查

### Codex 认证失败
```bash
# 检查配置
cat ~/.codex/config.toml

# 重新登录
codex logout
codex login
```

### Gemini 认证失败
```bash
# 检查环境变量
echo $GOOGLE_API_KEY

# 测试 API 密钥
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=$GOOGLE_API_KEY"
```

---

## 安全提醒

1. **不要提交密钥到 Git**
   - 使用环境变量而非硬编码
   - 将密钥文件添加到 `.gitignore`

2. **定期轮换密钥**
   - 每 3-6 个月更换一次
   - 发现泄露立即撤销

3. **限制密钥权限**
   - OpenAI: 设置使用限额和速率限制
   - Google: 限制 API 密钥的使用范围

---

## 相关资源

- Codex CLI 文档: https://github.com/openai/codex-cli
- Gemini CLI 文档: https://ai.google.dev/gemini-api/docs
- 太一元系统文档: `~/.claude/CLAUDE.md`

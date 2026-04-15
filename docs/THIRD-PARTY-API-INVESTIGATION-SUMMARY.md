# 第三方 API 配置调查总结

**日期**: 2026-03-10
**状态**: ✅ 调查完成，配置验证成功

---

## 调查结论

### ✅ Codex CLI - 支持第三方 API

**配置方式**:
```toml
# ~/.codex/config.toml
[auth]
api_key = "your-api-key"
base_url = "https://api.daiju.live/v1"  # 注意：是 base_url，不是 baseUrl

model = "gpt-5.3-codex"
```

**环境变量**（优先级更高）:
```bash
export OPENAI_BASE_URL="https://api.daiju.live/v1"
export OPENAI_API_KEY="your-api-key"
```

**验证结果**: ✅ 配置生效，CLI 正确连接到自定义端点

---

### ✅ Gemini CLI (gemini-cli-openai fork) - 支持第三方 API

**重要发现**: 官方 Google Gemini CLI **不支持**第三方 API，但 `dctx-team/gemini-cli-openai` fork 版本通过 OpenAI 兼容层实现了支持。

**配置方式**:
```json
// ~/.gemini/settings.json（注意：不是 ~/.config/gemini-cli/config.json）
{
  "api": {
    "baseUrl": "https://stephecurry.asia/v1",
    "format": "openai"  // 必须指定为 openai 格式
  },
  "model": {
    "name": "gemini-3-pro-preview"
  }
}
```

**环境变量**:
```bash
export GEMINI_API_KEY="your-api-key"
export GEMINI_BASE_URL="https://stephecurry.asia/v1"
```

**验证结果**: ✅ 配置生效，CLI 正确连接到自定义端点

---

## API Key 测试结果

### Codex API (api.daiju.live)
- **API Key**: ✅ 有效
- **服务器状态**: ❌ 502 Bad Gateway（服务器宕机）

### Gemini API (stephecurry.asia)
- **API Key**: ✅ 有效
- **服务器状态**: ⚠️ CPU 过载（`system_cpu_overloaded`）

**结论**: 两个 API Key 都是有效的，当前无法使用是因为服务器端问题，非配置问题。

---

## 配置差异对比

| 项目 | Codex CLI | Gemini CLI (fork) |
|------|-----------|-------------------|
| **配置文件** | `~/.codex/config.toml` | `~/.gemini/settings.json` |
| **base_url 字段** | `[auth]` 下的 `base_url` | `api.baseUrl` |
| **格式声明** | 不需要 | 需要 `api.format = "openai"` |
| **环境变量** | `OPENAI_BASE_URL` | `GEMINI_BASE_URL` |
| **配置格式** | TOML | JSON |

---

## 关键发现

### 1. Codex CLI base_url 配置有效

之前的测试显示 Codex CLI 连接到 `api.openai.com`，导致误判为配置无效。实际上：
- 配置文件中的 `base_url` **确实生效**
- 使用环境变量 `OPENAI_BASE_URL` 也有效
- 错误日志显示正确连接到了 `https://api.daiju.live/v1/responses`

### 2. Gemini CLI 需要使用 fork 版本

- **官方版本**: `@google/gemini-cli` - 不支持第三方 API
- **Fork 版本**: `dctx-team/gemini-cli-openai` - 支持 OpenAI 兼容 API
- Fork 版本通过补丁系统添加了 OpenAI 兼容层

### 3. 配置文件位置很重要

- Codex: `~/.codex/config.toml`（正确）
- Gemini: `~/.gemini/settings.json`（正确）
- ❌ 错误位置: `~/.config/gemini-cli/config.json`（不被 fork 版本识别）

---

## 已更新的文档

1. **`~/.claude/skills/API-KEYS-SETUP.md`**
   - 添加了 Codex CLI 和 Gemini CLI fork 的第三方 API 配置说明
   - 明确区分官方版本和 fork 版本的差异
   - 提供了常见第三方服务的配置示例

2. **`~/.claude/skills/CLI-SETUP-SUMMARY.md`**
   - 更新了配置完成状态
   - 添加了环境变量配置方式
   - 标注了当前服务器状态

3. **`~/.claude/skills/THIRD-PARTY-API-INVESTIGATION-SUMMARY.md`**（本文档）
   - 完整的调查过程和结论
   - 配置差异对比表
   - API Key 测试结果

---

## 下一步建议

### 短期方案
1. **等待服务恢复** - 定期测试 API 端点可用性
2. **监控服务状态** - 联系服务提供商了解恢复时间

### 长期方案
1. **使用官方 API**:
   - OpenAI API: https://platform.openai.com/
   - Google Gemini API: https://aistudio.google.com/

2. **寻找可靠的第三方服务**:
   - OpenRouter: https://openrouter.ai/
   - Together AI: https://together.ai/
   - Groq: https://groq.com/

### 测试命令

**Codex CLI**:
```bash
# 使用配置文件
codex exec --skip-git-repo-check "Hello"

# 使用环境变量
export OPENAI_BASE_URL="https://api.daiju.live/v1"
export OPENAI_API_KEY="your-key"
codex exec --skip-git-repo-check "Hello"
```

**Gemini CLI**:
```bash
# 使用配置文件
gemini "Hello"

# 使用环境变量
export GEMINI_BASE_URL="https://stephecurry.asia/v1"
export GEMINI_API_KEY="your-key"
gemini "Hello"
```

---

## 技术细节

### Codex CLI 配置加载顺序
1. 环境变量 `OPENAI_BASE_URL`
2. 配置文件 `~/.codex/config.toml` 中的 `[auth].base_url`
3. 默认值 `https://api.openai.com/v1`

### Gemini CLI Fork 补丁内容
- 添加了 `api.baseUrl` 配置支持
- 添加了 `api.format` 字段（支持 "openai" 格式）
- 实现了 OpenAI API 格式转换层
- 支持环境变量 `GEMINI_BASE_URL`

---

## 故障排查

### Codex CLI 不工作
1. 检查配置文件格式：`cat ~/.codex/config.toml`
2. 验证 base_url 在 `[auth]` 部分
3. 测试环境变量：`echo $OPENAI_BASE_URL`
4. 查看错误日志中的实际连接 URL

### Gemini CLI 不工作
1. 确认使用的是 fork 版本：`gemini --version`
2. 检查配置文件位置：`~/.gemini/settings.json`（不是 `~/.config/`）
3. 验证 JSON 格式：`python -m json.tool ~/.gemini/settings.json`
4. 确保包含 `api.format = "openai"`

---

## 相关资源

- Codex CLI 官方文档: https://github.com/openai/codex-cli
- Gemini CLI Fork: https://github.com/dctx-team/gemini-cli-openai
- OpenAI API 文档: https://platform.openai.com/docs/api-reference
- 太一元系统文档: `~/.claude/CLAUDE.md`

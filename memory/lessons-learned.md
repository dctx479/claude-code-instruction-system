# 经验教训库 (Lessons Learned)

> 自动维护的知识库，记录错误、解决方案和最佳实践
> 每次遇到问题或完成复杂任务后自动更新

---

## 使用说明

### 添加新条目
```markdown
## [YYYY-MM-DD] 条目标题 #ID

### 问题描述
[具体描述遇到的问题]

### 根因分析
[分析问题产生的根本原因]

### 解决方案
[如何解决这个问题]

### 配置更新
[对系统配置的更新，如果有]
- 文件: [文件路径]
- 变更: [具体变更内容]

### 验证方法
[如何验证问题已解决]

### 标签
[相关标签，如: #agent #parallel #error-handling]
```

### 查询经验
- 按日期: 查看最近的经验
- 按标签: 搜索特定领域的经验
- 按问题类型: 查找类似问题的解决方案

---

## 经验条目

### [2026-02-20] hud-v2.sh 数据源全面错误 + 跨会话 Edit 陷阱 #010

### 问题描述
`hud-v2.sh` v2.0.0 的所有动态数据（model、cost、tokens、context、agent）均显示为 0 或默认值。调查发现脚本中使用的 JSON 字段名全部错误，与 Claude Code 实际发送的 JSON 格式不符。同时，在上下文压缩后新会话中尝试 Edit 旧会话已读文件时全部报 "File has not been read yet" 错误。

### 根因分析

**A：Claude Code statusline JSON 实际格式与脚本假设不符**

| 脚本中使用的字段（错误） | Claude Code 实际字段（正确） |
|---|---|
| `.model.name` | `.model.display_name` |
| `.session.estimatedCost` | `.cost.total_cost_usd` |
| `.session.contextUsed` / `.contextLimit` | 不存在，需读 `transcript_path` JSONL |
| `.session.inputTokens` / `.outputTokens` | 不存在，需读 `transcript_path` JSONL |
| CLAUDE_AGENT 环境变量 | `~/.claude/intent-state.json` 文件 |

**实际 JSON 结构**：
```json
{
  "model": {"id": "claude-sonnet-4-6", "display_name": "Sonnet 4.6"},
  "cost": {"total_cost_usd": 0.349},
  "transcript_path": "C:/Users/.../.claude/projects/.../session.jsonl",
  "exceeds_200k_tokens": false
}
```

**B：Token/Context 数据需从 transcript JSONL 提取**

Token 数据存储在 `transcript_path` 指向的 JSONL 文件中，最后一条 `"type":"assistant"` 行的 `"usage"` 字段：
```json
{"type":"assistant","usage":{"input_tokens":N,"output_tokens":N,"cache_read_input_tokens":N,"cache_creation_input_tokens":N}}
```
上下文使用率 = `(input + cache_read + cache_creation) / 200000 * 100`

**C：跨会话 Edit 失败**

当对话被上下文压缩后，旧会话中 Read 的文件记录不会被带入新会话。在新会话中直接 Edit 这些文件会报：
```
File has not been read yet. Read it first before writing to it.
```
即使上次会话的摘要中提到"已读取该文件"，新会话仍需重新 Read。

**D：`-p /dev/stdin` 在 Cygwin/Windows 始终返回 false**

hud-v2.sh 使用 `if [[ -p /dev/stdin ]]` 检测管道输入，在 Cygwin 环境下永远为 false，导致 stdin JSON 从未被读取，`HUD_SESSION_JSON` 始终为空。

### 解决方案

1. **修正所有字段名**：按实际 JSON 格式更新 `get_model()`、`get_session_cost()`
2. **重写 context/token 函数**：通过 `transcript_path` 读取 JSONL 文件提取数据
3. **修复 stdin 读取**：移除 `-p /dev/stdin` 检测，改为无条件 `HUD_SESSION_JSON=$(cat 2>/dev/null || echo "")`
4. **跨会话编辑规则**：新会话开始时必须 Read 文件后才能 Edit

### 配置更新
- 文件: `.claude/statusline/hud-v2.sh` (项目级) → 6 处函数全面重写
- 文件: `C:\Users\ASUS\.claude\statusline\hud-v2.sh` (全局级) → 同步所有修复

### 验证方法
```bash
# 用实际 JSON 格式测试
echo '{"model":{"id":"claude-sonnet-4-6","display_name":"Sonnet 4.6"},"cost":{"total_cost_usd":0.123},"transcript_path":"","exceeds_200k_tokens":false}' \
  | bash "C:/Users/ASUS/.claude/statusline/hud-v2.sh" render
# 期望: 显示 Sonnet、$0.123、正确时间、git 信息
```

### 最佳实践
- **新会话中首先 Read 所有需要编辑的文件**，即使摘要中提到曾经读过
- **statusline 脚本写入前先用 JSON 测试**，验证字段名正确
- Cygwin 环境下避免使用 `[[ -p /dev/stdin ]]`，改用无条件 stdin 读取

### 标签
#statusline #hud #json-fields #cross-session #cygwin #stdin #transcript-jsonl

---

### [2026-02-20] Windows Hooks/Statusline 静默失败三连击 #009

### 问题描述
重启 Claude Code 后 statusline 完全不显示，UserPromptSubmit hook 持续报错 `cannot execute binary file`，且意图识别（intent-detector）从未工作过（1443 条日志全为空 USER_MESSAGE）。三个问题叠加，互相掩盖，排查困难。

### 根因分析

**根因 A：Claude Code Windows .sh 自动前缀逻辑**
Claude Code 在 Windows 上检测到命令包含 `.sh` 时，若不以 `bash ` 开头会自动追加 `bash `：
```
原命令:  "I:\APP\Git\usr\bin\bash.exe" "hud-v2.sh" render
转换后:  bash "I:\APP\Git\usr\bin\bash.exe" "hud-v2.sh" render
```
Cygwin bash 把 `bash.exe`（Windows PE 二进制）当脚本解释 → `cannot execute binary file`

**根因 B：set -eo pipefail + jq 缺失 → 脚本静默崩溃**
`hud-v2.sh` 升级到 v2.0.0 时引入 `set -eo pipefail`，但 4 个函数的 6 处 jq 调用没有 `|| fallback`。jq 未安装时 exit 127 被 pipefail 捕获，脚本立即退出，零输出。

**根因 C：Hook stdin JSON 字段名错误**
`intent-detector.sh` 读取 `"user_message"` 字段，但 UserPromptSubmit hook 的实际字段是 `"prompt"`，导致意图识别从未生效。

### 解决方案

1. **statusLine/hook 命令格式**：改为 `bash "script.sh"` 前缀格式（满足 Claude Code 的前缀检查，避免双重追加）
2. **jq fallback**：所有 jq 调用加 `|| echo "default_value"`，不论 `set -eo pipefail` 是否启用
3. **字段名修复**：`"user_message"` → `"prompt"`

### 配置更新
- 文件: `~/.claude/settings.json` → statusLine command 改为 `bash "C:\\...\\hud-v2.sh" render`
- 文件: `.claude/settings.json` → statusLine command 改为 `bash "./.claude/statusline/hud-v2.sh" render`
- 文件: `.claude/statusline/hud-v2.sh` → 6 处 jq 调用加 `|| echo "0"` / `|| echo ""`
- 文件: `~/.claude/hooks/intent-detector.sh` → 字段名 `user_message` → `prompt`
- 文件: `~/.claude/settings.json` → 8 处 hook 命令移除 `bash.exe` 前缀，改为直接引用脚本路径

### 验证方法
```bash
# 验证 statusline 脚本能正常输出
"I:\APP\Git\usr\bin\bash.exe" "./.claude/statusline/hud-v2.sh" render
# 期望: 有 ANSI 格式的状态行输出

# 验证意图识别
echo '{"prompt":"测试"}' | bash ~/.claude/hooks/intent-detector.sh
# 期望: intent.log 有非空 USER_MESSAGE 记录
```

### 最佳实践
- Windows 上所有 hook/statusLine 命令**必须**以 `bash "script.sh"` 格式书写
- 使用 `set -eo pipefail` 的脚本中，所有外部工具调用**必须**加 `|| fallback`
- 升级脚本版本时，检查是否引入了新的外部依赖（jq、python、etc.）
- UserPromptSubmit hook 使用 `"prompt"` 字段，不是 `"user_message"` 或 `"content"`

### 标签
#hooks #statusline #windows #bash #set-pipefail #jq #intent-detector #silent-failure

---

### [2026-01-24] Stop Hook 执行失败 - Bash 脚本错误处理 #008

### 问题描述
Stop hook 执行时报错：`Failed with non-blocking status code: 系统找不到指定的路径`
- 错误出现在 `ralph-stop-interceptor.sh` 脚本
- Windows GBK 编码显示乱码
- 脚本使用 `set -e` 导致命令失败时立即退出

### 根因分析
1. **过于严格的错误处理**: `set -e` 导致任何命令失败都会退出
2. **缺少默认值**: `grep` 命令在状态文件不存在时失败，没有 fallback
3. **不必要的 cat 管道**: `cat file | grep` 可简化为 `grep file`

### 解决方案
1. 改进 `set -e` 为 `set -euo pipefail`（更严格但可控）
2. 为所有 grep 命令添加 `|| echo "default"` fallback
3. 移除不必要的 `cat` 管道，直接使用 `grep file`

### 配置更新
- 文件: `hooks/ralph-stop-interceptor.sh`
- 变更:
  ```bash
  # 修改前
  RALPH_ACTIVE=$(cat "$RALPH_STATE_FILE" | grep -o '"active":[^,}]*' | cut -d':' -f2 | tr -d ' ')

  # 修改后
  RALPH_ACTIVE=$(grep -o '"active":[^,}]*' "$RALPH_STATE_FILE" | cut -d':' -f2 | tr -d ' ' || echo "false")
  ```

### 验证方法
```bash
cd project && bash ./hooks/ralph-stop-interceptor.sh
# 应该返回 exit code 0，不报错
```

### 最佳实践
- Bash 脚本中使用 `set -euo pipefail` 而非 `set -e`
- 所有可能失败的命令都应提供 fallback: `command || default_value`
- 避免不必要的管道: `grep file` 优于 `cat file | grep`
- Windows 环境下注意路径和编码问题

### 标签
#hooks #bash #error-handling #windows #ralph

---

### [初始化] 系统启动 #000

### 问题描述
首次使用系统，需要建立基础经验库

### 解决方案
创建初始结构，等待实际使用中的经验积累

### 标签
#initialization #system

---

## [2026-01-23] OpenAPI 转换器 Windows 编码问题修复 #001

### 问题描述
在 Windows 系统上运行 OpenAPI 转换器时，遇到 `UnicodeEncodeError: 'gbk' codec can't encode character` 错误。转换器中使用了 emoji 和中文字符，但 Windows 默认使用 GBK 编码，导致输出失败。

### 根因分析
- Windows 系统默认使用 GBK 编码作为标准输出编码
- Python 脚本中使用了 UTF-8 字符（emoji 和中文）
- 当 print 函数尝试输出这些字符时，GBK 编码无法处理，导致异常

### 解决方案
在脚本开头添加编码设置代码：

```python
import sys
import io

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

### 配置更新
- 文件: `tools/openapi-converter/converter.py`
- 变更: 在文件开头添加 UTF-8 编码设置，确保 Windows 系统兼容性

### 验证方法
1. 在 Windows 系统上运行转换器
2. 确认可以正常输出 emoji 和中文字符
3. 验证转换流程完整执行

### 标签
#encoding #windows #python #openapi-converter

---

## [2026-01-23] OpenAPI 转换器成功集成 TikHub API #002

### 问题描述
需要将 TikHub API 集成到太一元系统，使用 OpenAPI 转换器自动生成 Skill。

### 解决方案
1. 创建示例 OpenAPI 规范文件（`tikhub-sample.json`）
2. 修复 Windows 编码问题
3. 运行转换器生成 Skill
4. 验证生成的文件结构和内容

### 生成的文件
```
.claude/skills/tikhub-api-helper/
├── SKILL.md                 # 核心 Skill 文件（1.7KB）
├── REFERENCE.md             # 完整 API 文档（2.4KB）
├── openapi.json             # 原始 OpenAPI 规范（8.3KB）
├── scripts/
│   ├── api_client.py       # API 客户端
│   └── search.py           # 端点搜索工具
└── index/
    ├── keywords.json       # 关键词索引
    └── endpoints.json      # 端点元数据
```

### 核心端点（10个）
1. GET /trending/topics - 获取热门话题
2. GET /trending/videos - 获取热门视频
3. GET /users/{user_id} - 获取用户信息
4. GET /users/{user_id}/videos - 获取用户视频列表
5. GET /videos/{video_id} - 获取视频详情
6. GET /videos/{video_id}/comments - 获取视频评论
7. GET /search/users - 搜索用户
8. GET /search/videos - 搜索视频
9. GET /hashtags/{hashtag_id} - 获取话题详情
10. GET /hashtags/{hashtag_id}/videos - 获取话题视频

### 配置更新
- 文件: `tools/openapi-converter/examples/tikhub-sample.json`
- 变更: 创建 TikHub API 示例规范

### 验证方法
1. 检查生成的文件结构完整
2. 验证 SKILL.md 包含所有核心端点
3. 确认 API 客户端和搜索工具正确生成
4. 验证关键词索引和端点元数据正确

### 经验总结
- OpenAPI 转换器可以在 10 分钟内完成 API 集成
- 自动生成的 Skill 包含完整的搜索和调用功能
- 渐进式披露机制确保 Token 高效使用
- 转换器支持 JSON 和 YAML 格式的 OpenAPI 规范

### 标签
#openapi-converter #api-integration #tikhub #skill-generation

---

## [2026-01-24] 全局 Hooks 配置 Matcher 格式错误 #004

### 问题描述
在配置全局 `~/.claude/settings.json` 的 hooks 时，多次遇到格式错误：
```
matcher: Expected string, but received object
```

尝试了多种格式都失败：
- `"matcher": {"tools": ["Bash"]}` - 报错
- `"matcher": {"tools": ["BashTool"]}` - 报错
- `"matcher": "BashTool"` - 报错（工具名称错误）

### 根因分析
1. **配置层级差异**：全局 `settings.json` 和项目级别 `hooks/hooks.json` 使用不同的 schema
2. **Matcher 格式**：全局配置的 matcher 应该是**字符串**，不是对象
3. **工具名称**：应该使用实际的工具名称 "Bash"，不是 "BashTool"
4. **文档误导**：项目级别配置使用对象格式，导致误以为全局配置也应该使用相同格式

### 解决方案

**正确的全局配置格式**：
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "python \"C:\\Users\\ASUS\\.claude\\scripts\\port-management\\port-check-hook.py\"",
        "description": "检查 Docker 端口冲突（全局）",
        "timeout": 3000
      }]
    }]
  }
}
```

**支持的 matcher 格式**：
- 精确匹配：`"Bash"`, `"Write"`, `"Edit"`
- 正则表达式：`"/Bash|Write/"`
- 通配符：`"*"`

### 配置更新
| 文件 | 更新内容 | 理由 |
|------|----------|------|
| `~/.claude/settings.json` | 使用字符串格式的 matcher: `"Bash"` | 符合全局配置 schema |
| `CLAUDE.md` | 更新 Hooks 配置格式规范，明确全局 vs 项目差异 | 防止类似错误 |
| `memory/lessons-learned.md` | 新增经验条目 #004 | 记录正确的配置格式 |

### 验证方法
1. ✅ 修改全局配置使用字符串格式的 matcher
2. ✅ 重启 Claude Code，确认无错误消息
3. ✅ 测试 Bash 工具触发 Port Management hook
4. ✅ 验证 JSON 格式正确性

### 关键发现
- **全局配置 matcher 格式**：字符串（`"Bash"`）
- **项目配置 matcher 格式**：可能是对象（`{"tools": ["Bash"]}`）- 需要验证
- **工具名称**：使用实际的工具名称（从工具文档确认）
- **错误信息**：虽然示例显示对象格式，但实际应该使用字符串格式

### 后续建议
1. **验证项目配置**：检查项目级别 `hooks/hooks.json` 的 matcher 格式是否正确
2. **统一文档**：在 CLAUDE.md 中明确说明全局和项目配置的格式差异
3. **添加验证工具**：创建配置验证脚本，自动检查 hooks 格式
4. **更新示例**：在所有文档中使用正确的配置示例

### 标签
#hooks #configuration #matcher #global-settings #format

---

## [2026-01-24] ⚠️ **已废弃** - Hooks 配置格式误解 #003

> **警告**: 本条目记录了错误的经验，已被 #005 替代。保留此条目仅作为错误记录。

### 错误记录
**本条目错误地声称**：
- ❌ 项目配置 `hooks/hooks.json` 应该使用对象格式 `{"matcher": {"tools": ["Write"]}}`
- ❌ 字符串格式 `"matcher": "Write"` 是过时的格式

### 实际情况
经过验证（2026-01-24），**实际情况完全相反**：
- ✅ **全局和项目配置都使用字符串格式**：`"matcher": "Bash"`
- ✅ 当前项目的 `hooks/hooks.json` 就是使用字符串格式，并且工作正常
- ❌ 对象格式会导致错误：`matcher: Expected string, but received object`

### 真正的问题
本条目混淆了真正的问题：
1. ✅ **Windows 路径兼容性**：需要使用 Git Bash 完整路径而非相对路径
2. ✅ **JSON 格式验证**：需要定期验证 JSON 格式正确性
3. ❌ **Matcher 格式**：这不是问题，字符串格式始终是正确的

### 正确的配置示例
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"./script.sh\"",
        "timeout": 5000
      }]
    }]
  }
}
```

### 废弃原因
- 记录了错误的"解决方案"（对象格式）
- 误导了配置格式的理解
- 与实际验证结果不符
- 已被 #004 和 #005 的正确经验替代

### 参考正确的经验
- 参见 **#004**: 全局配置 matcher 格式（正确）
- 参见 **#005**: Hooks 配置统一格式规范（正确）

### 标签
#deprecated #error #hooks #configuration #format

---

## [2026-01-24] Hooks 配置统一格式规范 #005

### 问题描述
经过多次错误尝试（见 #003 废弃条目），最终确认了 hooks 配置的正确格式。之前的混乱源于对全局和项目配置格式的误解。

### 核心发现
**全局和项目配置使用相同的格式**：
- ✅ `matcher` 字段**始终使用字符串格式**
- ✅ 全局 `~/.claude/settings.json` 和项目 `hooks/hooks.json` 格式一致
- ❌ 对象格式 `{"tools": ["Bash"]}` 会导致解析错误

### 正确的配置格式

#### 1. PreToolUse / PostToolUse（需要 matcher）
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"./script.sh\"",
        "description": "描述",
        "timeout": 5000
      }]
    }]
  }
}
```

#### 2. 其他事件（无需 matcher）
```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"./cleanup.sh\""
      }]
    }]
  }
}
```

### Matcher 支持的模式

| 模式 | 示例 | 说明 |
|------|------|------|
| **精确匹配** | `"Bash"` | 匹配 Bash 工具 |
| **多工具** | `"Bash\|Write"` | 匹配 Bash 或 Write |
| **正则表达式** | `"/Bash\|Write/"` | 使用正则 |
| **通配符** | `"*"` | 匹配所有工具 |

### 配置验证方法

#### JSON 格式验证
```bash
# 验证语法
python -m json.tool hooks/hooks.json > /dev/null

# 或使用 jq
jq empty hooks/hooks.json
```

#### 配置测试
```bash
# 1. 重启 Claude Code
# 2. 观察启动日志，确认无错误
# 3. 触发相应工具，验证 hook 执行
```

### Windows 兼容性要点

**路径处理**：
- ✅ 使用 Git Bash：`"C:\\Program Files\\Git\\bin\\bash.exe"`
- ✅ 脚本路径加引号：`\"./script.sh\"`
- ❌ 避免相对路径的 bash：`./script.sh` (可能找不到 bash)
- ❌ 避免 WSL：`wsl bash` (可能环境问题)

**完整示例**：
```json
{
  "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"./hooks/my-hook.sh\"",
  "timeout": 5000
}
```

### 配置更新
| 文件 | 更新内容 | 理由 |
|------|----------|------|
| `memory/lessons-learned.md` | 废弃 #003，新增 #005 | 纠正错误经验 |
| `CLAUDE.md` | 移除对象格式说明，统一为字符串格式 | 防止误导 |
| `hooks/hooks.json` | 验证当前格式正确（已是字符串） | 确认无需修改 |

### 验证结果
- ✅ 全局配置 `~/.claude/settings.json` 使用字符串 matcher
- ✅ 项目配置 `hooks/hooks.json` 使用字符串 matcher
- ✅ 两者格式一致，可以互相参考
- ✅ Windows 环境下使用 Git Bash 路径工作正常

### 经验总结

#### 根本原因
1. **文档不足**：Claude Code 官方文档对 matcher 格式说明不够清晰
2. **错误推断**：看到错误消息后，错误地推断应该改用对象格式
3. **验证缺失**：未查看实际工作的配置文件进行对比

#### 正确方法
1. ✅ **查看工作示例**：先检查项目中已有的、工作正常的配置
2. ✅ **对比文档**：参考官方文档的示例
3. ✅ **小步验证**：每次只改一处，立即测试
4. ✅ **记录正确经验**：验证通过后记录到 lessons-learned

#### 防止类似错误
1. **配置变更前**：先查看当前工作的配置格式
2. **遇到错误时**：不要立即推断解决方案，先查资料
3. **记录经验时**：验证解决方案确实有效再记录
4. **定期审查**：检查 lessons-learned 中是否有矛盾或错误的条目

### 标签
#hooks #configuration #matcher #format #verified #windows #cross-platform

---

## [2026-01-24] Git Bash 路径配置错误导致 Hooks 执行失败 #006

### 问题描述
Stop hook 执行时报错：`Failed with non-blocking status code: The system cannot find the path specified.`

同时 Zotero MCP 配置也有警告：`Windows requires 'cmd /c' wrapper to execute npx`

### 根因分析
1. **Git Bash 路径不匹配**：
   - 配置中使用：`C:\Program Files\Git\bin\bash.exe`
   - 实际路径：`I:\APP\Git\usr\bin\bash.exe`
   - 原因：Git 安装在自定义位置，但配置使用了默认路径

2. **Windows npx 执行问题**：
   - 直接调用 `npx` 在 Windows 上可能失败
   - 需要通过 `cmd /c` 包装器执行

### 解决方案

#### 1. 修复 Git Bash 路径
使用 `where bash` 命令找到实际路径，然后更新所有 hooks 配置：

```json
{
  "command": "\"I:\\APP\\Git\\usr\\bin\\bash.exe\" \"./script.sh\""
}
```

#### 2. 修复 Zotero MCP 配置
添加 `cmd /c` 包装器：

```json
{
  "mcpServers": {
    "zotero": {
      "type": "stdio",
      "command": "cmd",
      "args": ["/c", "npx", "-y", "mcp-zotero"],
      "env": {...}
    }
  }
}
```

### 配置更新
| 文件 | 更新内容 | 理由 |
|------|----------|------|
| `hooks/hooks.json` | 所有 Git Bash 路径从 `C:\Program Files\Git\bin\bash.exe` 改为 `I:\APP\Git\usr\bin\bash.exe` | 匹配实际安装路径 |
| `C:\Users\ASUS\.claude.json` | Zotero MCP 配置添加 `cmd /c` 包装器 | Windows 兼容性 |

### 验证方法
1. ✅ 验证 JSON 格式：`python -m json.tool hooks/hooks.json`
2. ✅ 重启 Claude Code，观察是否还有错误
3. ✅ 运行 `/doctor` 检查配置状态
4. ✅ 触发 Stop hook，确认不再报错

### 最佳实践

#### 路径配置
1. **不要假设默认路径**：始终使用 `where` 或 `which` 命令查找实际路径
2. **使用绝对路径**：避免依赖环境变量或相对路径
3. **转义反斜杠**：Windows 路径使用双反斜杠 `\\`

#### Windows 兼容性
1. **npx 执行**：使用 `cmd /c npx` 而非直接 `npx`
2. **bash 脚本**：使用完整的 Git Bash 路径
3. **路径引号**：命令和参数都要加引号

#### 配置验证
1. **修改后立即验证**：`python -m json.tool <file.json>`
2. **测试实际执行**：不要只检查语法，要测试功能
3. **记录实际路径**：在文档中记录当前环境的实际路径

### 标签
#hooks #windows #git-bash #path #mcp #zotero #configuration

---

## [2026-01-24] Statusline 不显示 - 缺少全局配置 #007

### 问题描述
Statusline 不显示当前状态，用户无法看到实时的执行信息。

### 根因分析
1. **缺少全局配置**：
   - 项目中存在 `.claude/statusline/hud.sh` 脚本
   - 但全局配置 `C:\Users\ASUS\.claude.json` 中缺少 `statusLine` 配置
   - Claude Code 不知道如何调用 statusline 脚本

2. **配置位置**：
   - statusLine 配置应该在全局配置文件的顶层
   - 位于 `mcpServers` 之后，`firstStartTime` 之前

### 解决方案

#### 添加 statusLine 配置
在 `C:\Users\ASUS\.claude.json` 中添加：

```json
{
  "statusLine": {
    "type": "command",
    "command": "\"I:\\APP\\Git\\usr\\bin\\bash.exe\" \"./.claude/statusline/hud.sh\" render"
  }
}
```

**注意事项**：
- 使用实际的 Git Bash 路径（不是默认路径）
- 脚本路径使用相对路径 `./.claude/statusline/hud.sh`
- 命令参数是 `render`（渲染简洁版）

### 配置更新
| 文件 | 更新内容 | 理由 |
|------|----------|------|
| `C:\Users\ASUS\.claude.json` | 添加 statusLine 配置 | 启用 statusline 显示 |

### 验证方法
1. ✅ 验证 JSON 格式：`python -m json.tool C:\Users\ASUS\.claude.json`
2. ✅ 测试脚本执行：`bash ./.claude/statusline/hud.sh render`
3. ✅ 重启 Claude Code，观察 statusline 是否显示
4. ✅ 检查显示内容是否正确（时间、模型、Agent等）

### Statusline 功能说明

**显示内容**：
- 🕐 时间：当前时间 (HH:MM:SS)
- 🤖 模型：Opus/Sonnet/Haiku
- 👤 Agent：当前执行的 Agent (@agent-name)
- 📋 任务：当前任务名称
- 📊 进度：进度条和百分比
- 🔄 Ralph：Ralph Loop 状态 (R:iteration/max)
- 💬 Tokens：输入/输出 token 数量

**主题支持**：
- `default`：默认主题
- `minimal`：极简主题
- `unicode`：Unicode 字符
- `nerd`：Nerd Font 图标

**配置文件**：
- 脚本：`.claude/statusline/hud.sh`
- 配置：`memory/hud-config.json`

### 最佳实践

#### Statusline 配置
1. **使用绝对路径**：Git Bash 路径使用完整路径
2. **脚本路径相对化**：statusline 脚本使用相对路径，适应不同项目
3. **选择合适的渲染模式**：
   - `render`：简洁版（推荐）
   - `full`：完整版（带边框）

#### 自定义 Statusline
1. **修改主题**：编辑 `memory/hud-config.json` 中的 `theme` 字段
2. **调整组件**：启用/禁用特定组件（时间、模型、tokens等）
3. **自定义颜色**：修改 `colors` 配置

#### 故障排查
1. **Statusline 不显示**：
   - 检查全局配置是否有 `statusLine` 字段
   - 验证 Git Bash 路径是否正确
   - 测试脚本是否可执行

2. **显示内容不正确**：
   - 检查环境变量（CLAUDE_MODEL, CLAUDE_AGENT等）
   - 验证 Ralph 状态文件是否存在
   - 查看脚本日志输出

3. **性能问题**：
   - 降低刷新率（修改 `refresh.rate`）
   - 禁用不需要的组件
   - 使用 `minimal` 主题

### 标签
#statusline #hud #configuration #display #visualization

---

## [2026-01-24] 配置文件位置混淆导致多次错误尝试 #008

### 问题描述
在配置 statusLine 时，多次在错误的文件中尝试配置，浪费了大量时间：
1. 先尝试在 `C:\Users\ASUS\.claude.json` 中配置（错误）
2. 再尝试在项目级 `.claude/settings.json` 中配置（错误）
3. 最后才找到正确位置 `~/.claude/settings.json`

### 根因分析

#### 1. 配置文件命名混淆
- `~/.claude.json` - 用户数据文件（启动次数、项目历史等）
- `~/.claude/settings.json` - **全局设置文件**（hooks、statusLine、环境变量）
- 两个文件名称相似，容易混淆

#### 2. 文档说明不足
- CLAUDE.md 中没有明确说明各配置文件的用途
- 示例代码中只说"全局 settings.json"，没有给出完整路径
- 缺少配置文件结构的总览文档

### 解决方案

#### 明确配置文件用途

**全局配置文件**：

| 文件 | 用途 | 配置内容 |
|------|------|---------|
| `~/.claude/settings.json` | **全局设置** | hooks, statusLine, env, permissions, model |
| `~/.claude.json` | **用户数据** | numStartups, projects, tipsHistory（自动管理，不要手动编辑） |

**项目配置文件**：

| 文件 | 用途 | 配置内容 |
|------|------|---------|
| `.claude/settings.json` | **项目设置** | 项目级 hooks, statusLine, env |
| `hooks/hooks.json` | **项目 hooks** | 项目特定的 hooks 配置 |

#### 配置优先级

```
项目级 .claude/settings.json
    ↓ 覆盖
全局级 ~/.claude/settings.json
    ↓ 覆盖
默认配置
```

### 配置更新
| 文件 | 更新内容 | 理由 |
|------|----------|------|
| `memory/lessons-learned.md` | 新增 #008 条目 | 记录配置文件混淆问题 |
| `CLAUDE.md` | 需添加配置文件说明章节 | 明确各文件用途 |

### 验证方法
1. ✅ 检查 `~/.claude/settings.json` 是否存在 statusLine 配置
2. ✅ 确认 `~/.claude.json` 中没有 statusLine 配置
3. ✅ 重启 Claude Code，验证 statusLine 显示正常

### 最佳实践

#### 配置文件管理

1. **全局配置** (`~/.claude/settings.json`):
   - 用于所有项目通用的设置
   - hooks、statusLine、环境变量、权限
   - 手动编辑和管理

2. **用户数据** (`~/.claude.json`):
   - 由 Claude Code 自动管理
   - **不要手动编辑**
   - 包含启动次数、项目历史、提示历史

3. **项目配置** (`.claude/settings.json`):
   - 项目特定的设置
   - 覆盖全局配置
   - 可以提交到版本控制

#### 配置查找顺序

遇到配置问题时，按以下顺序检查：
1. **项目配置**：`.claude/settings.json`
2. **全局配置**：`~/.claude/settings.json`
3. **用户数据**：`~/.claude.json`（通常不需要检查）

#### 避免混淆的技巧

1. **记住文件名**：
   - `settings.json` = 设置（可编辑）
   - `.claude.json` = 数据（自动管理）

2. **使用完整路径**：
   - 全局：`~/.claude/settings.json`
   - 项目：`.claude/settings.json`

### 标签
#configuration #settings #statusline #file-location #confusion #best-practices

---

## [2026-01-26] Skills/Pipeline 设计模式学习与融合 #009

### 问题描述
学习外部优秀实践（research-units-pipeline-skills、literature-mentor skill、论文修改助手 prompt），提炼可融入太一元系统的设计模式。

### 核心学习点

#### 1. Skills 设计四要素（契约化设计）
每个 Skill 应该是自包含的执行单元，包含：
- **What**: 输入/输出显式声明（显式依赖）
- **How**: 执行步骤 + 边界情况（notes + procedures）
- **When done**: 验收标准（acceptance criteria）
- **What NOT to do**: 边界约束（guardrails）

**应用到太一系统**：
- Agent 定义增强验收标准字段
- 明确每个 Agent 的"绝对禁止"清单
- 输入输出契约化

#### 2. Pipeline 原子化解耦
- 流程拆解为原子化 skills，通过配置文件（而非代码）描述执行顺序
- 不同任务可复用同一套 skills，仅通过编排方式完成
- 阶段性产物保留，便于回滚和调试
- 质量门机制在关键节点兜底

**应用到太一系统**：
- 强化 orchestrator 的编排配置化能力
- 中间产物（specs、QA reports）作为检查点
- 质量门（QA Loop）已实现，可进一步细化

#### 3. 交互式逐步推进模式
- 每完成一个步骤必须停顿，等待用户确认
- 禁止一次性完成多步（防止失控）
- 三维分析视角：学习导向、批判视角、启发视角

**应用到太一系统**：
- autopilot supervised 模式已支持阶段审核
- 可增强 Ralph Loop 的 checkpoint 机制
- 复杂任务增加"人机确认点"

#### 4. 规则化定义方法
- 系统性词汇映射表（before -> after 示例）
- 绝对禁止修改的内容清单
- 约束条件明确表述（字数、风格等）

**应用到太一系统**：
- Prompt 模板可采用映射表方式定义风格
- 每个 Agent 的 guardrails 应有具体示例
- 避免抽象描述，用 before/after 展示预期行为

### 融入策略（非照搬原则）

#### 已有能力增强
| 现有机制 | 增强方向 | 优先级 |
|---------|---------|--------|
| Agent 定义 | 增加验收标准和 guardrails 字段 | 高 |
| orchestrator | 配置化编排规则 | 中 |
| QA Loop | 细化质量门检查项 | 中 |
| autopilot | 增强 checkpoint 交互 | 低 |

#### 新增能力考虑
| 能力 | 描述 | 评估 |
|-----|------|------|
| 契约化 Skill | 输入输出显式声明 | 可融入现有 Skills 系统 |
| 阶段性产物 | 中间产物持久化 | 已有 specs/QA reports，可扩展 |
| 质量门配置 | 可配置的检查点 | 值得添加 |

### 配置更新
- 文件: `memory/lessons-learned.md`
- 变更: 新增 #009 条目，记录外部实践学习

### 验证方法
1. 在下次创建 Agent 时，尝试应用四要素框架
2. 在执行复杂任务时，观察是否自然地使用了交互式确认
3. 定期回顾此条目，评估融入效果

### 经验总结

#### 学习方法论
1. **提炼而非照搬**：识别核心模式，适配到现有架构
2. **增量融入**：先增强现有机制，再考虑新增能力
3. **契约化思维**：明确输入输出、验收标准、边界约束
4. **交互式思维**：复杂任务分步执行，适时确认

#### 道家智慧映射
- **原子化解耦** → 道生一，一生二，二生三：从简单到复杂的组合
- **契约化设计** → 有无相生：明确边界才能自由组合
- **交互式推进** → 动静有常：行动与反思交替进行
- **质量门机制** → 无为而治：系统自动守护质量底线

### 标签
#self-evolution #skills #pipeline #design-pattern #learning #contract #guardrails

---

## [2026-02-20] StatusLine 对话启动时竖排显示 #010

### 问题描述
对话启动时，Claude Code 的 statusLine 将每个字符单独显示在一行，形成竖排效果（`2`, `1`, `:`, `4`, `0`... 各占一行，颜色正确但位置错误）。问题仅在对话启动时出现，Stop 事件后正常。

### 根因分析
**双重原因**：

1. **`cat` 阻塞风险**：`HUD_SESSION_JSON=$(cat 2>/dev/null || echo "")` 在对话启动时，若 Claude Code 建立了未写数据的 stdin pipe，`cat` 会阻塞等待，statusLine 命令挂起。

2. **Rendering area 未初始化**：对话启动时 Claude Code 的 statusLine 渲染区域尚未完全初始化（宽度接近 0），任何有内容的输出都会导致每个字符换行——即使脚本最终输出了完整的单行 ANSI 字符串。

**关键证据**：
- `cat -A` 检测到输出无 CRLF，单行输出，ANSI 码正确
- `xxd` 验证字节序列完整无误
- 仅在对话启动时触发，Stop 事件后正常
- 截图显示字符带有正确颜色（说明 ANSI 码被处理），但每字符占一行（说明宽度=1）

### 解决方案
```bash
# 1. cat 加 timeout 防阻塞
HUD_SESSION_JSON=$(timeout 0.5 cat 2>/dev/null || echo "")

# 2. 无 session JSON（对话启动）时直接退出，不渲染
if [[ -z "$HUD_SESSION_JSON" && "$action" == "render" ]]; then
    exit 0
fi
```

**逻辑**：Stop 事件触发时 JSON 立即可用（0.5s 超时足够），对话启动时无 JSON → 退出 → 渲染区域初始化完成后再正常渲染。

### 配置更新
- 文件: `~/.claude/statusline/hud-v2.sh`
- 变更: `main()` 函数第一段替换为 `timeout 0.5 cat` + 空 JSON 早退出保护
- 文件: `~/.claude/CLAUDE.md`
- 变更: StatusLine stdin JSON 格式规范中更新 `cat` 说明为 `timeout` 方案，并注明启动时早退出规则

### 验证方法
```bash
# 无 stdin：输出为空（启动保护）
bash ~/.claude/statusline/hud-v2.sh render < /dev/null | wc -c  # 应为 0

# 有 session JSON：正常单行输出
echo '{"model":...}' | bash ~/.claude/statusline/hud-v2.sh render | wc -l  # 应为 1
```

### 反模式（禁止）
- ❌ `HUD_SESSION_JSON=$(cat 2>/dev/null || echo "")` 无超时 → 启动阻塞
- ❌ 无论是否有 JSON 都输出 statusLine → 启动时竖排
- ❌ `[[ -p /dev/stdin ]]` 检测是否为 pipe → Cygwin 始终 false

### 标签
#statusline #cygwin #windows #startup #rendering #timeout #ansi

---

## [2026-02-20] CLAUDE.md 超过 40k 字符阈值 #011

### 问题描述
Claude Code 每次启动时警告 `⚠Large CLAUDE.md will impact performance (40.4k chars > 40.0k)`。警告来自项目级 CLAUDE.md（40,446 chars），全局 CLAUDE.md 当时为 39,946 chars（恰好在阈值以下）。

### 根因分析
项目 CLAUDE.md 在一次自进化中新增了 "Bash 脚本安全规则（新增）" section（~1,500 chars），同时将原来的独立 StatusLine 格式规范和跨会话 Edit 规则从文档末尾**嵌入**到该新 section 内（而非作为独立 section）。

结果：
- 独立 section（StatusLine + Edit）被移走 (~1,000 chars)
- Bash 规则 section 包含所有内容 (~1,500 chars)
- 净增 ~500 chars → 超过 40k 阈值

**双重问题**：内容重复（全局 CLAUDE.md 已有独立 StatusLine/Edit sections）+ 文件过大。

### 解决方案
**三步修复**：
1. 从项目 CLAUDE.md 的 Bash 规则 section 中移除嵌入的 StatusLine 和 Edit 子节（这些内容在全局 CLAUDE.md 的独立 section 中已存在）
2. 更新全局 CLAUDE.md 的 `cat` 说明为新的 `timeout` 方案
3. 验证两文件均在 40k 以下

**结果**：
- 项目 CLAUDE.md: 40,446 → 39,654 chars ✓
- 全局 CLAUDE.md: 39,946 → 39,996 chars ✓

### 配置更新
- 文件: `CLAUDE.md`（项目）
- 变更: 移除 Bash 规则 section 内嵌的 StatusLine JSON 格式和 Edit 规则内容（约 600 chars）
- 文件: `~/.claude/CLAUDE.md`（全局）
- 变更: StatusLine 说明中更新 `cat` 为 `timeout`，添加启动时退出说明

### 验证方法
```bash
wc -m ~/.claude/CLAUDE.md         # 应 < 40000
wc -m /path/to/project/CLAUDE.md  # 应 < 40000
```

### 最佳实践（防止再次超限）

**CLAUDE.md 内容管理规则**：
1. **新增内容前先检查字符数**：`wc -m CLAUDE.md` 确认余量
2. **避免跨 section 重复**：同一信息只保留一处（preferring 全局文件的独立 section）
3. **Bash 规则 section 只存放独特规则**：不嵌入 StatusLine/Edit 等已有独立 section 的内容
4. **阈值：40,000 chars**，建议保留 ≥500 chars 余量（目标 ≤39,500）
5. **大块详细内容移到外部文件引用**：如 `memory/lessons-learned.md`、`agents/*.md`

### 反模式（禁止）
- ❌ 自进化时在新 section 中嵌入已有 section 的内容（造成重复）
- ❌ 不检查字符数就添加大块内容
- ❌ 两个 section 包含相同信息（一处为主，另一处应引用）

### 标签
#claude-md #size-limit #performance #duplication #self-evolution #config

---

<!-- 新的经验条目将自动添加在这里 -->


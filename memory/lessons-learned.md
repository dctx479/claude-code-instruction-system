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

<!-- 新的经验条目将自动添加在这里 -->


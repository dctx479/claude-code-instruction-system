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

## [2026-01-24] Hooks 配置格式错误导致系统加载失败 #003

### 问题描述
项目中的 `hooks/hooks.json` 配置文件使用了已过时的格式，导致用户复制到全局配置后出现以下错误：
1. **Matcher 格式错误**: `"matcher": "Write"` (字符串) 应该是对象格式 `{"tools": ["Write"]}`
2. **事件类型错误**: `Stop`, `UserPromptSubmit` 等事件直接使用 `type` 和 `command` 字段，缺少 `hooks` 数组包裹
3. **WSL Bash 路径问题**: Windows 环境下 `./hooks/script.sh` 无法正确执行，需要使用 Git Bash 完整路径

错误消息：
```
matcher: Expected string, but received object
WSL ERROR: execvpe(/bin/bash) failed: No such file or directory
```

### 根因分析
1. **格式变更未同步**: Claude Code 更新了 hooks 格式规范，但项目配置文件未及时更新
2. **缺少格式验证**: 项目中没有自动验证 hooks 配置格式的机制
3. **跨平台兼容性不足**: 配置文件假设 Unix/Linux 环境，未考虑 Windows 用户
4. **文档滞后**: 快速参考文档中的示例使用了旧格式

### 解决方案

#### 1. 修复 hooks/hooks.json 格式

**PreToolUse/PostToolUse 事件** - 使用对象格式的 matcher:
```json
{
  "matcher": {"tools": ["Write"]},
  "hooks": [...]
}
```

**其他事件 (Stop, UserPromptSubmit, etc.)** - 移除 matcher，使用 hooks 数组:
```json
{
  "hooks": [
    {"type": "command", "command": "..."}
  ]
}
```

#### 2. 改用 Git Bash (Windows 兼容)
```json
{
  "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"./script.sh\""
}
```

#### 3. 添加 JSON 格式验证
```bash
python -m json.tool hooks/hooks.json > /dev/null
```

### 配置更新

| 文件 | 更新内容 | 理由 |
|------|----------|------|
| `hooks/hooks.json` | 修复所有 matcher 格式为对象；使用 Git Bash 完整路径 | 符合新规范，Windows 兼容 |
| `QUICK-REFERENCE.md` | 更新 hooks 配置示例，展示正确格式 | 防止用户复制错误示例 |
| `HOOKS-FORMAT-FIX.md` | 创建详细修复报告文档 | 记录问题和解决方案 |
| `CLAUDE.md` | 添加配置验证规则（见下方） | 防止类似问题再次发生 |

### 验证方法
1. ✅ 运行 `python -m json.tool hooks/hooks.json` 验证 JSON 格式
2. ✅ 重启 Claude Code，确认无错误消息
3. ✅ 测试各个 hook 触发正常（PreToolUse, Stop, UserPromptSubmit）
4. ✅ 在 Windows 环境下验证 Git Bash 命令执行成功

### 最佳实践（新增）

#### 配置文件管理
1. **定期验证**: 在提交前运行 JSON 格式验证
2. **跨平台测试**: 配置文件应在 Windows/Linux/macOS 测试
3. **版本跟踪**: 关注 Claude Code 官方文档的格式变更
4. **模板更新**: 发现格式问题后，同步更新所有模板和示例

#### Hooks 配置规范
1. **PreToolUse/PostToolUse**: 必须使用 `{"matcher": {"tools": ["ToolName"]}}`
2. **其他事件**: 不使用 matcher，直接使用 `hooks` 数组
3. **Windows 兼容**: 优先使用 Git Bash 完整路径
4. **超时设置**: 复杂脚本添加 `timeout` 字段（默认 30s）

#### 文档同步策略
1. **配置变更**: 同时更新 `hooks.json`, `CLAUDE.md`, `QUICK-REFERENCE.md`
2. **版本标注**: 在配置文件中记录格式版本号
3. **迁移指南**: 重大格式变更时提供迁移指南

### 系统改进建议

#### 1. 添加配置验证命令
创建 `/validate-config` 命令，自动检查：
- JSON 格式正确性
- Hooks matcher 格式
- 跨平台路径兼容性
- 必需字段完整性

#### 2. 增强错误处理
在 hooks 执行失败时：
- 显示友好的错误消息
- 提供修复建议链接
- 记录到错误日志

#### 3. 添加配置模板生成工具
提供交互式工具生成 hooks 配置：
```bash
/generate-hook
? 事件类型: PreToolUse
? 工具名称: Write
? 脚本路径: ./scripts/my-hook.sh
? 超时时间: 5000
✓ 生成配置片段到剪贴板
```

### 标签
#hooks #configuration #format #windows #cross-platform #git-bash #validation

---

<!-- 新的经验条目将自动添加在这里 -->


# /validate-config - 配置文件验证命令

验证系统配置文件的格式和内容正确性。

## 用法

```bash
/validate-config                  # 验证所有配置文件
/validate-config hooks            # 仅验证 hooks 配置
/validate-config settings         # 仅验证 settings 配置
/validate-config --fix            # 验证并尝试自动修复
/validate-config --export-report  # 生成详细报告
```

## 功能

### 1. JSON 格式验证
- 检查 JSON 语法正确性
- 验证必需字段完整性
- 检测多余或无效字段

### 2. Hooks 配置验证
- **Matcher 格式**: 检查 PreToolUse/PostToolUse 是否使用对象格式
- **Hooks 数组**: 验证事件是否正确使用 hooks 数组包裹
- **命令路径**: 检查跨平台兼容性（Windows/Linux/macOS）
- **脚本文件**: 验证引用的脚本文件是否存在
- **超时设置**: 检查 timeout 值是否合理

### 3. Settings 配置验证
- 权限配置正确性
- 模型设置有效性
- MCP 服务器配置
- Agent 并行度设置

### 4. 自动修复
- 修正 matcher 格式（字符串 → 对象）
- 添加缺失的 hooks 数组包裹
- 更正命令路径格式（Windows 兼容）
- 生成修复后的配置文件

## 验证项目

### Hooks 配置 (`hooks/hooks.json`)

| 检查项 | 严重性 | 说明 |
|--------|--------|------|
| JSON 语法 | 错误 | 必须是有效的 JSON |
| Matcher 格式 | 错误 | PreToolUse/PostToolUse 必须使用字符串格式 `"ToolName"` |
| Hooks 数组 | 错误 | 所有事件必须使用 `hooks` 数组包裹 |
| 命令路径 | 警告 | Windows 环境建议使用 Git Bash 完整路径 |
| 脚本存在性 | 警告 | 引用的脚本文件应该存在 |
| 超时设置 | 警告 | Timeout 应在 1000-60000ms 范围内 |

### Settings 配置 (`config/settings.json`)

| 检查项 | 严重性 | 说明 |
|--------|--------|------|
| JSON 语法 | 错误 | 必须是有效的 JSON |
| 权限配置 | 警告 | allow/deny 列表格式正确 |
| 模型设置 | 警告 | default 模型有效 (sonnet/opus/haiku) |
| 上下文限制 | 警告 | maxTokens 在合理范围内 |
| Agent 并行度 | 警告 | parallel 值建议 1-10 |

## 使用示例

### 示例 1: 快速验证

```bash
$ /validate-config

🔍 开始配置文件验证...

✓ hooks/hooks.json - 通过
✓ config/settings.json - 通过
✓ config/keywords.json - 通过

总计: 3 个文件, 0 个错误, 0 个警告
✨ 所有配置文件都正确！
```

### 示例 2: 发现错误

```bash
$ /validate-config hooks

============================================================
开始 Hooks 配置诊断
============================================================

ℹ 加载配置文件: hooks/hooks.json
✓ 配置文件加载成功
ℹ 检查 Hooks 结构...
ℹ 检查 Matcher 格式...
ℹ 检查 Hooks 数组结构...

============================================================
诊断报告
============================================================

✗ 发现 2 个错误:
============================================================

[1] INVALID_MATCHER_FORMAT
  消息: PreToolUse[0] matcher 格式错误（对象格式）
  位置: hooks.PreToolUse[0].matcher
  当前值: {"tools": ["Write"]}
  🔧 修复方案: 修改为字符串格式: "Write"

[2] WINDOWS_INCOMPATIBLE_PATH
  消息: Stop[0].hooks[0] 使用相对路径脚本
  位置: hooks.Stop[0].hooks[0].command
  当前值: ./hooks/ralph-stop-interceptor.sh
  🔧 修复方案: 使用 Git Bash: "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"./hooks/ralph-stop-interceptor.sh\""

总计: 2 个错误, 0 个警告

运行 /validate-config --fix 自动修复这些问题
```

### 示例 3: 自动修复

```bash
$ /validate-config --fix

🔧 开始自动修复...

✓ 修复 PreToolUse[0] matcher 格式
✓ 修复 Stop[0] 命令路径

修复后的配置已保存到: hooks/hooks.json.fixed
运行以下命令应用修复:
  cp hooks/hooks.json hooks/hooks.json.backup
  mv hooks/hooks.json.fixed hooks/hooks.json

验证修复:
  python -m json.tool hooks/hooks.json
```

### 示例 4: 生成详细报告

```bash
$ /validate-config --export-report

生成验证报告...

✓ 报告已导出到: config-validation-report.md

报告包含:
- 所有配置文件的验证结果
- 错误和警告详情
- 修复建议和示例代码
- 最佳实践建议
```

## 工作流程

```
用户运行 /validate-config
    ↓
1. 检测平台环境 (Windows/Linux/macOS)
    ↓
2. 扫描配置文件
    ├─ hooks/hooks.json
    ├─ config/settings.json
    ├─ config/keywords.json
    └─ config/mcp-servers.json
    ↓
3. 验证每个文件
    ├─ JSON 格式
    ├─ 必需字段
    ├─ 值的有效性
    └─ 跨平台兼容性
    ↓
4. 收集错误和警告
    ↓
5. 生成报告
    ├─ 控制台输出
    └─ [可选] 导出到文件
    ↓
6. [可选] 自动修复
    ├─ 生成修复后的配置
    └─ 提示用户应用
```

## 技术实现

### 核心脚本
```python
# scripts/validate-config.py
- 加载和解析 JSON
- 执行各种验证规则
- 生成修复建议
- 导出详细报告
```

### 集成方式
```bash
# commands/general/validate-config.md
执行: python scripts/validate-config.py $ARGS
```

### 依赖工具
- Python 3.7+
- json 模块（标准库）
- scripts/detect-git-bash.py（Git Bash 检测）
- scripts/diagnose-hooks.py（Hooks 诊断）

## 退出状态码

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 0 | 成功 | 所有配置文件都正确 |
| 1 | 错误 | 发现严重错误，需要修复 |
| 2 | 警告 | 发现警告，建议修复 |
| 3 | 部分失败 | 某些文件无法验证 |

## 集成到工作流

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# 验证配置文件
if ! /validate-config; then
  echo "配置验证失败，请修复后再提交"
  exit 1
fi
```

### CI/CD

```yaml
# .github/workflows/validate-config.yml
name: Validate Configuration

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate config
        run: |
          python scripts/validate-config.py
          if [ $? -ne 0 ]; then
            echo "配置验证失败"
            exit 1
          fi
```

### 定期检查

```bash
# cron 任务：每天检查配置
0 0 * * * cd /path/to/project && /validate-config --export-report
```

## 相关命令

- `/detect-git-bash` - 检测 Git Bash 路径
- `/diagnose-hooks` - 诊断 Hooks 配置
- `/fix-config` - 自动修复配置（别名）

## 最佳实践

1. **定期验证**: 每次修改配置后运行验证
2. **提交前检查**: 使用 pre-commit hook 自动验证
3. **备份配置**: 修复前备份原始配置
4. **阅读报告**: 理解错误和警告的原因
5. **测试修复**: 修复后测试配置实际加载

## 故障排除

### 问题: 验证工具无法运行

```bash
# 检查 Python 版本
python --version  # 需要 3.7+

# 检查脚本权限
chmod +x scripts/validate-config.py

# 手动运行脚本
python scripts/validate-config.py --help
```

### 问题: 自动修复失败

- 检查文件权限（是否可写）
- 备份配置文件后手动修改
- 查看详细错误日志

### 问题: 报告导出失败

- 检查输出目录权限
- 使用 `--output` 指定其他路径
- 检查磁盘空间

## 参考文档

- [Hooks 配置格式规范](../CLAUDE.md#八进化指令)
- [配置文件验证规则](../CLAUDE.md#配置文件验证规则)
- [Hooks 格式修复报告](../HOOKS-FORMAT-FIX.md)
- [错误诊断工具](../scripts/diagnose-hooks.py)

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-01-24 | 初始版本 |

---

**维护人员**: 太一元系统开发团队
**文档版本**: 1.0.0

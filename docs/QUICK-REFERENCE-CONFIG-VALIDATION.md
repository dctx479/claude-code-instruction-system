# 配置验证快速参考卡片

**版本**: 1.0.0 | **日期**: 2026-01-24 | **适用**: 太一元系统 v3.1.0

---

## 🚀 快速开始

```bash
# 验证所有配置
python scripts/validate-config.py

# 自动修复问题
python scripts/validate-config.py --fix

# 仅验证 hooks
python scripts/validate-config.py hooks
```

---

## ⚠️ 常见错误速查表

### 错误 1: Matcher 格式错误

**错误信息**:
```
invalid_matcher_format
PreToolUse[0] matcher 格式错误（字符串）
当前值: "Write"
```

**原因**: 使用了旧的字符串格式

**修复**:
```json
❌ 错误:
"matcher": "Write"

✅ 正确:
"matcher": {"tools": ["Write"]}
```

---

### 错误 2: Windows 路径不兼容

**错误信息**:
```
windows_incompatible_path
使用相对路径脚本: ./hooks/script.sh
```

**原因**: Windows 无法直接执行相对路径的 .sh 脚本

**修复**:
```json
❌ 错误:
"command": "./hooks/script.sh"

✅ 正确:
"command": "\"C:\\\\Program Files\\\\Git\\\\bin\\\\bash.exe\" \"./hooks/script.sh\""
```

**快速获取 Git Bash 路径**:
```bash
python scripts/detect-git-bash.py
```

---

### 错误 3: 缺少 Hooks 数组

**错误信息**:
```
missing_hooks_array
Stop[0] 缺少 hooks 数组包裹
```

**原因**: 旧格式直接写 type 和 command

**修复**:
```json
❌ 错误:
{
  "type": "command",
  "command": "..."
}

✅ 正确:
{
  "matcher": {"tools": ["Write"]},
  "hooks": [{
    "type": "command",
    "command": "..."
  }]
}
```

---

### 错误 4: JSON 语法错误

**错误信息**:
```
JSON 解析错误: 行 45, 列 12: Expecting ',' delimiter
```

**原因**: JSON 格式不正确（多余逗号、缺少引号等）

**快速检查**:
```bash
python -m json.tool hooks/hooks.json
```

**修复**: 使用 JSON 验证工具找到并修复语法错误

---

## 📋 Hooks 配置模板

### PreToolUse Hook（工具执行前）

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": {"tools": ["Write", "Edit"]},
        "hooks": [
          {
            "type": "command",
            "command": "\"C:\\\\Program Files\\\\Git\\\\bin\\\\bash.exe\" \"./scripts/validate-command.sh\"",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

### PostToolUse Hook（工具执行后）

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": {"tools": ["Write", "Edit"]},
        "hooks": [
          {
            "type": "command",
            "command": "\"C:\\\\Program Files\\\\Git\\\\bin\\\\bash.exe\" \"./hooks/post-edit.sh\"",
            "timeout": 3000
          }
        ]
      }
    ]
  }
}
```

### Stop Hook（会话停止时）

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"C:\\\\Program Files\\\\Git\\\\bin\\\\bash.exe\" \"./hooks/on-stop.sh\"",
            "timeout": 10000
          }
        ]
      }
    ]
  }
}
```

**注意**: Stop 和 UserPromptSubmit 事件不需要 matcher！

---

## 🔧 工具命令速查

### Git Bash 检测

```bash
# 检测 Git Bash 路径
python scripts/detect-git-bash.py

# 导出 hooks 配置片段
python scripts/detect-git-bash.py --export-config

# 导出路径到文件
python scripts/detect-git-bash.py --export-path bash-path.txt
```

### Hooks 诊断

```bash
# 诊断 hooks 配置
python scripts/diagnose-hooks.py

# 指定配置文件
python scripts/diagnose-hooks.py --config path/to/hooks.json

# 生成修复后的配置
python scripts/diagnose-hooks.py --fix
```

### 配置验证

```bash
# 验证所有配置
python scripts/validate-config.py

# 仅验证 hooks
python scripts/validate-config.py hooks

# 仅验证 settings
python scripts/validate-config.py settings

# 自动修复
python scripts/validate-config.py --fix

# 导出报告
python scripts/validate-config.py --export-report report.md
```

---

## 🎯 验证清单

在提交配置前，确保通过以下检查：

- [ ] JSON 语法正确（无多余逗号、引号匹配）
- [ ] PreToolUse/PostToolUse 使用对象 matcher
- [ ] Stop/UserPromptSubmit 不使用 matcher
- [ ] 所有 hooks 使用数组包裹
- [ ] Windows 环境使用 Git Bash 完整路径
- [ ] 引用的脚本文件存在
- [ ] timeout 设置合理（1000-60000ms）
- [ ] 运行 `python scripts/validate-config.py` 无错误

---

## 🐛 调试技巧

### 1. 检查 JSON 格式
```bash
python -m json.tool hooks/hooks.json
```

### 2. 测试脚本执行
```bash
# 手动测试脚本
"C:\Program Files\Git\bin\bash.exe" "./scripts/test.sh"
```

### 3. 查看 Claude Code 日志
```bash
# Windows
%APPDATA%\.claude\logs\

# Linux/macOS
~/.claude/logs/
```

### 4. 验证配置同步
```bash
# 确保项目配置和全局配置一致
diff hooks/hooks.json ~/.claude/settings.json
```

---

## 📊 错误严重程度

| 级别 | 图标 | 含义 | 是否阻塞 |
|------|------|------|----------|
| 错误 | 🔴 | 必须修复 | ✅ 是 |
| 警告 | 🟡 | 建议修复 | ❌ 否 |
| 信息 | 🔵 | 提示信息 | ❌ 否 |

---

## 🔗 相关文档

- **详细指南**: `docs/hooks-configuration-guide.md`
- **故障排除**: `docs/troubleshooting.md`
- **格式修复报告**: `HOOKS-FORMAT-FIX.md`
- **命令文档**: `commands/general/validate-config.md`
- **工具源码**: `scripts/validate-config.py`

---

## 💡 最佳实践

1. **定期验证**: 每次修改配置后运行验证
2. **备份配置**: 修改前备份 `hooks.json`
3. **测试脚本**: 手动测试脚本是否能正常执行
4. **版本控制**: 使用 Git 跟踪配置变更
5. **文档同步**: 更新配置时同步更新文档

---

## 📞 获取帮助

- **Issue 报告**: `memory/lessons-learned.md`
- **进化报告**: `EVOLUTION-REPORT-003.md`
- **实施报告**: `IMPLEMENTATION-REPORT.md`

---

**维护团队**: 太一元系统开发团队
**更新日期**: 2026-01-24
**文档版本**: 1.0.0

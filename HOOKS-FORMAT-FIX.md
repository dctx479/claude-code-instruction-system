# ⚠️ 文档已废弃

**废弃日期**: 2026-01-24
**原因**: 本文档包含错误的 hooks matcher 格式示例

**正确格式**: Matcher 应使用**字符串格式**，而非对象格式
- ✅ 正确: `"matcher": "Bash"`
- ❌ 错误: `"matcher": {"tools": ["Bash"]}`

**请参考最新文档**:
- 核心配置: `CLAUDE.md` (第八章 进化指令 - 配置文件验证规则)
- 快速参考: `QUICK-REFERENCE.md`
- 配置验证: `docs/QUICK-REFERENCE-CONFIG-VALIDATION.md`

---

# Hooks 配置格式修复报告

**日期**: 2026-01-24
**版本**: 3.1.0
**修复人员**: Claude Code (Debugger Agent)

## 问题概述

项目中的 `hooks/hooks.json` 配置文件存在格式错误，导致用户复制到 `C:\Users\ASUS\.claude\settings.json` 后出现以下错误：

1. **Matcher 格式错误**: `"matcher": "Write"` 是字符串，但 Claude Code 新格式要求对象格式
2. **WSL Bash 执行失败**: 路径转换问题，Windows 环境下无法正确执行

## 修复内容

### 1. hooks/hooks.json

#### 修复前的错误格式

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",  // ❌ 错误：应该是字符串格式
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/validate-command.sh"  // ❌ 错误：WSL 路径问题
          }
        ]
      }
    ],
    "Stop": [
      {
        "type": "command",  // ❌ 错误：缺少 hooks 数组包裹
        "command": "./hooks/ralph-stop-interceptor.sh"
      }
    ]
  }
}
```

#### 修复后的正确格式

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",  // ✅ 正确：字符串格式
        "hooks": [
          {
            "type": "command",
            "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"./scripts/validate-command.sh\""  // ✅ 正确：Git Bash 完整路径
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [  // ✅ 正确：hooks 数组包裹
          {
            "type": "command",
            "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"./hooks/ralph-stop-interceptor.sh\""
          }
        ]
      }
    ]
  }
}
```

### 2. QUICK-REFERENCE.md

更新了文档中的 hooks 配置示例，使用正确的格式和 Git Bash 路径。

### 3. C:\Users\ASUS\.claude\settings.json

Debugger Agent 已修复用户全局配置文件，将 bash 命令替换为 Windows `cmd` 占位符。

## 格式规范

### PreToolUse / PostToolUse

这些事件类型需要使用 `matcher` 对象来指定匹配的工具：

```json
{
  "matcher": "ToolName",
  "hooks": [
    {
      "type": "command",
      "command": "命令"
    }
  ]
}
```

**支持的工具名称**:
- `Write` - 文件写入
- `Edit` - 文件编辑
- `Read` - 文件读取
- `Bash` - Bash 命令执行
- `Glob` - 文件搜索
- `Grep` - 内容搜索

### 其他事件类型

`UserPromptSubmit`, `Stop`, `Notification`, `PreCompact` 等事件类型不需要 `matcher`，直接使用 `hooks` 数组：

```json
{
  "hooks": [
    {
      "type": "command",
      "command": "命令"
    }
  ]
}
```

### Windows 环境下的 Bash 命令

**推荐方式：使用 Git Bash**

```json
{
  "command": "\"C:\\Program Files\\Git\\bin\\bash.exe\" \"./script.sh\""
}
```

**备选方式**:
1. **WSL**: `"wsl bash /mnt/g/path/to/script.sh"`
2. **PowerShell**: `"powershell -ExecutionPolicy Bypass -File \"script.ps1\""`

## 验证结果

✅ **hooks/hooks.json** - JSON 格式验证通过
✅ **QUICK-REFERENCE.md** - 配置示例已更新
✅ **C:\Users\ASUS\.claude\settings.json** - 错误已修复

## 相关文件

- `hooks/hooks.json` - 主要配置文件
- `QUICK-REFERENCE.md` - 快速参考文档
- `hooks/ralph-stop-interceptor.sh` - Ralph Loop 停止拦截器
- `hooks/intent-detector.sh` - Intent Detector Hook

## 参考文档

- [Claude Code Hooks 官方文档](https://code.claude.com/docs/en/hooks)
- [Git for Windows](https://gitforwindows.org/)

## 后续建议

1. **测试 Hooks 功能**: 重启 Claude Code 并测试各个 hook 是否正常工作
2. **自定义 Git Bash 路径**: 如果 Git 安装在其他位置，需要修改配置中的路径
3. **考虑 PowerShell 版本**: 对于更复杂的 hook 逻辑，可以考虑使用 PowerShell 脚本
4. **更新其他环境**: 如果有其他开发环境（Linux/macOS），确保配置兼容性

## 修复历史

| 日期 | 版本 | 修复内容 |
|------|------|----------|
| 2026-01-24 | 3.1.0 | 初次修复：matcher 格式 + Git Bash 支持 |

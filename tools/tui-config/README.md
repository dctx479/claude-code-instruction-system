# Taiyi TUI Config

> 交互式终端用户界面配置工具

## 概述

Taiyi TUI Config 是一个用 Rust 编写的交互式终端配置工具，使用 [ratatui](https://github.com/ratatui-org/ratatui) 框架构建。它提供了一个友好的界面来浏览和编辑 Taiyi 元系统的配置。

## 特性

- **实时预览**: 配置更改的即时可视化
- **Agent 管理**: 浏览和编辑 Agent 定义
- **主题选择器**: 在不同主题之间切换，带有实时预览
- **Hooks 配置**: 查看和管理 Hooks
- **内存系统**: 查看内存系统状态和统计
- **键盘导航**: 完整的键盘快捷键支持
- **搜索功能**: 快速搜索配置项

## 安装

### 从源码构建

```bash
cd tools/tui-config
cargo build --release
```

编译后的二进制文件位于 `target/release/taiyi-config`。

### 依赖

- Rust 1.70+
- 终端支持 ANSI 颜色

## 使用

### 基本用法

```bash
# 在当前目录启动
./taiyi-config

# 指定 Taiyi 根目录
./taiyi-config --path /path/to/taiyi

# 使用特定主题启动
./taiyi-config --theme nerd
```

### 命令行参数

| 参数 | 简写 | 默认值 | 描述 |
|------|------|--------|------|
| `--path` | `-p` | `.` | Taiyi 根目录路径 |
| `--tab` | `-t` | `overview` | 初始显示的标签页 |
| `--watch` | `-w` | `true` | 监听文件变化 |
| `--theme` | | `default` | 使用的主题 |

## 键盘快捷键

### 全局

| 快捷键 | 功能 |
|--------|------|
| `q` / `Ctrl+C` | 退出 |
| `?` | 显示/隐藏帮助 |
| `/` | 开始搜索 |
| `r` | 刷新配置 |
| `Ctrl+S` | 保存更改 |
| `t` | 循环切换主题 |

### 导航

| 快捷键 | 功能 |
|--------|------|
| `Tab` | 下一个标签页 |
| `Shift+Tab` | 上一个标签页 |
| `1-5` | 直接跳转到标签页 |
| `j` / `↓` | 向下移动 |
| `k` / `↑` | 向上移动 |
| `Enter` | 选择/编辑项目 |
| `Esc` | 返回/取消 |

## 界面布局

```
┌─────────────────────────────────────────────────────────┐
│ [1]Overview [2]Agents [3]Themes [4]Hooks [5]Memory      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐  ┌─────────────────────────────┐   │
│  │ System Status   │  │ Quick Actions               │   │
│  │                 │  │                             │   │
│  │ Version: 3.1    │  │ [t] Cycle theme             │   │
│  │ Agents: 25      │  │ [r] Refresh config          │   │
│  │ Themes: 3       │  │ [Ctrl+s] Save changes       │   │
│  │ Ralph: Active   │  │ [?] Show help               │   │
│  │                 │  │ [q] Quit                    │   │
│  └─────────────────┘  └─────────────────────────────┘   │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ Taiyi | Ready | Theme: default | Press ? for help       │
└─────────────────────────────────────────────────────────┘
```

## 标签页说明

### Overview (概览)

显示系统整体状态：
- 版本信息
- 已加载的 Agent 数量
- 可用主题
- Ralph 状态
- HUD 状态

### Agents (代理)

浏览和管理 Agent：
- 左侧列表显示所有 Agent
- 右侧显示选中 Agent 的详细信息
- 包括模型、工具、描述和触发条件

### Themes (主题)

主题选择和预览：
- 列出所有可用主题
- 实时预览 HUD 和代码块效果
- 按 Enter 应用选中的主题

### Hooks (钩子)

查看 Hooks 配置：
- PreToolUse hooks
- PostToolUse hooks
- Stop hooks
- PreCompact hooks

### Memory (记忆)

内存系统统计：
- Lessons learned 条目数
- Error patterns 数量
- 活动计划数
- Context archives 数量
- 最后归档时间

## 项目结构

```
tools/tui-config/
├── Cargo.toml          # 项目配置和依赖
├── README.md           # 本文档
└── src/
    ├── main.rs         # 入口点和主循环
    ├── config.rs       # 配置加载和解析
    ├── state.rs        # 应用状态管理
    ├── preview.rs      # 实时预览渲染
    └── ui/
        └── mod.rs      # UI 组件和渲染
```

## 依赖库

| 库 | 版本 | 用途 |
|---|------|------|
| ratatui | 0.28 | TUI 框架 |
| crossterm | 0.28 | 终端控制 |
| tokio | 1.40 | 异步运行时 |
| serde | 1.0 | 序列化 |
| serde_json | 1.0 | JSON 解析 |
| toml | 0.8 | TOML 解析 |
| syntect | 5.2 | 语法高亮 |
| clap | 4.5 | CLI 参数 |
| anyhow | 1.0 | 错误处理 |

## 开发

### 构建调试版本

```bash
cargo build
```

### 运行测试

```bash
cargo test
```

### 检查代码

```bash
cargo clippy
cargo fmt --check
```

## 与其他组件集成

TUI Config 与 Taiyi 系统的以下组件集成：

- **CLAUDE.md**: 读取版本信息
- **agents/INDEX.md**: 加载 Agent 定义
- **themes/*.toml**: 加载主题配置
- **hooks/hooks.json**: 加载 Hooks 配置
- **config/settings.json**: 加载和保存设置
- **memory/**: 读取内存系统状态

## 故障排除

### 颜色显示不正确

确保终端支持 256 色或 True Color：
```bash
echo $TERM
# 应该是 xterm-256color 或类似值
```

### 界面闪烁

尝试减少刷新率或使用更简单的主题。

### 配置加载失败

检查文件路径是否正确，确保 JSON/TOML 文件格式有效。

## 相关文档

- [Taiyi 系统文档](../../CLAUDE.md)
- [主题系统](../../themes/README.md)
- [Hooks 配置](../../hooks/hooks.json)

# HUD Renderer (Rust)

高性能 HUD 状态栏渲染器，使用 Rust 实现。

## 性能提升

- 渲染速度: 7-10x 提升
- 内存占用: 减少 60%
- 启动时间: <10ms

## 使用方法

```bash
hud-render --theme nerd --format full
```

## 主题支持

- `default`: 默认主题
- `minimal`: 简约主题
- `nerd`: Nerd Font 图标主题

## 配置

HUD 渲染器从以下位置读取配置：
- 全局配置: `~/.claude/statusline/hud-config.json`
- 项目配置: `.claude/statusline/hud-config.json`

## 构建

```bash
cd tools/hud-render-rust
cargo build --release
```

构建产物位于 `target/release/hud-render`

## 集成

在 `.claude/settings.json` 中配置：

```json
{
  "statusLine": {
    "type": "command",
    "command": "hud-render --theme nerd --format full"
  }
}
```

## 性能对比

| 实现 | 渲染时间 | 内存占用 |
|------|----------|----------|
| Bash | 50-70ms | 2-3MB |
| Rust | 5-7ms | 0.5MB |
| **提升** | **7-10x** | **60%** |

## 相关文档

- 配置指南: `memory/hud-config.json`
- Statusline 系统: `.claude/statusline/hud.sh`
- 主题系统: `docs/THEMES.md`

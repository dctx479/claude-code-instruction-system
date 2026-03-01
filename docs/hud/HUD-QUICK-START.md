# HUD StatusLine v2.0 - Quick Start Guide

**Get up and running in 5 minutes**

---

## Installation

### 1. Copy Files

```bash
# Navigate to project directory
cd /path/to/claude-code-instruction-system

# Copy HUD script to Claude directory
cp .claude/statusline/hud-v2.sh ~/.claude/statusline/hud-v2.sh
chmod +x ~/.claude/statusline/hud-v2.sh

# Copy configuration file
cp memory/hud-config-v2.json ~/.claude/hud-config.json

# Create cache directory
mkdir -p ~/.claude/cache
```

### 2. Configure Claude Code

Edit `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline/hud-v2.sh render"
  }
}
```

### 3. Test

```bash
# Test basic rendering
bash ~/.claude/statusline/hud-v2.sh render

# Expected output:
# 00:24:28 | Sonnet | my-project | master ✓ | 45% | $0.150 | @architect | 0i/0o
```

---

## What You'll See

### Basic Display

```
[Time] [Model] [Project] [Git] [Context] [Cost] [Agent] [Tokens]
```

### Example Outputs

**Clean Git Repository**:
```
00:24:28 | Sonnet | my-project | master ✓ | 45% | $0.150 | @architect | 0i/0o
```

**Dirty Repository (uncommitted changes)**:
```
00:24:28 | Sonnet | my-project | master * | 45% | $0.150 | @architect | 0i/0o
```

**Ahead of Remote**:
```
00:24:28 | Sonnet | my-project | master ✓ ↑2 | 45% | $0.150 | @architect | 0i/0o
```

**High Context Usage (Warning)**:
```
00:24:28 | Sonnet | my-project | master ✓ | 85% | $0.150 | @architect | 0i/0o
```
(85% will be displayed in yellow)

**Critical Context Usage**:
```
00:24:28 | Sonnet | my-project | master ✓ | 92% | $0.150 | @architect | 0i/0o
```
(92% will be displayed in red)

---

## Understanding the Display

| Element | Description | Example |
|---------|-------------|---------|
| **Time** | Current time | `00:24:28` |
| **Model** | Claude model | `Opus` (magenta), `Sonnet` (blue), `Haiku` (cyan) |
| **Project** | Directory name | `my-project` |
| **Git Branch** | Current branch | `master`, `develop`, `feature-x` |
| **Git Status** | Repository state | `✓` (clean), `*` (dirty) |
| **Git Ahead/Behind** | Commits vs remote | `↑2` (ahead), `↓3` (behind) |
| **Context** | Context usage % | `45%` (green), `85%` (yellow), `92%` (red) |
| **Cost** | Session cost | `$0.150` |
| **Agent** | Active agent | `@architect`, `@orchestrator` |
| **Tokens** | Token usage | `30000i/20000o` |

---

## Customization

### Change Theme

Edit `~/.claude/hud-config.json`:

```json
{
  "theme": "nerd"
}
```

**Available themes**: `default`, `minimal`, `unicode`, `nerd`

**Nerd theme output**:
```
00:24:28 ┃ Sonnet ┃ my-project ┃ master  ┃ 45% ┃ $0.150 ┃ @architect ┃ 0i/0o
```

### Disable Modules

To hide specific information:

```json
{
  "modules": {
    "time": {"enabled": false},
    "cost": {"enabled": false}
  }
}
```

### Adjust Context Warnings

```json
{
  "modules": {
    "context": {
      "warn_threshold": 70,      // Yellow at 70%
      "critical_threshold": 85   // Red at 85%
    }
  }
}
```

---

## Common Commands

```bash
# Render statusline
hud-v2.sh render

# Render with border
hud-v2.sh full

# Use specific theme
hud-v2.sh theme nerd

# Show configuration
hud-v2.sh config

# Clear cache (if statusline seems stuck)
hud-v2.sh cache-clear

# Show version
hud-v2.sh version

# Show help
hud-v2.sh help
```

---

## Troubleshooting

### Git information not showing?

```bash
# Check if you're in a git repository
git rev-parse --git-dir

# If not, initialize git
git init
```

### Statusline not updating?

```bash
# Clear cache
hud-v2.sh cache-clear

# Restart Claude Code
```

### Symbols not displaying correctly?

Install a [Nerd Font](https://www.nerdfonts.com/) and use the `nerd` theme, or switch to `default` theme:

```json
{
  "theme": "default"
}
```

### Performance issues?

```bash
# Disable expensive modules
# Edit ~/.claude/hud-config.json
{
  "modules": {
    "git": {
      "show_ahead_behind": false
    }
  }
}
```

---

## Next Steps

- Read the [Full User Guide](./HUD-STATUSLINE-GUIDE.md)
- Review [Performance Comparison](./HUD-PERFORMANCE-COMPARISON.md)
- Check [Research Report](./STATUSLINE-RESEARCH-REPORT.md)
- Customize your configuration

---

## Support

- Configuration reference: `~/.claude/hud-config.json`
- Cache directory: `~/.claude/cache/`
- Documentation: `docs/HUD-STATUSLINE-GUIDE.md`

**Version**: 2.0.0
**Last Updated**: 2026-02-14

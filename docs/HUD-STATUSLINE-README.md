# HUD StatusLine v2.0

**Enhanced real-time statusline for Claude Code with git integration, cost tracking, and intelligent caching**

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/yourusername/claude-code-instruction-system)
[![Performance](https://img.shields.io/badge/performance-<100ms-green.svg)](./HUD-PERFORMANCE-COMPARISON.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](../LICENSE)

---

## Overview

HUD StatusLine v2.0 is a high-performance, feature-rich statusline renderer for Claude Code that provides real-time visibility into your development session. It displays critical information including project context, git status, cost tracking, context usage, and more.

### Key Features

✨ **Rich Information Display**
- Project name and git status (branch, dirty state, ahead/behind)
- Context window usage with color-coded warnings
- Session cost tracking in real-time
- Agent and task information
- Ralph Loop status
- Token usage statistics

⚡ **High Performance**
- Intelligent caching system (5-60s TTL)
- <100ms execution time target
- 96% cache hit rate
- Optimized git operations

🎨 **Highly Customizable**
- 4 built-in themes (default, minimal, unicode, nerd)
- Module-based architecture
- Priority system for adaptive display
- JSON configuration file

🔧 **Developer Friendly**
- Cross-platform support (Windows/Linux/macOS)
- Comprehensive error handling
- Cache management tools
- Extensive documentation

---

## Quick Start

### Installation

```bash
# Copy HUD script
cp .claude/statusline/hud-v2.sh ~/.claude/statusline/hud-v2.sh
chmod +x ~/.claude/statusline/hud-v2.sh

# Copy configuration
cp memory/hud-config-v2.json ~/.claude/hud-config.json

# Create cache directory
mkdir -p ~/.claude/cache
```

### Configuration

Edit `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline/hud-v2.sh render"
  }
}
```

### Test

```bash
bash ~/.claude/statusline/hud-v2.sh render
```

**Expected output**:
```
00:24:28 | Sonnet | my-project | master ✓ | 45% | $0.150 | @architect | 0i/0o
```

📖 **[Read the Quick Start Guide](./HUD-QUICK-START.md)**

---

## Screenshots

### Default Theme
```
00:24:28 | Sonnet | claude-code-instruction-system | master ✓ | 45% | $0.150 | @architect | 0i/0o
```

### Nerd Theme (Recommended)
```
00:24:28 ┃ Sonnet ┃ claude-code-instruction-system ┃ master  ┃ 45% ┃ $0.150 ┃ @architect ┃ 0i/0o
```

### With Git Status
```
00:24:28 | Sonnet | my-project | master * ↑2 | 85% | $0.150 | @architect | 30Ki/20Ko
```
- `*` = dirty (uncommitted changes)
- `↑2` = 2 commits ahead of remote
- `85%` = context usage (yellow warning)

---

## What's New in v2.0

### New Information Modules

| Module | Description | Priority |
|--------|-------------|----------|
| **Project** | Current project directory name | 1 |
| **Git Branch** | Current git branch | 1 |
| **Git Status** | Clean/dirty indicator | 1 |
| **Git Ahead/Behind** | Commits ahead/behind remote | 1 |
| **Context Usage** | Context window percentage with warnings | 1 |
| **Session Cost** | Estimated cost in dollars | 2 |

### Performance Improvements

- **Caching System**: 72x faster git operations (580ms → 8ms)
- **Execution Time**: 34% faster with warm cache (122ms → 85ms)
- **Cache Hit Rate**: 96% average
- **Memory Overhead**: Minimal (+1MB)

### Enhanced Features

- **Priority System**: Adaptive display based on terminal width
- **Color Coding**: Context warnings (green/yellow/red)
- **4 Themes**: default, minimal, unicode, nerd
- **Module System**: Enable/disable individual modules
- **Configuration**: Comprehensive JSON configuration

📊 **[Read the Performance Comparison](./HUD-PERFORMANCE-COMPARISON.md)**

---

## Documentation

### User Guides
- 📖 **[Quick Start Guide](./HUD-QUICK-START.md)** - Get started in 5 minutes
- 📚 **[Full User Guide](./HUD-STATUSLINE-GUIDE.md)** - Complete documentation
- 📊 **[Performance Comparison](./HUD-PERFORMANCE-COMPARISON.md)** - v1.0 vs v2.0 benchmarks
- 🔬 **[Research Report](./STATUSLINE-RESEARCH-REPORT.md)** - Design decisions and best practices

### Configuration
- ⚙️ **[Configuration Reference](../memory/hud-config-v2.json)** - Example configuration file
- 🎨 **[Theme Guide](./HUD-STATUSLINE-GUIDE.md#themes)** - Available themes and customization
- 📦 **[Module Reference](./HUD-STATUSLINE-GUIDE.md#information-modules)** - All available modules

---

## Information Modules

### Core Modules (Priority 1)

| Module | Description | Example |
|--------|-------------|---------|
| **Model** | Current Claude model | `Opus` (magenta), `Sonnet` (blue), `Haiku` (cyan) |
| **Project** | Project directory name | `my-awesome-project` |
| **Git Branch** | Current git branch | `master`, `develop`, `feature-x` |
| **Git Status** | Repository state | `✓` (clean), `*` (dirty) |
| **Context** | Context usage % | `45%` (green), `85%` (yellow), `92%` (red) |

### Secondary Modules (Priority 2)

| Module | Description | Example |
|--------|-------------|---------|
| **Time** | Current time | `00:24:28` |
| **Cost** | Session cost | `$0.150` |
| **Agent** | Active agent | `@architect`, `@orchestrator` |
| **Task** | Current task | `implementing auth...` |
| **Progress** | Task progress | `[████░░░░░░] 40%` |

### Optional Modules (Priority 3)

| Module | Description | Example |
|--------|-------------|---------|
| **Ralph** | Ralph Loop status | `R:3/10` |
| **Tokens** | Token usage | `30000i/20000o` |
| **Performance** | Response time | `250ms` |

---

## Configuration

### Basic Configuration

```json
{
  "version": "2.0.0",
  "theme": "nerd",
  "width": "auto",
  "modules": {
    "model": {"enabled": true, "priority": 1},
    "project": {"enabled": true, "priority": 1},
    "git": {"enabled": true, "priority": 1},
    "context": {"enabled": true, "priority": 1},
    "cost": {"enabled": true, "priority": 2}
  }
}
```

### Minimal Configuration (Performance Focus)

```json
{
  "theme": "minimal",
  "modules": {
    "time": {"enabled": false},
    "model": {"enabled": true, "priority": 1},
    "project": {"enabled": true, "priority": 1},
    "git": {"enabled": true, "priority": 1, "show_ahead_behind": false},
    "context": {"enabled": true, "priority": 1},
    "cost": {"enabled": false}
  }
}
```

### Full Configuration (Maximum Information)

```json
{
  "theme": "nerd",
  "modules": {
    "time": {"enabled": true, "priority": 2},
    "model": {"enabled": true, "priority": 1},
    "project": {"enabled": true, "priority": 1},
    "git": {
      "enabled": true,
      "priority": 1,
      "show_branch": true,
      "show_status": true,
      "show_ahead_behind": true
    },
    "context": {"enabled": true, "priority": 1},
    "cost": {"enabled": true, "priority": 2},
    "agent": {"enabled": true, "priority": 2},
    "task": {"enabled": true, "priority": 2},
    "progress": {"enabled": true, "priority": 2},
    "ralph": {"enabled": true, "priority": 3},
    "tokens": {"enabled": true, "priority": 3}
  }
}
```

---

## Performance

### Benchmark Results

| Version | Execution Time | Cache Status | Information Modules |
|---------|---------------|--------------|---------------------|
| v1.0    | 122ms         | No cache     | 7 modules           |
| v2.0 (cold) | 728ms     | Cold cache   | 15 modules          |
| v2.0 (warm) | 85ms      | Warm cache   | 15 modules          |

### Performance Optimization

**Caching System**:
- Git operations: 72x faster (580ms → 8ms)
- Cache hit rate: 96% average
- TTL: 5-60 seconds depending on module

**Lazy Evaluation**:
- Only compute displayed modules
- Priority-based rendering
- Adaptive to terminal width

**Optimized Git Operations**:
- Fast porcelain format
- Minimal subprocess calls
- Intelligent cache invalidation

📊 **[Read the Full Performance Report](./HUD-PERFORMANCE-COMPARISON.md)**

---

## Themes

### Available Themes

| Theme | Border | Progress | Separator | Git Symbols |
|-------|--------|----------|-----------|-------------|
| **default** | `-` | `#` `.` | `\|` | `✓` `*` `^` `v` |
| **minimal** | ` ` | `=` `-` | `\|` | `✓` `●` `↑` `↓` |
| **unicode** | `─` | `█` `░` | `│` | `✓` `●` `↑` `↓` |
| **nerd** | `━` | `█` `▒` | `┃` | `` (nerd fonts) |

### Setting Theme

**In configuration file**:
```json
{
  "theme": "nerd"
}
```

**Via environment variable**:
```bash
export HUD_THEME=nerd
```

**Via command line**:
```bash
hud-v2.sh theme nerd
```

---

## Commands

```bash
# Render statusline
hud-v2.sh render

# Render with border
hud-v2.sh full

# Use specific theme
hud-v2.sh theme nerd

# Show configuration
hud-v2.sh config

# Clear cache
hud-v2.sh cache-clear

# Show version
hud-v2.sh version

# Show help
hud-v2.sh help
```

---

## Troubleshooting

### Common Issues

**Git information not showing?**
```bash
# Check if in git repository
git rev-parse --git-dir

# Initialize git if needed
git init
```

**Statusline not updating?**
```bash
# Clear cache
hud-v2.sh cache-clear

# Restart Claude Code
```

**Symbols not displaying?**
- Install a [Nerd Font](https://www.nerdfonts.com/)
- Or use `default` theme

**Performance issues?**
```json
{
  "modules": {
    "git": {"show_ahead_behind": false}
  }
}
```

📖 **[Read the Troubleshooting Guide](./HUD-STATUSLINE-GUIDE.md#troubleshooting)**

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                    HUD StatusLine v2.0                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Theme      │  │ Configuration│  │    Cache     │ │
│  │   System     │  │    System    │  │   System     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Information Gathering Layer            │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ Time │ Model │ Project │ Git │ Context │ Cost   │  │
│  │ Agent│ Task  │ Progress│Ralph│ Tokens  │ Perf   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │              Rendering Layer                     │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ Priority System │ Color Coding │ Adaptive Width │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
Claude Code Session JSON
         ↓
    stdin (JSON)
         ↓
  HUD StatusLine v2.0
         ↓
  ┌──────────────┐
  │ Load Config  │
  └──────┬───────┘
         ↓
  ┌──────────────┐
  │ Load Theme   │
  └──────┬───────┘
         ↓
  ┌──────────────┐
  │ Gather Info  │ ← Cache System
  └──────┬───────┘
         ↓
  ┌──────────────┐
  │ Render       │
  └──────┬───────┘
         ↓
    stdout (ANSI)
         ↓
  Claude Code Display
```

---

## Comparison with v1.0

| Feature | v1.0 | v2.0 | Improvement |
|---------|------|------|-------------|
| **Information Modules** | 7 | 15 | +114% |
| **Execution Time** | 122ms | 85ms (warm) | +30% faster |
| **Caching** | ❌ | ✅ | 72x faster git |
| **Git Support** | ❌ | ✅ | New |
| **Cost Tracking** | ❌ | ✅ | New |
| **Context Tracking** | ❌ | ✅ | New |
| **Priority System** | ❌ | ✅ | New |
| **Adaptive Display** | ❌ | ✅ | New |
| **Configuration** | Basic | Advanced | Enhanced |
| **Themes** | 4 | 4 | Same |
| **Documentation** | Basic | Comprehensive | Enhanced |

---

## Roadmap

### v2.1 (Planned)
- [ ] Parallel git operations
- [ ] Custom color support
- [ ] Multi-line display
- [ ] System monitoring (CPU/memory)
- [ ] Animation support

### v2.2 (Future)
- [ ] Rust performance-critical sections
- [ ] Custom segment API
- [ ] Plugin system
- [ ] Visual configuration tool
- [ ] Remote statusline support

### v3.0 (Vision)
- [ ] Full Rust rewrite
- [ ] Real-time updates (no polling)
- [ ] Advanced analytics
- [ ] AI-powered insights
- [ ] Cloud sync

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](../CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/claude-code-instruction-system.git
cd claude-code-instruction-system

# Install dependencies
# (none required for bash version)

# Run tests
bash tests/hud-v2-test.sh

# Run benchmarks
bash tests/hud-v2-benchmark.sh
```

### Testing

```bash
# Unit tests
bash tests/hud-v2-test.sh

# Performance tests
bash tests/hud-v2-benchmark.sh

# Integration tests
bash tests/hud-v2-integration.sh
```

---

## License

MIT License - see [LICENSE](../LICENSE) for details

---

## Acknowledgments

### Inspiration
- [Starship Prompt](https://starship.rs/) - Rust-based prompt
- [tmux-powerline](https://github.com/erikw/tmux-powerline) - Bash statusline
- [Powerlevel10k](https://github.com/romkatv/powerlevel10k) - Zsh theme

### Resources
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code/statusline)
- [Nerd Fonts](https://www.nerdfonts.com/)
- [ANSI Escape Codes](https://en.wikipedia.org/wiki/ANSI_escape_code)

### Community
- Claude Code community for feedback and testing
- Open source contributors

---

## Support

### Documentation
- 📖 [Quick Start Guide](./HUD-QUICK-START.md)
- 📚 [Full User Guide](./HUD-STATUSLINE-GUIDE.md)
- 📊 [Performance Comparison](./HUD-PERFORMANCE-COMPARISON.md)
- 🔬 [Research Report](./STATUSLINE-RESEARCH-REPORT.md)

### Getting Help
- Check [Troubleshooting Guide](./HUD-STATUSLINE-GUIDE.md#troubleshooting)
- Review [FAQ](./HUD-STATUSLINE-GUIDE.md#faq)
- Open an [Issue](https://github.com/yourusername/claude-code-instruction-system/issues)

### Contact
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

## Statistics

- **Lines of Code**: 736 (vs 299 in v1.0)
- **File Size**: 19KB (vs 6.5KB in v1.0)
- **Information Modules**: 15 (vs 7 in v1.0)
- **Cache Files**: 4
- **Themes**: 4
- **Documentation Pages**: 4
- **Development Time**: 15 hours
- **Performance Gain**: 30% (with warm cache)

---

**Version**: 2.0.0
**Release Date**: 2026-02-14
**Status**: Production Ready
**Maintained by**: Taiyi Meta-System

---

⭐ **Star this project if you find it useful!**

📖 **[Get Started Now](./HUD-QUICK-START.md)**

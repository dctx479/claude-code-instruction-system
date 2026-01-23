# Taiyi Git Info

> High-performance Git information collector for Taiyi Meta-System

## Overview

`taiyi-git-info` is a blazingly fast Git status and information collector written in Rust. It provides a **5-8x performance improvement** over traditional shell script approaches using `git` commands.

## Features

- **Fast Status Collection**: Single-pass status scanning
- **Branch Information**: Local and remote branch details with tracking info
- **Commit History**: Efficient log traversal with relative timestamps
- **Diff Statistics**: File-level diff information
- **Multiple Output Formats**: Text, JSON, and compact modes
- **Color Output**: Terminal colors for better readability

## Installation

### From Source

```bash
cd tools/git-info-rust
cargo build --release
```

The binary will be at `target/release/git-info`.

### System-wide Installation

```bash
cargo install --path .
```

## Usage

### Basic Commands

```bash
# Full summary (default)
git-info

# Repository status
git-info status
git-info status --untracked --ignored

# Branch information
git-info branch
git-info branch --all

# Commit log
git-info log
git-info log --count 20 --oneline

# Diff statistics
git-info diff
git-info diff --base main
```

### Output Formats

```bash
# Human-readable text (default)
git-info --format text

# JSON output (for scripting)
git-info --format json

# Compact single-line (for prompts)
git-info --format compact
```

### Examples

#### Compact Status for Shell Prompt

```bash
$ git-info status --format compact
main -> origin/main [+2/-1] S:3 U:2 ?:5 clean
```

Output meaning:
- `main`: Current branch
- `-> origin/main`: Tracking branch
- `[+2/-1]`: 2 commits ahead, 1 behind
- `S:3`: 3 staged files
- `U:2`: 2 unstaged changes
- `?:5`: 5 untracked files

#### JSON Output for Scripts

```bash
$ git-info status --format json
{
  "branch": "main",
  "tracking": "origin/main",
  "ahead": 2,
  "behind": 1,
  "staged": {
    "added": 1,
    "modified": 2,
    "deleted": 0,
    "renamed": 0
  },
  "unstaged": {
    "added": 0,
    "modified": 2,
    "deleted": 0,
    "renamed": 0
  },
  "untracked": 5,
  "conflicts": 0,
  "stashes": 1,
  "is_clean": false,
  "is_rebasing": false,
  "is_merging": false,
  "is_bisecting": false
}
```

#### Oneline Log

```bash
$ git-info log --oneline --count 5
a326887 docs(system): add Skills system and expand agent ecosystem
6e31585 feat(system): integrate AI/ML and research support systems
...
```

## Performance

### Benchmarks

| Operation | Shell Script | git-info | Speedup |
|-----------|--------------|----------|---------|
| Status | 45ms | 8ms | 5.6x |
| Branch list | 120ms | 15ms | 8x |
| Log (10) | 80ms | 12ms | 6.7x |
| Full summary | 250ms | 35ms | 7.1x |

### Why It's Faster

1. **libgit2**: Direct repository access without spawning processes
2. **Single-pass**: Status collection in one traversal
3. **No shell overhead**: No command parsing or pipe overhead
4. **Optimized output**: Minimal allocations for output formatting

## Integration with Taiyi

### HUD Statusline

The compact output mode is designed for integration with the Taiyi HUD:

```bash
# In HUD update script
GIT_STATUS=$(git-info status --format compact)
```

### Ralph Loop

Git info is used to track progress during development:

```bash
# Check for uncommitted changes before task completion
if ! git-info status --format json | jq -e '.is_clean'; then
    echo "Warning: Uncommitted changes"
fi
```

### Plan-Scoped Memory

Git commit hashes are recorded in plan memory:

```bash
# Record current commit in plan
COMMIT=$(git-info log --count 1 --format json | jq -r '.[0].hash')
```

## Configuration

### Environment Variables

- `NO_COLOR`: Disable colored output
- `GIT_INFO_FORMAT`: Default output format

### Example Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias gs='git-info status --format compact'
alias gl='git-info log --oneline'
alias gb='git-info branch'
```

## API Reference

### Subcommands

| Command | Description |
|---------|-------------|
| `status` | Show repository status |
| `branch` | Show branch information |
| `log` | Show recent commits |
| `diff` | Show diff statistics |
| `summary` | Show complete summary (default) |

### Global Options

| Option | Description |
|--------|-------------|
| `-p, --path <PATH>` | Repository path (default: .) |
| `-f, --format <FORMAT>` | Output format: text, json, compact |

## Dependencies

- `git2`: libgit2 bindings for Rust
- `clap`: Command-line argument parsing
- `serde`/`serde_json`: JSON serialization
- `chrono`: Date/time handling
- `crossterm`: Terminal colors

## Related Tools

- `hud-render`: HUD rendering tool (Rust)
- `tui-config`: TUI configuration tool (Rust)
- Shell fallback: `scripts/git-info.sh`

## License

MIT License - Part of the Taiyi Meta-System

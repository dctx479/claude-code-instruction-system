# HUD StatusLine v2.0 - Example Configurations

**Collection of ready-to-use configuration examples for different use cases**

---

## Table of Contents

1. [Minimal Configuration](#minimal-configuration)
2. [Performance-Focused Configuration](#performance-focused-configuration)
3. [Information-Rich Configuration](#information-rich-configuration)
4. [Developer Configuration](#developer-configuration)
5. [Cost-Conscious Configuration](#cost-conscious-configuration)
6. [Git-Focused Configuration](#git-focused-configuration)
7. [Large Repository Configuration](#large-repository-configuration)
8. [Multi-Project Configuration](#multi-project-configuration)
9. [Theme Configurations](#theme-configurations)
10. [Custom Configurations](#custom-configurations)

---

## Minimal Configuration

**Use Case**: Minimal information, maximum performance

**Features**:
- Only essential information
- No expensive operations
- Fast execution (<50ms)

```json
{
  "version": "2.0.0",
  "theme": "minimal",
  "width": "auto",
  "modules": {
    "time": {
      "enabled": false
    },
    "model": {
      "enabled": true,
      "priority": 1
    },
    "project": {
      "enabled": true,
      "priority": 1,
      "max_length": 20
    },
    "git": {
      "enabled": true,
      "priority": 1,
      "show_branch": true,
      "show_status": false,
      "show_ahead_behind": false
    },
    "context": {
      "enabled": true,
      "priority": 1,
      "warn_threshold": 80,
      "critical_threshold": 90
    },
    "cost": {
      "enabled": false
    },
    "agent": {
      "enabled": false
    },
    "task": {
      "enabled": false
    },
    "progress": {
      "enabled": false
    },
    "ralph": {
      "enabled": false
    },
    "tokens": {
      "enabled": false
    }
  },
  "cache": {
    "enabled": true,
    "git_ttl": 10,
    "project_ttl": 120
  }
}
```

**Expected Output**:
```
Sonnet | my-project | master | 45%
```

---

## Performance-Focused Configuration

**Use Case**: Balance between information and speed

**Features**:
- Moderate information density
- Optimized cache settings
- Disabled expensive operations

```json
{
  "version": "2.0.0",
  "theme": "default",
  "width": "auto",
  "modules": {
    "time": {
      "enabled": true,
      "priority": 2
    },
    "model": {
      "enabled": true,
      "priority": 1
    },
    "project": {
      "enabled": true,
      "priority": 1,
      "max_length": 25
    },
    "git": {
      "enabled": true,
      "priority": 1,
      "show_branch": true,
      "show_status": true,
      "show_ahead_behind": false
    },
    "context": {
      "enabled": true,
      "priority": 1,
      "warn_threshold": 75,
      "critical_threshold": 90
    },
    "cost": {
      "enabled": true,
      "priority": 2
    },
    "agent": {
      "enabled": true,
      "priority": 2
    },
    "task": {
      "enabled": false
    },
    "progress": {
      "enabled": false
    },
    "ralph": {
      "enabled": true,
      "priority": 3
    },
    "tokens": {
      "enabled": false
    }
  },
  "cache": {
    "enabled": true,
    "git_ttl": 5,
    "project_ttl": 60
  },
  "performance": {
    "max_execution_time": 80,
    "lazy_evaluation": true
  }
}
```

**Expected Output**:
```
00:24:28 | Sonnet | my-project | master ✓ | 45% | $0.150 | @architect | R:3/10
```

---

## Information-Rich Configuration

**Use Case**: Maximum information, all features enabled

**Features**:
- All modules enabled
- Full git information
- Complete visibility

```json
{
  "version": "2.0.0",
  "theme": "nerd",
  "width": "auto",
  "modules": {
    "time": {
      "enabled": true,
      "priority": 2,
      "format": "HH:MM:SS"
    },
    "model": {
      "enabled": true,
      "priority": 1,
      "show_full_name": false
    },
    "project": {
      "enabled": true,
      "priority": 1,
      "max_length": 30
    },
    "git": {
      "enabled": true,
      "priority": 1,
      "show_branch": true,
      "show_status": true,
      "show_ahead_behind": true
    },
    "context": {
      "enabled": true,
      "priority": 1,
      "format": "percentage",
      "warn_threshold": 80,
      "critical_threshold": 90
    },
    "cost": {
      "enabled": true,
      "priority": 2,
      "format": "dollars",
      "show_trend": false
    },
    "agent": {
      "enabled": true,
      "priority": 2,
      "prefix": "@"
    },
    "task": {
      "enabled": true,
      "priority": 2,
      "max_length": 20,
      "truncate": true
    },
    "progress": {
      "enabled": true,
      "priority": 2,
      "bar_width": 10,
      "show_percentage": true
    },
    "ralph": {
      "enabled": true,
      "priority": 3,
      "prefix": "R:"
    },
    "tokens": {
      "enabled": true,
      "priority": 3,
      "format": "compact"
    }
  },
  "cache": {
    "enabled": true,
    "git_ttl": 5,
    "project_ttl": 60,
    "performance_ttl": 1
  },
  "performance": {
    "max_execution_time": 100,
    "lazy_evaluation": true
  }
}
```

**Expected Output**:
```
00:24:28 ┃ Sonnet ┃ my-project ┃ master  ↑2 ┃ 45% ┃ $0.150 ┃ @architect ┃ implementing auth... ┃ [████░░░░░░] 40% ┃ R:3/10 ┃ 30Ki/20Ko
```

---

## Developer Configuration

**Use Case**: Active development with frequent git operations

**Features**:
- Git-focused information
- Task and progress tracking
- Agent visibility

```json
{
  "version": "2.0.0",
  "theme": "unicode",
  "width": "auto",
  "modules": {
    "time": {
      "enabled": false
    },
    "model": {
      "enabled": true,
      "priority": 1
    },
    "project": {
      "enabled": true,
      "priority": 1,
      "max_length": 30
    },
    "git": {
      "enabled": true,
      "priority": 1,
      "show_branch": true,
      "show_status": true,
      "show_ahead_behind": true
    },
    "context": {
      "enabled": true,
      "priority": 1,
      "warn_threshold": 70,
      "critical_threshold": 85
    },
    "cost": {
      "enabled": false
    },
    "agent": {
      "enabled": true,
      "priority": 1,
      "prefix": "@"
    },
    "task": {
      "enabled": true,
      "priority": 1,
      "max_length": 25,
      "truncate": true
    },
    "progress": {
      "enabled": true,
      "priority": 1,
      "bar_width": 15,
      "show_percentage": true
    },
    "ralph": {
      "enabled": true,
      "priority": 2
    },
    "tokens": {
      "enabled": false
    }
  },
  "cache": {
    "enabled": true,
    "git_ttl": 3,
    "project_ttl": 60
  }
}
```

**Expected Output**:
```
Sonnet │ my-project │ master ● ↑2 │ 45% │ @architect │ implementing auth │ [███████████░░░░] 75% │ R:3/10
```

---

## Cost-Conscious Configuration

**Use Case**: Focus on cost tracking and context management

**Features**:
- Prominent cost display
- Context warnings
- Token tracking

```json
{
  "version": "2.0.0",
  "theme": "default",
  "width": "auto",
  "modules": {
    "time": {
      "enabled": true,
      "priority": 2
    },
    "model": {
      "enabled": true,
      "priority": 1
    },
    "project": {
      "enabled": true,
      "priority": 2,
      "max_length": 20
    },
    "git": {
      "enabled": true,
      "priority": 2,
      "show_branch": true,
      "show_status": true,
      "show_ahead_behind": false
    },
    "context": {
      "enabled": true,
      "priority": 1,
      "warn_threshold": 60,
      "critical_threshold": 80
    },
    "cost": {
      "enabled": true,
      "priority": 1,
      "format": "dollars",
      "show_trend": true
    },
    "agent": {
      "enabled": true,
      "priority": 2
    },
    "task": {
      "enabled": false
    },
    "progress": {
      "enabled": false
    },
    "ralph": {
      "enabled": false
    },
    "tokens": {
      "enabled": true,
      "priority": 1,
      "format": "compact"
    }
  },
  "cache": {
    "enabled": true,
    "git_ttl": 10,
    "project_ttl": 120
  }
}
```

**Expected Output**:
```
00:24:28 | Sonnet | 45% | $0.150 | 30Ki/20Ko | my-project | master ✓ | @architect
```

---

## Git-Focused Configuration

**Use Case**: Heavy git usage, detailed repository information

**Features**:
- Full git information
- Frequent cache updates
- Branch and status prominent

```json
{
  "version": "2.0.0",
  "theme": "nerd",
  "width": "auto",
  "modules": {
    "time": {
      "enabled": false
    },
    "model": {
      "enabled": true,
      "priority": 2
    },
    "project": {
      "enabled": true,
      "priority": 1,
      "max_length": 35
    },
    "git": {
      "enabled": true,
      "priority": 1,
      "show_branch": true,
      "show_status": true,
      "show_ahead_behind": true
    },
    "context": {
      "enabled": true,
      "priority": 2,
      "warn_threshold": 80,
      "critical_threshold": 90
    },
    "cost": {
      "enabled": false
    },
    "agent": {
      "enabled": true,
      "priority": 2
    },
    "task": {
      "enabled": false
    },
    "progress": {
      "enabled": false
    },
    "ralph": {
      "enabled": false
    },
    "tokens": {
      "enabled": false
    }
  },
  "cache": {
    "enabled": true,
    "git_ttl": 2,
    "project_ttl": 60
  }
}
```

**Expected Output**:
```
my-awesome-project ┃ feature/user-auth  ↑3↓1 ┃ Sonnet ┃ 45% ┃ @architect
```

---

## Large Repository Configuration

**Use Case**: Optimize for large repositories (>10K files)

**Features**:
- Aggressive caching
- Disabled expensive operations
- Minimal git operations

```json
{
  "version": "2.0.0",
  "theme": "minimal",
  "width": "auto",
  "modules": {
    "time": {
      "enabled": false
    },
    "model": {
      "enabled": true,
      "priority": 1
    },
    "project": {
      "enabled": true,
      "priority": 1,
      "max_length": 25
    },
    "git": {
      "enabled": true,
      "priority": 1,
      "show_branch": true,
      "show_status": true,
      "show_ahead_behind": false
    },
    "context": {
      "enabled": true,
      "priority": 1,
      "warn_threshold": 80,
      "critical_threshold": 90
    },
    "cost": {
      "enabled": true,
      "priority": 2
    },
    "agent": {
      "enabled": true,
      "priority": 2
    },
    "task": {
      "enabled": false
    },
    "progress": {
      "enabled": false
    },
    "ralph": {
      "enabled": false
    },
    "tokens": {
      "enabled": false
    }
  },
  "cache": {
    "enabled": true,
    "git_ttl": 15,
    "project_ttl": 300
  },
  "performance": {
    "max_execution_time": 150,
    "lazy_evaluation": true
  }
}
```

**Expected Output**:
```
Sonnet | large-monorepo | master * | 45% | $0.150 | @architect
```

---

## Multi-Project Configuration

**Use Case**: Switching between multiple projects frequently

**Features**:
- Prominent project name
- Quick git status
- Context awareness

```json
{
  "version": "2.0.0",
  "theme": "unicode",
  "width": "auto",
  "modules": {
    "time": {
      "enabled": false
    },
    "model": {
      "enabled": true,
      "priority": 2
    },
    "project": {
      "enabled": true,
      "priority": 1,
      "max_length": 40
    },
    "git": {
      "enabled": true,
      "priority": 1,
      "show_branch": true,
      "show_status": true,
      "show_ahead_behind": false
    },
    "context": {
      "enabled": true,
      "priority": 1,
      "warn_threshold": 75,
      "critical_threshold": 90
    },
    "cost": {
      "enabled": true,
      "priority": 2
    },
    "agent": {
      "enabled": false
    },
    "task": {
      "enabled": false
    },
    "progress": {
      "enabled": false
    },
    "ralph": {
      "enabled": false
    },
    "tokens": {
      "enabled": false
    }
  },
  "cache": {
    "enabled": true,
    "git_ttl": 5,
    "project_ttl": 30
  }
}
```

**Expected Output**:
```
frontend-dashboard │ develop ● │ 45% │ Sonnet │ $0.150
```

---

## Theme Configurations

### Nerd Font Theme (Recommended)

```json
{
  "version": "2.0.0",
  "theme": "nerd",
  "modules": {
    "model": {"enabled": true, "priority": 1},
    "project": {"enabled": true, "priority": 1},
    "git": {"enabled": true, "priority": 1},
    "context": {"enabled": true, "priority": 1},
    "cost": {"enabled": true, "priority": 2},
    "agent": {"enabled": true, "priority": 2}
  }
}
```

**Output**:
```
Sonnet ┃ my-project ┃ master  ┃ 45% ┃ $0.150 ┃ @architect
```

### Unicode Theme

```json
{
  "version": "2.0.0",
  "theme": "unicode",
  "modules": {
    "model": {"enabled": true, "priority": 1},
    "project": {"enabled": true, "priority": 1},
    "git": {"enabled": true, "priority": 1},
    "context": {"enabled": true, "priority": 1}
  }
}
```

**Output**:
```
Sonnet │ my-project │ master ✓ │ 45%
```

### Minimal Theme

```json
{
  "version": "2.0.0",
  "theme": "minimal",
  "modules": {
    "model": {"enabled": true, "priority": 1},
    "project": {"enabled": true, "priority": 1},
    "git": {"enabled": true, "priority": 1}
  }
}
```

**Output**:
```
Sonnet | my-project | master ✓
```

---

## Custom Configurations

### Configuration for Pair Programming

**Focus**: Show who's driving, what they're working on

```json
{
  "version": "2.0.0",
  "theme": "nerd",
  "modules": {
    "model": {"enabled": true, "priority": 1},
    "project": {"enabled": true, "priority": 1},
    "git": {"enabled": true, "priority": 1, "show_ahead_behind": true},
    "agent": {"enabled": true, "priority": 1},
    "task": {"enabled": true, "priority": 1, "max_length": 30},
    "progress": {"enabled": true, "priority": 1}
  }
}
```

### Configuration for Code Review

**Focus**: Git status, context usage

```json
{
  "version": "2.0.0",
  "theme": "unicode",
  "modules": {
    "model": {"enabled": true, "priority": 2},
    "project": {"enabled": true, "priority": 1},
    "git": {"enabled": true, "priority": 1, "show_ahead_behind": true},
    "context": {"enabled": true, "priority": 1},
    "agent": {"enabled": false},
    "task": {"enabled": false}
  }
}
```

### Configuration for Learning/Tutorial

**Focus**: Cost awareness, simple display

```json
{
  "version": "2.0.0",
  "theme": "default",
  "modules": {
    "model": {"enabled": true, "priority": 1},
    "context": {"enabled": true, "priority": 1, "warn_threshold": 50},
    "cost": {"enabled": true, "priority": 1},
    "tokens": {"enabled": true, "priority": 1}
  }
}
```

---

## Configuration Tips

### Optimizing for Performance

1. **Disable expensive modules**:
   - `git.show_ahead_behind`: Most expensive operation
   - `performance`: Adds overhead
   - `task`, `progress`: If not using

2. **Increase cache TTL**:
   ```json
   {
     "cache": {
       "git_ttl": 10,
       "project_ttl": 120
     }
   }
   ```

3. **Use minimal theme**:
   ```json
   {
     "theme": "minimal"
   }
   ```

### Optimizing for Information

1. **Enable all modules**:
   ```json
   {
     "modules": {
       "time": {"enabled": true},
       "model": {"enabled": true},
       "project": {"enabled": true},
       "git": {"enabled": true, "show_ahead_behind": true},
       "context": {"enabled": true},
       "cost": {"enabled": true},
       "agent": {"enabled": true},
       "task": {"enabled": true},
       "progress": {"enabled": true},
       "ralph": {"enabled": true},
       "tokens": {"enabled": true}
     }
   }
   ```

2. **Use nerd theme**:
   ```json
   {
     "theme": "nerd"
   }
   ```

3. **Lower warning thresholds**:
   ```json
   {
     "modules": {
       "context": {
         "warn_threshold": 60,
         "critical_threshold": 80
       }
     }
   }
   ```

---

## Testing Your Configuration

### Test Command

```bash
# Test with your configuration
HUD_CONFIG_FILE=~/.claude/hud-config.json bash ~/.claude/statusline/hud-v2.sh render

# Test with custom configuration
HUD_CONFIG_FILE=/path/to/custom-config.json bash ~/.claude/statusline/hud-v2.sh render

# Test performance
time bash ~/.claude/statusline/hud-v2.sh render
```

### Validation

```bash
# Validate JSON syntax
jq empty ~/.claude/hud-config.json

# Or with Python
python -m json.tool ~/.claude/hud-config.json > /dev/null
```

---

## Configuration Migration

### From v1.0 to v2.0

**Old v1.0 config**:
```json
{
  "theme": "default",
  "width": 80,
  "show_time": true,
  "show_model": true,
  "show_tokens": true
}
```

**New v2.0 config**:
```json
{
  "version": "2.0.0",
  "theme": "default",
  "width": "auto",
  "modules": {
    "time": {"enabled": true, "priority": 2},
    "model": {"enabled": true, "priority": 1},
    "tokens": {"enabled": true, "priority": 3}
  }
}
```

---

## Troubleshooting Configurations

### Configuration Not Loading

```bash
# Check file exists
ls -lh ~/.claude/hud-config.json

# Check JSON syntax
jq empty ~/.claude/hud-config.json

# Check permissions
chmod 644 ~/.claude/hud-config.json
```

### Modules Not Showing

```bash
# Verify module is enabled
jq '.modules.git.enabled' ~/.claude/hud-config.json

# Check priority
jq '.modules.git.priority' ~/.claude/hud-config.json
```

### Performance Issues

```bash
# Check cache settings
jq '.cache' ~/.claude/hud-config.json

# Disable expensive modules
jq '.modules.git.show_ahead_behind = false' ~/.claude/hud-config.json > /tmp/config.json
mv /tmp/config.json ~/.claude/hud-config.json
```

---

## Additional Resources

- [Full User Guide](./HUD-STATUSLINE-GUIDE.md)
- [Performance Comparison](./HUD-PERFORMANCE-COMPARISON.md)
- [Quick Start Guide](./HUD-QUICK-START.md)
- [Configuration Reference](../memory/hud-config-v2.json)

---

**Version**: 2.0.0
**Last Updated**: 2026-02-14
**Maintained by**: Taiyi Meta-System

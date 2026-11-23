---
name: reflection
description: 根据真实任务证据复盘，区分机械检查与判断规则；保留历史案例，不凑经验数量或自动扩张流程。
license: MIT
metadata:
  category: system
  tags:
  - reflection
  - lessons-learned
  - knowledge-compounding
  - ingest
  - self-evolution
  integration:
  - neat
  - skill-creator
  - knowledge-compounding
  version: 1.0.0
  trigger:
  - /reflection
  - 复盘一下
  - 总结经验
  - 提炼教训
  - 记录一下这次的收获
disable-model-invocation: true
---

# Evidence-based reflection

Use the completed task's actual artifacts and command results. Search related existing entries before proposing a new lesson. Follow the mechanical-versus-judgment split in `docs/VNEXT-WORKFLOW.md` and /evolve.

For each supported finding record the incident, evidence pointer, before/after behavior, verification method and confidence. Produce only as many findings as evidence supports; zero is valid. Do not invent another incident to meet the two-event rule for new permanent rules.
Distinguish a template, proposed metric and real measurement. Invocation counts do not establish quality, success rate, time or cost. Missing raw measurements remain unknown.

Write only the artifact the user requested. Historical memory remains unchanged unless its update is authorized; when authorized append dated evidence and mark supersession explicitly, preserving the original case. Do not automatically chain neat, create a new Skill, add rules or build a wiki. Already supplied authorization is sufficient; do not ask again for that same action.

---

## Integration: Session Notes and Annotations

**New in v1.1.0**: Reflection now prioritizes reading from session notes and conversation annotations to reduce recall burden.

### Pre-Reflection Checklist

Before starting reflection, automatically check:

1. **Session Notes**: Read `.claude/scratch/session-*.md` for current session
   ```bash
   python scripts/note-manager.py show session
   ```

2. **Annotations**: Read `.claude/context/annotations.jsonl` for marked insights
   ```bash
   python scripts/annotation-manager.py list --limit 50
   ```

3. **Checkpoint Status**: Review recent checkpoint for changed files
   ```bash
   python scripts/checkpoint.py review
   ```

### Annotation-Driven Reflection

**Priority order**:
1. **Annotated insights** (`key-insight`, `decision`) - User explicitly marked
2. **Session notes** (`insight`, `decision` tags) - Recorded during work
3. **Conversation history** - Full context as fallback

**Output format**:
```markdown
## Reflection Summary

### Annotated Insights (from !mark)
- [key-insight @ turn 15] Docker exec bypasses network routing
- [decision @ turn 23] Use JWT instead of session cookies

### Session Notes
- [idea] Try method B after A failed
- [assumption] Token stored in httpOnly cookie - VERIFIED

### Extracted Lessons
1. ...
```

### Commands

```bash
# Standard reflection (automatically reads annotations + notes)
/reflection

# Show annotation summary before reflection
python scripts/annotation-manager.py summary

# Export annotations to review
python scripts/annotation-manager.py export reflection-input.md
```

### Benefits

- **Faster reflection**: Direct access to marked key points
- **Higher accuracy**: User-marked insights have higher confidence
- **Lower cognitive load**: No need to recall "which turn had the insight"
- **Better context**: Session notes provide temporal flow

### Integration with memory/

Reflection continues to write to:
- `memory/lessons-learned.md` - Extracted lessons
- `memory/error-patterns.md` - Error cases
- `memory/best-practices.md` - Validated practices

Annotations and session notes are **input sources**, not replacement for structured memory.

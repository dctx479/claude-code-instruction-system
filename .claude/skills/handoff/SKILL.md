---
name: handoff
description: 上下文交接仪式 - /compact 之前写交接文档（compact模式），或生成可复制的续接 prompt 用于开新对话窗口（new-window模式）
license: MIT
metadata:
  category: system
  tags:
  - handoff
  - context-engineering
  - compact
  - session-management
  - continuity
  integration:
  - prime
  - neat
  - reflection
  - context-engineering
  version: 1.1.0
  trigger:
  - /handoff
  - 准备 compact
  - 上下文快满了
  - 交接一下
  - 记录当前进度
  - 开新窗口继续
  - 生成续接 prompt
  - context is getting full
disable-model-invocation: true
---

# Verified handoff

Use `scripts/checkpoint.py` as described in `docs/VNEXT-WORKFLOW.md`.
For a global install, use `$HOME/.claude/scripts/checkpoint.py` with the target project as cwd (requires the commands component). Do not assume this repository's scripts exist in every project.
Save one worktree-local checkpoint before compacting or moving to a new session. Include goal, completed work, next actions, evidence commands/paths and the repository-relative changed files.
Feed JSON to `python scripts/checkpoint.py save`; the script computes hashes. Never fabricate test results or hashes.
On continuation run `python scripts/checkpoint.py show`: 0 valid, 2 absent, 1 corrupted/stale. If stale, inspect the changes and preserve the original evidence before updating.
For a new-window handoff, produce a short continuation prompt pointing to the same checkpoint; do not duplicate the full state in memory/handoff.md.
Legacy memory/handoff.md may be read as historical context only, with a WARNING that it lacks integrity verification.

---

## Integration: Session Notes and Annotations

**New in v1.2.0**: Handoff now checks for unarchived session notes and includes annotation summaries.

### Pre-Handoff Checklist

Before generating handoff document:

1. **Check for unarchived session notes**:
   ```bash
   # Check if session notes exist
   ls .claude/scratch/session-*.md 2>/dev/null
   ```
   
   If found:
   - **Option 1**: Archive now → `python scripts/note-manager.py archive`
   - **Option 2**: Include in handoff → Content added to handoff document
   - **Option 3**: Discard → User confirms, then clear

2. **Check annotations**:
   ```bash
   python scripts/annotation-manager.py summary
   ```
   
   If annotations exist:
   - Include summary in handoff document
   - Export full list → `python scripts/annotation-manager.py export handoff-annotations.md`

3. **Review checkpoint**:
   ```bash
   python scripts/checkpoint.py review
   ```
   
   Report any ⚠️ (missing) or ⛔ (modified) files in handoff.

### Handoff Document Structure

```markdown
# Handoff - {session-id} - {timestamp}

## Checkpoint
- Status: [checkpoint.py review summary]
- Changed files: [list]

## Session Notes Summary
### Ideas (3)
- Try method B after A failed
- Docker exec bypasses routing
- ...

### Decisions (2)
- Use JWT for auth
- ...

### TODOs (1)
- Verify token refresh logic

## Annotations Summary
- key-insight: 2
- todo: 3
- decision: 1

[Full annotation export: handoff-annotations.md]

## Next Actions
- ...
```

### Automatic Actions

On `/handoff` execution:

1. ✅ Create checkpoint
2. ✅ Check for session notes → Prompt user
3. ✅ Check for annotations → Include summary
4. ✅ Archive session notes (if user confirms)
5. ✅ Generate handoff document
6. ✅ Report status

### Commands

```bash
# Standard handoff (compact mode)
/handoff

# Check session notes before handoff
/note show session

# Check annotations before handoff
python scripts/annotation-manager.py summary

# Manual archive
python scripts/note-manager.py archive
```

### Benefits

- **No information loss**: Session notes preserved or archived
- **Context continuity**: Annotations carry over to next session
- **Explicit decisions**: User controls what to keep/discard
- **Audit trail**: Archived notes provide history

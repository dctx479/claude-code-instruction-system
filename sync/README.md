# Memory Synchronization System

Minimal synchronization mechanism for the Taiyi meta-system memory layer.

## Components

### 1. memory-sync.py
Synchronizes `memory/*.md` files with conflict detection.

**Usage:**
```bash
python sync/memory-sync.py [strategy]
```

**Strategies:**
- `last_write_wins` (default): Use most recent modification
- `manual`: Report conflicts for manual resolution

**Features:**
- File hash tracking
- Modification time tracking
- Conflict detection
- Sync state persistence (`.sync-state.json`)
- Sync logging (`.sync-log.jsonl`)

### 2. graphiti-sync.py
Syncs memory data to Graphiti knowledge graph (placeholder).

**Usage:**
```bash
python sync/graphiti-sync.py [--dry-run]
```

**Features:**
- Parses `lessons-learned.md` into structured entities
- Parses `agent-performance.md` into metrics
- Placeholder for Graphiti API integration
- Dry-run mode for testing

**Status:** Placeholder - requires Graphiti configuration

### 3. conflict-resolver.py
Resolves synchronization conflicts.

**Usage:**
```bash
python sync/conflict-resolver.py [strategy]
```

**Strategies:**
- `last_write_wins`: Accept current version
- `merge`: Attempt automatic merge
- `manual`: Require manual intervention

## Sync Architecture

```
memory/*.md ──┬──> memory-sync.py ──> .sync-state.json
              │                    └──> .sync-log.jsonl
              │
              └──> graphiti-sync.py ──> Graphiti API (placeholder)
                                    └──> .graphiti-sync-log.jsonl

Conflicts ──> conflict-resolver.py ──> .conflict-resolution-log.jsonl
```

## Sync Strategies

### Real-time (Graphiti)
- Triggered on file modification
- Immediate knowledge graph update
- Requires Graphiti configuration

### Periodic (memory/*.md)
- Daily: Full sync of all files
- On-demand: Manual trigger
- Conflict detection and resolution

### On-demand
- Manual sync trigger
- Conflict resolution
- Report generation

## Data Flow

1. **File Modification** → Hash calculation → State comparison
2. **Conflict Detection** → Strategy selection → Resolution
3. **Sync Execution** → State update → Log recording
4. **Graphiti Sync** → Entity extraction → API call (placeholder)

## Configuration

Edit `graphiti-sync.py` to enable Graphiti:
```python
GRAPHITI_ENABLED = True  # Set to True when configured
```

Add Graphiti API integration:
```python
# TODO: Implement Graphiti client
# from graphiti import GraphitiClient
# client = GraphitiClient(config)
# client.add_entities(entities)
```

## Logs

- `.sync-state.json`: Current sync state (file hashes, timestamps)
- `.sync-log.jsonl`: Sync operation history
- `.graphiti-sync-log.jsonl`: Graphiti sync history
- `.conflict-resolution-log.jsonl`: Conflict resolution history

## Integration

### With Self-Evolution Protocol
```python
# After learning event
from sync.memory_sync import sync_memory_files
sync_memory_files(strategy="last_write_wins")
```

### With Performance Monitoring
```python
# After performance report generation
from sync.graphiti_sync import sync_to_graphiti
sync_to_graphiti(dry_run=False)
```

### With Agent Orchestration
```python
# After task completion
from sync.memory_sync import sync_memory_files
from sync.graphiti_sync import sync_to_graphiti

sync_memory_files()
sync_to_graphiti()
```

## Future Enhancements

- [ ] Implement Graphiti API integration
- [ ] Add semantic merge for conflicts
- [ ] Support incremental sync
- [ ] Add sync scheduling (cron)
- [ ] Implement bidirectional sync
- [ ] Add sync metrics dashboard

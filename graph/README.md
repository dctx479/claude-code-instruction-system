# Knowledge Graph Module

Minimal implementation of knowledge graph for Apollo system.

## Architecture

```
graph/
├── entities.py    # Entity and Relation definitions
├── storage.py     # Storage layer (JSON/Graphiti)
├── builder.py     # Build graph from Resolution data
├── queries.py     # Query interface
└── __init__.py    # Module exports
```

## Entity Types

- **Problem**: Issues, bugs, errors
- **Solution**: Fixes, resolutions
- **File**: Source files affected
- **Tag**: Categories, labels
- **ErrorPattern**: Common error patterns
- **BestPractice**: Best practices
- **Agent**: AI agents
- **Workflow**: Workflows

## Relation Types

- **SOLVED_BY**: Problem → Solution
- **MODIFIES**: Solution → File
- **OCCURS_IN**: Problem → File
- **RELATED_TO**: Generic relation
- **TAGGED_WITH**: Entity → Tag
- **USES**: Entity uses another
- **DEPENDS_ON**: Dependency relation

## Usage

### Basic Operations

```python
from graph import get_storage, GraphBuilder, GraphQuery, Entity, Relation

# Initialize
storage = get_storage()
builder = GraphBuilder(storage)
query = GraphQuery(storage)

# Build from resolution
resolution = {
    'problem': 'TypeScript type error',
    'solution': 'Add interface definition',
    'files': ['src/agent.ts'],
    'tags': ['typescript', 'types'],
    'severity': 'medium'
}
builder.build_from_resolution(resolution)

# Query
problems = query.find_related_problems('Problem: TypeScript type error')
solutions = query.find_solutions_for_problem('Problem: TypeScript type error')
impact = query.trace_file_impact('src/agent.ts')
```

### Query Examples

```python
# Find related problems
related = query.find_related_problems('Problem: API timeout')

# Find solutions
solutions = query.find_solutions_for_problem('Problem: API timeout')

# Trace file impact
impact = query.trace_file_impact('src/api/client.ts')
# Returns: {'file': Entity, 'problems': [...], 'solutions': [...]}

# Search by tag
results = query.search_by_tag('performance')
# Returns: {'tag': 'performance', 'entities': [...], 'count': 5}
```

## Storage

### Local JSON (Default)

Data stored in `graph/data/`:
- `entities.json`: All entities
- `relations.json`: All relations

### Graphiti (Future)

When Graphiti MCP is configured, automatically uses Neo4j backend.

## Integration Points

1. **Self-Evolution Protocol**: Auto-capture errors and solutions
2. **Agent System**: Record agent performance and patterns
3. **Memory System**: Sync with `memory/*.md` files
4. **QA System**: Track quality issues and fixes

## API Reference

### GraphBuilder

- `build_from_resolution(resolution: Dict)`: Extract and store graph data

### GraphQuery

- `find_related_problems(problem_name: str)`: Find similar problems
- `find_solutions_for_problem(problem_name: str)`: Get solutions
- `find_files_affected_by_problem(problem_name: str)`: Get affected files
- `trace_file_impact(file_path: str)`: Full file impact analysis
- `search_by_tag(tag: str)`: Search by tag

## Data Format

### Resolution Input

```python
{
    'problem': 'Description of problem',
    'solution': 'Description of solution',
    'files': ['file1.py', 'file2.py'],
    'tags': ['tag1', 'tag2'],
    'severity': 'high|medium|low',
    'category': 'bug|feature|refactor',
    'effectiveness': 0.95
}
```

### Entity Structure

```python
Entity(
    name='unique-name',
    type='Problem|Solution|File|Tag',
    properties={'key': 'value'},
    created_at='2026-01-22T...'
)
```

### Relation Structure

```python
Relation(
    source='entity-name',
    type='SOLVED_BY|MODIFIES|...',
    target='entity-name',
    properties={'key': 'value'},
    created_at='2026-01-22T...'
)
```

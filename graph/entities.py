"""Entity definitions for knowledge graph."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class Entity:
    """Base entity in knowledge graph."""
    name: str
    type: str
    properties: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

@dataclass
class Relation:
    """Relationship between entities."""
    source: str
    type: str
    target: str
    properties: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

# Entity types from architecture
class EntityType:
    PROBLEM = "Problem"
    SOLUTION = "Solution"
    FILE = "File"
    TAG = "Tag"
    ERROR_PATTERN = "ErrorPattern"
    BEST_PRACTICE = "BestPractice"
    AGENT = "Agent"
    WORKFLOW = "Workflow"

# Relation types from architecture
class RelationType:
    SOLVED_BY = "SOLVED_BY"
    MODIFIES = "MODIFIES"
    OCCURS_IN = "OCCURS_IN"
    RELATED_TO = "RELATED_TO"
    TAGGED_WITH = "TAGGED_WITH"
    USES = "USES"
    DEPENDS_ON = "DEPENDS_ON"

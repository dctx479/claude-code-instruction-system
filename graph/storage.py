"""Storage layer for knowledge graph - supports local JSON or Graphiti."""
import json
import os
from pathlib import Path
from typing import List, Optional, Dict
from .entities import Entity, Relation

class GraphStorage:
    """Abstract storage interface."""

    def add_entity(self, entity: Entity) -> bool:
        raise NotImplementedError

    def add_relation(self, relation: Relation) -> bool:
        raise NotImplementedError

    def get_entity(self, name: str) -> Optional[Entity]:
        raise NotImplementedError

    def query_entities(self, type: Optional[str] = None, **filters) -> List[Entity]:
        raise NotImplementedError

    def query_relations(self, source: Optional[str] = None, target: Optional[str] = None) -> List[Relation]:
        raise NotImplementedError

class LocalJSONStorage(GraphStorage):
    """Local JSON file storage."""

    def __init__(self, data_dir: str = "graph/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.entities_file = self.data_dir / "entities.json"
        self.relations_file = self.data_dir / "relations.json"
        self._load()

    def _load(self):
        self.entities = {}
        self.relations = []

        if self.entities_file.exists():
            with open(self.entities_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.entities = {k: Entity(**v) for k, v in data.items()}

        if self.relations_file.exists():
            with open(self.relations_file, 'r', encoding='utf-8') as f:
                self.relations = [Relation(**r) for r in json.load(f)]

    def _save(self):
        with open(self.entities_file, 'w', encoding='utf-8') as f:
            json.dump({k: v.__dict__ for k, v in self.entities.items()}, f, indent=2, ensure_ascii=False)

        with open(self.relations_file, 'w', encoding='utf-8') as f:
            json.dump([r.__dict__ for r in self.relations], f, indent=2, ensure_ascii=False)

    def add_entity(self, entity: Entity) -> bool:
        self.entities[entity.name] = entity
        self._save()
        return True

    def add_relation(self, relation: Relation) -> bool:
        self.relations.append(relation)
        self._save()
        return True

    def get_entity(self, name: str) -> Optional[Entity]:
        return self.entities.get(name)

    def query_entities(self, type: Optional[str] = None, **filters) -> List[Entity]:
        results = list(self.entities.values())
        if type:
            results = [e for e in results if e.type == type]
        for key, value in filters.items():
            results = [e for e in results if e.properties.get(key) == value]
        return results

    def query_relations(self, source: Optional[str] = None, target: Optional[str] = None) -> List[Relation]:
        results = self.relations
        if source:
            results = [r for r in results if r.source == source]
        if target:
            results = [r for r in results if r.target == target]
        return results

def get_storage() -> GraphStorage:
    """Get storage instance - tries Graphiti, falls back to local JSON."""
    # TODO: Add Graphiti detection and initialization
    return LocalJSONStorage()

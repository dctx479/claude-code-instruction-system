"""Build knowledge graph from Resolution data."""
from typing import Dict, List
from .entities import Entity, Relation, EntityType, RelationType
from .storage import GraphStorage

class GraphBuilder:
    """Extract and build knowledge graph from resolution data."""

    def __init__(self, storage: GraphStorage):
        self.storage = storage

    def build_from_resolution(self, resolution: Dict) -> None:
        """Extract entities and relations from a resolution."""
        problem = self._extract_problem(resolution)
        solution = self._extract_solution(resolution)
        files = self._extract_files(resolution)
        tags = self._extract_tags(resolution)

        # Add entities
        if problem:
            self.storage.add_entity(problem)
        if solution:
            self.storage.add_entity(solution)
        for file in files:
            self.storage.add_entity(file)
        for tag in tags:
            self.storage.add_entity(tag)

        # Add relations
        if problem and solution:
            self.storage.add_relation(Relation(
                source=problem.name,
                type=RelationType.SOLVED_BY,
                target=solution.name
            ))

        for file in files:
            if solution:
                self.storage.add_relation(Relation(
                    source=solution.name,
                    type=RelationType.MODIFIES,
                    target=file.name
                ))
            if problem:
                self.storage.add_relation(Relation(
                    source=problem.name,
                    type=RelationType.OCCURS_IN,
                    target=file.name
                ))

        for tag in tags:
            if problem:
                self.storage.add_relation(Relation(
                    source=problem.name,
                    type=RelationType.TAGGED_WITH,
                    target=tag.name
                ))

    def _extract_problem(self, resolution: Dict) -> Entity:
        """Extract problem entity."""
        problem_desc = resolution.get('problem', '')
        if not problem_desc:
            return None

        return Entity(
            name=f"Problem: {problem_desc[:50]}",
            type=EntityType.PROBLEM,
            properties={
                'description': problem_desc,
                'severity': resolution.get('severity', 'medium'),
                'category': resolution.get('category', 'general')
            }
        )

    def _extract_solution(self, resolution: Dict) -> Entity:
        """Extract solution entity."""
        solution_desc = resolution.get('solution', '')
        if not solution_desc:
            return None

        return Entity(
            name=f"Solution: {solution_desc[:50]}",
            type=EntityType.SOLUTION,
            properties={
                'description': solution_desc,
                'steps': resolution.get('steps', []),
                'effectiveness': resolution.get('effectiveness', 0.8)
            }
        )

    def _extract_files(self, resolution: Dict) -> List[Entity]:
        """Extract file entities."""
        files = resolution.get('files', [])
        return [
            Entity(
                name=file,
                type=EntityType.FILE,
                properties={'path': file}
            )
            for file in files
        ]

    def _extract_tags(self, resolution: Dict) -> List[Entity]:
        """Extract tag entities."""
        tags = resolution.get('tags', [])
        return [
            Entity(
                name=tag,
                type=EntityType.TAG,
                properties={}
            )
            for tag in tags
        ]

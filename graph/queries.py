"""Query interface for knowledge graph."""
from typing import List, Dict, Optional
from .entities import Entity, Relation, EntityType, RelationType
from .storage import GraphStorage

class GraphQuery:
    """Query knowledge graph."""

    def __init__(self, storage: GraphStorage):
        self.storage = storage

    def find_related_problems(self, problem_name: str) -> List[Entity]:
        """Find problems related to given problem."""
        # Get tags of the problem
        relations = self.storage.query_relations(source=problem_name)
        tags = [r.target for r in relations if r.type == RelationType.TAGGED_WITH]

        # Find other problems with same tags
        related = []
        for tag in tags:
            tag_relations = self.storage.query_relations(target=tag)
            for rel in tag_relations:
                if rel.type == RelationType.TAGGED_WITH and rel.source != problem_name:
                    entity = self.storage.get_entity(rel.source)
                    if entity and entity.type == EntityType.PROBLEM:
                        related.append(entity)

        return related

    def find_solutions_for_problem(self, problem_name: str) -> List[Entity]:
        """Find solutions for a problem."""
        relations = self.storage.query_relations(source=problem_name)
        solutions = []
        for rel in relations:
            if rel.type == RelationType.SOLVED_BY:
                solution = self.storage.get_entity(rel.target)
                if solution:
                    solutions.append(solution)
        return solutions

    def find_files_affected_by_problem(self, problem_name: str) -> List[Entity]:
        """Find files where problem occurs."""
        relations = self.storage.query_relations(source=problem_name)
        files = []
        for rel in relations:
            if rel.type == RelationType.OCCURS_IN:
                file = self.storage.get_entity(rel.target)
                if file:
                    files.append(file)
        return files

    def find_files_modified_by_solution(self, solution_name: str) -> List[Entity]:
        """Find files modified by a solution."""
        relations = self.storage.query_relations(source=solution_name)
        files = []
        for rel in relations:
            if rel.type == RelationType.MODIFIES:
                file = self.storage.get_entity(rel.target)
                if file:
                    files.append(file)
        return files

    def trace_file_impact(self, file_path: str) -> Dict:
        """Trace all problems and solutions related to a file."""
        file_entity = self.storage.get_entity(file_path)
        if not file_entity:
            return {'problems': [], 'solutions': []}

        # Find problems occurring in this file
        problem_relations = self.storage.query_relations(target=file_path)
        problems = []
        for rel in problem_relations:
            if rel.type == RelationType.OCCURS_IN:
                problem = self.storage.get_entity(rel.source)
                if problem:
                    problems.append(problem)

        # Find solutions modifying this file
        solution_relations = self.storage.query_relations(target=file_path)
        solutions = []
        for rel in solution_relations:
            if rel.type == RelationType.MODIFIES:
                solution = self.storage.get_entity(rel.source)
                if solution:
                    solutions.append(solution)

        return {
            'file': file_entity,
            'problems': problems,
            'solutions': solutions
        }

    def search_by_tag(self, tag: str) -> Dict:
        """Search all entities tagged with given tag."""
        tag_relations = self.storage.query_relations(target=tag)
        entities = []
        for rel in tag_relations:
            if rel.type == RelationType.TAGGED_WITH:
                entity = self.storage.get_entity(rel.source)
                if entity:
                    entities.append(entity)

        return {
            'tag': tag,
            'entities': entities,
            'count': len(entities)
        }

"""Integration adapter for Apollo system to use knowledge graph."""
import sys
from pathlib import Path

# Add graph module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from graph import get_storage, GraphBuilder, GraphQuery

class ApolloGraphAdapter:
    """Adapter to integrate knowledge graph with Apollo system."""

    def __init__(self):
        self.storage = get_storage()
        self.builder = GraphBuilder(self.storage)
        self.query = GraphQuery(self.storage)

    def record_error_resolution(self, error_info: dict) -> None:
        """Record error and its resolution to knowledge graph.

        Args:
            error_info: Dict with keys: problem, solution, files, tags, severity
        """
        resolution = {
            'problem': error_info.get('problem', ''),
            'solution': error_info.get('solution', ''),
            'files': error_info.get('files', []),
            'tags': error_info.get('tags', []),
            'severity': error_info.get('severity', 'medium'),
            'category': error_info.get('category', 'bug'),
            'effectiveness': error_info.get('effectiveness', 0.8)
        }
        self.builder.build_from_resolution(resolution)

    def find_similar_problems(self, problem_description: str) -> list:
        """Find problems similar to the given description.

        Args:
            problem_description: Description of the current problem

        Returns:
            List of similar problem entities
        """
        problem_name = f"Problem: {problem_description[:50]}"
        return self.query.find_related_problems(problem_name)

    def get_solutions(self, problem_description: str) -> list:
        """Get solutions for a given problem.

        Args:
            problem_description: Description of the problem

        Returns:
            List of solution entities
        """
        problem_name = f"Problem: {problem_description[:50]}"
        return self.query.find_solutions_for_problem(problem_name)

    def analyze_file_history(self, file_path: str) -> dict:
        """Analyze the problem/solution history of a file.

        Args:
            file_path: Path to the file

        Returns:
            Dict with file, problems, and solutions
        """
        return self.query.trace_file_impact(file_path)

    def search_knowledge(self, tag: str) -> dict:
        """Search knowledge by tag.

        Args:
            tag: Tag to search for

        Returns:
            Dict with tag, entities, and count
        """
        return self.query.search_by_tag(tag)

# Global instance for easy import
apollo_graph = ApolloGraphAdapter()

# Convenience functions
def record_resolution(error_info: dict):
    """Record error resolution to knowledge graph."""
    apollo_graph.record_error_resolution(error_info)

def find_similar(problem: str):
    """Find similar problems."""
    return apollo_graph.find_similar_problems(problem)

def get_solutions(problem: str):
    """Get solutions for problem."""
    return apollo_graph.get_solutions(problem)

def analyze_file(file_path: str):
    """Analyze file history."""
    return apollo_graph.analyze_file_history(file_path)

def search_by_tag(tag: str):
    """Search by tag."""
    return apollo_graph.search_knowledge(tag)

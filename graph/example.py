"""Example usage of knowledge graph system."""
from graph import get_storage, GraphBuilder, GraphQuery

def main():
    # Initialize
    storage = get_storage()
    builder = GraphBuilder(storage)
    query = GraphQuery(storage)

    # Example 1: Build from resolution
    print("=== Example 1: Building from Resolution ===")
    resolution = {
        'problem': 'TypeScript type error in agent orchestrator',
        'solution': 'Add interface definition for Agent type',
        'files': ['src/agent-orchestrator.ts', 'src/types.ts'],
        'tags': ['typescript', 'types', 'agent'],
        'severity': 'medium',
        'category': 'bug',
        'effectiveness': 0.95
    }
    builder.build_from_resolution(resolution)
    print("[OK] Resolution added to graph")

    # Example 2: Add another related problem
    print("\n=== Example 2: Adding Related Problem ===")
    resolution2 = {
        'problem': 'TypeScript generic type inference failure',
        'solution': 'Explicitly specify generic type parameters',
        'files': ['src/agent-orchestrator.ts'],
        'tags': ['typescript', 'types', 'generics'],
        'severity': 'low',
        'category': 'bug',
        'effectiveness': 0.90
    }
    builder.build_from_resolution(resolution2)
    print("[OK] Second resolution added")

    # Example 3: Query related problems
    print("\n=== Example 3: Finding Related Problems ===")
    related = query.find_related_problems('Problem: TypeScript type error in agent orchestrator')
    print(f"Found {len(related)} related problem(s):")
    for p in related:
        print(f"  - {p.name}")

    # Example 4: Find solutions
    print("\n=== Example 4: Finding Solutions ===")
    solutions = query.find_solutions_for_problem('Problem: TypeScript type error in agent orchestrator')
    print(f"Found {len(solutions)} solution(s):")
    for s in solutions:
        print(f"  - {s.name}")
        print(f"    Effectiveness: {s.properties.get('effectiveness', 'N/A')}")

    # Example 5: Trace file impact
    print("\n=== Example 5: Tracing File Impact ===")
    impact = query.trace_file_impact('src/agent-orchestrator.ts')
    print(f"File: {impact['file'].name if impact['file'] else 'Not found'}")
    print(f"Problems: {len(impact['problems'])}")
    print(f"Solutions: {len(impact['solutions'])}")
    for p in impact['problems']:
        print(f"  Problem: {p.name}")
    for s in impact['solutions']:
        print(f"  Solution: {s.name}")

    # Example 6: Search by tag
    print("\n=== Example 6: Searching by Tag ===")
    results = query.search_by_tag('typescript')
    print(f"Tag: {results['tag']}")
    print(f"Found {results['count']} entities:")
    for e in results['entities']:
        print(f"  - [{e.type}] {e.name}")

    print("\n[OK] All examples completed successfully!")
    print(f"\nData stored in: graph/data/")

if __name__ == '__main__':
    main()

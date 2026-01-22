"""Example of integrating knowledge graph with Apollo system workflows."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from graph.apollo_integration import record_resolution, find_similar, get_solutions, analyze_file

def example_error_handling_workflow():
    """Example: Integrate with error handling."""
    print("=== Error Handling Workflow ===\n")

    # Simulate error occurrence
    error = {
        'problem': 'Agent orchestrator fails with undefined property',
        'solution': 'Add null checks and type guards',
        'files': ['src/orchestrator.ts', 'src/types.ts'],
        'tags': ['typescript', 'null-safety', 'agent'],
        'severity': 'high',
        'category': 'bug',
        'effectiveness': 0.92
    }

    print("1. Error occurred - recording to knowledge graph...")
    record_resolution(error)
    print("   [OK] Error recorded\n")

    # Check for similar past issues
    print("2. Checking for similar past issues...")
    similar = find_similar(error['problem'])
    if similar:
        print(f"   Found {len(similar)} similar issue(s):")
        for issue in similar[:3]:  # Show top 3
            print(f"   - {issue.name}")
    else:
        print("   No similar issues found (this is new)")
    print()

def example_proactive_learning():
    """Example: Learn from past solutions."""
    print("=== Proactive Learning Workflow ===\n")

    # New problem occurs
    new_problem = "TypeScript compilation error with generics"
    print(f"New problem: {new_problem}\n")

    # Search for solutions
    print("Searching knowledge graph for solutions...")
    solutions = get_solutions(new_problem)

    if solutions:
        print(f"Found {len(solutions)} solution(s) from past experience:")
        for sol in solutions:
            effectiveness = sol.properties.get('effectiveness', 'N/A')
            print(f"  - {sol.name}")
            print(f"    Effectiveness: {effectiveness}")
    else:
        print("No past solutions found - this is a new problem type")
    print()

def example_file_impact_analysis():
    """Example: Analyze file before modifying."""
    print("=== File Impact Analysis Workflow ===\n")

    file_to_modify = "src/orchestrator.ts"
    print(f"Planning to modify: {file_to_modify}\n")

    print("Analyzing file history...")
    impact = analyze_file(file_to_modify)

    if impact['file']:
        print(f"File: {impact['file'].name}")
        print(f"Historical problems: {len(impact['problems'])}")
        print(f"Past solutions applied: {len(impact['solutions'])}")

        if impact['problems']:
            print("\nPast problems in this file:")
            for prob in impact['problems'][:3]:
                print(f"  - {prob.name}")
                print(f"    Severity: {prob.properties.get('severity', 'unknown')}")

        if impact['solutions']:
            print("\nPast solutions applied:")
            for sol in impact['solutions'][:3]:
                print(f"  - {sol.name}")
    else:
        print("No history found for this file")
    print()

def example_agent_performance_tracking():
    """Example: Track and query agent performance."""
    print("=== Agent Performance Tracking ===\n")

    # Record agent execution
    agent_execution = {
        'problem': 'Code review task completed',
        'solution': 'Used code-reviewer agent with parallel strategy',
        'files': ['src/app.ts', 'src/utils.ts'],
        'tags': ['agent', 'code-review', 'performance'],
        'severity': 'low',
        'category': 'task',
        'effectiveness': 0.88
    }

    print("Recording agent execution...")
    record_resolution(agent_execution)
    print("[OK] Execution recorded\n")

    # Query agent-related knowledge
    print("Querying agent performance data...")
    from graph.apollo_integration import search_by_tag
    results = search_by_tag('agent')

    print(f"Found {results['count']} agent-related entries:")
    for entity in results['entities'][:5]:
        print(f"  - [{entity.type}] {entity.name}")
    print()

def main():
    """Run all integration examples."""
    print("=" * 60)
    print("Apollo System - Knowledge Graph Integration Examples")
    print("=" * 60)
    print()

    example_error_handling_workflow()
    example_proactive_learning()
    example_file_impact_analysis()
    example_agent_performance_tracking()

    print("=" * 60)
    print("All integration examples completed!")
    print("=" * 60)

if __name__ == '__main__':
    main()

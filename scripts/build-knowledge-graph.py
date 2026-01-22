#!/usr/bin/env python3
"""Build knowledge graph from context archives"""
import json
import sys
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

CONTEXT_DIR = Path(".claude/context")
RESOLUTIONS_DIR = CONTEXT_DIR / "resolutions"
GRAPH_FILE = CONTEXT_DIR / "knowledge-graph.json"

def build_knowledge_graph():
    """Build knowledge graph from resolutions"""
    if not RESOLUTIONS_DIR.exists():
        print("No resolutions found")
        return

    nodes = []
    edges = []
    node_ids = set()

    # Process each resolution
    for ndjson_file in sorted(RESOLUTIONS_DIR.glob("*.ndjson")):
        with open(ndjson_file, encoding="utf-8") as f:
            for line in f:
                res = json.loads(line.strip())
                res_id = res.get("id")

                # Add resolution node
                if res_id not in node_ids:
                    nodes.append({
                        "id": res_id,
                        "type": "resolution",
                        "label": res.get("problem_signature", "Unknown"),
                        "tags": res.get("tags", [])
                    })
                    node_ids.add(res_id)

                # Add file nodes and edges
                for artifact in res.get("artifacts_touched", []):
                    file_id = f"file:{artifact}"
                    if file_id not in node_ids:
                        nodes.append({
                            "id": file_id,
                            "type": "file",
                            "label": artifact
                        })
                        node_ids.add(file_id)

                    edges.append({
                        "from": res_id,
                        "to": file_id,
                        "type": "touches"
                    })

    graph = {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "resolution_count": sum(1 for n in nodes if n["type"] == "resolution"),
            "file_count": sum(1 for n in nodes if n["type"] == "file")
        }
    }

    # Save graph
    CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
    with open(GRAPH_FILE, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)

    print(f"✅ Knowledge graph built: {GRAPH_FILE}")
    print(f"   Nodes: {graph['metadata']['node_count']}")
    print(f"   Edges: {graph['metadata']['edge_count']}")
    print(f"   Resolutions: {graph['metadata']['resolution_count']}")
    print(f"   Files: {graph['metadata']['file_count']}")

if __name__ == "__main__":
    print("🔨 Building knowledge graph...")
    build_knowledge_graph()

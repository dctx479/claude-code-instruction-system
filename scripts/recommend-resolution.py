#!/usr/bin/env python3
"""Recommend relevant resolutions based on problem description"""
import json
import sys
from pathlib import Path
from collections import Counter

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

CONTEXT_DIR = Path(".claude/context")
RESOLUTIONS_DIR = CONTEXT_DIR / "resolutions"

def jaccard_similarity(a, b):
    """Calculate Jaccard similarity between two sets"""
    set_a = set(a.lower().split())
    set_b = set(b.lower().split())
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0

def recommend_resolutions(query, top_k=5):
    """Recommend resolutions based on query"""
    if not RESOLUTIONS_DIR.exists():
        print("No resolutions found")
        return []

    # Collect all resolutions
    resolutions = []
    for ndjson_file in sorted(RESOLUTIONS_DIR.glob("*.ndjson"), reverse=True):
        with open(ndjson_file, encoding="utf-8") as f:
            for line in f:
                res = json.loads(line.strip())
                resolutions.append(res)

    # Calculate similarity scores
    scored = []
    for res in resolutions:
        # Combine searchable fields
        text = f"{res.get('problem_signature', '')} {res.get('problem', '')} {' '.join(res.get('tags', []))}"
        score = jaccard_similarity(query, text)
        scored.append((score, res))

    # Sort by score and return top K
    scored.sort(reverse=True, key=lambda x: x[0])
    return [(score, res) for score, res in scored[:top_k] if score > 0]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python recommend-resolution.py <query>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"🔍 Searching for: {query}\n")

    results = recommend_resolutions(query)

    if not results:
        print("No matching resolutions found")
        sys.exit(0)

    print(f"📋 Found {len(results)} relevant resolutions:\n")
    for i, (score, res) in enumerate(results, 1):
        print(f"{i}. [{res.get('id')}] {res.get('problem_signature', 'Unknown')}")
        print(f"   Similarity: {score:.2%}")
        print(f"   Summary: {res.get('problem', 'N/A')[:80]}...")
        print()

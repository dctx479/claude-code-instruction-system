"""Recommendation engine for context resolutions"""
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import Counter
import math

CONTEXT_DIR = Path(".claude/context")

def jaccard_similarity(a: List[str], b: List[str]) -> float:
    """Calculate Jaccard similarity"""
    if not a or not b:
        return 0.0
    set_a, set_b = set(a), set(b)
    return len(set_a & set_b) / len(set_a | set_b)

def text_similarity(text1: str, text2: str) -> float:
    """Simple word overlap similarity"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    return len(words1 & words2) / len(words1 | words2)

def calculate_similarity(current: Dict[str, Any], candidate: Dict[str, Any]) -> float:
    """Calculate overall similarity score"""
    text_sim = text_similarity(
        current.get('problem', ''),
        candidate.get('problem', '')
    )

    tag_sim = jaccard_similarity(
        current.get('tags', []),
        candidate.get('tags', [])
    )

    file_sim = jaccard_similarity(
        current.get('files', []),
        candidate.get('artifacts_touched', [])
    )

    return text_sim * 0.4 + tag_sim * 0.3 + file_sim * 0.3

def recency_score(date_str: str) -> float:
    """Calculate recency score with 30-day half-life"""
    try:
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        days = (datetime.now() - date).days
        return math.exp(-days / 30)
    except:
        return 0.5

def recommend(problem: Dict[str, Any], top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
    """Recommend similar resolutions"""
    candidates = []
    res_dir = CONTEXT_DIR / "resolutions"

    if not res_dir.exists():
        return []

    for ndjson_file in res_dir.glob("*.ndjson"):
        with open(ndjson_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    res = json.loads(line)
                    sim = calculate_similarity(problem, res)
                    rec = recency_score(res.get('evidence', {}).get('when', ''))
                    score = sim * 0.7 + rec * 0.3
                    candidates.append((res, score))

    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[:top_k]

if __name__ == "__main__":
    from datetime import datetime
    test_problem = {
        'problem': 'Docker connection timeout',
        'tags': ['docker', 'network'],
        'files': ['docker-compose.yml']
    }

    results = recommend(test_problem)
    print(f"Found {len(results)} recommendations")
    for res, score in results:
        print(f"  {res['id']}: {score:.2f}")

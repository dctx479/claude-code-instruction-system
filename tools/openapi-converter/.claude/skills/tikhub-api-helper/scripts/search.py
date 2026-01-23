"""
TikHub API Helper 端点搜索工具

自动生成于: 2026-01-23 14:42:45
"""

import json
from typing import List, Dict, Any
from pathlib import Path


class EndpointSearcher:
    """端点搜索工具"""

    def __init__(self, index_dir: str = "index"):
        self.index_dir = Path(__file__).parent.parent / index_dir
        self.keywords_index = self._load_keywords_index()
        self.endpoints_metadata = self._load_endpoints_metadata()

    def _load_keywords_index(self) -> Dict[str, List[str]]:
        """加载关键词索引"""
        index_file = self.index_dir / "keywords.json"
        if index_file.exists():
            with open(index_file, encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _load_endpoints_metadata(self) -> List[Dict[str, Any]]:
        """加载端点元数据"""
        metadata_file = self.index_dir / "endpoints.json"
        if metadata_file.exists():
            with open(metadata_file, encoding='utf-8') as f:
                return json.load(f)
        return []

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        搜索相关端点

        Args:
            query: 搜索查询
            limit: 返回结果数量

        Returns:
            匹配的端点列表
        """
        # 提取查询关键词
        keywords = self._extract_keywords(query.lower())

        # 搜索匹配的端点
        results = []
        for endpoint in self.endpoints_metadata:
            score = self._calculate_score(endpoint, keywords)
            if score > 0:
                results.append({
                    **endpoint,
                    "score": score
                })

        # 按相关性排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def _extract_keywords(self, query: str) -> List[str]:
        """提取查询关键词"""
        # 简单的分词
        return [word for word in query.split() if len(word) > 2]

    def _calculate_score(self, endpoint: Dict[str, Any], keywords: List[str]) -> float:
        """计算端点与查询的相关性分数"""
        score = 0.0
        text = f"{endpoint.get('path', '')} {endpoint.get('summary', '')} {endpoint.get('description', '')}".lower()

        for keyword in keywords:
            if keyword in text:
                score += 1.0

        return score


# 使用示例
if __name__ == "__main__":
    searcher = EndpointSearcher()
    results = searcher.search("get user information")
    for result in results:
        print(f"{result['method']} {result['path']} - {result['summary']}")

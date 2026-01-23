# OpenAPI → Skill 转换工具

> **设计理念**: 自动将 OpenAPI 规范转换为 Claude Code Skill，支持大规模 API（400+ 端点）

## 命令概览

`/convert-openapi` 命令自动将 OpenAPI 规范（JSON/YAML）转换为标准的 Claude Code Skill。

## 使用方法

### 基本用法
```bash
/convert-openapi <openapi-file> --name "Skill Name"
```

**示例**:
```bash
/convert-openapi tikhub-openapi.json --name "TikHub API Helper"
```

### 高级选项
```bash
/convert-openapi <openapi-file> \
  --name "Skill Name" \
  --output .claude/skills/my-api \
  --core-endpoints 20 \
  --search-method semantic
```

**参数说明**:
- `--name`: Skill 名称（必需）
- `--output`: 输出目录（默认：`.claude/skills/<skill-name>`）
- `--core-endpoints`: 核心端点数量（默认：20）
- `--search-method`: 搜索方法（`keyword` | `semantic` | `hybrid`，默认：`hybrid`）

---

## 转换流程

```
OpenAPI 规范 (openapi.json)
    ↓
1. 解析和验证
    ├─ 提取 API 元数据
    ├─ 解析端点定义
    └─ 识别认证方式
    ↓
2. 核心端点提取
    ├─ 分析端点重要性
    ├─ 提取 Top N 核心端点
    └─ 生成端点摘要
    ↓
3. 生成 Skill 文件
    ├─ SKILL.md (轻量级，~500 行)
    ├─ REFERENCE.md (完整文档)
    ├─ api_client.py (API 客户端)
    └─ search.py (端点搜索工具)
    ↓
4. 生成搜索索引
    ├─ 关键词索引
    ├─ 语义向量索引（可选）
    └─ 端点元数据
    ↓
输出: .claude/skills/my-api/
```

---

## 生成的文件结构

```
.claude/skills/my-api/
├── SKILL.md                 # 核心 Skill 文件（轻量级）
├── REFERENCE.md             # 完整 API 文档
├── openapi.json             # 原始 OpenAPI 规范
├── scripts/
│   ├── api_client.py       # API 客户端
│   ├── search.py           # 端点搜索工具
│   └── __init__.py
├── index/
│   ├── keywords.json       # 关键词索引
│   ├── endpoints.json      # 端点元数据
│   └── embeddings.npy      # 语义向量（可选）
└── examples/
    └── usage.md            # 使用示例
```

---

## SKILL.md 模板

```markdown
---
name: my-api-helper
description: My API 集成，支持 400+ 端点，提供数据查询和分析功能
version: 1.0.0
license: MIT
metadata:
  category: api-integration
  tags: [api, data, integration]
  api_base_url: https://api.example.com
  auth_type: bearer
---

# My API Helper Skill

## 概述
My API 提供 400+ 端点，用于数据查询和分析。

## 核心端点（Top 20）
1. **获取用户信息**: GET /api/v1/users/{id}
2. **搜索数据**: GET /api/v1/search
3. **创建资源**: POST /api/v1/resources
...

## 使用方法
当用户请求 My API 数据时：
1. 使用 `search.py` 搜索相关端点
2. 调用 `api_client.py` 执行请求
3. 返回格式化结果

## 认证
需要 API Key，存储在环境变量 `MY_API_KEY`

详细文档见 REFERENCE.md
```

---

## api_client.py 模板

```python
import os
import requests
from typing import Dict, Any, Optional

class APIClient:
    """My API 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('MY_API_KEY')
        self.base_url = "https://api.example.com"
        self.session = requests.Session()

        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}"
            })

    def call(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        调用 API 端点

        Args:
            endpoint: API 端点路径（如 "/api/v1/users"）
            method: HTTP 方法（GET/POST/PUT/DELETE）
            params: 查询参数
            data: 请求体数据

        Returns:
            API 响应（JSON）
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None)
            }

# 使用示例
if __name__ == "__main__":
    client = APIClient()
    result = client.call("/api/v1/users/123")
    print(result)
```

---

## search.py 模板

```python
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
            with open(index_file) as f:
                return json.load(f)
        return {}

    def _load_endpoints_metadata(self) -> List[Dict[str, Any]]:
        """加载端点元数据"""
        metadata_file = self.index_dir / "endpoints.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
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
        # 简单的分词（实际应用中可以使用更复杂的 NLP 方法）
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
```

---

## 搜索方法对比

### 方法 1：关键词搜索（默认）

**优点**:
- 快速（<1ms）
- 简单易实现
- 无需额外依赖

**缺点**:
- 准确率中等
- 无法理解语义

**适用场景**:
- 小型 API（<100 端点）
- 明确的关键词查询

### 方法 2：语义搜索

**优点**:
- 准确率高
- 理解语义
- 支持模糊查询

**缺点**:
- 需要 embedding 模型
- 索引生成慢
- 依赖 numpy/torch

**适用场景**:
- 大型 API（>100 端点）
- 复杂查询

### 方法 3：混合搜索（推荐）

**策略**:
```
用户查询
    ↓
关键词快速匹配
    ↓
找到结果? ─YES→ 返回
    NO↓
语义搜索
    ↓
返回 Top K
```

**优点**:
- 平衡速度和准确率
- 覆盖长尾查询

---

## 核心端点提取算法

```python
def extract_core_endpoints(openapi_spec: Dict, limit: int = 20) -> List[Dict]:
    """
    提取核心端点

    评分标准:
    1. 端点重要性（基于 HTTP 方法）
       - GET: 1.0
       - POST: 1.2
       - PUT/PATCH: 0.8
       - DELETE: 0.6
    2. 文档完整性
       - 有 summary: +0.5
       - 有 description: +0.3
       - 有 examples: +0.2
    3. 参数复杂度
       - 无参数: 1.0
       - 简单参数: 0.9
       - 复杂参数: 0.7
    """
    endpoints = []

    for path, methods in openapi_spec['paths'].items():
        for method, spec in methods.items():
            score = calculate_endpoint_score(path, method, spec)
            endpoints.append({
                'path': path,
                'method': method.upper(),
                'summary': spec.get('summary', ''),
                'description': spec.get('description', ''),
                'score': score
            })

    # 按分数排序
    endpoints.sort(key=lambda x: x['score'], reverse=True)
    return endpoints[:limit]
```

---

## 使用示例

### 示例 1：TikHub API

```bash
/convert-openapi tikhub-openapi.json --name "TikHub API Helper"
```

**生成结果**:
```
✓ 解析 OpenAPI 规范: 400+ 端点
✓ 提取核心端点: 20 个
✓ 生成 SKILL.md: 2.5KB
✓ 生成 api_client.py: 3KB
✓ 生成 search.py: 4KB
✓ 生成关键词索引: 1.2KB

Skill 已生成到: .claude/skills/tikhub-api-helper/
```

**使用**:
```markdown
"获取 TikTok 热门话题"
→ 自动激活 TikHub API Helper Skill
→ 搜索端点: GET /api/v1/trending/topics
→ 调用 API 并返回结果
```

### 示例 2：自定义 API

```bash
/convert-openapi my-api.yaml \
  --name "My Custom API" \
  --output .claude/skills/my-custom-api \
  --core-endpoints 30 \
  --search-method semantic
```

---

## 最佳实践

### 1. OpenAPI 规范质量

✅ **推荐**:
- 完整的 `summary` 和 `description`
- 清晰的参数说明
- 示例请求和响应
- 标准的认证定义

❌ **避免**:
- 缺少 `summary`
- 模糊的端点描述
- 不一致的命名

### 2. 核心端点选择

**策略**:
- 优先选择高频使用的端点
- 覆盖主要功能领域
- 包含典型的 CRUD 操作

### 3. 搜索优化

**关键词索引**:
- 提取端点的关键词
- 建立倒排索引
- 支持模糊匹配

**语义索引**:
- 使用 sentence-transformers
- 生成端点 embeddings
- 支持语义相似度搜索

---

## 故障排查

### OpenAPI 解析失败

**问题**: 无法解析 OpenAPI 文件

**解决方案**:
1. 验证 OpenAPI 格式（JSON/YAML）
2. 检查 OpenAPI 版本（支持 2.0, 3.0, 3.1）
3. 使用在线验证工具检查规范

### 端点搜索不准确

**问题**: 搜索结果不相关

**解决方案**:
1. 改进端点的 `summary` 和 `description`
2. 使用语义搜索方法
3. 调整搜索算法的权重

### Token 消耗过高

**问题**: 生成的 SKILL.md 过大

**解决方案**:
1. 减少核心端点数量（`--core-endpoints 10`）
2. 将详细文档移到 REFERENCE.md
3. 使用更简洁的描述

---

## 相关文档

- **Skills 集成指南**: `.claude/skills/README.md`
- **API 客户端最佳实践**: `docs/api-client-best-practices.md`
- **搜索算法**: `docs/search-algorithms.md`

---

## 更新日志

### 2026-01-23
- 创建 OpenAPI → Skill 转换工具
- 支持关键词和语义搜索
- 生成标准 Skill 文件结构
- 提供核心端点提取算法

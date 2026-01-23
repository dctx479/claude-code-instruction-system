#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAPI to Claude Code Skill Converter

将 OpenAPI 规范自动转换为 Claude Code Skill
"""

import sys
import io
import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class OpenAPIConverter:
    """OpenAPI 转换器"""

    def __init__(self, openapi_file: Path, skill_name: str, output_dir: Optional[Path] = None):
        self.openapi_file = openapi_file
        self.skill_name = skill_name
        self.output_dir = output_dir or Path(f".claude/skills/{self._slugify(skill_name)}")
        self.spec = self._load_openapi()

    def _slugify(self, text: str) -> str:
        """将文本转换为 slug 格式"""
        return text.lower().replace(" ", "-").replace("_", "-")

    def _load_openapi(self) -> Dict[str, Any]:
        """加载 OpenAPI 规范"""
        with open(self.openapi_file, 'r', encoding='utf-8') as f:
            if self.openapi_file.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                return json.load(f)

    def convert(self, core_endpoints: int = 20) -> None:
        """执行转换"""
        print(f"🔄 开始转换 OpenAPI 规范...")
        print(f"   输入文件: {self.openapi_file}")
        print(f"   Skill 名称: {self.skill_name}")
        print(f"   输出目录: {self.output_dir}")

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "scripts").mkdir(exist_ok=True)
        (self.output_dir / "index").mkdir(exist_ok=True)
        (self.output_dir / "examples").mkdir(exist_ok=True)

        # 提取核心端点
        print(f"\n📊 分析 API 端点...")
        endpoints = self._extract_endpoints()
        print(f"   总端点数: {len(endpoints)}")

        core_eps = self._select_core_endpoints(endpoints, core_endpoints)
        print(f"   核心端点: {len(core_eps)}")

        # 生成文件
        print(f"\n📝 生成 Skill 文件...")
        self._generate_skill_md(core_eps)
        print(f"   ✓ SKILL.md")

        self._generate_reference_md(endpoints)
        print(f"   ✓ REFERENCE.md")

        self._generate_api_client()
        print(f"   ✓ scripts/api_client.py")

        self._generate_search_tool(endpoints)
        print(f"   ✓ scripts/search.py")

        self._generate_index(endpoints)
        print(f"   ✓ index/keywords.json")
        print(f"   ✓ index/endpoints.json")

        # 复制原始 OpenAPI 文件
        import shutil
        shutil.copy(self.openapi_file, self.output_dir / "openapi.json")
        print(f"   ✓ openapi.json")

        print(f"\n✅ 转换完成！")
        print(f"   Skill 位置: {self.output_dir}")

    def _extract_endpoints(self) -> List[Dict[str, Any]]:
        """提取所有端点"""
        endpoints = []
        paths = self.spec.get('paths', {})

        for path, methods in paths.items():
            for method, spec in methods.items():
                if method.lower() in ['get', 'post', 'put', 'patch', 'delete']:
                    endpoints.append({
                        'path': path,
                        'method': method.upper(),
                        'summary': spec.get('summary', ''),
                        'description': spec.get('description', ''),
                        'tags': spec.get('tags', []),
                        'parameters': spec.get('parameters', []),
                        'operationId': spec.get('operationId', ''),
                    })

        return endpoints

    def _select_core_endpoints(self, endpoints: List[Dict], limit: int) -> List[Dict]:
        """选择核心端点"""
        # 计算每个端点的重要性分数
        for ep in endpoints:
            score = 0.0

            # HTTP 方法权重
            method_weights = {
                'GET': 1.0,
                'POST': 1.2,
                'PUT': 0.8,
                'PATCH': 0.8,
                'DELETE': 0.6
            }
            score += method_weights.get(ep['method'], 0.5)

            # 文档完整性
            if ep['summary']:
                score += 0.5
            if ep['description']:
                score += 0.3
            if ep['operationId']:
                score += 0.2

            # 参数复杂度（简单的端点更重要）
            param_count = len(ep['parameters'])
            if param_count == 0:
                score += 1.0
            elif param_count <= 3:
                score += 0.7
            else:
                score += 0.4

            ep['score'] = score

        # 按分数排序
        endpoints.sort(key=lambda x: x['score'], reverse=True)
        return endpoints[:limit]

    def _generate_skill_md(self, core_endpoints: List[Dict]) -> None:
        """生成 SKILL.md"""
        info = self.spec.get('info', {})
        servers = self.spec.get('servers', [])
        base_url = servers[0]['url'] if servers else 'https://api.example.com'

        # 识别认证方式
        security_schemes = self.spec.get('components', {}).get('securitySchemes', {})
        auth_type = 'none'
        if security_schemes:
            first_scheme = list(security_schemes.values())[0]
            auth_type = first_scheme.get('type', 'none')

        content = f"""---
name: {self._slugify(self.skill_name)}
description: {info.get('description', self.skill_name)}
version: {info.get('version', '1.0.0')}
license: MIT
metadata:
  category: api-integration
  tags: [api, integration]
  api_base_url: {base_url}
  auth_type: {auth_type}
---

# {self.skill_name}

## 概述
{info.get('description', f'{self.skill_name} API 集成')}

**API 版本**: {info.get('version', '1.0.0')}
**Base URL**: {base_url}

## 核心端点（Top {len(core_endpoints)}）

"""
        for i, ep in enumerate(core_endpoints, 1):
            content += f"{i}. **{ep['summary'] or ep['path']}**: {ep['method']} {ep['path']}\n"

        content += f"""

## 使用方法

当用户请求 {self.skill_name} 数据时：

1. 使用 `scripts/search.py` 搜索相关端点
2. 调用 `scripts/api_client.py` 执行请求
3. 返回格式化结果

### 示例

```python
from scripts.api_client import APIClient
from scripts.search import EndpointSearcher

# 搜索端点
searcher = EndpointSearcher()
results = searcher.search("your query")

# 调用 API
client = APIClient()
response = client.call(results[0]['path'], results[0]['method'])
print(response)
```

## 认证

"""
        if auth_type == 'bearer':
            env_var = f"{self._slugify(self.skill_name).upper().replace('-', '_')}_API_KEY"
            content += f"需要 API Key，存储在环境变量 `{env_var}`\n"
        elif auth_type == 'apiKey':
            content += "需要 API Key，请参考 API 文档配置\n"
        else:
            content += "无需认证\n"

        content += f"""

## 详细文档

完整的 API 文档请参考 `REFERENCE.md`

---

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**工具**: OpenAPI Converter
"""

        (self.output_dir / "SKILL.md").write_text(content, encoding='utf-8')

    def _generate_reference_md(self, endpoints: List[Dict]) -> None:
        """生成 REFERENCE.md"""
        info = self.spec.get('info', {})

        content = f"""# {self.skill_name} - 完整 API 参考

## API 信息

- **版本**: {info.get('version', '1.0.0')}
- **描述**: {info.get('description', '')}
- **联系方式**: {info.get('contact', ).get('email', 'N/A')}

## 所有端点

"""
        # 按 tag 分组
        by_tag = {}
        for ep in endpoints:
            tags = ep['tags'] or ['未分类']
            for tag in tags:
                if tag not in by_tag:
                    by_tag[tag] = []
                by_tag[tag].append(ep)

        for tag, eps in by_tag.items():
            content += f"\n### {tag}\n\n"
            for ep in eps:
                content += f"#### {ep['method']} {ep['path']}\n\n"
                if ep['summary']:
                    content += f"**摘要**: {ep['summary']}\n\n"
                if ep['description']:
                    content += f"**描述**: {ep['description']}\n\n"
                if ep['parameters']:
                    content += "**参数**:\n"
                    for param in ep['parameters']:
                        required = "必需" if param.get('required') else "可选"
                        content += f"- `{param.get('name')}` ({param.get('in')}, {required}): {param.get('description', '')}\n"
                    content += "\n"
                content += "---\n\n"

        (self.output_dir / "REFERENCE.md").write_text(content, encoding='utf-8')

    def _generate_api_client(self) -> None:
        """生成 API 客户端"""
        servers = self.spec.get('servers', [])
        base_url = servers[0]['url'] if servers else 'https://api.example.com'

        env_var = f"{self._slugify(self.skill_name).upper().replace('-', '_')}_API_KEY"

        content = f'''"""
{self.skill_name} API 客户端

自动生成于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import os
import requests
from typing import Dict, Any, Optional


class APIClient:
    """{self.skill_name} API 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('{env_var}')
        self.base_url = "{base_url}"
        self.session = requests.Session()

        if self.api_key:
            self.session.headers.update({{
                "Authorization": f"Bearer {{self.api_key}}"
            }})

    def call(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        调用 API 端点

        Args:
            endpoint: API 端点路径（如 "/api/v1/users"）
            method: HTTP 方法（GET/POST/PUT/DELETE）
            params: 查询参数
            data: 请求体数据
            headers: 额外的请求头

        Returns:
            API 响应（JSON）
        """
        url = f"{{self.base_url}}{{endpoint}}"

        if headers:
            self.session.headers.update(headers)

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
            return {{
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None)
            }}


# 使用示例
if __name__ == "__main__":
    client = APIClient()
    result = client.call("/api/v1/example")
    print(result)
'''

        (self.output_dir / "scripts" / "api_client.py").write_text(content, encoding='utf-8')

    def _generate_search_tool(self, endpoints: List[Dict]) -> None:
        """生成搜索工具"""
        content = f'''"""
{self.skill_name} 端点搜索工具

自动生成于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
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
        return {{}}

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
                results.append({{
                    **endpoint,
                    "score": score
                }})

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
        text = f"{{endpoint.get('path', '')}} {{endpoint.get('summary', '')}} {{endpoint.get('description', '')}}".lower()

        for keyword in keywords:
            if keyword in text:
                score += 1.0

        return score


# 使用示例
if __name__ == "__main__":
    searcher = EndpointSearcher()
    results = searcher.search("get user information")
    for result in results:
        print(f"{{result['method']}} {{result['path']}} - {{result['summary']}}")
'''

        (self.output_dir / "scripts" / "search.py").write_text(content, encoding='utf-8')

        # 创建 __init__.py
        (self.output_dir / "scripts" / "__init__.py").write_text("", encoding='utf-8')

    def _generate_index(self, endpoints: List[Dict]) -> None:
        """生成搜索索引"""
        # 关键词索引
        keywords_index = {}
        for ep in endpoints:
            text = f"{ep['path']} {ep['summary']} {ep['description']}".lower()
            words = [w for w in text.split() if len(w) > 2]

            for word in words:
                if word not in keywords_index:
                    keywords_index[word] = []
                endpoint_id = f"{ep['method']} {ep['path']}"
                if endpoint_id not in keywords_index[word]:
                    keywords_index[word].append(endpoint_id)

        (self.output_dir / "index" / "keywords.json").write_text(
            json.dumps(keywords_index, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

        # 端点元数据
        endpoints_metadata = [
            {
                'path': ep['path'],
                'method': ep['method'],
                'summary': ep['summary'],
                'description': ep['description'],
                'tags': ep['tags']
            }
            for ep in endpoints
        ]

        (self.output_dir / "index" / "endpoints.json").write_text(
            json.dumps(endpoints_metadata, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='将 OpenAPI 规范转换为 Claude Code Skill'
    )
    parser.add_argument(
        'openapi_file',
        type=Path,
        help='OpenAPI 规范文件路径（JSON 或 YAML）'
    )
    parser.add_argument(
        '--name',
        required=True,
        help='Skill 名称'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='输出目录（默认：.claude/skills/<skill-name>）'
    )
    parser.add_argument(
        '--core-endpoints',
        type=int,
        default=20,
        help='核心端点数量（默认：20）'
    )

    args = parser.parse_args()

    # 验证输入文件
    if not args.openapi_file.exists():
        print(f"❌ 错误：文件不存在 {args.openapi_file}")
        return 1

    # 执行转换
    converter = OpenAPIConverter(
        openapi_file=args.openapi_file,
        skill_name=args.name,
        output_dir=args.output
    )

    try:
        converter.convert(core_endpoints=args.core_endpoints)
        return 0
    except Exception as e:
        print(f"❌ 转换失败：{e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

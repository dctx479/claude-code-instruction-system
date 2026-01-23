"""
TikHub API Helper API 客户端

自动生成于: 2026-01-23 14:42:45
"""

import os
import requests
from typing import Dict, Any, Optional


class APIClient:
    """TikHub API Helper API 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('TIKHUB_API_HELPER_API_KEY')
        self.base_url = "https://api.tikhub.io/v1"
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
        url = f"{self.base_url}{endpoint}"

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
            return {
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None)
            }


# 使用示例
if __name__ == "__main__":
    client = APIClient()
    result = client.call("/api/v1/example")
    print(result)

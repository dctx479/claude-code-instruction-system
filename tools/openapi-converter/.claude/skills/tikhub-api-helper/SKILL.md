---
name: tikhub-api-helper
description: TikHub API 提供 TikTok 数据查询和分析功能
version: 1.0.0
license: MIT
metadata:
  category: api-integration
  tags: [api, integration]
  api_base_url: https://api.tikhub.io/v1
  auth_type: http
---

# TikHub API Helper

## 概述
TikHub API 提供 TikTok 数据查询和分析功能

**API 版本**: 1.0.0
**Base URL**: https://api.tikhub.io/v1

## 核心端点（Top 10）

1. **获取热门话题**: GET /trending/topics
2. **获取热门视频**: GET /trending/videos
3. **获取用户信息**: GET /users/{user_id}
4. **获取用户视频列表**: GET /users/{user_id}/videos
5. **获取视频详情**: GET /videos/{video_id}
6. **获取视频评论**: GET /videos/{video_id}/comments
7. **搜索用户**: GET /search/users
8. **搜索视频**: GET /search/videos
9. **获取话题详情**: GET /hashtags/{hashtag_id}
10. **获取话题视频**: GET /hashtags/{hashtag_id}/videos


## 使用方法

当用户请求 TikHub API Helper 数据时：

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

无需认证


## 详细文档

完整的 API 文档请参考 `REFERENCE.md`

---

**生成时间**: 2026-01-23 14:42:45
**工具**: OpenAPI Converter

# TikHub API Helper - 完整 API 参考

## API 信息

- **版本**: 1.0.0
- **描述**: TikHub API 提供 TikTok 数据查询和分析功能
- **联系方式**: api@tikhub.example.com

## 所有端点


### Trending

#### GET /trending/topics

**摘要**: 获取热门话题

**描述**: 获取当前 TikTok 平台的热门话题列表

**参数**:
- `limit` (query, 可选): 返回结果数量
- `region` (query, 可选): 地区代码

---

#### GET /trending/videos

**摘要**: 获取热门视频

**描述**: 获取当前 TikTok 平台的热门视频列表

**参数**:
- `limit` (query, 可选): 返回结果数量

---


### Users

#### GET /users/{user_id}

**摘要**: 获取用户信息

**描述**: 根据用户 ID 获取用户详细信息

**参数**:
- `user_id` (path, 必需): 用户 ID

---

#### GET /users/{user_id}/videos

**摘要**: 获取用户视频列表

**描述**: 获取指定用户发布的视频列表

**参数**:
- `user_id` (path, 必需): 用户 ID
- `limit` (query, 可选): 返回结果数量

---


### Videos

#### GET /videos/{video_id}

**摘要**: 获取视频详情

**描述**: 根据视频 ID 获取视频详细信息

**参数**:
- `video_id` (path, 必需): 视频 ID

---

#### GET /videos/{video_id}/comments

**摘要**: 获取视频评论

**描述**: 获取指定视频的评论列表

**参数**:
- `video_id` (path, 必需): 视频 ID
- `limit` (query, 可选): 返回结果数量

---


### Search

#### GET /search/users

**摘要**: 搜索用户

**描述**: 根据关键词搜索用户

**参数**:
- `q` (query, 必需): 搜索关键词
- `limit` (query, 可选): 返回结果数量

---

#### GET /search/videos

**摘要**: 搜索视频

**描述**: 根据关键词搜索视频

**参数**:
- `q` (query, 必需): 搜索关键词
- `limit` (query, 可选): 返回结果数量

---


### Hashtags

#### GET /hashtags/{hashtag_id}

**摘要**: 获取话题详情

**描述**: 根据话题 ID 获取话题详细信息

**参数**:
- `hashtag_id` (path, 必需): 话题 ID

---

#### GET /hashtags/{hashtag_id}/videos

**摘要**: 获取话题视频

**描述**: 获取指定话题下的视频列表

**参数**:
- `hashtag_id` (path, 必需): 话题 ID
- `limit` (query, 可选): 返回结果数量

---


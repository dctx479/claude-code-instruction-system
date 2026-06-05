# Real-Time Communication System Template

## 系统概览

**典型场景**: 即时通讯（微信、钉钉、Slack）、实时协作（腾讯文档、Figma）、直播弹幕

**核心特征**:
- 低延迟（< 100ms）
- 长连接（WebSocket）
- 在线状态管理
- 消息可靠性（不丢、不重、有序）
- 群聊和单聊

---

## 六灵魂问题典型值

| 维度 | 典型值 | 说明 |
|------|--------|------|
| **规模** | 100 万 - 1000 万在线用户 | 中大型IM平台 |
| **读写比** | 1:1 | 发送和接收消息量相当 |
| **一致性** | 最终一致 | 允许短暂延迟（< 1 秒） |
| **增长** | 爆发式 | 突发群聊、直播场景 |
| **故障代价** | 高 | 1 小时宕机 = 大量客诉 |
| **约束** | 延迟 > 可用性 > 一致性 > 成本 | 卡顿是最大敌人 |

---

## 粗算示例

**假设场景**: 500 万在线用户，每用户每分钟发送 1 条消息

### 存储估算
```
历史消息: 500 万 × 1440 条/天 × 365 天 × 1KB/条 = 2.6TB/年
在线状态: 500 万用户 × 100 字节 = 500MB（内存）
离线消息: 500 万 × 10 条 × 1KB = 5GB（Redis）
```

### QPS 估算
```
消息发送 QPS: 500 万 / 60 = ~83,000 QPS
在线状态更新: 500 万 / 300（5 分钟一次心跳）= ~16,000 QPS
峰值（群聊、直播）: ~200,000 QPS
```

### 瓶颈识别
- **WebSocket 连接**: 单机最大 ~6 万连接（C10K 问题）
- **消息推送**: 100 万人群聊需要广播 100 万次
- **在线状态**: 高频心跳更新

---

## 关键决策分叉

### 决策 1: 实时通信协议

**选项 A: HTTP 长轮询（Long Polling）**
```javascript
async function poll() {
    const response = await fetch('/messages?since=123', {timeout: 30000});
    const messages = await response.json();
    handleMessages(messages);
    poll();  // 递归轮询
}
```
- ✅ 优点: 兼容性好（所有浏览器支持）
- ❌ 缺点: 延迟高（1-3 秒），服务器压力大（频繁请求）
- 📌 适用: 低实时性场景（如通知）

**选项 B: WebSocket**
```javascript
const ws = new WebSocket('wss://chat.example.com');

ws.onopen = () => {
    ws.send(JSON.stringify({type: 'auth', token: '...'}));
};

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    handleMessage(msg);
};
```
- ✅ 优点: 全双工，低延迟（< 50ms），服务器推送
- ❌ 缺点: 需要维护长连接，防火墙/代理可能阻断
- 📌 适用: **推荐方案**（IM、实时协作）

**选项 C: Server-Sent Events (SSE）**
```javascript
const eventSource = new EventSource('/events');
eventSource.onmessage = (event) => {
    handleMessage(JSON.parse(event.data));
};
```
- ✅ 优点: 服务端推送，自动重连
- ❌ 缺点: 单向（服务端 → 客户端），HTTP/1.1 连接数限制
- 📌 适用: 只需服务端推送的场景（如股票行情）

---

### 决策 2: 消息存储

**选项 A: 仅存储离线消息（Redis）**
```python
# 用户上线时拉取离线消息
offline_msgs = redis.lrange(f"offline:{user_id}", 0, -1)
redis.delete(f"offline:{user_id}")
```
- ✅ 优点: 成本低，性能好
- ❌ 缺点: 无法漫游历史消息（换设备看不到）
- 📌 适用: 临时聊天室、弹幕

**选项 B: 存储最近 N 天消息（MySQL + 归档）**
```sql
-- 最近 30 天消息（热数据）
CREATE TABLE messages_hot (
    id BIGINT PRIMARY KEY,
    conversation_id BIGINT,
    sender_id BIGINT,
    content TEXT,
    created_at TIMESTAMP,
    INDEX idx_conversation_time (conversation_id, created_at)
);

-- 30 天前消息（冷数据，归档到 S3）
```
- ✅ 优点: 支持消息漫游，节省成本
- ❌ 缺点: 冷数据读取慢（需要从 S3 加载）
- 📌 适用: **推荐方案**（IM）

**选项 C: 全部持久化（Kafka + MySQL）**
```
1. 消息发送 → Kafka（持久化）
2. 消费者消费 → MySQL（索引查询）
3. 用户拉取历史 → MySQL
```
- ✅ 优点: 不丢消息，可回溯
- ❌ 缺点: 存储成本高
- 📌 适用: 企业 IM（合规要求）

---

### 决策 3: 在线状态管理

**选项 A: 心跳 + 超时检测**
```python
# 客户端每 30 秒发送心跳
redis.setex(f"online:{user_id}", 60, "1")

# 服务端判断在线状态
is_online = redis.exists(f"online:{user_id}")
```
- ✅ 优点: 简单，成本低
- ❌ 缺点: 延迟高（最多 60 秒才知道离线）
- 📌 适用: 低实时性场景

**选项 B: WebSocket 连接状态**
```python
# WebSocket 断开时触发
@websocket.on_disconnect
def on_disconnect(user_id):
    redis.srem("online_users", user_id)
    broadcast_status(user_id, "offline")
```
- ✅ 优点: 实时（< 1 秒感知离线）
- ❌ 缺点: 依赖 WebSocket，可能误判（网络抖动）
- 📌 适用: **推荐方案**（IM）

**选项 C: 混合模式（WebSocket + 心跳）**
```
1. WebSocket 连接 → 标记在线
2. 定期心跳（30 秒）→ 续期
3. WebSocket 断开 → 等待 10 秒 → 标记离线
```
- ✅ 优点: 防误判，准确
- ❌ 缺点: 复杂
- 📌 适用: 高要求场景

---

### 决策 4: 群聊消息推送

**选项 A: 扇出写（Fanout on Write）**
```python
def send_group_message(group_id, sender_id, content):
    members = get_group_members(group_id)
    for member_id in members:
        # 写入每个成员的消息队列
        redis.lpush(f"inbox:{member_id}", message)
```
- ✅ 优点: 读取快（每人只读自己队列）
- ❌ 缺点: 写入慢（100 万人群 = 100 万次写入）
- 📌 适用: 小群聊（< 100 人）

**选项 B: 扇出读（Fanout on Read）**
```python
def get_messages(user_id):
    groups = get_user_groups(user_id)
    messages = []
    for group_id in groups:
        # 读取群消息列表
        messages += redis.lrange(f"group:{group_id}", 0, -1)
    return merge_and_sort(messages)
```
- ✅ 优点: 写入快（只写一次）
- ❌ 缺点: 读取慢（用户在 10 个群 = 10 次查询）
- 📌 适用: **推荐方案**（大群聊，如直播弹幕）

**选项 C: 混合模式**
```
小群（< 500 人）→ 扇出写
大群（> 500 人）→ 扇出读
```
- ✅ 优点: 平衡读写性能
- ❌ 缺点: 逻辑复杂
- 📌 适用: 同时支持小群和大群

---

## 架构图

```
客户端（App/Web）
    ↓
────────────────────────────────────────
│  接入层（长连接）                       │
├─────────────────────────────────────┤
│ WebSocket Gateway（负载均衡）          │
│   ├─ 节点 1（10 万连接）               │
│   ├─ 节点 2（10 万连接）               │
│   └─ 节点 N                           │
│ Connection Manager（连接状态维护）     │
│   └─ Redis（user_id → gateway_node） │
└─────────────────────────────────────┘
    ↓
────────────────────────────────────────
│  业务层                                │
├─────────────────────────────────────┤
│ 消息服务                               │
│   ├─ 单聊路由（点对点）                │
│   ├─ 群聊路由（扇出）                  │
│   └─ 消息持久化（MySQL/Kafka）         │
│                                       │
│ 在线状态服务                           │
│   ├─ 心跳处理                          │
│   └─ 状态广播（Pub/Sub）               │
│                                       │
│ 离线消息服务                           │
│   └─ Redis（临时存储）                 │
└─────────────────────────────────────┘
    ↓
────────────────────────────────────────
│  数据层                                │
├─────────────────────────────────────┤
│ Redis 集群（在线状态、离线消息、连接映射）│
│ MySQL（历史消息、用户关系、群组）       │
│ Kafka（消息队列、事件流）               │
│ S3（消息归档、文件存储）                │
└─────────────────────────────────────┘
```

---

## 数据模型

### 消息表（messages - 分表）
```sql
CREATE TABLE messages_shard_1 (
    id BIGINT PRIMARY KEY,
    conversation_id BIGINT,  -- 单聊: user1_user2, 群聊: group_123
    sender_id BIGINT,
    content TEXT,
    msg_type ENUM('text', 'image', 'file', 'video'),
    created_at TIMESTAMP,
    INDEX idx_conversation_time (conversation_id, created_at)
);
```

### 会话表（conversations）
```sql
CREATE TABLE conversations (
    id BIGINT PRIMARY KEY,
    type ENUM('private', 'group'),
    participant_ids JSON,  -- [user1, user2] 或群成员列表
    last_message_id BIGINT,
    last_message_time TIMESTAMP,
    created_at TIMESTAMP
);
```

### 群组表（groups）
```sql
CREATE TABLE groups (
    id BIGINT PRIMARY KEY,
    name VARCHAR(200),
    owner_id BIGINT,
    member_count INT,
    max_members INT DEFAULT 500,
    created_at TIMESTAMP
);

CREATE TABLE group_members (
    group_id BIGINT,
    user_id BIGINT,
    role ENUM('owner', 'admin', 'member'),
    joined_at TIMESTAMP,
    PRIMARY KEY (group_id, user_id),
    INDEX idx_user (user_id)
);
```

### Redis 数据结构

**在线状态**
```
SET online:{user_id} 1 EX 60
```

**连接映射**（user → gateway node）
```
HSET connections {user_id} "gateway_node_1"
```

**离线消息**
```
LPUSH inbox:{user_id} {message_json}
```

**群消息（扇出读）**
```
LPUSH group:{group_id} {message_json}
EXPIRE group:{group_id} 86400  # 24 小时过期
```

---

## ADR 示例

### ADR-001: 使用 WebSocket 作为实时通信协议

**决策**: 使用 WebSocket 协议，放弃 HTTP 长轮询

**理由**:
- 需要低延迟（< 100ms），长轮询无法满足
- 双向通信（发送和接收消息）
- 浏览器和移动端都支持 WebSocket

**后果**:
- ✅ 优点: 低延迟，服务端推送
- ❌ 缺点: 需要维护长连接，负载均衡复杂

**替代方案**:
- 长轮询（延迟高）
- SSE（单向通信）

---

### ADR-002: 群聊使用混合扇出模式

**决策**: 小群（< 500 人）扇出写，大群（> 500 人）扇出读

**理由**:
- 80% 群聊人数 < 100，扇出写体验好
- 20% 大群（如公司全员群），扇出写成本过高
- 直播弹幕场景（百万人）必须扇出读

**后果**:
- ✅ 优点: 平衡读写性能，覆盖所有场景
- ❌ 缺点: 逻辑复杂，需要群大小阈值判断

**替代方案**:
- 全部扇出写（大群性能差）
- 全部扇出读（小群体验差）

---

## 演进路线图

### MVP（3 个月）
- 单聊（WebSocket + Redis）
- 简单群聊（< 100 人，扇出写）
- 消息只存储 7 天

### V1.1（6 个月）
- 大群聊支持（扇出读）
- 消息持久化（MySQL + Kafka）
- 在线状态实时同步

### V2.0（12 个月）
- 消息漫游（30 天热数据 + S3 冷数据）
- 文件传输（S3 + CDN）
- 消息已读回执

### V3.0（18 个月）
- 音视频通话（WebRTC）
- 端到端加密
- 消息搜索（Elasticsearch）

---

## 风险列表

### 技术风险

1. **WebSocket 连接风暴**
   - 影响: 系统重启后所有用户同时重连
   - 缓解: 客户端随机延迟重连（0-10 秒）

2. **消息乱序**
   - 影响: 群聊消息顺序错误
   - 缓解: 消息携带序列号 + 客户端排序

3. **大群广播风暴**
   - 影响: 100 万人群发消息导致系统崩溃
   - 缓解: 限流（1 条/秒）+ 扇出读

### 业务风险

1. **离线消息堆积**
   - 影响: 用户上线后消息推送慢
   - 缓解: 限制离线消息数量（最多 100 条）

2. **在线状态误判**
   - 影响: 明明在线却显示离线
   - 缓解: 混合模式（WebSocket + 心跳）

3. **消息丢失**
   - 影响: 客户投诉
   - 缓解: 持久化（Kafka） + 客户端重试

---

## 挑战性问题

**反问用户**:
1. 如果网络抖动导致 WebSocket 断开又重连（5 秒内），你怎么避免用户看到"XX 上线了"的通知？
2. 如果 100 万人群里有人发消息，你怎么保证不拖垮系统？
3. 如果用户同时在手机和电脑登录，收到消息后怎么同步"已读"状态？

---

## 参考资料

- 微信技术架构: https://www.infoq.cn/article/the-road-of-the-growth-weixin-background
- WebSocket 最佳实践: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API
- 群聊扩展性: https://discord.com/blog/how-discord-stores-billions-of-messages

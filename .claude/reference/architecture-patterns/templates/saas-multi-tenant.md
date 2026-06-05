# SaaS Multi-Tenant System Template

## 系统概览

**典型场景**: SaaS 多租户平台（Salesforce、Slack、Notion、飞书）

**核心特征**:
- 数据隔离（租户之间完全隔离）
- 弹性伸缩（租户增长不影响性能）
- 计费系统（按租户、按用户、按使用量）
- 自助注册和配置
- 权限管理（租户管理员 + 成员）

---

## 六灵魂问题典型值

| 维度 | 典型值 | 说明 |
|------|--------|------|
| **规模** | 1000 - 10000 租户 | 中型 SaaS 平台 |
| **读写比** | 10:1 | 读多写少 |
| **一致性** | 最终一致 | 可接受短暂延迟 |
| **增长** | 爆发式 | 新租户快速增长 |
| **故障代价** | 高 | 1 小时宕机 = 大量客诉 + SLA 赔偿 |
| **约束** | 隔离性 > 可用性 > 性能 > 成本 | 数据泄露是红线 |

---

## 粗算示例

**假设场景**: 5000 租户，每租户平均 50 用户，每用户日均 100 次操作

### 存储估算
```
用户数据: 5000 × 50 × 2KB/用户 = 500MB
业务数据: 5000 租户 × 100MB/租户 = 500GB
文件存储: 5000 租户 × 5GB/租户 = 25TB
总计: ~25TB（主要是文件）
```

### QPS 估算
```
操作 QPS: (5000 × 50 × 100) / 86400 = ~300 QPS
峰值: ~1500 QPS
单租户峰值: 假设头部租户占 10%，~150 QPS
```

### 瓶颈识别
- **数据隔离**: 共享表需要加 tenant_id 索引，性能随租户增长下降
- **热点租户**: 大租户（如 1000+ 用户）可能占用大量资源
- **计费**: 需要实时统计每租户的使用量

---

## 关键决策分叉

### 决策 1: 数据隔离模式

**选项 A: 共享数据库 + 共享表（Shared Everything）**
```sql
CREATE TABLE documents (
    id BIGINT PRIMARY KEY,
    tenant_id BIGINT,  -- 租户 ID
    title VARCHAR(200),
    content TEXT,
    created_at TIMESTAMP,
    INDEX idx_tenant (tenant_id)
);

-- 查询时必须带 tenant_id
SELECT * FROM documents WHERE tenant_id = 123;
```
- ✅ 优点: 成本最低，资源利用率高
- ❌ 缺点: 租户间相互影响（慢查询拖垮全部），数据泄露风险
- 📌 适用: 小型 SaaS（< 100 租户）

**选项 B: 共享数据库 + 独立表（Shared Database）**
```sql
-- 每个租户一张表
CREATE TABLE documents_tenant_123 (...);
CREATE TABLE documents_tenant_456 (...);
```
- ✅ 优点: 隔离性好，单租户慢查询不影响其他租户
- ❌ 缺点: 表数量爆炸（5000 租户 = 5000+ 表），运维复杂
- 📌 适用: 中等规模（100-1000 租户）

**选项 C: 独立数据库（Isolated Database）**
```
租户 A → database_tenant_123
租户 B → database_tenant_456
```
- ✅ 优点: 完全隔离，安全性最高，支持租户数据导出
- ❌ 缺点: 成本高，资源利用率低，连接数爆炸
- 📌 适用: **推荐方案**（大型 SaaS 或高安全需求）

**选项 D: 混合模式（Hybrid）**
```
小租户（< 100 用户）→ 共享数据库 + 共享表
大租户（> 100 用户）→ 独立数据库
```
- ✅ 优点: 平衡成本和隔离性
- ❌ 缺点: 架构复杂，需要租户路由层
- 📌 适用: 成熟 SaaS 平台

---

### 决策 2: 租户识别方式

**选项 A: 子域名（Subdomain）**
```
租户 A: https://companyA.saas.com
租户 B: https://companyB.saas.com
```
- ✅ 优点: 租户品牌感强，URL 易识别
- ❌ 缺点: 需要通配符证书，DNS 解析延迟
- 📌 适用: **推荐方案**（toB SaaS）

**选项 B: 路径（Path）**
```
租户 A: https://saas.com/companyA/...
租户 B: https://saas.com/companyB/...
```
- ✅ 优点: 简单，无需 DNS
- ❌ 缺点: URL 冗长，品牌感弱
- 📌 适用: 内部工具

**选项 C: Header（API Token）**
```http
GET /api/documents
X-Tenant-ID: 123
Authorization: Bearer <token>
```
- ✅ 优点: 适合 API 场景，灵活
- ❌ 缺点: 客户端需要管理 Tenant ID
- 📌 适用: API 优先的 SaaS

---

### 决策 3: 弹性伸缩策略

**选项 A: 垂直扩展（Scale Up）**
```
单机 MySQL: 8 核 → 16 核 → 32 核
```
- ✅ 优点: 简单，无需改代码
- ❌ 缺点: 上限低（单机最大 ~1000 TPS），成本高
- 📌 适用: 小型 SaaS

**选项 B: 水平扩展 - 按租户分片（Sharding by Tenant）**
```
租户 1-1000 → 数据库 1
租户 1001-2000 → 数据库 2
...
```
- ✅ 优点: 线性扩展，单租户访问不跨库
- ❌ 缺点: 热点租户可能导致分片不均
- 📌 适用: **推荐方案**（中大型 SaaS）

**选项 C: 读写分离 + 缓存**
```
写: 主库
读: 从库 + Redis 缓存
```
- ✅ 优点: 提升读性能，降低主库压力
- ❌ 缺点: 主从延迟，缓存失效策略复杂
- 📌 适用: 读多写少场景

---

### 决策 4: 计费模式

**选项 A: 按租户固定费用（Flat Fee）**
```
基础版: $99/月（50 用户）
专业版: $299/月（200 用户）
企业版: $999/月（无限用户）
```
- ✅ 优点: 简单，可预测收入
- ❌ 缺点: 大客户吃亏，小客户占便宜
- 📌 适用: 标准化产品

**选项 B: 按用户数（Per User）**
```
$10/用户/月
```
- ✅ 优点: 公平，客户易理解
- ❌ 缺点: 需要准确统计活跃用户
- 📌 适用: **推荐方案**（Slack、Notion 模式）

**选项 C: 按使用量（Usage-Based）**
```
API 调用: $0.01/次
存储: $0.1/GB/月
```
- ✅ 优点: 真正的按需付费
- ❌ 缺点: 账单波动大，客户难以预算
- 📌 适用: API 服务（Stripe、Twilio）

---

## 架构图

```
用户端（Web/Mobile）
    ↓
CDN（静态资源）
    ↓
负载均衡（Nginx）
    ↓
API 网关（租户识别、鉴权）
    ↓
────────────────────────────────────────
│  租户路由层                             │
├─────────────────────────────────────┤
│ Tenant Router（根据 tenant_id 路由）   │
│  ├─ 小租户 → 共享数据库                 │
│  └─ 大租户 → 独立数据库                 │
└─────────────────────────────────────┘
    ↓
────────────────────────────────────────
│  应用层（微服务）                       │
├─────────────────────────────────────┤
│ 用户服务 │ 文档服务 │ 协作服务 │ 计费服务 │
│         │         │         │         │
│ Redis   │ S3      │ WebSocket│ MySQL   │
│ (缓存)  │ (文件)  │ (实时)   │ (账单)  │
└─────────────────────────────────────┘
    ↓
────────────────────────────────────────
│  数据层                                │
├─────────────────────────────────────┤
│ MySQL 集群（租户数据 - 分片）           │
│   ├─ Shard 1（租户 1-1000）            │
│   ├─ Shard 2（租户 1001-2000）         │
│   └─ Shard N（大租户独立库）            │
│                                       │
│ Redis 集群（缓存、会话）                │
│ S3（文件存储 - 按租户隔离）             │
│ Kafka（审计日志、计费事件）             │
└─────────────────────────────────────┘
```

---

## 数据模型

### 租户表（tenants）
```sql
CREATE TABLE tenants (
    id BIGINT PRIMARY KEY,
    name VARCHAR(200),
    subdomain VARCHAR(100) UNIQUE,  -- 子域名
    plan ENUM('free', 'basic', 'pro', 'enterprise'),
    max_users INT,  -- 用户数上限
    shard_id INT,  -- 数据分片 ID
    status ENUM('active', 'suspended', 'deleted'),
    created_at TIMESTAMP,
    expired_at TIMESTAMP,
    INDEX idx_subdomain (subdomain)
);
```

### 用户表（users - 共享或分片）
```sql
-- 共享模式
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    tenant_id BIGINT,  -- 必须带租户 ID
    email VARCHAR(200),
    role ENUM('admin', 'member', 'guest'),
    created_at TIMESTAMP,
    INDEX idx_tenant (tenant_id),
    UNIQUE KEY uk_tenant_email (tenant_id, email)  -- 租户内唯一
);
```

### 文档表（documents - 分片）
```sql
CREATE TABLE documents_shard_1 (
    id BIGINT PRIMARY KEY,
    tenant_id BIGINT,
    user_id BIGINT,
    title VARCHAR(200),
    content TEXT,
    file_url VARCHAR(500),  -- S3 路径: s3://bucket/tenant_123/doc_456.pdf
    created_at TIMESTAMP,
    INDEX idx_tenant_user (tenant_id, user_id)
);
```

### 计费表（billing）
```sql
CREATE TABLE billing (
    id BIGINT PRIMARY KEY,
    tenant_id BIGINT,
    billing_period VARCHAR(20),  -- '2026-06'
    user_count INT,  -- 本月活跃用户数
    storage_gb DECIMAL(10,2),  -- 本月存储用量
    api_calls BIGINT,  -- 本月 API 调用次数
    amount DECIMAL(10,2),  -- 应收金额
    status ENUM('pending', 'paid', 'overdue'),
    created_at TIMESTAMP,
    INDEX idx_tenant_period (tenant_id, billing_period)
);
```

---

## ADR 示例

### ADR-001: 混合数据隔离模式

**决策**: 小租户共享数据库，大租户独立数据库

**理由**:
- 80% 租户用户数 < 50，共享模式成本低
- 20% 大租户（> 100 用户）需要性能保障
- 完全独立数据库成本过高（5000 × $100/月 = $50 万/月）

**后果**:
- ✅ 优点: 平衡成本和性能，灵活
- ❌ 缺点: 需要租户路由层，架构复杂

**替代方案**:
- 全部共享（大租户影响小租户）
- 全部独立（成本过高）

---

### ADR-002: 租户识别使用子域名

**决策**: 使用子域名识别租户（https://companyA.saas.com）

**理由**:
- toB 客户重视品牌（自定义域名是卖点）
- 方便前端路由和 Cookie 隔离
- 竞品（Slack、Notion）都用子域名

**后果**:
- ✅ 优点: 品牌感强，客户满意度高
- ❌ 缺点: 需要通配符证书，DNS 管理成本

**替代方案**:
- 路径模式（品牌感弱）
- Header 模式（不适合 Web 应用）

---

## 演进路线图

### MVP（3 个月）
- 单数据库 + 共享表
- 子域名识别
- 固定计费（$99/月）

### V1.1（6 个月）
- 按用户数计费
- 读写分离 + Redis 缓存
- 文件存储迁移到 S3

### V2.0（12 个月）
- 混合数据隔离（小租户共享，大租户独立）
- 租户自助管理后台
- 审计日志（符合 SOC 2）

### V3.0（18 个月）
- 多区域部署（全球化）
- 自定义域名（CNAME）
- SSO 集成（SAML/OAuth）

---

## 风险列表

### 技术风险

1. **数据泄露（跨租户）**
   - 影响: 客户流失，法律风险
   - 缓解: 强制 tenant_id 过滤 + 代码审计 + 渗透测试

2. **大租户拖垮性能**
   - 影响: 其他租户体验差
   - 缓解: 大租户独立数据库 + 资源隔离

3. **数据库连接数耗尽**
   - 影响: 新租户无法注册
   - 缓解: 连接池 + 按需创建数据库

### 业务风险

1. **租户流失**
   - 影响: 收入下降
   - 缓解: 计费灵活（按月/按年）+ 免费试用

2. **计费错误**
   - 影响: 客诉，赔偿
   - 缓解: 自动化计费 + 账单透明化

3. **数据迁移失败**
   - 影响: 租户升级失败（从共享到独立）
   - 缓解: 灰度迁移 + 双写验证

---

## 挑战性问题

**反问用户**:
1. 如果一个租户的慢查询（SELECT * 没 WHERE）拖垮整个数据库，你怎么隔离？
2. 如果租户要求"删除所有数据"（GDPR），你怎么保证彻底删除？
3. 如果大租户要求"专属服务器"（Private Cloud），你的架构能支持吗？

---

## 参考资料

- Salesforce 多租户架构: https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/
- AWS SaaS 最佳实践: https://aws.amazon.com/partners/programs/saas-factory/
- 多租户数据隔离: https://www.mongodb.com/blog/post/building-multi-tenant-applications-with-mongodb

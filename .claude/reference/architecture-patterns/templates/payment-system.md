# Payment System Template

## 系统概览

**典型场景**: 第三方支付平台（支付宝、微信支付、Stripe）或企业内部支付系统

**核心特征**:
- 强一致性（钱不能多也不能少）
- 幂等性（重复请求不能重复扣款）
- 高可用性（99.99% SLA）
- 对账机制（日终对账、实时监控）
- 安全性（防刷、防篡改）

---

## 六灵魂问题典型值

| 维度 | 典型值 | 说明 |
|------|--------|------|
| **规模** | 日交易 100 万 - 1000 万笔 | 中大型支付平台 |
| **读写比** | 1:10 | 写多读少（交易 > 查询） |
| **一致性** | **强一致** | 绝对不能出错 |
| **增长** | 稳定 | 交易量稳定增长 |
| **故障代价** | **极高** | 1 小时宕机 = 数百万损失 + 监管处罚 |
| **约束** | 一致性 > 可用性 > 性能 > 成本 | 准确性第一 |

---

## 粗算示例

**假设场景**: 日交易 500 万笔，平均金额 100 元

### 存储估算
```
交易记录: 500 万 × 365 天 × 2 年 × 2KB/笔 = 7.3TB
对账记录: 500 万 × 365 天 × 2 年 × 1KB/笔 = 3.6TB
日志: 500 万 × 365 天 × 10KB/笔 = 18TB/年
总计: ~30TB（2 年）
```

### QPS 估算
```
交易 QPS: 500 万 / 86400 = ~60 QPS
查询 QPS: 500 万 × 0.1 / 86400 = ~6 QPS
峰值（促销）: ~300 QPS
```

### 瓶颈识别
- **数据库事务**: 强一致性要求，单机 MySQL 最大 ~1000 TPS
- **第三方通道**: 银行接口限流（单通道 ~100 TPS）
- **对账**: 日终对账需要处理海量数据

---

## 关键决策分叉

### 决策 1: 分布式事务方案

**选项 A: 2PC（两阶段提交）**
```
协调者: 准备阶段 → 所有参与者 Prepare
        ↓ (所有返回 OK)
        提交阶段 → 所有参与者 Commit
```
- ✅ 优点: 强一致性，逻辑简单
- ❌ 缺点: 性能差，阻塞，协调者单点故障
- 📌 适用: 小规模（< 10 TPS）

**选项 B: TCC（Try-Confirm-Cancel）**
```sql
-- Try: 预留资源
UPDATE account SET frozen = frozen + 100 WHERE user_id = 123;

-- Confirm: 确认扣款
UPDATE account SET balance = balance - 100, frozen = frozen - 100 WHERE user_id = 123;

-- Cancel: 回滚（如果失败）
UPDATE account SET frozen = frozen - 100 WHERE user_id = 123;
```
- ✅ 优点: 无阻塞，性能好
- ❌ 缺点: 业务侵入性强，需要实现三个接口
- 📌 适用: **推荐方案**（中大型支付）

**选项 C: 本地消息表（最终一致性）**
```
1. 本地事务：扣款 + 写入消息表
2. 定时任务：扫描消息表 → 调用下游服务
3. 下游成功 → 删除消息；失败 → 重试
```
- ✅ 优点: 解耦，高可用
- ❌ 缺点: 最终一致（不适合实时转账）
- 📌 适用: 异步场景（如积分、优惠券）

---

### 决策 2: 幂等性保证

**选项 A: 唯一索引**
```sql
CREATE TABLE transactions (
    id BIGINT PRIMARY KEY,
    order_id VARCHAR(64) UNIQUE,  -- 业务订单号
    user_id BIGINT,
    amount DECIMAL(10,2),
    status ENUM('pending', 'success', 'failed'),
    created_at TIMESTAMP
);

-- 插入时，如果 order_id 重复会报错
INSERT INTO transactions (order_id, ...) VALUES ('order_123', ...);
```
- ✅ 优点: 数据库层面保证，简单可靠
- ❌ 缺点: 依赖数据库，分库分表后需要路由到同一分片
- 📌 适用: **推荐方案**（单库或按订单号分片）

**选项 B: 分布式锁（Redis）**
```python
import redis

client = redis.Redis()

def process_payment(order_id):
    lock_key = f"lock:payment:{order_id}"
    if client.set(lock_key, "1", nx=True, ex=60):  # 60 秒超时
        try:
            # 执行支付逻辑
            ...
        finally:
            client.delete(lock_key)
    else:
        raise Exception("重复请求")
```
- ✅ 优点: 适用于分布式环境
- ❌ 缺点: Redis 单点故障，锁超时需要处理
- 📌 适用: 分库分表且无法保证路由到同一分片

**选项 C: Token 机制（预生成 Token）**
```
1. 用户发起支付前 → 申请 Token（一次性）
2. 用户提交支付 → 携带 Token
3. 服务端验证 Token → 使用后删除
```
- ✅ 优点: 天然防重复，无需存储订单状态
- ❌ 缺点: 需要额外的 Token 服务
- 📌 适用: 高并发场景（防刷单）

---

### 决策 3: 账户余额存储

**选项 A: 数据库行锁（悲观锁）**
```sql
BEGIN TRANSACTION;
SELECT balance FROM accounts WHERE user_id = 123 FOR UPDATE;
UPDATE accounts SET balance = balance - 100 WHERE user_id = 123;
COMMIT;
```
- ✅ 优点: 强一致性，逻辑简单
- ❌ 缺点: 高并发下锁竞争严重
- 📌 适用: 低并发（< 100 TPS）

**选项 B: 乐观锁（版本号）**
```sql
UPDATE accounts 
SET balance = balance - 100, version = version + 1 
WHERE user_id = 123 AND version = 5;

-- 如果 affected_rows = 0，说明版本号已变化（被其他事务修改），需要重试
```
- ✅ 优点: 无锁等待，性能好
- ❌ 缺点: 冲突时需要重试
- 📌 适用: **推荐方案**（中等并发）

**选项 C: 流水账（只增不改）**
```sql
-- 不存储余额，只存储流水
CREATE TABLE transactions (
    id BIGINT PRIMARY KEY,
    user_id BIGINT,
    amount DECIMAL(10,2),  -- 正数为入账，负数为出账
    created_at TIMESTAMP
);

-- 查询余额时实时计算
SELECT SUM(amount) FROM transactions WHERE user_id = 123;
```
- ✅ 优点: 无锁，天然支持对账
- ❌ 缺点: 查询余额慢（需要全表扫描），需要定期归档
- 📌 适用: 对账系统、审计日志

---

### 决策 4: 对账机制

**选项 A: 日终批量对账**
```
1. 每天凌晨 1 点，导出今日所有交易
2. 与银行/第三方对账文件比对
3. 发现差异 → 人工处理
```
- ✅ 优点: 简单，成本低
- ❌ 缺点: 延迟高（T+1），差异发现晚
- 📌 适用: 小型支付系统

**选项 B: 实时对账**
```
1. 每笔交易完成后，立即查询第三方状态
2. 如果状态不一致 → 告警
3. 自动重试或人工介入
```
- ✅ 优点: 及时发现问题
- ❌ 缺点: 第三方接口压力大，成本高
- 📌 适用: **推荐方案**（大型支付平台）

**选项 C: 准实时对账（消息队列）**
```
1. 交易完成 → 发送消息到 Kafka
2. 对账服务消费消息 → 异步查询第三方
3. 差异 → 写入差异表 → 告警
```
- ✅ 优点: 平衡及时性和成本
- ❌ 缺点: 有延迟（秒级到分钟级）
- 📌 适用: 中大型支付系统

---

## 架构图

```
用户端（App/Web）
    ↓
API 网关（鉴权、限流、防刷）
    ↓
────────────────────────────────────────
│  支付流程（同步）                       │
├─────────────────────────────────────┤
│ 1. 订单服务（创建订单）                 │
│ 2. 支付服务（扣款）                    │
│    ├─ 幂等性校验（Redis/唯一索引）      │
│    ├─ 余额扣减（TCC Try）              │
│    └─ 调用支付通道（银行/支付宝/微信）  │
│ 3. 等待支付结果（轮询或回调）           │
│ 4. 更新订单状态（TCC Confirm/Cancel）  │
└─────────────────────────────────────┘
    ↓
────────────────────────────────────────
│  异步流程                               │
├─────────────────────────────────────┤
│ 对账服务（消费 Kafka）                  │
│ ├─ 实时查询第三方状态                   │
│ ├─ 差异检测                            │
│ └─ 告警通知                            │
│                                       │
│ 清算服务（日终批处理）                  │
│ ├─ 导出交易文件                         │
│ ├─ 与银行文件比对                       │
│ └─ 生成对账报告                         │
└─────────────────────────────────────┘
    ↓
────────────────────────────────────────
│  数据层                                │
├─────────────────────────────────────┤
│ MySQL 主从（账户、交易、订单）          │
│ Redis（幂等性锁、分布式锁）             │
│ Kafka（交易事件、对账消息）             │
│ S3（对账文件、审计日志）                │
└─────────────────────────────────────┘
```

---

## 数据模型

### 账户表（accounts）
```sql
CREATE TABLE accounts (
    id BIGINT PRIMARY KEY,
    user_id BIGINT UNIQUE,
    balance DECIMAL(18,2) DEFAULT 0.00,  -- 余额
    frozen DECIMAL(18,2) DEFAULT 0.00,   -- 冻结金额（TCC Try）
    version INT DEFAULT 1,  -- 乐观锁版本号
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_user (user_id)
);
```

### 交易表（transactions - 分库分表）
```sql
CREATE TABLE transactions_0 (
    id BIGINT PRIMARY KEY,
    order_id VARCHAR(64) UNIQUE,  -- 业务订单号（幂等性）
    user_id BIGINT,  -- 分片键
    amount DECIMAL(10,2),
    type ENUM('recharge', 'withdraw', 'transfer', 'refund'),
    status ENUM('pending', 'success', 'failed', 'refunding'),
    channel VARCHAR(50),  -- 'alipay', 'wechat', 'bank'
    third_party_id VARCHAR(100),  -- 第三方交易流水号
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_order (order_id)
);
```

### 对账差异表（reconciliation_diff）
```sql
CREATE TABLE reconciliation_diff (
    id BIGINT PRIMARY KEY,
    transaction_id BIGINT,
    our_status VARCHAR(20),  -- 我方状态
    third_party_status VARCHAR(20),  -- 第三方状态
    our_amount DECIMAL(10,2),
    third_party_amount DECIMAL(10,2),
    diff_type ENUM('status_mismatch', 'amount_mismatch', 'missing_local', 'missing_remote'),
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    resolved_at TIMESTAMP
);
```

---

## ADR 示例

### ADR-001: 分布式事务使用 TCC 模式

**决策**: 支付流程使用 TCC（Try-Confirm-Cancel）模式

**理由**:
- 需要跨多个服务（账户、订单、积分）
- 2PC 性能不足，单点故障风险高
- 最终一致性不满足实时转账需求

**后果**:
- ✅ 优点: 无阻塞，高性能，可用性高
- ❌ 缺点: 业务侵入性强，每个服务需实现 Try/Confirm/Cancel

**替代方案**:
- 2PC（性能差）
- 本地消息表（延迟高）

---

### ADR-002: 幂等性使用唯一索引 + 分布式锁

**决策**: 订单号使用数据库唯一索引，高并发场景额外使用 Redis 分布式锁

**理由**:
- 唯一索引天然防重复，简单可靠
- 分库分表后，订单号作为分片键，可路由到同一分片
- 高并发时，Redis 锁降低数据库压力

**后果**:
- ✅ 优点: 双重保障，既有数据库强一致性，又有 Redis 性能
- ❌ 缺点: 依赖 Redis，需要处理 Redis 故障

**替代方案**:
- 仅唯一索引（高并发时数据库压力大）
- Token 机制（需要额外服务）

---

## 演进路线图

### MVP（3 个月）
- 单体应用 + MySQL
- 支持基本充值、提现
- 行锁保证一致性

### V1.1（6 个月）
- 拆分为微服务（账户、交易、对账）
- 引入 TCC 分布式事务
- 交易表分库分表

### V2.0（12 个月）
- 准实时对账（Kafka + 对账服务）
- 多支付通道（银行、支付宝、微信）
- 自动化差异处理

### V3.0（18 个月）
- 跨境支付（多币种）
- 风控系统（反欺诈、反洗钱）
- 灰度发布（金丝雀部署）

---

## 风险列表

### 技术风险

1. **数据不一致**
   - 影响: 用户余额错误，客诉
   - 缓解: TCC + 对账 + 人工审核

2. **第三方通道故障**
   - 影响: 支付失败
   - 缓解: 多通道备份 + 自动切换

3. **数据库主库宕机**
   - 影响: 写入服务不可用
   - 缓解: 主从自动切换 + 数据同步

### 业务风险

1. **重复扣款**
   - 影响: 用户投诉，赔偿
   - 缓解: 唯一索引 + 分布式锁 + 对账

2. **恶意刷单**
   - 影响: 资金损失
   - 缓解: 风控规则（单用户限额、异常检测）

3. **对账差异无法自动处理**
   - 影响: 人工成本高
   - 缓解: 规则引擎 + 自动重试 + 告警

---

## 挑战性问题

**反问用户**:
1. 如果用户点击两次"支付"按钮（网络延迟），你怎么保证只扣一次钱？
2. 如果银行返回"成功"，但你的系统崩溃了没记录，对账时怎么处理？
3. 如果用户余额 100 元，两个请求同时扣 80 元，你怎么保证不透支？

---

## 参考资料

- 微信支付架构: https://pay.weixin.qq.com/wiki/doc/api/
- TCC 分布式事务: https://github.com/seata/seata
- 金融系统设计: https://awesome-distributed-transactions.readthedocs.io/

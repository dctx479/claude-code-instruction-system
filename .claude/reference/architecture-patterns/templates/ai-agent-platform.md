# AI Agent Platform Template

## 系统概览

**典型场景**: AI Agent 协作平台（类似 AutoGPT、LangChain、Claude Code）

**核心特征**:
- 多 Agent 协同工作
- 长时任务执行（分钟到小时级别）
- 复杂状态管理（任务状态、上下文、记忆）
- 高可靠性要求（不能丢失用户工作）

---

## 六灵魂问题典型值

| 维度 | 典型值 | 说明 |
|------|--------|------|
| **规模** | DAU 10 万 - 100 万 | 中型 SaaS 平台 |
| **读写比** | 1:1 | 大量写入（任务日志、状态更新） |
| **一致性** | 最终一致 | 任务状态可延迟，记忆需强一致 |
| **增长** | 稳定 | 企业客户为主，增长可预测 |
| **故障代价** | 中等 | 1 小时宕机 = 用户体验差，但不致命 |
| **约束** | 可靠性 > 性能 > 成本 | 不能丢失用户任务 |

---

## 粗算示例

**假设场景**: DAU 50 万，每用户日均创建 5 个任务，每任务 10 个步骤

### 存储估算
```
任务数据: 50 万 × 5 × 365 天 × 50KB/任务 = 4.5TB/年
对话历史: 50 万 × 20 条消息/天 × 5KB/消息 × 365 天 = 1.8TB/年
记忆数据: 50 万用户 × 10MB/用户 = 5TB
总计: ~11TB/年
```

### QPS 估算
```
任务创建 QPS: (50 万 × 5) / 86400 = ~30 QPS
状态更新 QPS: (50 万 × 5 × 10) / 86400 = ~300 QPS
峰值: ~1500 QPS
```

### 瓶颈识别
- **存储**: 需要对象存储（S3）+ 数据库分片
- **计算**: Agent 执行需要隔离（容器化）
- **并发**: 需要任务队列 + Worker 池

---

## 关键决策分叉

### 决策 1: Agent 执行隔离

**选项 A: 多线程（共享进程）**
```python
import threading

def run_agent(task_id):
    # Agent 逻辑
    pass

for task in tasks:
    threading.Thread(target=run_agent, args=(task.id,)).start()
```
- ✅ 优点: 简单，资源开销小
- ❌ 缺点: 一个 Agent 崩溃可能影响其他 Agent，安全隔离弱
- 📌 适用: MVP 阶段

**选项 B: 多进程 + 容器（Docker）**
```yaml
# docker-compose.yml
services:
  agent-worker:
    image: agent-runtime:latest
    deploy:
      replicas: 10
    environment:
      - MAX_MEMORY=2GB
      - TIMEOUT=600s
```
- ✅ 优点: 完全隔离，可限制资源，崩溃不互相影响
- ❌ 缺点: 资源开销大，启动慢（秒级）
- 📌 适用: **推荐方案**（生产环境）

**选项 C: Serverless（Lambda/Cloud Run）**
- ✅ 优点: 自动扩缩容，按需付费
- ❌ 缺点: 冷启动慢（5-10 秒），有执行时间限制（15 分钟）
- 📌 适用: 短任务场景（如单次 API 调用）

---

### 决策 2: 任务状态管理

**选项 A: 数据库轮询**
```python
while True:
    task = db.query("SELECT * FROM tasks WHERE status = 'pending' LIMIT 1")
    if task:
        execute_task(task)
    time.sleep(1)
```
- ✅ 优点: 简单，易于调试
- ❌ 缺点: 数据库压力大，延迟高（秒级）
- 📌 适用: 小规模（< 1000 任务/天）

**选项 B: 消息队列（RabbitMQ/Redis Queue）**
```python
# Producer
queue.push('tasks', task_id)

# Consumer
while True:
    task_id = queue.pop('tasks', timeout=5)
    execute_task(task_id)
```
- ✅ 优点: 解耦，支持高并发，延迟低（毫秒级）
- ❌ 缺点: 需要维护消息队列，处理失败重试
- 📌 适用: **推荐方案**（中大型）

**选项 C: 事件驱动（Kafka + Stream Processing）**
- ✅ 优点: 支持复杂 DAG 任务流，可回溯
- ❌ 缺点: 复杂度高，学习成本大
- 📌 适用: 超大规模（> 100 万任务/天）

---

### 决策 3: 上下文存储（Memory）

**选项 A: 关系型数据库（PostgreSQL）**
```sql
CREATE TABLE agent_memory (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    session_id VARCHAR(64),
    key VARCHAR(200),
    value JSONB,
    created_at TIMESTAMP
);
```
- ✅ 优点: 事务支持，查询灵活
- ❌ 缺点: JSONB 查询性能差，扩展性有限
- 📌 适用: 小型项目

**选项 B: 文档数据库（MongoDB）**
```javascript
db.memory.insertOne({
    user_id: 12345,
    session_id: "abc123",
    memories: [
        { type: "user_preference", content: "喜欢简洁的代码" },
        { type: "decision", content: "选择 TypeScript 而非 JavaScript" }
    ]
});
```
- ✅ 优点: Schema 灵活，查询性能好
- ❌ 缺点: 无事务，一致性弱
- 📌 适用: **推荐方案**（中大型）

**选项 C: 向量数据库（Pinecone/Weaviate）**
- ✅ 优点: 支持语义搜索（"用户之前说过类似的话吗？"）
- ❌ 缺点: 成本高，查询延迟高（100-500ms）
- 📌 适用: RAG 场景

---

## 架构图

```
用户端（Web/CLI）
    ↓
API 网关（鉴权、限流）
    ↓
────────────────────────────────────────
│  编排层                                │
├─────────────────────────────────────┤
│ Task Manager（任务调度）                │
│     ↓                                 │
│ Message Queue（RabbitMQ）             │
│     ↓                                 │
│ Agent Worker Pool（10+ Workers）      │
│   ├── Worker 1（Docker）              │
│   ├── Worker 2（Docker）              │
│   └── Worker N（Docker）              │
└─────────────────────────────────────┘
    ↓
────────────────────────────────────────
│  服务层                                │
├─────────────────────────────────────┤
│ LLM Service（OpenAI/Anthropic）       │
│ Tool Service（Code Exec/Web Search）  │
│ Memory Service（Read/Write Context）  │
└─────────────────────────────────────┘
    ↓
────────────────────────────────────────
│  数据层                                │
├─────────────────────────────────────┤
│ PostgreSQL（任务、用户、权限）          │
│ MongoDB（记忆、对话历史）               │
│ Redis（缓存、分布式锁、速率限制）        │
│ S3/MinIO（文件、快照）                 │
└─────────────────────────────────────┘
```

---

## 数据模型

### 核心表设计

**任务表（tasks）**
```sql
CREATE TABLE tasks (
    id BIGINT PRIMARY KEY,
    user_id BIGINT,
    agent_type VARCHAR(50),  -- 'architect', 'debugger', etc.
    status VARCHAR(20),  -- 'pending', 'running', 'completed', 'failed'
    input JSONB,  -- 用户输入
    output JSONB,  -- Agent 输出
    steps JSONB,  -- [{step: 1, action: 'read_file', result: '...'}]
    created_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    INDEX idx_user_status (user_id, status)
);
```

**记忆表（memories - MongoDB）**
```javascript
{
    _id: ObjectId("..."),
    user_id: 12345,
    session_id: "abc123",
    type: "user_preference",  // 'user_preference', 'decision', 'feedback'
    content: "喜欢使用 TypeScript",
    metadata: {
        source: "conversation",
        confidence: 0.9,
        created_at: ISODate("2026-06-05T10:00:00Z")
    },
    embedding: [0.1, 0.2, ...]  // 可选，用于语义搜索
}
```

**工具调用日志（tool_calls）**
```sql
CREATE TABLE tool_calls (
    id BIGINT PRIMARY KEY,
    task_id BIGINT,
    tool_name VARCHAR(100),  -- 'bash', 'read', 'write'
    input JSONB,
    output TEXT,
    duration_ms INT,
    success BOOLEAN,
    created_at TIMESTAMP,
    INDEX idx_task (task_id)
);
```

---

## ADR 示例

### ADR-001: Agent 执行使用 Docker 容器隔离

**决策**: 每个 Agent 任务在独立 Docker 容器中运行

**理由**:
- Agent 可能执行不受信任的代码（用户提供的脚本）
- 需要限制资源（CPU、内存、网络）
- 一个 Agent 崩溃不能影响其他 Agent

**后果**:
- ✅ 优点: 完全隔离，安全性高
- ❌ 缺点: 启动开销大（~2 秒），资源消耗高

**替代方案**:
- 多线程（安全性不足）
- Serverless（冷启动慢，执行时间受限）

---

### ADR-002: 记忆存储使用 MongoDB + 向量搜索

**决策**: 结构化记忆用 MongoDB，语义搜索用嵌入向量

**理由**:
- 记忆数据 Schema 不固定（用户偏好、决策、反馈等）
- 需要支持"找到类似的记忆"（语义搜索）
- PostgreSQL JSONB 查询性能不足

**后果**:
- ✅ 优点: Schema 灵活，查询性能好
- ❌ 缺点: 向量搜索延迟高（100-200ms）

**替代方案**:
- PostgreSQL（Schema 固定，不灵活）
- 纯向量数据库（成本高，查询语法受限）

---

## 演进路线图

### MVP（3 个月）
- 单体应用 + PostgreSQL
- 多线程执行 Agent
- 基本的任务状态管理

### V1.1（6 个月）
- 引入消息队列 + Worker 池
- Docker 容器隔离
- MongoDB 存储记忆

### V2.0（12 个月）
- 多 Agent 协作（Hierarchical 模式）
- 向量搜索支持语义记忆
- 任务 DAG 可视化

### V3.0（18 个月）
- Serverless 支持（短任务场景）
- 实时协作（多用户共享 Agent）
- 自动化测试和质量门（QA Agent）

---

## 风险列表

### 技术风险

1. **LLM API 限流**
   - 影响: Agent 无法调用 LLM
   - 缓解: 多供应商备份（OpenAI + Anthropic）+ 降级策略

2. **Docker 容器资源耗尽**
   - 影响: 新任务无法启动
   - 缓解: 监控容器数量 + 自动清理闲置容器

3. **消息队列积压**
   - 影响: 任务延迟
   - 缓解: 动态扩容 Worker + 优先级队列

### 业务风险

1. **Agent 执行恶意代码**
   - 影响: 安全漏洞
   - 缓解: 容器隔离 + 代码审计 + 沙箱环境

2. **任务卡死不结束**
   - 影响: 资源泄漏
   - 缓解: 超时机制 + 心跳检测

3. **记忆数据泄露**
   - 影响: 隐私风险
   - 缓解: 加密存储 + 访问控制

---

## 挑战性问题

**反问用户**:
1. 如果一个 Agent 任务需要运行 2 小时，你的容器能保持这么久吗？
2. 如果用户要求"忘记之前的所有对话"，你怎么清理记忆？
3. 如果两个 Agent 同时修改同一个文件，你怎么处理冲突？

---

## 参考资料

- LangChain 架构: https://python.langchain.com/docs/get_started/introduction
- AutoGPT 设计: https://github.com/Significant-Gravitas/AutoGPT
- Claude Code 工作原理: https://www.anthropic.com/claude/code

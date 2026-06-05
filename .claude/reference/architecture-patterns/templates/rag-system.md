# RAG System Template

## 系统概览

**典型场景**: RAG（Retrieval-Augmented Generation）系统，如企业知识库问答、文档助手、智能客服

**核心特征**:
- 向量检索（语义搜索）
- 大规模文档处理（PDF、Word、Markdown）
- 权限控制（不同用户看到不同内容）
- 混合检索（向量 + 关键词）
- 上下文窗口管理

---

## 六灵魂问题典型值

| 维度 | 典型值 | 说明 |
|------|--------|------|
| **规模** | 10 万 - 1000 万文档 | 企业级知识库 |
| **读写比** | 1000:1 | 查询远多于写入 |
| **一致性** | 最终一致 | 向量索引可以延迟几秒 |
| **增长** | 稳定 | 文档缓慢增长，查询稳定 |
| **故障代价** | 中等 | 1 小时宕机 = 用户体验差，但非致命 |
| **约束** | 准确性 > 速度 > 成本 | 答案错误比慢更糟糕 |

---

## 粗算示例

**假设场景**: 100 万文档，每文档平均 2000 字，DAU 10 万，每用户日均 5 次查询

### 存储估算
```
原始文档: 100 万 × 2000 字 × 2 字节/字 = 4GB
文档 Chunks: 100 万文档 × 5 chunks/文档 × 500 字/chunk × 2 字节 = 5GB
向量数据: 500 万 chunks × 1536 维 × 4 字节/维 = 30GB
元数据（权限、标题等）: 500 万 chunks × 1KB = 5GB
总计: ~44GB（不含原始文件存储）
```

### QPS 估算
```
查询 QPS: (10 万 × 5) / 86400 = ~6 QPS
文档写入 QPS: (100 万 / 365 天) / 86400 = ~0.03 QPS
峰值: ~30 QPS
```

### 瓶颈识别
- **向量检索**: 单机 Faiss 可支撑 1000 万向量（< 100ms）
- **LLM 调用**: OpenAI API 限流是瓶颈（每分钟 3500 tokens）
- **权限过滤**: 需要在向量检索后二次过滤

---

## 关键决策分叉

### 决策 1: 向量数据库选型

**选项 A: 开源本地（Faiss + SQLite）**
```python
import faiss
import sqlite3

# 构建索引
index = faiss.IndexFlatL2(1536)  # OpenAI embedding 维度
index.add(embeddings)  # numpy array

# 检索
D, I = index.search(query_embedding, k=10)  # 返回最近 10 个
```
- ✅ 优点: 免费，低延迟（< 10ms），无网络开销
- ❌ 缺点: 单机内存限制（1000 万向量 ~60GB），无分布式
- 📌 适用: 小型项目（< 1000 万文档）

**选项 B: 云服务（Pinecone/Weaviate）**
```python
import pinecone

pinecone.init(api_key="...")
index = pinecone.Index("my-index")

# 写入
index.upsert(vectors=[("id1", embedding1, {"text": "..."})])

# 检索
results = index.query(query_embedding, top_k=10, filter={"user_id": 123})
```
- ✅ 优点: 托管服务，支持分布式，内置过滤
- ❌ 缺点: 成本高（$70/月起），延迟高（50-200ms），vendor lock-in
- 📌 适用: **推荐方案**（中大型企业）

**选项 C: 自建分布式（Milvus）**
- ✅ 优点: 开源，支持千万级向量，延迟低（20-50ms）
- ❌ 缺点: 运维复杂，需要 K8s 集群
- 📌 适用: 超大规模（> 1 亿文档）

---

### 决策 2: Embedding 生成策略

**选项 A: 实时生成（用户查询时调用 API）**
```python
def search(query: str):
    embedding = openai.Embedding.create(input=query, model="text-embedding-3-small")
    results = index.query(embedding)
    return results
```
- ✅ 优点: 简单，无需存储 query embedding
- ❌ 缺点: 每次查询都调 API（50-100ms），成本高
- 📌 适用: 低频查询（< 100 QPS）

**选项 B: 缓存常见查询**
```python
cache = {}  # Redis

def search(query: str):
    if query in cache:
        embedding = cache[query]
    else:
        embedding = openai.Embedding.create(input=query)
        cache[query] = embedding
    results = index.query(embedding)
    return results
```
- ✅ 优点: 命中率高时节省成本和延迟
- ❌ 缺点: 缓存失效策略复杂
- 📌 适用: **推荐方案**（高频重复查询场景）

**选项 C: 本地模型（sentence-transformers）**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode(query)
```
- ✅ 优点: 零成本，低延迟（5-20ms）
- ❌ 缺点: 精度略低于 OpenAI，需要 GPU
- 📌 适用: 成本敏感场景

---

### 决策 3: 权限控制策略

**选项 A: 后过滤（Post-Filtering）**
```python
# 1. 向量检索（不考虑权限）
results = index.query(embedding, k=100)

# 2. 过滤无权限的结果
filtered = [r for r in results if user_has_permission(user_id, r.doc_id)]

# 3. 返回前 10 个
return filtered[:10]
```
- ✅ 优点: 简单，向量检索不受权限影响
- ❌ 缺点: 可能过滤后不足 10 个结果，需要多次检索
- 📌 适用: 权限过滤比例低（< 10%）

**选项 B: 预过滤（Pre-Filtering）**
```python
# 1. 获取用户有权限的文档 ID
allowed_doc_ids = get_user_permissions(user_id)

# 2. 在向量数据库中过滤
results = index.query(embedding, k=10, filter={"doc_id": {"$in": allowed_doc_ids}})
```
- ✅ 优点: 保证返回足够结果，逻辑清晰
- ❌ 缺点: 依赖向量数据库支持过滤（Pinecone 支持，Faiss 不支持）
- 📌 适用: **推荐方案**（使用云服务时）

**选项 C: 租户隔离（Namespace）**
```python
# 每个租户独立索引
index_tenant_a = pinecone.Index("tenant-a")
index_tenant_b = pinecone.Index("tenant-b")

results = index_tenant_a.query(embedding, k=10)
```
- ✅ 优点: 完全隔离，性能最优
- ❌ 缺点: 成本高（每索引单独计费），管理复杂
- 📌 适用: SaaS 多租户场景

---

### 决策 4: 文档分块（Chunking）策略

**选项 A: 固定长度（500 tokens/chunk）**
```python
def chunk_document(text: str, chunk_size=500):
    tokens = tokenizer.encode(text)
    chunks = [tokens[i:i+chunk_size] for i in range(0, len(tokens), chunk_size)]
    return [tokenizer.decode(c) for c in chunks]
```
- ✅ 优点: 简单，可预测
- ❌ 缺点: 可能切断语义（句子被切断）
- 📌 适用: 通用场景

**选项 B: 语义分块（按段落/章节）**
```python
def chunk_document(text: str):
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    for p in paragraphs:
        if len(current_chunk) + len(p) < 1000:
            current_chunk += p + "\n\n"
        else:
            chunks.append(current_chunk)
            current_chunk = p
    return chunks
```
- ✅ 优点: 保留语义完整性
- ❌ 缺点: chunk 大小不均匀
- 📌 适用: **推荐方案**（长文档、书籍）

**选项 C: 滑动窗口（Overlap）**
```python
def chunk_document(text: str, chunk_size=500, overlap=100):
    tokens = tokenizer.encode(text)
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunks.append(tokens[i:i+chunk_size])
    return [tokenizer.decode(c) for c in chunks]
```
- ✅ 优点: 避免边界信息丢失
- ❌ 缺点: chunk 数量增加（存储和计算成本上升）
- 📌 适用: 高精度场景（如法律文书）

---

## 架构图

```
用户端（Web/API）
    ↓
API 网关（鉴权、限流）
    ↓
────────────────────────────────────────
│  查询流程                               │
├─────────────────────────────────────┤
│ 1. Query Rewrite（查询改写）           │
│ 2. Embedding Service（生成向量）       │
│    ├─ Cache（Redis）                  │
│    └─ OpenAI API / Local Model       │
│ 3. Vector Search（向量检索）           │
│    ├─ Pinecone / Milvus / Faiss      │
│    └─ 返回 Top-K Chunks               │
│ 4. Permission Filter（权限过滤）       │
│ 5. Rerank（重排序，可选）              │
│ 6. LLM Generate（生成答案）            │
│    └─ OpenAI GPT-4 / Claude           │
└─────────────────────────────────────┘
    ↓
────────────────────────────────────────
│  索引构建流程（离线/异步）              │
├─────────────────────────────────────┤
│ 1. Document Loader（文档加载）         │
│    ├─ PDF / Word / Markdown          │
│    └─ OCR（如果需要）                 │
│ 2. Text Extraction（文本提取）         │
│ 3. Chunking（文档分块）                │
│ 4. Embedding Generation（批量）        │
│ 5. Vector Index Update（更新索引）     │
│ 6. Metadata Storage（元数据存储）      │
│    └─ PostgreSQL（文档、权限）         │
└─────────────────────────────────────┘
```

---

## 数据模型

### 文档表（documents）
```sql
CREATE TABLE documents (
    id BIGINT PRIMARY KEY,
    title VARCHAR(500),
    content TEXT,  -- 原始文本（用于展示）
    source VARCHAR(200),  -- 来源（文件路径、URL）
    owner_id BIGINT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_owner (owner_id)
);
```

### 文档块表（chunks）
```sql
CREATE TABLE chunks (
    id BIGINT PRIMARY KEY,
    document_id BIGINT,
    chunk_index INT,  -- 块序号（第几块）
    text TEXT,  -- 块内容
    embedding_id VARCHAR(100),  -- 向量数据库中的 ID
    token_count INT,
    created_at TIMESTAMP,
    INDEX idx_document (document_id),
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
```

### 权限表（permissions）
```sql
CREATE TABLE permissions (
    id BIGINT PRIMARY KEY,
    user_id BIGINT,
    document_id BIGINT,
    permission ENUM('read', 'write', 'admin'),
    granted_at TIMESTAMP,
    INDEX idx_user_doc (user_id, document_id)
);
```

### 向量数据库 Schema（Pinecone）
```python
{
    "id": "chunk_12345",
    "values": [0.1, 0.2, ...],  # 1536 维向量
    "metadata": {
        "document_id": 67890,
        "chunk_index": 2,
        "text": "这是第二个块的内容...",
        "owner_id": 123,
        "created_at": "2026-06-05T10:00:00Z"
    }
}
```

---

## ADR 示例

### ADR-001: 向量数据库选择 Pinecone

**决策**: 使用 Pinecone 作为向量数据库

**理由**:
- 团队无 DevOps 能力，不想运维 Milvus
- 文档量预计 500 万（可控），Pinecone 成本可接受（~$200/月）
- 需要权限过滤功能，Pinecone 原生支持 metadata filter

**后果**:
- ✅ 优点: 托管服务，开箱即用，支持过滤
- ❌ 缺点: Vendor lock-in，延迟略高（100-150ms）

**替代方案**:
- Faiss（成本低但无权限过滤）
- Milvus（性能好但运维复杂）

---

### ADR-002: Chunk 大小选择 500 tokens + 100 overlap

**决策**: 每个 chunk 500 tokens，overlap 100 tokens

**理由**:
- GPT-4 上下文窗口 128K，可以容纳 10+ chunks
- 500 tokens 约 1-2 段文字，语义完整
- Overlap 避免边界信息丢失

**后果**:
- ✅ 优点: 检索精度高，生成答案质量好
- ❌ 缺点: chunk 数量增加 25%（100/500），成本略高

**替代方案**:
- 固定 500 无 overlap（成本低但精度差）
- 按段落分块（大小不均）

---

## 演进路线图

### MVP（3 个月）
- 单租户系统
- 本地 Faiss + SQLite
- 固定 500 tokens 分块
- 基本的文档上传和问答

### V1.1（6 个月）
- 迁移到 Pinecone
- 添加权限控制
- 支持多种文档格式（PDF、Word）

### V2.0（12 个月）
- 混合检索（向量 + BM25）
- Rerank 优化相关性
- 多租户支持

### V3.0（18 个月）
- 本地 embedding 模型（降低成本）
- 实时增量索引更新
- 答案溯源和引用展示

---

## 风险列表

### 技术风险

1. **向量检索精度不足**
   - 影响: 答案不准确
   - 缓解: 混合检索（向量 + 关键词）+ Rerank

2. **LLM 幻觉**
   - 影响: 生成不存在的信息
   - 缓解: 强制引用原文 + 置信度评分

3. **权限绕过**
   - 影响: 用户看到无权限文档
   - 缓解: 双重验证（向量库过滤 + 应用层二次校验）

### 业务风险

1. **文档更新不及时**
   - 影响: 答案过时
   - 缓解: 定时全量重建索引 + 增量更新

2. **成本超预算**
   - 影响: OpenAI API 费用过高
   - 缓解: 缓存 + 本地模型 + 限流

3. **索引构建时间过长**
   - 影响: 新文档无法立即搜索
   - 缓解: 异步队列 + 批量处理

---

## 挑战性问题

**反问用户**:
1. 如果用户查询"公司财务报表"，但他只有 2023 年的权限，你怎么避免他看到 2024 年的数据？
2. 如果一个 10 页的 PDF 被分成 50 个 chunks，用户问"这份文档的主要内容是什么"，你怎么生成答案？
3. 如果两个文档内容几乎一样但权限不同，向量检索会返回哪个？

---

## 参考资料

- LangChain RAG 教程: https://python.langchain.com/docs/use_cases/question_answering/
- Pinecone 最佳实践: https://docs.pinecone.io/docs/choosing-index-type-and-size
- OpenAI Embeddings: https://platform.openai.com/docs/guides/embeddings
- RAG 性能优化: https://www.anthropic.com/research/contextual-retrieval

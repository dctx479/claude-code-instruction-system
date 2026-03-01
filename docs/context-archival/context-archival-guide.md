# 上下文归档系统使用指南

## 概述

上下文归档系统是太一元系统 v3.1 引入的核心记忆机制，旨在解决 Claude Code 长对话中的上下文压缩问题。

### 核心问题

Claude 官方的 `/compact` 命令只是简单摘要，会丢失大量关键细节：
- ❌ 试错过程中的正确路径
- ❌ 环境特定的配置经验
- ❌ 问题的根本原因分析
- ❌ 反模式（不应该做的）

### 解决方案

**结构化沉淀 + 渐进式注入**

```
压缩前自动沉淀 → index/detail 分离存储 → 按需精确检索
```

## 架构设计

### 三层记忆架构

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: 实时记忆 (当前对话)                            │
│  - 完整上下文，所有工具调用                              │
│  - Token 限制: ~200K                                     │
└────────────────────┬────────────────────────────────────┘
                     │ PreCompact Hook 自动触发
                     ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 2: 结构化沉淀 (.claude/context/)                 │
│  - index.json: 项目状态、已验证事实 (~2KB)              │
│  - resolutions/*.ndjson: 问题解决方案详情 (~5-10KB/个)  │
│  - 精准检索，按需加载                                    │
└────────────────────┬────────────────────────────────────┘
                     │ 定期同步
                     ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 3: 长期记忆 (memory/*.md + Graphiti)             │
│  - 最佳实践模式库                                        │
│  - Agent 性能数据                                        │
│  - 知识图谱关系                                          │
└─────────────────────────────────────────────────────────┘
```

### 为什么是三层？

1. **Layer 1 (实时)**: 当前任务的完整上下文，支持复杂推理
2. **Layer 2 (结构化)**: 历史经验的精准索引，避免重复试错
3. **Layer 3 (长期)**: 跨项目的知识沉淀，形成最佳实践

## 核心概念

### index.json - 轻量级索引

**作用**: 快速了解项目状态，判断是否有相关历史

**内容**:
- 项目目标和当前状态
- 已验证事实（非猜测）
- 技术约束和环境信息
- 问题解决方案索引（只有摘要）

**大小**: 通常 <2KB，消耗极少 Token

**示例**:
```json
{
  "context_version": "v3.1",
  "project": "EnglishLearning-compare",
  "current_state": "favorites_feature_complete",
  "goals": [
    "实现句子收藏功能",
    "提供收藏列表页面"
  ],
  "verified_facts": [
    "sentence_favorites 表已创建",
    "UNIQUE(user_id, original_text) 防止重复"
  ],
  "detail_index": {
    "resolutions": [
      {
        "id": "res-001",
        "problem_signature": "Connection terminated due to connection timeout",
        "summary": "使用 docker exec 在容器内执行 SQL",
        "tags": ["docker", "postgresql", "network"]
      }
    ]
  }
}
```

### resolutions/*.ndjson - 详细方案

**作用**: 保存问题解决的完整路径，可复现

**内容**:
- 问题签名（稳定的错误关键词）
- 根本原因分析
- 最终修复步骤（可执行）
- 验证方法
- 反模式（1-3 条不应该做的）

**格式**: NDJSON（每行一个 JSON 对象）

**示例**:
```json
{"id":"res-001","type":"resolution","problem_signature":"Connection terminated due to connection timeout","problem":"Node.js 无法连接 Docker 内 PostgreSQL","root_cause":"localhost 无法路由到容器","final_fix":["docker compose up -d","docker exec -i container psql < schema.sql"],"why_it_works":"容器内执行绕过网络路由","verification":["\\d sentence_favorites 显示表结构"],"anti_patterns":["增加 connectionTimeoutMillis 无效","修改 DATABASE_URL 无效"],"artifacts_touched":["lib/favorites-schema.sql","docker-compose.yml"],"evidence":{"signals":["CREATE TABLE 成功","表结构显示所有字段"],"when":"2026-01-22T14:30:00Z"}}
```

## 使用流程

### 1. 自动沉淀（推荐）

**触发时机**: 上下文即将压缩时

**工作流程**:
```
Claude 检测到 Token 接近上限
    ↓
PreCompact Hook 触发
    ↓
context-archivist Agent 启动
    ↓
分析当前对话，提炼关键信息
    ↓
生成/更新 index.json 和 resolutions/*.ndjson
    ↓
执行 /compact 压缩上下文
```

**优势**: 无需人工干预，自动保存关键信息

### 2. 手动保存

**使用场景**:
- 完成重要功能开发后
- 解决复杂问题后
- 对话即将结束前

**命令**:
```bash
/save-context "完成用户认证功能"
```

**输出**:
```
✓ 上下文归档完成

📋 项目状态: auth_feature_complete
✅ 已验证事实: 3 条
🔧 问题解决方案: 2 个
📁 文件已保存:
  - .claude/context/index.json
  - .claude/context/resolutions/2026-01-22-143052.ndjson
```

### 3. 读取归档

**读取项目状态**:
```bash
/read-context index
```

**读取特定问题解决方案**:
```bash
/read-context resolution res-001
```

**列出所有归档**:
```bash
/read-context list
```

## 渐进式上下文注入

### 核心思想

**不是一次性加载所有历史，而是按需精确检索**

### 工作流程

```
用户: "Docker 连接数据库失败"
    ↓
系统: 读取 index.json (2KB)
    ↓
系统: 搜索 problem_signature，发现 res-001 匹配
    ↓
系统: 读取 res-001 详情 (5KB)
    ↓
回复: "根据历史经验 (res-001)，这个问题通常是网络路由导致，
      建议使用 docker exec 在容器内执行..."
```

### Token 节省

**传统方式** (Full-context):
- 加载所有历史对话: ~50K tokens
- 大量噪音，稀释注意力

**渐进式注入**:
- 加载 index.json: ~500 tokens
- 按需加载 resolution: ~1K tokens
- 总计: ~1.5K tokens (节省 97%)

### 效果对比

根据 EverMemOS 的评测数据：
- Full-context 准确率: 89.7%
- 渐进式注入准确率: 92.3%
- **精准的遗忘和精准的记一样重要**

## 最佳实践

### 何时保存

✅ **应该保存**:
- 多次尝试后才成功的方案（模型知识盲区）
- 环境特定的配置和调试经验
- 复杂问题的根本原因分析
- 功能开发的完整实现路径

❌ **不应该保存**:
- 纯信息查询（如"这个文件是什么"）
- 未完成的尝试（除非作为 anti_pattern）
- 常规操作和标准流程

### 问题签名设计

**好的问题签名**（稳定、可检索）:
- ✅ "Connection terminated due to connection timeout"
- ✅ "EADDRINUSE: address already in use"
- ✅ "Module not found: Can't resolve"

**不好的问题签名**（不稳定、难检索）:
- ❌ "出错了"
- ❌ "Error at line 42"
- ❌ "Something went wrong"

### 反模式记录

**目的**: 避免后续重复试错

**原则**:
- 记录 1-3 条最典型的错误尝试
- 说明为什么无效
- 简洁明了

**示例**:
```json
"anti_patterns": [
  "增加 connectionTimeoutMillis 参数无法解决根本的网络路由问题",
  "修改 DATABASE_URL 为 127.0.0.1 仍然超时",
  "未先确认 Docker 容器是否运行就执行迁移"
]
```

## 集成其他系统

### 与自进化协议集成

```
归档的 resolutions
    ↓
自动同步到 memory/lessons-learned.md
    ↓
形成可复用的经验库
```

### 与 Agent 驾驭集成

```
记录 Agent 编排策略的效果
    ↓
沉淀最优策略选择模式
    ↓
优化未来的编排决策
```

### 与质量保障集成

```
QA 发现的问题和修复方案
    ↓
沉淀到 resolutions
    ↓
避免类似问题再次出现
```

## 故障排查

### 文件不存在

**问题**: 执行 `/read-context` 提示文件不存在

**解决**:
1. 首次使用需先执行 `/save-context`
2. 检查 `.claude/context/` 目录是否存在
3. 确认之前有保存过上下文

### 内容为空

**问题**: index.json 存在但内容为空

**解决**:
1. 确认对话内容足够（>10 轮）
2. 检查是否有实际的问题解决过程
3. 验证 context-archivist Agent 是否正常工作

### ID 不存在

**问题**: 读取 resolution 时提示 ID 不存在

**解决**:
1. 使用 `/read-context list` 查看所有 ID
2. 确认 ID 格式正确（如 res-001）
3. 检查 NDJSON 文件格式是否正确

## 高级用法

### 搜索相关问题

```bash
# 未来功能
/search-context "Docker 连接超时"
```

### 同步到长期记忆

```bash
# 未来功能
/sync-context
```

### 导出归档

```bash
# 未来功能
/export-context --format=markdown
```

## 与 context-retrieval 的对比

| 特性 | context-retrieval | 太一元系统 |
|------|-------------------|-----------|
| 核心理念 | 对话归档 | 三层记忆架构 |
| 文件格式 | index.json + resolutions.ndjson | 相同 + sessions/ |
| 触发方式 | PreCompact Hook | 相同 + 手动触发 |
| 检索方式 | MCP 工具 | 命令 + 自动注入 |
| 集成深度 | 独立插件 | 深度集成自进化/编排/QA |
| 长期记忆 | 无 | 同步到 memory/ + Graphiti |

## 总结

上下文归档系统是太一元系统迈向"认知时代"的关键一步：

1. **精准的记**: 结构化沉淀试错后的正确路径
2. **精准的忘**: 压缩时保留关键信息，丢弃噪音
3. **按需注入**: 渐进式加载，节省 Token
4. **持续进化**: 与自进化协议深度集成

**未来的 AI 不再是阅后即焚的聊天窗口，而是有历史、有偏好、真正懂你的"第二大脑"。**

---

**维护者**: context-archivist Agent
**最后更新**: 2026-01-22

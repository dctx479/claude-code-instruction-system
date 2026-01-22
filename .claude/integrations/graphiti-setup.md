# Graphiti MCP 集成指南

## 概述

Graphiti是一个知识图谱记忆系统，为Apollo系统提供跨会话的持久化知识存储和检索能力。通过MCP (Model Context Protocol) 集成，实现自动知识积累和智能检索。

---

## 安装配置

### 1. 安装Graphiti MCP服务器

在 `~/.claude/mcp_servers.json` 中添加：

```json
{
  "mcpServers": {
    "graphiti": {
      "command": "uvx",
      "args": ["graphiti-mcp"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your-password",
        "OPENAI_API_KEY": "your-openai-key"
      }
    }
  }
}
```

### 2. Neo4j数据库配置

**选项A: Docker快速启动**
```bash
docker run \
  --name neo4j-graphiti \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your-password \
  -v $HOME/neo4j/data:/data \
  neo4j:latest
```

**选项B: Neo4j Desktop**
1. 下载并安装 [Neo4j Desktop](https://neo4j.com/download/)
2. 创建新数据库，设置密码
3. 启动数据库
4. 记录连接信息 (默认: bolt://localhost:7687)

### 3. 环境变量配置

创建 `.env` 文件 (或在系统环境变量中设置):
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
OPENAI_API_KEY=your-openai-key  # 用于生成嵌入向量
```

### 4. 验证安装

启动Claude Desktop后，检查MCP连接:
```bash
# 在Claude中执行
检查Graphiti MCP是否可用
```

预期看到可用的工具:
- `add_entities` - 添加实体
- `add_relations` - 添加关系
- `search` - 语义搜索
- `retrieve_episodes` - 检索历史事件

---

## 核心概念

### 知识图谱结构

```
┌─────────────────────────────────────────────────────┐
│                   Knowledge Graph                    │
│                                                       │
│   [实体] ──────关系──────> [实体]                    │
│     │                         │                       │
│     │                         │                       │
│   属性集                    属性集                    │
│   时间戳                    时间戳                    │
│   来源                      来源                      │
│                                                       │
│   示例:                                               │
│   [Apollo系统] ──使用──> [Agent编排]                 │
│        │                      │                       │
│     version: 2.0          strategy: hierarchical     │
│     created: 2026-01       created: 2026-01          │
└─────────────────────────────────────────────────────┘
```

### 数据模型

**实体 (Entity)**:
- 名称 (name): 实体唯一标识
- 类型 (type): 实体类别
- 属性 (properties): 键值对
- 时间戳 (timestamp): 创建/更新时间
- 嵌入向量 (embedding): 用于语义搜索

**关系 (Relation)**:
- 源实体 (source): 关系起点
- 目标实体 (target): 关系终点
- 关系类型 (type): 关系名称
- 属性 (properties): 关系属性
- 时间戳 (timestamp): 创建时间

**事件 (Episode)**:
- 内容 (content): 事件描述
- 时间戳 (timestamp): 发生时间
- 相关实体 (entities): 关联的实体列表
- 来源 (source): 事件来源

---

## 使用方法

### 1. 存储知识

**添加实体**:
```markdown
存储实体:
- 名称: "Apollo自进化系统"
- 类型: "系统架构"
- 属性: {"version": "2.0", "capabilities": ["自进化", "Agent驾驭", "知识沉淀"]}
```

**添加关系**:
```markdown
创建关系:
- 源: "Apollo系统"
- 关系: "使用技术"
- 目标: "TypeScript"
- 属性: {"用途": "核心实现语言"}
```

**记录事件**:
```markdown
记录事件:
2026-01-16: 完成Graphiti集成，实现知识图谱能力
相关实体: ["Apollo系统", "Graphiti", "知识管理"]
```

### 2. 检索知识

**语义搜索**:
```markdown
搜索: "如何使用Agent编排"
# 返回相关实体、关系和历史事件
```

**精确查询**:
```markdown
查询实体: "Apollo系统"
# 返回该实体的所有属性和关联关系
```

**时序检索**:
```markdown
检索事件: 时间范围 2026-01-01 到 2026-01-16
# 返回该时间段内的所有事件
```

### 3. 更新知识

**更新实体属性**:
```markdown
更新实体 "Apollo系统":
- 添加属性: {"last_updated": "2026-01-16"}
```

**删除过时关系**:
```markdown
删除关系:
- 源: "旧系统"
- 关系: "依赖"
- 目标: "废弃库"
```

---

## 最佳实践

### 1. 知识建模原则

**实体命名规范**:
- 使用描述性名称: `"Apollo自进化系统"` ✓ 优于 `"系统1"` ✗
- 保持一致性: 同一概念使用相同名称
- 避免特殊字符: 使用中文、英文、数字和下划线

**关系设计**:
- 使用动词描述关系: `"使用"`, `"包含"`, `"依赖"`
- 明确方向性: 考虑 A→B 和 B→A 的语义差异
- 添加时间戳: 便于追踪知识演化

**属性设置**:
- 关键信息作为属性: 版本、状态、配置等
- 使用结构化数据: JSON格式便于查询
- 记录元数据: 来源、创建者、置信度

### 2. 知识沉淀策略

**何时存储知识**:
- ✅ 任务完成后: 沉淀解决方案和最佳实践
- ✅ 发现新技术: 记录工具、库、方法
- ✅ 遇到问题: 记录错误模式和修复方案
- ✅ 学到经验: 提炼可复用知识
- ❌ 临时信息: 不存储一次性数据

**知识分类**:
```
├── 项目知识
│   ├── 系统架构
│   ├── 技术栈
│   └── 配置信息
├── 技术知识
│   ├── 编程语言
│   ├── 框架工具
│   └── 设计模式
├── 经验知识
│   ├── 最佳实践
│   ├── 错误模式
│   └── 解决方案
└── 领域知识
    ├── 业务规则
    ├── 专业术语
    └── 行业标准
```

### 3. 检索优化

**提高检索准确率**:
- 使用具体描述而非泛泛查询
- 结合关键词和语义搜索
- 利用时间范围缩小结果
- 通过实体类型过滤

**示例**:
```markdown
❌ 差: "搜索Agent"
✓ 好: "搜索Agent编排策略和最佳实践"

❌ 差: "查询错误"
✓ 好: "查询2026年1月发生的TypeScript类型错误及解决方案"
```

### 4. 知识维护

**定期清理**:
- 删除过时信息
- 合并重复实体
- 更新变化的关系
- 归档历史版本

**质量保证**:
- 验证实体存在性
- 检查关系完整性
- 确认属性准确性
- 审核知识一致性

### 5. 隐私与安全

**敏感信息处理**:
- ❌ 不存储: 密码、API密钥、个人隐私
- ✓ 可存储: 架构设计、技术方案、经验总结
- ⚠️ 脱敏后存储: 错误日志(移除敏感路径)

**访问控制**:
- 本地部署Neo4j，数据不离开本地
- 设置强密码保护数据库
- 定期备份知识图谱

---

## 与Apollo系统集成

### 自动知识沉淀流程

```
任务执行 → 触发沉淀 → 提取知识 → 构建图谱 → 持久化存储
    ↑                                              ↓
    └──────────── 检索增强 ←────────────────────┘
```

### 集成点

1. **自进化协议集成**:
   - 错误发生时 → 自动记录错误模式实体
   - 任务完成时 → 沉淀解决方案和最佳实践
   - 发现改进时 → 更新知识图谱

2. **Agent驾驭集成**:
   - Agent性能数据 → 存储为实体属性
   - 编排策略 → 建立关系网络
   - 任务历史 → 记录为事件序列

3. **记忆引用集成**:
   - `memory/*.md` → 结构化后导入Graphiti
   - Graphiti → 增强现有记忆系统
   - 双向同步 → 保持一致性

### 使用示例

参见: `.claude/examples/graphiti-usage.md`

---

## 故障排除

### 常见问题

**问题1: MCP连接失败**
```
症状: Claude无法识别Graphiti工具
解决:
1. 检查 mcp_servers.json 配置是否正确
2. 验证 uvx 是否安装: pip install uvx
3. 重启Claude Desktop
4. 查看日志: ~/.claude/logs/mcp.log
```

**问题2: Neo4j连接错误**
```
症状: "Failed to connect to Neo4j"
解决:
1. 确认Neo4j正在运行: docker ps 或 Neo4j Desktop
2. 检查连接信息: URI、用户名、密码
3. 测试连接: cypher-shell -a bolt://localhost:7687
4. 检查防火墙: 确保7687端口开放
```

**问题3: 搜索结果为空**
```
症状: 搜索返回无结果
解决:
1. 确认知识已成功存储
2. 检查嵌入向量生成: 验证OPENAI_API_KEY
3. 使用精确查询测试: 查询特定实体名称
4. 查看Neo4j数据: MATCH (n) RETURN n LIMIT 10
```

**问题4: 性能缓慢**
```
症状: 检索速度慢
优化:
1. 创建索引: CREATE INDEX ON :Entity(name)
2. 限制结果数量: 使用 LIMIT 子句
3. 优化查询: 避免全图扫描
4. 增加内存: 调整Neo4j配置
```

---

## 进阶使用

### Cypher查询示例

**查询所有实体类型**:
```cypher
MATCH (n)
RETURN DISTINCT labels(n) AS types, count(n) AS count
ORDER BY count DESC
```

**查询实体关系网络**:
```cypher
MATCH (source)-[r]->(target)
WHERE source.name = "Apollo系统"
RETURN source, r, target
```

**时序分析**:
```cypher
MATCH (n)
WHERE n.timestamp >= datetime("2026-01-01")
RETURN n.name, n.timestamp
ORDER BY n.timestamp DESC
```

### 批量操作

**批量导入**:
```markdown
批量添加实体:
[
  {"name": "实体1", "type": "类型A", "properties": {...}},
  {"name": "实体2", "type": "类型B", "properties": {...}}
]
```

**批量更新**:
```markdown
批量更新属性:
实体类型 "系统架构" 的所有实体添加属性 {"reviewed": true}
```

---

## 参考资源

- Graphiti官方文档: https://github.com/getzep/graphiti
- Neo4j文档: https://neo4j.com/docs/
- MCP协议: https://modelcontextprotocol.io/
- Cypher查询语言: https://neo4j.com/docs/cypher-manual/

---

## 更新日志

- 2026-01-16: 初始版本，集成Graphiti MCP
- 待定: 添加自动备份功能
- 待定: 实现知识图谱可视化

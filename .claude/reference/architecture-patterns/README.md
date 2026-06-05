# 架构模式知识库

> 来源: [awesome-architecture](https://github.com/study8677/awesome-architecture)  
> 用途: 为 architecture-copilot Skill 和 architect Agent 提供实战参考

## 目录结构

```
architecture-patterns/
├── README.md           # 本文件
├── tutorials/          # 26 章架构思维教程（精选）
├── templates/          # 25 个系统架构模板
└── cases/              # 6 个端到端演进案例
```

## 使用方式

### 1. 与 architecture-copilot Skill 协同

在七阶段流程的**阶段 6（关键决策分叉）**时：
- 根据系统类型，加载对应 `templates/` 中的模板
- 模板提供该类型系统的典型决策点和权衡分析

### 2. 与 architect Agent 协同

在架构设计任务中：
- 参考 `tutorials/` 学习架构思维框架
- 参考 `cases/` 了解真实系统的演进路径
- 参考 `templates/` 获取同类系统的设计模式

## 核心理念

**架构不是"灵感画出来的"，而是"约束逼出来的"**

- 没有银弹，只有权衡
- 没有"最佳架构"，只有"最适合当前约束的架构"
- 代码告诉计算机做什么，架构决定是否值得做、能否扛住生产压力

## 内容概览

### Tutorials（教程）

26 章系统化教程，涵盖：
- 架构思维基础框架
- 分布式系统基础
- 数据一致性模式
- 故障弹性工程
- AI 原生架构设计
- Agent 平台与编码系统

### Templates（模板）

25 个真实系统架构，包括：
- 电商系统（高并发秒杀）
- 社交平台（Feed 流 + 实时通信）
- 支付系统（强一致性 + 幂等性）
- 推荐系统（离线训练 + 在线服务）
- AI Agent 平台（多 Agent 协作）
- RAG 系统（向量检索 + 权限控制）
- SaaS 多租户（数据隔离 + 弹性伸缩）

### Cases（案例）

6 个端到端项目演进，展示：
- 从 MVP 到生产的完整路径
- 如何应对突发流量（如抢票系统）
- 如何处理数据增长（如时序数据）
- 如何重构遗留系统（如单体 → 微服务）

## 加载策略

**按需加载，避免 token 浪费**：

1. **初始阶段**: 只读本 README
2. **需要理论指导**: 加载 `tutorials/` 中的相关章节
3. **需要实战参考**: 加载 `templates/` 中的对应模板
4. **需要演进路径**: 加载 `cases/` 中的相关案例

## 内容提取计划

由于原仓库内容庞大（26 章 + 25 模板 + 6 案例），采用**渐进式提取**策略：

### Phase 1: 核心框架（优先）
- [ ] 提取 6 个最常见系统模板（电商、社交、支付、AI Agent、RAG、SaaS）
- [ ] 提取 5 个核心教程章节（架构思维、分布式基础、一致性、弹性、AI 原生）
- [ ] 提取 2 个典型案例（抢票系统、SaaS 演进）

### Phase 2: 扩展覆盖（次优先）
- [ ] 补充剩余 19 个模板
- [ ] 补充剩余 21 章教程
- [ ] 补充剩余 4 个案例

### Phase 3: 持续更新
- [ ] 跟踪原仓库更新
- [ ] 根据使用频率调整内容优先级

## 贡献指南

新增模板/案例时，确保包含：
- **背景**: 业务场景和约束
- **决策点**: 关键技术选型及理由
- **权衡分析**: 每个选择的优缺点
- **演进路径**: 从 MVP 到生产的里程碑
- **坑点警告**: 实际踩过的坑

## 参考资源

- 原始仓库: https://github.com/study8677/awesome-architecture
- architecture-copilot 原始仓库: https://github.com/study8677/architecture-copilot

**Sources:**
- [Architecture Copilot Repository](https://github.com/study8677/architecture-copilot)
- [Awesome Architecture Repository](https://github.com/study8677/awesome-architecture)

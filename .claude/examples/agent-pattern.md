# Agent模式示例

> 本文档展示Apollo系统中Agent的最佳实践模式和实际应用案例

---

## 一、Agent定义模板

### 1.1 标准Agent结构

```yaml
---
name: agent-name                  # Agent标识符 (kebab-case)
description: 简短描述，说明何时使用此Agent
tools: Read, Grep, Glob          # 授权的工具列表
model: sonnet                     # 模型选择: opus/sonnet/haiku
permissionMode: readOnly          # 可选: 权限模式
---

你是一名[角色定位]，专注于[核心职责]。

## 职责

当被调用时:
1. [第一步]
2. [第二步]
3. [第三步]

## [核心能力模块1]

### 子能力1.1
[详细说明和示例]

### 子能力1.2
[详细说明和示例]

## [核心能力模块2]

...

## 输出格式

[明确定义期望的输出结构]
```

### 1.2 最小可用Agent

```yaml
---
name: file-searcher
description: 快速文件搜索专家。查找文件时使用。
tools: Glob, Grep
model: haiku
---

你是一名文件搜索专家。

## 职责
快速定位文件，支持模糊匹配和内容搜索。

## 搜索策略
1. 使用Glob进行文件名匹配
2. 使用Grep进行内容搜索
3. 返回完整的绝对路径

## 输出格式
\`\`\`
找到的文件:
- /path/to/file1.ts
- /path/to/file2.ts
\`\`\`
```

---

## 二、Agent分类模式

### 2.1 规划类Agent (Planning)

**特征**:
- 模型: opus (需要深度思考)
- 工具: Read, Grep, Glob, Bash
- 职责: 分析、设计、决策

**示例: architect**

```yaml
---
name: architect
description: 软件架构师，用于系统设计、架构决策和技术方案规划
tools: Read, Grep, Glob, Bash
model: opus
---

## 核心能力
1. 需求分析与架构建模
2. 设计模式应用
3. 技术选型评估
4. 架构文档生成

## 输出
- 架构设计文档
- 技术选型报告
- 实施计划
```

### 2.2 开发类Agent (Development)

**特征**:
- 模型: sonnet (平衡能力和成本)
- 工具: Read, Write, Edit, Bash
- 职责: 实现、修改、优化

**示例: code-implementer**

```yaml
---
name: code-implementer
description: 代码实现专家，根据设计文档编写高质量代码
tools: Read, Write, Edit, Bash
model: sonnet
---

## 实施流程
1. 读取设计文档
2. 创建文件结构
3. 实现核心逻辑
4. 编写单元测试
5. 运行测试验证

## 质量标准
- 遵循代码规范
- 100%类型覆盖
- 测试覆盖率≥80%
```

### 2.3 质量类Agent (Quality)

**特征**:
- 模型: sonnet
- 工具: Read, Grep, Glob, Bash
- 职责: 审查、验证、优化

**示例: code-reviewer**

```yaml
---
name: code-reviewer
description: 专业代码审查员，确保代码质量和安全性
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: readOnly
---

## 审查清单
- [ ] 代码质量
- [ ] 安全性
- [ ] 性能
- [ ] 测试覆盖

## 输出格式
### 🔴 严重问题 (必须修复)
### 🟡 警告 (应该修复)
### 🔵 建议 (考虑改进)
```

### 2.4 专业类Agent (Specialized)

**特征**:
- 模型: sonnet/haiku (根据复杂度)
- 工具: 领域特定工具
- 职责: 特定领域任务

**示例: data-scientist**

```yaml
---
name: data-scientist
description: 数据科学专家，用于SQL查询、数据分析和洞察提取
tools: Bash, Read, Write
model: sonnet
---

## 分析流程
1. 需求理解
2. 数据探索
3. 分析查询
4. 结果解读
5. 可视化建议

## 输出
- 分析报告
- SQL查询
- 数据洞察
```

---

## 三、编排模式

### 3.1 并行模式 (PARALLEL)

**适用场景**: 独立子任务，无依赖关系

**示例: 多文件代码审查**

```markdown
## 任务: 审查5个文件

### 编排策略: PARALLEL

执行计划:
1. 同时启动5个code-reviewer Agent
2. 每个Agent审查1个文件
3. 并行执行，提升效率5倍
4. 收集所有结果
5. 合并生成总报告

预估时间: 1分钟 (vs 串行5分钟)
```

### 3.2 串行模式 (SEQUENTIAL)

**适用场景**: 有依赖链的任务

**示例: 完整开发流程**

```markdown
## 任务: 实现新功能

### 编排策略: SEQUENTIAL

执行流程:
1. architect → 设计方案
   ↓ (输出: 设计文档)
2. code-implementer → 实现代码
   ↓ (输出: 代码文件)
3. code-reviewer → 审查代码
   ↓ (输出: 审查报告)
4. debugger → 修复问题 (如有)
   ↓ (输出: 修复后代码)
5. security-analyst → 安全检查
   ↓ (输出: 安全报告)

必须按顺序执行，后续步骤依赖前序输出
```

### 3.3 层级模式 (HIERARCHICAL)

**适用场景**: 需要专家指导的复杂任务

**示例: 大型系统重构**

```markdown
## 任务: 重构支付系统

### 编排策略: HIERARCHICAL

层级结构:

architect (领导者)
  ↓ 设计重构方案
  ├─→ implementer-1 (Worker) - 重构订单模块
  ├─→ implementer-2 (Worker) - 重构支付模块
  └─→ implementer-3 (Worker) - 重构通知模块
        ↓
  所有Worker完成后返回architect
        ↓
  architect整合并验证一致性
```

### 3.4 协作模式 (COLLABORATIVE)

**适用场景**: 跨领域复杂问题

**示例: 全面代码优化**

```markdown
## 任务: 优化关键API性能

### 编排策略: COLLABORATIVE

协作流程:

1. 初始分析 (并行)
   ├─ code-reviewer → 代码质量分析
   ├─ security-analyst → 安全性分析
   └─ performance-optimizer → 性能分析

2. 讨论阶段
   三个Agent交换意见，识别冲突:
   - 性能优化 vs 代码可读性
   - 安全增强 vs 性能开销

3. 达成共识
   综合各方建议，制定平衡方案

4. 实施优化
   implementer根据共识方案执行
```

### 3.5 竞争模式 (COMPETITIVE)

**适用场景**: 探索性任务，需要多方案比较

**示例: 算法选择**

```markdown
## 任务: 选择最优排序算法

### 编排策略: COMPETITIVE

竞争流程:

1. 方案生成 (并行)
   ├─ implementer-1 → 实现快速排序
   ├─ implementer-2 → 实现归并排序
   └─ implementer-3 → 实现堆排序

2. 性能测试 (并行)
   每个Agent提交:
   - 代码实现
   - 性能测试结果
   - 内存占用分析

3. 评估对比
   orchestrator综合评估:
   - 时间复杂度
   - 空间复杂度
   - 代码可读性
   - 实际测试性能

4. 选择最优方案
   根据项目需求选择最佳算法
```

### 3.6 群体模式 (SWARM)

**适用场景**: 大规模任务，需要广泛覆盖

**示例: 全项目代码迁移**

```markdown
## 任务: 将1000个文件从JS迁移到TS

### 编排策略: SWARM

群体协作:

1. 任务分解
   orchestrator将1000个文件分为100批
   每批10个文件

2. 启动Worker群体
   同时启动20个migrator Agent
   每个Agent处理5批

3. 进度跟踪
   orchestrator实时监控:
   - 已完成: 45%
   - 进行中: 20%
   - 待处理: 35%

4. 动态调整
   - 失败任务重新分配
   - 空闲Agent接收新任务
   - 性能慢的Agent减少负载

5. 结果聚合
   所有Agent完成后:
   - 验证迁移完整性
   - 生成迁移报告
   - 运行全量测试
```

---

## 四、实际应用案例

### 4.1 案例1: Bug修复流程

```markdown
## 场景
生产环境报错: 用户无法登录

## 使用的Agent
1. debugger
2. code-reviewer
3. security-analyst

## 执行流程

### Step 1: debugger分析问题
- 查看错误日志
- 定位失败代码
- 识别根本原因: JWT过期时间配置错误

### Step 2: debugger修复
- 更新配置: JWT_EXPIRY = 24h
- 添加错误提示
- 编写回归测试

### Step 3: code-reviewer审查
- 检查修复代码
- 验证测试覆盖
- 确认无副作用

### Step 4: security-analyst验证
- 检查JWT配置安全性
- 验证会话管理
- 确认无安全风险

## 结果
- Bug修复完成
- 测试通过
- 安全验证通过
- 部署到生产环境
```

### 4.2 案例2: 新功能开发

```markdown
## 场景
开发用户通知系统

## 使用的Agent
1. architect
2. code-implementer (×3)
3. code-reviewer
4. security-analyst

## 执行流程 (HIERARCHICAL策略)

### Phase 1: 架构设计
architect:
- 设计系统架构
- 选择消息队列 (Redis Pub/Sub)
- 定义API接口
- 设计数据模型

输出: 架构设计文档

### Phase 2: 并行开发
architect指导3个implementer并行开发:

implementer-1: 通知服务
- 实现消息队列订阅
- 实现通知发送逻辑
- 编写单元测试

implementer-2: API层
- 实现RESTful API
- 实现WebSocket推送
- 编写API测试

implementer-3: 数据层
- 实现通知存储
- 实现查询接口
- 编写数据库测试

### Phase 3: 质量保障
code-reviewer:
- 审查所有代码
- 验证代码规范
- 检查测试覆盖

security-analyst:
- 验证API权限控制
- 检查数据加密
- 审计日志记录

### Phase 4: 集成测试
architect:
- 整合所有模块
- 执行集成测试
- 性能压测
- 生成文档

## 结果
- 功能完整实现
- 测试覆盖率95%
- 安全验证通过
- 文档齐全
```

### 4.3 案例3: 代码重构

```markdown
## 场景
重构遗留代码，提升可维护性

## 使用的Agent
1. code-reviewer (分析)
2. architect (设计)
3. code-implementer (重构)
4. debugger (验证)

## 执行流程 (SEQUENTIAL策略)

### Step 1: code-reviewer分析现状
- 识别代码异味
- 统计技术债务
- 标记重构优先级

输出:
- 高优先级: UserService (复杂度过高)
- 中优先级: AuthService (耦合严重)
- 低优先级: LogService (可读性差)

### Step 2: architect设计重构方案
针对UserService设计:
- 拆分为多个小类
- 引入依赖注入
- 应用策略模式

输出: 重构设计文档

### Step 3: code-implementer执行重构
按设计文档重构:
- 创建新结构
- 迁移代码
- 更新测试
- 保持API兼容

### Step 4: debugger验证
- 运行所有测试
- 验证功能一致性
- 性能对比测试
- 修复发现的问题

## 结果
- 代码复杂度降低60%
- 测试覆盖率提升到90%
- 性能无回退
- 可维护性显著提升
```

---

## 五、最佳实践总结

### 5.1 Agent设计原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **单一职责** | 每个Agent专注一个领域 | code-reviewer只做审查 |
| **最小权限** | 仅授予必要工具 | 审查Agent无Write权限 |
| **清晰输出** | 定义明确的输出格式 | 使用Markdown结构化输出 |
| **可组合** | 支持与其他Agent协作 | 输出可作为下一个Agent输入 |

### 5.2 编排策略选择指南

```
任务分析
   ↓
是否可分解? ─No→ 使用单一Agent
   ↓ Yes
子任务间有依赖? ─Yes→ SEQUENTIAL
   ↓ No
需要专家指导? ─Yes→ HIERARCHICAL
   ↓ No
跨领域问题? ─Yes→ COLLABORATIVE
   ↓ No
需要多方案比较? ─Yes→ COMPETITIVE
   ↓ No
大规模任务? ─Yes→ SWARM
   ↓ No
默认使用 → PARALLEL
```

### 5.3 避免的反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|----------|
| 万能Agent | 一个Agent做所有事 | 创建专业化Agent |
| 过度细分 | Agent太多太细 | 合理粒度,3-10个为宜 |
| 权限过大 | 所有Agent都有Full权限 | 最小权限原则 |
| 无输出规范 | Agent输出格式随意 | 定义清晰的输出模板 |
| 忽略上下文 | 每次重新加载 | 使用渐进式披露 |

---

## 六、模板库

### 6.1 快速搜索Agent

```yaml
---
name: quick-searcher
description: 快速搜索文件和代码片段
tools: Glob, Grep
model: haiku
---

## 搜索方法
1. Glob匹配文件名
2. Grep搜索内容

## 输出
文件路径列表
```

### 6.2 文档生成Agent

```yaml
---
name: doc-generator
description: 根据代码生成文档
tools: Read, Write, Bash
model: sonnet
---

## 生成流程
1. 读取代码文件
2. 提取JSDoc/注释
3. 生成Markdown文档
4. 包含示例代码

## 输出
完整的API文档
```

### 6.3 性能分析Agent

```yaml
---
name: performance-analyzer
description: 分析代码性能并提供优化建议
tools: Read, Bash, Grep
model: sonnet
---

## 分析维度
1. 时间复杂度
2. 空间复杂度
3. 数据库查询
4. 网络请求

## 输出
性能分析报告 + 优化建议
```

---

## 附录: Agent检查清单

创建新Agent时检查:

- [ ] YAML frontmatter完整
- [ ] name使用kebab-case
- [ ] description清晰说明使用场景
- [ ] tools列表正确
- [ ] model选择合理
- [ ] 职责明确
- [ ] 输出格式定义清晰
- [ ] 已添加到agents/INDEX.md
- [ ] 已测试基本功能
- [ ] 已记录使用示例

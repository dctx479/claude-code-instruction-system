# Apollo系统架构文档

> Apollo - 自进化元系统的完整技术架构

---

## 一、系统概览

### 1.1 核心定位

Apollo是一个**自进化的AI智能体编排系统**，通过渐进式披露、知识沉淀和自主决策机制，实现高效、智能的软件开发自动化。

### 1.2 核心能力

```
┌─────────────────────────────────────────────────────────┐
│                   Apollo 核心引擎                         │
├─────────────────────────────────────────────────────────┤
│  1. 自进化能力   - 从错误中学习，自动完善配置           │
│  2. Agent驾驭   - 智能编排多Agent协作                    │
│  3. 知识沉淀    - 持久化学习成果到memory/               │
│  4. 动态适应    - 根据任务自动选择最优策略               │
│  5. 渐进式披露  - 按需加载，节省60-80% Token            │
└─────────────────────────────────────────────────────────┘
```

### 1.3 版本历史

| 版本 | 发布日期 | 核心特性 |
|------|----------|----------|
| 1.0 Basic | 2026-01 | 基础Agent系统 |
| 2.0 Apollo | 2026-01 | 自进化 + Agent编排 |
| 2.1 Apollo+ | 2026-01 | 渐进式披露 + Context Engineering |

---

## 二、系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户交互层                               │
│  Claude Code CLI → CLAUDE.md → 解析指令 → 选择执行路径          │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                       配置管理层                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  CLAUDE.md   │  │ agents/      │  │ .claude/     │          │
│  │  (核心配置)  │  │ INDEX.md     │  │ reference/   │          │
│  │              │  │ (Agent索引)  │  │ examples/    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      编排决策层                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Orchestrator (元编排者)                         │  │
│  │  - 任务分解                                               │  │
│  │  - 策略选择 (并行/串行/层级/协作/竞争/群体)              │  │
│  │  - Agent调度                                             │  │
│  │  - 结果整合                                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                       Agent执行层                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Planning   │  │ Development │  │   Quality   │            │
│  │  ─────────  │  │  ─────────  │  │  ─────────  │            │
│  │ architect   │  │code-reviewer│  │  security-  │            │
│  │             │  │  debugger   │  │   analyst   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│  ┌─────────────┐                                                │
│  │ Specialized │                                                │
│  │  ─────────  │                                                │
│  │data-scientist│                                               │
│  └─────────────┘                                                │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      工具执行层                                  │
│  Read | Write | Edit | Bash | Grep | Glob | Task               │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      知识沉淀层                                  │
│  memory/                                                         │
│  ├── lessons-learned.md    (经验教训)                           │
│  ├── best-practices.md     (最佳实践)                           │
│  ├── error-patterns.md     (错误模式)                           │
│  └── agent-performance.md  (Agent性能)                          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流图

```
用户请求
   ↓
CLAUDE.md解析
   ↓
读取 agents/INDEX.md ← [渐进式披露入口]
   ↓
任务分析
   ↓
   ├─ 简单任务 → 直接执行
   ├─ 中等任务 → 加载对应Agent → 执行
   └─ 复杂任务 → 激活Orchestrator
                    ↓
                任务分解
                    ↓
                选择编排策略
                    ↓
              ┌─────┴─────┐
              ↓           ↓
         加载Agent1   加载Agent2 (仅加载需要的)
              ↓           ↓
            执行         执行
              ↓           ↓
              └─────┬─────┘
                    ↓
              整合结果
                    ↓
              质量验证
                    ↓
            返回给用户
                    ↓
        沉淀到memory/ (自进化)
```

---

## 三、核心模块设计

### 3.1 渐进式披露模块

**目标**: 减少Token消耗，提升响应速度

```
┌─────────────────────────────────────────────────────────┐
│             渐进式披露引擎                               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Step 1: 读取 agents/INDEX.md (~500 tokens)            │
│          ↓                                              │
│  Step 2: 分析任务 → 匹配Agent                          │
│          ↓                                              │
│  Step 3: 仅加载匹配的Agent完整定义 (~800 tokens)        │
│          ↓                                              │
│  Step 4: 按需引用 .claude/reference/ (~200 tokens)     │
│                                                          │
│  总计: ~1500 tokens (vs 传统方式 15000 tokens)          │
│  节省率: 90%                                             │
└─────────────────────────────────────────────────────────┘
```

**实现机制**:
1. **索引优先**: INDEX.md包含所有Agent元数据
2. **延迟加载**: 仅在需要时读取完整Agent文件
3. **引用系统**: 详细文档通过引用而非嵌入
4. **上下文释放**: Agent执行完毕后释放上下文

### 3.2 Agent编排模块

**编排策略矩阵**:

```
┌────────────────────────────────────────────────────────┐
│  任务特征                推荐策略         Agent配置    │
├────────────────────────────────────────────────────────┤
│  独立子任务              PARALLEL         多Worker     │
│  依赖链任务              SEQUENTIAL       管道式       │
│  复杂决策                HIERARCHICAL     专家+Worker  │
│  跨领域问题              COLLABORATIVE    多专家讨论   │
│  创新探索                COMPETITIVE      多方案竞争   │
│  大规模任务              SWARM            群体协作     │
└────────────────────────────────────────────────────────┘
```

**策略选择算法**:

```python
def select_strategy(task: Task) -> Strategy:
    """根据任务特征自动选择最优编排策略"""

    score = {
        'PARALLEL': 0,
        'SEQUENTIAL': 0,
        'HIERARCHICAL': 0,
        'COLLABORATIVE': 0,
        'COMPETITIVE': 0,
        'SWARM': 0,
    }

    # 分析任务特征
    if task.has_independent_subtasks:
        score['PARALLEL'] += 3
        score['SWARM'] += 2

    if task.has_dependencies:
        score['SEQUENTIAL'] += 3

    if task.requires_expertise:
        score['HIERARCHICAL'] += 3
        score['COLLABORATIVE'] += 2

    if task.is_cross_domain:
        score['COLLABORATIVE'] += 3

    if task.needs_exploration:
        score['COMPETITIVE'] += 3

    if task.scale == 'large':
        score['SWARM'] += 3

    # 返回得分最高的策略
    return max(score, key=score.get)
```

### 3.3 自进化模块

**学习循环**:

```
┌─────────────────────────────────────────────────────────┐
│                  自进化循环引擎                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  触发条件:                                               │
│  ├─ ❌ 任务失败                                         │
│  ├─ ⚠️ 重复错误 (≥2次)                                 │
│  ├─ 💡 发现更优方案                                     │
│  ├─ 📝 用户添加指令                                     │
│  └─ 🔄 复杂任务回顾                                     │
│                                                          │
│  执行流程:                                               │
│  1. 捕获事件 → 分析根因                                 │
│  2. 生成改进建议 → 更新配置文件                         │
│  3. 记录到 memory/lessons-learned.md                    │
│  4. 验证效果 → 持续反馈循环                             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**更新目标**:
- `CLAUDE.md` - 核心指令优化
- `agents/*.md` - Agent定义改进
- `commands/*.md` - 命令优化
- `memory/lessons-learned.md` - 经验积累

### 3.4 知识管理模块

**知识图谱结构**:

```
memory/
├── lessons-learned.md      # 经验教训库
│   └── 格式: [日期] 问题 → 根因 → 解决方案 → 验证
│
├── best-practices.md       # 最佳实践
│   └── 格式: 模式名称 → 应用场景 → 实施方法
│
├── error-patterns.md       # 错误模式
│   └── 格式: 错误类型 → 识别特征 → 预防措施
│
└── agent-performance.md    # Agent性能
    └── 格式: Agent名称 → 成功率 → 平均耗时 → 优化建议
```

**知识查询API**:
```typescript
interface KnowledgeQuery {
  type: 'lesson' | 'practice' | 'error' | 'performance';
  keywords: string[];
  dateRange?: [Date, Date];
}

function queryKnowledge(query: KnowledgeQuery): Knowledge[] {
  // 从memory/目录检索相关知识
  // 支持关键词匹配、时间范围过滤
}
```

---

## 四、技术选型

### 4.1 基础技术

| 组件 | 技术 | 版本 | 说明 |
|------|------|------|------|
| CLI工具 | Claude Code CLI | latest | 官方CLI |
| 配置格式 | Markdown + YAML | - | 易读易写 |
| 脚本语言 | Bash + TypeScript | 5.x | 跨平台支持 |
| 模型 | Claude Opus/Sonnet/Haiku | 4.5 | 根据任务选择 |

### 4.2 Agent模型分配

```
┌─────────────────────────────────────────────────────────┐
│  Agent              模型        Token成本    适用场景   │
├─────────────────────────────────────────────────────────┤
│  orchestrator       opus        ★★★★★      复杂编排    │
│  architect          opus        ★★★★★      架构设计    │
│  code-reviewer      sonnet      ★★★☆☆      代码审查    │
│  debugger           sonnet      ★★★☆☆      问题诊断    │
│  security-analyst   sonnet      ★★★☆☆      安全审计    │
│  data-scientist     sonnet      ★★★☆☆      数据分析    │
│  explorer (未来)    haiku       ★☆☆☆☆      快速搜索    │
└─────────────────────────────────────────────────────────┘
```

---

## 五、性能优化策略

### 5.1 Token优化

**优化前后对比**:

| 场景 | 传统方式 | Apollo方式 | 节省率 |
|------|----------|-----------|--------|
| 简单任务 | 15000 | 1500 | 90% |
| 代码审查 | 8000 | 2000 | 75% |
| 架构设计 | 20000 | 5000 | 75% |
| 复杂编排 | 30000 | 8000 | 73% |

**优化技术**:
1. 渐进式披露 (60-80%节省)
2. 引用系统 (85%节省)
3. Agent按需加载 (70%节省)
4. 上下文释放 (50%节省)

### 5.2 响应速度优化

```
┌─────────────────────────────────────────────────────────┐
│  优化层次          优化方法                 效果提升    │
├─────────────────────────────────────────────────────────┤
│  配置加载          索引优先加载              90% ↑     │
│  Agent选择         智能匹配算法              80% ↑     │
│  并行执行          PARALLEL策略             3-5x ↑     │
│  缓存策略          Memory层缓存             60% ↑     │
└─────────────────────────────────────────────────────────┘
```

### 5.3 并发处理

**并行模式**:
```
任务队列
   ↓
Orchestrator分解
   ↓
   ├─→ Agent1 (Worker)
   ├─→ Agent2 (Worker)  ← 并行执行
   └─→ Agent3 (Worker)
        ↓
     结果合并
```

---

## 六、安全架构

### 6.1 权限控制

```
┌─────────────────────────────────────────────────────────┐
│  权限层级        授权范围                               │
├─────────────────────────────────────────────────────────┤
│  ReadOnly        Read, Grep, Glob, Bash (只读命令)      │
│  Standard        + Write (受限写入)                      │
│  Elevated        + Edit (编辑现有文件)                   │
│  Full            + Task (创建Agent)                      │
└─────────────────────────────────────────────────────────┘
```

**Agent权限分配**:
- code-reviewer: ReadOnly
- debugger: Standard
- architect: Elevated
- orchestrator: Full

### 6.2 敏感信息保护

**保护机制**:
1. 环境变量存储密钥
2. `.gitignore` 排除本地配置
3. Security-analyst Agent审查
4. Pre-commit Hook验证

### 6.3 Hook验证

```json
{
  "preToolUse": {
    "Write": "hooks/verify-write.sh",
    "Edit": "hooks/verify-edit.sh"
  },
  "postToolUse": {
    "Edit": "hooks/post-edit-lint.sh"
  }
}
```

---

## 七、扩展性设计

### 7.1 新Agent添加流程

```
1. 创建 agents/new-agent.md
   ├─ 定义 YAML frontmatter
   ├─ 编写系统提示词
   └─ 设置工具权限

2. 更新 agents/INDEX.md
   ├─ 添加Agent元数据
   └─ 更新分类和策略矩阵

3. 测试验证
   ├─ 独立测试Agent功能
   └─ 集成测试编排场景

4. 记录到memory/
   └─ 沉淀使用经验
```

### 7.2 新策略添加

```typescript
// 在orchestrator.md中添加新策略
enum Strategy {
  PARALLEL = 'PARALLEL',
  SEQUENTIAL = 'SEQUENTIAL',
  HIERARCHICAL = 'HIERARCHICAL',
  COLLABORATIVE = 'COLLABORATIVE',
  COMPETITIVE = 'COMPETITIVE',
  SWARM = 'SWARM',
  CUSTOM_NEW = 'CUSTOM_NEW', // 新增策略
}
```

### 7.3 插件系统 (规划中)

```
plugins/
├── custom-agents/       # 自定义Agent插件
├── custom-strategies/   # 自定义策略插件
├── custom-tools/        # 自定义工具插件
└── integrations/        # 第三方集成
```

---

## 八、监控与度量

### 8.1 关键指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| Token使用率 | 实际/传统方式 | <30% |
| 任务成功率 | 成功/总任务数 | >95% |
| Agent响应时间 | 平均执行时间 | <5s |
| 自进化触发率 | 学习事件/任务数 | >10% |

### 8.2 性能追踪

```typescript
interface PerformanceMetrics {
  taskId: string;
  startTime: Date;
  endTime: Date;
  tokensUsed: number;
  agentsInvolved: string[];
  strategy: Strategy;
  success: boolean;
}

// 记录到 memory/agent-performance.md
```

---

## 九、未来规划

### 9.1 短期计划 (1-3个月)

- [ ] 完善渐进式披露机制
- [ ] 增加更多专业Agent (Explorer, Optimizer等)
- [ ] 实现Agent性能自动调优
- [ ] 完善知识图谱系统

### 9.2 中期计划 (3-6个月)

- [ ] 实现插件系统
- [ ] 支持自定义编排策略
- [ ] 多项目知识共享机制
- [ ] Web UI管理界面

### 9.3 长期愿景

- [ ] 完全自主的AI开发系统
- [ ] 跨团队知识协作平台
- [ ] 行业领域专用Agent库
- [ ] AI驱动的软件工程标准

---

## 十、参考资源

### 10.1 内部文档

- `.claude/reference/best-practices.md` - 最佳实践指南
- `.claude/reference/coding-standards.md` - 代码规范
- `.claude/examples/agent-pattern.md` - Agent模式示例
- `memory/lessons-learned.md` - 历史经验

### 10.2 外部资源

- [Claude Code CLI 官方文档](https://code.claude.com/docs)
- [Anthropic Agent编排最佳实践](https://www.anthropic.com/engineering)
- [Awesome Claude Code](https://github.com/hesreallyhim/awesome-claude-code)

---

## 附录: 术语表

| 术语 | 定义 |
|------|------|
| Agent | 专业化的AI智能体，负责特定领域任务 |
| Orchestrator | 元编排者，负责调度和协调多个Agent |
| 渐进式披露 | 按需加载配置，减少Token消耗的策略 |
| A.C.E.循环 | Analyze-Code-Evaluate，自主开发循环 |
| 自进化 | 从错误中学习，自动完善配置的能力 |
| Context Engineering | 上下文工程，优化配置结构的方法论 |

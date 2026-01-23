# RPI 工作流 - Spec Flow 命令

> **设计理念**: 强制阶段分离，防止上下文污染，提高规范质量

## 命令概览

`/spec-flow` 命令实现 RPI (Research, Plan, Implement) 工作流的状态机管理。

## 使用方法

### 启动新功能开发
```bash
/spec-flow start <feature-name>
```

**示例**:
```bash
/spec-flow start user-authentication
```

**执行流程**:
1. 创建 `specs/###-user-authentication/` 目录
2. 初始化状态: `RESEARCH`
3. 创建 `.spec-flow-state.json` 状态文件
4. 启动 Research 阶段

### 转换到下一阶段
```bash
/spec-flow next
```

**执行流程**:
1. 验证当前阶段是否完成
2. 保存当前阶段输出
3. 清理上下文（可选）
4. 加载下一阶段所需上下文
5. 转换状态

### 查看当前状态
```bash
/spec-flow status
```

**输出示例**:
```
当前功能: user-authentication
当前阶段: PLAN (2/3)
进度: 66%

已完成:
✓ RESEARCH - 2026-01-23 14:30
  输出: specs/001-user-authentication/research.md

进行中:
→ PLAN - 开始于 2026-01-23 15:00
  预期输出: spec.md, data-model.md, tasks.md

待执行:
○ IMPLEMENT
```

### 跳转到指定阶段
```bash
/spec-flow goto <phase>
```

**示例**:
```bash
/spec-flow goto IMPLEMENT
```

---

## RPI 三阶段详解

### 阶段 1: RESEARCH (研究澄清)

**目标**: 理解问题域，收集信息，做出技术决策

**输入**:
- 用户需求描述
- 项目宪章 (`memory/constitution.md`)

**输出**:
- `research.md` - 技术调研和决策记录
- `clarifications.md` - 需求澄清记录

**关键活动**:
- 需求分析（九维度清单）
- 技术调研
- 风险识别
- 决策记录

**九维度清单**:
1. 功能范围与行为
2. 领域与数据模型
3. 交互与用户体验流程
4. 非功能质量属性
5. 集成与外部依赖
6. 边缘情况与故障处理
7. 约束与权衡
8. 术语与一致性
9. 完成信号

**验收标准**:
- [ ] 所有九维度都有明确答案
- [ ] 技术方案已调研并记录
- [ ] 风险已识别并有对策
- [ ] 决策依据清晰

**上下文大小**: ~5KB

---

### 阶段 2: PLAN (规划设计)

**目标**: 设计架构，定义契约，生成任务列表

**输入**:
- `research.md` (从 RESEARCH 阶段)
- 代码库结构
- 技术栈信息

**输出**:
- `spec.md` - 功能规范
- `data-model.md` - 数据模型
- `api-contracts.yaml` - API 契约
- `tasks.md` - 任务清单

**关键活动**:
- 架构设计
- 数据模型定义
- API 契约设计
- 任务分解

**验收标准**:
- [ ] Spec 包含所有必需章节
- [ ] 数据模型完整且一致
- [ ] API 契约符合 OpenAPI 规范
- [ ] 任务清单可执行且有优先级

**上下文大小**: ~15KB

---

### 阶段 3: IMPLEMENT (实施开发)

**目标**: 按照 Plan 执行任务，实现功能

**输入**:
- `tasks.md` (从 PLAN 阶段)
- `spec.md` + `data-model.md` + `api-contracts.yaml`
- 相关代码文件

**输出**:
- 可运行的代码
- 测试用例
- 文档更新

**关键活动**:
- 按 tasks.md 顺序执行
- 测试驱动开发 (TDD)
- 代码审查
- 文档更新

**验收标准**:
- [ ] 所有任务已完成并标记 `[X]`
- [ ] 测试覆盖率 ≥80%
- [ ] QA Reviewer 评分 ≥80
- [ ] 文档已更新

**上下文大小**: ~20KB

---

## 状态机设计

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │ /spec-flow start
       ▼
┌─────────────┐
│  RESEARCH   │ ← 需求分析、技术调研
└──────┬──────┘
       │ /spec-flow next
       │ (验证九维度清单)
       ▼
┌─────────────┐
│    PLAN     │ ← 架构设计、任务分解
└──────┬──────┘
       │ /spec-flow next
       │ (验证 spec 完整性)
       ▼
┌─────────────┐
│  IMPLEMENT  │ ← 代码实现、测试
└──────┬──────┘
       │ /spec-flow next
       │ (验证 QA 评分)
       ▼
┌─────────────┐
│    DONE     │
└─────────────┘
```

---

## 状态文件格式

`.spec-flow-state.json`:
```json
{
  "feature": "user-authentication",
  "spec_id": "001",
  "current_phase": "PLAN",
  "phases": {
    "RESEARCH": {
      "status": "completed",
      "started_at": "2026-01-23T14:30:00Z",
      "completed_at": "2026-01-23T15:00:00Z",
      "outputs": [
        "specs/001-user-authentication/research.md",
        "specs/001-user-authentication/clarifications.md"
      ],
      "validation": {
        "nine_dimensions": true,
        "technical_research": true,
        "risk_identified": true
      }
    },
    "PLAN": {
      "status": "in_progress",
      "started_at": "2026-01-23T15:00:00Z",
      "outputs": [],
      "validation": {}
    },
    "IMPLEMENT": {
      "status": "pending",
      "outputs": [],
      "validation": {}
    }
  },
  "created_at": "2026-01-23T14:30:00Z",
  "updated_at": "2026-01-23T15:00:00Z"
}
```

---

## 上下文管理策略

### 阶段转换时的上下文处理

```python
def transition_phase(current_phase, next_phase):
    # 1. 验证当前阶段完成
    validate_phase_completion(current_phase)

    # 2. 保存当前阶段输出
    save_phase_outputs(current_phase)

    # 3. 清理上下文（可选）
    # 注意：不是真正清理，而是标记为"可卸载"
    mark_context_unloadable(current_phase)

    # 4. 加载下一阶段所需上下文
    load_phase_context(next_phase)

    # 5. 更新状态
    update_state(next_phase)
```

### 上下文分层

| 阶段 | 加载的上下文 | 大小估算 |
|------|-------------|---------|
| RESEARCH | 用户需求 + 项目宪章 | ~2KB |
| PLAN | research.md + 代码库结构 | ~10KB |
| IMPLEMENT | tasks.md + spec.md + 相关代码 | ~20KB |

**关键优化**:
- 每个阶段只加载必要信息
- 避免加载完整代码库
- 使用引用而非复制

---

## 集成点

### 与 Spec-First 工作流的关系

RPI 工作流是 Spec-First 的增强版本：

```
Spec-First (原有):
需求 → spec-writer → spec.md → 开发 → qa-reviewer

RPI-PHASED (增强):
需求 → RESEARCH → research.md
     → PLAN → spec.md + tasks.md
     → IMPLEMENT → 代码
```

**优势**:
- 更明确的阶段边界
- 更好的上下文管理
- 更高的规范质量

### 与 Orchestrator 的集成

```markdown
# orchestrator 可以调用 spec-flow

当任务复杂度高且需要深度思考时:
1. orchestrator 识别需要 RPI 工作流
2. 调用 /spec-flow start <feature>
3. 监控各阶段进度
4. 在 IMPLEMENT 阶段调度 Worker Agents
```

---

## 最佳实践

### 1. 何时使用 RPI 工作流

✅ **推荐使用**:
- 复杂功能开发（估算 Token > 30K）
- 需求不明确，需要深度澄清
- 跨领域问题，涉及多个技术栈
- 高风险功能，需要充分规划

❌ **不推荐使用**:
- 简单 Bug 修复
- 小型功能增强
- 紧急热修复
- 明确且简单的需求

### 2. 阶段转换的时机

**RESEARCH → PLAN**:
- 九维度清单全部完成
- 技术方案已调研
- 风险已识别

**PLAN → IMPLEMENT**:
- Spec 通过验证
- 任务清单可执行
- API 契约已定义

**IMPLEMENT → DONE**:
- 所有任务完成
- QA 评分 ≥80
- 测试覆盖率 ≥80%

### 3. 跨阶段协作

**多人协作**:
```
开发者 A: RESEARCH 阶段
  ↓ 输出 research.md
开发者 B: PLAN 阶段
  ↓ 输出 spec.md + tasks.md
开发者 C, D, E: IMPLEMENT 阶段（并行）
```

**单人开发**:
```
Session 1: RESEARCH (1 小时)
  [保存检查点]
Session 2: PLAN (2 小时)
  [保存检查点]
Session 3: IMPLEMENT (4 小时)
```

---

## 故障排查

### 阶段验证失败

**问题**: `/spec-flow next` 提示验证失败

**解决方案**:
1. 运行 `/spec-flow status` 查看缺失项
2. 补充缺失的输出文件
3. 确保验收标准全部满足
4. 重新运行 `/spec-flow next`

### 上下文过大

**问题**: 即使使用 RPI，上下文仍然超过限制

**解决方案**:
1. 进一步分解任务
2. 使用更小的代码片段
3. 采用 SWARM 策略并行开发
4. 考虑拆分为多个功能

### 状态文件丢失

**问题**: `.spec-flow-state.json` 文件丢失

**解决方案**:
1. 从 `specs/###-feature/` 目录重建状态
2. 根据已有输出文件推断当前阶段
3. 手动创建状态文件
4. 使用 `/spec-flow goto` 跳转到正确阶段

---

## 相关文档

- **Spec-First 工作流**: `workflows/spec-driven-dev.md`
- **九维度清单**: `agents/spec-writer.md`
- **编排策略**: `workflows/orchestration-patterns.md`
- **上下文工程**: `workflows/context-engineering.md`

---

## 更新日志

### 2026-01-23
- 创建 RPI 工作流命令
- 实现状态机管理
- 集成九维度清单
- 定义阶段验收标准

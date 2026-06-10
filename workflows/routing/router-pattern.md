# Router 路由模式

> 来源：`agents/router.md` + `docs/ORCHESTRATION-GUIDE.md` § 路由器 Agent 设计模式

---

## 概述

Router 是一种**分发层设计模式**，而非执行层。它的职责是接收用户意图、匹配能力、构造上下文、分发给合适的 Agent/Skill 组合执行。

```
用户请求
    ↓
Router（意图识别 + 能力匹配 + 上下文构造）
    ↓
Specialist Agent（读取 Skill 执行任务）
    ↓
结果返回用户
```

---

## 路由粒度

路由粒度决定了模型切换的频率，直接影响 KV-cache 命中率和推理成本。

| 粒度 | 切换频率 | KV-cache 友好性 | 适用场景 |
|------|---------|----------------|---------|
| **request 级** | 每次请求 | ❌ 频繁失效 | 简单任务分发 |
| **session 级** | 每个会话一次 | ✅ 命中率高 | 对话式任务 |
| **sub-agent 级** | 子 Agent 独立 | ✅ 主/子隔离 | 复杂多 Agent 协作 |

**推荐原则**：
- 对话式任务 → session 级路由（会话开始时确定 Agent，中途不切换）
- 并行子 Agent → sub-agent 级路由（独立路由状态，互不污染）
- 单次查询 → request 级路由（简单但 cache 效率低）

---

## 本系统实现方式

### 自动路由（intent-state.json）

```
UserPromptSubmit Hook
    → intent-detector.sh 分析关键词
    → 写入 ~/.claude/intent-state.json
    → Claude 读取 agent 字段
    → 加载 agents/{agent}.md
    → 以该 Agent 角色执行
```

**优点**：零认知负担，全自动  
**缺点**：依赖关键词匹配，复杂意图可能路由失准

### 手动路由（@agent-id 前缀）

```bash
@architect 请帮我设计系统
@debugger 这个报错怎么回事
@orchestrator 编排这个复杂任务
@router 分析意图后路由
```

**优点**：精确控制，跳过自动路由  
**缺点**：需要用户记住 Agent ID

### 显式 Router Agent（agents/router.md）

对于复杂任务、多 Agent 协作场景，显式调用 Router Agent：

```bash
@router 帮我写一篇关于 AI Agent 的技术博客
```

Router 会：
1. 识别意图（技术写作）
2. 匹配能力（deep-research + paper-writing-assistant）
3. 决定编排模式（SEQUENTIAL）
4. 分发并监督执行

---

## 路由决策规则

### 任务类型 → Agent 映射

| 任务类型 | 路由 Agent | 辅助 Skill | 编排模式 |
|---------|-----------|-----------|---------|
| Bug 修复 | debugger | — | SINGLE |
| 代码审查 | code-reviewer | — | SINGLE |
| 新功能开发 | spec-writer → orchestrator | sdd-riper | SEQUENTIAL |
| 架构设计 | architect | architecture-copilot | SINGLE |
| 数据查询 | data-scientist | pandas | SINGLE |
| 安全审计 | security-analyst | code-security-review | SINGLE |
| 文献调研 | literature-manager | deep-research | SEQUENTIAL |
| 批量任务 | orchestrator | — | SWARM（>50）|

### 复杂度 → 编排模式映射

```
单一意图、单一领域    → SINGLE（直接路由到 Specialist）
多步骤、有依赖        → SEQUENTIAL（按顺序路由）
独立子任务 ≤10       → PARALLEL（并行路由）
同质任务 >50         → SWARM（群体路由）
跨领域、需协商        → COLLABORATIVE（多 Specialist）
```

---

## 负向路由（告知不需要什么）

Router 在分发子 Agent 时，除了告知"需要什么 Skill"，同样重要的是告知"不需要什么 Skill"：

```markdown
# 子 Agent prompt 模板

你负责 {task_description}。

执行前，请先读取以下 Skills:
1. {skill_path_1} — 原因: {why_needed}

你不需要读取: {excluded_skills}（与当前任务无关，避免 Token 浪费）
```

**原则**：负向路由减少无关 Skill 加载，节省 60-80% Token。

---

## session 级路由实现（PilotDeck 模式）

核心设计：路由决策按 `sessionId` 缓存，子 Agent 用 `sessionId:sub` 区分。

```typescript
function makeKey(sessionId: string, isSubagent: boolean): string {
  return isSubagent ? `${sessionId}:sub` : sessionId;
}
```

**本系统的潜在优化**（P1 建议）：
1. 在 `intent-state.json` 增加 `lastRouteDecision` 字段，同 session 复用
2. 子 Agent 启动时写入 `intent-state-{task_id}.json`，避免污染主会话
3. 路由缓存 TTL 设置为 10-30 分钟（≥ Prompt Cache TTL 5 分钟）

---

## 路由失效防护

当上下文超过 ~300-400k tokens 时，路由匹配约束力下降：

1. **主动压缩**：~250k tokens 时 `/compact` 并附上未来方向和路由提醒
2. **路由强化**：关键路由规则写入 CLAUDE.md（固定上下文，每次都加载）
3. **Subagent 隔离**：大量中间输出交给 Subagent，避免撑大主上下文

---

## 相关文件

| 文件 | 作用 |
|------|------|
| `agents/router.md` | Router Agent 完整定义 |
| `~/.claude/hooks/intent-detector.sh` | 自动路由的核心实现 |
| `~/.claude/intent-state.json` | 路由状态文件 |
| `docs/ORCHESTRATION-GUIDE.md` | 路由器设计模式详解 |
| `memory/best-practices.md` BP-024 | 能力路由优先于工具堆叠 |

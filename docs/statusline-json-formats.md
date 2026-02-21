# StatusLine stdin JSON 格式参考

> 记录 Claude Code 通过 stdin 传给 statusLine 命令的所有已观测 JSON 格式。
> 每个格式标注 Claude Code 版本、json_len 和观测时间，供后续调试参考。

---

## 快速决策规则

```
total_cost_usd 不存在  →  EXIT_EARLY（对话启动时）
total_cost_usd = 0     →  EXIT_EARLY（初始化调用）
total_cost_usd > 0     →  渲染 HUD（Stop 事件）
```

---

## 格式 A：对话启动 JSON（初始化）

**特征**：含 `session_id`、`cwd`、`workspace`、`version`，**无 `cost`/`total_cost_usd`**

**Claude Code 版本**：2.0.x（2026-02-21 观测）
**json_len**：约 900–1200 字节（真实会话，含 transcript_path）
**观测场景**：每次打开 Claude Code 对话时触发，可能触发 2–3 次

### 简单会话样本（json_len ≈ 114）

```json
{
  "session_id": "abc",
  "cwd": "G:\\proj",
  "model": {
    "id": "claude-sonnet-4-6",
    "display_name": "Sonnet"
  },
  "version": "2.0.80"
}
```

### 真实会话样本（json_len ≈ 1121，字段部分省略）

```json
{
  "session_id": "acee10ae-ba87-42eb-a878-81f6b5f920cb",
  "transcript_path": "C:\\Users\\ASUS\\.claude\\projects\\G--GitHub-...\\acee10ae-....jsonl",
  "cwd": "G:\\GitHub_local\\Self-built\\Prompt\\ClaudeCodePlan\\claude-code-instruction-system",
  "model": {
    "id": "claude-sonnet-4-6",
    "display_name": "Sonnet 4.6"
  },
  "workspace": { ... }
}
```

> **注意**：真实会话启动 JSON 含 `transcript_path`（与 Stop 事件 JSON 相同），但**无 `cost` 字段**。
> 不能用 `transcript_path` 是否存在来区分启动 vs Stop 事件。

---

## 格式 B：Stop 事件 JSON（正常渲染触发）

**特征**：含 `cost.total_cost_usd`（**> 0**）、`transcript_path`、`exceeds_200k_tokens`，**无 `session_id`**（简单会话）或**可能含 `session_id`**（真实会话，待确认）

**Claude Code 版本**：2.0.x（2026-02-21 观测）
**json_len**：约 158 字节（简单会话样本；真实会话可能更大）
**观测场景**：对话结束时（Claude 完成回复后）触发

### 简单会话样本（json_len ≈ 158）

```json
{
  "model": {
    "id": "claude-sonnet-4-6",
    "display_name": "Sonnet 4.6"
  },
  "cost": {
    "total_cost_usd": 0.015
  },
  "transcript_path": "C:\\path.jsonl",
  "exceeds_200k_tokens": false
}
```

> **⚠️ 待确认**：真实会话（json_len > 158）的 Stop 事件 JSON 格式尚未捕获。
> 已知真实会话 Stop JSON 导致 statusLine 无法渲染（可能含 `session_id`，被旧版 session_id 检测过滤）。
> debug 日志仍开启中，等待下一次 Stop 事件捕获完整格式。

---

## 格式 C：初始化调用（cost=0）

**特征**：含 `session_id` + `cost.total_cost_usd = 0`，json 较小

**Claude Code 版本**：2.0.x（2026-02-21 观测）
**json_len**：约 82 字节
**观测场景**：启动序列的第 3 次调用，约在启动后 1–2 秒

### 样本

```json
{
  "session_id": "abc",
  "cost": {
    "total_cost_usd": 0
  },
  "model": {
    "display_name": "Sonnet"
  }
}
```

---

## 格式 D：其他项目启动 JSON（真实项目，中文路径）

**特征**：同格式 A，但含中文路径和完整 workspace
**json_len**：约 914–933 字节
**观测时间**：2026-02-21 09:13:36–09:13:53

```json
{
  "session_id": "85090c42-e47a-4a80-97d3-84aa57f0b953",
  "transcript_path": "C:\\Users\\ASUS\\.claude\\projects\\E-----------------\\85090c42-e47a-4a80-97d3-84aa57f0b953.jsonl",
  "cwd": "E:\\项目\\市调\\呼和浩特烧麦\\论文",
  "model": {
    "id": "claude-sonnet-4-6",
    "display_name": "Sonnet 4.6"
  },
  "workspace": { ... }
}
```

---

## 调试历史

| 日期 | 版本 | 事件 | 结果 |
|------|------|------|------|
| 2026-02-20 | v1 修复 | 假设启动时 stdin 为空 | ❌ 无效，Claude Code 始终发送 JSON |
| 2026-02-20 | v2 修复 | 检测 `cost` 字段存在 | ⚠️ 部分有效，但 cost=0 的初始化调用会误渲染 |
| 2026-02-21 | v3 修复 | 检测 `session_id` + `cost` 双重守卫 | ❌ 过于激进，Stop 事件含 session_id 时会被过滤 |
| 2026-02-21 | v4 修复 | 检测 `total_cost_usd > 0` | ✅ 当前方案，待验证真实 Stop 事件 |

---

## 待捕获格式

- [ ] **真实会话 Stop 事件 JSON**（json_len 预估 > 300，可能含 session_id）
  - 捕获方式：保持 debug 日志开启，等待下一次 Stop 事件
  - 日志路径：`~/.claude/hud-v2-debug.log`

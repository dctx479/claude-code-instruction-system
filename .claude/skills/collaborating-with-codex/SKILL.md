---
name: collaborating-with-codex
description: 多模型协作技能，通过后台 Bash 子进程调用 OpenAI Codex CLI，将代码实现任务并行委托给 Codex，Claude 读取结果后融合分析，实现优势互补
version: 1.0.0
license: MIT
metadata:
  category: development
  tags: [multi-model, codex, parallel, collaboration, cli]
  source: linux.do community workflow
trigger:
  - "/collab-codex"
  - "调用 Codex"
  - "让 Codex 实现"
  - "多模型协作"
  - "并行实现代码"
---

# Collaborating with Codex Skill

> 将 OpenAI Codex CLI 作为并行协作者，Claude 负责理解、规划和融合，Codex 负责代码实现，
> 通过后台进程实现非阻塞并行，最终由 Claude 综合两份输出给出最优方案。

## 契约化设计

### What (输入/输出)

**输入**:
- 当前任务描述（代码实现/重构/调试等）
- 相关代码上下文（文件路径、函数签名、错误信息）
- 可选：期望实现风格或约束条件

**输出**:
- Codex 的实现方案（从 `/tmp/codex_result_*.txt` 读取）
- Claude 自身的分析和方案
- 融合后的最终推荐方案（取两者最优部分）
- 差异分析：两个模型在哪些判断上不同及原因

### When Done (验收标准)

1. Codex CLI 已作为后台进程调用（非阻塞）
2. 等待 Codex 完成后读取结果文件
3. 生成对比分析（Claude方案 vs Codex方案）
4. 给出明确的融合推荐，并说明取舍理由
5. 结果文件已清理（或保留供用户参考）

### What NOT (边界约束)

- 不盲目采用 Codex 输出，Claude 必须审查和融合
- 不在 Codex 未完成时强行读取空文件
- 不将此 Skill 用于非代码类任务（文献综述、数据分析等用其他 Skill）
- 不同时运行超过 3 个 Codex 实例（资源限制）
- 不用于需要访问私有 API 或密钥的场景

---

## 核心理念

### 多模型协作原理

```
Claude (规划/理解/融合)
    ↕ 异步协作
Codex (代码实现/补全)
```

**优势互补**：
- Claude: 强于整体理解、需求分析、代码审查、多方案权衡
- Codex: 强于代码补全、模式匹配、样板代码生成、API 用法

**并行加速**：Claude 思考的同时，Codex 已在生成代码，无需等待。

---

## 工作流程

### Phase 1: 任务评估

判断是否适合启用 Codex 协作：

```markdown
适合协作的任务：
✅ 需要大量样板代码（CRUD、测试用例）
✅ API 用法不确定（需要示例）
✅ 重构大段现有代码
✅ 需要多种实现方案比较

不适合协作的任务：
❌ 简单的单行修改
❌ 纯逻辑推理（无代码输出）
❌ 需要项目深度上下文的架构决策
```

### Phase 2: 并行调用 Codex

```bash
# 生成唯一任务 ID
TASK_ID=$(date +%s)
RESULT_FILE="/tmp/codex_result_${TASK_ID}.txt"
PROMPT_FILE="/tmp/codex_prompt_${TASK_ID}.txt"

# 写入 prompt（包含上下文）
cat > "$PROMPT_FILE" << 'EOF'
[任务描述]
[相关代码上下文]
[具体要求]
EOF

# 后台异步调用 Codex CLI
bash -c "codex --model gpt-4o \
  --input \"$PROMPT_FILE\" \
  --output \"$RESULT_FILE\" \
  2>&1" &

CODEX_PID=$!
echo "Codex started (PID: $CODEX_PID, output: $RESULT_FILE)"
```

### Phase 3: Claude 独立分析

在 Codex 运行期间，Claude 同步进行：
1. 读取相关代码文件
2. 分析需求和约束
3. 构建自己的实现方案
4. 识别潜在边界情况

### Phase 4: 读取 Codex 结果

```bash
# 等待 Codex 完成（带超时）
TIMEOUT=120  # 2分钟超时
ELAPSED=0
while [ ! -f "$RESULT_FILE" ] || [ ! -s "$RESULT_FILE" ]; do
    sleep 2
    ELAPSED=$((ELAPSED + 2))
    if [ $ELAPSED -ge $TIMEOUT ]; then
        echo "Codex timeout after ${TIMEOUT}s"
        kill $CODEX_PID 2>/dev/null
        break
    fi
done

# 读取结果
CODEX_OUTPUT=$(cat "$RESULT_FILE" 2>/dev/null || echo "Codex did not produce output")
```

### Phase 5: 融合分析与推荐

```markdown
## 多模型协作结果

### Claude 方案
[Claude 的实现方案]

### Codex 方案
[从结果文件读取的 Codex 实现]

### 差异分析
| 维度 | Claude | Codex |
|------|--------|-------|
| 代码结构 | ... | ... |
| 错误处理 | ... | ... |
| 性能考虑 | ... | ... |

### 融合推荐
**采用**：[选择哪个方案的哪些部分]
**理由**：[具体取舍原因]

### 最终代码
[融合后的最优实现]
```

### Phase 6: 清理

```bash
# 清理临时文件
rm -f "$RESULT_FILE" "$PROMPT_FILE"
```

---

## 实用模板

### 模板1：代码实现请求

```bash
TASK="实现一个 Redis 缓存中间件，支持 TTL 和 LRU 淘汰策略"
CONTEXT=$(cat src/cache/interface.ts 2>/dev/null || echo "无现有文件")

TASK_ID=$(date +%s)
RESULT_FILE="/tmp/codex_result_${TASK_ID}.txt"

cat > "/tmp/codex_prompt_${TASK_ID}.txt" << EOF
Task: $TASK

Existing code context:
$CONTEXT

Requirements:
- TypeScript with strict types
- Unit testable (dependency injection)
- Handle connection failures gracefully
EOF

bash -c "codex --input /tmp/codex_prompt_${TASK_ID}.txt > $RESULT_FILE 2>&1" &
```

### 模板2：代码审查请求

```bash
TASK_ID=$(date +%s)
RESULT_FILE="/tmp/codex_review_${TASK_ID}.txt"

# 让 Codex 审查指定文件
bash -c "codex 'Review this code for bugs, performance issues, and security concerns' \
  --file src/auth/jwt.ts \
  > $RESULT_FILE 2>&1" &
```

### 模板3：测试生成

```bash
TARGET_FILE="src/utils/validator.ts"
TASK_ID=$(date +%s)
RESULT_FILE="/tmp/codex_tests_${TASK_ID}.txt"

bash -c "codex 'Generate comprehensive unit tests for this file using Jest. Include edge cases and error scenarios.' \
  --file $TARGET_FILE \
  > $RESULT_FILE 2>&1" &
```

---

## 与太一元系统集成

### 与 Orchestrator 集成

在 COLLABORATIVE 策略中，Codex 作为外部协作者参与：

```markdown
## 编排计划 (COLLABORATIVE + Codex)

### 任务分工
- Claude: 需求分析、架构决策、代码审查、结果融合
- Codex: 代码实现、样板生成、API 示例

### 并行执行
1. Claude 读取需求和上下文
2. 同时启动 Codex 后台进程
3. Claude 完成分析时读取 Codex 结果
4. 融合最优方案
```

### 与 Ralph Loop 集成

在 `/ralph` 循环中，可为每次迭代启动 Codex 协作：

```markdown
## Ralph Loop with Codex

迭代 N:
1. 识别当前待实现的功能
2. 启动 Codex 后台进程（如任务为代码实现）
3. Claude 分析依赖和接口
4. 读取 Codex 输出
5. 融合实现，提交代码
6. 进入下一迭代
```

### 与 Autopilot 集成

在 Development 阶段，当 spec-writer 生成规范后：
- 简单实现任务 → Ralph Loop
- 复杂代码实现 → Collaborating with Codex
- 架构决策 → Claude 独立（无需 Codex）

---

## 最佳实践

### Do's

1. **明确划分职责** - Claude 负责理解和融合，Codex 负责实现
2. **提供充分上下文** - Codex 没有项目历史，需要在 prompt 中提供
3. **设置合理超时** - 避免无限等待，建议 60-120 秒
4. **审查 Codex 输出** - 不盲目采用，注意幻觉和错误
5. **记录差异** - 两个模型的不同判断本身就有价值

### Don'ts

1. **不要同步等待** - 使用后台进程，Claude 同时工作
2. **不要跳过融合步骤** - 直接采用 Codex 输出而不审查
3. **不要用于需要实时上下文的任务** - 如需读取项目内多个文件的架构分析
4. **不要在生产环境直接使用 Codex 输出** - 必须经过 Claude 审查

---

## 前置要求

```bash
# 安装 Codex CLI
npm install -g @openai/codex

# 验证安装
codex --version

# 设置 API Key（如未设置）
export OPENAI_API_KEY="your-key-here"
```

---

## 配置参数

```yaml
collaborating_with_codex:
  model: "gpt-4o"              # Codex 使用的模型
  timeout: 120                  # 超时秒数
  max_concurrent: 3             # 最大并发实例数
  result_dir: "/tmp"            # 结果文件目录
  auto_cleanup: true            # 完成后自动清理临时文件

  trigger_conditions:
    - "大量样板代码"
    - "API 用法示例"
    - "重构大段代码"
    - "多方案比较"
```

---

## 更新日志

### 2026-03-01
- 初始版本创建
- 定义契约化设计框架
- 实现后台进程调用模式
- 添加与太一元系统各组件的集成说明

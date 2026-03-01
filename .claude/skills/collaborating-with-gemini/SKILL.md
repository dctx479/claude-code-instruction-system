---
name: collaborating-with-gemini
description: 多模型协作技能，通过后台 Bash 子进程调用 Google Gemini CLI，将分析、写作或代码任务并行委托给 Gemini，Claude 读取结果后融合分析，适合需要长上下文窗口的场景
version: 1.0.0
license: MIT
metadata:
  category: development
  tags: [multi-model, gemini, parallel, collaboration, cli, long-context]
  source: linux.do community workflow
---

# Collaborating with Gemini Skill

> 将 Google Gemini CLI 作为并行协作者，利用 Gemini 的超长上下文窗口（100万+ tokens）处理
> 大型代码库分析、长文档处理等任务，Claude 负责规划和最终融合，实现互补协作。

## 契约化设计

### What (输入/输出)

**输入**:
- 当前任务描述（代码分析/文档处理/长上下文任务等）
- 相关文件或文本内容（可以是大型文件）
- 可选：特定分析角度或输出格式要求

**输出**:
- Gemini 的分析结果（从 `/tmp/gemini_result_*.txt` 读取）
- Claude 自身的分析
- 融合后的综合结论
- 各模型独特见解的对比

### When Done (验收标准)

1. Gemini CLI 已作为后台进程调用（非阻塞）
2. 等待 Gemini 完成后读取结果文件
3. 生成两个模型的对比分析
4. 给出融合推荐，标注哪些见解来自 Gemini
5. 临时文件已处理（清理或保留）

### What NOT (边界约束)

- 不盲目信任 Gemini 输出，Claude 必须审查
- 不在 Gemini 未完成时读取空文件
- 不同时运行超过 2 个 Gemini 实例（API 费用考虑）
- 不将私密信息（密钥、个人数据）发送给 Gemini
- 不用于需要本地文件系统操作的任务

---

## 核心理念

### Gemini 的独特优势

```
Gemini 适合的场景：
🔷 超长上下文：整个代码库一次性分析
🔷 多模态：代码 + 图表 + 文档混合分析
🔷 大型文档：论文、报告、日志文件全文处理
🔷 跨文件理解：同时加载多个文件进行关联分析
```

### 与 Codex 的分工

| 任务类型 | 推荐协作者 |
|----------|-----------|
| 代码实现、样板生成 | Codex |
| 大型代码库分析 | Gemini |
| 长文档摘要/理解 | Gemini |
| API 用法示例 | Codex |
| 多文件关联分析 | Gemini |
| 测试用例生成 | Codex |

---

## 工作流程

### Phase 1: 任务评估

判断是否适合启用 Gemini 协作：

```markdown
适合 Gemini 协作的任务：
✅ 需要分析整个代码库（>50个文件）
✅ 处理超长文档（>100K tokens）
✅ 多文件关联分析（找出跨文件的 bug 或模式）
✅ 需要额外视角验证 Claude 的判断

不适合的任务：
❌ 需要执行命令或修改文件（Gemini CLI 为只读分析）
❌ 简单的单文件操作
❌ 需要实时状态的任务
```

### Phase 2: 并行调用 Gemini

```bash
# 生成唯一任务 ID
TASK_ID=$(date +%s)
RESULT_FILE="/tmp/gemini_result_${TASK_ID}.txt"
PROMPT_FILE="/tmp/gemini_prompt_${TASK_ID}.txt"

# 写入 prompt
cat > "$PROMPT_FILE" << 'EOF'
[任务描述]
[分析要求]
[期望输出格式]
EOF

# 后台异步调用 Gemini CLI
# 方式1：使用 prompt 文件
bash -c "gemini --model gemini-2.0-flash-exp \
  --prompt-file \"$PROMPT_FILE\" \
  > \"$RESULT_FILE\" 2>&1" &

GEMINI_PID=$!
echo "Gemini started (PID: $GEMINI_PID, output: $RESULT_FILE)"

# 方式2：直接传入文件进行分析
bash -c "gemini 'Analyze this codebase and identify architectural patterns, potential issues, and improvement opportunities' \
  --file src/ \
  > \"$RESULT_FILE\" 2>&1" &
```

### Phase 3: Claude 独立分析

在 Gemini 运行期间，Claude 同步进行：
1. 处理当前上下文中可用的信息
2. 建立自己的分析框架
3. 识别需要 Gemini 大上下文窗口才能解答的问题

### Phase 4: 读取 Gemini 结果

```bash
# 等待 Gemini 完成（带超时）
TIMEOUT=180  # Gemini 大上下文处理可能需要更长时间
ELAPSED=0

echo "Waiting for Gemini (timeout: ${TIMEOUT}s)..."
while kill -0 $GEMINI_PID 2>/dev/null; do
    sleep 3
    ELAPSED=$((ELAPSED + 3))
    echo -n "."
    if [ $ELAPSED -ge $TIMEOUT ]; then
        echo "\nGemini timeout after ${TIMEOUT}s"
        kill $GEMINI_PID 2>/dev/null
        break
    fi
done
echo ""

# 读取结果
if [ -f "$RESULT_FILE" ] && [ -s "$RESULT_FILE" ]; then
    GEMINI_OUTPUT=$(cat "$RESULT_FILE")
    echo "Gemini completed successfully ($(wc -c < $RESULT_FILE) bytes)"
else
    GEMINI_OUTPUT="Gemini did not produce usable output"
fi
```

### Phase 5: 融合分析

```markdown
## 多模型协作分析报告

### 任务背景
[当前分析的任务和目标]

### Claude 分析
[基于当前上下文的 Claude 分析]

### Gemini 分析
[从结果文件读取的 Gemini 分析]

### 独特见解对比
| 维度 | Claude | Gemini |
|------|--------|--------|
| 架构评估 | ... | ... |
| 风险识别 | ... | ... |
| 改进建议 | ... | ... |

### Gemini 的额外洞察
（仅 Gemini 基于大上下文窗口发现的内容）
- [见解1]
- [见解2]

### 综合结论
[融合两个模型的最终结论和行动建议]
```

### Phase 6: 清理

```bash
# 清理临时文件
rm -f "$RESULT_FILE" "$PROMPT_FILE"
```

---

## 实用模板

### 模板1：代码库全局分析

```bash
TASK_ID=$(date +%s)
RESULT_FILE="/tmp/gemini_analysis_${TASK_ID}.txt"

# 让 Gemini 分析整个 src 目录
bash -c "gemini \
  'Analyze the entire codebase. Identify:
  1. Overall architecture pattern
  2. Potential circular dependencies
  3. Code smells and anti-patterns
  4. Security vulnerabilities
  5. Performance bottlenecks
  Provide specific file:line references for all findings.' \
  --file src/ \
  > $RESULT_FILE 2>&1" &

echo "Gemini analyzing codebase in background (PID: $!)"
```

### 模板2：大型文档理解

```bash
TASK_ID=$(date +%s)
RESULT_FILE="/tmp/gemini_doc_${TASK_ID}.txt"

# 处理大型技术文档
bash -c "gemini \
  'Summarize this technical document. Extract:
  1. Core concepts and definitions
  2. Key algorithms or processes
  3. Important constraints and requirements
  4. Implementation recommendations' \
  --file docs/technical-spec.pdf \
  > $RESULT_FILE 2>&1" &
```

### 模板3：跨文件 Bug 追踪

```bash
TASK_ID=$(date +%s)
RESULT_FILE="/tmp/gemini_bug_${TASK_ID}.txt"

ERROR_MSG="TypeError: Cannot read property 'user' of undefined at auth.js:45"

bash -c "gemini \
  \"Trace the root cause of this error across the entire codebase:
  $ERROR_MSG

  Find all places where the 'user' property is set, passed, or expected.
  Identify the exact location where it becomes undefined.\" \
  --file src/ \
  > $RESULT_FILE 2>&1" &
```

### 模板4：多版本对比分析

```bash
TASK_ID=$(date +%s)
RESULT_FILE="/tmp/gemini_compare_${TASK_ID}.txt"

bash -c "gemini \
  'Compare these two implementations and evaluate:
  1. Correctness (edge cases, error handling)
  2. Performance characteristics
  3. Maintainability
  4. Which is better and why' \
  --file implementation-v1.ts \
  --file implementation-v2.ts \
  > $RESULT_FILE 2>&1" &
```

---

## 与太一元系统集成

### 与 Orchestrator 集成

在 COLLABORATIVE 策略中，Gemini 提供大上下文支持：

```markdown
## 编排计划 (COLLABORATIVE + Gemini)

### 适用场景
- 大型代码库重构：Gemini 分析全局，Claude 执行局部
- 文档生成：Gemini 理解完整代码，Claude 撰写规范

### 任务分工
- Gemini: 全局上下文扫描（并行后台）
- Claude: 当前任务执行（主线程）
- 融合: Claude 读取 Gemini 洞察后更新方案
```

### 与 Parallel Explore 集成

当探索多个技术方案时，Gemini 可分析历史实现：

```markdown
## Parallel Explore + Gemini

Phase 1 前：
1. 启动 Gemini 分析现有代码库，理解当前实现
2. Claude 开始定义探索方案
3. Gemini 完成后，将历史经验注入到方案定义中
```

### 与 Deep Research 集成

```markdown
## Deep Research + Gemini

当研究主题有大量相关代码或文档时：
1. Deep Research 收集相关技术文章
2. Gemini 批量处理长文档摘要（后台）
3. Claude 综合 Gemini 摘要和 web 搜索结果
```

---

## 最佳实践

### Do's

1. **充分利用大上下文** - 一次性提供完整的代码库或文档
2. **明确分析角度** - 告诉 Gemini 从哪个维度分析
3. **设置合适超时** - 大上下文可能需要 2-3 分钟
4. **验证 Gemini 输出** - 大上下文不保证准确，需 Claude 审查
5. **保存有价值的分析** - 将 Gemini 发现记录到 memory/

### Don'ts

1. **不要发送敏感数据** - API 密钥、个人信息等
2. **不要期望实时更新** - Gemini CLI 为一次性查询
3. **不要超过 API 限制** - 注意 rate limit 和费用
4. **不要跳过审查** - Gemini 的大上下文分析也可能有错误

---

## 前置要求

```bash
# 安装 Gemini CLI
npm install -g @google/gemini-cli
# 或
pip install google-generativeai

# 验证安装
gemini --version

# 设置 API Key
export GOOGLE_API_KEY="your-key-here"
# 或
export GEMINI_API_KEY="your-key-here"
```

---

## 配置参数

```yaml
collaborating_with_gemini:
  model: "gemini-2.0-flash-exp"  # 推荐模型（大上下文）
  timeout: 180                    # 超时秒数（大文件需要更长）
  max_concurrent: 2               # 最大并发实例数（费用考虑）
  result_dir: "/tmp"              # 结果文件目录
  auto_cleanup: true              # 完成后自动清理临时文件

  trigger_conditions:
    - "整个代码库分析"
    - "超长文档处理"
    - "跨文件 bug 追踪"
    - "多文件关联分析"

  vs_codex:
    use_gemini_when: "large context, document analysis, cross-file understanding"
    use_codex_when: "code generation, API examples, unit test creation"
```

---

## 更新日志

### 2026-03-01
- 初始版本创建
- 定义契约化设计框架
- 实现后台进程调用模式
- 明确与 Codex Skill 的分工
- 添加与太一元系统各组件的集成说明

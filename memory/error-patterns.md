# 错误模式库 (Error Patterns)

> 记录常见错误模式及其解决方案，防止重复犯错

---

## 错误分类

### 按严重程度
| 级别 | 说明 | 处理策略 |
|------|------|----------|
| 🔴 Critical | 导致任务完全失败 | 立即停止，请求人工介入 |
| 🟠 High | 严重影响任务质量 | 尝试恢复，记录并报告 |
| 🟡 Medium | 部分影响，可绕过 | 自动重试或替代方案 |
| 🟢 Low | 轻微问题 | 记录后继续 |

### 按错误类型
| 类型 | 说明 | 常见原因 |
|------|------|----------|
| Agent失败 | Agent执行出错 | 超时、模型错误、权限问题 |
| 策略错误 | 编排策略选择不当 | 任务分析不准确 |
| 依赖错误 | 任务依赖处理错误 | 依赖图分析错误 |
| 集成错误 | 结果整合失败 | 输出格式不兼容 |
| 资源错误 | 资源不足 | Token超限、超时 |

---

## 已知错误模式

### EP-006: 跨会话 Edit 失败 — "File has not been read yet"

**模式描述**:
在上下文压缩（context compaction）后启动新会话时，尝试 Edit 旧会话中已 Read 过的文件，报错 `File has not been read yet`。

**触发条件**:
- 对话上下文被压缩/摘要
- 新会话中直接 Edit 文件（未在本次会话中 Read）
- 即使摘要中明确提到"已读取该文件"

**解决方案**:
```bash
# ❌ 错误：直接在新会话中 Edit 旧会话读过的文件
Edit(file_path="C:/...", old_string="...", new_string="...")
# → File has not been read yet

# ✅ 正确：新会话中先 Read，再 Edit
Read(file_path="C:/...")
Edit(file_path="C:/...", old_string="...", new_string="...")
```

**预防措施**:
- 每次新会话开始，**必须先 Read 所有需要编辑的文件**
- 从对话摘要继续工作时，把"读取文件"作为第一步
- 批量修改多个文件时，可并行 Read 所有文件后再批量 Edit

---

### EP-004: Windows Hook "cannot execute binary file"

**模式描述**:
Claude Code 的 hook 或 statusLine 命令在 Windows 上执行时报 `cannot execute binary file`，命令静默失败，statusline 不显示或 hook 不执行。

**触发条件**:
- hook/statusLine 命令格式为 `"bash.exe" "script.sh"`（包含 bash 可执行文件路径）
- Claude Code 在 Windows 上检测到 `.sh` 文件时自动在命令前追加 `bash `
- 结果：`bash "bash.exe" "script.sh"` → Cygwin bash 把 PE 二进制当脚本执行 → 失败

**解决方案**:
```json
// ❌ 错误格式（触发双重 bash 问题）
"command": "\"I:\\APP\\Git\\usr\\bin\\bash.exe\" \"script.sh\""

// ✅ 正确格式（以 bash 开头，Claude Code 不再追加）
"command": "bash \"C:\\Users\\...\\script.sh\""

// ✅ 或直接引用脚本（依赖 shebang #!/bin/bash）
"command": "\"C:\\Users\\...\\script.sh\""
```

**预防措施**:
- Windows 上所有 hook/statusLine 命令统一以 `bash "script.sh"` 格式书写
- 写完配置后运行脚本直接测试一次

---

### EP-005: set -eo pipefail + 外部工具缺失 → 脚本静默崩溃

**模式描述**:
脚本使用 `set -eo pipefail`，内部调用了未安装的外部工具（如 jq、python 等），工具缺失时返回 exit 127，`pipefail` 捕获后脚本立即静默退出，无任何错误输出。

**触发条件**:
- `set -eo pipefail` 已启用
- 调用外部工具（jq、curl、python 等）无 `|| fallback` 保护
- 工具未安装或不在 PATH

**解决方案**:
```bash
# ❌ 危险：jq 缺失时 pipefail 捕获 exit 127，脚本立即退出
value=$(echo "$JSON" | jq -r '.field' 2>/dev/null)

# ✅ 安全：|| fallback 让整体表达式成功，pipefail 不会触发
value=$(echo "$JSON" | jq -r '.field' 2>/dev/null || echo "default")
```

**预防措施**:
- 脚本顶部用 `command -v tool &>/dev/null || { echo "tool missing"; exit 1; }` 显式检查依赖
- 所有外部工具调用加 `|| fallback_value`
- 升级脚本时检查新增的外部依赖

---

### EP-001: Agent超时无响应

**模式描述**:
Agent长时间无响应，导致任务卡住

**触发条件**:
- 任务过于复杂
- 网络问题
- 模型负载高

**解决方案**:
```
1. 设置合理超时 (默认120秒)
2. 超时后检查部分输出
3. 尝试分解为更小任务
4. 切换到更快的模型
```

**预防措施**:
- 预估任务复杂度，设置合适超时
- 大任务预先分解
- 监控Agent进度

---

### EP-002: 并行任务冲突

**模式描述**:
多个并行Agent同时修改同一资源

**触发条件**:
- 任务分解不充分
- 资源依赖分析遗漏

**解决方案**:
```
1. 检测资源冲突
2. 转换为串行执行
3. 使用锁机制
4. 合并冲突结果
```

**预防措施**:
- 任务分解时分析资源依赖
- 并行任务使用独立资源

---

### EP-003: 循环依赖

**模式描述**:
任务间形成循环依赖，无法执行

**触发条件**:
- 依赖关系分析错误
- 任务设计不当

**解决方案**:
```
1. 检测循环依赖
2. 打破循环 (合并任务或重新设计)
3. 报告错误给用户
```

**预防措施**:
- 构建DAG并验证无环
- 任务设计遵循单向依赖原则

---

### EP-004: 输出格式不兼容

**模式描述**:
Agent输出格式与预期不符，无法整合

**触发条件**:
- Agent理解偏差
- 提示词不清晰

**解决方案**:
```
1. 解析并转换格式
2. 要求Agent重新输出
3. 使用后处理Agent
```

**预防措施**:
- 明确指定输出格式
- 使用示例说明
- 添加格式验证

---

### EP-005: Token超限

**模式描述**:
任务或上下文超过Token限制

**触发条件**:
- 输入数据过大
- 任务描述冗长
- 积累过多上下文

**解决方案**:
```
1. 分块处理大数据
2. 精简任务描述
3. 使用/clear清理上下文
4. 使用子Agent隔离上下文
```

**预防措施**:
- 监控Token使用
- 及时清理无用上下文
- 大任务预先分块

---

### EP-007: 自动生成 Skills 导致歧义永久化

**模式描述**:
在数据分析等知识域场景中，让 Claude 自动生成指标定义、实体映射或查询模板，反而会将现有数据中的歧义永久化到 Skill 中，导致准确率不升反降。

**触发条件**:
- 让 AI 通过扫描现有仪表盘、SQL 脚本、notebook 自动提取知识
- 现有数据本身存在歧义（如同一术语在不同地方有不同含义）
- 缺乏人工审核和歧义消解步骤

**核心问题**:
| 期望 | 实际 |
|------|------|
| AI 学习到正确的知识模式 | AI 学习到数据中已存在的混乱模式 |
| 自动化减少维护成本 | 歧义永久化，准确率下降 |
| 生成的 Skill 可直接使用 | 需要大量人工清理和消歧 |

**实际案例** (来源: Anthropic 数据分析实践):
- Anthropic 初期让 Claude 自动扫描 1000+ 仪表盘生成 metric 定义
- 结果："活跃用户"在 10 个不同仪表盘里有 10 种统计口径
- Claude 生成的 Skill 无法消解这种歧义，反而将歧义固化
- 准确率从 21% 仅提升到 ~40%，远低于人工设计的 95%

**正确做法** (Pairwise Skills 模式):
1. **人工设计语义层** — 由资深分析师定义权威的指标和实体
2. **显式歧义消解表** — 列出所有可能混淆的术语及其正确含义
3. **Skill 指向语义层** — AI 的职责是路由到正确实体，而非自己定义实体
4. **强制来源标注** — 每次回答必须附带数据来源和置信度

**解决方案**:
```markdown
# ❌ 错误：让 AI 自动生成知识
"扫描所有 SQL 文件，生成用户指标的 Skill"
→ 结果：50 种"用户"定义混在一起

# ✅ 正确：人工设计语义层 + AI 负责路由
1. 资深分析师定义 5 种"用户"实体（注册/活跃/付费/月活/日活）
2. 创建歧义消解表：用户问"用户数"时，必须先确认指哪一种
3. Skill 强制执行澄清流程
4. AI 的职责：把问题映射到 5 种实体之一，而非自己定义第 6 种
```

**预防措施**:
- 知识域 Skill（数据分析/API 文档/产品知识库）必须由领域专家设计核心结构
- AI 可以辅助（如生成查询模板、编写文档），但不能自主定义实体语义
- 任何自动生成的 Skill 必须经过人工审核和歧义消解
- 使用离线评估集验证准确率，准确率 <90% 的 Skill 不可上线

**适用范围**:
- ✅ 数据分析 Skill — 必须人工设计语义层
- ✅ API 文档 Skill — 必须基于权威文档，而非自动推断
- ✅ 业务术语 Skill — 必须有明确的 glossary
- ⚠️ 代码模式 Skill — 可以部分自动提取，但需人工验证
- ✅ 通用编程 Skill — 可以完全自动生成（如 PyTorch/pandas 用法）

**反模式识别**:
```
如果你听到这些说法，立即警惕：
- "让 Claude 自动学习我们的数据模式"
- "把所有历史查询喂给 AI，让它总结规律"
- "AI 应该能从数据中推断出业务逻辑"

数据分析的核心挑战不是信息获取，而是歧义消解。
自动生成只会放大歧义，不会解决歧义。
```

> 来源: Anthropic 数据分析博客 — "We learned the hard way that auto-generating metric definitions just perpetuates existing ambiguity"

---

## 自动检测规则

```python
# 错误模式检测器
ERROR_PATTERNS = {
    "EP-001": {
        "detect": lambda log: "timeout" in log.lower(),
        "action": "retry_with_smaller_task"
    },
    "EP-002": {
        "detect": lambda log: "conflict" in log.lower(),
        "action": "serialize_tasks"
    },
    "EP-003": {
        "detect": lambda log: "circular" in log.lower(),
        "action": "break_cycle"
    },
    "EP-004": {
        "detect": lambda log: "format" in log.lower() and "error" in log.lower(),
        "action": "reformat_output"
    },
    "EP-005": {
        "detect": lambda log: "token" in log.lower() and "limit" in log.lower(),
        "action": "chunk_and_retry"
    }
}
```

---

## 新增错误模式

<!-- 运行时发现的新错误模式将自动添加在这里 -->


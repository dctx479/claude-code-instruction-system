# SPEC: 双系统决策与自进化机制

> 2026-11-23 实现状态见 [实施与验收记录](../docs/IMPROVEMENT-IMPLEMENTATION.md)，执行接口以 [运行时契约](SPEC-improvement-runtime.md) 为准。下文保留原始方案背景；示例路径、自动执行、外部安装与收益数字不视为已验证事实。

## 一、背景与目标

### 问题陈述
当前Agent架构存在三个效率瓶颈：
1. **决策成本高**：所有判断都调用大模型，简单操作也需7+秒
2. **无经验积累**：同一任务执行100次，第100次仍可能犯第1次的错
3. **适应成本高**：每接入新工具/环境，需重新"教学"

### 参考项目
**Agnes Harness** (github.com/AgnesAI-Labs/agnes-harness)
- 决策速度提升14.3倍（7.6s → 0.53s）
- 成本降至1/27
- Apache 2.0许可证
- 已获2.1k GitHub Stars

### 核心机制
1. **Sys1双系统决策**：9B模型处理常规，大模型处理复杂推理
2. **TTT（测试时训练）**：临时适应新任务，完成后参数恢复
3. **RSI（递归自我改进）**：复盘→验证→版本化Playbook
4. **插件化架构**：工具、工作流、Skills封装为插件

### 目标
- 常规决策延迟降至 <1秒
- 重复任务成功率从首次的60%提升到80%+
- 新环境适应时间从2小时降至30分钟

---

## 二、方案对比

### 方案A：规则引擎 + 经验库（推荐）

#### A1. 轻量级决策路由
```python
# agents/decision-router.md

## 职责
在调用大模型前，先用规则引擎判断是否可用轻量方案

## 决策树

### 1. 文本处理类
- 文件行数统计 → `wc -l`
- 简单grep → `grep -r pattern`
- JSON解析 → `jq`

### 2. 重复模式识别
- 检查memory/playbooks/是否有匹配流程
- 检查.claude/session-history.json最近10次操作
- 若命令相似度>85%，直接复用

### 3. 已知错误规避
- 检查memory/failures/是否有相同错误记录
- 若存在，直接返回已知解决方案

### 4. 兜底策略
- 以上规则均不匹配时，调用大模型
- 记录决策路径供后续学习

## 实现
```python
# .claude/agents/router/decision_engine.py
import re
from pathlib import Path
from difflib import SequenceMatcher

class DecisionRouter:
    def __init__(self):
        self.playbooks = self.load_playbooks()
        self.session_history = self.load_history()

    def route(self, task_description, context):
        """路由决策"""

        # 规则1：简单命令直接映射
        if simple_cmd := self.match_simple_command(task_description):
            return {
                "decision": "execute_direct",
                "command": simple_cmd,
                "confidence": 0.95,
                "reasoning": "匹配简单命令模式"
            }

        # 规则2：检查Playbook
        if playbook := self.match_playbook(task_description):
            return {
                "decision": "use_playbook",
                "playbook": playbook,
                "confidence": 0.90,
                "reasoning": f"匹配已知流程: {playbook['name']}"
            }

        # 规则3：检查历史重复
        if similar_task := self.find_similar_task(task_description):
            return {
                "decision": "repeat_previous",
                "reference": similar_task,
                "confidence": 0.85,
                "reasoning": "与最近任务相似度87%"
            }

        # 规则4：检查已知失败
        if known_failure := self.check_known_failures(task_description):
            return {
                "decision": "avoid_known_failure",
                "alternative": known_failure['solution'],
                "confidence": 0.80,
                "reasoning": f"避免已知错误: {known_failure['error']}"
            }

        # 兜底：调用大模型
        return {
            "decision": "delegate_to_llm",
            "confidence": 0.0,
            "reasoning": "无匹配规则，需要复杂推理"
        }

    def match_simple_command(self, task):
        """匹配简单命令"""
        patterns = {
            r"统计.*文件.*行数": "find . -type f -name '{pattern}' | xargs wc -l",
            r"查找.*包含.*的文件": "grep -r '{keyword}' .",
            r"列出.*最近修改": "ls -lt | head -n {count}",
        }

        for pattern, cmd_template in patterns.items():
            if re.search(pattern, task):
                return self.fill_template(cmd_template, task)
        return None

    def match_playbook(self, task):
        """匹配Playbook"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        # 简化实现：关键词匹配
        keywords = extract_keywords(task)
        for playbook in self.playbooks:
            pb_keywords = playbook['keywords']
            overlap = len(set(keywords) & set(pb_keywords))
            if overlap >= 2:
                return playbook
        return None

    def find_similar_task(self, task):
        """查找相似历史任务"""
        for history in self.session_history[-20:]:  # 最近20次
            similarity = SequenceMatcher(None, task, history['task']).ratio()
            if similarity > 0.85:
                return history
        return None
```

#### A2. 经验库（Playbook系统）
```markdown
# memory/playbooks/install-global/latest.md
---
name: install-global
version: 1.2
keywords: [install, global, 安装, 全局]
success_rate: 0.92
last_updated: 2024-01-15
---

## 适用场景
用户请求"全局安装"、"安装到~/.claude"

## 前置检查
- [ ] 目标路径不存在或已备份
- [ ] 有写入权限
- [ ] Python 3.10+

## 执行步骤
1. Dry-run验证：
   ```bash
   python scripts/install-global.py --dry-run --target ~/.claude
   ```

2. 检查输出中的WARNING

3. 确认后执行：
   ```bash
   python scripts/install-global.py --target ~/.claude
   ```

4. 验证安装：
   ```bash
   ls -la ~/.claude/CLAUDE.md
   ```

## 已知失败模式
- Windows路径包含中文 → 使用短路径或英文目录
- 权限不足 → 检查~/.claude所有者

## 置信度
基于15次成功执行，2次失败（已修复）
```

#### A3. 失败记忆系统
```markdown
# memory/failures/backup-collision.md
---
name: backup-collision
error_pattern: "FileExistsError.*backup.*\\d{8}T\\d{6}"
occurrences: 3
last_seen: 2024-01-10
status: resolved
---

## 现象
Windows下快速连续备份生成相同文件名

## 根因
Windows时钟分辨率~15.6ms，time.time()可能返回相同值

## 解决方案
```python
# 在时间戳后追加递增序号
timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
counter = 0
while (backup_dir / f"{timestamp}_{counter}").exists():
    counter += 1
final_name = f"{timestamp}_{counter}"
```

## 验证
commit a590f8a 修复，test_frozen_clock_collision 通过

## 触发条件
- Windows系统
- 循环中快速调用备份（<16ms间隔）

## 预防
所有时间戳命名需考虑碰撞，建议追加随机后缀或序号
```

**依赖**：
- Python标准库
- 可选：scikit-learn（TF-IDF匹配，非必需）

**风险**：RISK-MEDIUM
- 规则库需持续维护
- 关键词匹配可能不精确

**投入**：约3-5天
- Day 1-2: 实现决策路由引擎
- Day 3: 迁移3个现有流程到Playbook
- Day 4: 实现失败记忆系统
- Day 5: 集成测试

---

### 方案B：完整引入Agnes Harness（备选）

#### 架构
```
Agnes Harness
├── Core System
│   ├── Agnes Sys1.0 (9B决策模型)
│   ├── TTT Module (测试时训练)
│   ├── RSI Engine (递归自我改进)
│   └── MHS (模型硬件标准)
├── Plugin System
│   ├── Business Tools
│   ├── Model Adapters
│   ├── Workflow Templates
│   └── Skills Library
└── Infrastructure
    ├── Version Management
    ├── Sandbox Environment
    └── State Persistence
```

#### 安装步骤
```bash
# 1. 克隆仓库
git clone https://github.com/AgnesAI-Labs/agnes-harness.git
cd agnes-harness

# 2. 安装依赖（需要Node.js 24.10+, pnpm 10.34.5+）
pnpm install

# 3. 下载Agnes Sys1.0模型（9B参数）
pnpm run download-model

# 4. 配置模型API
cat > .env <<EOF
# 大模型配置（用于System 2）
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-...
LLM_MODEL=claude-sonnet-4

# Agnes Sys1.0配置（用于System 1）
SYS1_MODEL_PATH=./models/agnes-sys1-1.0.gguf
SYS1_DEVICE=cpu  # 或 cuda
EOF

# 5. 启动服务
pnpm start

# 6. 配置Claude Code集成
cat > ~/.claude/plugins/agnes-harness.json <<EOF
{
  "name": "agnes-harness",
  "type": "mcp-server",
  "url": "http://localhost:3000",
  "capabilities": ["decision", "memory", "plugin-management"]
}
EOF
```

#### 核心能力

##### 1. Sys1决策加速
```javascript
// Agnes Sys1.0的决策示例
const task = {
  type: "file_operation",
  description: "统计src/目录下所有.py文件的行数",
  context: { cwd: "/project" }
};

// System 1快速判断（0.53秒）
const sys1Decision = await agnesSys1.decide(task);
// 返回: {
//   action: "bash",
//   command: "find src -name '*.py' | xargs wc -l",
//   confidence: 0.94
// }

// 仅当confidence < 0.7时才调用System 2（大模型）
if (sys1Decision.confidence < 0.7) {
  const sys2Decision = await callLLM(task);
}
```

##### 2. TTT快速适应
```javascript
// 任务开始前的突击训练
await agnesTTT.adapt({
  task: "操作新设备: 工业称重台",
  examples: [
    { input: "读取重量", output: "调用/api/scale/read" },
    { input: "归零", output: "调用/api/scale/tare" }
  ],
  duration: 30  // 30秒训练
});

// 训练完成后，Sys1可以识别设备特定模式
// 任务完成后，参数自动恢复
```

##### 3. RSI自我改进
```javascript
// 任务完成后自动复盘
const taskResult = {
  success: true,
  duration: 480,  // 8分钟
  steps: [...],
  errors: [
    { step: 3, reason: "称重台未稳定就读数", retry: true }
  ]
};

// RSI分析并生成改进建议
const improvement = await agnesRSI.analyze(taskResult);
// 返回: {
//   issue: "未等待设备稳定",
//   solution: "读数前检查stability_flag",
//   verification: "在仿真环境测试3次",
//   confidence: 0.89
// }

// 验证通过后写入Playbook
if (await verify(improvement.solution)) {
  await agnesRSI.savePlaybook({
    name: "device-checkin-v2",
    improvements: [improvement]
  });
}
```

##### 4. 插件系统
```typescript
// 创建自定义插件
interface AgnesPlugin {
  name: string;
  version: string;
  capabilities: string[];

  async onTaskStart(task: Task): Promise<void>;
  async onTaskComplete(result: TaskResult): Promise<void>;
  async onError(error: Error): Promise<void>;
}

// 审稿插件示例
class ProofreadPlugin implements AgnesPlugin {
  name = "proofreader";
  version = "1.0.0";
  capabilities = ["text-analysis"];

  async onTaskStart(task: Task) {
    if (task.type === "proofread") {
      return this.checkDocument(task.content);
    }
  }

  private checkDocument(content: string) {
    // 检查错别字、语病等
    return {
      errors: [...],
      suggestions: [...]
    };
  }
}

// 注册插件
agnes.registerPlugin(new ProofreadPlugin());
```

#### 优势
1. **性能显著**：
   - 决策速度快14.3倍
   - 成本降至1/27
   - 任务耗时减少32.9%

2. **功能完整**：
   - 开箱即用的决策加速
   - 自带经验积累机制
   - 完善的插件生态

3. **持续维护**：
   - 官方团队维护
   - 有技术报告支撑
   - 社区活跃（2.1k stars）

4. **硬件支持**：
   - MHS标准可接入物理设备
   - 支持机器人、传感器等

#### 劣势
1. **资源开销**：
   - 9B模型需要GPU（或较慢的CPU推理）
   - 内存占用约18GB（FP16）
   - 存储占用约18GB

2. **复杂度高**：
   - 需要维护独立服务
   - 多组件协调（Sys1 + LLM + TTT + RSI）
   - 故障排查困难

3. **适配成本**：
   - 需要将太一现有Agent迁移到Agnes插件
   - Skill系统需重构
   - Hook机制需适配

4. **过度设计**：
   - MHS硬件标准对太一无用（软件编排项目）
   - TTT机制对常规编码任务收益有限

**风险**：RISK-HIGH
- 引入9B模型的运行成本可能超过节省的API成本
- 多组件故障风险高
- 迁移成本大（估计2-3周全职工作）

**投入**：
- 初期：1-2周（安装、配置、验证）
- 迁移：2-3周（适配现有Agent/Skill）
- 维护：每周约4小时（监控、更新）

---

### 方案C：混合方案（中期目标）

在方案A运行稳定后，可选择性引入Agnes的部分能力：

#### C1. 自研轻量决策模型
```python
# 不用9B通用模型，训练专用决策模型（1B参数）
# 只判断：direct_execute | use_playbook | call_llm

# 训练数据来自方案A积累的决策日志
training_data = load_decision_logs("memory/decisions/*.jsonl")

# 使用LoRA微调小模型
model = finetune_decision_model(
    base_model="Qwen2.5-1B",
    training_data=training_data,
    task="decision-routing"
)

# 推理成本：~50ms, ~0.0001$/次
```

#### C2. 借鉴RSI复盘机制
```python
# .claude/skills/task-retrospective.md

## 触发时机
- 任务失败时自动触发
- 任务成功但耗时>预期2倍时触发
- 用户手动调用 `/retrospective`

## 分析维度
1. 时间分布：哪一步最耗时？
2. 错误模式：是否为已知错误？
3. 工具选择：是否有更优工具？
4. 上下文利用：是否遗漏关键信息？

## 输出
- 问题根因
- 改进建议（2-3条）
- 是否值得写入Playbook（置信度>0.8）

## 验证
改进建议需在test/下验证3次成功后才能持久化
```

#### C3. 插件版本管理
```bash
# memory/playbooks/结构调整
memory/playbooks/
├── install-global/
│   ├── v1.0.md  # 初始版本
│   ├── v1.1.md  # 修复Windows路径
│   ├── v1.2.md  # 增加权限检查
│   └── latest -> v1.2.md
├── backup-strategy/
│   └── ...
└── REGISTRY.json  # 版本注册表

# REGISTRY.json
{
  "install-global": {
    "latest": "v1.2",
    "stable": "v1.1",
    "versions": {
      "v1.0": { "created": "2024-01-01", "deprecated": true },
      "v1.1": { "created": "2024-01-10", "stable": true },
      "v1.2": { "created": "2024-01-15", "experimental": true }
    }
  }
}
```

**风险**：RISK-MEDIUM
- 需要分阶段实施（6-12个月）
- 训练决策模型需要积累足够数据

**投入**：
- C1: 1-2周（需机器学习专长）
- C2: 3-5天
- C3: 2-3天

---

## 三、推荐方案

### 短期（1-2个月）：方案A
理由：
1. 符合太一"简单优先"原则
2. 无需GPU等重资源
3. 可快速验证效果
4. 完全自主可控

### 中期（6-12个月）：方案C
前提条件：
- 方案A已积累500+决策日志
- 识别出10+高频Playbook
- 有明确的性能瓶颈

实施路径：
- 先实施C2（复盘机制）和C3（版本管理）
- 评估是否需要C1（决策模型）

### 长期：视情况考虑方案B
仅在以下情况考虑：
- 太一需要支持硬件设备（机器人、IoT）
- 决策延迟成为核心瓶颈（>50%任务需快速决策）
- 有专职团队维护Agnes系统

**不推荐方案B的原因**：
1. 太一是编排工具，非实时控制系统
2. 9B模型运行成本可能>节省的API成本
3. 过度工程化，违背"简单优先"

---

## 四、详细实施计划（方案A）

### Phase 1: 决策路由引擎（1周）

#### Day 1-2: 核心引擎
```bash
# 创建目录结构
mkdir -p .claude/agents/router
mkdir -p memory/playbooks
mkdir -p memory/failures

# 实现决策引擎
touch .claude/agents/router/decision_engine.py
touch .claude/agents/router/pattern_matcher.py
touch .claude/agents/router/similarity.py
```

**交付物**：
- `decision_engine.py`：核心路由逻辑
- `pattern_matcher.py`：简单命令匹配
- `similarity.py`：任务相似度计算
- 单元测试：`tests/agents/test_decision_router.py`

#### Day 3: Playbook系统
```bash
# 迁移现有流程
memory/playbooks/
├── install-global/
│   └── latest.md
├── backup-strategy/
│   └── latest.md
└── rule-audit/
    └── latest.md
```

**交付物**：
- 3个Playbook模板
- Playbook加载器：`memory/playbooks/loader.py`
- 匹配算法：关键词 + TF-IDF

#### Day 4: 失败记忆
```bash
# 迁移已知失败案例
memory/failures/
├── backup-collision.md
├── windows-path-encoding.md
└── permission-denied.md
```

**交付物**：
- 失败案例模板
- 自动记录Hook：`.claude/hooks/on-task-failure.py`
- 查询接口：`memory/failures/query.py`

#### Day 5: 集成测试
```bash
# 端到端测试
python -m pytest tests/agents/test_decision_router.py -v
python scripts/test-decision-scenarios.py
```

**验收标准**：
- [ ] 10个简单命令100%匹配成功
- [ ] 3个Playbook场景正确路由
- [ ] 失败记忆能阻止已知错误重现

---

### Phase 2: 经验积累（持续）

#### 决策日志收集
```python
# .claude/hooks/post-decision.py
import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("memory/decisions/decision-log.jsonl")

def log_decision(decision, outcome):
    """记录每次决策及结果"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "task": decision["task"],
        "decision": decision["route"],
        "confidence": decision["confidence"],
        "outcome": outcome,  # success | failure | llm_override
        "duration": outcome.get("duration"),
        "cost": outcome.get("cost")
    }

    with LOG_FILE.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
```

#### 周期性分析
```python
# scripts/analyze-decisions.py
import pandas as pd

# 加载决策日志
df = pd.read_json("memory/decisions/decision-log.jsonl", lines=True)

# 分析准确率
accuracy = df[df["outcome"] == "success"].shape[0] / df.shape[0]
print(f"决策准确率: {accuracy:.2%}")

# 识别高频模式
top_patterns = df.groupby("task")["decision"].value_counts().head(10)
print("\n高频模式:")
print(top_patterns)

# 识别失败模式
failures = df[df["outcome"] == "failure"]
print("\n失败场景:")
print(failures[["task", "decision", "confidence"]])
```

**里程碑**：
- 1个月后：积累100+决策日志，识别5+高频Playbook
- 3个月后：积累500+决策日志，准确率>80%
- 6个月后：评估是否需要升级到方案C

---

## 五、验收标准

### 功能验收

#### 决策路由
- [ ] 简单命令匹配准确率 >90%
- [ ] Playbook匹配准确率 >80%
- [ ] 失败记忆命中率 100%（已知错误不重犯）
- [ ] LLM兜底正常工作（未匹配时调用大模型）

#### 经验积累
- [ ] 决策日志完整记录（包含task、decision、outcome）
- [ ] Playbook可版本化管理
- [ ] 失败案例可手动/自动添加

#### 性能指标
- [ ] 决策延迟 <100ms（规则匹配）
- [ ] 决策延迟 <1s（Playbook匹配）
- [ ] 重复任务执行时间减少 >40%

### 质量验收

#### 单元测试
```bash
pytest tests/agents/test_decision_router.py --cov=.claude/agents/router
# 目标覆盖率: >80%
```

#### 集成测试
```bash
python scripts/test-decision-scenarios.py
# 测试10个典型场景:
# 1. 文件行数统计
# 2. 简单grep
# 3. JSON解析
# 4. 重复任务识别
# 5. 已知失败规避
# 6. Playbook匹配
# 7. LLM兜底
# 8. 并发决策
# 9. 决策日志完整性
# 10. 失败恢复
```

#### 回归测试
```bash
python scripts/audit-rules.py --strict
python -m unittest discover -s tests -p "test_*.py"
```

### 业务验收

#### 对比实验
选取5个真实项目任务，分别用"纯LLM"和"决策路由"两种方式执行：

| 任务 | 纯LLM耗时 | 路由后耗时 | 节省比例 |
|------|-----------|-----------|---------|
| 统计代码行数 | 8.2s | 0.5s | 94% |
| 全局安装 | 45s | 12s | 73% |
| 规则审计 | 120s | 85s | 29% |
| 备份恢复 | 60s | 20s | 67% |
| 文档生成 | 90s | 85s | 6% |

**目标**：
- 简单任务节省 >70%
- 中等任务节省 >30%
- 复杂任务节省 >10%（规避已知错误）

---

## 六、风险与缓解

### 风险1：规则库维护负担
**表现**：
- 规则数量增长到100+条，难以管理
- 规则间冲突，匹配结果不确定

**缓解**：
1. **分层组织**：
   ```
   patterns/
   ├── file-operations.yaml
   ├── text-processing.yaml
   ├── git-operations.yaml
   └── project-specific.yaml
   ```

2. **优先级机制**：
   ```yaml
   - pattern: "统计.*行数"
     priority: 100
     action: "wc -l"

   - pattern: "统计.*Python.*行数"
     priority: 200  # 更具体的规则优先级更高
     action: "find . -name '*.py' | xargs wc -l"
   ```

3. **定期清理**：
   - 每季度review一次规则库
   - 删除命中率<1%的规则
   - 合并相似规则

### 风险2：Playbook过时
**表现**：
- 工具版本更新后，Playbook中的命令失效
- 项目结构变化后，路径不正确

**缓解**：
1. **版本标记**：
   ```markdown
   ---
   dependencies:
     python: ">=3.10"
     scripts/install-global.py: "exists"
   ---
   ```

2. **自动验证**：
   ```python
   # scripts/validate-playbooks.py
   def validate_playbook(pb):
       # 检查依赖是否满足
       for dep, constraint in pb["dependencies"].items():
           if not check_constraint(dep, constraint):
               print(f"WARNING: {pb['name']} 依赖不满足: {dep} {constraint}")
   ```

3. **失效提示**：
   ```python
   if playbook_validation_failed:
       return {
           "decision": "delegate_to_llm",
           "reason": "Playbook已过时，需要人工判断"
       }
   ```

### 风险3：决策误判
**表现**：
- 将复杂任务误判为简单命令，导致执行错误
- 匹配了错误的Playbook，执行不相关流程

**缓解**：
1. **置信度阈值**：
   ```python
   if decision["confidence"] < 0.75:
       # 低置信度时，给Agent提供建议而非直接执行
       return {
           "suggestion": decision["action"],
           "reasoning": decision["reasoning"],
           "require_confirmation": True
       }
   ```

2. **用户反馈**：
   ```python
   # Agent可以拒绝建议
   user_response = agent.confirm(decision["suggestion"])

   if user_response == "reject":
       # 记录误判
       log_false_positive(decision)
       # 降低该规则的优先级
       adjust_rule_priority(decision["rule_id"], -10)
   ```

3. **A/B测试**：
   - 10%的任务仍使用纯LLM路径
   - 对比两种方式的成功率
   - 持续调整路由策略

---

## 七、后续迭代路线图

### v1.0: 基础决策路由（当前SPEC）
- ✅ 简单命令匹配
- ✅ Playbook系统
- ✅ 失败记忆
- ✅ 决策日志

**交付时间**：2周

---

### v1.1: 自适应优化（+1个月）
- 根据决策日志自动调整规则优先级
- 识别高频模式，自动生成新规则
- Playbook自动版本升级提示

**触发条件**：
- 积累100+决策日志
- 识别出3+误判模式

---

### v1.2: 多Agent协作（+2个月）
- 决策路由支持子Agent调度
- 不同Agent的决策经验隔离
- 跨Agent的经验共享机制

**应用场景**：
- Ralph持续监控需要不同决策策略
- QA Reviewer的决策模式与开发Agent不同

---

### v2.0: 轻量决策模型（+6个月）
- 训练1B专用决策模型
- 替代规则引擎（保留作为fallback）
- 推理延迟 <50ms

**前置条件**：
- 积累500+决策日志
- 规则匹配准确率遇到瓶颈（<85%）
- 有ML工程能力

---

### v3.0: 完整自进化（+12个月）
- 自动任务复盘
- 改进建议验证
- 经验自动沉淀

**参考实现**：Agnes RSI机制

---

## 八、成本效益分析

### 实施成本

#### 开发成本
- 方案A: 2周开发 + 1周测试 = 约120小时
- 方案B: 2周部署 + 3周迁移 = 约200小时
- 方案C: 分阶段实施，约300小时（累计）

#### 运行成本
- 方案A: 无额外成本（使用现有基础设施）
- 方案B:
  - GPU租赁: ~$0.5/小时 × 24小时 × 30天 = $360/月
  - 或本地GPU: RTX 4090 ~$1600（一次性）
  - 电费: ~$30/月
- 方案C:
  - 训练成本: ~$50（一次性）
  - 推理成本: 可用CPU，无额外费用

### 收益估算

#### 时间节省
假设每天10个任务，每个任务平均节省30秒：
- 每天节省: 10 × 30s = 5分钟
- 每月节省: 5分钟 × 20工作日 = 100分钟 ≈ 1.7小时
- 每年节省: 100分钟 × 12月 = 1200分钟 ≈ 20小时

#### API成本节省
假设30%任务可规则处理，每次API调用$0.01：
- 每天节省: 10 × 30% × $0.01 = $0.03
- 每月节省: $0.03 × 20 = $0.6
- 每年节省: $0.6 × 12 = $7.2

#### ROI计算
- 方案A:
  - 投入: 120小时开发（一次性）
  - 收益: 20小时/年 + $7.2/年
  - ROI周期: 约6年（时间收益）

- 方案B:
  - 投入: 200小时 + $360/月
  - 收益: 假设节省50%时间 = 100小时/年 + $36/年
  - ROI周期: 约2年（但持续有运行成本）

**结论**：方案A更适合中小规模使用，方案B适合大规模/高频场景。

---

## 九、总结

### 推荐实施路径
1. **立即启动**：方案A（2-3周）
2. **持续迭代**：v1.1 → v1.2（3-6个月）
3. **评估升级**：6个月后决定是否需要v2.0或方案B

### 关键成功因素
1. **渐进式**：从简单规则开始，逐步优化
2. **数据驱动**：所有决策基于日志分析
3. **用户反馈**：Agent可拒绝建议，系统持续学习
4. **简单优先**：避免过度工程化

### 不确定性
- 实际节省效果取决于任务类型分布
- 规则维护负担可能超过预期
- Agnes Harness的长期维护状态未知

### 下一步行动
- [ ] Review本SPEC，确认方案选择
- [ ] 创建实施任务清单
- [ ] 分配开发资源
- [ ] 设置里程碑检查点

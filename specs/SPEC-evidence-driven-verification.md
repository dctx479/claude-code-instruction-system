# SPEC: 证据驱动验证系统

> 2026-11-23 实现状态见 [实施与验收记录](../docs/IMPROVEMENT-IMPLEMENTATION.md)，执行接口以 [运行时契约](SPEC-improvement-runtime.md) 为准。下文保留原始方案背景；示例路径、自动执行、外部安装与收益数字不视为已验证事实。

## 一、背景与目标

### 问题陈述
当前项目虽然强调"证据优先"，但缺乏系统化的证据管理机制：
1. **证据分散**：分布在commit、issue、memory、文档，无统一视图
2. **可信度不明**：无法量化"这个结论有多可靠"
3. **溯源困难**：事后难以追溯"这个规则是怎么来的"
4. **验证缺失**：改进建议缺乏量化的相似度/准确度测量

### 参考项目
**Craft Anything** (github.com/storytold/craft-anything)
- 核心理念：证据台账 + 量化测量 + 四步验证
- 技术栈：完全Rust实现，300+逆向工具
- 状态：early alpha (v0.6.1)
- 适用场景：软件复刻、逆向分析

**关键借鉴点**：
1. **证据台账**：记录结论来源、可信度、具体字节位置
2. **量化测量**：给出具体相似度百分比（如93%），而非模糊判断
3. **四步流程**：Study → Build → Check → Ready
4. **权限分级**：Clean room模式 vs Deep模式

### 目标
- 所有规则/记忆都有可追溯的证据链
- 结论附带置信度（0.0-1.0）
- 验证结果可量化（百分比、具体指标）
- 支持"这个规则基于什么证据"的快速查询

---

## 二、方案对比

### 方案A：增强现有Memory系统（推荐）

#### A1. 结构化证据字段

```markdown
# memory/fix-backup-collision.md (增强版)
---
name: fix-backup-collision
description: Windows时钟精度导致备份文件名冲突
metadata:
  type: feedback
  confidence: 0.95  # 新增：置信度
  evidence:  # 新增：证据列表
    - id: ev-001
      type: test
      source: "tests/test_backup.py:45-67"
      method: "单元测试复现"
      confidence: 0.95
      date: "2024-01-10"
      verified_by: human

    - id: ev-002
      type: commit
      source: "commit:a590f8a"
      method: "实际修复验证"
      confidence: 1.0
      date: "2024-01-10"
      verified_by: ci

    - id: ev-003
      type: measurement
      source: "tests/test_backup.py:test_frozen_clock_collision"
      metrics:
        execution_time: "0.023s"
        collision_rate_before: 1.0
        collision_rate_after: 0.0
      confidence: 1.0

  related_evidence: [[backup-timestamp-design]]

  # 新增：影响范围
  impact:
    scope: "backup系统"
    severity: "P1"  # P0:致命 | P1:严重 | P2:一般
    affected_files:
      - "scripts/backup.py"
      - "tests/test_backup.py"
---

## 问题现象
Windows系统下连续备份可能生成相同文件名

## 根因分析
**证据链**：
1. [ev-001] 单元测试`test_frozen_clock_collision`可稳定复现
2. [ev-002] Windows时钟分辨率文档：~15.6ms (QueryPerformanceCounter)
3. [ev-003] 实际测量：连续调用time.time()在<16ms间隔内返回相同值

**置信度**：0.95（基于3个独立证据源）

## 解决方案
```python
# 在时间戳后追加递增序号
timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
counter = 0
while (backup_dir / f"{timestamp}_{counter}").exists():
    counter += 1
final_name = f"{timestamp}_{counter}"
```

**验证结果**：
- ✅ 单元测试通过（collision_rate: 1.0 → 0.0）
- ✅ CI通过（commit a590f8a）
- ✅ 10,000次快速调用无碰撞

**Why**：防止备份覆盖，保证每次备份有唯一文件名

**How to apply**：
- 所有时间戳命名需考虑碰撞
- 高频操作（<100ms间隔）必须追加唯一标识
- 推荐：时间戳 + 随机后缀或序号
```

#### A2. 证据查询接口

```python
# memory/evidence/query.py
from pathlib import Path
import yaml
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Evidence:
    id: str
    type: str  # test | commit | measurement | observation | documentation
    source: str
    method: str
    confidence: float
    date: str
    verified_by: str
    metrics: Optional[dict] = None

@dataclass
class MemoryWithEvidence:
    name: str
    description: str
    confidence: float
    evidence_list: List[Evidence]
    content: str

class EvidenceQuery:
    def __init__(self, memory_dir: Path = Path("memory")):
        self.memory_dir = memory_dir

    def load_memory(self, name: str) -> MemoryWithEvidence:
        """加载记忆及其证据"""
        file_path = self.memory_dir / f"{name}.md"
        content = file_path.read_text(encoding="utf-8")

        # 解析frontmatter
        frontmatter, body = self._parse_frontmatter(content)

        # 解析证据
        evidence_list = []
        for ev_data in frontmatter.get("metadata", {}).get("evidence", []):
            evidence_list.append(Evidence(**ev_data))

        return MemoryWithEvidence(
            name=frontmatter["name"],
            description=frontmatter["description"],
            confidence=frontmatter["metadata"].get("confidence", 0.5),
            evidence_list=evidence_list,
            content=body
        )

    def find_by_confidence(self, min_confidence: float = 0.8) -> List[str]:
        """查找高置信度记忆"""
        results = []
        for md_file in self.memory_dir.glob("*.md"):
            memory = self.load_memory(md_file.stem)
            if memory.confidence >= min_confidence:
                results.append(memory.name)
        return results

    def trace_evidence_chain(self, name: str) -> dict:
        """追溯证据链"""
        memory = self.load_memory(name)

        chain = {
            "conclusion": memory.description,
            "confidence": memory.confidence,
            "evidence": []
        }

        for ev in memory.evidence_list:
            chain["evidence"].append({
                "type": ev.type,
                "source": ev.source,
                "confidence": ev.confidence,
                "verified_by": ev.verified_by,
                "details": ev.method
            })

        # 递归查找关联证据
        related = self._extract_related(memory.content)
        if related:
            chain["related"] = [
                self.trace_evidence_chain(r) for r in related
            ]

        return chain

    def verify_evidence(self, name: str) -> dict:
        """验证证据仍然有效"""
        memory = self.load_memory(name)

        results = {
            "valid": [],
            "invalid": [],
            "unverifiable": []
        }

        for ev in memory.evidence_list:
            if ev.type == "test":
                # 检查测试是否仍然存在且通过
                test_file = ev.source.split(":")[0]
                if Path(test_file).exists():
                    # 可以运行测试验证
                    results["valid"].append(ev.id)
                else:
                    results["invalid"].append({
                        "id": ev.id,
                        "reason": f"测试文件不存在: {test_file}"
                    })

            elif ev.type == "commit":
                # 检查commit是否存在
                commit_hash = ev.source.split(":")[1]
                # git cat-file -t {commit_hash}
                results["valid"].append(ev.id)

            elif ev.type == "measurement":
                # 度量数据无法自动验证
                results["unverifiable"].append(ev.id)

        return results
```

#### A3. 证据可视化命令

```python
# .claude/skills/evidence-trace.md

## 触发
用户询问"这个规则基于什么"、"证据是什么"、"可信度如何"

## 实现
使用 memory/evidence/query.py

## 示例
用户: "backup-collision这个修复的证据是什么？"

输出:
\`\`\`
📋 记忆: fix-backup-collision
描述: Windows时钟精度导致备份文件名冲突
总体置信度: 0.95 ⭐⭐⭐⭐⭐

🔍 证据链:
1. [ev-001] 单元测试复现
   • 来源: tests/test_backup.py:45-67
   • 方法: 单元测试复现
   • 置信度: 0.95
   • 验证者: human
   • 日期: 2024-01-10

2. [ev-002] 实际修复验证
   • 来源: commit:a590f8a
   • 方法: 实际修复验证
   • 置信度: 1.0
   • 验证者: ci
   • 日期: 2024-01-10

3. [ev-003] 量化测量
   • 来源: tests/test_backup.py:test_frozen_clock_collision
   • 指标:
     - execution_time: 0.023s
     - collision_rate_before: 1.0 (100%)
     - collision_rate_after: 0.0 (0%)
   • 置信度: 1.0

🔗 关联证据:
• [[backup-timestamp-design]] (设计文档)

✅ 证据验证状态:
• ev-001: ✅ 有效（测试文件存在）
• ev-002: ✅ 有效（commit存在）
• ev-003: ⚠️  无法自动验证（需手动复测）
\`\`\`
```

#### A4. 证据审计工具

```python
# scripts/audit-evidence.py
"""审计所有记忆的证据完整性"""

from pathlib import Path
from memory.evidence.query import EvidenceQuery

def audit_all_memories():
    query = EvidenceQuery()

    report = {
        "total": 0,
        "with_evidence": 0,
        "without_evidence": 0,
        "low_confidence": [],
        "invalid_evidence": []
    }

    for md_file in Path("memory").glob("*.md"):
        report["total"] += 1

        try:
            memory = query.load_memory(md_file.stem)

            if not memory.evidence_list:
                report["without_evidence"] += 1
                print(f"⚠️  {memory.name}: 缺少证据")
                continue

            report["with_evidence"] += 1

            if memory.confidence < 0.6:
                report["low_confidence"].append({
                    "name": memory.name,
                    "confidence": memory.confidence
                })
                print(f"⚠️  {memory.name}: 低置信度 ({memory.confidence})")

            # 验证证据有效性
            verification = query.verify_evidence(md_file.stem)
            if verification["invalid"]:
                report["invalid_evidence"].append({
                    "name": memory.name,
                    "invalid": verification["invalid"]
                })
                for inv in verification["invalid"]:
                    print(f"❌ {memory.name}: 证据失效 - {inv['reason']}")

        except Exception as e:
            print(f"❌ {md_file.name}: 解析失败 - {e}")

    # 输出汇总
    print("\n" + "="*60)
    print(f"总计: {report['total']} 条记忆")
    print(f"有证据: {report['with_evidence']} ({report['with_evidence']/report['total']*100:.1f}%)")
    print(f"无证据: {report['without_evidence']} ({report['without_evidence']/report['total']*100:.1f}%)")
    print(f"低置信度: {len(report['low_confidence'])} 条")
    print(f"证据失效: {len(report['invalid_evidence'])} 条")

    if report["without_evidence"] > 0:
        print("\n建议:")
        print("  • 为无证据记忆补充证据来源")
        print("  • 或标记为 UNVERIFIED 状态")

    return report

if __name__ == "__main__":
    audit_all_memories()
```

**依赖**：
- Python标准库（yaml、dataclasses）
- 无额外第三方库

**风险**：RISK-LOW
- 只是增强现有系统，不破坏兼容性
- 旧格式记忆仍可正常工作（无evidence字段时降级处理）

**投入**：约3-5天
- Day 1: 设计证据字段schema
- Day 2: 实现EvidenceQuery
- Day 3: 实现evidence-trace Skill
- Day 4: 实现audit-evidence.py
- Day 5: 迁移5条现有记忆到新格式

---

### 方案B：引入Craft Anything逆向工具集（不推荐）

#### 完整能力
```
Craft Anything
├── Reverse Engineering Engine (Rust)
│   ├── Disassemblers (x86/x64/ARM/MIPS/...)
│   ├── Decompilers (Ghidra集成)
│   ├── Binary Parsers (PE/ELF/Mach-O/DEX/...)
│   ├── .NET Analyzer (dnSpy)
│   ├── Java/Android Tools
│   └── Firmware/Protocol Analyzers
├── Evidence System
│   ├── Byte-level Tracking
│   ├── Confidence Scoring
│   └── Cross-reference Graph
├── Verification Engine
│   ├── Visual Similarity (多屏幕宽度测量)
│   ├── Behavior Testing (执行结果对比)
│   └── API Compatibility Check
└── Clean Room Mode
    ├── Screenshot-only Analysis
    ├── Observable Behavior Recording
    └── No Source Access
```

#### 安装步骤
```bash
# 1. 下载预编译版本
# Windows/macOS/Linux/FreeBSD都有官方签名安装包
wget https://github.com/storytold/craft-anything/releases/download/v0.6.1/craft-anything-v0.6.1-windows-x64.exe

# 2. 安装
./craft-anything-v0.6.1-windows-x64.exe

# 3. 验证
craft-anything-cli --version

# 4. 配置Claude Code集成
cat > ~/.claude/plugins/craft-anything.json <<EOF
{
  "name": "craft-anything",
  "type": "mcp-tools",
  "tools": [
    "craft-reverse",
    "craft-compare",
    "craft-verify"
  ],
  "config": {
    "mode": "clean-room",  # 默认安全模式
    "deep-mode-password": null  # Deep模式需要显式启用
  }
}
EOF
```

#### 在太一中的潜在应用

##### 应用1：Hook代码逆向分析
```bash
# 场景：用户提交了一个二进制Hook（如compiled Python extension）
# 需要分析它的行为是否安全

craft-anything-cli study suspicious-hook.pyd --output report.json

# 输出证据台账
{
  "file": "suspicious-hook.pyd",
  "type": "PE32+ DLL",
  "evidence": [
    {
      "finding": "调用 CreateProcessW",
      "confidence": 1.0,
      "location": "0x1234:CALL CreateProcessW",
      "severity": "high",
      "reasoning": "可以执行任意进程"
    },
    {
      "finding": "读取环境变量 CLAUDE_API_KEY",
      "confidence": 0.85,
      "location": "0x5678:PUSH 'CLAUDE_API_KEY'; CALL getenv",
      "severity": "critical",
      "reasoning": "可能泄露API密钥"
    }
  ]
}
```

##### 应用2：复刻第三方Agent行为
```bash
# 场景：想要学习其他优秀Agent的决策模式
craft-anything-cli study competitor-agent.exe --mode deep

# 输出：决策树、工具调用模式、错误处理策略
```

##### 应用3：验证自动生成代码
```bash
# 场景：Agent生成了复杂代码，需要验证与规格的一致性
craft-anything-cli compare \
  --original specs/SPEC-backup-strategy.md \
  --generated scripts/backup.py \
  --output similarity-report.json

# 输出
{
  "similarity": 0.87,
  "matched_requirements": [
    "时间戳命名 ✅",
    "碰撞检测 ✅",
    "错误处理 ⚠️ (部分实现)"
  ],
  "missing_features": [
    "备份验证checksum"
  ],
  "extra_features": [
    "压缩功能（未在规格中）"
  ]
}
```

#### 优势
1. **深度分析**：可以分析二进制、混淆代码
2. **量化精确**：给出具体字节位置、置信度
3. **工具完整**：300+工具覆盖各种场景
4. **Rust性能**：分析速度快

#### 劣势
1. **场景不匹配**：太一是编排工具，很少需要逆向二进制
2. **复杂度高**：300+工具对大多数任务是overkill
3. **Early Alpha**：v0.6.1仍不稳定，API可能变化
4. **学习曲线**：需要逆向工程知识
5. **安全风险**：Deep模式可执行任意代码

**风险**：RISK-HIGH
- 引入300+工具严重违背"按需加载"原则
- 安全边界复杂（Clean room vs Deep模式）
- 维护负担重（跟随上游更新）

**不推荐原因**：
- 太一的核心场景是"编排Agent工作流"，不是"逆向分析软件"
- 99%的任务不需要反汇编/反编译
- 证据系统理念可借鉴，但完整工具集不适用

---

### 方案C：混合方案（长期考虑）

在方案A运行稳定后，可选择性引入Craft Anything的部分能力：

#### C1. MCP工具选择性接入
```json
// 只接入verification相关工具，不接入逆向工具
{
  "name": "craft-verify",
  "tools": [
    "craft-compare",    // 代码相似度对比
    "craft-measure"     // 量化测量
  ],
  "exclude": [
    "craft-disassemble",
    "craft-decompile",
    "craft-ghidra"
  ]
}
```

#### C2. 证据格式兼容
```python
# 使太一的证据格式兼容Craft Anything输出
def import_craft_evidence(craft_report: dict) -> Evidence:
    """导入Craft Anything的分析结果为证据"""
    return Evidence(
        id=f"craft-{craft_report['finding_id']}",
        type="measurement",
        source=craft_report['location'],
        method=f"Craft Anything analysis (confidence: {craft_report['confidence']})",
        confidence=craft_report['confidence'],
        date=datetime.now().isoformat(),
        verified_by="tool",
        metrics={
            "finding": craft_report['finding'],
            "severity": craft_report['severity']
        }
    )
```

#### C3. 按需安装策略
```python
# .claude/skills/analyze-binary.md

## 触发
用户请求分析二进制文件、.pyd、.so等

## 前置检查
if not shutil.which("craft-anything-cli"):
    print("⚠️  此任务需要 Craft Anything 工具")
    print("   安装: https://github.com/storytold/craft-anything")
    print("   或使用其他方式完成任务")
    return

## 执行
subprocess.run(["craft-anything-cli", "study", target_file])
```

**风险**：RISK-MEDIUM
- 需要用户手动安装外部工具
- 依赖外部项目的稳定性

**投入**：约1周
- Day 1-2: 设计MCP集成接口
- Day 3-4: 实现证据格式转换
- Day 5: 编写按需安装Skill

---

## 三、推荐方案

### 优先采用方案A，理由：
1. **需求匹配**：太一需要的是"结构化证据管理"，不是"逆向工程"
2. **轻量实现**：增强现有系统，无需引入300+工具
3. **完全控制**：自主实现，可按需迭代
4. **零依赖**：只用Python标准库

### 方案B不推荐，理由：
- 场景不匹配（编排工具 vs 逆向工具）
- 过度工程化
- Early Alpha状态

### 方案C作为长期储备：
- 仅在出现"分析二进制Hook"等特殊需求时考虑
- 通过MCP选择性接入，而非完整安装

---

## 四、详细实施计划（方案A）

### Phase 1: 证据Schema设计（2天）

#### Day 1: 定义数据结构
```yaml
# memory/schemas/evidence-v1.yaml
Evidence:
  id:
    type: string
    pattern: "^ev-\\d{3}$"
    description: "证据唯一标识，如 ev-001"

  type:
    type: enum
    values:
      - test          # 单元测试、集成测试
      - commit        # Git commit
      - measurement   # 量化测量（性能、准确率等）
      - observation   # 人工观察
      - documentation # 官方文档、RFC等
    description: "证据类型"

  source:
    type: string
    examples:
      - "tests/test_backup.py:45-67"
      - "commit:a590f8a"
      - "https://docs.python.org/3/library/time.html#time.time"
    description: "证据来源（可点击/可验证）"

  method:
    type: string
    description: "获取证据的方法"

  confidence:
    type: float
    min: 0.0
    max: 1.0
    description: "证据可信度"

  date:
    type: string
    format: "YYYY-MM-DD"
    description: "证据获取日期"

  verified_by:
    type: enum
    values: [human, ci, tool, peer-review]
    description: "验证方式"

  metrics:
    type: object
    optional: true
    description: "量化指标"
```

#### Day 2: 编写验证器
```python
# memory/schemas/validator.py
import yaml
from jsonschema import validate, ValidationError

class EvidenceValidator:
    def __init__(self, schema_path="memory/schemas/evidence-v1.yaml"):
        with open(schema_path) as f:
            self.schema = yaml.safe_load(f)

    def validate_evidence(self, evidence_data: dict) -> tuple[bool, str]:
        """验证证据格式"""
        try:
            validate(instance=evidence_data, schema=self.schema)
            return True, ""
        except ValidationError as e:
            return False, str(e)

    def validate_memory_file(self, file_path: Path) -> dict:
        """验证整个记忆文件"""
        # 解析frontmatter
        # 验证每个证据
        # 返回报告
        pass
```

---

### Phase 2: 实现查询接口（2天）

#### Day 3: 核心查询功能
实现前述的 `memory/evidence/query.py`

#### Day 4: 命令行工具
```python
# scripts/evidence-cli.py
import click
from memory.evidence.query import EvidenceQuery

@click.group()
def cli():
    """证据管理命令行工具"""
    pass

@cli.command()
@click.argument("name")
def show(name):
    """显示记忆的证据链"""
    query = EvidenceQuery()
    chain = query.trace_evidence_chain(name)
    # 格式化输出
    print_evidence_chain(chain)

@cli.command()
@click.option("--min-confidence", default=0.8, type=float)
def list_high_confidence(min_confidence):
    """列出高置信度记忆"""
    query = EvidenceQuery()
    results = query.find_by_confidence(min_confidence)
    for name in results:
        memory = query.load_memory(name)
        print(f"{name}: {memory.confidence:.2f}")

@cli.command()
@click.argument("name")
def verify(name):
    """验证证据有效性"""
    query = EvidenceQuery()
    results = query.verify_evidence(name)

    print(f"✅ 有效: {len(results['valid'])}")
    print(f"❌ 失效: {len(results['invalid'])}")
    print(f"⚠️  无法验证: {len(results['unverifiable'])}")

    for inv in results['invalid']:
        print(f"\n❌ {inv['id']}: {inv['reason']}")

if __name__ == "__main__":
    cli()
```

---

### Phase 3: 迁移现有记忆（3天）

#### Day 5-6: 迁移高优先级记忆
选择10条最重要的记忆迁移到新格式：
1. fix-backup-collision
2. windows-path-encoding
3. hook-execution-safety
4. memory-compact-strategy
5. agent-decision-routing
6. rule-deprecation-lifecycle
7. qa-scoring-method
8. global-install-procedure
9. skill-loading-pattern
10. context-budget-management

#### Day 7: 验证与文档
- 运行 `python scripts/audit-evidence.py`
- 确保所有迁移记忆通过验证
- 更新 `docs/MEMORY-GUIDE.md`

---

### Phase 4: 集成到工作流（2天）

#### Day 8: 集成到/rule-audit
```python
# 在规则审计时显示证据状态
def audit_rule(rule):
    # ... 现有逻辑 ...

    # 新增：检查证据
    if rule.has_memory:
        query = EvidenceQuery()
        verification = query.verify_evidence(rule.memory_name)

        if verification['invalid']:
            print(f"⚠️  规则 {rule.name} 的证据已失效:")
            for inv in verification['invalid']:
                print(f"   • {inv['reason']}")
            print("   建议: 重新验证或标记为UNVERIFIED")
```

#### Day 9: 集成到/evolve
```python
# 在规则演化时要求提供证据
def propose_new_rule(incident):
    print("请提供至少2个独立证据来源:")
    print("1. 单元测试复现")
    print("2. Commit记录")
    print("3. 量化测量")
    print("4. 人工观察")

    evidence = collect_evidence()

    if len(evidence) < 2:
        print("❌ 证据不足，无法生成新规则")
        return None

    confidence = calculate_confidence(evidence)

    if confidence < 0.6:
        print(f"⚠️  置信度较低 ({confidence:.2f})，建议标记为实验性规则")
```

---

## 五、验收标准

### 功能验收

#### 证据管理
- [ ] 所有新记忆必须包含至少1个证据
- [ ] 证据格式通过schema验证
- [ ] 支持5种证据类型（test/commit/measurement/observation/documentation）
- [ ] 证据可自动验证有效性（test/commit类型）

#### 查询能力
- [ ] 可查询指定记忆的证据链
- [ ] 可按置信度筛选记忆
- [ ] 可追溯关联证据（递归查询）
- [ ] 查询延迟 <100ms

#### 可视化
- [ ] 命令行工具可格式化显示证据
- [ ] Skill可回答"基于什么证据"类问题
- [ ] 审计工具可发现无证据/低置信度/失效证据

### 质量验收

#### 单元测试
```bash
pytest tests/memory/test_evidence_query.py --cov=memory/evidence
# 目标覆盖率: >85%
```

测试场景：
1. 解析带证据的记忆
2. 解析不带证据的记忆（向后兼容）
3. 证据验证（有效/无效/无法验证）
4. 置信度计算
5. 证据链追溯
6. 循环引用检测

#### 集成测试
```python
# tests/memory/test_evidence_integration.py
def test_full_lifecycle():
    """测试完整生命周期"""
    # 1. 创建新记忆（带证据）
    # 2. 查询证据链
    # 3. 验证证据有效性
    # 4. 修改记忆
    # 5. 重新验证
    pass

def test_rule_audit_integration():
    """测试与规则审计的集成"""
    # /rule-audit 能发现证据失效的规则
    pass
```

#### 回归测试
```bash
python scripts/audit-evidence.py
python scripts/audit-rules.py --strict
python -m unittest discover -s tests -p "test_*.py"
```

---

### 业务验收

#### 迁移验收
- [ ] 10条核心记忆迁移到新格式
- [ ] 所有记忆通过 `audit-evidence.py` 检查
- [ ] 旧格式记忆仍可正常读取（向后兼容）

#### 实际使用
选取3个真实场景验证：

**场景1：新人onboarding**
- 问题："backup-collision这个修复是怎么来的？"
- 期望：显示完整证据链，新人能理解根因和解决方案

**场景2：规则审计**
- 任务：审计所有规则的证据状态
- 期望：发现并报告无证据/低置信度/失效证据的规则

**场景3：规则演化**
- 任务：提出新规则
- 期望：系统要求提供证据，拒绝无证据的规则

---

## 六、风险与缓解

### 风险1：迁移成本
**表现**：
- 50+条现有记忆，全部迁移工作量大
- 历史记忆缺乏证据来源信息

**缓解**：
1. **渐进式迁移**：
   - 先迁移10条核心记忆
   - 新记忆强制使用新格式
   - 旧记忆按需迁移（被查询时提示"建议补充证据"）

2. **兼容性保证**：
   ```python
   def load_memory(name):
       memory = parse_frontmatter(...)

       # 旧格式兼容
       if "evidence" not in memory.metadata:
           memory.confidence = 0.5  # 默认中等置信度
           memory.evidence_list = []
           memory.legacy = True  # 标记为旧格式
   ```

3. **批量辅助工具**：
   ```python
   # scripts/migrate-memory.py
   def suggest_evidence(memory_content):
       """AI辅助提取可能的证据"""
       # 扫描内容中的commit hash
       # 扫描测试文件引用
       # 返回建议的证据列表
   ```

---

### 风险2：证据过时
**表现**：
- 测试文件被删除
- Commit被rebase掉
- 外部文档链接失效

**缓解**：
1. **定期验证**：
   ```bash
   # CI中运行
   python scripts/audit-evidence.py --strict
   # 发现失效证据时报警
   ```

2. **多证据要求**：
   - 重要结论要求≥2个独立证据
   - 单一证据失效不影响整体置信度

3. **降级策略**：
   ```python
   if all_evidence_invalid:
       memory.confidence *= 0.5
       memory.status = "NEEDS_REVERIFICATION"
   ```

---

### 风险3：主观证据可信度
**表现**：
- observation类型证据难以量化
- 不同人的observation可信度差异大

**缓解**：
1. **验证者权重**：
   ```python
   VERIFIER_WEIGHT = {
       "human": 0.8,
       "ci": 1.0,
       "tool": 0.9,
       "peer-review": 0.95
   }

   def calculate_confidence(evidence_list):
       weighted_sum = sum(
           ev.confidence * VERIFIER_WEIGHT[ev.verified_by]
           for ev in evidence_list
       )
       return weighted_sum / len(evidence_list)
   ```

2. **peer-review机制**：
   - observation类证据建议标记为待审查
   - 经2人以上确认后提升verified_by

3. **透明化**：
   - 显示证据链时明确标注observation来源
   - 让用户自行判断可信度

---

## 七、后续迭代路线图

### v1.0: 基础证据系统（当前SPEC）
- ✅ 结构化证据字段
- ✅ 查询接口
- ✅ 命令行工具
- ✅ 10条记忆迁移

**交付时间**：2周

---

### v1.1: 可视化增强（+2周）
- 证据关系图（Graphviz）
- Web界面查看证据链
- 时间线视图（证据按时间排列）

**示例**：
```
fix-backup-collision (2024-01-10)
│
├─ ev-001: 单元测试复现 (confidence: 0.95)
│  └─ tests/test_backup.py:45-67
│
├─ ev-002: 实际修复 (confidence: 1.0)
│  └─ commit:a590f8a
│     └─ CI通过 (2024-01-10 15:23)
│
└─ ev-003: 量化测量 (confidence: 1.0)
   └─ collision_rate: 100% → 0%
```

---

### v1.2: 自动证据收集（+1个月）
- Git commit时自动提取相关记忆
- 测试通过时自动记录为证据
- CI失败时建议创建失败记忆

**工作流**：
```bash
# .git/hooks/post-commit
#!/bin/bash
python .claude/hooks/auto-evidence.py \
  --commit HEAD \
  --scan-tests \
  --update-memory
```

---

### v2.0: 证据强度分析（+3个月）
- 基于贝叶斯网络的置信度传播
- 证据冲突检测（两个证据支持相反结论）
- 建议补充证据（当前证据不足以支持结论）

**示例**：
```
结论: "Windows时钟分辨率~15.6ms"
当前置信度: 0.85

建议补充证据:
• 在实际Windows机器上测量（当前只有文档引用）
• 不同Windows版本的对比测试
• QueryPerformanceFrequency() 实测值

补充后预期置信度: 0.95
```

---

### v3.0: 证据即代码（+6个月）
- 证据可执行（test类证据可一键重跑）
- 证据可重现（measurement类证据可复现）
- 证据版本化（证据本身也有历史）

**参考实现**：Craft Anything的量化测量机制

---

## 八、与其他SPEC的集成

### 与SPEC-context-optimization集成
- 决策路由的"置信度"来自证据系统
- 路由规则的制定需要提供证据

### 与SPEC-dual-system-decision集成
- Playbook的success_rate基于证据记录
- 失败记忆系统使用相同的证据结构

### 与现有规则系统集成
- `/rule-audit`显示规则的证据状态
- `/evolve`要求新规则提供证据
- `docs/RULE-EVOLUTION.md`引用证据标准

---

## 九、度量指标

### 过程指标
- 新记忆带证据比例（目标：>90%）
- 平均证据数量（目标：≥2个）
- 证据有效性（目标：>95%有效）

### 结果指标
- 规则争议减少（有证据支撑的规则被质疑次数）
- onboarding效率（新人理解规则来源的时间）
- 规则演化速度（有证据支撑可加快迭代）

### 质量指标
- 高置信度记忆占比（>80%记忆confidence>0.8）
- 低置信度记忆处理时间（发现后多久补充证据或删除）

---

## 十、总结

### 核心价值
1. **可追溯**：每个结论都能追溯到源头
2. **可量化**：置信度、相似度等有具体数字
3. **可验证**：证据可以被重新检查
4. **可演化**：证据充足时可快速迭代规则

### 实施建议
- 优先方案A：轻量级、增量式
- 避免方案B：过度工程化
- 考虑方案C：长期特殊场景

### 下一步行动
- [ ] Review本SPEC
- [ ] 创建Phase 1任务清单
- [ ] 设计10条记忆的迁移方案
- [ ] 启动实施

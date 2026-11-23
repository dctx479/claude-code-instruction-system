# SPEC: 上下文优化系统

> 2026-11-23 实现状态见 [实施与验收记录](../docs/IMPROVEMENT-IMPLEMENTATION.md)，执行接口以 [运行时契约](SPEC-improvement-runtime.md) 为准。下文保留原始方案背景；示例路径、自动执行、外部安装与收益数字不视为已验证事实。

## 一、背景与目标

### 问题陈述
当前Agent在处理大数据量任务时存在三个核心问题：
1. **Token浪费**：原始数据全量进入上下文（如56KB截图、45KB日志）
2. **上下文污染**：过程数据挤占工作记忆，导致提前触发compact
3. **重复成本**：compact后丢失上下文，需重新输入需求

### 参考项目
**Context Mode** (github.com/mksglu/context-mode)
- 声称节省98% token（最优场景）
- 核心机制：沙箱执行 + 会话记忆 + 检索缓存
- 许可证：Elastic License 2.0（限制托管转售）

### 目标
- 真实场景节省30-50% token（保守估算）
- 延长有效会话时长1.5-2倍
- 不引入超过3个新依赖

---

## 二、方案对比

### 方案A：轻量级借鉴（推荐）

**核心理念**：Think in Code + 智能路由

#### A1. 决策路由层
```python
# .claude/hooks/pre-tool-call.py
import json
import os
from pathlib import Path

STATE_FILE = Path.home() / ".claude" / "session-state.json"

def should_use_script(tool_name, params):
    """判断是否应该用脚本替代直接工具调用"""

    # 规则1：批量文件读取 → 脚本聚合
    if tool_name == "Read" and is_batch_pattern(params):
        return {
            "route": "script",
            "reason": "检测到批量读取模式",
            "suggestion": "考虑用Bash脚本聚合结果"
        }

    # 规则2：重复Grep → 写正则脚本
    if tool_name == "Grep" and get_grep_count() >= 3:
        return {
            "route": "script",
            "reason": "连续3次Grep",
            "suggestion": "用脚本一次性提取所有匹配"
        }

    # 规则3：大文件分析 → 流式处理
    if tool_name == "Read" and get_file_size(params) > 100_000:
        return {
            "route": "stream",
            "reason": f"文件大小 {get_file_size(params)} 字节",
            "suggestion": "用Bash管道流式处理：head/tail/grep/awk"
        }

    return {"route": "direct"}

def is_batch_pattern(params):
    """检测是否为批量模式"""
    # 检查session-state中最近3次Read是否在同一目录
    # 实现略
    pass
```

#### A2. 结果摘要注入
```python
# .claude/hooks/post-tool-call.py
def summarize_output(tool_name, output):
    """对大体量输出进行摘要"""

    if len(output) < 5000:
        return output  # 小输出直接返回

    if tool_name == "Bash" and is_log_analysis(output):
        return extract_log_summary(output)

    if tool_name == "web_search":
        return f"[搜索结果已缓存，共{count_results(output)}条]\n{output[:1000]}..."

    return output

def extract_log_summary(log_text):
    """提取日志关键信息"""
    return {
        "total_lines": log_text.count("\n"),
        "error_count": log_text.count("ERROR"),
        "warning_count": log_text.count("WARN"),
        "sample": log_text.split("\n")[:5]  # 前5行样本
    }
```

#### A3. 简化记忆检索
```python
# commands/memory/quick-search.py
import sqlite3
from pathlib import Path

MEMORY_DB = Path("memory/.cache/index.db")

def init_memory_index():
    """首次运行时建立索引"""
    conn = sqlite3.connect(MEMORY_DB)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts
        USING fts5(name, description, content, filename)
    """)

    # 索引所有.md文件
    for md_file in Path("memory").glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        # 解析frontmatter
        name, desc = parse_frontmatter(content)
        conn.execute(
            "INSERT INTO memory_fts VALUES (?, ?, ?, ?)",
            (name, desc, content, md_file.name)
        )
    conn.commit()

def search_memory(query, limit=3):
    """快速检索记忆"""
    conn = sqlite3.connect(MEMORY_DB)
    results = conn.execute(
        "SELECT filename, rank FROM memory_fts WHERE memory_fts MATCH ? ORDER BY rank LIMIT ?",
        (query, limit)
    ).fetchall()
    return [f"memory/{r[0]}" for r in results]
```

**依赖**：
- Python标准库 sqlite3（已有）
- 无额外第三方库

**风险**：RISK-MEDIUM
- 路由规则可能误判
- 需要维护规则库

**投入**：约2-3天
- Day 1: 实现决策路由Hook
- Day 2: 实现结果摘要Hook
- Day 3: 记忆索引 + 测试

---

### 方案B：完整引入Context Mode（备选）

#### 架构
```
context-mode (MCP Server)
├── Sandbox Runtime (12种语言)
├── Memory Store (SQLite + FTS5)
├── Cache Layer (TTL 24h)
└── Hooks Integration
    ├── pre-tool-call
    ├── post-tool-call
    └── pre-compact
```

#### 安装步骤
```bash
# 1. 安装MCP服务器
cd ~/.claude/plugins
git clone https://github.com/mksglu/context-mode
cd context-mode
npm install

# 2. 配置Claude Code插件
cat > ~/.claude/plugins/context-mode.json <<EOF
{
  "name": "context-mode",
  "type": "mcp-server",
  "command": "node",
  "args": ["~/.claude/plugins/context-mode/dist/index.js"],
  "settings": {
    "sandbox_enabled": true,
    "cache_ttl": 86400,
    "throttle_limits": {
      "search": 8,
      "fetch": 5
    }
  }
}
EOF

# 3. 重启Claude Code
```

#### 核心能力
1. **沙箱执行**：
   - JavaScript/TypeScript (Node.js)
   - Python 3.10+
   - Shell (Bash)
   - 其他9种语言

2. **会话记忆**：
   - 双路检索（词干 + trigram）
   - RRF排序融合
   - Levenshtein纠错

3. **智能缓存**：
   - URL缓存（24h TTL）
   - 大文档片段化
   - 渐进式节流

#### 优势
- 官方维护，持续更新
- 功能完整，开箱即用
- 社区验证（Hacker News第一）

#### 劣势
- **许可证风险**：Elastic License 2.0不允许托管转售
- **依赖重**：需要Node.js环境 + 多语言runtime
- **不可控**：黑盒服务，故障难排查
- **营销数字**：98%节省率仅在最优场景成立

**风险**：RISK-HIGH
- 许可证可能与太一的分发策略冲突
- 外部依赖故障影响核心功能
- 社区项目可能停止维护

**投入**：约1天（安装配置） + 长期维护成本

---

## 三、推荐方案

**优先采用方案A**，理由：
1. 符合太一"简单优先、按需加载"原则
2. 完全控制实现，可按需迭代
3. 无许可证风险
4. 保守估算仍可节省30%+ token

**方案B作为技术储备**：
- 在方案A实施3个月后评估效果
- 若节省不足预期，再考虑完整引入
- 届时需法务审查Elastic License 2.0

---

## 四、验收标准

### 功能验收
- [ ] 识别批量Read模式准确率 >80%
- [ ] 大文件（>100KB）自动建议流式处理
- [ ] 记忆检索延迟 <200ms
- [ ] Hook执行不阻塞正常工作流

### 性能验收
- [ ] 10次典型会话的token对比：
  - 文档分析任务：节省 >40%
  - 代码审查任务：节省 >25%
  - 混合任务：节省 >30%
- [ ] 有效会话时长延长 >1.5倍

### 回归测试
```bash
python scripts/audit-rules.py --strict
python scripts/audit-skills.py
python -m unittest discover -s tests/hooks -p "test_*.py"
```

---

## 五、实施计划

### Phase 1: 决策路由层（1周）
- Day 1-2: 实现pre-tool-call.py
- Day 3-4: 实现post-tool-call.py
- Day 5: 单元测试 + 文档

### Phase 2: 记忆索引（3天）
- Day 1: 实现memory索引构建
- Day 2: 实现快速检索接口
- Day 3: 集成到现有Skill

### Phase 3: 验证与调优（1周）
- 在5个真实项目中试用
- 收集token节省数据
- 调整路由规则阈值

---

## 六、风险与缓解

### 风险1：路由误判导致任务失败
**缓解**：
- 所有路由建议都是"软建议"，Agent可选择忽略
- 保留完整的fallback路径
- 记录误判案例，迭代规则

### 风险2：记忆索引不同步
**缓解**：
- 每次启动时检查索引版本
- memory/文件修改时自动触发重建
- 提供手动重建命令：`/memory:rebuild-index`

### 风险3：性能开销
**缓解**：
- Hook执行超时设置（100ms）
- 索引查询使用覆盖索引
- 异步处理非关键路径

---

## 七、后续迭代

### v1.1: 自适应阈值
根据用户习惯动态调整路由阈值：
- 记录每次路由决策的接受率
- 被拒绝>3次的规则自动降低优先级

### v1.2: 跨会话缓存
将URL缓存、文档片段持久化到本地：
```
~/.claude/cache/
├── web-fetch/
│   └── {url_hash}.json
└── memory-index/
    └── index.db
```

### v2.0: 可选完整沙箱
如方案A效果显著，可考虑自研轻量沙箱：
- 只支持Python + Bash（覆盖90%场景）
- 使用Docker容器隔离
- 避免Elastic License依赖

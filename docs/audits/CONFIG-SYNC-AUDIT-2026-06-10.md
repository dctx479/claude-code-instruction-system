# 全局与项目配置完整对比审计报告

**审计日期**: 2026-06-10  
**执行者**: Orchestrator (Task #1)  
**全局配置根**: `C:\Users\ASUS\.claude\`  
**项目配置根**: `G:\GitHub_local\Self-built\Prompt\ClaudeCodePlan\claude-code-instruction-system\.claude\`

---

## 执行摘要

本次审计发现**严重的配置不同步问题**：

1. **全局配置缺失关键项目更新**：全局 CLAUDE.md 缺少"废弃规则管理协议"章节
2. **项目配置严重不完整**：项目侧缺少 agents/commands/workflows 所有定义文件
3. **Hooks 配置缺失**：项目侧 hooks 目录存在但为空，缺少 hooks.json
4. **Skills INDEX 不一致**：项目侧新增 2 个 skills 未同步到全局

---

## 一、关键配置文件对比

### 1.1 CLAUDE.md 文件

| 位置 | Hash | 大小 | 状态 |
|------|------|------|------|
| 全局 `~/.claude/CLAUDE.md` | `d268c9bd5363...` | 未测量 | ⚠️ **缺少最新章节** |
| 项目根 `CLAUDE.md` | `33894e5f01d4...` | 未测量 | ✅ 包含废弃规则协议 |

**差异详情**:
- 项目版 CLAUDE.md 在 §八 增加了"废弃规则管理（Deprecation Protocol）"章节
- 该章节定义了过时规则标记格式、废弃生命周期（60天）、适用场景判断
- **建议**: 立即将此章节同步到全局 CLAUDE.md

### 1.2 核心配置文件状态

| 文件 | 全局 | 项目 | 状态 |
|------|------|------|------|
| `CLAUDE.md` | ✅ 存在 | ⊘ 不存在 | 📦 仅全局有（项目用根目录版本） |
| `settings.json` | ✅ 存在 | ⊘ 不存在 | 📦 仅全局有 |
| `config/settings.json` | ✅ 存在 (686 bytes) | ⊘ 不存在 | 📦 仅全局有 |
| `config/keywords.json` | ✅ 存在 (5482 bytes) | ⊘ 不存在 | 📦 仅全局有 |
| `config/mcp-servers.json` | ✅ 存在 (3228 bytes) | ⊘ 不存在 | 📦 仅全局有 |
| `agents/INDEX.md` | ✅ 存在 | ⊘ 不存在 | 📦 仅全局有 |
| `skills/INDEX.md` | ✅ 存在 (6902 bytes) | ✅ 存在 (7222 bytes) | ⚠️ **冲突** |
| `hooks/hooks.json` | ✅ 存在 (3496 bytes) | ⊘ 不存在 | 📦 仅全局有 |

**备注**: 项目侧有 `settings.local.json` (2059 bytes)，包含项目特定权限配置。

---

## 二、目录结构对比

### 2.1 顶层目录差异

**全局独有目录** (35 个):
```
.god/ agents/ backups/ cache/ commands/ config/ context-mode/
debug/ docs/ file-history/ ide/ paste-cache/ plans/ plugins/
projects/ session-env/ sessions/ shell-snapshots/ specs/
tasks/ themes/ tools/ [等13个]
```

**项目独有目录** (1 个):
```
worktrees/
```

**共有目录** (12 个):
```
context/ examples/ hooks/ integrations/ memory/ prompts/
reference/ scripts/ skills/ statusline/ workflows/
```

### 2.2 Agents 配置

| 指标 | 全局 | 项目 |
|------|------|------|
| `.md` 文件数 | **42** | **0** |
| INDEX.md | ✅ 存在 | ⊘ **缺失** |

**全局 agents 结构**:
```
agents/
├── ai/ (4 files)
│   ├── deep-learning.md
│   ├── model-interpretability.md
│   ├── reinforcement-learning.md
│   └── time-series-analysis.md
├── ops/ (5 files)
├── research/ (4 files)
├── security/ (2 files)
├── testing/ (1 file)
├── visualization/ (1 file)
└── [根目录] (25 files)
```

**项目 agents 结构**: ⊘ **目录不存在**

**影响评估**: 🔴 **严重** — 项目侧无法执行 Agent 自动调度协议（§零），所有 intent-based routing 失效。

### 2.3 Skills 配置

| 指标 | 全局 | 项目 |
|------|------|------|
| `.md` 文件数 | 252 | 252 |
| INDEX.md | ✅ (6902 bytes) | ✅ (7222 bytes) |
| 状态 | 基准版本 | ⚠️ **领先版本** |

**Skills INDEX 差异**:

项目版新增 2 个 skills：
1. `source-evaluator` — 信息源评估器（伯乐），五维度评估学习材料质量
2. `hv-analysis-enhanced` — 增强版横纵分析法，延迟收敛式多视角决策支持

**建议**: 将这 2 个新 skill 同步到全局 INDEX.md。

**顶层结构差异**:

全局独有文件：
- `API-KEYS-SETUP.md`
- `CLI-SETUP-SUMMARY.md`
- `THIRD-PARTY-API-INVESTIGATION-SUMMARY.md`

项目独有目录：
- （仅文件结构差异，主要 skill 内容完全相同）

### 2.4 Commands 配置

| 指标 | 全局 | 项目 |
|------|------|------|
| `.md` 文件数 | **31** | **0** |
| 目录存在 | ✅ | ⊘ **不存在** |

**全局 commands 结构**:
```
commands/
├── ai-agent/ (1 file)
├── data-analysis/ (2 files)
├── dev/ (4 files)
├── general/ (14 files)
├── research/ (4 files)
└── security/ (2 files)
```

**影响评估**: 🔴 **严重** — 项目侧无法使用 `/ralph`, `/autopilot`, `/orchestrate` 等核心命令。

### 2.5 Workflows 配置

| 指标 | 全局 | 项目 |
|------|------|------|
| `.md` 文件数 | **15** | **0** |
| 目录存在 | ✅ 有 5 个子目录 | ✅ 目录存在但为空 |

**全局 workflows 子目录**:
```
workflows/
├── execution/
├── orchestration/
├── quality/
├── research/
└── routing/
```

**项目 workflows**: 目录存在但无内容文件。

**影响评估**: 🟡 **中等** — 缺少工作流模板，影响复杂任务编排的可复用性。

### 2.6 Memory 系统

| 文件 | 全局 | 项目 |
|------|------|------|
| `knowledge-strategy.md` | ✅ | ✅ |
| `best-practices.md` | ✅ | ⊘ |
| `lessons-learned.md` | ✅ | ⊘ |
| `error-patterns.md` | ✅ | ⊘ |
| `agent-performance.md` | ✅ | ⊘ |
| `optimization-history.md` | ✅ | ⊘ |
| `active-worktrees.md` | ✅ | ⊘ |

**影响评估**: 🟡 **中等** — 项目侧无法积累经验知识，每次任务都从零开始。

### 2.7 Hooks 配置

| 位置 | 全局 | 项目 |
|------|------|------|
| `hooks/` 目录 | ✅ 存在 | ✅ 存在 |
| `hooks/hooks.json` | ✅ 存在 (3496 bytes) | ⊘ **缺失** |
| 钩子脚本 | 多个 `.sh` 文件 | ⊘ **目录为空** |

**影响评估**: 🔴 **严重** — 项目侧无法执行：
- UserPromptSubmit Hook（Intent Detector，自动 Agent 调度核心）
- PreToolUse Hook（端口冲突检测）
- Stop Hook（Ralph 循环控制）
- PostToolUse Hook（自动记忆沉淀）

---

## 三、配置优先级验证

根据 CLAUDE.md 规定的配置优先级：

```
项目 .claude/settings.json → 全局 ~/.claude/settings.json → 默认
```

### 当前实际情况

1. **项目侧缺少 `settings.json`**，完全依赖全局配置
2. **项目侧有 `settings.local.json`** (2059 bytes)，但这不是标准配置文件名
3. **hooks.json 缺失**导致所有 Hook 协议在项目侧失效

### 预期行为 vs 实际行为

| 配置项 | 预期 | 实际 |
|--------|------|------|
| Agent 调度 | 项目级 hooks → 全局 hooks | ⚠️ 项目级 hooks 不存在，完全依赖全局 |
| Skills 加载 | 项目 skills → 全局 skills | ✅ 正常（两侧都有） |
| Agents 定义 | 项目 agents → 全局 agents | ⚠️ 项目侧无 agents，依赖全局 |
| Commands 可用性 | 项目 commands → 全局 commands | ⚠️ 项目侧无 commands，依赖全局 |

**结论**: 项目配置层几乎完全缺失，所有运行时行为由全局配置主导，违背了"项目覆盖全局"的设计原则。

---

## 四、差异类型分类汇总

### ✅ 正常（符合预期的差异）

1. 项目有 `settings.local.json`，包含项目特定权限
2. 项目有 `worktrees/` 目录（项目特定的 git worktree 管理）
3. Skills 内容文件数相同（252 个），表明 skills 已同步

### ⚠️ 冲突（需要决策）

1. **根 CLAUDE.md 版本不一致**
   - 项目版领先，包含"废弃规则管理协议"
   - 需决策：以项目版为准，同步到全局
   
2. **Skills INDEX.md 内容不一致**
   - 项目版新增 2 个 skills 注册
   - 需决策：同步到全局 INDEX.md

### 📦 孤立（只存在一侧）

**仅全局有（项目需要补齐）**:
- `agents/` 目录及全部 42 个定义文件 🔴
- `commands/` 目录及全部 31 个定义文件 🔴
- `workflows/` 目录及全部 15 个工作流 🟡
- `hooks/hooks.json` 及钩子脚本 🔴
- `memory/` 下 6 个知识库文件 🟡
- `config/` 下全部配置文件 🟡

**仅项目有（可保留或同步到全局）**:
- `worktrees/` 目录（项目特定，无需同步）
- `settings.local.json`（项目特定，无需同步）

### 🔄 待同步（一侧更新但另一侧未跟进）

**项目 → 全局**:
1. 根 CLAUDE.md 的"废弃规则管理协议"章节
2. Skills INDEX.md 中的 2 个新 skill 注册：
   - `source-evaluator`
   - `hv-analysis-enhanced`

**全局 → 项目**:
1. 整个 `agents/` 目录结构
2. 整个 `commands/` 目录结构
3. `workflows/` 目录内容
4. `hooks/hooks.json` 及钩子脚本
5. `memory/` 下的知识库文件
6. `config/` 下的配置文件

---

## 五、影响评估与风险等级

### 🔴 高风险（立即修复）

1. **项目侧缺少 hooks.json**
   - **影响**: Intent Detector 无法运行，自动 Agent 调度完全失效
   - **症状**: 每次任务都使用默认 orchestrator，无法根据 intent 自动切换专用 Agent
   - **修复优先级**: P0

2. **项目侧缺少 agents/ 目录**
   - **影响**: 即使 Intent Detector 运行，也无法加载对应 Agent 定义
   - **症状**: §零.2 步骤 4 的文件查找失败，回退到默认行为
   - **修复优先级**: P0

3. **项目侧缺少 commands/ 目录**
   - **影响**: 核心命令 `/ralph`, `/autopilot`, `/orchestrate` 等不可用
   - **症状**: 用户调用命令时找不到定义文件
   - **修复优先级**: P0

### 🟡 中风险（计划修复）

4. **项目侧缺少 workflows/ 内容**
   - **影响**: 无法使用预定义工作流模板，降低复杂任务执行效率
   - **修复优先级**: P1

5. **项目侧缺少 memory/ 知识库**
   - **影响**: 无法积累项目级经验，每次任务从零开始
   - **修复优先级**: P1

6. **根 CLAUDE.md 不一致**
   - **影响**: 全局配置缺少最新协议定义，可能导致行为不一致
   - **修复优先级**: P1

### 🟢 低风险（可选优化）

7. **项目侧缺少 config/ 文件**
   - **影响**: 无法做项目级配置覆盖，完全依赖全局配置
   - **当前**: 功能正常，因为全局配置可用
   - **修复优先级**: P2

---

## 六、修复建议与执行计划

### 6.1 立即执行（P0）

#### 任务 A: 同步 hooks.json 到项目

```bash
# 复制全局 hooks 配置到项目
cp "C:/Users/ASUS/.claude/hooks/hooks.json" \
   "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/.claude/hooks/"

# 复制所有 hook 脚本
cp "C:/Users/ASUS/.claude/hooks/"*.sh \
   "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/.claude/hooks/"
```

**验证方法**: 检查项目 hooks 目录不为空，hooks.json 可被解析。

#### 任务 B: 同步 agents/ 目录到项目

```bash
# 复制整个 agents 目录
cp -r "C:/Users/ASUS/.claude/agents" \
      "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/.claude/"
```

**验证方法**: 项目侧有 42 个 agent 定义文件，INDEX.md 存在。

#### 任务 C: 同步 commands/ 目录到项目

```bash
# 复制整个 commands 目录
cp -r "C:/Users/ASUS/.claude/commands" \
      "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/.claude/"
```

**验证方法**: 项目侧有 31 个 command 定义文件。

### 6.2 计划执行（P1）

#### 任务 D: 同步根 CLAUDE.md（项目 → 全局）

```bash
# 提取项目版的新增章节，手动合并到全局版
# 新增章节：§八 "废弃规则管理（Deprecation Protocol）"
```

**操作方式**: 人工 review 差异后合并，确保不丢失全局版的其他更新。

#### 任务 E: 同步 Skills INDEX.md（项目 → 全局）

```bash
# 在全局 INDEX.md 中添加 2 个新 skill 注册条目
# 1. source-evaluator
# 2. hv-analysis-enhanced
```

**验证方法**: 全局 INDEX.md 包含这 2 个条目。

#### 任务 F: 同步 workflows/ 内容到项目

```bash
# 复制整个 workflows 目录
cp -r "C:/Users/ASUS/.claude/workflows/"* \
      "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/.claude/workflows/"
```

**验证方法**: 项目侧有 5 个子目录，15 个 workflow 文件。

#### 任务 G: 同步 memory/ 知识库到项目

```bash
# 复制关键 memory 文件
for file in best-practices.md lessons-learned.md error-patterns.md \
            agent-performance.md optimization-history.md; do
  cp "C:/Users/ASUS/.claude/memory/$file" \
     "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/.claude/memory/"
done
```

**注意**: 检查是否需要合并 `knowledge-strategy.md`（两侧都有）。

### 6.3 可选执行（P2）

#### 任务 H: 建立项目级 config/ 覆盖

```bash
# 创建项目级 config 目录
mkdir -p "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/.claude/config"

# 复制基准配置
cp "C:/Users/ASUS/.claude/config/settings.json" \
   "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system/.claude/config/"

# 根据项目需求修改
```

**使用场景**: 当项目需要不同于全局的权限/模型/超时设置时。

---

## 七、配置同步维护策略

### 7.1 当前问题根因

项目配置不完整的原因推测：
1. 项目初始化时未完整克隆全局配置
2. 全局配置持续演进，但未定期同步到项目
3. 缺少自动化同步机制

### 7.2 未来维护建议

#### 建立定期审计机制

```bash
# 每季度执行一次完整配置审计
/orchestrate "执行全局与所有活跃项目的配置同步审计"
```

#### 关键更新的强制同步点

在以下场景下，必须手动同步配置：

1. **新增 Agent 定义** → 同步 `agents/` 和 `agents/INDEX.md`
2. **新增 Skill** → 同步 `skills/INDEX.md` 和 skill 文件
3. **新增/修改 Command** → 同步 `commands/`
4. **hooks.json 变更** → 同步到所有项目
5. **CLAUDE.md 核心协议更新** → 双向检查，以最新版为准

#### 建立配置版本标记

在 `CLAUDE.md` 头部增加版本号和最后同步日期：

```markdown
# 太一元系统核心配置 v1.1
# 发布: 2026-03-01 | 最后更新: 2026-06-10
# 最后同步: 2026-06-10 (全局 ↔ 项目)
```

#### 使用 Git 管理项目配置

将项目 `.claude/` 目录纳入版本控制：

```bash
cd "G:/GitHub_local/Self-built/Prompt/ClaudeCodePlan/claude-code-instruction-system"
git add .claude/
git commit -m "chore: sync global config to project"
```

**注意**: 排除临时文件和敏感信息：
- `.claude/context-mode/sessions/`
- `.claude/worktrees/`
- `.claude/settings.local.json`（如包含敏感权限）

---

## 八、附录：文件完整清单

### 8.1 全局配置文件总数

| 类别 | 数量 |
|------|------|
| 总配置文件（.md + .json） | 2282 |
| Agents | 42 |
| Skills | 252 |
| Commands | 31 |
| Workflows | 15 |

### 8.2 项目配置文件总数

| 类别 | 数量 |
|------|------|
| 总配置文件（.md + .json） | 4892 |
| Agents | 0 |
| Skills | 252 |
| Commands | 0 |
| Workflows | 0 |

**注**: 项目侧文件总数更多，主要是 `worktrees/` 目录下的大量临时文件。

### 8.3 关键文件哈希记录

| 文件 | 位置 | MD5 Hash |
|------|------|----------|
| CLAUDE.md | 全局 ~/.claude/ | `d268c9bd5363...` |
| CLAUDE.md | 项目根 | `33894e5f01d4...` |
| skills/INDEX.md | 全局 | `b6676d2cff8a...` |
| skills/INDEX.md | 项目 | `0542c2caeb88...` |
| hooks/hooks.json | 全局 | （未计算） |
| hooks/hooks.json | 项目 | N/A（不存在） |

---

## 九、总结

### 核心发现

1. **项目配置严重不完整**：agents/commands/workflows/hooks 全部缺失
2. **全局配置滞后**：缺少项目侧的"废弃规则管理协议"和 2 个新 skills
3. **配置同步机制缺失**：无定期审计和自动同步流程

### 立即行动项（优先级 P0）

- [ ] 同步 hooks.json 到项目（任务 A）
- [ ] 同步 agents/ 到项目（任务 B）
- [ ] 同步 commands/ 到项目（任务 C）

### 后续行动项（优先级 P1）

- [ ] 同步根 CLAUDE.md（项目 → 全局，任务 D）
- [ ] 同步 Skills INDEX.md（项目 → 全局，任务 E）
- [ ] 同步 workflows/ 到项目（任务 F）
- [ ] 同步 memory/ 到项目（任务 G）

### 长期改进

- [ ] 建立季度配置审计机制
- [ ] 在 CLAUDE.md 增加同步日期标记
- [ ] 将项目 `.claude/` 纳入 Git 管理
- [ ] 编写配置同步自动化脚本

---

**审计完成时间**: 2026-06-10 22:45  
**下一次审计计划**: 2026-09-10（季度审计）

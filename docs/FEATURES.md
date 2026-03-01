# 太一元系统特性文档
# 版本: 1.0 Taiyi (太一) - 道之演化
# 发布日期: 2026-03-01

> 本文件记录系统特性概览，供参考查阅。执行指令见 `CLAUDE.md`。

---

## 3.1 新特性一览

| 特性 | 命令/路径 | 说明 |
|------|-----------|------|
| **Ralph Loop** | `/ralph "任务"` | 自主循环执行直到完成 |
| **HUD Statusline** | `.claude/statusline/hud.sh` | 实时状态可视化 |
| **Intent Detector** | `hooks/intent-detector.sh` | 27种意图→22个Agent自动调度 |
| **Agent Auto-Dispatch** | `~/.claude/intent-state.json` | 自动加载Agent定义切换角色 |
| **Model Router** | `workflows/model-router.md` | 根据任务复杂度自动选模型 |
| **Plan-Scoped Memory** | `workflows/plan-scoped-memory.md` | 计划级知识隔离 |
| **Autopilot** | `/autopilot "任务"` | 端到端5阶段全自主执行 |
| **Research Parallel** | `workflows/research-parallel.md` | 多Agent并行科研工作流 |
| **TUI Config** | `taiyi-tui-config --path /project` | Rust+ratatui 交互式配置 |
| **HUD Renderer (Rust)** | `hud-render --theme nerd` | 7-10x 性能提升 |
| **Git Info Collector (Rust)** | `git-info status` | 5-8x 性能提升 |
| **Port Management** | `scripts/port-manager.py` | 跨项目端口冲突预防 |

---

## Autopilot 5阶段工作流

```
1. Planning     — 任务分解、策略选择
2. Specification — 规范生成、架构设计
3. Development  — Ralph Loop 执行 + Model Router
4. QA           — 自动审查、自愈修复
5. Delivery     — 文档生成、变更记录
```

```bash
/autopilot "开发用户认证系统"        # 默认监督模式
/autopilot full "快速原型开发"       # 完全自主
/autopilot supervised "重构支付模块" # 阶段审核
/autopilot step "数据库迁移"         # 每步确认
```

详见: `commands/general/autopilot.md`, `workflows/autopilot-flow.md`

---

## 主题系统

```bash
cc-patcher.sh theme nerd   # 切换主题（可用: default, minimal, nerd）
cc-patcher.sh themes       # 列出可用主题
```

---

## Port Management 端口管理

**自动触发机制**（PreToolUse Hook 拦截 Docker 命令）：
```bash
docker run -p 3307:3306 mysql  # ⚠️ 自动警告：端口冲突
docker run -p 9999:80 nginx    # ✅ 自动通过：端口空闲
```

**手动管理**：
```bash
python scripts/port-manager.py register 3307 myproject mysql -d "主数据库"
python scripts/port-manager.py conflicts
python scripts/port-manager.py suggest mysql
python scripts/port-manager.py export myproject --output myproject.env
```

详见: `docs/PORT-MANAGEMENT-GUIDE.md`, `docs/PORT-MANAGEMENT-ARCHITECTURE.md`

---

## Research Parallel 并行策略

| 场景 | 策略 | 加速比 |
|------|------|--------|
| 文献综述 | SWARM (5 workers) | 3.3x |
| 实验执行 | PARALLEL (4 workers) | 2.3x |
| 数据分析 | HIERARCHICAL (lead+workers) | 2-3x |

```bash
/literature-review "主题" --parallel --workers 5
/experiment-track parallel --workers 4
```

详见: `workflows/research-parallel.md`

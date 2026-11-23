# 改进方案运行时契约

日期：2026-11-23。RISK-MEDIUM；本契约校正三份原始方案中的示例，作为实现和验收依据。

## 范围与接口

- 复用 `scripts/taiyi/` 标准库模块，不建立第二套 `.claude/agents` 或 Hook 目录。
- `scripts/taiyi-tool.py` 提供 route、search、rebuild、playbook、record、analyze、session、summarize、aggregate、cache、evidence、audit 子命令。
- `hooks/context-optimizer.py` 是可选 `context-optimization` 安装组件，接收 Claude Hook JSON。覆盖 PreToolUse、PostToolUse、PostToolUseFailure、PreCompact、SessionStart；可注入事件仅返回 additionalContext，PreCompact 不注入，不 allow/deny、不改参数、不执行任务。用户提示路由保持既有显式命令入口。
- 状态按项目绝对路径和 session_id 分区，放项目 `.claude/taiyi/`；全局安装的知识仍从安装根目录读取。显式缺少会话标识时 WARNING 并跳过持久化。
- 读取建议：同目录连续 3 次 Read、连续 3 次 Grep、未限制范围的大文件读取。第 4–8 次缩减提醒，第 9 次起只建议批量；不阻断工具。编辑或其他操作打断连续计数。
- 原始输出无法由普通 PostToolUse 替换。真正聚合在 aggregate/summarize 工具内先计算再输出；不会声称 Hook 自动省 token。
- 搜索递归索引 Markdown，SQLite FTS5 + 子串后备 + 拼写纠错；内容哈希检查重建，事务更新，缺少 FTS5 时 WARNING 后降级。返回有来源的有界片段。
- Playbook 使用 JSON 注册表指定 latest，避免 Windows 符号链接。只推荐已匹配流程，历史复用仅参考成功记录，不执行其命令。实际反馈才更新成功率。
- 证据采用 JSON frontmatter（YAML 的兼容子集）或 Markdown 的相邻 JSON 台账；旧 Markdown 原样读取。5 种证据类型，confidence 是作者判断而非测得概率。静态引用、测试运行、外部无法核实分别报告；不执行证据中任意命令。
- 失败 Hook 只记录脱敏错误特征，不自动改写规则或宣称已修复。复盘输出候选建议，规则晋升仍遵守两次独立事故证据门槛。

## 风险、回滚与边界

不增加依赖，不修改权限设置，不安装外部系统；已有安全 Hook 保持独立。日志可能含路径和任务摘要，组件显式启用，敏感内容脱敏，有界存储；磁盘、锁、JSON、SQLite 损坏均 WARNING，不伪造结果。撤销组件注册即可停止 Hook，保留知识和历史状态；不自动清理历史记忆。

外部 Context Mode、Agentero/Agnes、Craft Anything 仅列为备选评估，不使用文章中的安装示例或未核实许可/性能数据作为事实。

## 验收

### 全局启用前的 Hook 优化（2026-11-23）

用户已明确授权修改真实全局配置并推送。本次优化减少无状态工具的磁盘写入，对有 limit 的分段 Read 不作批量提醒，普通连续读取/搜索只在第 3、6、9 次及之后每 9 次提醒；同一大文件只在首次读取时作流式建议。PostToolUse 事件与决策反馈合并为一次原子更新；无匹配反馈不写文件。保持失败 WARNING、项目/会话隔离和既有安全 Hook。部署仅增量安装 context-optimization 组件，保留已有其他组件和个人权限；安装器自动备份 settings，失败时从该快照恢复。不发送真实通知。

1. 测试 Hook stdin/stdout、连续计数、会话与项目隔离、并发、损坏、失败记录和 compact 恢复。
2. 测试递归索引、修改/删除/版本失配、模糊查询、中文、无 FTS5 后备。
3. 测试四层路由、失败优先、模糊任务兜底、版本选择、反馈统计和复盘。
4. 测试证据格式、范围校验、循环/失效引用、旧格式、审计非零退出；保留旧记忆，新增 10 条有当前仓库来源的策展索引。
5. 临时 target 安装、幂等合并、个人 Hook/权限保留、可选组件撤销。运行既有相关回归和静态检查。
6. 基准输出真实本地延迟与字节压缩比；只有输入真实 token 计数才报告 token 节省。长期成功率、3 个外部项目、会话延长列为待观测，不以合成测试冒充。

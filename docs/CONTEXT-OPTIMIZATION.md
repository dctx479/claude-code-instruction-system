# 上下文优化与轻量路由

本模块是推荐方案 A 的标准库实现。它提供先计算再输出、按需检索、版本化流程和会话事件恢复；收益需要实测，不能从字节压缩比推断整场 token 节省。

## 使用

从仓库根执行：

```bash
python scripts/taiyi-tool.py route "统计目录文件行数"
python scripts/taiyi-tool.py aggregate scripts/taiyi --pattern "*.py"
python scripts/taiyi-tool.py aggregate hooks --pattern "*.py" --operation grep --needle WARNING
python scripts/taiyi-tool.py summarize --file <日志文件>
python scripts/taiyi-tool.py search "backup collision"
python scripts/taiyi-tool.py rebuild
python scripts/taiyi-tool.py playbook install-global
python scripts/taiyi-tool.py playbook install-global --version v1.0
```

全局安装使用 `$HOME/.claude/scripts/taiyi-tool.py`，默认知识根是该安装目录的 memory。状态根用 `--root <项目>`，必须放在子命令前；查询其他知识用 `--memory <目录>`。

route 返回 use_script / use_playbook / repeat_previous / avoid_known_failure / delegate_to_llm。返回值只推荐处理方式，参数不会拼接成命令；兜底由当前 Agent 继续判断。任何路由都不自动启动子代理或调用付费模型。

## 可选 Hook

显式选择 `context-optimization` 组件才注册优化 Hook。建议先向临时目标安装和验证：

```bash
python scripts/install-global.py --dry-run --target <临时目录> --components hooks,commands,context-optimization
python scripts/install-global.py --target <临时目录> --components hooks,commands,context-optimization
python scripts/verify-global-install.py --target <临时目录> --components hooks,commands,context-optimization
```

真实用户目录安装需在用户授权范围执行。首次实现仅验证临时目录；本轮用户已明确授权真实全局部署，记录见 [实施状态](IMPROVEMENT-IMPLEMENTATION.md)。默认 Hook 不增加优化提醒。

优化 Hook 的 PreToolUse 提醒连续同目录 Read/Grep 和未限定范围的大文件读取；有正整数 limit 的分段 Read、编辑/其他操作会重置计数。普通连续调用只在第 3、6、9 次及之后每 9 次提醒，大文件的流式建议在首次读取时给出，不阻断工具或改变参数。无关工具和未命中反馈不写状态；工具事件与决策反馈合并为一次原子更新。所有依赖失败、损坏、锁冲突都在 stderr 输出 WARNING。锁等待最多 500ms，注册超时 5 秒；普通路径延迟见本地基准，不能保证所有磁盘下 <100ms。

PostToolUse 不能替换已经进入上下文的原始输出，因此不做重复摘要注入。实际减少输出应使用 aggregate 或把已授权命令输出直接管道给 summarize；聚合器保留计数和少量错误/命中样本，丢失细节时需按来源补读。它不是 OS 沙箱，不执行任意脚本。命令安全检查仍由已有安全 Hook 处理。

## 会话、反馈与复盘

```bash
python scripts/taiyi-tool.py --root <项目> --session <标识> route "全局安装" --record
python scripts/taiyi-tool.py --root <项目> --session <标识> record <决策id> success --duration-ms 420
python scripts/taiyi-tool.py --root <项目> --session <标识> analyze
python scripts/taiyi-tool.py --root <项目> --session <标识> session add --kind decision --text "采用标准库方案"
python scripts/taiyi-tool.py --root <项目> --session <标识> session snapshot
python scripts/taiyi-tool.py --root <项目> --session <标识> session recall --text backup
```

状态放在项目 `.claude/taiyi/`，项目路径和 session_id 都哈希分区。Hook 项目根优先 CLAUDE_PROJECT_DIR，文件路径按事件 cwd 解析。最多保留最近 200 条事件和 200 条决策，快照保存最近 30 条事件；不会删除原始记忆。缺少 session_id 跳过持久化并 WARNING。

自动记录相对项目根的编辑路径、git 操作类别、任务状态和失败特征；项目外编辑只记录类别，连续调用的目录/文件键使用哈希，不记录命令参数、原始响应或完整 prompt。自定义决定通过 session add 显式写入，写前自行避免敏感内容。日志会脱敏常见 key/token，但不能保证识别所有秘密。PreCompact 只保存快照；compact/resume 的 SessionStart 注入最多 4 条参考事件。新 session_id 可用旧 id 的 session recall 手动交接，仍须使用 checkpoint 复核工作状态。

Hook 提醒记录为决策，按 tool_use_id 关联实际工具结果。此结果表示原始工具成功/失败，不证明优化建议被采用。CLI 的 record 需回填实际结果；成功率不等于路由准确率，未测成本、准确率保持 null。analyze 输出按 Playbook 版本的成功率、高频任务和失败/超时复盘候选，不自动改规则。

## 缓存和检索

```bash
python scripts/taiyi-tool.py cache put https://example.test/doc --file <已获取文档> --ttl 86400
python scripts/taiyi-tool.py cache get https://example.test/doc --query "配置"
```

缓存显式写入，不访问网络或拦截 WebFetch。URL 以哈希作文件名，条目有内容哈希、TTL、2 MiB 原文上限，总量限制为 200 条/50 MiB；超出容量拒绝新写入并报告错误。返回最多约 900 字符片段；miss/过期返回退出码 2，不假装命中。过期内容保留为本地记录，不自动批量删除。

记忆索引递归扫描非隐藏 Markdown，检查内容哈希自动重建；FTS5 BM25 排序与子串召回通过 RRF 合并，支持中文子串、邻近度重排和拼写后备。不是语义向量检索，也不是完整 Context Mode 算法复刻。无 FTS5 时 WARNING 并用子串后备；数据库损坏返回错误，保留原文，不覆盖损坏库。检查后可手动移动损坏库备份，再 rebuild。

## 验证与回滚

```bash
python -m unittest discover -s tests -p "test_improvement_runtime.py" -v
python scripts/test-decision-scenarios.py
python scripts/benchmark.py --output .claude-tmp/improvement-benchmark.json
python scripts/measure-token-savings.py <实测JSONL>
```

JSONL 可以包含 raw_tokens/actual_tokens 或 raw_bytes/actual_bytes。两者分别报告；真实 token 比较应包括脚本、指令和二次读取，并保证任务结果一致。基准的日志/文件压缩是合成 fixture，不能当成真实会话成本。

回滚：重新安装相同组件集合但移除 context-optimization（保留 hooks 组件）会撤销该 Hook，保留个人 Hook 和权限。或恢复安装备份中的 settings 后重启。运行态和知识保留供核对。

完整外部系统与未验证指标见 [实施状态](IMPROVEMENT-IMPLEMENTATION.md)。

---
paths:
  - "hooks/**"
  - "scripts/**/*.sh"
  - "scripts/install-global.py"
  - "config/claude-global.md"
  - ".claude/statusline/**"
---

# Hook 与安装器维护约束

- Hook stdin 是 JSON，使用 JSON 解析器处理引号、换行和 Unicode，不能用正则拆 JSON。
- UserPromptSubmit 读 prompt；工具事件读 tool_name/tool_input；Stop 不是会话结束。
- stdin 的 session_id/cwd 用于隔离状态；路径或文件名使用前须规范化，不能信任其可作路径。
- stdout 是协议/本轮上下文；诊断写 stderr，包含 WARNING，不输出整条用户 prompt 到日志。
- 正常无匹配不是错误；依赖缺失、配置损坏和解析失败必须报告。
- 可选推荐失败可降级为空；权限、安全判断失败不能自动放行或声称验证通过。
- set -euo pipefail 下明确处理预期失败；禁止掩盖异常的静默 fallback。
- hooks/hooks.json 供安装器合并；不将它误认为已加载的配置。
- 全局脚本用 $HOME/.claude/...；项目脚本用 $CLAUDE_PROJECT_DIR/...，不依赖当前 cwd。
- command hook 的 timeout 按秒配置；需要阻塞时按事件协议使用退出码 2。
- matcher 使用字符串正则；Agent 工具兼容 matcher 为 Agent|Task。
- 修改后验证 JSON、Bash 语法、真实输入输出、错误分支以及 Windows 路径。
- 路由上下文来自本轮 stdout；全局 intent-state.json 仅作旧 HUD 快照，禁止用于会话决策。
- Ralph 全局状态必须携带 project_dir，防止阻塞其他项目；schema 见 commands/general/ralph.md。
- install-global.py 的 core 只安装跨项目模板；已有自定义全局指令需保留，显式要求替换才覆盖。
- 发布配置前先 dry-run；未明确要求全局同步时只验证沙箱，不自动改真实用户配置。

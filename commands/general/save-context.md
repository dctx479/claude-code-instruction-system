# 保存上下文

手动触发对话归档，将当前对话提炼为结构化上下文。

## 用法

```bash
/save-context
```

## 功能

将当前对话导出并调用 LLM 提炼为：
- `.claude/context/index.json` - 项目状态、已验证事实、下一步行动
- `.claude/context/resolutions/{timestamp}.ndjson` - 问题解决方案详情

## 执行步骤

1. 导出当前对话到临时文件
2. 运行: `python scripts/archive-context.py <conversation_file>`
3. 查看归档: `python scripts/read-context.py index`

## 示例

```bash
# 1. 手动导出对话（复制当前对话内容到文件）
# 2. 运行归档
python scripts/archive-context.py conversation.txt

# 3. 查看结果
python scripts/read-context.py index
python scripts/read-context.py list
python scripts/read-context.py resolution res-001
```

## 输出格式

### index.json
- project: 项目名称
- current_state: 当前状态
- verified_facts: 已验证事实
- next_actions: 下一步行动
- detail_index.resolutions: 问题解决方案索引

### resolutions.ndjson
每行一个 JSON 对象：
- problem_signature: 错误关键词（用于检索）
- final_fix: 最终修复步骤
- anti_patterns: 反模式（1-3 条无效尝试）
- verification: 验证方法

## 最佳实践

**何时保存**：
- 解决复杂问题后
- 完成重要功能后
- 对话即将结束前

**何时不保存**：
- 纯信息查询
- 任务未完成
- 短时间内重复保存

---

**相关脚本**:
- `scripts/archive-context.py` - 归档脚本
- `scripts/read-context.py` - 读取脚本

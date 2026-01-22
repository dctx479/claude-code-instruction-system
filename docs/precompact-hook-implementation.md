# PreCompact Hook 实现文档

## 概述

PreCompact Hook 在 Claude Code 执行 `/compact` 命令前自动触发，提取并归档对话中的关键知识，防止上下文压缩导致的知识丢失。

## 架构设计

```
/compact 触发
    ↓
pre-compact.sh (Hook)
    ↓
检查触发条件 (token/消息数阈值)
    ↓
archive-context.py (归档脚本)
    ↓
提取知识 (错误-修复对、技术决策、代码模式)
    ↓
生成 JSON 归档文件
    ↓
保存到 .claude/memory/context-archives/
```

## 文件结构

```
.claude/hooks/pre-compact.sh          # Hook 入口脚本
scripts/archive-context.py            # 归档处理脚本
scripts/test-archive.sh               # 测试脚本
.claude/memory/context-archives/      # 归档文件目录
```

## 触发条件

Hook 在以下条件下执行归档：

- **Token 阈值**: ≥ 150,000 tokens
- **消息数阈值**: ≥ 50 条消息
- **逻辑**: 满足任一条件即触发

低于阈值时跳过归档，避免不必要的开销。

## 知识提取算法

### 1. 错误-修复对识别

```python
# 检测包含 "error" 或 "failed" 的消息
# 查找下一条包含 "fix" 的消息作为解决方案
if "error" in content.lower():
    if next_msg contains "fix":
        记录错误-修复对
```

### 2. 技术决策识别

```python
# 检测 assistant 消息中的决策关键词
if role == "assistant" and ("决定" or "选择" or "采用" in content):
    记录技术决策
```

### 3. 代码模式识别

```python
# 检测代码块标记
if "```" in content:
    记录代码模式
```

## 归档文件格式

```json
{
  "version": "1.0",
  "archived_at": "2026-01-22T07:03:58+00:00",
  "session_id": "session-id",
  "metadata": {
    "message_count": 80,
    "token_count": 180000,
    "duration": 0
  },
  "knowledge": {
    "errors": [
      {
        "error": "错误描述",
        "solution": "解决方案",
        "timestamp": "2026-01-22T10:00:00Z"
      }
    ],
    "decisions": [
      {
        "decision": "决策内容",
        "timestamp": "2026-01-22T10:00:00Z"
      }
    ],
    "patterns": [
      {
        "code": "代码片段",
        "timestamp": "2026-01-22T10:00:00Z"
      }
    ]
  },
  "summary": "归档 X 个错误, Y 个决策, Z 个模式"
}
```

## 错误处理

- **失败不阻塞**: 归档失败不影响 compact 执行
- **日志输出**: 所有操作输出清晰日志
- **编码处理**: Windows 环境自动处理 UTF-8 编码
- **异常捕获**: Python 脚本捕获所有异常并返回错误码

## 使用方法

### 自动触发

当 Claude Code 执行 `/compact` 时自动触发，无需手动操作。

### 手动测试

```bash
# 运行完整测试套件
bash scripts/test-archive.sh

# 手动触发 Hook (模拟高阈值场景)
export CLAUDE_TOKEN_COUNT=160000
export CLAUDE_MESSAGE_COUNT=60
bash .claude/hooks/pre-compact.sh

# 直接测试归档脚本
python scripts/archive-context.py test-data.json
```

## 测试结果

```
测试 1: 低阈值场景 ✓
  - tokens: 1000, messages: 10
  - 结果: 跳过归档

测试 2: 高阈值场景 ✓
  - tokens: 160000, messages: 60
  - 结果: 执行归档，生成 JSON 文件

测试 3: 知识提取 ✓
  - 输入: 4 条消息
  - 输出: 2 个决策
  - 文件: archive-YYYYMMDD-HHMMSS.json
```

## 环境变量

Hook 使用以下环境变量（由 Claude Code 提供）：

- `CLAUDE_TOKEN_COUNT`: 当前上下文 token 数
- `CLAUDE_MESSAGE_COUNT`: 当前消息数
- `CLAUDE_SESSION_ID`: 会话 ID
- `TRIGGER_CONTEXT_ARCHIVE`: 标记触发归档（Hook 设置）

## 性能考虑

- **轻量级**: 提取算法简单高效
- **异步友好**: 可扩展为异步执行
- **存储优化**: 仅保存关键信息摘要（200-300 字符）
- **批量处理**: 支持批量归档多个会话

## 扩展方向

1. **增强提取算法**
   - 使用 NLP 识别更复杂的模式
   - 提取实体关系和知识图谱
   - 自动分类和标签

2. **集成 Graphiti**
   - 将归档数据导入知识图谱
   - 建立跨会话知识关联
   - 支持语义搜索

3. **智能推荐**
   - 基于历史归档推荐解决方案
   - 识别重复问题并提醒
   - 生成最佳实践文档

4. **可视化分析**
   - 生成知识演化时间线
   - 展示错误模式分布
   - 分析决策效果

## 维护指南

### 定期清理

```bash
# 删除 30 天前的归档文件
find .claude/memory/context-archives/ -name "*.json" -mtime +30 -delete
```

### 归档合并

```bash
# 合并多个归档文件为月度报告
python scripts/merge-archives.py --month 2026-01
```

### 质量检查

```bash
# 验证归档文件格式
python scripts/validate-archives.py
```

## 故障排查

### 问题: Hook 未触发

- 检查 `.claude/hooks/pre-compact.sh` 是否可执行
- 验证环境变量是否正确设置
- 查看 Claude Code 日志

### 问题: 归档失败

- 检查 Python 是否安装 (`python --version`)
- 验证目录权限
- 查看错误日志输出

### 问题: 编码错误

- 确保 `PYTHONIOENCODING=utf-8` 已设置
- 检查文件保存编码为 UTF-8
- Windows 用户确认控制台支持 UTF-8

## 更新日志

- **2026-01-22**: 初始实现
  - 基础 Hook 框架
  - 知识提取算法
  - 测试套件
  - 文档完善

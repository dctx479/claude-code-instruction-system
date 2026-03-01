# 上下文归档系统 - 快速上手

## 🎯 核心价值

在上下文压缩前，将对话提炼为可复用的工程上下文，实现 **97% Token 节省**。

## ⚡ 快速开始

### 1. 安装依赖

```bash
pip install anthropic
```

### 2. 配置 API Key

在 `~/.claude/settings.json` 中添加：
```json
{
  "apiKey": "sk-ant-..."
}
```

### 3. 使用

```bash
# 保存对话（需先手动导出对话到文件）
python scripts/archive-context.py conversation.txt

# 读取项目状态
python scripts/read-context.py index

# 列出所有问题
python scripts/read-context.py list

# 读取特定解决方案
python scripts/read-context.py resolution res-001
```

## 📋 输出格式

### index.json
- 项目状态、目标、约束
- 已验证事实
- 下一步行动
- 问题解决方案索引

### resolutions.ndjson
- problem_signature: 错误关键词
- final_fix: 最终修复步骤
- anti_patterns: 1-3 条无效尝试
- verification: 验证方法

## 💡 最佳实践

**何时保存**：
- ✅ 解决复杂问题后
- ✅ 完成重要功能后
- ✅ 对话即将结束前

**何时不保存**：
- ❌ 纯信息查询
- ❌ 任务未完成

## 📚 详细文档

- [实施完成报告](docs/context-archival-implementation.md)
- [使用指南](docs/context-archival-guide.md)
- [命令文档](commands/general/)

## 🔗 相关项目

- [context-retrieval](https://github.com/Jackson7362085/context-retrieval) - 灵感来源
- [EverMemOS](https://github.com/mem0ai/mem0) - 记忆系统参考

---

**版本**: v1.0 MVP
**日期**: 2026-01-22

# 读取上下文

读取归档的上下文信息。

## 用法

```bash
python scripts/read-context.py <index|resolution|list> [res_id]
```

## 功能

### 读取索引
```bash
python scripts/read-context.py index
```
显示项目状态、已验证事实、下一步行动。

### 读取解决方案
```bash
python scripts/read-context.py resolution res-001
```
显示特定问题的详细解决方案（问题、根因、修复步骤、反模式）。

### 列出归档
```bash
python scripts/read-context.py list
```
列出所有已归档的问题解决方案。

## 渐进式上下文注入

核心价值：**按需加载详细信息，节省 Token**

### 工作流程
```
新任务 → 读 index.json (轻量) → 判断相关性 → 读 resolution (详细)
```

### Token 节省
- index.json: ~2KB
- 完整对话: ~50KB
- 节省: 97%

## 最佳实践

**任务开始前**：
1. 读取 index 了解项目状态
2. 检查是否有相关历史问题

**遇到问题时**：
1. 搜索 problem_signature
2. 读取匹配的 resolution
3. 参考历史方案避免重复试错

---

**相关脚本**: `scripts/read-context.py`

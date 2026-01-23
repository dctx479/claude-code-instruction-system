# OpenAPI to Claude Code Skill Converter

自动将 OpenAPI 规范转换为 Claude Code Skill。

## 安装

```bash
cd tools/openapi-converter
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python converter.py <openapi-file> --name "Skill Name"
```

### 示例

```bash
# 转换 JSON 格式的 OpenAPI
python converter.py api-spec.json --name "My API Helper"

# 转换 YAML 格式的 OpenAPI
python converter.py api-spec.yaml --name "My API Helper"

# 指定输出目录
python converter.py api-spec.json \
  --name "My API Helper" \
  --output .claude/skills/my-api

# 指定核心端点数量
python converter.py api-spec.json \
  --name "My API Helper" \
  --core-endpoints 30
```

## 生成的文件结构

```
.claude/skills/my-api-helper/
├── SKILL.md                 # 核心 Skill 文件（轻量级）
├── REFERENCE.md             # 完整 API 文档
├── openapi.json             # 原始 OpenAPI 规范
├── scripts/
│   ├── __init__.py
│   ├── api_client.py       # API 客户端
│   └── search.py           # 端点搜索工具
└── index/
    ├── keywords.json       # 关键词索引
    └── endpoints.json      # 端点元数据
```

## 功能特性

- ✅ 支持 OpenAPI 2.0, 3.0, 3.1
- ✅ 支持 JSON 和 YAML 格式
- ✅ 自动提取核心端点
- ✅ 生成关键词搜索索引
- ✅ 生成 API 客户端代码
- ✅ 生成端点搜索工具
- ✅ 识别认证方式
- ✅ 按 tag 分组端点

## 核心端点选择算法

转换器会根据以下标准自动选择最重要的端点：

1. **HTTP 方法权重**：
   - GET: 1.0
   - POST: 1.2
   - PUT/PATCH: 0.8
   - DELETE: 0.6

2. **文档完整性**：
   - 有 summary: +0.5
   - 有 description: +0.3
   - 有 operationId: +0.2

3. **参数复杂度**：
   - 无参数: +1.0
   - 1-3 个参数: +0.7
   - 4+ 个参数: +0.4

## 使用生成的 Skill

生成 Skill 后，Claude 会自动发现并激活它：

```markdown
"使用 My API Helper 获取用户信息"
→ 自动激活 my-api-helper Skill
→ 搜索相关端点
→ 调用 API 并返回结果
```

## 故障排查

### 问题：无法解析 OpenAPI 文件

**解决方案**：
- 验证文件格式（JSON/YAML）
- 检查 OpenAPI 版本
- 使用在线验证工具检查规范

### 问题：生成的 Skill 过大

**解决方案**：
- 减少核心端点数量：`--core-endpoints 10`
- 详细文档已自动移到 REFERENCE.md

### 问题：搜索结果不准确

**解决方案**：
- 改进 OpenAPI 规范中的 summary 和 description
- 使用更具体的搜索关键词

## 开发

### 运行测试

```bash
# 使用示例 OpenAPI 文件测试
python converter.py examples/petstore.json --name "Pet Store API"
```

### 扩展功能

可以扩展的功能：
- 语义搜索（使用 sentence-transformers）
- 自动生成测试用例
- 支持更多认证方式
- 生成 TypeScript 客户端

## 相关文档

- **命令文档**: `commands/dev/convert-openapi.md`
- **Skills 指南**: `.claude/skills/README.md`
- **使用示例**: `examples/openapi-conversion-example.md`

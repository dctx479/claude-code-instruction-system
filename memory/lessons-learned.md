# 经验教训库 (Lessons Learned)

> 自动维护的知识库，记录错误、解决方案和最佳实践
> 每次遇到问题或完成复杂任务后自动更新

---

## 使用说明

### 添加新条目
```markdown
## [YYYY-MM-DD] 条目标题 #ID

### 问题描述
[具体描述遇到的问题]

### 根因分析
[分析问题产生的根本原因]

### 解决方案
[如何解决这个问题]

### 配置更新
[对系统配置的更新，如果有]
- 文件: [文件路径]
- 变更: [具体变更内容]

### 验证方法
[如何验证问题已解决]

### 标签
[相关标签，如: #agent #parallel #error-handling]
```

### 查询经验
- 按日期: 查看最近的经验
- 按标签: 搜索特定领域的经验
- 按问题类型: 查找类似问题的解决方案

---

## 经验条目

### [初始化] 系统启动 #000

### 问题描述
首次使用系统，需要建立基础经验库

### 解决方案
创建初始结构，等待实际使用中的经验积累

### 标签
#initialization #system

---

## [2026-01-23] OpenAPI 转换器 Windows 编码问题修复 #001

### 问题描述
在 Windows 系统上运行 OpenAPI 转换器时，遇到 `UnicodeEncodeError: 'gbk' codec can't encode character` 错误。转换器中使用了 emoji 和中文字符，但 Windows 默认使用 GBK 编码，导致输出失败。

### 根因分析
- Windows 系统默认使用 GBK 编码作为标准输出编码
- Python 脚本中使用了 UTF-8 字符（emoji 和中文）
- 当 print 函数尝试输出这些字符时，GBK 编码无法处理，导致异常

### 解决方案
在脚本开头添加编码设置代码：

```python
import sys
import io

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

### 配置更新
- 文件: `tools/openapi-converter/converter.py`
- 变更: 在文件开头添加 UTF-8 编码设置，确保 Windows 系统兼容性

### 验证方法
1. 在 Windows 系统上运行转换器
2. 确认可以正常输出 emoji 和中文字符
3. 验证转换流程完整执行

### 标签
#encoding #windows #python #openapi-converter

---

## [2026-01-23] OpenAPI 转换器成功集成 TikHub API #002

### 问题描述
需要将 TikHub API 集成到太一元系统，使用 OpenAPI 转换器自动生成 Skill。

### 解决方案
1. 创建示例 OpenAPI 规范文件（`tikhub-sample.json`）
2. 修复 Windows 编码问题
3. 运行转换器生成 Skill
4. 验证生成的文件结构和内容

### 生成的文件
```
.claude/skills/tikhub-api-helper/
├── SKILL.md                 # 核心 Skill 文件（1.7KB）
├── REFERENCE.md             # 完整 API 文档（2.4KB）
├── openapi.json             # 原始 OpenAPI 规范（8.3KB）
├── scripts/
│   ├── api_client.py       # API 客户端
│   └── search.py           # 端点搜索工具
└── index/
    ├── keywords.json       # 关键词索引
    └── endpoints.json      # 端点元数据
```

### 核心端点（10个）
1. GET /trending/topics - 获取热门话题
2. GET /trending/videos - 获取热门视频
3. GET /users/{user_id} - 获取用户信息
4. GET /users/{user_id}/videos - 获取用户视频列表
5. GET /videos/{video_id} - 获取视频详情
6. GET /videos/{video_id}/comments - 获取视频评论
7. GET /search/users - 搜索用户
8. GET /search/videos - 搜索视频
9. GET /hashtags/{hashtag_id} - 获取话题详情
10. GET /hashtags/{hashtag_id}/videos - 获取话题视频

### 配置更新
- 文件: `tools/openapi-converter/examples/tikhub-sample.json`
- 变更: 创建 TikHub API 示例规范

### 验证方法
1. 检查生成的文件结构完整
2. 验证 SKILL.md 包含所有核心端点
3. 确认 API 客户端和搜索工具正确生成
4. 验证关键词索引和端点元数据正确

### 经验总结
- OpenAPI 转换器可以在 10 分钟内完成 API 集成
- 自动生成的 Skill 包含完整的搜索和调用功能
- 渐进式披露机制确保 Token 高效使用
- 转换器支持 JSON 和 YAML 格式的 OpenAPI 规范

### 标签
#openapi-converter #api-integration #tikhub #skill-generation

---

<!-- 新的经验条目将自动添加在这里 -->


# Zotero-MCP 集成指南

## 简介
Zotero-MCP 允许 Claude Code 直接访问你的 Zotero 文献库，进行文献检索、摘要、引用分析等操作。

## 安装步骤

### 1. 安装 Zotero
- 下载并安装 [Zotero](https://www.zotero.org/)
- 创建账号并同步文献库

### 2. 获取 API Key
1. 访问 https://www.zotero.org/settings/keys
2. 创建新的 API Key
3. 权限设置：
   - ✅ Allow library access
   - ✅ Allow notes access
   - ✅ Allow write access（可选）

### 3. 配置 MCP Server

在 Claude Code 配置文件中添加：

**macOS/Linux**: `~/.config/claude-code/mcp_settings.json`
**Windows**: `%APPDATA%\claude-code\mcp_settings.json`

```json
{
  "mcpServers": {
    "zotero": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-zotero"],
      "env": {
        "ZOTERO_API_KEY": "your-api-key-here",
        "ZOTERO_USER_ID": "your-user-id-here"
      }
    }
  }
}
```

### 4. 获取 User ID
- 访问 https://www.zotero.org/settings/keys
- User ID 显示在页面顶部

### 5. 重启 Claude Code
```bash
# 重启以加载 MCP 配置
```

## 使用示例

### 搜索文献
```
帮我在 Zotero 中搜索关于"深度学习医学图像分割"的论文
```

### 总结文献集合
```
总结 Zotero 中"Coronary CTA"集合的所有论文
```

### 引用分析
```
分析 Zotero 中最近添加的 10 篇论文的引用关系
```

### 生成综述
```
基于 Zotero 中"AI in Healthcare"集合，生成文献综述
```

## 最佳实践

### 1. 文献组织
- 使用 Collections 分类文献
- 添加标签（Tags）便于检索
- 填写完整的元数据

### 2. 质量控制
- 优先收集闭源期刊高质量论文
- 补充开源数据库（arXiv, PubMed）
- 定期清理和更新文献库

### 3. 与 Claude Code 协作
- 先在 Zotero 中准备文献
- 让 Claude Code 访问和分析
- 人工审核 AI 生成的内容

## 故障排查

### MCP Server 未启动
```bash
# 检查 MCP 配置
cat ~/.config/claude-code/mcp_settings.json

# 手动测试 MCP Server
npx -y @modelcontextprotocol/server-zotero
```

### API Key 无效
- 检查 API Key 是否正确
- 确认权限设置
- 重新生成 API Key

### 无法访问文献库
- 确认 User ID 正确
- 检查网络连接
- 确认 Zotero 账号已同步

## 相关资源
- [Zotero 官方文档](https://www.zotero.org/support/)
- [Zotero-MCP GitHub](https://github.com/modelcontextprotocol/servers/tree/main/src/zotero)
- [MCP 协议文档](https://modelcontextprotocol.io/)

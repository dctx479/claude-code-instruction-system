基于当前已暂存和未暂存的更改创建一个规范的 Git 提交。

## 执行步骤

1. **查看更改**
   ```bash
   git status
   git diff --staged
   git diff
   ```

2. **分析更改内容**
   - 理解每个文件的修改目的
   - 确定更改的类型 (feat/fix/docs/refactor/test/chore)

3. **生成提交信息**
   遵循 Conventional Commits 规范:
   ```
   <type>(<scope>): <description>

   [optional body]

   [optional footer(s)]
   ```

4. **执行提交**
   - 暂存相关文件 (如果需要)
   - 创建提交

## 提交类型
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 格式调整 (不影响代码逻辑)
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具变更

## 注意事项
- 提交信息应清晰简洁
- 描述"为什么"而不仅是"做了什么"
- 每个提交应该是原子性的

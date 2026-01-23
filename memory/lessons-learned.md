# 经验教训库 (Lessons Learned)

本文件记录系统在运行过程中遇到的问题、解决方案和经验教训。

---

## [2026-01-24] 全局 Hooks 配置格式差异 #001

### 问题描述
在尝试将 Port Management 和 Statusline 集成到全局 `~/.claude/settings.json` 时，多次遇到 hooks 配置格式错误：
```
Expected string, but received object
```

### 根因分析
1. **格式差异未文档化**：全局 `settings.json` 的 hooks 格式与项目级别 `hooks/hooks.json` 不同
2. **错误使用项目格式**：在全局配置中使用了项目级别的对象格式 `{"tools": ["Bash"]}`
3. **缺少验证机制**：修改配置后没有自动验证规则
4. **文档不完整**：CLAUDE.md 中没有明确说明两种配置的差异

### 解决方案
1. **明确配置层级**：
   - ✅ **项目级别** (`hooks/hooks.json`)：使用对象 matcher，格式明确
   - ⚠️ **全局级别** (`~/.claude/settings.json`)：格式不明确，避免使用 hooks

2. **推荐实践**：
   - 优先在项目级别配置 hooks
   - 全局配置仅用于 statusLine 等非 hooks 功能
   - Port Management hooks 保留在项目级别

3. **验证流程**：
   - 修改 JSON 配置后必须验证格式
   - 使用 `python -m json.tool` 或 `jq` 验证
   - 在 Windows 上测试路径兼容性

### 配置更新
| 文件 | 更新内容 | 理由 |
|------|----------|------|
| `CLAUDE.md` | 新增"配置文件验证规则"章节 | 明确全局 vs 项目级别差异 |
| `CLAUDE.md` | 新增 Windows 兼容性指南 | 避免路径问题 |
| `CLAUDE.md` | 新增配置验证要求 | 防止格式错误 |
| `~/.claude/settings.json` | 移除 hooks 配置 | 避免格式冲突 |
| `~/.claude/settings.json` | 保留 statusLine 配置 | 启用全局 statusline |

### 验证结果
- ✅ JSON 格式验证通过
- ✅ Statusline 成功集成到全局配置
- ✅ Port Management hooks 在项目级别正常工作
- ✅ 文档更新完成，规范明确

### 后续建议
1. **文档完善**：
   - 在 QUICK-REFERENCE.md 中添加配置层级说明
   - 创建配置故障排查指南

2. **工具增强**：
   - 考虑创建配置验证脚本 `scripts/validate-config.sh`
   - 集成到 pre-commit hook 中自动验证

3. **最佳实践**：
   - 所有 hooks 配置优先使用项目级别
   - 全局配置仅用于跨项目的通用功能（如 statusLine）
   - 修改配置后必须验证 JSON 格式和实际执行

### 反模式（避免）
- ❌ 在全局 settings.json 中配置 hooks
- ❌ 修改配置后不验证 JSON 格式
- ❌ 假设全局和项目配置格式相同
- ❌ 在 Windows 上使用 Unix 路径格式

---

## 模板

### [日期] 经验条目 #ID

#### 问题描述
[什么出错了/什么可以更好]

#### 根因分析
[为什么会发生]

#### 解决方案
[如何修复/改进]

#### 配置更新
| 文件 | 更新内容 | 理由 |
|------|----------|------|
| ... | ... | ... |

#### 验证结果
[更新后的验证]

#### 后续建议
[如果有进一步建议]

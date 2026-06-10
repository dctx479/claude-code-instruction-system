# CLAUDE.md 版本管理指南

## 版本控制机制

### 双文件架构

```
项目级: ./CLAUDE.md (git管理)
全局级: ~/.claude/CLAUDE.md (手动同步)
```

### 版本号规范

遵循语义化版本 (Semantic Versioning):

- **主版本号 (Major)**: 重大架构变更，不向下兼容
- **次版本号 (Minor)**: 新增功能，向下兼容
- **修订号 (Patch)**: Bug修复，优化改进

当前版本: **v1.1**

### 同步协议

#### 何时同步

**必须同步**（P0优先级）:
- 新增核心协议（Agent调度/Skills加载/编排策略）
- 修改自主决策授权范围
- 新增或修改Hooks配置规范
- 更新核心命令定义

**建议同步**（P1优先级）:
- 新增最佳实践引用
- 更新文档索引链接
- 补充使用示例

**可选同步**（P2优先级）:
- 格式优化
- 注释补充

#### 同步方向

**项目 → 全局**（推荐）:
```bash
# 验证差异
diff ./CLAUDE.md ~/.claude/CLAUDE.md

# 执行同步
cp ./CLAUDE.md ~/.claude/CLAUDE.md

# 记录同步
echo "# $(date +%Y-%m-%d): 项目→全局同步" >> docs/CLAUDE-SYNC.log
```

**全局 → 项目**（谨慎）:
仅在全局配置包含未提交的实验性功能且验证成功后使用：
```bash
# 验证差异
diff ~/.claude/CLAUDE.md ./CLAUDE.md

# 执行同步
cp ~/.claude/CLAUDE.md ./CLAUDE.md

# Git提交
git add ./CLAUDE.md
git commit -m "sync(config): 全局→项目同步 - [变更描述]"
```

### 版本历史追踪

#### 版本日志位置

```
项目级: docs/CHANGELOG.md (完整历史)
配置级: CLAUDE.md 头部（最近3次同步）
```

#### 日志格式

```markdown
## [v1.1] - 2026-06-10

### Added
- §零.二 步骤8: 外部工具推荐检查协议
- §六.六: AI协作核心行为约束（Karpathy规则）

### Changed
- 文档索引行：新增Agent框架决策/SDK生态/部署安全指南

### Fixed
- N/A

### Sync
- 2026-06-10: 项目→全局，建立版本管理机制
- 2026-06-09: 项目→全局，同步外部工具推荐协议
```

### 差异检测

#### 自动检测脚本

创建 `scripts/check-claude-diff.sh`:

```bash
#!/bin/bash
set -euo pipefail

PROJECT_CLAUDE="./CLAUDE.md"
GLOBAL_CLAUDE="$HOME/.claude/CLAUDE.md"

if ! diff -q "$PROJECT_CLAUDE" "$GLOBAL_CLAUDE" >/dev/null 2>&1; then
    echo "⚠️ CLAUDE.md 配置不一致"
    echo
    echo "差异:"
    diff -u "$GLOBAL_CLAUDE" "$PROJECT_CLAUDE" | head -50 || true
    echo
    echo "建议: 执行 cp ./CLAUDE.md ~/.claude/CLAUDE.md"
    exit 1
else
    echo "✅ CLAUDE.md 配置一致"
    exit 0
fi
```

#### Git Hooks 集成

在 `.git/hooks/pre-commit` 中添加:

```bash
# 检查CLAUDE.md是否需要同步
if git diff --cached --name-only | grep -q "^CLAUDE.md$"; then
    echo "检测到CLAUDE.md变更，提醒同步到全局..."
    echo "执行: cp ./CLAUDE.md ~/.claude/CLAUDE.md"
fi
```

### 冲突解决

#### 冲突场景

**场景1**: 项目和全局都有修改

解决：
1. 使用 `diff -u` 比对差异
2. 手动合并关键变更
3. 以项目版为准（git版本控制更可靠）
4. 提交合并后的版本

**场景2**: 项目版落后于全局版

解决：
1. 检查全局版的变更是否已测试验证
2. 如已验证 → 全局→项目同步 + git commit
3. 如未验证 → 丢弃全局变更，以项目版为准

**场景3**: 跨会话工作导致配置漂移

预防：
- 每次工作前：检查差异
- 每次/compact前：执行同步
- 每次关闭窗口前：验证一致性

### 版本升级准则

#### 升级主版本号（v1.x → v2.0）

触发条件：
- Agent调度机制重构
- 编排策略框架变更
- 破坏性配置格式调整

升级流程：
1. 创建 `CLAUDE-v1.1-backup.md`
2. 更新主版本号
3. 迁移指南文档
4. 全面测试验证

#### 升级次版本号（v1.1 → v1.2）

触发条件：
- 新增Agent自动调度intent
- 新增核心Skill或命令
- 新增编排模式
- 新增最佳实践章节

升级流程：
1. 更新次版本号
2. 记录CHANGELOG
3. 同步到全局

#### 升级修订号（v1.1.0 → v1.1.1）

触发条件：
- Bug修复
- 文档链接更新
- 示例代码优化

升级流程：
1. 直接修改
2. 简要记录变更

### 最佳实践

#### ✅ 推荐做法

1. **每次/compact前检查差异**
   ```bash
   diff ./CLAUDE.md ~/.claude/CLAUDE.md
   ```

2. **重要变更必须git commit**
   ```bash
   git add CLAUDE.md
   git commit -m "feat(config): 新增XX协议"
   ```

3. **同步时更新版本头部的同步记录**
   ```markdown
   # 同步记录:
   # - 2026-06-10: 项目→全局，[变更描述]
   ```

4. **使用git log追踪历史**
   ```bash
   git log --oneline -- CLAUDE.md
   ```

#### ❌ 避免做法

1. ❌ 在全局版直接编辑（除非临时实验）
2. ❌ 同步后不记录变更
3. ❌ 跨会话工作不检查差异
4. ❌ 破坏性变更不备份旧版本

### 审计与验证

#### 定期审计（每月）

1. 检查版本号是否合理递增
2. 验证同步记录完整性
3. 对比项目和全局配置
4. 清理过期的实验性配置

#### 自动化验证

在CI/CD中集成：
```yaml
- name: Check CLAUDE.md sync
  run: bash scripts/check-claude-diff.sh
```

### 工具支持

#### 推荐工具

- **差异对比**: `diff -u`, `git diff --no-index`
- **版本追踪**: `git log --follow CLAUDE.md`
- **冲突解决**: VSCode Diff Editor, `vimdiff`

#### 快速命令

```bash
# 查看项目版和全局版差异
diff -u ~/.claude/CLAUDE.md ./CLAUDE.md | less

# 统计行数差异
wc -l ./CLAUDE.md ~/.claude/CLAUDE.md

# 同步并记录
cp ./CLAUDE.md ~/.claude/CLAUDE.md && \
echo "$(date +%Y-%m-%d): 项目→全局同步" >> docs/CLAUDE-SYNC.log
```

---

## 版本历史

### [v1.1] - 2026-06-10
- 建立版本管理机制
- 新增外部工具推荐协议（§0.2步骤8）
- 新增Karpathy规则（§六.六）
- 补充3个Agent注册（router/codemap-builder/data-warehouse-analyst）

### [v1.0] - 2026-03-01
- 初始版本发布
- 核心协议：自进化/Agent编排/Quality保障/Skills系统
- 25个Agent定义 + 54个Skills + 31个Commands

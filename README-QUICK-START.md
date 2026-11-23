# 🚀 快速开始 - 5 分钟上手

这个项目是**完全开放**的，任何 AI 工具（Claude, Codex, Gemini, DeepSeek 等）都可以直接使用。

---

## ⚡ 超快速开始（2 分钟）

### 1. 验证安装

```bash
python scripts/verify-simple.py
```

期望输出: `[SUCCESS] All validations passed!`

### 2. 记录你的第一条笔记

```bash
python scripts/note-manager.py add session "我的第一条笔记"
```

### 3. 添加你的第一个标注

```bash
python scripts/annotation-manager.py add "重要发现" --tag key-insight
```

### 4. 查看结果

```bash
python scripts/note-manager.py show
python scripts/annotation-manager.py summary
```

**完成！就这么简单！**

---

## 🎯 任何工具都可以使用

### Claude Code
```bash
/note session 临时想法
!mark key-insight
```

### Codex CLI
```bash
codex "task" > output.txt
python scripts/note-manager.py add session "$(head -1 output.txt)"
```

### Gemini API
```python
import sys
sys.path.insert(0, 'scripts')
from note_manager import SessionNotesManager

note_mgr = SessionNotesManager()
note_mgr.add_note('session', 'Gemini 的分析结果', tag='insight')
```

### 任何其他工具
```bash
# 通过命令行
python scripts/note-manager.py add session "内容"
python scripts/annotation-manager.py add "标注" --tag key-insight
```

---

## 📚 核心功能

### 1. 分层笔记系统

```bash
/note session <内容>      # 临时想法
/note workspace <内容>    # 项目决策
/note global <内容>       # 通用经验
```

### 2. 对话标注系统

```bash
!mark key-insight         # 关键洞察
!mark todo <text>         # 待办事项
!mark decision <text>     # 重要决策
```

### 3. 检查点审查

```bash
python scripts/checkpoint.py review
python scripts/checkpoint.py diff --from A --to B
```

---

## ✅ 核心优势

✅ **开箱即用** - 无需配置  
✅ **工具无关** - 任何工具都可以用  
✅ **完全开放** - 无锁定，无限制  
✅ **自动同步** - 多工具共享数据  
✅ **离线工作** - 无需网络  
✅ **隐私保护** - 本地存储  

---

## 📖 更多文档

- **详细指南**: `docs/SESSION-NOTES-GUIDE.md`
- **外部工具集成**: `docs/EXTERNAL-TOOLS-INTEGRATION.md`
- **完整特性**: `READY-TO-USE.md`

---

**立即开始使用！无需等待！**

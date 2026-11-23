---
{
  "name": "fix-backup-collision",
  "description": "备份标识在冻结时钟下仍须唯一",
  "metadata": {
    "confidence": 0.8,
    "evidence": [
      {
        "id": "fix-backup-collision-1",
        "type": "documentation",
        "source": "scripts/install-global.py",
        "method": "当前仓库来源核对；执行结果见实现报告",
        "confidence": 0.8,
        "date": "2026-11-23",
        "verified_by": "tool"
      },
      {
        "id": "fix-backup-collision-2",
        "type": "test",
        "source": "tests/test_closure.py:test_backup_identifiers_stay_unique_with_frozen_wall_clock",
        "method": "当前仓库来源核对；执行结果见实现报告",
        "confidence": 0.8,
        "date": "2026-11-23",
        "verified_by": "tool"
      }
    ],
    "related": []
  }
}
---

备份冲突来源是命名粒度和并发；当前实现含序号/UUID，不将 Windows 时钟精度示例当成已证实根因。

此记录是现有来源的策展索引，原始记忆不变。confidence 为策展判断，引用存在不表示测试已通过。

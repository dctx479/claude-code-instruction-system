---
{
  "name": "memory-compact-strategy",
  "description": "压缩交接需复核文件哈希，事件摘要只作参考",
  "metadata": {
    "confidence": 0.8,
    "evidence": [
      {
        "id": "memory-compact-strategy-1",
        "type": "documentation",
        "source": "scripts/checkpoint.py",
        "method": "当前仓库来源核对；执行结果见实现报告",
        "confidence": 0.8,
        "date": "2026-11-23",
        "verified_by": "tool"
      },
      {
        "id": "memory-compact-strategy-2",
        "type": "test",
        "source": "tests/test_vnext.py:test_checkpoint_absent_valid_changed_and_corrupt",
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

沿用 checkpoint，不将自动会话事件摘要视为已经验证的工作状态。

此记录是现有来源的策展索引，原始记忆不变。confidence 为策展判断，引用存在不表示测试已通过。

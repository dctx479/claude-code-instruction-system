---
{
  "name": "qa-scoring-method",
  "description": "验收失败和阻塞缺陷不能由总分抵消",
  "metadata": {
    "confidence": 0.8,
    "evidence": [
      {
        "id": "qa-scoring-method-1",
        "type": "documentation",
        "source": "docs/QA-SYSTEM.md",
        "method": "当前仓库来源核对；执行结果见实现报告",
        "confidence": 0.8,
        "date": "2026-11-23",
        "verified_by": "tool"
      },
      {
        "id": "qa-scoring-method-2",
        "type": "documentation",
        "source": "agents/qa-reviewer.md",
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

根据需求选择验证；不对所有仓库机械套用覆盖率或性能阈值。

此记录是现有来源的策展索引，原始记忆不变。confidence 为策展判断，引用存在不表示测试已通过。

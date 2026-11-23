---
{
  "name": "context-budget-management",
  "description": "规则入口与目录链预算分开计算",
  "metadata": {
    "confidence": 0.8,
    "evidence": [
      {
        "id": "context-budget-management-1",
        "type": "documentation",
        "source": "AGENTS.md",
        "method": "当前仓库来源核对；执行结果见实现报告",
        "confidence": 0.8,
        "date": "2026-11-23",
        "verified_by": "tool"
      },
      {
        "id": "context-budget-management-2",
        "type": "test",
        "source": "tests/test_rule_governance.py:test_chain_budget_does_not_sum_siblings",
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

统计字节不冒充 token；不得将互不生效的兄弟目录预算简单相加。

此记录是现有来源的策展索引，原始记忆不变。confidence 为策展判断，引用存在不表示测试已通过。

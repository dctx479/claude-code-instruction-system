---
{
  "name": "agent-decision-routing",
  "description": "只有显式指令触发 Agent 调度",
  "metadata": {
    "confidence": 0.8,
    "evidence": [
      {
        "id": "agent-decision-routing-1",
        "type": "documentation",
        "source": "hooks/intent-context.py",
        "method": "当前仓库来源核对；执行结果见实现报告",
        "confidence": 0.8,
        "date": "2026-11-23",
        "verified_by": "tool"
      },
      {
        "id": "agent-decision-routing-2",
        "type": "test",
        "source": "tests/test_intent_routing.py:test_pasted_article_and_quoted_commands_do_not_route",
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

文章、引号内的命令不应触发 Agent。机械路由通过显式 /route 使用。

此记录是现有来源的策展索引，原始记忆不变。confidence 为策展判断，引用存在不表示测试已通过。

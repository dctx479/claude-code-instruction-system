---
{
  "name": "hook-execution-safety",
  "description": "命令检查保持独立，推荐路由不能授予权限",
  "metadata": {
    "confidence": 0.8,
    "evidence": [
      {
        "id": "hook-execution-safety-1",
        "type": "documentation",
        "source": "scripts/validate/command_guard.py",
        "method": "当前仓库来源核对；执行结果见实现报告",
        "confidence": 0.8,
        "date": "2026-11-23",
        "verified_by": "tool"
      },
      {
        "id": "hook-execution-safety-2",
        "type": "test",
        "source": "tests/test_vnext.py:test_guard_parameter_variants_and_no_command_disclosure",
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

未知安全判断不可假成功；上下文优化只能建议，不能改 allow/deny。

此记录是现有来源的策展索引，原始记忆不变。confidence 为策展判断，引用存在不表示测试已通过。

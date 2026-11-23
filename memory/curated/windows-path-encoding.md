---
{
  "name": "windows-path-encoding",
  "description": "Hook JSON 和 Unicode 路径按 UTF-8 处理",
  "metadata": {
    "confidence": 0.8,
    "evidence": [
      {
        "id": "windows-path-encoding-1",
        "type": "documentation",
        "source": "hooks/intent-context.py",
        "method": "当前仓库来源核对；执行结果见实现报告",
        "confidence": 0.8,
        "date": "2026-11-23",
        "verified_by": "tool"
      },
      {
        "id": "windows-path-encoding-2",
        "type": "test",
        "source": "tests/test_intent_routing.py:test_explicit_command_and_utf8_protocol",
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

保留原有路径，不用改成英文目录掩盖编码问题；通过 JSON 解析及 UTF-8 输入输出核对。

此记录是现有来源的策展索引，原始记忆不变。confidence 为策展判断，引用存在不表示测试已通过。

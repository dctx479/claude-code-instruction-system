---
{
  "name": "global-install-procedure",
  "description": "安装使用临时 target 验证且保留个人配置",
  "metadata": {
    "confidence": 0.8,
    "evidence": [
      {
        "id": "global-install-procedure-1",
        "type": "documentation",
        "source": "specs/SPEC-global-install.md",
        "method": "当前仓库来源核对；执行结果见实现报告",
        "confidence": 0.8,
        "date": "2026-11-23",
        "verified_by": "tool"
      },
      {
        "id": "global-install-procedure-2",
        "type": "test",
        "source": "tests/test_rule_governance.py:test_full_install_preserves_settings_and_is_idempotent",
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

先 dry-run 再在授权范围执行，保持安装幂等和回滚能力。

此记录是现有来源的策展索引，原始记忆不变。confidence 为策展判断，引用存在不表示测试已通过。

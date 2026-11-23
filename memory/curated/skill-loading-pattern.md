---
{
  "name": "skill-loading-pattern",
  "description": "Skill 和 Agent 按 profile 与任务加载",
  "metadata": {
    "confidence": 0.8,
    "evidence": [
      {
        "id": "skill-loading-pattern-1",
        "type": "documentation",
        "source": "config/profiles.json",
        "method": "当前仓库来源核对；执行结果见实现报告",
        "confidence": 0.8,
        "date": "2026-11-23",
        "verified_by": "tool"
      },
      {
        "id": "skill-loading-pattern-2",
        "type": "documentation",
        "source": "scripts/check-doc-facts.py",
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

按需加载参考文件；不自动导入整个台账或 Playbook 正文。

此记录是现有来源的策展索引，原始记忆不变。confidence 为策展判断，引用存在不表示测试已通过。

# permission-denied

触发模式：`PermissionError|permission denied|权限不足`

处理：检查目标所有者和用户授权，避免自动提权；保留错误证据，授权范围内修复后重试。

来源：../curated/hook-execution-safety.md。仅为检索提示，不会自动阻断或修复；实际次数来自会话事件，不预填历史次数。

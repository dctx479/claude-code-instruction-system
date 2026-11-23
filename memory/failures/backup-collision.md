# backup-collision

触发模式：`FileExistsError.*backup|backup.*collision|备份.*冲突`

处理：检查目标和备份命名；保留已存在文件，使用当前安装器的唯一标识，并运行冻结时钟回归。

来源：../curated/fix-backup-collision.md。仅为检索提示，不会自动阻断或修复；实际次数来自会话事件，不预填历史次数。

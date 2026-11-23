# windows-path-encoding

触发模式：`UnicodeEncodeError|UnicodeDecodeError|路径.*编码`

处理：核对 UTF-8 编解码和 JSON stdin/stdout；保留原路径，不能以换英文目录代替修复。

来源：../curated/windows-path-encoding.md。仅为检索提示，不会自动阻断或修复；实际次数来自会话事件，不预填历史次数。

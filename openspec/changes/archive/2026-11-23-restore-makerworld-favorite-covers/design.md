## Context

國際站正式收藏清單已實際回傳 `cover`，部分模型也有 `coverPortrait`。舊快照僅嘗試 `coverUrl`。瀏覽器既有收藏卡會讀取同步快照的 `preview_url`。

## Decisions

- 優先讀取清單的 `cover`，沿用 `coverUrl` 並允許可用的直式封面。每個候選網址皆通過既有驗證。
- 重複出現的模型可補上先前缺少的封面。由現有同步重建快照。

## Risks / Trade-offs

- 上游未提供有效封面時沿用既有的圖片暫不可用提示。

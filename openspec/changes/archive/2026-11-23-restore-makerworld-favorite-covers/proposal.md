## Why

MakerWorld 國際站的收藏清單使用 `cover` 傳回模型封面。工作台同步成功後漏存該欄位，導致已有封面的收藏仍顯示圖片暫不可用。

## What Changes

- 同步時保留收藏清單回傳且通過既有 HTTPS 網域驗證的圖片網址。

## Capabilities

### New Capabilities

### Modified Capabilities

- `makerworld-favorites` 在收藏卡顯示上游提供的可用封面。

## Impact

MakerWorld 收藏資料轉換與回歸測試。正式版更新後重新同步快照即可補回封面。

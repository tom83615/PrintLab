## Why

設備頁重複顯示未知的噴嘴路線，且部分工作流程仍要求指定實體噴嘴。使用者要求移除 PrintLab 的噴嘴路線功能與限制。

## What Changes

- 移除設備與確認卡的噴嘴路線資料、提示及逐任務確認。
- 移除準備、切片與送印對噴嘴路線的設定、推斷及驗證。
- 保留材料與料槽檢查、噴嘴規格、切片完整性及設備狀態檢查。

## Capabilities

### Modified Capabilities

- `printer-supply-snapshot` 移除噴嘴路線資訊。
- `print-dispatch` 移除噴嘴路線限制。

## Impact

影響設備與確認頁、待列印清單、切片準備與列印轉接器。

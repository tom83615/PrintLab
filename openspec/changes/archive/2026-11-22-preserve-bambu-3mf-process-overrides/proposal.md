## Why

一份切片使用 Gyroid，但 3MF 未登記這項工藝差異，Bambu Studio 開啟後回到標準預設的 Grid。使用者已確認補登記後可以正常開啟。

## What Changes

- `printlab slice` 將工藝檔明確指定的稀疏填充圖樣登記為專案差異。
- 核對輸出的 3MF 設定與該盤 G-code，發現不一致時標記切片失敗。

## Capabilities

### New Capabilities

- `bambu-slice-settings` 保留 Bambu Studio 切片包的稀疏填充圖樣。

### Modified Capabilities

## Impact

涉及切片時複製的工藝檔，以及現有的離線切片檢查。既有列印任務和 Studio 系統預設維持原狀。

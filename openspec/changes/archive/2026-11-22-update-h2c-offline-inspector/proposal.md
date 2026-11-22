## Why

舊版獨立離線檢查器無法辨識 H2C 首層溫度設定，導致 Studio 交接無法建立。上游 1.1.99 已對同一檔案回傳相符的離線檢查結果。

## What Changes

- 將獨立檢查器和下載鎖定檔更新至經驗證的上游版本。

## Capabilities

### Modified Capabilities

- `print-dispatch` 支援由 Bambu Studio 02.09.01.70 產生的 H2C 切片包離線檢查。

## Impact

涉及依賴鎖定、安裝腳本、離線 MCP 客戶端與列印文件。

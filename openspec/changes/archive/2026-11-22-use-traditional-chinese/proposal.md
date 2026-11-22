## Why

PrintLab 的中文文件、工作台介面與提示混用簡體和繁體。統一維護中的中文文字，讓使用者在文件、瀏覽器及命令列看到一致的繁體中文。

## What Changes

- 將中文 README、維護文件、範本、介面和訊息中的簡體字改成繁體。
- 將繁體 README 的入口改為 `README.zh-TW.md`，舊網址提供連結至新入口。
- 保留第三方介面辨識字串、相容性所需的固定值、本機資料及外部來源。

## Capabilities

### New Capabilities

- `traditional-chinese-copy`：統一 PrintLab 維護的中文文字。

### Modified Capabilities

無。

## Impact

涵蓋文件、範本、命令列、後端提示、工作台和相關驗收。英文入口、資料結構及列印行為延續原有設計。

# Proposal

## Why

桌面 CI 的送印測試仍使用舊核准規則與模擬設備狀態，導致三組執行環境在 pytest 階段停止。

## What Changes

- 依現行送印規格更新測試斷言、模擬資料與呼叫介面。
- 保留對帳、取消證據、設備待清板與單次送印的回歸覆蓋。

## Capabilities

### New Capabilities

- `desktop-verification` 記錄桌面 CI 的送印回歸驗收契約。

### Modified Capabilities

## Impact

範圍為測試與驗證資料。實際送印、核准和對帳程式維持原樣。

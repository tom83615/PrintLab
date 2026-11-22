# Proposal

## Why

Windows 上模型建置成功後，`build.json` 以反斜線寫入來源與產物相對路徑；PrintLab 的 lineage validator 以正斜線建立目前檔案清單並檢查產物前綴，造成合法建置被拒絕。端到端驗收已重現此問題。

## What Changes

- 建置 manifest 將來源和產物路徑一律序列化為 POSIX 相對路徑。
- 加入跨平台回歸檢查，涵蓋 Windows 路徑分隔符。

## Capabilities

此修正僅統一內部 manifest 路徑表示，沒有改變使用者可見行為或需求，故不新增規格 delta（`skip_specs: true`）。

## Impact

- 影響 `Harness/build_model.py` 的建置 manifest 路徑欄位及其測試。
- 不改變檔案位置、CLI 參數、manifest 欄位名稱或既有資料格式語義。

# Tasks

## 1. 統一路徑格式

- [x] 1.1 在建置器加入 pathlib 相對 POSIX 路徑 helper，並用於 source 與 artifact manifest；以 PureWindowsPath 回歸測試確認輸出使用正斜線（`pytest Harness/tests/test_build_model.py -q` 通過）。

## 2. 驗證 Windows 建置 lineage

- [x] 2.1 執行相關 PrintLab workflow 測試，並以Windows 建置確認 manifest 可通過 lineage 驗證及尺寸檢查（指定 pytest 測試 3 項通過、2 項略過，模型建置及 Bambu Studio 試切片均成功）。

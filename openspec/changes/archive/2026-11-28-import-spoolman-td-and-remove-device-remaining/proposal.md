## Why

使用者已在 Spoolman 中維護幾乎全部線材的透光值（`filament.extra.td`），但 PrintLab 目前尚未讀取或傳遞此數值，導致建模、配色與切片審查階段無法直接依 TD 評估高透光淺色線材覆蓋深色結構或低填充時的透底色風險。同時，PrintLab 前端介面仍於 AMS 槽位與核驗畫面重複顯示「設備餘量未知／設備報告」欄位，在 OpenSpoolMan 快照模式下既無實質餘量資訊又造成視覺干擾。

## What Changes

- 從 Spoolman `filament.extra.td` 解析並匯入線材透光值（`transmission_distance`），覆蓋庫存列表、OpenSpoolMan 已關聯槽位、既有槽位總覽以及專案設計約束快照（`manufacturing-context.json`）。
- 在 PrintLab 前端材料台帳與 AMS 槽位卡片顯示線材透光值（`TD`），缺值時不猜測。
- 移除 PrintLab 前端介面中的設備餘量顯示欄位（包含 AMS 槽位卡片的 `deviceRemainingLabel`、相關提示語句及待列印核驗明細中的設備餘量段落），保留 Spoolman 台帳餘量估算顯示。
- 將 TD 透光值防透底／壁厚與沖刷進填充檢查整合進工作流規範與最終製作 Review 文件（倉庫範本與外部工作區同步更新）。

## Capabilities

### Modified Capabilities

- `material-inventory`: 從 Spoolman 匯入 `filament.extra.td` 作為 `transmission_distance` 並納入專案設計約束與前端材料台帳呈現；未知或無效值維持為空。
- `printer-supply-snapshot`: 將關聯 Spoolman 料卷的 `transmission_distance` 帶入槽位快照，並於前端槽位與核驗介面移除設備餘量顯示欄位。

## Impact

- 後端：`Harness/printlab/supplies.py`、`Harness/printlab/materials.py`、`Harness/printlab/constraints.py`。
- 前端：`Harness/studio/src/Materials.jsx`、`Harness/studio/src/Prepared.jsx`、`Harness/studio/src/presentation.js`、`Harness/studio/src/materials.css` 與打包產物 `Harness/studio/dist/`。
- 測試：`Harness/tests/test_supplies.py`、`Harness/tests/test_materials_display.py`、`Harness/tests/test_constraints.py`。
- 工作流文件：`Context/workflow.md`、`Context/x2d-final-review.md`、`Templates/Project/Review/x2d-final-review.md` 及外部工作區對應 `Context/` 文件。

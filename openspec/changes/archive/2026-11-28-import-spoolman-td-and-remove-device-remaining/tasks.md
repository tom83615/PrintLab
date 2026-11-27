## 1. 後端 Spoolman TD 匯入與資料流

- [x] 1.1 在 `Harness/printlab/supplies.py` 新增 `extra.td` 解析函式，於 `_ledger_row` 填入 `transmission_distance`，並於 `_slots` 將已關聯 Spoolman 料卷的 `transmission_distance` 帶入 OpenSpoolMan 槽位。
- [x] 1.2 在 `Harness/printlab/materials.py` 將 `transmission_distance` 加入 `PUBLIC_FIELDS`，並於 `slot_overview` 匹配料卷時輸出 `transmission_distance`。
- [x] 1.3 在 `Harness/printlab/constraints.py` 將 `transmission_distance` 納入 `owned_materials` 欄位與雜湊變更偵測。

## 2. PrintLab 前端介面更新

- [x] 2.1 在 `Harness/studio/src/presentation.js` 新增 `transmissionDistanceLabel` 格式化函式，並移除 `deviceRemainingLabel`。
- [x] 2.2 更新 `Harness/studio/src/Materials.jsx` 與 `Harness/studio/src/materials.css`：移除 AMS 槽位卡片的設備餘量欄位與相關提示，並在 AMS 槽位卡片與材料台帳卡片顯示已知的 `透光值 TD`（缺值不猜測）。
- [x] 2.3 更新 `Harness/studio/src/Prepared.jsx`，移除核驗明細中的設備餘量顯示欄位。

## 3. 工作流規範整合

- [x] 3.1 更新倉庫與外部工作區的 `Context/workflow.md`、`Context/x2d-final-review.md` 與 `Templates/Project/Review/x2d-final-review.md`，加入線材透光值（TD）於多色疊層、薄壁、淺色防透底與 `flush_into_infill` 評估之檢核規範。

## 4. 測試、建置與驗證

- [x] 4.1 補齊 `Harness/tests/test_supplies.py`、`Harness/tests/test_materials_display.py` 與 `Harness/tests/test_constraints.py` 針對 Spoolman TD 解析（含 `0`、小數、缺失與無效值）、槽位傳遞與約束變更偵測之單元測試。
- [x] 4.2 執行前端建置（`npm run build`）更新 `Harness/studio/dist/`，執行相關 pytest 測試，並以本機 `printlab status`／`context` 唯讀驗證實測 Spoolman TD 讀回。

## Context

- Spoolman `/api/v1/spool` 回傳的每筆 `filament.extra` 物件中，自訂浮點欄位 `td` 以 JSON 字串或數值形式儲存（例如 `"6.3"`、`"0"`、`"100"`），缺失或空字串代表未知。
- `Harness/printlab/supplies.py` 的 `_ledger_row` 負責將 Spoolman 料卷轉成 PrintLab 標準材料列，並同時被 `supplies.inventory()` 與 OpenSpoolMan 的 `_slots()` 共用。
- `Harness/printlab/materials.py` 以 `PUBLIC_FIELDS` 白名單控制可對外輸出的材料欄位。
- `Harness/printlab/constraints.py` 將非封存料卷精簡欄位序列化至 `Review/manufacturing-context.json`，並以 SHA-256 偵測材料變更。
- 前端 `Harness/studio/src/Materials.jsx` 透過 `deviceRemainingLabel(slot)` 在每張 AMS 槽位卡顯示「設備餘量未知／設備報告 XX%」，且 `Prepared.jsx` 核驗明細亦包含設備餘量文字。

## Goals / Non-Goals

**Goals:**
- 零額外 API 請求，直接由既有 Spoolman `/api/v1/spool` 回應解析 `filament.extra.td` 為有限非負浮點數 `transmission_distance`；缺失、非數值、負數、布林或非有限值一律保留為 `None`。
- 讓 `transmission_distance` 一致流經 `supplies.inventory()`、`supplies.device()`（已關聯料卷之槽位）、`materials.inventory_items()`、`materials.slot_overview()`（匹配料卷時）與 `constraints.current()`（含雜湊變更偵測）。
- 在前端材料台帳卡片與已裝料 AMS 槽位卡片以統一格式顯示 `透光值 TD <值>`（缺失時於台帳細節標註或於卡片省略，不猜測數值）。
- 移除前端所有「設備餘量」顯示欄位與相關 `deviceRemainingLabel` 函式，但維持後端資料結構與既有 API 欄位向後相容（不破壞 `test_materials_display.py`、`test_prepared.py` 等既有契約）。
- 在工作流與最終製作 Review 文件補上高 TD 淺色防透底色／壁厚／`flush_into_infill` 檢查規範。

**Non-Goals:**
- 不修改 Spoolman 遠端資料或新增寫入 TD 的 `material-intake` 流程。
- 不移除 Spoolman 台帳估算餘量（`inventoryRemainingLabel`）顯示。
- 不對未知 TD 線材套用預設值或顏色推估。

## Decisions

1. **欄位命名採用 `transmission_distance`**：相較縮寫 `td`，語意清楚且與 `material_number`、`storage_location` 一致；UI 顯示簡明標示為 `透光值 TD 6.3`（整數顯示如 `TD 0`、`TD 100`，小數去尾零如 `TD 6.3`）。
2. **Spoolman `extra.td` 寬容解析、嚴格驗證**：Spoolman extra 欄位常以字串包裝（如 `"6.3"` 或 `"\"6.3\""`），先嘗試 `json.loads` 再轉浮點，嚴格排除 `bool`、`NaN`、`inf` 與負數（`< 0`）；`0` 為有效不透光值（例如黑色線材 `TD = 0`）。
3. **前端移除設備餘量而不破壞後端契約**：從 `Materials.jsx`、`Prepared.jsx`、`presentation.js` 與 `materials.css` 移除設備餘量呈現與 `deviceRemainingLabel`，後端 `reported_remaining_percent` 與 `remaining_basis` 仍維持原本安全邊界供既有測試與預檢使用。
4. **工作流文件同步更新**：同時更新倉庫內 `Context/workflow.md`、`Context/x2d-final-review.md`、`Templates/Project/Review/x2d-final-review.md` 與本機外部資料空間的 `Context/workflow.md`、`Context/x2d-final-review.md`，確保新專案與目前工作區即時生效。

## Risks / Trade-offs

- **風險**：既有專案的 `Review/manufacturing-context.json` 在匯入 `transmission_distance` 後，`owned_materials` 雜湊會變更而顯示 `needs_refresh`。
  - **緩解**：這屬於預期行為，下次 `constraints capture` 即可將 TD 快照寫入專案約束，不影響舊快照讀取。
- **風險**：前端移除 `deviceRemainingLabel` 後須確認無其他元件或自動化腳本依賴該字串。
  - **緩解**：已以全倉搜尋核對所有 JSX 與瀏覽器驗證腳本，並將重建 `Harness/studio/dist` 及執行完整測試。

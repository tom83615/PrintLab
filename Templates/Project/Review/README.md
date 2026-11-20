# 實物覆盤

每次列印單獨記錄：批次 ID、設計和切片版本、材料、噴嘴、方向、層高、設備回執、照片、尺寸偏差、配合/外觀/支撐回饋、結論與下一步。照片必須來自真實成品。未驗收前保持待檢查。


## 列印前製作審查

每個最終模型按 `Context/x2d-final-review.md` 做一次製作Review，填寫本目錄 `x2d-final-review.md` 模板並保留實際模型/切片證據。模板未填寫不算已審查，實物覆盤與列印前審查分別記錄。

## 每輪選圖歸檔

每次比較圖片並收到選擇/回饋後，按 `Library/Taste/README.md` 用 `taste-choice.example.json` 的欄位建立獨立輪次記錄，歸檔全部呈現候選，不只選中圖；使用 `printlab taste record` 儲存不可覆蓋的圖片快照。使用者未說明理由留空；新回饋用於修正 `Context/taste.md`，不自動升格推測。

## 選圖、改裝與建模接續

預設按 `Context/image-to-print.md` v3先選外形、再從四套三視圖中選一整套，隨後建模、真實預覽對照、配色與正式3MF。建模模型按 `Context/agent-policy.json` 與使用者當前可用環境選擇。

已有模型改裝填寫 `remix-plan.md`；兩次選擇寫 `design-target.json` 與 `design-reference.md`。`model-routing.md` 區分預設/計畫與實際執行，實際模型讀回證據另存 `model-routing.json`。模板存在不表示選型或檢查已完成；當前專案已確認選擇直接接續。

<!-- PRINTLAB_TEXT2CAD_TRIAL:BEGIN -->
## 參數化 CAD 接入

共享入口為倉庫根目錄的 `Harness/bin/text2cad`。先按 `docs/DEPENDENCIES.md` 獨立安裝並用當前 `--help` 核驗，再填寫 `text2cad-trial.md`。工具版本和幾何檢查結果來自本機實際執行，具體列印沿用 PrintLab 任務確認流程。
<!-- PRINTLAB_TEXT2CAD_TRIAL:END -->

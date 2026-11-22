# 可複用的造物經驗

- 好看的概念圖需要實際模型對照。選定一套三視圖後從同源模型渲染檢查。
- USB 插頭的硬殼、硬尾和轉彎空間分別測量，線槽要驗證完整裝入路徑。
- 卡扣鬆緊通過同源小樣驗證，列印誤差和建模間隙分開記錄。
- 模型放大或鏡像後核對介面方向、孔軸、單位和保護區。
- 切片要檢查實際啟動載料和溫度順序，介面進度與設備 ACK 需要實際出料驗證。
- 支撐、材料、冷卻與擺放可能共同影響缺陷。照片和工藝對照不足時保留待驗證原因。
- 材料餘量標明設備報告、賬面估算或實稱來源。
- 失敗、取消或結果不明的發送保留原始回執，處理前先對賬。

<!-- printlab-update:p001-gyroid-3mf-diff-20261122 -->
<!-- content-sha256:90437a4b181aad825d538c7f3b5901e713fe2d31e28c69e2a7b3c266ca0a6268 -->
## 2026-11-21T16:39:16.346776+00:00

P001 reprint finding: a sliced job.gcode.3mf may store sparse_infill_pattern=gyroid in Metadata/project_settings.config but still have different_settings_to_system empty. When the selected print_settings_id names a system preset that defaults to grid, Bambu Studio can reload the project as Grid. Any process override must also list changed process keys in the process entry of different_settings_to_system (for this single-filament H2C package: [sparse_infill_pattern, ", "]). Verify the final 3MF by round-tripping it through the installed Bambu Studio CLI and checking both Metadata/project_settings.config and Metadata/plate_1.gcode; both must retain gyroid before the task is offered for Studio handoff. Confirmed on P001 job J20261122-003428-08d42e.

來源記錄

P001 reprint, 2026-11-22, job J20261122-003428-08d42e

<!-- printlab-update:p001-gyroid-diff-array-clarify-20261122 -->
<!-- content-sha256:1be68159ebeb01df1e6eeaeeaea0c2cd53859a2ec851cae6f8999d514cb2cd07 -->
## 2026-11-21T16:39:48.806242+00:00

補充精確欄位位置：different_settings_to_system 的陣列第一項是工藝差異清單；單材料任務其餘兩項留空。Gyroid 的合法記法為三項陣列，第一項包含 sparse_infill_pattern，第二與第三項為空字串。

來源記錄

P001 corrected 3MF metadata check, 2026-11-22

<!-- printlab-update:cad-draft-then-solidcraft-20261122 -->
<!-- content-sha256:6f56787956503cd80de73d038d2d49dc06280dd2b04d895cf6af92cf59232120 -->
## 2026-11-22T14:06:36.993555+00:00

CAD 交接採草稿後精修：先用 Text-to-CAD 建立草稿並保留 Python 源碼，再匯出 STEP 到 SolidCraft 由 AI 與使用者共同修正。重大改變才回 Text-to-CAD 重建草稿；SolidCraft 的修改另存原生設計與 STEP，並明確標記目前正式版本，因兩邊不會自動同步。

來源記錄

使用者 2026-11-22 訊息：「Text-to-CAD 先做草稿，之後輸出 .STEP 讓 AI、我人類用 SolidCraft 修正，除非變化太大才重新建成草稿。」

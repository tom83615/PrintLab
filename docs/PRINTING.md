# 列印能力與首次驗證

## 首版的設備適配

PrintLab 工作台可在未連接設備時啟動。接入 Bambuddy 後提供狀態、材料與列印歷史。本候選版已擴展官方模板解析與離線切片檢查，A1、A1 mini、P1S、X1 Carbon 的 0.4 mm PLA 官方切片與獨立文件檢查已在 Mac 執行通過。相應硬體發送仍待現場驗證。

| 路線 | 當前範圍 |
| --- | --- |
| 官方 Studio，由 Codex 操作介面 | Agent 開啟具體切片包，核對機型、板型、材料與發送選項，使用 PrintLab 的批准與單次預約記錄，點選一次發送後讀回設備。需要當前 Codex 具備桌面控制能力。 |
| Windows 官方 Studio 手動交接 | 無需 Bambuddy；任務綁定本機記錄的 Studio 名稱、機型與序號。使用者當次核對設備就緒、噴嘴/料槽路線、材料與清板，記錄任務確認後由使用者在 Bambu Studio 發送。沒有即時遙測時，結果保持未知，須以同一任務名稱記錄觀察結果。 |
| 工作台按鈕呼叫本機發送助手 | 中文 Studio 02.08.02.61、X2D、0.4 mm、單主料 PLA/PETG、AMS 左主噴嘴、紋理 PEI、單盤。需要 macOS 14+、使用者登入且桌面解鎖、輔助功能與螢幕讀取權限。 |
| 工作台按鈕呼叫 Bambuddy 佇列 | Mac/Windows 共用 HTTP 發送程式碼，當前接入 A1、A1 mini、P1S、X1 Carbon 的 AMS 路線。需綁定 `bambuddy_queue`、讀回正確機型、可用儲存卡、IDLE 與具體材料；文件、排隊、啟動及異常對賬使用原任務記錄。軟體模擬已通過，實際設備接受與首層待現場驗證。 |
| 歷史原生 MCP 發送 | 發佈首版未提供可執行客戶端。來源和獨立安裝邊界見 DEPENDENCIES.md。 |

## 獨立離線檢查

安裝程序獨立下載 bambu-printer-mcp 1.1.33。工作台預檢和官方 Studio 預約通過公開 MCP 文件檢查介面核對相同 SHA-256 與盤號；不會傳入設備憑據、呼叫發送工具或啟動列印。PrintLab 自身的官方模板、載料及溫度檢查繼續執行。檢查成功只證明文件檢查通過，仍須核驗即時設備、材料、授權及發送助手。

## 準備一次具體列印

1. Codex 根據當前版本、選定材料、板型、噴嘴和機器生成切片包，儲存模型和切片 SHA。
   - H2C 已安裝 FTS 時，預設以左噴嘴設計與切片，因左側可用列印空間較大；仍須在 Studio 切片映射核對 AMS 槽位是否實際分配至左噴嘴。
2. 展示真實模型、關鍵尺寸、分盤、材料映射、預計耗時與用量。
3. 使用者確認列印這一版，並確認列印板清潔空置。當前流程校驗 30 分鐘有效期。
4. 使用 `printlab approve --help`、`printlab submit --help` 確認當前參數。`submit` 預設預檢，真實執行需要明確 `--execute`。
5. 發送後使用任務 ID 讀回設備，核對實際出料和首層，再等待完成與實物檢查。出現超時或回執不明時先對賬。

## 設定工作台發送助手

在倉庫根目錄執行以下命令。`build` 將專用助手安裝到本機 `/Applications`，需要 Swift 命令列工具及相應目錄寫入權限。

```bash
./Harness/bin/printlab studio-bridge build
./Harness/bin/printlab studio-bridge capability
```

使用者選擇啟用系統權限後，再執行 `./Harness/bin/printlab studio-bridge permissions`，按 macOS 提示授予專用助手權限。隨後重跑 `capability` 檢查實際狀態。`Runtime/config.json` 的 `studio_printer_name` 必須與 Studio 設備名一致。Agent 應讀取視窗中的準確名稱，並核對 Studio 所選設備與目標設備的序列號。Bambuddy 中的別名可能不同，不能直接代填。缺少名稱時，`capability` 會報告設定缺項。

任務超出支援範圍時，按具體提示核對並使用官方 Studio 介面工作流。首次設定完成後，使用者仍需對實際設備、材料與列印結果進行驗證。

### Windows without Bambuddy

先在 Studio 設備頁核對印表機名稱、機型和序號，再讀本機設定哈希並綁定身份。此設定只記錄目標身份，不修改 Handy、Bambu Cloud 或 Studio 登入。

```powershell
.\Harness\bin\printlab.ps1 workspace connection
.\Harness\bin\printlab.ps1 workspace studio-device --name 'Studio 顯示名稱' --model 'Bambu Lab H2C' --serial 'Studio 顯示的序號' --expect-sha '上一步返回的 SHA256'
```

準備具體列印任務後，在官方 Studio 當次確認並記錄同一任務的五項事實：`device_ready`、`routing_verified`、`material_loaded`、`plate_clear`、`print_authorized`。`routing_verified` 和 `device_ready` 必須來自 Studio/設備的當次畫面核對，不能從 OpenSpoolMan 快照推定。接著以該事件批准，`submit --execute` 只建立 60 秒有效的單次交接回執；使用者再於 Studio 開啟回執指出的確切檔案並自行發送。

沒有 Bambuddy 遙測時，`reconcile` 不會查詢印表機，也不會重送。使用者觀察到這個確切任務後，可記錄結果：

```powershell
.\Harness\bin\printlab.ps1 reconcile 專案ID 作業ID --outcome completed --task-name '作業ID.gcode' --evidence '在 Studio/設備畫面觀察到此任務完成' --source '觀察位置與日期'
```

可用結果為 `printing`、`completed`、`failed` 或 `cancelled`。完成只會進入待實物檢查，不代表實物已驗收。任務結果不明時不要再送一次。

## 遠程使用

預設服務僅監聽本機 127.0.0.1。需要私人遠程訪問時，可自行設定 Tailscale 並把自己的地址寫入 `tailscale_ip`，再重啟服務。本機已登入、未鎖屏與實體清板條件仍適用。請在可信私人網路使用工作台，連接規則在 `Harness/serve.py` 中。

連接模式與手機/電腦/Agent 的具體路徑見 [連接與控制指南](CONNECTIONS.md)。

## 設定跨平臺佇列路線

先使用 `workspace profiles --model 機型` 找到實際官方預設，解析機型、工藝和材料設定後切片。單噴嘴的 `extruder_mapping` 使用實際韌體噴嘴 0；AMS 槽位按現場讀回映射。映射還需包含已確認的材料、顏色、料卷關聯與 `routing_verified`，完整欄位查詢當前 CLI 與實際切片。

準備佇列任務時明確設定 `mapping.transport` 為 `bambuddy_queue`。已有官方 Studio 包保留其綁定，轉換通道時重新準備任務和具體批准。Bambuddy 寫入憑據需能上傳文件、維護佇列並啟動任務。工作台按鈕執行同一 `submit`，先上傳、讀回唯一佇列項，再發送一次啟動請求。超時保留回執並對賬。

設備報告 IDLE、儲存卡可用僅證明當前前提。簽名或韌體拒絕須依據實際返回診斷，首次現場驗收記錄韌體、網路模式、任務、材料和精確設備讀回。

機型證據見 [支援範圍](MACHINE_SUPPORT.md)，異常處理見 [排障與經驗接續](TROUBLESHOOTING.md)。

如果冷啟動後的設備卡暫時只顯示 `X2D 0.4mm`，助手會在任務名和設備名一致時重新整理一次設備卡，然後重新核對完整的雙噴嘴資訊、料位和列印選項。重新整理後仍不符合會返回錯誤。錯誤設備、錯誤任務和遮擋視窗的系統提示均需先處理。

助手通過本次請求獨有的回執確認執行結果。缺少回執、啟動異常或發送結果未知時，先核對設備和工作台記錄。未知的發送結果保留在記錄中，禁止自動再次發送。

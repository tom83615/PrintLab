# 列印歷史與收藏來源說明

## 當前資料來源

| 頁面或功能 | 當前來源 | 覆蓋範圍 |
| --- | --- | --- |
| 列印歷史和圖冊 | Bambuddy archives 與 print-log | Bambuddy 已儲存並可讀取的記錄，包含其捕獲的外部任務 |
| 靈感收藏 | 本機 Library/References/favorites.json 和 MakerWorld 同步快照 | 本機登記的收藏，以及已連線帳號的模型收藏 |
| 安裝前的雲端列印歷史 | 本輪範圍外 | 本輪已取消帳號舊歷史匯入開發 |
| MakerWorld 帳號收藏 | 所選站點的帳號收藏夾 | 帳號自己的預設與自訂收藏夾 |

記錄、模型文件和預覽圖各有來源。歷史中存在某次列印時，原始 3MF、當次切片和預覽的可用性仍逐項核對。發佈版的軟體安裝與空介面驗收覆蓋基礎執行，已有檔案缺圖可按 [預覽恢復說明](PREVIEW_RECOVERY.md) 處理。

## 安裝後原有功能消失

1. 記錄印表機型號、韌體、PrintLab 和 Bambuddy 版本，國內站或國際站，以及 Agent 改動過的設定名稱與改動前後的值。
2. 在原來的 Handy、Studio 或 MakerWorld 中核對同一帳號和地區，查看一條安裝前的列印記錄、一項已收藏模型。
3. 需要雲列印和帳號同步的使用者，按機型說明恢復先前可用的雲連接與帳號登入。網路模式調整由使用者確認，訪問碼變更後更新相應連接設定。
4. 檢查 API key 的歸屬與用途。PrintLab 的專用讀取 key 用於狀態、材料和已有檔案。已有同步工具的 key 按該工具要求恢復權限。
5. Bambuddy 的 Allow Cloud Access 對應帳號雲讀取，Manage Library 包含模型匯入。具體授權按已安裝版本、帳號歸屬和實際呼叫核對。[上游權限說明](https://wiki.bambuddy.cool/features/api-keys/)
6. 原應用有舊列印記錄而 PrintLab 沒有時，記錄缺失來源與時間範圍。安裝前的帳號列印歷史可從原應用查看。

## 連接 MakerWorld 收藏

1. 在專用瀏覽器設定檔登入正確的 MakerWorld 站點，並依 [Bambuddy 的 Access Token Login 說明](https://wiki.bambuddy.cool/features/cloud-profiles/#access-token-login) 在瀏覽器內取得該次登入的 access token。這是 Bambu 帳號憑據，只在本機隱藏輸入提示貼上。
2. 使用下列連線命令。中國站使用 `--region cn`，國際站使用 `--region global`。第一次完整讀取成功才會儲存連線。

   - Windows 原生工作台：`./Harness/bin/printlab.ps1 makerworld connect --region cn`
   - macOS 原生工作台：`./Harness/bin/printlab makerworld connect --region global`
   - 含此功能的 Windows Docker 正式工作台：`docker exec -it printlab-production-studio-1 python -m printlab.cli makerworld connect --region cn`

3. 開啟「靈感收藏」，核對至少一個收藏夾及模型。Studio 服務每小時同步，收藏頁每分鐘更新畫面。要立即讀取可將連線命令中的 `connect --region cn` 或 `connect --region global` 換成 `sync`。
4. 畫面若提示重新連接，請用同一站點的新登入憑據重跑連線。其他暫時錯誤會保留上次成功快照，並在下一輪重試。

連線和快照存於工作台的 `Runtime/private`。PrintLab 只用這份憑據讀取對應地區的收藏。中國站使用中國區 Bambu Cloud，國際站使用 MakerWorld。收藏介面來自 [社群客戶端的實測記錄](https://github.com/sebasdoes/bambu-downloader/blob/main/app/makerworld.py)。

## 驗收方式

安裝 Agent 核對原 Handy、Studio 與 MakerWorld 的已有功能仍然可用，再選一條 Bambuddy 已捕獲的列印記錄與一項本機登記收藏，驗證工作台顯示、來源 ID、時間與文件可用性。缺圖時按預覽恢復流程核對檔案、設備、設定和板號，記錄實際恢復數量和缺失原因。

報告問題時提供版本、機型、設定名稱、脫敏錯誤碼與缺失記錄的時間範圍。帳號密碼、訪問碼、API key 與登入 token 留在使用者自己的設定中。

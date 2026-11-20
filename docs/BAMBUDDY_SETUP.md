# 獨立連接 Bambuddy

PrintLab 通過 HTTP API 讀取獨立執行的 Bambuddy。當前適配驗證版本為 `v1.2.5.7`，原始碼提交 `188df76f8a7342542c0876dac68990ea2a8c8313`。請從原作者獲取並按對應作業系統的安裝方式執行。[官方安裝說明](https://wiki.bambuddy.cool/getting-started/installation/)

## 首次連接

1. 開啟自己的 Bambuddy 頁面，先確認服務能獨立訪問。官方安裝常用 `http://localhost:8000`，PrintLab 示例設定沿用 `http://127.0.0.1:8017`。將 `Runtime/config.json` 的 `bambuddy_url` 改成實際地址。
2. 按 Bambuddy 的添加印表機流程填寫自己的設備資訊，等待狀態與材料讀回。網路模式、韌體與開發者模式按自己機型核對，具體路線見連接指南。[添加印表機](https://wiki.bambuddy.cool/getting-started/first-printer/) · [連接方式](CONNECTIONS.md)
3. 為 PrintLab 新建專用 API key，啟用讀取狀態權限，用於設備、庫存和 Bambuddy 已儲存歷史。填寫到本機 `Runtime/private/bambuddy.json` 的 `read_api_key`。已有 API key、帳號雲登入、同步設定與其他應用權限按使用者現有用途保留。雲訪問和模型匯入各自按實際功能設定，見 [同步排查](SYNC_TROUBLESHOOTING.md)。
4. 讀取印表機 ID，寫入 `Runtime/config.json` 的 `printer_id`。設備型號、噴嘴、列印板與實際供料路線寫入設備檔案。
5. 執行 `printlab status` 和 `printlab materials`。核對目標機器、在線狀態、資料更新時間和槽位。首次連接結果寫入自己的 `Library/Devices/X2D/installed.md`。

需要通過 Bambuddy 發送具體任務時，再按所選通道設定獨立寫入憑據。官方 Studio 通道的控制條件見列印指南。[列印能力](PRINTING.md)

## 可復現的介面驗收

維護者可執行 `Runtime/venv/bin/python scripts/verify_bambuddy_install.py`，Windows 使用 `Runtime/venv/Scripts/python.exe`。腳本從原倉庫下載上述版本，在臨時虛擬環境安裝服務端，使用獨立資料庫與本機隨機連接埠，通過真實 PrintLab 客戶端檢查設備列表、庫存、槽位、佇列、歷史與列印日誌。

測試建立臨時只讀 key，驗證後撤銷，關閉服務並清理臨時資料。結果和實際依賴版本寫入 `Runtime/verification`。測試範圍為服務端安裝和空資料介面，前端安裝、添加真實印表機及遙測讀取需在使用者環境核對。

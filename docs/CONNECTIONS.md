# ChatGPT、電腦和手機怎樣參與列印

PrintLab 是執行在你自己電腦上的工作台。ChatGPT/Codex 需要宿主提供本機文件、終端或桌面操作工具，才能執行相應工作；只有網頁聊天並不自動獲得這些能力。

| 入口 | 實際路徑 | 條件與邊界 |
| --- | --- | --- |
| Agent 設計 | 需求 → Text-to-CAD/參數化源文件 → 真實預覽 → Bambu Studio 切片 → PrintLab 登記 | 需要本機執行及對應工具；圖像生成和 CAD 查看能力分別核驗 |
| Agent 控制列印 | 具體任務批准 → PrintLab 預檢與預約 → 官方 Studio 介面發送一次 → 設備讀回 | 需要桌面控制能力；Windows 可由具備該能力的 Agent 操作官方介面，尚無 Windows 專用自動發送助手 |
| 工作台一鍵啟動 | 待列印卡片 → 核驗 → 清板確認 → 啟動 → 本機 Studio 助手 | 僅 PRINTING.md 列明的 Mac/X2D/Studio/材料組合；按鈕不繞過預檢和授權 |
| 電腦 Studio | 開啟已綁定的切片包，核對設備、板型及材料，再按 PrintLab 官方交接發送 | 不重新切片或換包後沿用舊批准，發送不明不得重複點 |
| 手機瀏覽器 | 私人網路連接電腦上的 PrintLab 網頁 | 電腦服務需持續執行；發送仍由電腦執行，Mac助手需已登入且解鎖 |
| Bambu Handy | 拓竹官方雲服務與手機應用 | 與 PrintLab 手機網頁是不同入口；LAN Only 下的可用功能按機型手冊核實，不能承諾仍可雲列印 |

Bambuddy 捕獲的 Studio/Handy 列印歷史可以在工作台顯示；歷史可見不等於 PrintLab 已取得這些客戶端的控制能力。

## 先選擇連接路線，再修改印表機設定

不能把“所有工作台連接都必須開啟 LAN Only”作為統一前提。只讀監控、第三方直接控制和官方 Studio 發送有不同條件。先查你當前機型、韌體及所選路線。

Bambuddy 文件對較新韌體的完整第三方控制要求 LAN Only 與 Developer Mode；僅 LAN Only 而無開發者模式可能只有監控能力。先確認使用者是否需要 Handy 雲列印和雲端記錄，說明模式切換對這些功能的影響，再由使用者選擇路線。選定本機控制路線後按對應機型菜單設定並讀取訪問碼，切換模式後舊碼可能失效。官方 Studio 路線使用官方應用的連接與授權，不能把原生第三方通道受限說成所有發送都不可用。[Bambuddy 設備與開發者模式說明](https://wiki.bambuddy.cool/reference/printers/)

在 Bambuddy 中添加設備需要對應的地址、序列號、訪問碼和可通信網路。核對電腦/服務到印表機的連通性，避免訪客 Wi-Fi 隔離。只讀驗收應讀回正確機型/身分、當前狀態、溫度及 AMS 資料；不要通過加熱、運動或列印試探連接。[首次設備設定](https://wiki.bambuddy.cool/getting-started/first-printer/)

## 設定 Bambuddy

從 [官方安裝頁](https://wiki.bambuddy.cool/getting-started/installation/) 獨立安裝。Windows 有獨立安裝器，預設服務地址為 `http://localhost:8000`；本專案歷史示例 `8017` 並非固定要求。將實際地址寫入 `Runtime/config.json` 的 `bambuddy_url`，並填寫真實 `printer_id`。

在 Bambuddy 建立所需 API key，儲存在 `Runtime/private/bambuddy.json`。先設定只讀 key 驗收 `status` 和 `materials`，需要佇列寫入時再設定寫入權限。Studio 官方發送不等於呼叫 Bambuddy 佇列。

## 手機訪問

本機地址 `127.0.0.1` 在手機上指手機自身，不能拿它訪問電腦。按 PRINTING.md 設定私人 Tailscale 連接與本機 `tailscale_ip`，手機登入同一私人網路後訪問電腦地址與工作台連接埠。無需為演示把工作台公開到互聯網。網頁能開啟、能預檢、能發送分別驗收；鎖屏或權限不足會影響 Mac 助手。

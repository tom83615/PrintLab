# 驗證記錄

## v0.5.0 workbench project deletion

The browser check creates two projects in a temporary workspace and opens the target from the project gallery. It cancels once, attempts deletion during an active workbench operation, then confirms after that operation ends. It checks the actual project directory, the original source outside the project, the sibling project's metadata and the gallery after a reload. Both desktop and narrow-screen layouts are exercised. Run `scripts/verify_browser.py` after setup with Playwright and Chromium installed.

`Harness/tests/test_project_delete.py` covers the HTTP confirmation, project identity, active jobs, shared data, concurrent changes and retry after interrupted file cleanup. The release ZIP installation check also runs the deletion tests in a new workspace. Hardware is outside the scope of these checks.

## v0.4.4 English-first documentation

## v0.4.0 個性化工作流與發送準備

2026-11-13，功能候選 `898f7ca` 在 macOS、Windows Server 2022/Python 3.11 與 Windows Server 2025/Python 3.13 雲端虛擬機全部通過。Mac 為438項通過、9項跳過及9個子場景通過；兩臺Windows各414項通過、33項跳過。每組另通過21項乾淨ZIP迴歸。跳過項包括平臺專屬、私人樣本和實體設備檢查。[候選雲端記錄](https://github.com/AFangTeam/PrintLab/actions/runs/43326110000)

- 從ZIP全新安裝，檢查初始化、中斷接續、共同狀態、材料補錄、併發更新和設定保留。
- 獨立安裝Text-to-CAD、Bambuddy與官方Bambu Studio。五機型X2D、A1、A1 mini、P1S和X1 Carbon完成實際可編輯工程匯出、官方切片及文件檢查。
- 八個工作台頁面完成真實瀏覽器驗收。發送邊界使用模擬，雲端均未連接實體印表機。
- Mac Codex實際建立Mike和Sarah兩個聊天，讀回各自介紹及同一工作區。Windows實際宿主建聊仍待現場驗證。
- 本機正式程式碼實際完成Studio切片開啟、發送視窗準備、設備/料位/材料/選項核驗。延時攝影從開啟恢復關閉、設備重新整理按鈕定位與點選均已實測。
- 單噴嘴顯示經人工重新整理轉為完整雙噴嘴已實測。自動觸發重新整理再全量核驗的組合由迴歸覆蓋，尚未取得該組合的現場端到端證據。

本輪按專案維護者決定取消實體試打。最終發送、設備接受、首層和成品尚未驗收；其他機型硬體、Windows 10/11桌面及新觀眾從倉庫到首件成品的完整現場體驗仍待驗證。Mac發送助手當前限固定中文Studio版本、X2D、單主料AMS左主噴嘴、PLA/PETG、紋理PEI單盤。跨平臺Bambuddy佇列通道已通過軟體迴歸。

第12輪Claude只讀複核未提出新修改項。已修復短命助手啟動等待競爭、設備名稱缺項、低密度截圖識別和冷啟動設備卡重新整理。結果未知時保留記錄並先對賬，禁止自動重發。保留一項Starlette httpx棄用提示。最終發佈提交和安裝包SHA-256見對應Release說明。


## v0.3.1 預覽恢復

2026-11-12，本機 Mac 完整 Python 測試 392 通過、9 跳過。新增 15 項恢復測試覆蓋 CFURL 內嵌圖片和外部文件、WebKit 內嵌圖片和 blob、缺失緩存、損壞圖片、路徑越界、身分缺失、板號衝突、圖片衝突、不同設備、舊索引、重複執行、中途失敗重試、併發進程以及正常 CLI 入口。顯式緩存 URL 下載通過模擬 HTTP 驗證開關、域名、跳轉、大小與隱私邊界，真實過期連結的可用性取決於官方服務。

本機真實 Bambuddy 樣本共 40 條檔案。當前 Studio WebKit 緩存可恢復 5 條，重複執行新增 0 條，全部 5 張 PNG 校驗通過。當前 CFURL Cache.db 已不存在。帶入原有 26 條關聯及圖片後，26 條全部保留，另恢復 5 條。驗證寫入隔離臨時目錄，私人索引哈希保持一致。真實緩存和圖片均留在本機。

Windows 原生 Studio 緩存解析尚未實現。Windows 的 PNG / 3MF 清單、PowerShell 正常入口、中文空格路徑與併發寫入由同一套測試覆蓋。三平臺 CI 同時從 git archive 生成 ZIP、核對恢復模塊與相容腳本入包、在獨立目錄安裝並再次執行恢復測試。對應執行和 Artifacts 可在 PR #3 的 Desktop VM verification 中查看。

本機 Chromium 驗收已讀回三種來源標籤和三張合成 PNG，頁面腳本錯誤為零。測試通過真實本機文件 HTTP 路由載入圖片。設備與 GUI 發送邊界沿用合成驗證。

預覽符合到設定與板號後，圖冊顯示“設定板預覽”。當次修改、實際顏色與實體品質仍需要原始切片及實物證據。帳號舊列印歷史可從原應用查看，MakerWorld 收藏依[同步排查](SYNC_TROUBLESHOOTING.md)單獨驗收。

## v0.3.0 三平臺驗收

2026-11-12，候選 `5416518` 的 PR 合併預覽 `f997fc0` 在 GitHub 託管 macOS、Windows Server 2022 和 Windows Server 2025 虛擬機全部通過。報告和安裝包已下載讀回。[雲端記錄](https://github.com/AFangTeam/PrintLab/actions/runs/43144025772)

- Mac Python 測試 377 通過、9 跳過。兩臺 Windows 各 363 通過、23 跳過。跳過項對應平臺專屬檢查及需要使用者設備、設定和私人模型的集成檢查。
- 從原始碼 ZIP 在中文空格目錄全新安裝，檢查 CLI、初始化保留設定、真實公開文件檢查器、專案建立與跨進程接續。
- 獨立安裝 Text-to-CAD 0.11.9，真實生成臨時幾何，核對體積、有效性以及 STEP/STL 匯出。
- 獨立安裝 Bambuddy v1.2.5.7，通過六個真實只讀介面，撤銷測試 key，停止服務並刪除臨時資料。
- 獨立下載官方 Bambu Studio 02.08.02.61，校驗下載哈希，解析官方 X2D 設定，真實切片並完成啟動指令審查及公開文件檢查。
- 真實 Chromium 驗收工作台和待列印頁。Mac 檢查、清板確認、提交與重新整理後單次發送記錄通過。Windows 顯示官方 Studio 手動交接路徑。設備和 GUI 發送邊界採用模擬，頁面腳本錯誤為零。

本輪修復了 Windows 臨時 SQLite 文件在服務退出後仍被佔用的清理失敗。清理會等待最多 15 秒，持續失敗仍使驗收失敗。此前 GitHub 排隊狀態異常通過服務恢復後手動重新觸發解除。

雲端 Windows 使用 Server 虛擬機。Windows 10/11 桌面、CAD 宿主外掛程式與查看器、GUI 登入和權限、真實印表機連接及實體列印仍需現場驗證。測試生成物僅供臨時驗收。

## v0.2.0 Windows 與 Mac

2026-11-11 在 GitHub 託管 Windows 虛擬機完成獨立安裝與驗收，原始碼提交 `b5a87c3`。Windows Server 2022 使用 Python 3.11.9，Windows Server 2025 使用 Python 3.13.17，Node.js 22。兩臺機器各自完成以下檢查。

- PowerShell 安裝入口、生產網頁構建、CLI 入口和真實服務啟動。
- Python 測試各 **356 通過、20 跳過**。包含跨進程排他鎖、中文文件讀寫、私人目錄 DACL 和 Windows 官方 Studio 提示。
- Node 離線檢查各 **12 通過**。
- 獨立進程入門驗收全部 5 組通過，驗證建立專案、分工、交接與下一進程接續。
- Chromium 開啟總覽及七個工作台頁面，建立並讀取中文專案，在包含空格和中文的臨時路徑執行實際服務器，頁面腳本錯誤為零。
- 儲存 JUnit XML、瀏覽器結果 JSON、桌面/窄屏截圖和服務日誌。查看對應 Windows job 與 Artifacts。[雲端執行記錄](https://github.com/AFangTeam/PrintLab/actions/runs/43027295139)

本機 Mac 對相同原始碼執行 **368 通過、8 跳過**，Node 12 項通過。此前候選 `adc2619` 的 macOS 雲端安裝、入門驗收與瀏覽器檢查通過。其後的平臺程式碼改動為 Windows DACL 設定與 Mac 專用命令在 Windows 上的錯誤提示。[Mac 雲端記錄](https://github.com/AFangTeam/PrintLab/actions/runs/43026694159)

Windows 的 20 項跳過包括 14 項 Mac 專用適配檢查，以及 6 項實際設備、已安裝切片設定與私人模型樣本檢查。Mac 的 8 項跳過包括這 6 項與 2 項 Windows 專用檢查。

Windows 雲端環境為 Server 2022/2025 x64。Windows 10/11 桌面、真實 CAD/切片軟體、印表機連接與實體列印待現場驗證。自動 Studio 發送助手適用於 macOS，Windows 使用官方 Studio 介面交接。官方 `submit` 預約介面依賴的獨立原生檢查客戶端尚未完成 Windows 安裝驗收。瀏覽器合成專案驗收覆蓋工作台與文件交接，宿主聊天建立仍按實際能力確認。

v0.1.2 驗證日期為 2026-11-11。驗收使用同一臺 Apple Silicon Mac 的全新隔離目錄、獨立 Python 虛擬環境與獨立工作台連接埠，Python 3.13、Node.js 22.23.2。

## v0.1.2 已完成

- 下載公開 v0.1.1 ZIP 並全新安裝，檢查原有觀眾與 Agent 入門流程，據此修復文件、模板及 CLI 缺口。
- 將 v0.1.2 待發布文件複製到另一空目錄，執行 `scripts/setup.sh`，安裝依賴並完成網頁生產構建。
- Python 自動測試 **365 通過、6 跳過**。覆蓋專案與版本、文件路徑、確認與回執、重複發送防護、重啟恢復、材料、購物清單、歷史、安裝初始化、自定義連接埠、分工讀取及發送助手 CLI 路由。
- Node 離線檢查 **12 通過**。
- `scripts/verify_onboarding.py` 通過全部 5 組檢查。實際 CLI 子進程完成空工作區初始化、新建立專案、分工記錄、兩次交接及新進程接手；HTTP API 可讀取專案、需求和分工，設備保持待設定，待列印佇列為空。
- 使用 `scripts/start.sh --port 18018` 啟動全新工作台。在瀏覽器填寫“新想法”，點選複製後顯示成功狀態；用 CLI 建立該模擬需求，重新整理後顯示 P001 專案及初始需求。
- 瀏覽器開啟“覆盤與接續”，確認 Sara、Mike、任務小組的模擬分工與本輪交接實際可見。下一進程繼續相同專案，歷史交接保留。
- `printlab studio-bridge capability` 對未安裝助手返回對應狀態。build、capability、permissions 三條 CLI 路由通過 mock 檢查。
- 發佈文件檢查覆蓋個人絕對路徑、模型文件擴展名及 Markdown 相對連結。

## 首版已有驗證

- 初始化重複執行保留已有設定與使用者偏好，私人設定檔權限為 600。
- 獨立工作台的健康、專案、總覽、設備、歷史、購物、資料和待列印介面返回 HTTP 200。
- `Harness/macos/build.sh` 完成可選 Mac 應用構建及本機簽名校驗。原生視窗交互尚未單獨驗收。
- 發佈文件檢查覆蓋內網地址、憑據常見格式及嵌入憑據的 URL。

## 驗證範圍與待驗證項

6 項跳過分別對應實機只讀集成、兩項已安裝切片設定和三項私人真實切片樣本。相關資料由使用者在自己環境中提供。

本輪角色任務採用模擬記錄，驗證的是共享文件、CLI、網頁與跨進程接續。實際宿主建立 Sara/Mike 聊天和跨聊天調度尚未驗收，也尚未開展獨立 Agent 僅憑倉庫的盲測。

其他 Mac 上的安裝、圖像生成、真實 CAD、切片、設備連接、Studio 權限與列印，需要按 `AGENT_START.md`、`SETUP.md` 和 `PRINTING.md` 在當地環境逐項驗證。其他機型、Bambuddy 新版、其他 Studio 版本與多材料發送路線尚待驗證。

構建保留兩條非阻斷提示。Three.js 分包約 528 kB，Vite 提示超過 500 kB。當前 Starlette 測試客戶端提示其 httpx 相容介面將棄用，全部測試仍通過。

## 復現

```bash
bash scripts/setup.sh
Runtime/venv/bin/python scripts/verify_onboarding.py
Runtime/venv/bin/python -m pytest Harness/tests -q -rs
node --test Harness/tests/native-inspection.test.mjs
cd Harness/studio
npm run build
```

有設備連接時，先核對測試目標與環境，再顯式選擇 `PRINTLAB_LIVE_TEST=1` 的只讀集成測試。實際列印依照當前具體任務的確認流程執行。


## 2026-11-13 Mac 發送視窗候選修正

本機真實執行已驗證冷啟動載入切片，並開啟對應發送視窗。實際視窗檢查發現低密度截圖會把相鄰按鈕識別為合併文字，也發現螢幕讀取確認提示可能覆蓋視窗。發送助手現先檢查選項，狀態已經正確時跳過設定點選，系統提示和錯誤任務會停止準備動作。

本輪本機 Python 迴歸為 434 通過、9 跳過，另有 4 個入口子場景通過，Swift 類型檢查通過。覆蓋任務不符合、系統提示、合併文字拒絕和已正確設定時跳過點選。原有依賴棄用提示仍存在。

低密度截圖的 2 倍重採樣已加入候選，實際按鈕識別和切換效果仍待無遮擋視窗驗證。本輪沒有呼叫最終發送動作，實體任務符合、首層和成品驗證仍待完成。Windows 宿主建聊仍需實際宿主驗證。雲端舊提交的成功結果保留在原記錄，新程式碼的雲端結果應按具體提交查詢。

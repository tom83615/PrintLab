# Agent 從 GitHub 接手 PrintLab

## 接手目標與當前能力

目標是讓使用者擁有自己的工作台、共同資料、角色分工和可跨會話繼續的專案。首先確認當前 Agent 能讀取 GitHub、執行本機終端、讀寫目標目錄。瀏覽器/桌面控制、圖像生成、CAD 查看器和聊天管理能力按當前宿主實際暴露的工具記錄。

使用者給出本倉庫連結並要求安裝時，先讀取 README 和 AGENTS。按下面步驟自主完成授權內的安裝、軟體驗收和故障修復。需要帳戶登入、密鑰授權、系統權限選擇、實體測量或裝料時，給出具體操作，取得實際結果後繼續。

所有相對路徑均以倉庫根目錄為基準。共享目錄是本機唯一長期工作區。示例專案 ID 必須替換為命令實際返回的 ID。

## 下載和安裝

先識別作業系統。Windows 使用 `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1` 安裝，使用同樣方式執行 `scripts/start.ps1` 啟動。以下 Bash 示例中的 `./Harness/bin/printlab` 在 PowerShell 中替換為 `powershell -NoProfile -ExecutionPolicy Bypass -File .\Harness\bin\printlab.ps1`，`Runtime/venv/bin/python` 替換為 `Runtime/venv/Scripts/python.exe`。Windows 完整步驟見 [Windows 指南](WINDOWS.md)。

1. 檢查當前目錄和已有安裝，找到已有工作區就接續。新安裝選擇使用者指定路徑，未指定時可採用 `~/PrintLab`，已有同名目錄時先檢查內容。
2. 克隆 `https://github.com/AFangTeam/PrintLab.git`，或下載 Release 的 `PrintLab.zip`。將 Codex 工作區指向實際倉庫根目錄。
3. 檢查 `python3 --version`、`node --version` 和 `npm --version`。需要 Python 3.11+、Node.js 22+。系統解釋器較舊時，使用本機合適的解釋器路徑設定 `PRINTLAB_PYTHON`。缺少的基礎執行時從官方來源安裝。
4. 執行 `bash scripts/setup.sh`。安裝結果應包含 `Runtime/venv/bin/python`、`Harness/studio/dist/index.html`、本機設定及 `Context/team.md`。
5. 執行下面的入門驗收。它使用臨時工作區，通過實際 CLI 子進程檢查建專案、分工、交接、重新讀取及 API。命令結束輸出 JSON，`ok` 應為 `true`。

```bash
Runtime/venv/bin/python scripts/verify_onboarding.py
./Harness/bin/printlab doctor
./Harness/bin/printlab context
```

`doctor` 的工具路徑存在檢查只能說明文件存在。繼續用各工具實際幫助和最小功能呼叫驗證可用性。第一次 `context` 的 `missing` 應為空，設備和材料可以處於待設定狀態。

## 啟動與檢查工作台

執行 `bash scripts/start.sh`，在單獨終端或宿主提供的持久進程中保持服務。開啟 `http://127.0.0.1:8018`。預設連接埠被佔用時，核對已有服務身分，獨立工作區可使用 `--port 18018`。

檢查 `/api/health` 返回 `ok: true`，網頁能顯示總覽、專案圖冊、資料與設備頁。空工作區應顯示待設定設備。先把工作台地址和啟動方式交給使用者。服務存活期間網頁可持續訪問，終端停止後需重新執行啟動命令。

## 首次設備與偏好設定

先完成 [首次設定訪談](FIRST_RUN.md)，把已確認資訊寫入共享設備檔案與個人偏好。任務小組須讀取同一份記錄，不能套用作者的機器設定。

## 建立團隊

按 [可恢復設定流程](ONBOARDING.md) 檢查宿主能力、查詢已有聊天、預留缺少角色、呼叫宿主建立工具並讀回首次介紹。使用者已要求自動建隊時，主 Agent 完成這段任務。新角色使用 Sarah 和 Mike，已有 Sara 入口可以直接接續。角色提示詞與職責見 [角色說明](ROLES.md)。

工作台“設定與團隊”展示實際介紹、共同資料和待辦。`Context/onboarding.json` 儲存建立證據，`Context/team.md` 保留使用者的團隊說明。兩個角色沿用主會話已收集的答案，只有真實缺項才繼續詢問。

## 建立真實專案與分工

先用 `./Harness/bin/printlab status` 查找是否已有對應作品。已有作品繼續其 ID。新作品從用途、關鍵尺寸、外觀和驗收標準開始，未知事實保持待補充。

```bash
./Harness/bin/printlab new '桌邊耳機掛鉤' --kind functional --brief '用途為懸掛耳機，桌板厚度和載荷待使用者測量' --summary '桌邊掛鉤，先整理需求'
```

命令返回專案 ID 後，執行 `./Harness/bin/printlab context 專案ID`。根據返回的 `documents[].path` 找到以下文件並填寫。

- `brief.md` 儲存需求、已知條件與待確認事項。
- `decisions.md` 記錄實際確認及出處。
- `Review/team.md` 記錄當前統籌、Sara 的材料/配件任務、Mike 的工具任務，以及實際產出與交接。
- `Context/team.md` 記錄這件作品對應的任務小組聊天入口。

在工作台重新整理專案圖冊，檢查新專案及需求可見。為作品建立聊天需要使用者要求或當前建立團隊指令中的明確授權，聊天命名採用“任務小組 · 作品名稱”。

## 儲存與驗證交接

在每輪結束執行以下命令，內容使用本輪事實。

```bash
./Harness/bin/printlab handoff 專案ID --note '角色、當前版本、本輪完成、驗證證據、使用者確認、未解決項、下一步及相關路徑'
./Harness/bin/printlab context 專案ID
```

確認返回內容包含本輪交接和 `Review/team.md`。下一位 Agent 以相同工作區和專案 ID 再執行 `context`，按 `latest_session` 指針繼續。專案正式版本由當前統籌者維護，協作候選用獨立目錄，合入時重新核對來源和輸出。

## 接入設計與列印工具

按照 [依賴說明](DEPENDENCIES.md) 閱讀上游當前安裝方法，在使用者授權範圍內從原作者渠道獨立安裝。分別記錄工具版本、實際入口、檢查結果和未完成項。

| 能力 | 必要條件 | 最小驗證 |
| --- | --- | --- |
| 概念圖與選圖 | 宿主可用的圖像生成或使用者提供的參考圖 | 能生成/讀取圖片並儲存選擇證據 |
| CAD 與預覽 | Text-to-CAD、適用的 CadQuery/Blender 環境 | 實際匯出、單位/尺寸檢查與預覽 |
| 材料與設備 | Spoolman 與 OpenSpoolMan，或獨立 Bambuddy 與對應憑據 | `status` 與 `materials` 讀回正確設備和來源 |
| 正式切片 | 官方 Bambu Studio 與本機設定 | 實際切片、板型/材料映射和時間用量檢查 |
| 發送助手 | 支援範圍內的設備/Studio、助手和系統權限 | `studio-bridge capability` 返回實際結果 |

開始新外形前讀取 `Context/image-to-print.md`，在記錄使用者選擇時從 `Templates/Project/Review/design-target.json` 初始化專案對應文件，填寫實際圖片、哈希和選擇。模型選擇讀取 `Context/agent-policy.json`，空值時使用使用者當前可用的模型，並記錄實際執行者。

首次設備接入遵循 [安裝指南](SETUP.md)。實際列印按 [列印說明](PRINTING.md) 綁定具體文件與印表機身份；逐任務材料/路線/設備就緒/清板確認不作為必要門檻。

## 交付給使用者

報告實際工作區、工作台地址與再次啟動命令、已建立的角色入口、專案 ID 與當前階段。分別列出工作台、專案接續、圖像、CAD、切片、設備和列印的驗證結果。為缺失能力寫清具體下一步。驗收依據包含真實命令結果、網頁顯示、文件與交接內容。

連接模式與手機/電腦/Agent 的具體路徑見 [連接與控制指南](CONNECTIONS.md)。

Text-to-CAD 的固定版本、Mac/Windows 安裝命令、宿主接入和最小建模驗收見 [CAD 安裝指南](CAD_SETUP.md)。Text-to-CAD 草稿交給 SolidCraft 進行 MCP 精修的流程見 [SolidCraft MCP 指南](SOLIDCRAFT_MCP.md)。

## 既有終端與帳號同步

安裝先記錄使用者正在使用的 Handy、Studio、Bambu Cloud 和 MakerWorld 功能，保留其帳號登入、網路模式與現有憑據權限。為 PrintLab 新建專用讀取憑據。使用者需要雲功能時，先說明 LAN Only / Developer Mode 的具體影響並確認所選路線。按 `docs/SYNC_TROUBLESHOOTING.md` 核對歷史與收藏的實際來源及覆蓋時間，核對原應用功能仍然可用。帳號舊歷史和 MakerWorld 收藏匯入已排除在本輪開發範圍外。已有檔案缺圖時，按 `docs/PREVIEW_RECOVERY.md` 使用 `printlab history-recover`，記錄來源和恢復數量。

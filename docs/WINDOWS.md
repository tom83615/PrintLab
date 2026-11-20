# Windows 安裝與工作流

Windows 版本提供瀏覽器工作台、專案與版本管理、中文資料、跨會話交接、材料與列印記錄、購物清單和列印包管理。使用 Python 3.11+、Node.js 22+（含 npm）以及有本機終端和文件訪問能力的 Codex。

## 安裝與啟動

從 Release 下載 `PrintLab.zip` 並解壓，或克隆倉庫。進入 PrintLab 資料夾，在 PowerShell 執行。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start.ps1
```

開啟 http://127.0.0.1:8018 。保持啟動終端執行。獨立工作區需要其他連接埠時，在啟動命令末尾加 `--port 18018`。執行策略參數僅對該進程生效。

安裝腳本優先使用 Python Launcher 的 `py -3`，也支援 PATH 中的 `python`。指定解釋器時，先設定 `$env:PRINTLAB_PYTHON = 'C:\你的路徑\python.exe'`。重複安裝會保留已有設定。使用已下載 ZIP 時可以跳過 Git 安裝。

## 驗證與接續

```powershell
.\Runtime\venv\Scripts\python.exe scripts/verify_onboarding.py
powershell -NoProfile -ExecutionPolicy Bypass -File .\Harness\bin\printlab.ps1 doctor
powershell -NoProfile -ExecutionPolicy Bypass -File .\Harness\bin\printlab.ps1 context
```

入門驗收建立臨時中文專案，通過獨立進程檢查專案、分工、交接和 API，成功輸出 `ok: true`。Sarah、Mike 和任務小組共享同一工作區，按接手指南建立入口與交接記錄。其餘文件的 `./Harness/bin/printlab` 命令在 Windows 中使用以上 PowerShell 入口，後面的子命令和參數相同。

## 獨立安裝設計與列印工具

Bambu Studio、Blender、Text-to-CAD、Bambuddy 和可選建模依賴均從各自上游獨立獲取。按照上游 Windows 安裝說明記錄實際版本和可執行文件路徑。來源見 [依賴說明](DEPENDENCIES.md)。

獨立安裝步驟見 [Text-to-CAD](CAD_SETUP.md)、[Bambuddy](BAMBUDDY_SETUP.md) 和 [Bambu Studio](STUDIO_SETUP.md)。

在 `Runtime/config.json` 核對 `slicer_path`、`slicer_profiles_path`、`blender_path` 和 `cad_python`。安裝程序會查找 PATH 與 Program Files 中的 Bambu Studio、Blender。JSON 中 Windows 路徑可使用正斜槓，例如 `C:/Program Files/Bambu Studio/bambu-studio.exe`。切片設定目錄通常為安裝目錄的 `resources/profiles`，應以實際安裝為準。

需要 CadQuery 匯出時，使用本機虛擬環境獨立安裝並檢查實際匯出。

```powershell
.\Runtime\venv\Scripts\python.exe -m pip install cadquery trimesh numpy pillow
```

MLX 圖生模型路線適用於 Apple Silicon。Windows 的圖生模型工具需按對應上游說明獨立選擇和驗證。模型權重由使用者從原作者獲取。

## 通過官方 Studio 列印

Windows 的待列印頁按任務綁定的通道處理。使用 `bambuddy_queue` 的適配機型可以通過工作台按鈕發送，條件與當前驗證範圍見 PRINTING.md。官方 Studio 包按下面步驟交接，Mac 的專用視窗助手仍需 macOS。

1. 在 PrintLab 儲存當前版本、切片包、設備、板型、材料映射和用量，確認具體作業及清板狀態。
2. 使用 `studio-copy 專案ID 作業ID` 準備官方 Studio 副本，按命令返回內容核對文件與任務記錄。先查看當前 `--help`。
3. 使用者或具備桌面控制能力的 Agent 在官方 Studio 開啟該副本，核對設備、材料與發送選項。儲存使用者對具體文件的批准，在 Studio 發送一次，並把任務名、文件哈希、時間與回執寫入專案 Session。
4. 單次發送後讀取設備狀態與任務回執。回執不明確時先對賬，再決定下一步。
5. 儲存首層、完成狀態與實物回饋，繼續相同專案。

安裝腳本會獨立下載固定版本的公開文件檢查器。`doctor` 實際執行文件檢查，並報告依賴缺失或呼叫失敗。Windows 的文件檢查、官方預約和工作台 API 可執行。本候選版新增共用 Bambuddy 佇列按鈕適配；Mac Studio 助手繼續僅在 macOS 使用。Windows 虛擬機中的新通道迴歸與實體發送驗證尚待完成。

具體批准和回執約束見 [列印流程](PRINTING.md)。首次接入自己的印表機需現場驗證設備、切片與發送。

## 虛擬機驗證

倉庫的 Desktop VM verification 工作流在 GitHub 託管 Windows Server 2022、Windows Server 2025 與 macOS 環境執行安裝、自動測試、獨立進程交接和 Chromium 頁面檢查。每次執行儲存測試結果、服務日誌與截圖。Windows 10/11 桌面、使用者安裝的 CAD/切片軟體以及實體列印需要相應環境驗證。具體已完成結果見 [驗證記錄](VERIFICATION.md)。

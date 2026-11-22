# 更新、備份與回退

更新前記錄當前 Release 標籤和本機工具版本，結束文件編輯並停止工作台。正在列印或回執未知的任務，先保留記錄並讀取實際設備狀態。

## 儲存資料

在當前工作區執行。Windows 將解釋器換成 `Runtime/venv/Scripts/python.exe`。

```bash
Runtime/venv/bin/python Harness/backup.py backup --verify
```

成功結果包含快照位置、恢復驗證目錄和 `sha256: all_match`。備份含本機憑據，應存放在本人受限目錄。該命令驗證文件恢復和資料庫完整性。Bambuddy 安裝在工作區外時，用 Bambuddy 自身備份功能另行儲存它的資料。

另外保留當前版本的完整原始碼 ZIP。備份腳本只複製其清單列出的目錄，環境和第三方安裝需要按原版本重建。

## 升級

Git 使用者先用 `git status --short` 檢查自己修改過的原始碼與流程文件，儲存修改後切換到選定 Release 標籤，再執行安裝腳本。ZIP 使用者將新版解壓到獨立目錄，保留舊目錄，遷移 `Project`、個人 `Library`、`Runtime/config.json` 和 `Runtime/private`。將自己修改過的 `Context` 與新版逐項合併，保留設備檔案和使用者明確決定。

Mac 執行 `bash scripts/setup.sh`。Windows 執行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1`。初始化會保留已有設定。然後執行 `doctor`、`context` 和 `scripts/verify_onboarding.py`，核對專案數量、最近交接、設備身分和材料讀取。

升級前已核准的任務重新核對文件及設備。文件或材料映射變化時按當前任務重新確認。

## Roll back

停止新版工作台，儲存升級後新增的專案與任務記錄。在獨立目錄解壓舊版原始碼，用舊版安裝腳本重建依賴。先恢復到備份驗證目錄並核對 SHA-256，再遷移相應資料，檢查專案和設備連接。保留新版目錄以便找回新增記錄。

實際恢復前核對目標路徑。Bambuddy 資料庫恢復時停止該服務，按其官方恢復流程處理資料庫及伴隨文件。回退後執行 `doctor` 和只讀狀態檢查，未知發送結果繼續使用已有任務記錄對賬。

## 安裝失敗

- Python 版本不足時選擇 Python 3.11+，使用 `PRINTLAB_PYTHON` 指向解釋器後重跑安裝。
- PyPI/npm 下載失敗時儲存錯誤類型和失敗域名，恢復網路後重跑同一安裝命令。
- 文件檢查器失敗時執行 `Runtime/venv/bin/python scripts/install_inspector.py`，Windows 換用對應解釋器，再執行 `doctor`。
- 連接埠占用時核對已有服務。獨立工作區通過啟動命令的 `--port` 選擇連接埠。
- 設備讀不到時依次核對 Bambuddy 頁面、實際服務 URL、只讀 key、印表機 ID 和網路模式。介面連接成功後，再核對即時資料時間與材料。

提交問題時使用倉庫問題表單，附作業系統、Release、脫敏錯誤和復現步驟。憑據文件保留在本機。

## v0.5.0：專案刪除

升級並重啟工作台後，可在專案圖冊選擇「刪除專案」。對話框會顯示名稱與 ID；永久刪除會移除專案本機資料夾、待列印項目及購物需求。取消不會刪除。若有進行中或結果不明的列印，先對賬以保留記錄；印表機歷史、共享庫存、選圖檔案、專案外原始檔和備份會保留。

## v0.4.4: English-first documentation

The Traditional Chinese introduction is available in [README.zh-TW.md](../README.zh-TW.md), and the English guide remains in [README.en.md](../README.en.md). The former Chinese README links to the Traditional Chinese introduction. YouTube is the primary walkthrough link. Merge any customized instructions and retain existing user records. See [language coverage](LANGUAGE.md).

## v0.4.3: route selection and queue checks

The read-only `dispatch-plan` command assesses the route before recommending permissions. Queue startup checks the file, plate and materials; previously approved tasks do not automatically switch routes.

A1 without AMS / using Ext still uses Studio fallback; this combination has no new automatic dispatch adapter. If Studio has already sliced the correct file, continue that print there without upgrading solely for troubleshooting. Upgrade when you want the newer route planning/window helper. Downloading a ZIP does not automatically upgrade an existing workspace.

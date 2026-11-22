# Windows 本機開發與正式部署

| 用途 | 網址 | 資料目錄 |
| --- | --- | --- |
| 開發測試 | `http://localhost:8018` | `%LOCALAPPDATA%\PrintLab\development` |
| Docker 正式版 | `http://127.0.0.1:10818` | `%LOCALAPPDATA%\PrintLab\production` |

請使用表中的主機名稱開啟兩個入口，讓工作台的瀏覽器會話 Cookie 分開。兩個埠均限本機連線。

## 開發

在倉庫根目錄執行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

Python 檔案存檔後會重載服務。前端建置完成後重新整理頁面，建置記錄位於開發資料目錄的 `Runtime/logs`。開發版首次啟動建立空白工作區。執行開發用 CLI 時，先將 `PRINTLAB_ROOT` 指到表中的開發資料目錄，再呼叫 `Harness/bin/printlab.ps1`。

## 正式更新

Docker Desktop 須在執行。將完整提交 SHA 傳給部署腳本：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\deploy-production.ps1 -Revision <40位SHA>
```

部署程式檢查 `tom83615/PrintLab` 的 `tom83615` 分支，以及該 push 的 **Desktop VM verification** 是否成功。若 GitHub API 需要登入，可在執行腳本的終端提供已有讀取權限的 `GH_TOKEN`。腳本從 Git 匯出指定提交，在空白容器中檢查 API、首頁及前端資產，再切換正式容器。程式、前端與模板來自映像，正式專案、設定與憑據保存在宿主機。新容器未通過檢查時會嘗試恢復上一個映像。

首次建立可對本機 `tom83615` 上的已提交版本加 `-Bootstrap`。腳本會額外執行本機工作台測試。若需接續現有工作區，在首次啟用前將 `Project`、`Context`、`Library` 和所需的 `Runtime` 設定及資料複製至正式資料目錄，並保護 `Runtime/private` 的存取權。Windows 虛擬環境、第三方工具、鎖、快取和瀏覽器會話請留在原環境。

如材料服務使用 Windows 已信任的內部 CA，可把其公開 CA 憑證以 PEM 格式放在正式工作區的 `Runtime/container-ca.pem`。容器啟動時會將它加到系統 CA，保留 HTTPS 驗證。工作區的唯讀 CLI 查詢可使用 `docker exec printlab-production-studio-1 python -m printlab.cli status`。

手動切回上一版：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\deploy-production.ps1 -Rollback
```

回退會使用目前正式資料。需要變更資料格式時，先備份正式工作區。工作台可在 Docker Desktop 啟動後自動恢復。Windows 的 Bambu Studio、Blender、CAD 與切片工具由 Windows 執行，可從正式工作區取得檔案後開啟。

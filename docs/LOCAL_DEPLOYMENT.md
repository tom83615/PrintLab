# Windows 本機開發與正式部署

| 用途 | 網址 | 資料目錄 |
| --- | --- | --- |
| Windows 原生開發 | `http://localhost:8018` | 透過正式 API 讀寫共用資料 |
| Docker 正式版 | `http://127.0.0.1:10818` | 預設 `%LOCALAPPDATA%\PrintLab\production`，可設定作品資料位置 |

請使用表中的主機名稱開啟兩個入口，讓工作台的瀏覽器會話 Cookie 分開。兩個埠均限本機連線。

## 開發

在倉庫根目錄執行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

Python 檔案存檔後會重載服務。前端建置完成後重新整理頁面。前端建置及 `Runtime/logs` 日誌存放在 `%LOCALAPPDATA%\PrintLab\development`。作品與列印記錄集中存放在正式工作區，`8018` 將 API 請求交給 `10818`，兩個入口的資料操作使用同一套檔案鎖及同源驗證。

## 正式更新

正式資料位置可在 `%LOCALAPPDATA%\PrintLab\production\workspace-path.txt` 指定。檔案只需一行已存在的 Windows 絕對路徑。搬移時，先停止正式服務，再複製 `Project`、`Library` 和 `Context` 至新位置。部署、回退與 Windows CLI（`Harness/bin/printlab.ps1`）都會讀取這個設定：`printlab.ps1` 在未覆寫 `PRINTLAB_ROOT` 時會自動指向該外部資料目錄，並共用 `%LOCALAPPDATA%\PrintLab\production\Runtime`（含 `config.json`、鎖與憑據）。

當正式資料目錄位於程式碼倉庫外部時，部署腳本也會在程式碼倉庫根目錄維護受 `.gitignore` 忽略的 `Workspace/` 目錄聯結指向該外部資料目錄，方便本機瀏覽與 AI 探索；即使程式碼倉庫內不含本機專案檔，AI 仍可透過 `workspace-path.txt`、`Workspace/` 或 `printlab.ps1 status` / `context` 回報的 `workspace_root` 找到唯一設計資料空間。`Runtime`、憑據及版本記錄使用原本的本機目錄。

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

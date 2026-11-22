# SolidCraft MCP 使用指引

本流程用 Text-to-CAD 建立草稿，再把 STEP 交給 SolidCraft，讓使用者與 AI 在可視化 CAD 介面中共同修正。SolidCraft 是獨立第三方工具；PrintLab 不附帶它的程式、MCP 伺服器或技能。請從 [SolidCraft 官方網站](https://solidcraft.io/) 安裝穩定版，並遵循其版本相容說明。

## 連接 Codex

1. 開啟 SolidCraft，於 `Preferences > Assistant > Agents through MCP` 啟用 `Let AI agents connect`。這會允許本機 AI 客戶端連到正在執行的 SolidCraft；不啟用時，live 連線不會操作桌面程式。
2. 在 PowerShell 預覽 Codex 設定變更：

   ```powershell
   solidcraft-cli mcp setup --dry-run --client codex --live
   ```

   檢查預覽只會新增 SolidCraft 的 MCP 項目，且用戶端是 Codex。
3. 確認後套用設定：

   ```powershell
   solidcraft-cli mcp setup --client codex --live
   ```

4. 完全重新啟動 Codex，並保持 SolidCraft 開啟。`solidcraft` 可建立不顯示桌面操作的獨立工作階段；`solidcraft-live` 連到開啟中的應用，適合人類同步觀看 AI 修改。SolidCraft 官方文件亦提供應用內 `Help > Connect AI assistants…` 設定入口。

若 PowerShell 找不到 `solidcraft-cli`，先確認安裝程式是否把 CLI 加入 PATH；依 SolidCraft 安裝說明重新開啟終端，或在 Codex MCP 設定中指定 `solidcraft-cli.exe` 的完整路徑。設定後重啟 Codex。

## PrintLab 草稿到 SolidCraft 的交接

1. 用 Text-to-CAD 建立草稿，保留 `.py` 源碼、輸入與建模結果；先檢查毫米單位、實體數、外形尺寸與關鍵配合。
2. 從 Text-to-CAD 匯出 STEP，將它作為 SolidCraft 的修正工作副本。不要覆寫原始草稿或其他已確認版本。
3. 在 SolidCraft 開啟 STEP，先請 AI 檢查設計與量測，再分次提出修改。可用的 MCP 操作包括檢視設計、量測、執行建模指令、復原／重做、儲存及匯出；操作前後都要核對尺寸和實體。
4. 精修後另存 SolidCraft 原生 `.sc`，並匯出新版本 STEP 回到該 PrintLab 專案。記錄兩個檔案的版本關係，明確標出目前正式幾何。兩邊不會自動同步。
5. 設計變化太大時，回 Text-to-CAD 重建草稿，再重新匯出 STEP。正式切片仍使用 PrintLab／Bambu Studio 工作流程；幾何檔不能當作已切片列印包。

### STEP 與特徵歷史

STEP 可讓 SolidCraft 讀取實體幾何並在其上新增特徵，但一般不會帶回 Text-to-CAD Python 源碼或其原始特徵歷史。SolidCraft 會把 STEP 當作匯入基礎特徵；後續 SolidCraft 特徵可在 `.sc` 設計中編輯。不要把 SolidCraft 的 STEP 修改誤認為已同步回原 `.py`。

## 檔案存取與安全

SolidCraft MCP 只可讀寫目前設計所在或本次工作階段已開啟／儲存的資料夾，以及明確授權的資料夾。PrintLab 專案檔應放在目前專案資料夾中；若 MCP 回報路徑不在允許範圍，僅將該專案的既有資料夾加入 SolidCraft MCP 伺服器的 `--allow-path`，然後重啟 Codex。避免使用 `--allow-any-path`，因為授權範圍內的檔案可被 MCP 讀寫或刪除。

變更既有設計前先另存副本；先量測，再修改，再量測並檢查視圖。正式作品保留 Text-to-CAD `.py`、SolidCraft `.sc`、最終 STEP 和各自版本記錄。詳細 MCP 指令、支援格式與權限邊界以 [SolidCraft 官方 MCP 指南](https://docs.solidcraft.io/guide/mcp.html) 和[檔案格式文件](https://docs.solidcraft.io/guide/files.html)為準。

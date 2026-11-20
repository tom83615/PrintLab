# 找回已有列印記錄的模型預覽

`printlab history-recover` 為 Bambuddy 已捕獲的檔案補圖。指定設備後，工具逐頁讀取檔案，符合設定 ID 和明確板號，將 PNG 與關聯表儲存在當前工作區。首次執行預設預演，檢查報告後加 `--apply` 寫入。

## 可用來源

| 系統 | 來源 | 當前支援範圍 |
| --- | --- | --- |
| macOS | Studio 的 CFURL / WebKit 圖片緩存 | 自動定位當前使用者的 `~/Library/Caches/com.bambulab.bambu-studio`，也支援 `--cache-dir` 指定緩存根目錄 |
| Windows / macOS | 本機 PNG 或 3MF 與綁定清單 | `--manifest` 讀取明確綁定的設備、檔案、設定和板號，從 3MF 提取指定板 PNG |
| 任意系統 | 從 Mac 複製的 CFURL / WebKit 緩存 | `--cache-dir` 讀取上述已知格式；Windows 原生 Studio 緩存解析尚未實現 |

緩存可能已被清理、只有 URL 或缺少圖片本體，預設會報告 `not_found`。預設讀取現存圖片字節，聯網請求限於設定的 Bambuddy 檔案 GET 介面。緩存仍有官方圖片 URL 時，可加 `--fetch-missing` 嘗試補回圖片本體，沿用舊腳本的下載能力。下載限定已識別的官方 HTTPS 圖片域名、禁止跳轉並限制圖片大小，過期 URL 計入 `failed_downloads`。帳號舊列印歷史與 MakerWorld 帳號收藏匯入已排除在本輪開發範圍外。

## Mac 操作

先設定 Bambuddy 地址、專用讀取憑據和設備 ID，按 [安裝說明](SETUP.md) 完成基礎連接。工作區根目錄執行以下命令。

```bash
./Harness/bin/printlab history --refresh
./Harness/bin/printlab history-recover
./Harness/bin/printlab history-recover --apply
./Harness/bin/printlab history --refresh
```

緩存只有圖片連結時，可預演並應用下載結果。

```bash
./Harness/bin/printlab history-recover --fetch-missing
./Harness/bin/printlab history-recover --fetch-missing --apply
```

工具預設使用 `Runtime/config.json` 的 `printer_id`。多設備或緩存副本可顯式指定。

```bash
./Harness/bin/printlab history-recover --printer-id 2 --cache-dir "/Volumes/Backup/Studio cache"
./Harness/bin/printlab history-recover --printer-id 2 --cache-dir "/Volumes/Backup/Studio cache" --apply
```

傳入的目錄應直接包含 `Cache.db` 或 `WebKit/NetworkCache/Version */Records`。版本目錄自動枚舉。資料庫、緩存文件和 Studio 登入狀態均保持原狀。

舊腳本路徑作為相容入口保留，同樣預設預演。

```bash
Runtime/venv/bin/python Harness/tools/recover_studio_covers.py --help
```

## Windows 與本機文件操作

從 Bambuddy 的對應檔案確認 `id`、`printer_id`、`extra_data._print_data.raw_data.profile_id` 和 `plate_idx` 或 `plate_id`。清單中的數值須與檔案完全一致。檔案缺少設定 ID 或板號時，先尋找可核對的任務證據。相似標題不能用於綁定。

把下列內容儲存為 `preview-bindings.json`。示例數值需要替換為自己的實際檔案。文件相對路徑以清單所在目錄為基準，也支援本機絕對路徑。Windows JSON 路徑可以使用 `/`。

```json
{
  "schema_version": 1,
  "previews": [
    {
      "printer_id": 2,
      "archive_id": 8,
      "profile_id": "123",
      "plate": 2,
      "file": "models/my-slice.3mf"
    }
  ]
}
```

```powershell
.\Harness\bin\printlab.ps1 history-recover --printer-id 2 --manifest "D:/PrintLab files/preview-bindings.json"
.\Harness\bin\printlab.ps1 history-recover --printer-id 2 --manifest "D:/PrintLab files/preview-bindings.json" --apply
.\Harness\bin\printlab.ps1 history --refresh
```

PNG 同樣通過 `file` 提供。只使用有明確設定和板號來源的模型圖片。清單表達使用者確認的關聯，工具無法獨立證明外部文件就是當次列印文件，因此匯入後顯示“原模型參考”。已經由 PrintLab 任務和切片包準確關聯的圖片繼續優先顯示為“切片模型預覽”。Studio 緩存圖片顯示“設定板預覽”，對應公開設定和板號，當次改動與配色仍需實際切片文件核對。

## 報告與衝突處理

| 狀態 | 含義與處理 |
| --- | --- |
| `ready` | 預演找到一個有效候選，可加 `--apply` 儲存 |
| `recovered` | 圖片與關聯表已寫入 |
| `existing` | 已有有效關聯，重複執行保持原條目和時間 |
| `existing_unavailable` | 已有條目存在但符合、圖片或哈希校驗失敗，保留原條目供調查 |
| `missing_identity` | 檔案缺少設定 ID 或明確板號，或兩個板號欄位衝突 |
| `not_found` | 沒有可讀取且符合的圖片 |
| `conflict` | 同一符合出現不同圖片內容，或目標文件內容衝突，保留空位供核對 |

`issues` 提供缺少緩存資料庫、缺少 WebKit 記錄、損壞圖片、無法讀取來源、模糊緩存記錄和清單不符合計數，同時記錄顯式下載的成功與失敗數量。先處理這些原因，再執行預演。報告省略簽名 URL、原始緩存、帳號令牌和本機來源路徑。

已有 `recovered-previews.json` 的舊數字鍵繼續讀取。新條目使用 `printer_id:archive_id`，同一檔案編號在不同設備間獨立儲存。寫入使用跨進程鎖、原子圖片替換和原子 JSON 提交，重試可複用內容哈希圖片。中途失敗最多留下尚未被引用的圖片，下一次恢復可繼續。

衝突處理時先備份關聯表並核對源證據。工具自動保留已有條目，包括原模型參考。修正關聯表屬於顯式的資料維護操作。

## 複用給 Agent 的步驟

1. 核對當前工作區、Bambuddy 設備 ID 和歷史覆蓋範圍。
2. Mac 優先預演本機緩存。Windows 使用有明確檔案關聯的本機 PNG / 3MF 清單。
3. 檢查缺失身分、衝突和讀取失敗，記錄實際可恢復數量。
4. 在補圖授權內執行 `--apply`，隨後再次執行，核對 `written` 為零及已有記錄保留情況。
5. 用 `history --refresh` 和工作台圖冊檢查圖片、標籤與對應檔案，分別記錄恢復結果和未覆蓋項。

原圖和綁定表屬於使用者的私人資料，位於 `Library/References/PrintHistory/`，發佈 ZIP 只包含工具、說明與合成測試。

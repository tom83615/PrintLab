# 首次設定與中斷接續

主 Agent 負責首次設定，Mike 和 Sarah 接續同一個工作區。先完成 `AGENT_START.md` 的安裝與啟動，然後執行 `printlab onboarding status --refresh`。其中 `version` 用於防止兩個會話同時覆蓋設定進度。所有示例的版本、哈希、專案 ID 和路徑均替換為實際讀回值。Windows 使用 `Harness/bin/printlab.ps1`。

## 收集已經存在的答案

先讀 `printlab context`、`Context/team.md` 和現有宿主聊天。工作區已有使用者答案時，帶原記錄出處登記進度。向使用者只問尚缺的資訊。系統、可用工具和服務端設備列表由 Agent 自行檢查。

圍繞這次使用收集三件事，每項用 `onboarding answer` 儲存。使用者原話保留在共享記錄中。

```bash
./Harness/bin/printlab onboarding answer usage_goals --text '使用者實際目標' --source '使用者訊息或已確認文件位置' --expect 0
./Harness/bin/printlab onboarding answer cloud_needs --text '使用者現有 Handy、Studio 與雲連接需要' --source '實際出處' --expect 1
```

接通後再詢問其他庫存，讀回補錄結果後儲存 `additional_materials` 答案，並在文本里註明實際料卷 ID 或尚待補錄的事實。每次寫入後使用返回的新版本。設備的當前網路選擇按 `CONNECTIONS.md` 處理。

## 核對設備與耗材

已使用 Spoolman 和 OpenSpoolMan 的工作區，按 [連接指南](CONNECTIONS.md) 設定兩個服務網址，執行 `onboarding status --refresh` 讀回庫存與槽位。設備目前的網路模式和官方應用連接可保留。OpenSpoolMan 的 `updated_at` 是 PrintLab 讀取時間，`source_timestamp` 保持未知；不可當成即時遙測。未知重量維持未知，同一卷被多個槽位引用時會列出衝突。槽位快照不能替代實機身分、噴嘴與列印板核對。

使用 Bambuddy 作為資料來源時，在使用者的獨立 Bambuddy 中接入設備，憑據放 `Runtime/private/bambuddy.json`，操作見 `BAMBUDDY_SETUP.md`。既有服務先讀取設定。列表發現使用只讀 API。

```bash
./Harness/bin/printlab onboarding discover
./Harness/bin/printlab workspace connection
./Harness/bin/printlab workspace connect --url http://127.0.0.1:8017 --printer-id 1 --expect-sha 當前設定哈希
./Harness/bin/printlab workspace show device
./Harness/bin/printlab onboarding adopt-device --expect-sha 當前設備卡哈希
./Harness/bin/printlab status
./Harness/bin/printlab materials
```

只有一臺符合使用者描述的設備時可直接採用，多臺且用途不明確時詢問目標。`adopt-device` 記錄實際身分和讀回時間，保留使用者確認欄位。當前設備卡位於 `Library/Devices/H2C/device.json`。出現身分衝突時核對舊設備與新選擇。

按已安裝官方 Studio 設定及使用者實際設備核對可用空間、噴嘴、列印板與供料連接。軟體模板的可選能力與現場已安裝設備分別記錄。通過 `workspace device --file 確認欄位.json --source 事實出處 --expect-sha 當前哈希` 追加使用者確認。文件示例如下，數值必須來自本機事實。

```bash
./Harness/bin/printlab workspace profiles --model 實際機型
./Harness/bin/printlab workspace profile --name '上一步實際列出的預設名稱' --expect-sha 當前設備卡哈希
```

該入口解析已安裝官方設定的繼承與包含關係，儲存來源哈希。列印空間從實際設定讀取，已裝噴嘴仍由設備讀回或使用者確認。Studio 更新導致來源變化時，專案約束提示重新核對。

```json
{"user_confirmed":{"model":"實際型號","build_plate_description":"實際列印板"}}
```

### Spoolman 庫存

先比對現有庫存和 Spoolman 的耗材目錄，核對品牌、材質和顏色。一份 JSON 對應一卷實物，`spoolman_filament_id` 是耗材品項 ID，和實際料卷 ID 不同。只有確認該卷淨餘量後才填 `remaining_weight`。Spoolman 若已知初始重量，漏填餘量會預設為滿卷，所以 PrintLab 會要求核對餘量再寫入。目錄品項沒有初始重量時，可以保留未知。以下數字是格式示例，登記時使用實際值。

```json
{"spoolman_filament_id":1,"remaining_weight":750,"storage_location":"材料櫃"}
```

```bash
./Harness/bin/printlab material-intake --file spool.json --source '使用者確認的料卷事實' --request-id 同一卷的穩定錄入標識 --preview
```

資料核對完成且使用者要求登記這一卷時，移除 `--preview`，保留相同的請求標識。PrintLab 只建立該品項的一卷；不建立或改寫耗材目錄、不更新耗用量、不綁 AMS。結果不明時沿用同一個請求標識讀回，避免重複登記。

### Bambuddy 庫存

使用 Bambuddy 來源時，已裝載材料從即時狀態讀取，其他現有料卷儲存在 Bambuddy 庫存。使用者確認要登記一卷後使用 `material-intake`，支援材料、品牌、系列、顏色、產品號、存放位置及已知標籤克數。需要該服務的 `inventory:read` 和 `inventory:update` 權限。首次權限不足時給出對應權限項，保留其他應用的憑據。

```json
{"material":"PLA","brand":"使用者確認品牌","color_name":"白色","storage_location":"材料櫃"}
```

```bash
./Harness/bin/printlab material-intake --file spool.json --source '使用者確認擁有這一卷的原話與出處' --request-id 同一卷的穩定錄入標識
```

先檢查庫存是否已有同一實物。兩個真實料卷分別登記，外觀相近不代表同一卷。請求標識在超時和接續時保持相同，命令會查回原操作標記。結果不明確時保留待對賬狀態。餘量未知時保持未知，名義標籤克數僅供賬面估算。

## 自動建立兩個獨立聊天

先檢查宿主當前實際可用的工具，寫一份宿主能力 JSON。只有真實暴露且能使用的能力寫 `true`。

```json
{
  "name":"實際宿主名稱",
  "capabilities":{"local_files":true,"terminal":true,"chat_create":true,"chat_read":true},
  "evidence":"實際工具名稱、參數幫助與本工作區讀取結果"
}
```

```bash
./Harness/bin/printlab onboarding host --file host.json --expect 當前版本
```

依次處理 Mike 與 Sarah。已有 Sara 視為 Sarah 的舊名稱。先按實際工作區搜尋已有聊天並讀回，核對 `Context/team.md` 中的歷史入口。

1. 已有相符聊天時，讀取它的工作區、真實 ID 和首條介紹，通過下述回執加 `--adopt-existing` 登記。已有介紹不足時，在該聊天發送完整首次任務並等待回覆。
2. 缺少角色時執行 `onboarding reserve-role Mike --request-id 穩定建立標識 --expect 當前版本`。只有返回 `create_allowed: true` 的這一執行者負責建立。
3. 由主 Agent 呼叫宿主真實建立工具，把返回的 `role.prompt` 作為首條任務，使用同一個絕對工作區。Codex 宿主以當前工具幫助中的 `prompt` 和實際 project target 為準。腳本本身不具備聊天建立能力。
4. 取得最終真實 thread ID 後登記回執。宿主臨時客戶端 ID、僅有標題或計畫文本不足以作為完成證據。
5. 等待並讀回角色回覆及文件讀取記錄，再補充 `first_reply` 和實際 `context_paths`。工作台達到 `introduced` 後顯示它的介紹。
6. 通過帶版本檢查的 `workspace note team` 儲存實際入口與驗收結果。`onboarding.json` 儲存機器可讀的當前狀態，team 文件儲存說明及歷史交接。

```json
{
  "request_id":"與預留相同的標識",
  "thread_id":"宿主實際聊天 ID",
  "host_id":"實際宿主與本機環境",
  "workspace":"與主會話完全一致的絕對根目錄",
  "source":"宿主建立和讀回結果的位置",
  "first_reply":"實際回覆原文",
  "context_paths":["AGENTS.md","Context/profile.md","Context/workflow.md"]
}
```

```bash
./Harness/bin/printlab onboarding record-role Mike --file role-receipt.json --expect 當前版本
```

Sarah 用同樣步驟完成。建立中斷時 `creating` 會阻止重複建立，先用儲存的 request ID 和工作區在宿主找回結果。確定已有聊天后繼續登記。缺少宿主工具時，工作台顯示具體待辦，提供角色提示詞和工作區路徑供使用者在支援環境繼續。

## 共同事實與第一件作品

宿主明確返回建立失敗且按建立標識搜尋確認沒有建立結果後，可用 `onboarding release-role 角色 --request-id 原標識 --evidence 宿主錯誤與搜尋證據 --expect 當前版本` 解除未綁定預留，再重新建立。已有 thread ID 的綁定不能通過此入口解除。結果仍未知時繼續查詢宿主。

Mac 的 `Harness/bin/printlab` 是可直接執行的 shell 啟動器，Windows 使用 PowerShell 啟動器。它們會選擇已安裝環境。Python 直接入口為 `Runtime/venv/bin/python -m printlab.cli`，Windows 對應 `Runtime/venv/Scripts/python.exe -m printlab.cli`。

偏好、經驗和團隊說明使用 `workspace show 名稱` 讀取哈希後，通過 `workspace note 名稱 --text 內容 --source 出處 --request-id 穩定更新標識 --expect-sha 當前哈希` 追加。名稱支援 `profile`、`taste`、`lessons`、`team`。文件尚無內容時用 `missing`。衝突後重讀合併，重試同一更新使用同一請求標識。

結合使用者用途、已有材料和設備給出少量簡單作品方向。選定作品後查已有專案或建立穩定 ID，填寫需求與已確認尺寸。生圖前儲存設備材料約束，進入 CAD 和切片前重讀變化。

```bash
./Harness/bin/printlab constraints show 專案ID
./Harness/bin/printlab constraints capture 專案ID --source '此次需求與設備材料核對記錄' --expect-sha missing
./Harness/bin/printlab context 專案ID
```

`manufacturing_context` 返回當前事實、已儲存快照、缺項及變化來源。材料包含未裝入 AMS 的庫存，裝載狀態另讀即時設備。離線時保留上次庫存並標明時間。每次更新快照保留歷史。用途、實測尺寸、保護介面寫 `brief.md`，選圖和同款三視圖沿用 `design-target.json`，可編輯幾何按 `CAD_SETUP.md` 接入 Text-to-CAD。

最終檢查應覆蓋真實模型與所選圖、尺寸/壁厚/裝配、材料適用性、當前列印板和裝料槽位。切片和自動發送的實際支援範圍查詢 `PRINTING.md` 與本機能力結果。具體列印繼續沿用統一批准與任務回執。

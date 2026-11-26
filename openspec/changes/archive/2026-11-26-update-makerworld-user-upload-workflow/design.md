# Design

## Context

PrintLab 的常駐角色包含 `sarah`、`mike`、`chloe` 與 `leo`，其角色定義集中在 `Harness/printlab/onboarding.py` 的 `ROLES` 字典，並對應到 `docs/ROLES.md`、`AGENTS.md`、`Templates/Project/Review/team.md`、`config/team.md.example` 與多語 README。

在 P002（貓咪聖誕不倒翁）實際上架經驗中，使用者確認由自己親自操作 MakerWorld 網頁上傳表單、貼上文案並送審發布更可靠可控，並明確要求：
1. 文案集中於 `MakerWorld/README.md`（依 MakerWorld 表單順序排列方便複製貼上），同時於 `MakerWorld/` 產出結構化 JSON 檔並由 Agent 回覆確切檔名。
2. `.3mf` 維持預設同時準備 PLA 與 PETG 兩份專案檔，缺實物照者依 MakerWorld 上傳要求標記待補。
3. 完全移除瀏覽器代操作上傳流程。
4. 刪除獨立的 `.agents/skills/makerworld-upload/` 技能，將其完整作業流程與核對標準直接內化為 Chloe 的常駐角色能力。

## Goals / Non-Goals

**Goals:**
- 徹底移除 `.agents/skills/makerworld-upload/` 技能目錄與所有跨檔引用，由 `docs/ROLES.md` 單一權威來源完整承載 Chloe 的 MakerWorld 素材包準備 SOP 與合規限制。
- 確保 `Harness/printlab/onboarding.py`、角色規範、專案範本與 README 全面對齊「使用者自行上傳、Chloe＋Leo 備齊素材包」流程，不殘留瀏覽器代操作或 Save Draft 預設流程。
- 完整保留並明文化既有使用者偏好與合規底線（單一 `MakerWorld/` 目錄與 `source.json`、預設只出 `.3mf`、Save Project 且禁 `.gcode.3mf`／裸 `.gcode`、官方或 Generic 預設、Gyroid 填充 round-trip 驗證、A1 mini → A1 → H2S 檢查、誠實展示紅線、原檔保留與排除特定原圖）。
- 將 Leo 與 Chloe 的圖片協作對齊至「3 張不同角度實拍去陰影不改主體（另存不覆蓋）」與「封面圖分開產出 4:3（網頁版）與 3:4（行動版）兩份獨立檔案」。
- 透過測試驗證 `onboarding.py` 產生的 Chloe 角色提示詞、`printlab new` 產生的 `Review/team.md`，以及 `.agents/skills/makerworld-upload` 已移除且規範內化於 `docs/ROLES.md`。

**Non-Goals:**
- 不修改 `Harness/printlab/publication.py` 的本地合規審查資料結構或 `printlab publish` CLI 子命令介面（該模組本即為本地預檢且從未執行上傳）。
- 不修改工作台前端 React 頁面元件（`Onboarding.jsx` 已從 `/api/onboarding` 動態呈現角色狀態與標題，`Chloe · 行銷與模型發布顧問` 與 `Leo · 平面設計師` 顯示標題不變）。
- 不重構現有專案（如 P002）的歷史檔案，只更新工作區共用偏好 `Context/profile.md` 與本倉庫規範／程式碼。

## Decisions

1. **刪除 `.agents/skills/makerworld-upload/` 並將完整 SOP 內化至 `docs/ROLES.md`**
   - 原本的 `makerworld-upload` 技能是為跨角色瀏覽器自動上傳所設；在移除瀏覽器代操作並確立由 Chloe 專責備齊素材包後，獨立技能只會造成 `docs/ROLES.md` 與 `SKILL.md` 雙份維護與漂移風險。
   - 將原技能中的目錄結構、PLA／PETG 雙 `.3mf` 準備與 Gyroid round-trip／A1 mini→A1→H2S 單盤檢查、圖片與 Leo 協作清單、`MakerWorld/README.md` 依表單順序排列之五大文案區塊、`MakerWorld/` 結構化 JSON 與交付核對表，完整併入 `docs/ROLES.md` 的 Chloe 章節，並移除 `AGENTS.md` 與 `docs/ROLES.md` 對該技能的引用。

2. **維持常駐角色代號與顯示標題不變，僅更新職責摘要與規範內容**
   - `chloe` 的顯示標題維持 `Chloe · 行銷與模型發布顧問`，確保既有 `Context/onboarding.json`、工作台卡片標題與瀏覽器驗收腳本 `scripts/verify_browser.py` 完全相容。
   - `Harness/printlab/onboarding.py` 的 `role_prompt` 本即引導角色讀取 `AGENTS.md` 與 `docs/ROLES.md`，更新 `ROLES['chloe'][1]` 後無須再引用任何外部技能路徑。

3. **文案與結構化 JSON 雙軌交付於單一 `MakerWorld/` 目錄**
   - 所有可複製貼上的文字素材依 MakerWorld 網頁表單順序集中在 `MakerWorld/README.md`。
   - 同步在 `MakerWorld/` 目錄維持 `MakerWorld/source.json`（記錄 `project_id`、`source_revision` 與變體說明）並產出結構化上傳素材 JSON（如 `MakerWorld/upload-pack.json`），交付時由 Chloe 回覆確切檔名與路徑。

4. **維持 PLA 與 PETG 雙份專案 `.3mf` 並嚴格標記缺照狀態**
   - 維持同時準備 PLA 與 PETG 兩份獨立 Bambu Studio 專案 `.3mf`（Save Project / Save Project As），皆須保留 Gyroid 填充並經重載 round-trip 驗證，並依 A1 mini → A1 → H2S 順序確認單盤容納與切片；若僅有 STL／CAD 或一般 3MF 先匯入 Bambu Studio 準備。
   - 缺實物照的材料依 MakerWorld 規範標記為「缺實物照待補」，絕不以渲染圖或 AI 圖冒充。

## Risks / Trade-offs

- **風險：既有角色聊天（已建立的 Chloe／Leo）仍帶有舊提示詞記憶，可能嘗試讀取已刪除的 `.agents/skills/makerworld-upload/SKILL.md`**
  - 緩解：透過 `AGENTS.md`、`docs/ROLES.md` 與共用 `Context/profile.md` 統一收斂規範；角色每次執行 `printlab context` 與重讀 `AGENTS.md`／`docs/ROLES.md` 即可取得最新內化後的完整能力與流程。

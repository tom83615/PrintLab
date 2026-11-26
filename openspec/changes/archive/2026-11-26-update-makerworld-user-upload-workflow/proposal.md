# Proposal

## Why

目前 PrintLab 的 MakerWorld 發布流程預設由 Chloe 透過瀏覽器控制登入 MakerWorld、操作上傳表單並儲存草稿，並額外維護一份獨立的 `.agents/skills/makerworld-upload/SKILL.md` 技能檔。依據使用者於 2026-11-26 的明確指示，流程須調整為「使用者自行在 MakerWorld 網頁上傳、送審與發布；Chloe（搭配 Leo）在專案 `MakerWorld/` 目錄備齊所有可直接上傳的檔案、圖片、可複製貼上文案、結構化 JSON 與合規核對清單」，並將獨立的 `makerworld-upload` 技能移除、完整內化為 Chloe 的角色常駐能力（集中於 `docs/ROLES.md`），同時保留既有 `.3mf`、實物照與誠實展示規範，且徹底移除瀏覽器代操作流程。

## What Changes

- **BREAKING**：完全移除獨立技能目錄 `.agents/skills/makerworld-upload/`（含 `SKILL.md`）以及其中的瀏覽器自動上傳、登入、填表與 Save Draft 操作步驟；將 MakerWorld 上傳素材包準備流程與合規核對標準完整內化為 Chloe 角色能力（集中於 `docs/ROLES.md`）。
- 更新 `Harness/printlab/onboarding.py` 中 `ROLES['chloe']` 的職責描述，使 CLI（`reserve-role`、`record-role`、`status`）與 `/api/onboarding` 生成之角色提示詞與新分工一致，引導 Chloe 直接依 `AGENTS.md` 與 `docs/ROLES.md` 執行。
- 更新 `docs/ROLES.md` 中 Chloe 與 Leo 的提示詞及必守規範：
  - Chloe 內化完整的 MakerWorld 上傳素材包標準作業流程與合規規則，於單一上傳目錄 `MakerWorld/`（不得建立版本子資料夾）備齊四類素材：
    1. `MakerWorld/3mf/`：預設僅以 `.3mf` 發布（不額外附加 `.stl`／`.step`），維持同時準備 PLA 與 PETG 兩份獨立 Bambu Studio 專案 `.3mf`（Save Project / Save Project As、≤ 200 MB、禁止 `.gcode.3mf` 與裸 `.gcode`、限 Bambu 官方或 Generic 預設、保留 Gyroid 填充並經 Bambu Studio 重載 round-trip 驗證、依 A1 mini → A1 → H2S 檢查單盤容納與切片；若僅有 STL／CAD 或一般 3MF 先匯入 Bambu Studio 準備；缺實物照的材料依 MakerWorld 要求標記待補）。
    2. `MakerWorld/photos/` 與 `MakerWorld/photo-edits/`：至少 3 張不同角度真實成品照並協作 Leo 移除拍照陰影且嚴格不影響主要拍攝物（另存不覆蓋原檔）；每份 Print Profile 至少 1 張對應實物照；封面圖分開產出 **4:3（網頁版）** 與 **3:4（行動版／Bambu Handy）** 兩份獨立檔案；支援排除特定原圖僅留本機。
    3. `MakerWorld/README.md`：依 MakerWorld 表單順序集中整理可直接複製貼上的文字素材（標題、分類、含列印前準備／參數取捨／組裝與排查指導且善用 Emoji 的描述、約 8–10 個中英文 Tags、Boost Me 理由文案與各份 Print Profile 標題／說明，定位為吸引人列印而非商品推銷）。
    4. `MakerWorld/` 結構化 JSON 檔（含 `MakerWorld/source.json` 記錄 `project_id`、`source_revision` 與變體說明，以及對應上傳欄位與檔案清單之結構化 JSON 如 `MakerWorld/upload-pack.json`，交付時明確回覆檔名與路徑），並附原創／改作／AIGC／Exclusive／授權條款與缺口核對表。
  - 同步更新 Leo 規範：封面圖改為分別產出 4:3 與 3:4 兩份獨立檔案（不再要求單圖同時兼顧兩種比例），並納入 3 張不同角度實拍圖去陰影且嚴格不影響主要拍攝物、另存不覆蓋原檔的預設協作規範。
- 同步更新 `AGENTS.md`（移除 `.agents/skills/makerworld-upload/SKILL.md` 引用，統一指向 `docs/ROLES.md`）、`Templates/Project/Review/team.md`、`config/team.md.example`、`README.md`、`README.zh-TW.md`、`README.en.md` 與單元測試（`Harness/tests/test_onboarding.py`、`Harness/tests/test_onboarding_cli.py`）。
- 透過 `printlab workspace note profile` 將新的 MakerWorld 使用者自行上傳分工與交付偏好寫入外部資料空間 `Context/profile.md`。

## Capabilities

### New Capabilities

### Modified Capabilities

- `team-roles`: 更新常駐角色 `chloe` 的職責描述、提示詞與內化後的 MakerWorld 素材包準備流程與合規核對規範（刪除獨立 `makerworld-upload` 技能、移除瀏覽器代操作與 Save Draft，明確規定 `MakerWorld/README.md` 表單順序文案、結構化 JSON、PLA／PETG 雙專案 `.3mf` 與缺實物照待補標記），並同步更新 `leo` 的 4:3／3:4 獨立封面與實拍去陰影不改主體規範及專案分工範本。

## Impact

- 後端與 CLI：`Harness/printlab/onboarding.py`
- 技能移除：刪除 `.agents/skills/makerworld-upload/`（含 `SKILL.md`）
- 角色規範與入口：`docs/ROLES.md`、`AGENTS.md`
- 專案範本與說明文件：`Templates/Project/Review/team.md`、`config/team.md.example`、`README.md`、`README.zh-TW.md`、`README.en.md`
- 測試：`Harness/tests/test_onboarding.py`、`Harness/tests/test_onboarding_cli.py`
- 外部共用偏好：`Context/profile.md`（透過 `printlab workspace note profile` 追加記錄）

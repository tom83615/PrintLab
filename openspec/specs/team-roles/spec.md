# team-roles Specification

## Purpose

定義 PrintLab 常駐團隊角色在命令列（CLI）、API、工作台「設定與團隊」頁面與範本文件中的一致行為，涵蓋既有的 Sarah、Mike 與新增的行銷及模型發布角色 Chloe。

## Requirements

### Requirement: 支援行銷與模型發布常駐角色 Chloe

PrintLab 的 onboarding 模組、CLI（`reserve-role`、`record-role`、`release-role`、`status`）與 `/api/onboarding` SHALL 支援常駐角色 `chloe`（顯示標題 `Chloe · 行銷與模型發布顧問`），負責備齊 MakerWorld 等模型網站上傳素材包、可複製貼上文案與標籤、展示與封面圖規劃、合規專案 `.3mf` 與核對清單以供使用者自行上傳，並在角色開場提示詞引導讀取 `AGENTS.md` 與 `docs/ROLES.md`。角色名稱比對 SHALL 不區分大小寫，且保留既有的 `sarah`（含歷史別名 `sara`）與 `mike`。

#### Scenario: 透過 CLI 預留並登記 Chloe 角色

- **WHEN** 宿主能力已記錄且呼叫端執行 `printlab onboarding reserve-role Chloe` 與 `record-role Chloe`
- **THEN** 系統產生綁定當前共享工作空間、引導讀取 `docs/ROLES.md` 且明確指出備齊上傳素材包供使用者自行上傳之提示詞、依版本檢查寫入 `Context/onboarding.json`，並在讀取首次介紹與共同文件路徑後將狀態標記為 `introduced`

#### Scenario: 既有工作區載入新增角色

- **WHEN** 既有工作區的 `Context/onboarding.json` 已完成 `mike` 與 `sarah` 的 `introduced` 記錄但尚未建立 `chloe`
- **THEN** `onboarding.view()` 與 `/api/onboarding` 保留既有 `mike` 與 `sarah` 記錄、將 `chloe` 顯示為 `pending`、在 `next_actions` 列出建立 `Chloe · 行銷與模型發布顧問` 的待辦，並將 `team_ready` 回報為 `false` 直到所有常駐角色皆達 `introduced`

#### Scenario: 拒絕未定義的角色名稱

- **WHEN** 呼叫端傳入不在常駐角色清單內的角色名稱給 `reserve-role`、`record-role` 或 `release-role`
- **THEN** 系統拒絕操作並回傳明確列出支援角色（Mike、Sarah、Chloe、Leo）的錯誤訊息

### Requirement: 工作台與範本同步呈現 Chloe 角色

PrintLab 工作台「設定與團隊」頁面 SHALL 呈現包含 `Chloe · 行銷與模型發布顧問` 在內的所有常駐角色卡片，其複製設定提示詞 SHALL 動態列出所有常駐角色名稱，且在桌面與行動裝置視窗寬度下不得產生水平溢位。專案分工範本與角色文件（`docs/ROLES.md`）SHALL 將 MakerWorld 素材包準備與合規核對能力完整內化為 Chloe 職責（不設獨立 `makerworld-upload` 技能），規範由使用者自行上傳，並完全移除瀏覽器代操作與 Save Draft 流程。

#### Scenario: 在工作台檢視設定與團隊頁面

- **WHEN** 使用者開啟工作台 `/#/onboarding` 頁面
- **THEN** 頁面顯示 `Sarah · 3D 列印顧問`、`Mike · 工作流設計師`、`Chloe · 行銷與模型發布顧問` 與 `Leo · 平面設計師` 四張角色卡片，點擊「讓 Agent 接著設定」所複製的提示詞包含所有常駐角色名稱

#### Scenario: 建立新專案帶入 Chloe 分工

- **WHEN** 使用者執行 `printlab new` 建立新專案
- **THEN** 新專案產生的 `Review/team.md` 包含 Chloe 負責備齊 `MakerWorld/` 上傳素材包、可複製文案、結構化 JSON 與合規核對清單以供使用者自行上傳的分工項目

#### Scenario: 依 Chloe 內化規範備齊 MakerWorld 素材包

- **WHEN** 使用者要求 Chloe 準備作品上架至 MakerWorld
- **THEN** Chloe 依 `docs/ROLES.md` 內化流程於單一目錄 `MakerWorld/` 備齊 PLA／PETG 雙份合規專案 `.3mf`（缺實物照標記待補）、3 張不同角度去陰影實拍與 4:3／3:4 雙封面、依表單順序整理於 `MakerWorld/README.md` 的文案（含列印／組裝教學、Emoji、Tags 與 Boost Me）及 `MakerWorld/` 結構化 JSON，交付使用者自行上傳而不操作瀏覽器

### Requirement: 支援平面設計師常駐角色 Leo

PrintLab 的 onboarding 模組、CLI（`reserve-role`、`record-role`、`release-role`、`status`）與 `/api/onboarding` SHALL 支援常駐角色 `leo`（顯示標題 `Leo · 平面設計師`），負責協助修圖、裁切構圖、調整光線色彩與版面設計，製作作品展示圖與視覺素材，並在角色開場提示詞引導讀取 `AGENTS.md` 與 `docs/ROLES.md`。角色名稱比對 SHALL 不區分大小寫。

#### Scenario: 透過 CLI 預留並登記 Leo 角色

- **WHEN** 宿主能力已記錄且呼叫端執行 `printlab onboarding reserve-role Leo` 與 `record-role Leo`
- **THEN** 系統產生綁定當前共享工作空間與平面設計職責的提示詞、依版本檢查寫入 `Context/onboarding.json`，並在讀取首次介紹與共同文件路徑後將狀態標記為 `introduced`

#### Scenario: 既有三角色工作區載入新增角色 Leo

- **WHEN** 既有工作區的 `Context/onboarding.json` 已完成 `mike`、`sarah` 與 `chloe` 的 `introduced` 記錄但尚未建立 `leo`
- **THEN** `onboarding.view()` 與 `/api/onboarding` 保留既有角色記錄、將 `leo` 顯示為 `pending`、在 `next_actions` 列出建立 `Leo · 平面設計師` 的待辦，並將 `team_ready` 回報為 `false` 直到四位常駐角色皆達 `introduced`

### Requirement: 工作台與範本同步呈現平面設計師 Leo

PrintLab 工作台「設定與團隊」頁面 SHALL 呈現包含 `Leo · 平面設計師` 在內的四張常駐角色卡片，其複製設定提示詞 SHALL 動態列出所有常駐角色名稱，且在桌面與行動裝置視窗寬度下不得產生水平溢位。專案分工範本與角色文件 SHALL 包含 Leo 的職責、提示詞、保留原始實物照原檔與不得將編修／合成展示圖冒充未編修實物列印照之邊界規範，並明確規範為 MakerWorld 封面分別產出 4:3（網頁版）與 3:4（行動版）兩份獨立檔案，以及對 3 張不同角度實拍圖移除拍照陰影時嚴格不得影響主要拍攝物且另存輸出不覆蓋原檔。

#### Scenario: 在工作台檢視包含四位角色之設定與團隊頁面

- **WHEN** 使用者開啟工作台 `/#/onboarding` 頁面
- **THEN** 頁面顯示 `Sarah · 3D 列印顧問`、`Mike · 工作流設計師`、`Chloe · 行銷與模型發布顧問` 與 `Leo · 平面設計師` 四張角色卡片，點擊「讓 Agent 接著設定」所複製的提示詞包含所有常駐角色名稱

#### Scenario: 建立新專案帶入 Leo 平面設計分工

- **WHEN** 使用者執行 `printlab new` 建立新專案
- **THEN** 新專案產生的 `Review/team.md` 包含 `Leo` 負責實拍去陰影（另存不改主體）、4:3／3:4 獨立封面與展示視覺素材製作的分工項目

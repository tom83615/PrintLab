# Design

## Context

PrintLab 透過 `Harness/printlab/onboarding.py` 中的 `ROLES` 字典控管常駐角色白名單，並透過 `Context/onboarding.json` 保存角色預留、宿主聊天回執與首次介紹證據。前端 `Harness/studio/src/Onboarding.jsx` 透過 `/api/onboarding` 取得 `data.roles` 渲染卡片，但複製給 Agent 的設定提示詞原本寫死 `Mike 和 Sarah 兩個獨立聊天`，且 `.onboarding-roles` 樣式為固定兩欄。

## Goals / Non-Goals

**Goals:**

- 將 `chloe`（`Chloe · 行銷與模型發布顧問`）正式納入 `onboarding.py` 的常駐角色清單，完整支援 CLI 與 API 流程。
- 保留既有工作區 `Context/onboarding.json` 的相容性：已登記 `mike`、`sarah` 的工作區無需遷移，載入後即自動將 `chloe` 顯示為 `pending`（待建立）並列入 `next_actions`。
- 讓前端「設定與團隊」頁面的複製提示詞動態帶出所有常駐角色，且在桌面與手機寬度下皆能正常排版不溢位。
- 在角色提示詞、規則文件與新專案 `Review/team.md` 範本清楚界定 Chloe 的職責與發布安全邊界（先核對授權與來源、預設存草稿、未經使用者明確授權不公開發布）。

**Non-Goals:**

- 不變更 `Context/onboarding.json` 的 `schema_version`（維持 `1`）。
- 本變更不實作動態自訂任意角色的 UI 表單或資料結構重構。
- 不自動在宿主建立真實聊天或寫入偽造的 `thread_id`。

## Decisions

1. **角色代號與中文標題**
   - 採用 `chloe`（大小寫不敏感，支援 `Chloe` / `chloe`），標題為 `Chloe · 行銷與模型發布顧問`，職責摘要為 `模型網站上架、生成描述文案、規劃展示圖片與適合分享的檔案形式`。
   - 理由：與 `Sarah`、`Mike` 命名風格一致、簡短易輸入且無命名衝突。

2. **前端提示詞改由 `data.roles` 動態組裝**
   - 在 `Onboarding.jsx` 由 `data.roles` 萃取角色名稱（取 `title` 中 ` · ` 前的名稱）串接至提示詞，並將 `.onboarding-roles` 改為 `repeat(auto-fit, minmax(280px, 1fr))`（在 `<= 700px` 維持單欄 `1fr`）。
   - 理由：避免未來新增角色時提示詞再次脫鉤，且三個角色卡片在 1160px 容器中能平均排成三欄，在窄螢幕自動折行不產生水平捲軸。

3. **團隊就緒條件（`team_ready`）維持全員 `introduced`**
   - `onboarding.view()` 既有規則為 `all(role['status'] == 'introduced' for role in roles)`，維持不變，確保所有常駐角色（包含 Chloe）皆完成建立與首次介紹後才回報 `team_ready: true`。

## Risks / Trade-offs

- **既有測試假設兩角色即就緒**：`Harness/tests/test_onboarding.py` 中 `test_two_roles_normalize_workspace_paths_and_reach_ready` 原本只建立 Mike 與 Sarah 即斷言 `team_ready is True`；需更新為涵蓋三個常駐角色並驗證少一人時 `team_ready` 為 `False`。
- **既有外部工作區狀態顯示**：使用者既有工作區在升級後，「設定與團隊」頁會將 Chloe 顯示為「待建立」並提示建立她的新聊天，這正是預期行為，不影響既有 Mike 與 Sarah 的回執。

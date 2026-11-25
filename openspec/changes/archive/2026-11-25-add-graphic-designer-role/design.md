# Design

## Context

PrintLab 透過 `Harness/printlab/onboarding.py` 中的 `ROLES` 字典管理常駐角色白名單與提示詞生成，並透過 `Context/onboarding.json` 保存角色狀態。前端 `Harness/studio/src/Onboarding.jsx` 已從 `/api/onboarding` 的 `data.roles` 動態渲染卡片與複製設定提示詞，而 `Harness/studio/src/onboarding.css` 目前設定 `.onboarding-roles` 為 `repeat(auto-fit, minmax(280px, 1fr))`（在 `1160px` 容器內最多容納 3 欄）。

## Goals / Non-Goals

**Goals:**

- 將 `leo`（`Leo · 平面設計師`）加入 `onboarding.py` 的 `ROLES`，使 CLI、API、工作台「設定與團隊」頁與新專案範本完整支援四位常駐角色。
- 確保現有工作區（已完成 `mike`、`sarah`、`chloe` 的 `Context/onboarding.json`）無需資料遷移即可相容，並將 `leo` 顯示為 `pending` 待辦。
- 調整工作台 `.onboarding-roles` 網格最小欄寬，使四張角色卡片在桌面寬度下能平衡排列而不產生 3+1 孤立尾張或水平溢位。
- 在 `docs/ROLES.md` 明確定義 Leo 與 Chloe 的分工邊界與「不得覆蓋原始實物照、不得以編修／合成圖冒充未編修實物列印照」之規則。

**Non-Goals:**

- 不變更 `Context/onboarding.json` 的 `schema_version`（維持 `1`）。
- 不在本變更中自動在宿主（T3 Code / Codex）建立真實的 Leo 聊天會話或寫入偽造 `thread_id`。
- 不修改圖像編修工具或新增圖片處理後端 API。

## Decisions

1. **角色命名與代號：`Leo · 平面設計師`（代號 `leo`）**
   - 採用 `leo`（大小寫不敏感），與 `Sarah`、`Mike`、`Chloe` 風格一致、簡短易記且與現有角色及檔案名稱無衝突。
   - 職責摘要：`協助修圖、裁切構圖、調整光線色彩與版面設計，製作作品展示圖與視覺素材`。

2. **職責邊界：與 Chloe 互補且嚴守誠實展示原則**
   - Leo 專注於圖片與視覺素材層（修圖、調色、去背、4:3／3:4 封面構圖、尺寸標示與說明圖卡排版）；Chloe 專注於模型平台上架層（文案、標籤、分類、`.3mf` 規格與合規／草稿發布）。
   - 嚴格要求保留原始拍攝圖檔與原始渲染圖檔不覆蓋，編修後另存展示素材，且不得將大幅編修、合成或渲染圖片冒充 MakerWorld 要求的未編修實物列印照。

3. **工作台四卡網格微調**
   - 將 `Harness/studio/src/onboarding.css` 的 `.onboarding-roles` `minmax(280px, 1fr)` 調整為 `minmax(240px, 1fr)`（`<= 700px` 維持 `1fr`），在 `1160px` 桌面寬度下可同時容納四欄並於平板自動折行成 `2x2`，避免 3+1 不對稱排版。

## Risks / Trade-offs

- **既有測試斷言三角色即就緒**：`Harness/tests/test_onboarding.py` 的 `test_all_roles_normalize_workspace_paths_and_reach_ready` 原本建立 Mike、Sarah、Chloe 三人後即斷言 `team_ready is True`；須更新為在未建立 Leo 前驗證 `team_ready is False` 與 `leo` 為 `pending`，加入 Leo 後才為 `True`。
- **正式版容器鏡像同步**：本變更修改程式碼與前端資源後，已運行中的 Docker 正式版容器仍需透過正式發布流程更新鏡像才會呈現四張角色卡片；本輪先完成開發、建置與測試驗證。

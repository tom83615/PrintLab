# Design

## Context

PrintLab 透過 `Harness/printlab/onboarding.py` 中的 `ROLES` 字典管理常駐角色白名單與角色開場提示詞，並以 `Context/onboarding.json` 保存各角色的預留與介紹狀態。前端 `Harness/studio/src/Onboarding.jsx` 已透過 `/api/onboarding` 回傳的 `data.roles` 動態產生角色卡片與「讓 Agent 接著設定」提示詞；`Harness/studio/src/onboarding.css` 目前在 `1160px` 容器下以 `repeat(auto-fit, minmax(240px, 1fr))` 呈現四張卡片（4 欄）。

## Goals / Non-Goals

**Goals:**

- 將 `nora`（`Nora · 產品經理`）納入 `onboarding.py` 的 `ROLES`，使 CLI、API、工作台「設定與團隊」頁與新專案分工範本完整支援五位常駐角色。
- 在角色提示詞、`docs/ROLES.md`、`AGENTS.md` 與 `Templates/Project/Review/team.md` 明確寫入 Nora 的核心紅線：只負責接收指令、規劃拆解與統籌指派；嚴格不可涉入實際執行；缺乏合適人選時不得自行完成，必須向使用者徵求新增角色。
- 確保既有四角色工作區（已完成 `mike`、`sarah`、`chloe`、`leo` 的 `Context/onboarding.json`）無需資料遷移即可相容，並將 `nora` 顯示為 `pending` 待辦。
- 調整工作台 `.onboarding-roles` 欄寬，使五張角色卡片在桌面寬度呈現平衡的 3+2 網格而不產生 4+1 孤立尾張或水平溢位。

**Non-Goals:**

- 不變更 `Context/onboarding.json` 的 `schema_version`（維持 `1`）。
- 不在本變更中自動在宿主（T3 Code / Codex）建立真實的 Nora 聊天會話或寫入偽造 `thread_id`（依規範由使用者明確要求時再建立會話）。
- 不新增新的後端 API 端點或任務排程引擎。

## Decisions

1. **角色命名與代號：`Nora · 產品經理`（代號 `nora`）**
   - 採用 `nora`（大小寫不敏感），首字母 `N` 與既有角色 `Sarah`、`Mike`、`Chloe`、`Leo` 皆不重複，簡短易讀且符合使用者對女性產品經理（「她」）的稱呼。
   - 職責摘要：`接收使用者指令，負責需求規劃、工作拆解與任務統籌指派給合適的團隊角色；嚴格不可涉入實際執行，缺乏合適人選時亦不得自行完成，須向使用者徵求新增更多角色`。

2. **職責邊界：純規劃與統籌紅線（零實際執行＋缺人必徵求）**
   - Nora 負責接住使用者的目標與指令，釐清需求與驗收標準、拆解任務與先後順序、維護 `Review/team.md` 分工表與跨角色交接，並將明確的任務包指派給對應專責角色（Sarah、Mike、Chloe、Leo 或專案任務小組）。
   - **禁止涉入實際執行**：Nora 不得親自進行 CAD／Blender 建模、切片、修圖／平面設計、撰寫 MakerWorld 上架素材包或修改程式碼、工具設定與列印操作。
   - **缺乏合適人選的處理規則**：當盤點現有常駐角色與任務小組後，發現某項任務沒有合適人選時，Nora 不得自行完成，也不得硬將工作塞給職責不符的角色代做；必須列出缺少的能力、建議新增的角色名稱／職責與邊界，向使用者徵求新增角色，待使用者決定後再推進指派。

3. **工作台五卡網格調整（3+2 平衡排版）**
   - `.onboarding-page` 最大寬度為 `1160px`。若維持 `minmax(240px, 1fr)`，5 張卡片會排成 4+1（最後一張孤立）。將 `.onboarding-roles` 改為 `repeat(auto-fit, minmax(280px, 1fr))`（`<= 700px` 維持 `1fr`），在 `1160px` 桌面寬度下每列最多容納 3 欄（`3*280 + 2*20 = 880px <= 1160px`，`4*280 + 3*20 = 1180px > 1160px`），自然呈現 3+2 兩列平衡排列；平板寬度自動折為 2 欄，手機寬度為 1 欄且無水平溢位。

## Risks / Trade-offs

- **既有測試斷言四角色即就緒**：`Harness/tests/test_onboarding.py` 的 `test_all_roles_normalize_workspace_paths_and_reach_ready` 原本建立 Mike、Sarah、Chloe、Leo 四人後即斷言 `team_ready is True`；須更新為在未建立 Nora 前驗證 `team_ready is False` 與 `nora` 為 `pending`，加入 Nora 後才為 `True`。
- **正式版容器鏡像同步**：修改程式碼與前端資源後，已運行中的 Docker 正式版容器仍需於需要時依正式發布流程重建鏡像才會呈現五張角色卡片；本輪先完成開發、前端建置與完整測試驗證。

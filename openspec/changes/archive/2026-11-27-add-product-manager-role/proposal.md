# Proposal

## Why

目前 PrintLab 常駐團隊已有負責設備材料的 `Sarah`、工具與流程的 `Mike`、模型上架與行銷素材包的 `Chloe`，以及負責修圖與展示視覺素材的 `Leo`，但缺少專職負責「接收使用者指令、規劃拆解工作並將任務統籌指派給合適團隊成員」的產品經理角色。使用者希望新增一位純粹專注於規劃與統籌的產品經理，明確劃清「統籌規劃」與「實際執行」的界線——她絕不可涉入實際執行，當現有團隊缺乏合適人選時也不得自行代做，而必須向使用者徵求新增更多角色。

## What Changes

- 新增常駐團隊角色 **Nora · 產品經理**（代號 `nora`），專責接收使用者指令、釐清目標與驗收條件、進行規劃與任務拆解、協調跨角色交接與進度追蹤，並將具體工作指派給合適的團隊角色；嚴格禁止涉入任何實際執行工作，若缺乏合適人選亦不得自行完成，必須說明缺口並向使用者徵求新增更多角色。
- 在後端與 CLI（`Harness/printlab/onboarding.py`）將 `nora` 納入 `ROLES` 常駐角色清單，支援 `printlab onboarding reserve-role / record-role / release-role Nora`、角色開場提示詞生成、`/api/onboarding` 回報、`team_ready` 五角色判定與未知角色錯誤訊息更新。
- 調整工作台前端樣式（`Harness/studio/src/onboarding.css`）讓 5 張常駐角色卡片在桌面寬度呈現平衡的 3+2 網格排版（避免 4+1 孤立尾張），並於 `Harness/studio` 重新建置靜態資產（`Onboarding.jsx` 已透過 `data.roles` 動態呈現所有角色卡片與複製提示詞）。
- 更新角色提示詞、工作區規範與專案分工範本（`docs/ROLES.md`、`docs/ONBOARDING.md`、`AGENTS.md`、`.agents/skills/printlab/SKILL.md`、`config/team.md.example`、`Templates/Project/Review/team.md`、`README.md`、`README.zh-TW.md`、`README.en.md`）。
- 擴充單元測試與瀏覽器驗收腳本（`Harness/tests/test_onboarding.py`、`Harness/tests/test_onboarding_cli.py`、`scripts/verify_browser.py`），涵蓋五角色就緒檢查、既有四角色工作區載入 `nora` 為 `pending`、提示詞邊界關鍵語句與範本驗證。

## Capabilities

### New Capabilities

### Modified Capabilities

- `team-roles`: 新增常駐角色 `nora`（`Nora · 產品經理`），定義「只做規劃與統籌、嚴格不可涉入實際執行、缺乏合適人選時向使用者徵求新增角色而非自行完成」的角色規範，並更新支援角色清單、錯誤訊息、舊工作區載入 `pending` 待辦、`team_ready` 五角色判定、工作台呈現與專案分工範本。

## Impact

- 後端與 CLI：`Harness/printlab/onboarding.py`
- 前端工作台樣式與建置：`Harness/studio/src/onboarding.css`、`Harness/studio/dist`（建置驗證）
- 文件與範本：`docs/ROLES.md`、`docs/ONBOARDING.md`、`AGENTS.md`、`.agents/skills/printlab/SKILL.md`、`config/team.md.example`、`Templates/Project/Review/team.md`、`README.md`、`README.zh-TW.md`、`README.en.md`
- 測試與驗收：`Harness/tests/test_onboarding.py`、`Harness/tests/test_onboarding_cli.py`、`scripts/verify_browser.py`

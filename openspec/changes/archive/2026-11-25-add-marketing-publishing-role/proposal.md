# Proposal

## Why

目前 PrintLab 的常駐團隊角色僅包含負責設備、材料與配件的 `Sarah` 及負責工具、工作台與流程的 `Mike`，缺少專職處理模型網站上架、行銷描述、展示圖片規劃與分享檔案格式準備的常駐角色。每次將作品分享或上架到 MakerWorld 等模型網站時，無法在 PrintLab CLI 與工作台「設定與團隊」頁統一管理該角色的分工、預留與介紹狀態。

## What Changes

- 新增常駐團隊角色 **Chloe · 行銷與模型發布顧問**（代號 `chloe`），以 **MakerWorld** 為主要發布平台，負責於模型需要上傳至模型網站時，生成說明描述文案、規劃與生成展示圖片，以及評估並準備適合分享的檔案形式（依循 MakerWorld 實物照、`.3mf` 大小與設定、AIGC／獨家資格及來源授權規範，預設維持草稿、未經使用者明確授權不公開發布）。
- 在後端與 CLI（`Harness/printlab/onboarding.py`）將 `chloe` 納入 `ROLES` 角色白名單，支援 `printlab onboarding reserve-role / record-role / release-role Chloe`、角色開場提示詞生成、`/api/onboarding` 回報與 `team_ready` 判定。
- 更新工作台「設定與團隊」頁面（`Harness/studio/src/Onboarding.jsx`、`Harness/studio/src/onboarding.css`），使「讓 Agent 接著設定」複製提示詞動態納入所有常駐角色，並以響應式欄位排版容納三個以上角色卡片。
- 更新角色提示詞、工作區規範與專案分工範本（`docs/ROLES.md`、`docs/ONBOARDING.md`、`AGENTS.md`、`.agents/skills/printlab/SKILL.md`、`config/team.md.example`、`Templates/Project/Review/team.md`、`README*.md`）。
- 補齊單元測試與瀏覽器驗收腳本（`Harness/tests/test_onboarding.py`、`Harness/tests/test_onboarding_cli.py`、`scripts/verify_browser.py`）。

## Capabilities

### New Capabilities

- `team-roles`：定義 PrintLab 常駐團隊角色（Sarah、Mike、Chloe）在 CLI、API 與工作台「設定與團隊」頁面的註冊、狀態檢視與分工範本行為。

### Modified Capabilities

## Impact

- 後端與 CLI：`Harness/printlab/onboarding.py`
- 前端工作台：`Harness/studio/src/Onboarding.jsx`、`Harness/studio/src/onboarding.css`
- 文件與範本：`docs/ROLES.md`、`docs/ONBOARDING.md`、`AGENTS.md`、`.agents/skills/printlab/SKILL.md`、`config/team.md.example`、`Templates/Project/Review/team.md`、`README.md`、`README.zh-TW.md`、`README.en.md`
- 測試與驗收：`Harness/tests/test_onboarding.py`、`Harness/tests/test_onboarding_cli.py`、`scripts/verify_browser.py`

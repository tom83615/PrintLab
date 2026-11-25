# Proposal

## Why

目前 PrintLab 常駐團隊已有負責設備材料的 `Sarah`、工具與流程的 `Mike`，以及負責模型網站上架、文案與檔案規格的 `Chloe`，但缺少專職負責「修圖、裁切構圖、調色與調整視覺素材以供展示」的平面設計師角色。使用者需要在不混淆原始實物列印照片與編修展示素材的前提下，在 PrintLab CLI、工作台「設定與團隊」頁面與專案分工模板中統一管理這個常駐角色。

## What Changes

- 新增常駐團隊角色 **Leo · 平面設計師**（代號 `leo`），專責協助修圖、裁切與多比例構圖、光線色彩校正、去背與排版合成展示圖卡，以及調整視覺素材供作品展示、文件說明或模型網站上架使用（並嚴守「不覆蓋原始實物照原檔、不得將大幅編修或合成圖冒充未編修實物列印照」之誠實展示原則）。
- 在後端與 CLI（`Harness/printlab/onboarding.py`）將 `leo` 納入 `ROLES` 常駐角色清單，支援 `printlab onboarding reserve-role / record-role / release-role Leo`、角色開場提示詞生成、`/api/onboarding` 回報與 `team_ready` 判定。
- 調整工作台前端樣式（`Harness/studio/src/onboarding.css`）讓 4 張常駐角色卡片在桌面寬度呈現平衡網格排版，並於 `Harness/studio` 重新建置靜態資產（`Onboarding.jsx` 已透過 `data.roles` 動態產生角色卡片與複製提示詞）。
- 更新角色提示詞、工作區規範與專案分工範本（`docs/ROLES.md`、`docs/ONBOARDING.md`、`AGENTS.md`、`.agents/skills/printlab/SKILL.md`、`config/team.md.example`、`Templates/Project/Review/team.md`、`README.md`、`README.zh-TW.md`、`README.en.md`）。
- 擴充單元測試與瀏覽器驗收腳本（`Harness/tests/test_onboarding.py`、`Harness/tests/test_onboarding_cli.py`、`scripts/verify_browser.py`），涵蓋四角色就緒檢查、舊工作區載入 `leo` 為 `pending` 與範本驗證。

## Capabilities

### New Capabilities

### Modified Capabilities

- `team-roles`: 新增常駐角色 `leo`（`Leo · 平面設計師`），更新支援角色清單、錯誤訊息、舊工作區載入 `pending` 待辦、`team_ready` 四角色判定、工作台呈現與專案分工範本。

## Impact

- 後端與 CLI：`Harness/printlab/onboarding.py`
- 前端工作台樣式與建置：`Harness/studio/src/onboarding.css`、`Harness/studio/dist`（建置驗證）
- 文件與範本：`docs/ROLES.md`、`docs/ONBOARDING.md`、`AGENTS.md`、`.agents/skills/printlab/SKILL.md`、`config/team.md.example`、`Templates/Project/Review/team.md`、`README.md`、`README.zh-TW.md`、`README.en.md`
- 測試與驗收：`Harness/tests/test_onboarding.py`、`Harness/tests/test_onboarding_cli.py`、`scripts/verify_browser.py`

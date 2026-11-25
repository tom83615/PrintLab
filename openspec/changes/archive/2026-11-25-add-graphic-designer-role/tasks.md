# Tasks

## 1. 後端與 CLI 角色支援

- [x] 1.1 在 `Harness/printlab/onboarding.py` 的 `ROLES` 新增 `leo`（`Leo · 平面設計師`）與職責摘要，並更新 `_role()` 錯誤訊息包含 `Leo`
- [x] 1.2 更新 `Harness/tests/test_onboarding.py` 涵蓋 `Leo` 預留／登記、既有三角色工作區將 `leo` 顯示為 `pending`、四角色皆 `introduced` 才達 `team_ready` 與未知角色錯誤訊息驗證，並執行 `pytest Harness/tests/test_onboarding.py -q`

## 2. 工作台前端樣式與建置

- [x] 2.1 更新 `Harness/studio/src/onboarding.css` 的 `.onboarding-roles` 欄寬為 `minmax(240px, 1fr)`，使四張角色卡片在桌面與窄螢幕皆能平衡排版且無水平溢位
- [x] 2.2 於 `Harness/studio` 執行 `npm run build` 驗證前端建置通過

## 3. 角色文件、規範與專案範本同步

- [x] 3.1 更新 `docs/ROLES.md` 新增 `Leo · 平面設計師` 提示詞、修圖／素材調整職責及誠實展示與原檔保留規範，並更新 `docs/ONBOARDING.md` 常駐角色建隊說明
- [x] 3.2 更新 `AGENTS.md`、`.agents/skills/printlab/SKILL.md`、`config/team.md.example`、`Templates/Project/Review/team.md` 與 `README.md` / `README.zh-TW.md` / `README.en.md`
- [x] 3.3 更新 `Harness/tests/test_onboarding_cli.py` 驗證新專案 `Review/team.md` 帶入 `Leo` 分工項目，並執行 `pytest Harness/tests/test_onboarding_cli.py -q`

## 4. 整合測試與驗收檢查

- [x] 4.1 更新 `scripts/verify_browser.py` 驗證 `Leo · 平面設計師` 卡片標題
- [x] 4.2 執行完整測試套件（`pytest Harness/tests -q`、`scripts/verify_onboarding.py`）與 `openspec validate add-graphic-designer-role --strict` 確認全部通過

## Workflow follow-up

- 完成所有任務與驗證後，將 `add-graphic-designer-role` change 同步規格並 archive 至 `openspec/changes/archive/`。

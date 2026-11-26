# Tasks

## 1. 後端與 CLI 角色支援

- [x] 1.1 在 `Harness/printlab/onboarding.py` 的 `ROLES` 新增 `nora`（`Nora · 產品經理`）與規劃統籌／不可涉入實際執行／缺人徵求角色之職責摘要，並更新 `_role()` 錯誤訊息包含 `Nora`
- [x] 1.2 更新 `Harness/tests/test_onboarding.py` 涵蓋 `Nora` 預留／登記、提示詞邊界語句驗證、既有四角色工作區將 `nora` 顯示為 `pending`、五角色皆 `introduced` 才達 `team_ready` 與未知角色錯誤訊息驗證

## 2. 工作台前端樣式與建置

- [x] 2.1 更新 `Harness/studio/src/onboarding.css` 的 `.onboarding-roles` 欄寬為 `minmax(280px, 1fr)`，使五張角色卡片在桌面呈現 3+2 平衡排版且於窄螢幕無水平溢位
- [x] 2.2 於 `Harness/studio` 執行 `npm run build` 驗證前端建置通過

## 3. 角色文件、規範與專案範本同步

- [x] 3.1 更新 `docs/ROLES.md` 新增 `Nora · 產品經理` 提示詞與必守紅線（只做規劃與統籌、不可涉入實際執行、缺乏合適人選時向使用者徵求新增角色而非自行完成），並更新 `docs/ONBOARDING.md` 常駐角色建隊說明
- [x] 3.2 更新 `AGENTS.md`、`.agents/skills/printlab/SKILL.md`、`config/team.md.example`、`Templates/Project/Review/team.md` 與 `README.md` / `README.zh-TW.md` / `README.en.md`
- [x] 3.3 更新 `Harness/tests/test_onboarding_cli.py` 驗證新專案 `Review/team.md` 與 `docs/ROLES.md` 納入 `Nora` 分工與不可涉入實際執行之規範

## 4. 整合測試與驗收檢查

- [x] 4.1 更新 `scripts/verify_browser.py` 驗證 `Nora · 產品經理` 卡片標題
- [x] 4.2 執行完整測試套件（`pytest Harness/tests -q`、`scripts/verify_onboarding.py`）與 `openspec validate add-product-manager-role --strict` 確認全部通過

## Workflow follow-up

- 完成所有任務與驗證後，將 `add-product-manager-role` change 同步規格並 archive 至 `openspec/changes/archive/`。

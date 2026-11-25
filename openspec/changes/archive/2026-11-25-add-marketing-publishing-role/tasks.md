## 1. 後端與 CLI 角色支援

- [x] 1.1 在 `Harness/printlab/onboarding.py` 的 `ROLES` 新增 `chloe`（`Chloe · 行銷與模型發布顧問`）與職責摘要，並更新 `_role()` 錯誤訊息
- [x] 1.2 確認 `onboarding.view()`、`reserve_role()`、`record_role()`、`release_role()` 與 `printlab onboarding` CLI 正確處理 `Chloe`

## 2. 工作台前端介面與樣式

- [x] 2.1 更新 `Harness/studio/src/Onboarding.jsx` 的「讓 Agent 接著設定」提示詞改由 `data.roles` 動態組成所有常駐角色名稱
- [x] 2.2 更新 `Harness/studio/src/onboarding.css` 的 `.onboarding-roles` 網格排版以良好容納三個以上角色卡片且維持窄螢幕無水平溢位
- [x] 2.3 重新建置 `Harness/studio` 前端靜態資產

## 3. 文件、規則與範本同步

- [x] 3.1 更新 `docs/ROLES.md` 新增 Chloe 角色提示詞、MakerWorld 上傳規則與限制及發布安全邊界說明，並更新 `docs/ONBOARDING.md` 常駐角色建隊說明
- [x] 3.2 更新 `AGENTS.md`、`.agents/skills/printlab/SKILL.md`、`config/team.md.example`、`Templates/Project/Review/team.md` 與 `README.md` / `README.zh-TW.md` / `README.en.md`

## 4. 測試與驗證

- [x] 4.1 更新並擴充 `Harness/tests/test_onboarding.py` 與 `Harness/tests/test_onboarding_cli.py`，涵蓋 Chloe 預留/登記、三角色就緒判定與範本檢查
- [x] 4.2 更新 `scripts/verify_browser.py` 驗證 `Chloe · 行銷與模型發布顧問` 卡片標題
- [x] 4.3 執行 pytest 與相關驗證腳本確認全部通過，並驗證 `openspec validate`

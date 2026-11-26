# Tasks

## 1. 後端角色定義與測試更新

- [x] 1.1 更新 `Harness/printlab/onboarding.py` 中 `ROLES['chloe']` 的職責描述為備齊 MakerWorld 上傳素材包、可複製文案與標籤、展示與封面圖規劃、專案 `.3mf` 與合規核對清單（供使用者自行上傳），並於 `Harness/tests/test_onboarding.py` 驗證 `reserve_role('Chloe', ...)` 產生之提示詞包含更新後職責與 `docs/ROLES.md`（執行 `pytest Harness/tests/test_onboarding.py -q` 通過）

## 2. 移除獨立技能並內化為 Chloe 角色能力

- [x] 2.1 刪除 `.agents/skills/makerworld-upload/` 目錄與其 `SKILL.md`，並確認倉庫不再殘留該獨立技能或引用
- [x] 2.2 更新 `docs/ROLES.md` 的 Chloe 與 Leo 提示詞及必守規範：將原 `makerworld-upload` 技能的完整素材包準備作業流程與交付核對清單完整內化為 Chloe 能力（單一 `MakerWorld/` 目錄、PLA 與 PETG 雙專案 `.3mf` 含 STL／CAD 匯入準備／Gyroid round-trip／A1 mini → A1 → H2S 單盤檢查與缺實物照待補標記、3 張不同角度實拍去陰影不改主體且另存、4:3 與 3:4 兩份獨立封面、依表單順序整理的 `MakerWorld/README.md` 五大文案區塊含列印／組裝教學與 Emoji／Tags／Boost Me、以及 `MakerWorld/` 結構化 JSON 與合規核對回報清單），移除對 `.agents/skills/makerworld-upload/SKILL.md` 的引用且完全排除瀏覽器代操作與 Save Draft 流程
- [x] 2.3 同步更新 `AGENTS.md`（移除 `.agents/skills/makerworld-upload/SKILL.md` 引用）、`Templates/Project/Review/team.md`、`config/team.md.example`、`README.md`、`README.zh-TW.md` 與 `README.en.md`，並於 `Harness/tests/test_onboarding_cli.py` 驗證新專案 `Review/team.md` 帶入 Chloe 與 Leo 更新後分工項目且 `.agents/skills/makerworld-upload` 已移除（執行 `pytest Harness/tests/test_onboarding_cli.py -q` 通過）

## 3. 工作區共用偏好與整合驗證

- [x] 3.1 透過 `Harness/bin/printlab.ps1 workspace note profile` 將新的 MakerWorld 使用者自行上傳分工、交付格式（`MakerWorld/README.md` 表單順序文案＋`MakerWorld/` 結構化 JSON）、PLA／PETG 雙專案 `.3mf`（缺實物照標記待補）、4:3／3:4 雙封面與 3 張實拍去陰影偏好寫入外部資料空間 `Context/profile.md`，並讀回確認已寫入
- [x] 3.2 執行完整測試與驗證套件（`pytest Harness/tests/test_onboarding.py Harness/tests/test_onboarding_cli.py`、`scripts/verify_onboarding.py`、`openspec validate update-makerworld-user-upload-workflow --strict` 與 `git grep makerworld-upload` 殘留檢查）確認全部通過

## Workflow follow-up

- 完成所有任務與驗證後，將 `update-makerworld-user-upload-workflow` 的 delta specs 同步至 `openspec/specs/team-roles/spec.md` 並 archive 至 `openspec/changes/archive/`，再以 `openspec validate team-roles --type spec --strict` 與 `openspec validate --specs` 確認規格完整。
- 更新交接文件 `C:\Users\tom83\OneDrive\文件\PrintLab\Context\Handoffs\2026-11-26-makerworld-user-upload-workflow.md` 補記移除獨立技能並內化為 Chloe 能力的結果。

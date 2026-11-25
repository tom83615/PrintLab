# team-roles Specification

## Purpose

定義 PrintLab 常駐團隊角色在命令列（CLI）、API、工作台「設定與團隊」頁面與範本文件中的一致行為，涵蓋既有的 Sarah、Mike 與新增的行銷及模型發布角色 Chloe。

## Requirements

### Requirement: 支援行銷與模型發布常駐角色 Chloe

PrintLab 的 onboarding 模組、CLI（`reserve-role`、`record-role`、`release-role`、`status`）與 `/api/onboarding` SHALL 支援常駐角色 `chloe`（顯示標題 `Chloe · 行銷與模型發布顧問`），負責 MakerWorld 等模型網站上架、生成描述文案、規劃展示圖片與適合分享的檔案形式，並在角色開場提示詞引導讀取 `AGENTS.md` 與 `docs/ROLES.md`。角色名稱比對 SHALL 不區分大小寫，且保留既有的 `sarah`（含歷史別名 `sara`）與 `mike`。

#### Scenario: 透過 CLI 預留並登記 Chloe 角色

- **WHEN** 宿主能力已記錄且呼叫端執行 `printlab onboarding reserve-role Chloe` 與 `record-role Chloe`
- **THEN** 系統產生綁定當前共享工作空間與行銷發布職責的提示詞、依版本檢查寫入 `Context/onboarding.json`，並在讀取首次介紹與共同文件路徑後將狀態標記為 `introduced`

#### Scenario: 既有工作區載入新增角色

- **WHEN** 既有工作區的 `Context/onboarding.json` 已完成 `mike` 與 `sarah` 的 `introduced` 記錄但尚未建立 `chloe`
- **THEN** `onboarding.view()` 與 `/api/onboarding` 保留既有 `mike` 與 `sarah` 記錄、將 `chloe` 顯示為 `pending`、在 `next_actions` 列出建立 `Chloe · 行銷與模型發布顧問` 的待辦，並將 `team_ready` 回報為 `false` 直到所有常駐角色皆達 `introduced`

#### Scenario: 拒絕未定義的角色名稱

- **WHEN** 呼叫端傳入不在常駐角色清單內的角色名稱給 `reserve-role`、`record-role` 或 `release-role`
- **THEN** 系統拒絕操作並回傳明確列出支援角色（Mike、Sarah、Chloe）的錯誤訊息

### Requirement: 工作台與範本同步呈現 Chloe 角色

PrintLab 工作台「設定與團隊」頁面 SHALL 呈現包含 `Chloe · 行銷與模型發布顧問` 在內的所有常駐角色卡片，其複製設定提示詞 SHALL 動態列出所有常駐角色名稱，且在桌面與行動裝置視窗寬度下不得產生水平溢位。專案分工範本與角色文件 SHALL 包含 Chloe 的職責、提示詞、MakerWorld 上傳規則與限制，以及發布授權邊界。

#### Scenario: 在工作台檢視設定與團隊頁面

- **WHEN** 使用者開啟工作台 `/#/onboarding` 頁面
- **THEN** 頁面顯示 `Sarah · 3D 列印顧問`、`Mike · 工作流設計師` 與 `Chloe · 行銷與模型發布顧問` 三張角色卡片，點擊「讓 Agent 接著設定」所複製的提示詞包含所有常駐角色名稱

#### Scenario: 建立新專案帶入 Chloe 分工

- **WHEN** 使用者執行 `printlab new` 建立新專案
- **THEN** 新專案產生的 `Review/team.md` 包含 Chloe 負責模型網站上架、描述文案、展示圖片與分享檔案形式的分工項目

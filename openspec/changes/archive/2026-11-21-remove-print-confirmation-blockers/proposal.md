# Proposal

## Why

P001 已實際完成，但 PrintLab 把未記錄的逐項現場確認當成任務配置錯誤，導致合法的 Studio 手動流程長期停在 `awaiting_configuration`。使用者要求材料、FTS/噴嘴路線、設備就緒、板面清空與列印授權的任務確認不再成為必要條件或阻擋理由。

## What Changes

- 移除上述逐任務確認事實作為 approve、preflight、workbench 與 Studio handoff 的必要條件。
- Generic PLA 與未確認的 AMS/噴嘴路線可保留為切片/路由資訊，不單獨導致 `awaiting_configuration`。
- FTS 聲明變化不再使列印任務指紋失效。
- 保留實際錯誤檢查：檔案與模型完整性、機型/板型不相符、明確設備故障/離線、已有活動或結果不明的發送，以及明確要求清板的設備狀態。
- 送印仍由使用者主動執行 PrintLab 發送或在官方 Studio 點擊 Send，不新增自動啟動。

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `print-dispatch`: 任務確認事實不再是發送配置或批准阻擋條件。

## Impact

影響 `confirmation`, `core`, `bambuddy`, `prepared`, `workbench`, `official` 與相關 CLI/UI 任務檢查。既有確認事件與列印紀錄保留；不回寫或偽造 P001 的歷史發送回執。

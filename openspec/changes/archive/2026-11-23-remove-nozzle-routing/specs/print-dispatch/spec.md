## MODIFIED Requirements

### Requirement: Block dispatch when required evidence is unknown
PrintLab SHALL 由使用者主動啟動送印。缺少逐任務的就緒、裝料、清板及授權事實 SHALL NOT 單獨阻擋送印。即時設備狀態顯示離線、忙碌、故障、明確等待清板或發送結果不明時 SHALL 繼續阻擋。

#### Scenario: Required routing cannot be verified
- **WHEN** 使用者準備、批准或送出未指定噴嘴路線的任務
- **THEN** PrintLab SHALL 接受通過其他檢查的任務，且略過舊任務記錄的噴嘴路線欄位

#### Scenario: Current device readiness is unavailable
- **WHEN** 缺少逐任務的就緒或清板確認
- **THEN** PrintLab SHALL 依即時設備狀態執行適用的檢查

#### Scenario: Manual Studio handoff requires current observations
- **WHEN** 使用者執行官方 Studio 手動交接
- **THEN** PrintLab SHALL 依檔案完整性與印表機身份核對交接條件

#### Scenario: 檢查材料與文件
- **WHEN** 送印流程核對切片及實際料槽
- **THEN** PrintLab SHALL 保留板型、材料來源及身份、切片完整性和設備身份檢查

# Print Dispatch Specification

## Purpose

讓 PrintLab 在不依賴 Bambuddy 佇列服務的情況下延續已批准列印任務，並在設備或供料證據不足時安全阻止發送。

## Requirements

### Requirement: Use the official Studio path without Bambuddy
PrintLab SHALL support its official Bambu Studio handoff for an approved print task without requiring Bambuddy configuration or queue access.

#### Scenario: Prepare an approved Studio handoff
- **WHEN** a task has a valid model and slice binding, current required device and material evidence, and user approval
- **THEN** PrintLab prepares the official Studio handoff with the approved task identity and does not submit it to a Bambuddy queue

#### Scenario: Bambuddy is not configured
- **WHEN** the user uses the supported official Studio handoff and has not configured Bambuddy
- **THEN** PrintLab does not block the handoff solely because Bambuddy is absent

### Requirement: Bind manual Studio tasks to a local printer identity
When Bambuddy is not configured, PrintLab SHALL bind each prepared task to the locally configured Studio printer name, model, and serial number, and SHALL include that identity in task approval validation.

#### Scenario: Studio printer identity is missing
- **WHEN** a user prepares or approves a task without a complete local Studio printer identity
- **THEN** PrintLab identifies the missing identity and does not approve or reserve the task for dispatch

#### Scenario: Studio printer identity changes
- **WHEN** the configured Studio printer identity changes after a task was prepared or approved
- **THEN** the existing approval becomes invalid and PrintLab requires a newly bound task

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

### Requirement: Reconcile the same approved task without a Bambuddy queue
PrintLab SHALL preserve task identity and report dispatch outcome as unknown until the official Studio handoff has an observable result; it SHALL NOT retry an uncertain dispatch automatically.

#### Scenario: Studio handoff outcome is uncertain
- **WHEN** PrintLab cannot determine whether the official Studio handoff reached the printer
- **THEN** PrintLab records an unresolved outcome and requires reconciliation before another submission

#### Scenario: User records a manual observation
- **WHEN** the user reconciles a no-Bambuddy Studio task with the exact expected task name and an observation source
- **THEN** PrintLab records the observation against the same task without contacting a printer service or creating a new dispatch

### Requirement: 驗證 H2C Studio 交接切片

PrintLab SHALL 使用支援 H2C 切片設定的獨立離線檢查器。檢查證據 SHALL 與選定切片的 SHA-256、機型與盤號相符。

#### Scenario: H2C 單材料切片

- **WHEN** 檢查 Bambu Studio 02.09.01.70 所產生的有效 H2C 單材料切片
- **THEN** 檢查結果可辨識其首層溫度設定並回傳相符的檢查證據

#### Scenario: 檔案檢查未通過

- **WHEN** 檢查失敗或證據不符合檔案、機型或盤號
- **THEN** 不建立 Studio 送印回執

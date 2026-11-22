## ADDED Requirements

### Requirement: 驗證 H2C Studio 交接切片

PrintLab SHALL 使用支援 H2C 切片設定的獨立離線檢查器。檢查證據 SHALL 與選定切片的 SHA-256、機型與盤號相符。

#### Scenario: H2C 單材料切片

- **WHEN** 檢查 Bambu Studio 02.09.01.70 所產生的有效 H2C 單材料切片
- **THEN** 檢查結果可辨識其首層溫度設定並回傳相符的檢查證據

#### Scenario: 檔案檢查未通過

- **WHEN** 檢查失敗或證據不符合檔案、機型或盤號
- **THEN** 不建立 Studio 送印回執

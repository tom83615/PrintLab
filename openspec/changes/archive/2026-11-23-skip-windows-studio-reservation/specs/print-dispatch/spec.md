## ADDED Requirements

### Requirement: Windows 官方 Studio 直接手動送印

Windows 無 Bambuddy 的官方 Studio 路線 SHALL 允許使用者以 Studio 直接送出已準備的列印檔。

#### Scenario: 準備手動送印

- **WHEN** Agent 核對已批准的 Windows 官方 Studio 列印檔
- **THEN** PrintLab SHALL 回傳已核對的檔案與設備資訊，且不建立限時預約或派發回執
- **AND** 使用者 SHALL 可直接在 Studio 按「送出」

#### Scenario: 未預約的手動送印事後對帳

- **WHEN** 對帳帶有已批准任務的精確 Studio 任務名稱、觀察結果及來源，且任務指紋與批准一致
- **THEN** PrintLab SHALL 在同一任務下登記已觀察的結果，不接觸設備或重新送印

#### Scenario: 舊版預約

- **WHEN** 已有相符的舊版手動送印回執且提供了精確 Studio 任務觀察
- **THEN** PrintLab SHALL 允許在原紀錄上對帳

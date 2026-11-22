## ADDED Requirements

### Requirement: 清理一次性切片輸出

PrintLab SHALL 在作業專用的暫存目錄執行 Bambu Studio 命令列切片，並在作業結束時清理該目錄中的一次性切片輸出。

#### Scenario: 正常結束切片

- **WHEN** 切片器在工作目錄產生 `result.json` 等一次性報告
- **THEN** 暫存報告會被清理，正式切片包、任務記錄和切片日誌仍存於任務目錄

#### Scenario: 切片失敗

- **WHEN** 切片子程序未成功完成
- **THEN** 暫存報告仍會被清理，既有的失敗狀態與診斷照常處理

#### Scenario: 呼叫端已有同名檔案

- **WHEN** 呼叫端的工作目錄已有 `result.json`
- **THEN** 切片器及自動清理皆保留該檔案

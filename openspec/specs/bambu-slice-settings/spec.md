# bambu-slice-settings Specification

## Purpose

讓使用者以 Bambu Studio 開啟 PrintLab 從 STL 或幾何 3MF 產生的切片包時，保留指定的稀疏填充圖樣，以免重新切片時套用系統預設。

## Requirements

### Requirement: 保留指定的稀疏填充圖樣

一般 `printlab slice` 路徑在工藝檔明確指定稀疏填充圖樣時 SHALL 將圖樣及其工藝差異標記寫入輸出 3MF，並核對該盤 G-code 所記錄的圖樣。

#### Scenario: 標準預設搭配 Gyroid 覆寫

- **WHEN** 工藝檔選用標準預設並設定 Gyroid
- **THEN** 切片包內的專案設定和該盤 G-code 都記錄 Gyroid，專案設定也登記該工藝差異

#### Scenario: 切片器未保留圖樣或標記

- **WHEN** 輸出缺少工藝差異標記，或專案設定和 G-code 任一項與指定圖樣不符
- **THEN** 任務標為切片失敗且無法進入批准流程

#### Scenario: 交由切片器選擇預設圖樣

- **WHEN** 工藝檔未指定稀疏填充圖樣
- **THEN** 繼續沿用切片器原本的行為

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

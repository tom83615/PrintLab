## Why

Bambu Studio 命令列切片會在工作目錄留下 `result.json` 等一次性輸出。從倉庫根目錄切片時，這些檔案會混入工作區，可能被一併加入 Git。

## What Changes

- 將切片器的工作目錄放在每次作業專用的暫存目錄，作業結束時自動清理。
- 在交付流程說明如何回收舊版遺留且可確認來源的一次性報告。

## Capabilities

### Modified Capabilities

- `bambu-slice-settings`：隔離並清理切片器的一次性輸出。

## Impact

影響 PrintLab 切片、官方 Studio 離線驗證與切片交付流程。正式切片包、任務記錄與切片日誌仍使用原有路徑。

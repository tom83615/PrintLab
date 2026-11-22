## Context

舊版 1.1.33 拒絕 H2C 的首層溫度資料。隔離安裝的 1.1.99 可處理該檔案，且仍支援公開的 `inspect_print_file`。

## Decisions

- 更新上游的精確版本和鎖定檔，保留現行檔案快照、雜湊、機型與盤號核對。
- 重新安裝後，以現行 PrintLab 離線入口檢查同一份 H2C Studio 交接切片。

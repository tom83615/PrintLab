# Design

## Context

參考 proposal.md。建置器掃描 `Design/<revision>` 並把相對路徑存入來源與產物 hash map。Windows 的 `Path` 字串形式使用反斜線，而消費端以 POSIX 路徑比較。

## Goals / Non-Goals

**Goals:** 讓 manifest 路徑在 Windows 與 POSIX 上有相同穩定表示，並保留所有現有來源與 artifact hash 驗證。

**Non-Goals:** 不遷移專案檔案、不變更 manifest schema、不修補既有不完整/失敗的建置記錄。

## Decisions

- 產生相對路徑時呼叫 `Path.relative_to(root).as_posix()`，同時套用於 `source_sha256` 與 `artifacts`。這在 manifest 邊界標準化，優於讓每個消費端猜測多種分隔符。
- 抽出一個接受 pathlib path 的小型相對路徑函式，使 `PureWindowsPath` 可在任一主機平台測試；不新增依賴。

## Risks / Trade-offs

- 既有 Windows manifest 仍可能含反斜線；本次不做遷移。新 build 會用一致格式，舊 revision 可依需求重建。
- 路徑須仍位於專案根內；`relative_to` 會在越界時明確失敗。

# Design

## Context

`Harness/printlab/core.py` 的 `runtime_root()` 已經使用 `_ENV_RUNTIME_ROOT and ROOT == _INITIAL_ROOT` 判斷是否處於外部資料空間分離模式，避免影響測試對 `core.ROOT` 的 monkeypatch。`code_path()` 需採用一致條件，才不會讓未複製 `Templates/` 的隔離測試讀到程式碼倉庫的模板。

## Decisions

- `code_path(rel)` 優先回傳已存在的 `ROOT / rel`；僅當 `_ENV_RUNTIME_ROOT and ROOT == _INITIAL_ROOT` 時回退 `CODE_ROOT / rel`，否則維持回傳 `ROOT / rel`。

# Proposal

## Why

`core.code_path()` 在 `core.ROOT` 被單元測試 monkeypatch 至不含 `Templates/` 的暫存目錄時仍回退讀取程式碼倉庫的 `Templates/Project`，導致 `test_publication.py` 的 `test_init_and_packet_output_reject_symlink_directories` 提前生成 `Review/Publication/record.json` 而在 CI 失敗。

## What Changes

- 限制 `core.code_path()` 僅在啟用分離 Runtime 模式且 `core.ROOT` 未被改寫（`_ENV_RUNTIME_ROOT and ROOT == _INITIAL_ROOT`）時才回退至 `CODE_ROOT`。
- 補充單元測試驗證 monkeypatch `core.ROOT` 時不會從程式碼倉庫洩漏模板檔案。

## Capabilities

### New Capabilities

### Modified Capabilities

## Impact

- `Harness/printlab/core.py`
- `Harness/tests/test_external_workspace.py`

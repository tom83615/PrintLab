# Tasks

## 1. 修正 code_path 回退邊界

- [x] 1.1 更新 `Harness/printlab/core.py` 的 `code_path()`，僅於分離 Runtime 模式且未 monkeypatch `core.ROOT` 時回退至 `CODE_ROOT`。
- [x] 1.2 在 `Harness/tests/test_external_workspace.py` 補上 monkeypatch `core.ROOT` 隔離回歸測試，並驗證 `test_publication.py` 與 `test_external_workspace.py` 通過。

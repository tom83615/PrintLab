# macOS 視窗與發送助手

需要 macOS 14+ 和 Xcode Command Line Tools。

執行 `zsh Harness/macos/build.sh` 構建 PrintLab 視窗，產物在 `Runtime/macos-build/PrintLab.app`。構建時寫入本機實際工作區路徑，啟動後訪問本機 8018 服務。先執行 `scripts/start.sh`。

`StudioBridge.swift` 是單獨的發送助手原始碼，使用 `printlab studio-bridge --help` 查看安裝與權限命令。許可和支援範圍見 `docs/PRINTING.md`。構建或申請權限本身不會生成具體列印授權。

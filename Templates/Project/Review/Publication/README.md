# 公開上傳準備（按需）

本專案的 `record.json` 預設 `local_only`，不影響設計、收藏、私人列印或原有列印批准。

使用者提出公開上傳時，執行 `printlab publish init 專案 --kind original|remix|print_profile`，按 `<PRINTLAB_ROOT>/Library/Publishing/README.md` 儲存全部來源許可、實質改動、上傳文件與實拍證據，再執行 `publish check / prepare`。

檢查結果是已核對、缺失或不允許，不適用項解釋原因。任何核對通過僅表示可交使用者審查；公開上傳確認獨立於設計/列印確認。當前工具只生成本機待審資料，沒有自動上傳能力。

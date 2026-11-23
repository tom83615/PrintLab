## Context

Windows 官方 Studio 手動路線的 `submit --execute` 只在本機寫入限時預約。實際送印由使用者在 Studio 操作。

## Decisions

- Windows 手動路線把既有 `submit --execute` 當作預檢，回傳核對後的檔案與設備。預檢不建立派發回執，也不轉換任務狀態。
- 使用者在 Studio 送出後，有同名任務的觀察證據時才建立已觀察的派發紀錄。第一次對帳驗證批准的指紋、任務身分及檔案。既有 Windows 回執仍可對帳，已結案的觀察仍可安全重試。
- AI 處理檔案準備與預檢。使用者只需要在 Studio 核對後送出。

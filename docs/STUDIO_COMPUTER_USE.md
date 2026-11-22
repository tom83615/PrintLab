# Codex 找不到 Studio 窗口時怎麼辦

## 這次修了什麼

[Issue #7](https://github.com/AFangTeam/PrintLab/issues/7) 來自 MacBook Air M1 / macOS 15.6.1、中文 Studio 02.08.02.61、A1 0.4 mm、PLA、無 AMS / Ext。`noWindowsAvailable` 由 Codex Computer Use 返回；當時沒有調用 PrintLab 發送助手。CLI 和人工界面切片成功。報告中的組合調用不足以確定底層哪一步失敗，後來鎖屏也不能解釋此前錯誤。

**v0.4.2 增加獨立的 Mac Studio 窗口控制入口。** Codex 可以調用 PrintLab 自己的助手讀取窗口、恢復指定窗口、打開已有切片和發送準備頁，不必一直重試發生故障的 Computer Use 調用。修復了助手對 macOS `/private/tmp` 路徑的誤判，改為按窗口身份截圖，並在點擊前檢查前台、窗口位置和遮擋。超時保留回執，絕不自動重發。

這不是 Codex 引擎補丁，也不代表已在報告者的 M1 上驗證通過。v0.4.1 只有 Windows 修復，不能用它驗證本次新增能力。沒有證據要求升級或降級 Studio。

## 先判斷是否需要操作窗口

發送打印優先按 [默認發送路線](PRINTING.md#默認發送路線與後備方案) 評估 Bambuddy。適配和授權齊全時，直接通過 PrintLab 隊列發送，無需修復窗口才能發送。用戶拒絕授權、本版未適配或發送前檢查失敗時，再接續本頁的 Studio 後備方案。結果不明先對帳，不能把窗口故障當作換通道重發的理由。

報告者的 A1 / Ext 尚不在本版隊列適配範圍。可以直接在 Studio 複用已有切片完成當前打印。只有需要新增窗口助手時才升級，不讓用戶為了繼續打印長時間 debug。

## 最少操作

讓 Codex 按 [更新指南](UPGRADING.md) 升級到 v0.4.2，保留工程、配置、材料和舊任務。然後在新版工作空間執行：

```bash
./Harness/bin/printlab studio-bridge build
./Harness/bin/printlab studio-bridge windows
```

構建需要 macOS 14+ 和 Apple Swift 編譯工具。若缺少工具，由 Codex 按系統提示處理；構建成功不等於系統權限已授予。只有 `windows` 顯示權限缺失時才執行 `studio-bridge permissions`，按系統要求給 **PrintLab发送助手** 授予輔助功能和屏幕讀取權限，再重跑 `windows`。不要刪除 TCC 數據或給其他程序反覆授權。

`windows` 返回進程 ID、完整窗口標題、Studio 版本和會話狀態。後續目標必須來自這次實際返回，不能照抄示例數字。

```bash
# 只觀察指定窗口
./Harness/bin/printlab studio-bridge inspect --studio-pid PID --window-title '完整標題'
# 恢復並激活該窗口一次，等待窗口穩定，不點擊打印按鈕
./Harness/bin/printlab studio-bridge recover --studio-pid PID --window-title '完整標題'
```

需要打開已有的單盤 `.gcode.3mf` 時，先計算當前文件 SHA-256，再運行：

```bash
./Harness/bin/printlab studio-bridge open-file --file '/絕對路徑/文件.gcode.3mf' --sha256 '實際64位哈希'
```

該命令保留原工程，在 `Runtime/studio-previews` 生成經過逐項檢查的預覽副本，刀路和打印參數不變，不重新切片；另開 Studio 實例，返回新的進程 ID 和標題。打開後先 `inspect` 核對實際內容，再用返回的目標打開準備頁：

```bash
./Harness/bin/printlab studio-bridge open-panel --studio-pid PID --window-title '文件.gcode'
```

`opened_panel: true` 表示實際讀到了“发送打印任务”窗口，**沒有點擊最終發送**。按鈕被其他窗口或通知遮擋時會拒絕點擊；先移開遮擋、重新觀察，再決定是否重試。超時或讀回失敗時先看當前窗口，不能假定動作沒發生。

## A1 外掛與最終發送

通用窗口命令不要求 X2D、AMS 或打印機名稱，因此 A1 無 AMS 也能使用。它們不創建打印批准或發送記錄，也不代替機型、材料和清板核驗。

**A1 / Ext 的最終自動發送尚未適配和實機驗證。** 工作台現有自動發送仍限已驗證的 X2D 單料 AMS 組合，Bambuddy 隊列仍要求 `use_ams=true`。不能偽造 AMS、刪除檢查或把 A1 套進 X2D 發送流程。A1 到準備頁後核對實際 A1 / Ext 與具體文件，最終發送由使用者在當前任務獲得確認後完成；已有任務已發送或結果不明時，先對帳，不再發送。

如果用戶只需要繼續當前已成功切片的打印，可以直接在 Studio 中完成，無需為了排障升級。若希望 Codex 繼續自動操作窗口，推薦升級本版，避免要求用戶長時間 debug。

## 報錯與驗證範圍

錯誤包含 `code`、`stage` 和具體原因，區分權限、鎖屏、窗口缺失、激活失敗、窗口變化、遮擋和動作後未讀到結果。未知回執保留在 `Runtime/studio-bridge-ipc` 的私有目錄中；核實結果之前不要清理或重試發送。診斷只分享必要的脫敏錯誤，不能上傳整個 Runtime 或項目目錄。

本機中文 Studio 02.08.02.61 已實際驗證窗口讀取、指定窗口捕獲、A1 測試切片的發送準備頁、遮擋拒絕、獨立實例打開以及 X2D 預覽。A1、A1 mini、P1S、X1 Carbon、X2D 的合成模型均通過官方 CLI 切片。沒有 A1 實體發送驗證，也沒有復現報告者完全相同的底層錯誤。詳細範圍見 [機型說明](MACHINE_SUPPORT.md)。

#7 保持開放，等待報告者用新助手做一次不發送的窗口複驗。成功只確認新路徑在其電腦可用，不能據此聲稱 Codex 的窗口引擎已修復。

## 可以直接給觀眾的 Codex

```text
請將我的 PrintLab 按官方 docs/UPGRADING.md 升級到 v0.4.2，保留工程、配置、設備、材料和任務記錄，不重發舊任務。
按 docs/STUDIO_COMPUTER_USE.md 構建 PrintLab发送助手，讀取 windows；只在缺權限時引導我完成一次系統授權。
我的配置是 A1、0.4 mm、PLA、無 AMS、Ext。保留實際配置，不套用 X2D/AMS。
複用已有正確切片，計算 SHA-256，通過 studio-bridge open-file 打開獨立預覽，inspect 核對後用 open-panel 打開發送準備頁。不要最終發送，不要反覆調用失敗的 Computer Use。
報告成功到哪一步；失敗只給我 code、stage、脫敏原因和一個最少操作。超時先讀回，不重放動作。不要上傳憑據或私人工程。
```

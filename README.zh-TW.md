# PrintLab

繁體中文（台灣） · [English](README.en.md)

把一個想法，接著做成一件拿得起來的東西。

PrintLab 是阿方（Eric）在 E41 影片中使用的 3D 列印工作台與協作流程，面向 **Mac / Windows + Codex + 拓竹列印機**。你描述需求，Codex 協助選外形、建立模型、比較切片，再把版本、材料、列印記錄和實物回饋保存在同一個工作區。

## 看影片瞭解 PrintLab

[![當 ChatGPT 接上 3D 列印機——阿方的 PrintLab 示範（中文）](https://i.ytimg.com/vi/q7G8J5Tz0aQ/hqdefault.jpg)](https://www.youtube.com/watch?v=q7G8J5Tz0aQ)

[在 YouTube 觀看](https://www.youtube.com/watch?v=q7G8J5Tz0aQ) · [在 B 站觀看](https://www.bilibili.com/video/BV1r1W26hEHg/)

阿方 EricFang：《當 ChatGPT 接上 3D 列印機……》。影片語言：中文。當前發送支持範圍以本頁和列印指南為準。

> **致謝與專案分工**：感謝 [Text-to-CAD](https://github.com/earthtojake/text-to-cad) 提供 CAD 建模與查看工具、[Bambuddy](https://github.com/maziggy/bambuddy) 提供列印機狀態、耗材與列印記錄管理，以及 [Bambu Studio](https://github.com/bambulab/BambuStudio) 提供切片與官方發送能力。PrintLab 的原創部分是工作台、協作流程和適配接口；這些第三方工具由各自作者維護，從原專案獨立安裝並遵循各自許可。完整來源與許可見 [第三方說明](docs/DEPENDENCIES.md)。

## 歷史與收藏的同步範圍

當前發佈版彙總 Bambuddy 已捕獲的列印記錄，並展示本地維護的靈感收藏。安裝前的 Bambu Cloud 歷史和 MakerWorld 帳號收藏導入已排除在本輪開發範圍外。需要保留 Handy、雲列印和帳號收藏的使用者，應在安裝時明確這些需求，按同步排查核對已有功能。

已有檔案缺圖時，可用 `printlab history-recover` 從 Mac Studio 緩存或明確綁定的本地 PNG / 3MF 恢復。

[模型預覽恢復](docs/PREVIEW_RECOVERY.md) · [歷史與收藏來源說明](docs/SYNC_TROUBLESHOOTING.md)

工作台界面目前為中文。默認首頁、安裝和核心 Agent 協作說明採用英文，部分深入指南及專案模板仍為中文；Agent 可以按你的語言偏好解釋。詳見 [語言範圍](docs/LANGUAGE.md)。

## 從這裡開始

把儲存庫連結和下面這段話發給具有本機終端、文件讀寫能力的 Codex 或其他 Agent。

> 請幫我安裝 https://github.com/AFangTeam/PrintLab 。先讀 README.md、AGENTS.md 和 docs/AGENT_START.md，在本機建立長期工作區，啟動工作台並運行入門驗收。自動建立 Sarah · 3D 列印顧問和 Mike · 工作流設計師兩個獨立聊天，全部綁定同一工作區，讓它們讀取共同資料並分別介紹自己。瞭解我的列印機、材料與使用習慣，按 docs/ONBOARDING.md 接續配置，記錄實際建立狀態。第一件作品確定後再建立任務小組。第三方工具從原專案獨立安裝。需要設備資訊、登錄或系統權限時告訴我具體操作。最後給我工作區路徑、工作台地址、角色入口、驗證結果和下一步。

儲存庫內提供原創 [PrintLab Skill](.agents/skills/printlab/SKILL.md)。支持儲存庫 `.agents/skills` 的 Agent 可在此工作區加載；其他宿主按自身技能安裝規則安裝該目錄，技能仍需指向實際工作台。首次設備資訊按 [配置訪談](docs/FIRST_RUN.md) 收集。

觀眾的聊天、網頁操作與分工示例見 [交互指南](docs/GETTING_STARTED.md)。Agent 的執行步驟與完成標準見 [接手指南](docs/AGENT_START.md)。

想自己安裝，可以使用 Python 3.11+ 與 Node.js 22+，在終端執行以下命令。

```bash
git clone https://github.com/AFangTeam/PrintLab.git
cd PrintLab
bash scripts/setup.sh
bash scripts/start.sh
```

打開 <http://127.0.0.1:8018>。安裝程序生成空工作區與本機配置，重複運行會保留已有配置。系統 Python 版本較舊時，用 `PRINTLAB_PYTHON=/你的/python3路徑 bash scripts/setup.sh` 指定解釋器。詳細步驟見 [安裝指南](docs/SETUP.md)。

也可以從 [Release](https://github.com/AFangTeam/PrintLab/releases/latest) 下載 `PrintLab.zip`。解壓得到 `PrintLab/` 資料夾，在 Codex 中打開，或執行以下命令。

```bash
curl -fL -o PrintLab.zip https://github.com/AFangTeam/PrintLab/releases/latest/download/PrintLab.zip
unzip PrintLab.zip
cd PrintLab
bash scripts/setup.sh
bash scripts/start.sh
```

Windows 用戶在 PowerShell 中運行以下命令。安裝 Python 3.11+ 和 Node.js 22+ 後，打開儲存庫目錄。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start.ps1
```

Windows 的工具路徑、驗證命令和官方 Studio 交接見 [Windows 指南](docs/WINDOWS.md)。

## 這支隊伍怎樣配合

- **Sarah · 3D 列印顧問** 瞭解你的設備、材料和常見故障，幫助核對配件與耗材。購物清單可以跨專案彙總。實際加購物車由你授權後，交給具備瀏覽器操作能力的 Codex 完成。
- **Mike · 工作流設計師** 維護工具連接、工作台和共用規則，處理安裝、版本、接口與流程問題。
- **任務小組 · 作品名稱** 每件作品開一個對話，保存需求、選圖、源模型、切片與回饋，後續會話接著同一專案繼續。

角色可直接從 [角色提示詞](docs/ROLES.md) 複製。工作台通過文件和命令向 Codex 提供上下文，具體模型與工具能力取決於使用者當前安裝的 Codex 環境。

## 工作台裡有什麼

- 專案圖冊、真實 3D 模型預覽和設計版本。
- Bambuddy 提供的設備、材料與已捕獲列印歷史。
- 靈感收藏、個人偏好和每輪選圖記錄。
- 跨專案配件清單、庫存與採購記錄。
- 已準備的列印包、材料映射、時間和用量，以及綁定具體任務的確認與回執。

首次安裝會顯示空專案和未連接設備。按安裝指南連接自己的設備後，頁面展示相應資料。

## 從需求到實物

描述用途與尺寸 → 選外形 → 確認三視圖 → 實際 CAD → 對照修改 → 配色與材料 → 切片比較 → 確認這一版列印 → 實物回饋。

新外形默認先選單張方案，再從同一方案的四套三視圖中選一套。小改動按影響範圍處理，已有決定接續使用。Text-to-CAD 提供建模和查看能力，尺寸、接口和實際裝配仍逐項檢查。完整步驟在 [工作流](Context/workflow.md)。

## 支持範圍

v0.4.3 新增只讀 `dispatch-plan`，先判斷機型和供料方式，再建議所需權限。已適配的 A1、A1 mini、P1S、X1 Carbon AMS 組合優先評估 Bambuddy 隊列，Mac 與 Windows 共用該通道；真實設備接收仍需現場驗證。用戶拒絕權限、需要保留雲功能或本版未適配時，走官方 Studio 後備，必要時交接人工發送。**A1 無 AMS / Ext 的 PrintLab 自動發送尚未適配。** 發送結果未知時先對帳，不能換通道重發。

Mac 使用 macOS 14+，推薦 Apple Silicon。Windows 提供原生 PowerShell 安裝、命令行與瀏覽器工作台。通用工作台可獨立啟動，設備狀態與歷史依賴單獨安裝的 Bambuddy。Mac 自動發送助手對應 **X2D、中文 Bambu Studio 02.08.02.61、0.4 mm、單主料 AMS、左主噴嘴、紋理 PEI 單盤**。其他機型、軟體版本和多材料路線需要 Codex 按現場情況核對，詳見 [兼容性與列印](docs/PRINTING.md)。

本儲存庫提供工作台源碼、原創流程文檔、角色提示詞和空專案模板。第三方專案、模型權重、Bambu 軟體和插件從各自官方來源獨立獲取。你自己的作品保存在本機 `Project/`。第三方來源及職責見 [依賴說明](docs/DEPENDENCIES.md)。

## 開發與驗證

```bash
Runtime/venv/bin/python scripts/verify_onboarding.py
Runtime/venv/bin/python -m pytest Harness/tests -q
node --test Harness/tests/native-inspection.test.mjs
cd Harness/studio && npm run build
```

測試使用臨時工作區與合成設備。已安裝設備的只讀檢查需顯式設置 `PRINTLAB_LIVE_TEST=1`。發佈版驗證記錄見 [驗證說明](docs/VERIFICATION.md)。

## 使用許可與署名

PrintLab 原創源碼和文檔採用 **PolyForm Noncommercial 1.0.0**。允許在許可規定的非商業用途下使用、修改和再發布，再發布須附上許可及 `NOTICE.txt` 中的署名聲明。商業用途需要另行取得 AFangTeam 授權。

原作者為 **AFangTeam / 阿方（Eric）**，專案地址為 <https://github.com/AFangTeam/PrintLab>。許可全文見 [LICENSE.md](LICENSE.md)，署名要求見 [NOTICE.txt](NOTICE.txt)。獨立安裝的第三方軟體遵循各自的許可。

當前機型與驗證邊界見 [支持範圍](docs/MACHINE_SUPPORT.md)，發送與接續故障見 [排障指南](docs/TROUBLESHOOTING.md)。

# PrintLab

繁體中文（台灣） · [English](README.en.md)

把一個想法，接著做成一件拿得起來的東西。

PrintLab 是阿方（Eric）在 E41 影片中使用的 3D 列印工作台與協作流程，面向 **Mac / Windows + Codex + 拓竹印表機**。你描述需求，Codex 協助選外形、建立模型、比較切片，再把版本、材料、列印記錄和實物回饋儲存在同一個工作區。

## 歷史與收藏的同步範圍

當前發佈版彙總 Bambuddy 已捕獲的列印記錄，並展示本機維護的靈感收藏。安裝前的 Bambu Cloud 歷史和 MakerWorld 帳號收藏匯入已排除在本輪開發範圍外。需要保留 Handy、雲列印和帳號收藏的使用者，應在安裝時明確這些需求，按同步排查核對已有功能。

已有檔案缺圖時，可用 `printlab history-recover` 從 Mac Studio 緩存或明確綁定的本機 PNG / 3MF 恢復。

[模型預覽恢復](docs/PREVIEW_RECOVERY.md) · [歷史與收藏來源說明](docs/SYNC_TROUBLESHOOTING.md)

## 從這裡開始

把倉庫連結和下面這段話發給具有本機終端、文件讀寫能力的 Codex 或其他 Agent。

> 請幫我安裝 https://github.com/AFangTeam/PrintLab 。先讀 README.md、AGENTS.md 和 docs/AGENT_START.md，在本機建立長期工作區，啟動工作台並執行入門驗收。自動建立 Sarah · 3D 列印顧問和 Mike · 工作流設計師兩個獨立聊天，全部綁定同一工作區，讓它們讀取共同資料並分別介紹自己。瞭解我的印表機、材料與使用習慣，按 docs/ONBOARDING.md 接續設定，記錄實際建立狀態。第一件作品確定後再建立任務小組。第三方工具從原專案獨立安裝。需要設備資訊、登入或系統權限時告訴我具體操作。最後給我工作區路徑、工作台地址、角色入口、驗證結果和下一步。

倉庫內提供原創 [PrintLab Skill](.agents/skills/printlab/SKILL.md)。支援倉庫 `.agents/skills` 的 Agent 可在此工作區載入；其他宿主按自身技能安裝規則安裝該目錄，技能仍需指向實際工作台。首次設備資訊按 [設定訪談](docs/FIRST_RUN.md) 收集。

觀眾的聊天、網頁操作與分工示例見 [交互指南](docs/GETTING_STARTED.md)。Agent 的執行步驟與完成標準見 [接手指南](docs/AGENT_START.md)。

想自己安裝，可以使用 Python 3.11+ 與 Node.js 22+，在終端執行以下命令。

```bash
git clone https://github.com/AFangTeam/PrintLab.git
cd PrintLab
bash scripts/setup.sh
bash scripts/start.sh
```

開啟 <http://127.0.0.1:8018>。安裝程序生成空工作區與本機設定，重複執行會保留已有設定。系統 Python 版本較舊時，用 `PRINTLAB_PYTHON=/你的/python3路徑 bash scripts/setup.sh` 指定解釋器。詳細步驟見 [安裝指南](docs/SETUP.md)。

也可以從 [Release](https://github.com/AFangTeam/PrintLab/releases/latest) 下載 `PrintLab.zip`。解壓得到 `PrintLab/` 資料夾，在 Codex 中開啟，或執行以下命令。

```bash
curl -fL -o PrintLab.zip https://github.com/AFangTeam/PrintLab/releases/latest/download/PrintLab.zip
unzip PrintLab.zip
cd PrintLab
bash scripts/setup.sh
bash scripts/start.sh
```

Windows 使用者在 PowerShell 中執行以下命令。安裝 Python 3.11+ 和 Node.js 22+ 後，開啟倉庫目錄。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start.ps1
```

Windows 的工具路徑、驗證命令和官方 Studio 交接見 [Windows 指南](docs/WINDOWS.md)。

## 這支團隊怎樣配合

- **Sarah · 3D 列印顧問** 瞭解你的設備、材料和常見故障，幫助核對配件與耗材。購物清單可以跨專案彙總。實際加購物車由你授權後，交給具備瀏覽器操作能力的 Codex 完成。
- **Mike · 工作流設計師** 維護工具連接、工作台和共用規則，處理安裝、版本、介面與流程問題。
- **任務小組 · 作品名稱** 每件作品開一個對話，儲存需求、選圖、源模型、切片與回饋，後續會話接著同一專案繼續。

角色可直接從 [角色提示詞](docs/ROLES.md) 複製。工作台通過文件和命令向 Codex 提供上下文，具體模型與工具能力取決於使用者當前安裝的 Codex 環境。

## 工作台裡有什麼

- 專案圖冊、真實 3D 模型預覽和設計版本。
- 可用 Spoolman 管理庫存、OpenSpoolMan 查閱槽位與歷史；Bambuddy 仍可作為設備遙測與列印整合來源。
- 靈感收藏、個人偏好和每輪選圖記錄。
- 跨專案配件清單、庫存與採購記錄。
- 已準備的列印包、材料映射、時間和用量，以及綁定具體任務的確認與回執。

首次安裝會顯示空專案和未連接設備。按安裝指南連接自己的設備後，頁面展示相應資料。

## 從需求到實物

描述用途與尺寸 → 選外形 → 確認三視圖 → 實際 CAD → 對照修改 → 配色與材料 → 切片比較 → 確認這一版列印 → 實物回饋。

新外形預設先選單張方案，再從同一方案的四套三視圖中選一套。小改動按影響範圍處理，已有決定接續使用。Text-to-CAD 提供建模和查看能力，尺寸、介面和實際裝配仍逐項檢查。完整步驟在 [工作流](Context/workflow.md)。

## 支援範圍

Mac 使用 macOS 14+，推薦 Apple Silicon。Windows 提供原生 PowerShell 安裝、命令列與瀏覽器工作台。通用工作台可獨立啟動，設備狀態與歷史依賴單獨安裝的 Bambuddy。Mac 自動發送助手對應 **X2D、中文 Bambu Studio 02.08.02.61、0.4 mm、單主料 AMS、左主噴嘴、紋理 PEI 單盤**。其他機型、軟體版本和多材料路線需要 Codex 按現場情況核對，詳見 [相容性與列印](docs/PRINTING.md)。

本倉庫提供工作台原始碼、原創流程文件、角色提示詞和空專案模板。第三方專案、模型權重、Bambu 軟體和外掛程式從各自官方來源獨立獲取。你自己的作品儲存在本機 `Project/`。第三方來源及職責見 [依賴說明](docs/DEPENDENCIES.md)。

## 開發與驗證

```bash
Runtime/venv/bin/python scripts/verify_onboarding.py
Runtime/venv/bin/python -m pytest Harness/tests -q
node --test Harness/tests/native-inspection.test.mjs
cd Harness/studio && npm run build
```

測試使用臨時工作區與合成設備。已安裝設備的只讀檢查需顯式設定 `PRINTLAB_LIVE_TEST=1`。發佈版驗證記錄見 [驗證說明](docs/VERIFICATION.md)。

## 使用許可與署名

PrintLab 原創原始碼和文件採用 **PolyForm Noncommercial 1.0.0**。允許在許可規定的非商業用途下使用、修改和再發布，再發布須附上許可及 `NOTICE.txt` 中的署名聲明。商業用途需要另行取得 AFangTeam 授權。

原作者為 **AFangTeam / 阿方（Eric）**，專案地址為 <https://github.com/AFangTeam/PrintLab>。許可全文見 [LICENSE.md](LICENSE.md)，署名要求見 [NOTICE.txt](NOTICE.txt)。獨立安裝的第三方軟體遵循各自的許可。

當前機型與驗證邊界見 [支援範圍](docs/MACHINE_SUPPORT.md)，發送與接續故障見 [排障指南](docs/TROUBLESHOOTING.md)。

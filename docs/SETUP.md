# 安裝 PrintLab

Windows 使用 [Windows 安裝與工作流](WINDOWS.md)。以下命令適用於 Mac。

## 準備

需要 macOS 14+、Python 3.11+、Node.js 22+（包含 npm）、Git 和可用的 Codex。首次安裝只需工作台依賴，建模與設備連接按下面步驟逐項接入。依賴原作者連結見 `DEPENDENCIES.md`。

## 安裝工作台

```bash
git clone https://github.com/AFangTeam/PrintLab.git
cd PrintLab
bash scripts/setup.sh
bash scripts/start.sh
```

瀏覽器開啟 <http://127.0.0.1:8018>。終端退出時服務結束。若 8018 已被佔用，先核對正在執行的服務身分，避免啟動兩個工作台寫同一份資料。獨立工作區可執行 `bash scripts/start.sh --port 18018`，訪問相應連接埠。`setup.sh` 在本倉庫建立 Python 虛擬環境，通過 PyPI/npm 下載工作台依賴並構建網頁，隨後生成空本機設定。

Python 版本不夠時，安裝 Python 3.11 或更新版，用絕對路徑執行 `PRINTLAB_PYTHON=/path/to/python3 bash scripts/setup.sh`。安裝完成可執行 `./Harness/bin/printlab doctor`。

## 讓 Codex 接手

觀眾的日常操作見 [交互指南](GETTING_STARTED.md)，Agent 的執行步驟及完成標準見 [Agent 接手指南](AGENT_START.md)。

在 Codex 開啟本倉庫，使用 README 中的接手提示詞。首次補充 `Context/profile.md` 中的用途和偏好，選擇當前可用的 Codex 模型。模型偏好寫入 `Context/agent-policy.json`。角色提示詞見 `ROLES.md`。

建立空專案的示例命令如下。

```bash
./Harness/bin/printlab new '我的第一件作品' --kind functional --brief '填寫用途、尺寸和完成標準'
./Harness/bin/printlab context P001
```

## 選擇設備和庫存來源

已在使用 Spoolman 和 OpenSpoolMan 時，可以沿用它們做庫存管理與槽位查閱。按 [連接指南](CONNECTIONS.md) 設定來源；以下步驟只適用於選擇 Bambuddy 的工作區。

### 連接 Bambuddy 和印表機

開始前完成 [首次設定訪談](FIRST_RUN.md)。

獨立安裝、URL、只讀權限與介面驗收步驟見 [Bambuddy 設定](BAMBUDDY_SETUP.md)。

1. 使用者從 Bambuddy 原專案獨立安裝，按上游說明執行服務並添加自己的印表機。它管理設備連接、庫存和歷史。
2. 在 Bambuddy 設定中建立只讀 API key，讀取其印表機 ID。寫入 `Runtime/private/bambuddy.json` 的 `read_api_key`，保持文件權限 600。需要實際發送時，才設定具有相應權限的 `write_api_key`。
3. 編輯 `Runtime/config.json`，填寫 `bambuddy_url` 和 `printer_id`。預設 URL 是 `http://127.0.0.1:8017`，應按自己實際安裝的地址調整。
4. 更新 `Library/Devices/X2D/device.json`，核實型號、噴嘴、板型、AMS/外掛以及 FTS 情況。該目錄沿用首版 X2D 的設備卡路徑，填寫內容必須對應自己的機器。
5. 執行 `./Harness/bin/printlab status` 和 `./Harness/bin/printlab materials`，確認設備身分、即時狀態和材料映射。把核驗結果寫入 `Library/Devices/X2D/installed.md`。

以上下載、安裝、設定檢查和故障修復可以由具備本機終端能力的 Agent 執行。登入、密鑰授權、macOS 權限選擇和實體裝料由使用者在實際介面或設備上完成，再讓 Agent 讀取結果繼續。

API key 只儲存在本機受限文件中，填寫時不要把真實 key 貼進公開 issue 或執行日誌。PrintLab 通過 HTTP API 訪問獨立執行的 Bambuddy，相關資料由使用者本機管理。

## 安裝建模和切片工具

- **Text-to-CAD** 從原專案的安裝指南獨立安裝 Codex 外掛程式。先用其當前幫助驗證建模、匯出和 CAD 查看器，再開始具體作品。`Harness/bin/text2cad` 會呼叫已安裝的 `cad` 或 `cadgen`，也可用 `PRINTLAB_CAD_COMMAND` 指定可執行文件。
- **CadQuery 匯出鏈** 如果需要執行 PrintLab 的 `build --engine cadquery`，在本機虛擬環境獨立安裝 `cadquery`、`trimesh`、`numpy`、`pillow`。命令為 `Runtime/venv/bin/python -m pip install cadquery trimesh numpy pillow`，實際版本儲存到自己專案的工具記錄。
- **Blender** 從官網安裝，`Runtime/config.json` 中的 `blender_path` 預設指向 `/Applications/Blender.app/Contents/MacOS/Blender`。
- **Bambu Studio** 從官方來源安裝，登入和連接自己的設備。`slicer_path` 預設指向 `/Applications/BambuStudio.app/Contents/MacOS/BambuStudio`。切片設定從這份本機安裝讀取。

具體路徑、設定解析和離線切片驗收見 [Studio 安裝指南](STUDIO_SETUP.md)。

各工具都準備好後，執行 `doctor`，讓 Codex 在臨時專案中驗證真實尺寸、單位、匯出和預覽。首版當前 build 引擎為 CadQuery/Blender，Text-to-CAD 生成的 STEP 可以通過同版本 CadQuery 橋接匯出，須保留源腳本和輸入。

## 可選 Mac 視窗

安裝 Xcode Command Line Tools 後，執行 `zsh Harness/macos/build.sh`，得到 `Runtime/macos-build/PrintLab.app`。把生成的應用拖入自己的應用目錄。視窗使用本機 8018 工作台，先保持 `scripts/start.sh` 執行。移動工作區後重新構建，應用會記錄實際路徑。

## 首次列印

按 `PRINTING.md` 逐項驗證。工作台發送助手需要獨立構建與使用者授予輔助功能、螢幕讀取權限。`studio_printer_name` 填寫自己 Bambu Studio 中的準確設備名稱，發送時還會檢查序列號符合。

## 更新與備份

完整更新、驗證恢復與回退步驟見 [更新指南](UPGRADING.md)。

更新前儲存本機專案與設定。`python3 Harness/backup.py backup --help` 查看當前備份參數，備份含私人設定，儲存在自己的受限目錄。Git 更新原始碼後重跑 `setup.sh`，初始化會保留已有設定和資料。第三方工具升級後，重新核對介面和切片行為。

連接模式與手機/電腦/Agent 的具體路徑見 [連接與控制指南](CONNECTIONS.md)。

Text-to-CAD 的固定版本、Mac/Windows 安裝命令、宿主接入和最小建模驗收見 [CAD 安裝指南](CAD_SETUP.md)。

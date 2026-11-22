# 獨立安裝 Text-to-CAD

Text-to-CAD 草稿交由 SolidCraft 進行 AI／人工精修的 MCP 操作，見 [SolidCraft MCP 使用指引](SOLIDCRAFT_MCP.md)。

PrintLab 不附帶 Text-to-CAD 原始碼、外掛程式或模型。其官方新版本使用 `cad`；作者原工作台的 0.8.2 使用過 `cadgen`，不要混用命令。以下固定 **cad-server 0.11.9**，從 PyPI 獨立獲取。該版本的宿主安裝行為見 [上游安裝指南](https://github.com/earthtojake/text-to-cad/blob/main/docs/install.md)。

## 在工作台之外保留獨立工具環境

先完成 PrintLab 安裝。在倉庫根目錄執行：

Mac：

```bash
Runtime/venv/bin/python -m venv Runtime/third-party/cad-bootstrap
Runtime/third-party/cad-bootstrap/bin/python -m pip install uv==0.10.7
Runtime/third-party/cad-bootstrap/bin/python -m uv tool run --no-config --managed-python --python 3.14 --from cad-server==0.11.9 cad setup --only codex --dry-run
```

Windows PowerShell：

```powershell
Runtime/venv/Scripts/python.exe -m venv Runtime/third-party/cad-bootstrap
Runtime/third-party/cad-bootstrap/Scripts/python.exe -m pip install uv==0.10.7
Runtime/third-party/cad-bootstrap/Scripts/python.exe -m uv tool run --no-config --managed-python --python 3.14 --from cad-server==0.11.9 cad setup --only codex --dry-run
```

檢查計畫，確認操作的是希望設定的 Codex。執行同一條最後命令，移除 `--dry-run`，即可安裝；需要關閉遙測時加 `--no-telemetry`。不要對已有可用的個人外掛程式盲目升級：上游安裝器可能替換該宿主內的舊副本。按安裝器提示重啟宿主，再核實外掛程式和技能實際出現。未檢測到 Codex 時先處理宿主安裝，不能宣稱完成了外掛程式接入。

安裝後的共享入口在 Mac 為 `./Harness/bin/text2cad`，Windows 為 `powershell -NoProfile -ExecutionPolicy Bypass -File .\Harness\bin\text2cad.ps1`。兩者優先查找 `cad`，相容舊版 `cadgen`。PATH 尚未更新時，將 `PRINTLAB_CAD_COMMAND` 設定為安裝器報告的可執行文件完整路徑，再通過該入口執行 `--help`。路徑可以包含空格。

## 驗證順序

1. 用安裝生成的 `cad --help` 與 `cad doctor --check` 檢查命令和服務。若 PATH 未重新整理，使用安裝器報告的實際可執行路徑；PrintLab 的 `PRINTLAB_CAD_COMMAND` 可指定它。
2. 要求 Agent 在臨時目錄建立一個尺寸已知的簡單測試體，用 `cad run` 構建，檢查實體有效性、毫米尺寸和體積，並匯出 STEP/STL。隨後刪除臨時測試產物。命令存在不代表 CAD 內核已下載或能建模。
3. 在當前 Agent 宿主實際開啟 CAD 查看器，核對模型及後續修改是否同步。終端建模通過不能代替宿主查看器驗收。
4. 正式作品保留參數化源文件、輸入與版本。PrintLab 的原生 build 仍是 CadQuery/Blender；Text-to-CAD 的 STEP 橋接需要單獨準備 CadQuery 環境。幾何 3MF 不是可直接發送的已切片包。

## Agent 環境的啟動問題

如果提示沙箱不能自動啟動引擎，使用獲得相應權限的終端執行 `cad server` 並保持執行，再在同一安裝環境執行 `cad run`。不要反覆重裝外掛程式或停掉另一安裝的服務。`cad doctor --check` 用於只讀診斷；需要修復時先看具體錯誤。

本專案的 `scripts/verify_cad_install.py` 會獨立下載上述版本，在臨時狀態、緩存、啟動器目錄與連接埠執行真實建模/匯出，完成後關閉該測試服務；不安裝到你的 Agent 宿主，不連接印表機，不把測試模型打包分享。執行方式為工作台 Python 加此腳本路徑，診斷儲存在 `Runtime/verification/cad-install.log`。首次執行需下載 CAD 內核，耗時和空間明顯高於啟動空工作台。

# 獨立安裝與驗證 Bambu Studio

從拓竹官方獲取適合本機系統的安裝包。工作台自動發送助手當前符合中文 `02.08.02.61`，本次離線切片驗收也使用該版。其他版本需要重新核對設定和介面。[官方版本與下載](https://github.com/bambulab/BambuStudio/releases/tag/v02.08.02.61)

## 設定路徑

Mac 將官方應用安裝到自己的應用目錄。預設路徑為 `/Applications/BambuStudio.app/Contents/MacOS/BambuStudio`，設定目錄為應用內 `Contents/Resources/profiles`。

Windows 可使用官方安裝程序或便攜 ZIP。將 `Runtime/config.json` 的 `slicer_path` 設定為實際 `bambu-studio.exe`，`slicer_profiles_path` 設定為同一安裝的 `resources/profiles`。路徑中的空格可以保留，JSON 推薦使用正斜槓。

首次開啟 Studio，按自己的印表機選擇機型、噴嘴、耗材與列印板，並完成所選網路通道的連接。登入和網路外掛程式按官方介面提示處理。之後執行 `printlab doctor`，核對它找到的路徑。

## 完整設定與切片

官方設定包含繼承和模板引用。使用 PrintLab 自帶解析器，將實際安裝中的目標設定解析到自己的專案目錄，並儲存其來源校驗記錄。

```bash
Runtime/venv/bin/python Harness/resolve_bambu_profiles.py '實際官方設定.json' --output '專案設定輸出.json'
```

Windows 換用 `Runtime/venv/Scripts/python.exe`。分別解析機型、工藝和材料設定，保留 `.sources.json`，按真實設備修改必要的使用者工藝參數。執行 `printlab slice --help` 查看當前參數，再對已完成尺寸和幾何核查的專案試切片。

本版正式切片檢查面向 X2D。其他機型應先實現和驗證對應機型檢查，再接入自動流程。切片包生成後，核對機型、噴嘴、板型、材料映射、估時和真實 G-code。具體發送步驟見列印指南。[列印與授權](PRINTING.md)

## 維護者離線驗收

`Runtime/venv/bin/python scripts/verify_studio_install.py` 會從官方 Release 獨立下載固定包並核對 SHA-256。Mac 只讀掛載 DMG，Windows 解壓官方便攜 ZIP。應用使用臨時資料目錄，解析 X2D 官方設定，切片臨時測試幾何，驗證真實 3MF、載料升溫程式碼和公開檢查器結果，完成後清理。

該測試使用 X2D 0.4 mm、PLA、紋理 PEI 和單盤。測試結果寫入 `Runtime/verification/studio-install.json`，日誌為 `studio-slicing.log`。切片過程在本機離線進行，Studio 登入、網路外掛程式、真實設備選擇與發送助手權限仍需在使用者環境核驗。

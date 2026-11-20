# PrintLab Harness

統一命令為倉庫根目錄的 `./Harness/bin/printlab`。首次安裝見 `../docs/SETUP.md`。

```bash
./Harness/bin/printlab --help
./Harness/bin/printlab doctor
./Harness/bin/printlab context
./Harness/bin/printlab new '作品名稱' --kind functional --brief '用途、尺寸與完成標準'
./Harness/bin/printlab context P001
```

使用當前子命令幫助查看參數。原始碼包含專案、版本、建模、切片、設計選擇、正式 3MF、材料、購物清單、歷史、待列印、官方發送和實物覆盤。

FastAPI 服務由 `scripts/start.sh` 啟動，React 頁面由 `studio/` 構建。資料根目錄預設當前倉庫，Python 介面可用 `PRINTLAB_ROOT` 指定隔離工作區。網頁靜態資源來自該工作區的 `Harness/studio/dist`。

`Runtime/config.json` 存本機工具和服務路徑，`Runtime/private/` 存憑據。獨立第三方程序從原作者處安裝，來源見 `../docs/DEPENDENCIES.md`。歷史原生髮送客戶端在首版中不可用，當前列印路線見 `../docs/PRINTING.md`。

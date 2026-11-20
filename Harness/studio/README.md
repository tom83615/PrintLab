# PrintLab 網頁工作台

React + Vite，讀取本機 FastAPI 資料。生產啟動使用倉庫根目錄 `scripts/start.sh`。

```bash
npm ci
npm run build
npm run dev
```

開發服務器將 `/api` 轉發到本機 8018。新專案、庫存與具體作品繼續通過 Codex 和 PrintLab 共享命令儲存，待列印頁面提供綁定任務的確認流程。

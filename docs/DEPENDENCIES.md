# 第三方工具與獨立安裝

PrintLab 發佈包保留原創工作台、流程、適配介面與項目模板。下面的程序、外掛程式、原始碼、權重和技能由使用者從原作者渠道下載，各自遵守原許可。

| 項目 | 在流程中的作用 | 獲取與版本說明 |
| --- | --- | --- |
| [Bambuddy](https://github.com/maziggy/bambuddy) | 設備、材料庫存、佇列與已捕獲歷史 | 按原專案安裝指南獨立執行。PrintLab 本機適配基線為 v1.2.5.7，當前上游介面需重新驗證。通過獨立 HTTP API 連接。 |
| [Text-to-CAD](https://github.com/earthtojake/text-to-cad) | Codex 建模、模型查看、匯出與製造檢查 | 按原專案 `docs/install.md` 安裝。本機歷史驗證基線為 0.8.2，當前上游入口已使用 `cad`，以實際 `--help` 為準。 |
| [Bambu Studio](https://github.com/bambulab/BambuStudio) | 正式工程、切片與官方發送 | 從拓竹官方獲取應用及其外掛程式。首版發送助手的本機驗證版本為 02.08.02.61。 |
| [Blender](https://www.blender.org/download/) | 有機外形、同源預覽和動畫視圖 | 從官網安裝。原工作流使用 Blender 4.5 系列，當前安裝需檢查匯出介面。 |
| [CadQuery](https://github.com/CadQuery/cadquery) | 參數化結構和 STEP 橋接 | 在使用者虛擬環境中從 PyPI 安裝。 |
| [build123d](https://github.com/gumyr/build123d) | Text-to-CAD 的參數化幾何能力 | 按 Text-to-CAD 原專案環境要求獨立取得。 |
| [bambu-printer-mcp](https://github.com/DMontgomery40/bambu-printer-mcp) | 獨立離線切片檢查；歷史原生髮送研究來源 | 安裝腳本從 npm 獨立下載固定 1.1.33，通過公開 MCP inspect_print_file 呼叫，不提供印表機憑據，不匯入上游內部模塊。歷史原生髮送仍不可用。 |
| [Hunyuan3D-Swift](https://github.com/ZimengXiong/Hunyuan3D-Swift) / [Hunyuan3D-2](https://github.com/Tencent-Hunyuan/Hunyuan3D-2) | 可選圖生外形候選 | 程式碼和模型權重分別從原作者取得並檢查許可。`image3d` 保留本機適配原始碼，需要自行準備對應隔離環境和來源清單。 |

## 許可歸屬

核對過的上游許可包括 Text-to-CAD 的 MIT、Bambuddy 的 AGPL-3.0 和 bambu-printer-mcp 的 GPL-2.0。使用者應以自己下載版本的 LICENSE 為準。上游的許可與署名繼續適用，PrintLab 的非商用許可只覆蓋 PrintLab 原創部分。

舊原生客戶端通過進程內載入 `bambu-printer-mcp` 內部模塊工作。首版發佈包移除了該客戶端、上游補丁和相關執行環境，保留本專案的歷史任務讀回與獨立檢查邏輯。首版 `bambu_native` 發送返回明確的不可用原因，官方 Studio 工作流在 `PRINTING.md` 中說明。

## 工作台軟體依賴

Python 包在 `Harness/pyproject.toml` 聲明。網頁依賴在 `Harness/studio/package.json` 與 `package-lock.json` 聲明，包括 React、Three.js、Lucide、react-markdown 與 Vite。安裝時由包管理器從 PyPI/npm 獲取，下載的 `node_modules`、虛擬環境和構建產物儲存在使用者本機。

## 升級方法

先閱讀原專案新版本說明，在獨立目錄安裝，驗證 CLI/MCP、模型尺寸、匯出和設備只讀介面，再更新本機設定。儲存實際版本和驗證結果，已確認的列印任務繼續綁定其原文件和參數。

## 獨立檢查器與版本鎖

工作台安裝腳本會執行 `scripts/install_inspector.py`，從 npm 獨立獲取檢查器及依賴，儲存於被 Git 忽略的 `Runtime/third-party/bambu-inspector`。倉庫僅儲存下載清單與完整性校驗，不分發第三方原始碼、外掛程式或模型。檢查器保留其 GPL-2.0 許可。需要單獨重裝時使用工作台虛擬環境的 Python 執行該腳本。

Python 依賴使用 `scripts/requirements.lock` 的版本和 SHA-256；前端與檢查器分別使用自己的 package-lock.json。升級時更新鎖文件並重跑跨平臺驗收，不能直接改為 latest。

檢查器下載清單將 `bambu-js` 的間接依賴 `basic-ftp` 固定為 6.2.6，清除舊版目錄解析漏洞。該版本與檢查器已有的直接依賴一致，檢查器主版本仍為 1.1.33。此組合驗證範圍為本機 `inspect_print_file`，包括真實切片包檢查。[上游漏洞記錄](https://github.com/advisories/GHSA-c475-qrg2-pj4r)

Text-to-CAD 的固定版本、Mac/Windows 安裝命令、宿主接入和最小建模驗收見 [CAD 安裝指南](CAD_SETUP.md)。

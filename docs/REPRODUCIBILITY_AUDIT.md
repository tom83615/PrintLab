# 復刻體驗審查（2026-11-12）

審查原始碼：2491037bbff7c4d037e3e7b1c4c86e37e0e3aa72，版本 0.2.0。本文記錄調查和待修復項，不表示問題已修復、重新完成虛擬機驗收或已發佈新版。

## 官方資料帶來的發佈要求

- [Agent Skills 規範](https://agentskills.io/specification)：獨立技能以帶 name、description 的 SKILL.md 為入口；相容性、腳本、參考資料和資源應可找到。AGENTS.md 是倉庫協作入口，不能代替可獨立分發的 Skill。
- [Skill 腳本指南](https://agentskills.io/skill-creation/using-scripts)：聲明前提、固定工具版本、使用相對路徑，把複雜操作收斂到可測試腳本。第三方工具可以引用獨立安裝，不必複製到本倉庫。
- [GitHub 倉庫建議](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories)：README、許可、貢獻與問題報告入口共同構成使用體驗。
- [GitHub Release](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)：發佈物應對應明確 tag。本專案應額外驗收實際下載的發佈 ZIP，不能僅驗收原始碼 checkout。
- [GitHub 託管執行器](https://docs.github.com/en/actions/concepts/runners/github-hosted-runners)：新的 VM 仍預裝工具。因此雲端綠色結果不等於裸機前提齊全，更不證明印表機硬體和桌面發送權限可用。

## 本倉庫核驗結果

| 優先級 | 當前事實與證據 | 應完成的修改及驗收 |
| --- | --- | --- |
| P0 | prepared.py 的 check 和 official.py 的 submit 預設呼叫 native.run_client；native.py 要求發佈包沒有的 Harness/native-client.mjs | 補上獨立安裝、可驗證的檢查通路；缺依賴時提前明確禁用發送。必須在不注入成功 inspector 的情況下走真實檢查。不能跳過安全檢查解堵 |
| P0 | verify_browser.py 只訪問空待列印列表和其他頁面；verify_onboarding.py 只驗收空工作區、專案、交接與 API | 覆蓋已準備任務、檢查、按鈕、後臺預約與單次發送；僅模擬硬體與 GUI 邊界，加入未設定、版本不符、重複點選、未知回執等失敗場景 |
| P0 | desktop.yml 在 checkout 原始碼上安裝；獨立 CAD、Bambuddy、Studio 安裝沒有進入完整驗收 | 從候選發佈 ZIP 在新目錄安裝，按文件走設定；區分真實依賴、模擬設備和實機待驗證，儲存錯誤、修復與結果 |
| P1 | README、AGENT_START、角色提示詞齊全，但倉庫沒有 SKILL.md | 提供原創 PrintLab Skill 入口，說明何時使用、實際倉庫路徑、初始化與接續步驟、列印授權邊界；獨立安裝後驗證能發現和觸發 |
| P1 | SETUP 將設備填寫集中於步驟4；缺少結構化首次訪談 | 先問作業系統、Agent 能力、機型/韌體、噴嘴/板型、AMS/外掛、材料與連接方式；未知保持未知。讓設計小組讀取同一設備檔案 |
| P1 | Text-to-CAD 僅有上游安裝連結和歷史版本；Python 使用範圍依賴，只有前端有 package-lock.json | 提供已驗證版本清單、對應安裝步驟及最小匯出驗收；鎖定可復現的 Python 依賴，仍允許有記錄的升級 |
| P1 | doctor 與文件已承認工具路徑存在不足以證明可用 | 將版本、CLI 最小呼叫、設定、只讀連通性和發送能力分開診斷；輸出具體失敗原因、修復命令及複驗結果，不列印密鑰 |
| P1 | PRINTING 中官方介面、Mac助手、佇列並列；Windows 文件限制與主列印表述不夠一致 | 建立系統 × 機型 × 入口 × 驗證級別矩陣；明確 ChatGPT 需要本機執行/桌面能力，手機網頁、Handy、Studio 是不同入口；分別解釋雲與 LAN 路線的條件 |
| P2 | 有許可、署名、更新提示；無問題表單和貢獻說明 | 增加收集系統、版本、復現步驟、脫敏診斷的模板；說明備份、升級失敗回退及使用者資料保留 |

## 新版驗收完成標準

1. 先產出候選 ZIP 和 SHA-256，VM 從該包開始，使用 README 命令，不使用維護者的私人路徑和緩存環境。
2. 工作台啟動、重複安裝保留設定、中文空格路徑、實際網頁操作及跨進程接續通過。
3. 外部工具獨立安裝並記錄版本；實際生成臨時測試幾何和匯出，測試生成物不作為模型資源打包分享。
4. 真實檢查鏈不靠假的成功返回；硬體/GUI模擬邊界明確，發一次、未知不重發等條件必須保留。
5. 每項記錄已驗證、模擬驗證、未驗證、失敗。Windows Server VM 不寫成 Windows 10/11 實機驗收。
6. 印表機連接、真實 Studio 操作、出料與成品另行現場核驗；安裝/發佈授權不當作實體列印授權。
7. 發佈 tag、ZIP、驗證提交和文件一致；下載讀回後核對 SHA-256。未完成步驟不能寫進已驗證範圍。

建議先修 P0，再完成 Skill 與首次設定；不以增加文件數量代替打通核心流程。

## 修復進展

- `942917a`：公開上游 1.1.33 獨立安裝與 MCP 文件檢查已替換缺失客戶端的 inspect 路徑；原生直接發送仍不提供。Python 和檢查器下載依賴已鎖定，新增標準 Skill 與首次設備訪談。
- `dfea729`：真實文件檢查接入工作台 API、批准、官方預約和模擬介面單次發送；新增從 git archive 候選 ZIP 全新安裝驗收及連接方式文件。
- 本機從 dfea729 ZIP 全新安裝通過，ZIP SHA-256 為 `9ff491b7f423733e4105adad2406eafbd33097b1e34b871b4e28b2798dfe6537`。完整軟體測試保留設備/GUI模擬邊界。
- 新增固定版 Text-to-CAD 隔離安裝/真實建模/STEP/STL 匯出驗收，首次執行發現 Agent 環境禁止自動拉起引擎，改為顯式啟動獲准的獨立服務。狀態、緩存、啟動器及進程通信目錄均單獨設定。

- `f0f8d87` 在 Mac、Windows Server 2022、Windows Server 2025 的全新安裝、ZIP 安裝、真實 CAD 建模和匯出檢查全部通過。[雲端記錄](https://github.com/AFangTeam/PrintLab/actions/runs/43092718752)
- `644b6a6` 增加真實 Chromium 待列印按鈕測試，本機已驗證檢查、清板、提交和重新整理後保持單次發送記錄。設備與桌面發送邊界使用模擬對象，測試圖片明確標為合成資料。後續 `d3ac171` 的 Mac 與 Windows Server 2025 瀏覽器步驟通過，但最新候選整體迴歸尚未完成。
- 獨立 Bambuddy `v1.2.5.7` 服務端在全新本機虛擬環境安裝通過，真實 HTTP 客戶端驗證六個只讀介面，臨時 key 已撤銷。已加入可複用安裝驗收腳本、設定指南和更新回退說明。
- `50f7177` 增加官方 Studio 獨立下載、SHA-256、真實切片和公開文件檢查驗收。本機固定版 `02.08.02.61` 已完成該檢查，測試生成物保留在臨時目錄並清理。
- 雲端出現過 Mac 進程組清理權限異常。清理程式碼現在核對進程組是否已經退出，仍有存活成員時報告失敗。增加三種確定性迴歸情況，本機完整測試為 377 通過、8 跳過。
- Windows Server 2022 的 Bambuddy 安裝和六個介面檢查通過後，測試清理因 `bambuddy.db-shm` 被子進程佔用失敗。改為停止完整測試進程樹，並在臨時資料清理完成後才生成成功報告。本機複驗通過，Windows 修復待雲端讀回。[發現問題的執行](https://github.com/AFangTeam/PrintLab/actions/runs/43094517244)

最終迴歸已於 2026-11-12 通過。`5416518` 的 PR 合併預覽在三臺雲端虛擬機完成全部驗收，Windows 的 SQLite 清理失敗通過有超時限制的重試修復。安裝、CAD、Bambuddy、官方 Studio 切片和瀏覽器報告均已下載核對。[完整記錄](VERIFICATION.md)

CAD 宿主外掛程式與查看器、GUI 登入與權限、硬體連接及實物列印需使用者現場驗證。具體系統和驗證範圍見上述記錄。

---
name: makerworld-upload
description: 使用瀏覽器將本機 STL、CAD 或 Bambu Studio 3MF 上傳到 MakerWorld，填寫模型資訊與列印設定，儲存草稿或依使用者授權發佈。適用於 PrintLab 和其他本機模型。
---

# MakerWorld 瀏覽器上傳

## 準備 Bambu Studio 列印設定

確認要上傳的確切模型版本、檔案和圖片。使用現成的標題、描述、分類、標籤和實物照片，缺少文案時可依可驗證的資料起草。核對原創、改作或轉載的來源和授權，保留作者與來源連結。PrintLab 專案依其 AGENTS.md 核對版本與來源。只選取使用者指定或同意上傳的檔案。

- 同一模型版本須準備兩份獨立的 Bambu Studio 專案 3MF，一份選用 PLA，另一份選用 PETG。各自套用對應材料設定並切片，檔名與 MakerWorld 列印設定標題標明材料與機型。只有 STL／CAD 或一般 3MF 時，先匯入 Bambu Studio 準備這兩份檔案。
- 依 **A1 mini → A1 → H2S** 的順序選機型。從 A1 mini 開始，在 Bambu Studio 檢查該機型的一個列印盤能否容納全部零件與切片所需的支撐、裙邊等，並確認 PLA 和 PETG 設定均可完成切片。兩份檔案都以第一個符合條件的機型儲存。若 H2S 也無法在單盤完成，回報卡住的零件或排版限制，等使用者決定如何調整。

## 上傳與讀回

1. 使用 Codex 瀏覽器控制工具，優先接續使用者選定或已登入的 MakerWorld 分頁。從 https://makerworld.com/ 的 Upload 進入。登入、雙重驗證或 CAPTCHA 交還使用者在網站完成。透過頁面控制項及受支援的檔案選擇器操作，讓網站管理登入與上傳。
2. 在可見的上傳精靈使用 Bambu Studio 3MF 路線，將 PLA 和 PETG 兩份檔案分別加入同一模型的列印設定。依 Print Profile Information 實際要求提供標題、描述和對應設定的實物列印照片。以上傳成功提示、檔名和縮圖確認兩份檔案各自被接受；如工具無法操作檔案選擇器，請使用者選取指定檔案後接續。
3. 在 Model Information 核對標題、分類、描述、封面、圖庫、標籤、模型來源、授權和可見性。改作或轉載時填入已核實的來源。另核對兩份列印設定各自的相容機型、照片和可見性。模型與列印設定的封面及可見性可能各自獨立，分別讀回。表單欄位及必填條件以當前頁面為準。缺少實物照或授權資料時標為待補，實物照使用真實照片。
4. 使用者只要求上傳或準備時，使用可見的 Save Draft，從草稿列表或重開草稿確認 PLA 和 PETG 兩份設定及各自顯示的機型，回報草稿連結（如有）與待補項目。只有使用者已明確授權發佈這個版本、授權條款和公開範圍時才送出 Publish。送出後讀回平台狀態與連結，區分草稿、審核中與已發佈。若送出逾時或結果不明，先到草稿或創作者頁對帳，再決定是否重試。

上傳分流與欄位參考 [ModelPrep 的 MakerWorld web flow](https://github.com/iamdjem/modelprep/blob/main/backend/docs/makerworld-web-flow.md) 的 Two upload paths 和 Draft payload。執行時以 MakerWorld 網頁介面為準。

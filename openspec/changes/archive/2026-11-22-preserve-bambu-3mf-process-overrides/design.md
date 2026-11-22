# Design

## Context

Studio CLI 會以切片工藝檔的圖樣產生 G-code。Studio 開啟專案時也使用 `different_settings_to_system` 判斷哪些工藝設定應保留。

## Goals / Non-Goals

修正一般 STL 和幾何 3MF 切片，涵蓋明確設定的稀疏填充圖樣。既有切片、獨立的可編輯專案匯出及 P009 專用的 Studio 專案輸入沿用各自的流程。

## Decisions

- 交給切片器前，在任務的工藝檔副本補登記 `sparse_infill_pattern`。第一項存工藝差異，後面依序為各材料和機器。合併現有工藝差異，並保留來源雜湊。
- 在現有離線檢查讀取封裝時比對專案值、工藝差異及 G-code 設定。沿用切片失敗的記錄方式。此檢查使用切片器原生輸出，避免修改已生成的切片包。

## Risks / Trade-offs

切片器若輸出不同格式，任務會顯示檢查失敗。保留診斷與輸出供調查。

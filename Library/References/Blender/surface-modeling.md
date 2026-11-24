# Blender 表面建模與列印

以有定位孔的握把為例，先用正、側視圖控制掌心隆起與指槽深度，把孔心和安裝平面設為獨立基準。外形調整後，從這些基準重新量孔距、孔徑和裝配間隙。

## 從外形到殼體

1. 用少量面建立控制網格，讓邊環沿著握把輪廓與指槽走向排列。在 Subdivision Surface 選 Catmull-Clark，從低細分層級檢查側面剪影。需要保住稜線時，在轉折附近加支撐邊環或設定邊摺痕。光滑著色只改變表面明暗，列印輪廓取決於實際網格。[Blender 手冊：細分曲面](https://docs.blender.org/manual/en/4.5/modeling/modifiers/generate/subdivision_surface.html)
2. 若選定的是外殼外形，先確認面法線朝外並套用物件縮放，再在細分後加 Solidify，令厚度向內延伸。以剖面檢查指槽底、急彎與孔邊，這些位置可能比設定值薄或出現自交。[Blender 手冊：殼體厚度](https://docs.blender.org/manual/en/5.0/modeling/modifiers/generate/solidify.html)

## 接入 PrintLab

- 使用工作台的 Blender 建置器時，`model.py` 的 `build(params)` 回傳要匯出的 Blender 物件或物件列表，尺寸參數放在 `params.json`。腳本生成的 `model.blend` 會寫在腳本旁；若要手動精修，先另存新版本並登記哪個檔案是正式來源。
- 工作台腳本以米建立 Blender 幾何，匯出 STL 時乘以 1000。例如孔距 40 mm 在腳本中應為 0.040 m；匯入切片器後量同一對孔心，應讀到 40 mm。GLB 預覽沿用米制。
- 用套用修改器後的匯出網格檢查外形和尺寸。每個預計獨立列印的零件都要查開放邊、自交、法線方向和最薄處，再看切片逐層預覽，確認孔口、薄壁與內腔成形。檢查結果記入專案的 `Review/cad-master-design.md`。

## 依工作階段選用的外部資源

- **草模與輪廓比對**：calebrisc 的 `blender-modeler`（MIT）以同一份可編輯腳本逐版修形，配合尺寸檢查與固定視角。可在使用者選定 Blender 後，用其中的正交視圖比對外形，再用透視圖查轉角。作者列出 Blender 4.2 以上，開發與測試版本為 5.2。[作者倉庫與使用說明](https://github.com/calebrisc/blender-modeler)
- **局部曲面精修**：matty 的 `blender-mesh-topology` 涵蓋控制網格、邊流疏密轉換與曲面銜接。握把接到底座時，可參考其曲面過渡方法，檢查接縫附近的剪影與高光是否突然折斷。[作者的技能目錄](https://github.com/matty/agent-skills#general-3d-in-blender-any-engine)
- **選擇建模手法**：Blender Studio 的製作指南整理了雕刻、重新拓撲、細分與倒角的使用時機。角色或仿生件可先建立大形，再沿輪廓重整網格；硬殼可用摺痕調整邊緣銳度。[Blender Studio 建模指南](https://studio.blender.org/tools/artist-guide/asset-creation/modeling)
- **切片前檢查**：用 3D Print Toolbox 找出非流形邊、自交與可能過薄的面，再依專案的壁厚目標和實際切片判讀。[Blender Extensions 與工具說明](https://extensions.blender.org/add-ons/print3d-toolbox/)

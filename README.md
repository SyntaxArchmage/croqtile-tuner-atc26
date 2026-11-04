# CroqTile · ATC'26

**A Novel AI-Native GPU Kernel Programming Language for Autonomous Kernel Tuning**

Shanghai Enflame Intelligence & Shanghai Jiao Tong University · ATC'26, Hong Kong, November 2026.

打开：https://syntaxarchmage.github.io/croqtile-tuner-atc26/

- 两条 co-design 轴 · syntax ⇄ context（第 8–14 页）、compiler ⇄ harness（第 15–16 页）
- 五个 action · named shapes · parallel · event · tma · mma
- tuning loop、语言全貌、结论

幻灯片按 ← → 翻页，F 全屏，S 打开讲者备注。第 9–13 页的代码卡可以点 tab 切换 CroqTile / Triton / TileLang / CuTe / CUDA 的实现。

## Background 图表

第 2 页的两张图由 matplotlib 生成，数据与生成脚本在 `figures/`：

```bash
python3 figures/make_background_figures.py   # -> figures/out/*.svg + *.png
python3 figures/build_background_slide.py    # 把 SVG 内嵌回 index.html
```

- `figures/data/corpus-trend.json` · 276 篇论文的逐年计数
- `figures/data/dsl-timeline.json` · 46 个 DSL 的首次发布年份
- `figures/data/dsl-tiers.json` · 每个 DSL 在抽象层级上的定性定位（含编号）

`build_background_slide.py` 会整段重写第 2 页的 `<section>`，所以改文案/备注请同步改脚本；只改 CSS 不受影响。

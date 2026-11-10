# CroqTile · ATC'26

**A Novel AI-Native GPU Kernel Programming Language for Autonomous Kernel Tuning**

Shanghai Enflame Intelligence & Shanghai Jiao Tong University · ATC'26, Hong Kong, November 2026.

打开：https://syntaxarchmage.github.io/croqtile-tuner-atc26/

- 两条 co-design 轴 · syntax ⇄ context（第 11–14 页）、compiler ⇄ harness（第 15–16 页）
- 五个 action · named shapes · parallel · event · tma · mma
- tuning loop、语言全貌、结论

幻灯片按 ← → 翻页，F 全屏，S 打开讲者备注。第 12–13 页可通过代码卡 tab 查看其他语言的对应实现。

## Background 图表

第 2 页的两张图由 matplotlib 生成，数据与生成脚本在 `figures/`：

```bash
python3 figures/make_background_figures.py   # -> figures/out/*.svg + *.png
python3 figures/build_background_slide.py    # 把 SVG 内嵌回 index.html
```

- `figures/data/corpus-trend.json` · 276 篇论文的逐年计数
- `figures/data/dsl-timeline.json` · 46 个 DSL 的首次发布年份
- `figures/data/dsl-tiers.json` · 每个 DSL 在抽象层级上的定性定位（含编号）

`build_background_slide.py` 只更新第 2 页的图表，保留文案和讲者备注。

## Ways of tuning kernels（第 5–7 页）

第 5–7 页把 tuning 拆成 bottleneck / search / compiler 三种方式，第 6 页带搜索空间图：

```bash
python3 figures/make_expert_loop.py      # -> figures/out/expert-loop.svg（第 5 页概念图）
python3 figures/make_tuning_figures.py   # -> figures/out/search-space.svg/png
python3 figures/build_tuning_slides.py   # 更新第 5–6 页图表，保留文案/备注
```

第 5 页的 loop 图是内联 SVG（配色/字体取自页面的 CSS 变量），第 6 页的搜索空间图由 matplotlib 生成。

## 第 4 页 GFLOPs 图

```bash
python3 figures/make_operator_figure.py   # -> figures/out/operator-gflops.svg（横向条形图）
```

生成后需把 SVG 重新内嵌到第 4 页的 `<img src>`（这一页是手写 section）。

## Presentation polish

The design narrative follows syntax–context co-design and compiler–harness
co-design. Slide 14 connects compile success to fewer coupled syntax sites and
symbolic inference in the type system/compiler. Visible bullets support the
talk; `slides-craft` is a visual reference, not a source for replacement copy.

Original paper figures, EBNF and compiler diagnostics are preserved. Code cards
use a muted teal palette; the HTML comparison bars use proportional widths and
outside value labels. Presentation styles are authored in `polish.css`.
Rebuild the deliverables with:

```bash
python3 tools/export_pptx.py
```

The exporter embeds styles into the standalone `index.html` and
`dist/slides.html`, then regenerates `dist/slides.pptx`, `dist/slides.pdf` and
`dist/preview/all-slides.jpg`. To refresh only the HTML, run
`python3 tools/prepare_slides.py`.

Requires Playwright/Chromium, python-pptx, CairoSVG, PyMuPDF, Pillow and
Lato and Liberation Mono fonts. PowerPoint preserves editable
text, syntax colors, rendered line breaks, bullets and speaker notes; figures
are embedded at twice their displayed resolution. PDF uses the browser layout.
The previous PowerPoint postprocessing step is no longer necessary.

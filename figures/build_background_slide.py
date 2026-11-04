#!/usr/bin/env python3
"""Rebuild the Background slide in index.html from the generated figures.

Reads the matplotlib SVGs in figures/out/, embeds them as base64, and writes
the new Background section: the DSL line chart on top, then a trend block and
the numbered papers chart side by side, question inline with the H2.

Run after make_background_figures.py:
    python3 figures/build_background_slide.py
"""

from __future__ import annotations

import base64
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "out"
INDEX = ROOT / "index.html"


def data_uri(path: pathlib.Path) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(
        path.read_bytes()).decode("ascii")


def main() -> None:
    line_uri = data_uri(OUT / "papers-line.svg")
    dsl_uri = data_uri(OUT / "dsl-line.svg")

    section = f'''<section class="gs bg-slide">
  <div class="slide-header"><span class="rh-page"></span><span class="rh-mid">A Novel AI-Native GPU Kernel PL &middot; ATC&rsquo;26</span></div>

  <div class="bg-head">
    <h2>Background</h2>
    <p class="bg-question"><span class="q-tag">Question</span>Model architectures converged on encoder-only, decoder-only and diffusion, so why is operator work growing?</p>
  </div>

  <div class="bg-stack">
    <figure class="fig">
      <img src="{dsl_uri}" alt="Line chart of DSLs first released per year, 2013 to 2026, with each year's DSL names stacked at the marker; the crowded 2025 and 2026 columns list their names below the marker.">
    </figure>

    <div class="bg-bottom">
      <div class="trend-block">
        <div class="trend-hero">
          <span class="trend-num">22<span class="trend-dim">/46</span></span>
          <span class="trend-cap">DSLs in 2025&ndash;26</span>
        </div>
        <p class="trend-line"><b>&uarr; abstraction</b> intrinsics &rarr; tile DSL &rarr; agent</p>
        <p class="trend-line"><b>&rarr; efficiency</b> templates &rarr; tensor &rarr; agent-native</p>
      </div>
      <figure class="fig">
        <img src="{line_uri}" alt="Line chart of operator-optimization papers per year, 2013 to 2026, rising from 2 papers in 2013 to 81 in 2026.">
      </figure>
    </div>
    <p class="source-note"><strong>Source</strong> &middot; group survey corpus &middot; <strong>276</strong> papers &middot; <strong>46</strong> DSLs</p>
  </div>

  <aside class="notes">
    Two columns answer the question. On the left, operator-optimization papers by year in a 276-paper survey corpus: a handful a year through the 2010s, roughly a dozen through 2021, then twenty in 2022 and 2023, thirty-two in 2024, sixty-nine in 2025, and eighty-one in 2026 so far.

    On the right, the 46 operator-programming DSLs by first release year, with each year's names stacked at the marker. The line is flat through the 2010s — one or two DSLs a year — then climbs: five in 2022, three in 2024, and eleven each in 2025 and 2026. Twenty-two of the 46 landed in 2025–26 alone. The names are ordered by abstraction tier, from intrinsics and threads at the bottom to agent-native at the top; in the crowded 2025 and 2026 columns they run below the marker.

    The takeaway is the question this slide is built on. Model architectures converged: encoder-only, decoder-only, and diffusion cover nearly everything shipped. If the models are that few, why did operator effort go up, not down? It sounds backwards; it is the right question. The operator, not the model, is where the performance is won. That is the gap this talk targets.
  </aside>
</section>'''

    html = INDEX.read_text()
    i = html.index("<h2>Background</h2>")
    start = html.rfind("<section", 0, i)
    end = html.index("</section>", i) + len("</section>")
    html = html[:start] + section + html[end:]
    INDEX.write_text(html)
    print(f"rebuilt Background section ({len(section):,} chars)")


if __name__ == "__main__":
    main()

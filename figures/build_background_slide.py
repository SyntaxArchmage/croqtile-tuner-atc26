#!/usr/bin/env python3
"""Rebuild the Background slide in index.html from the generated figures.

Reads the matplotlib SVGs in figures/out/, embeds them as base64, and writes
the new two-column Background section: line chart + numbered DSL index on the
left, bubble chart on the right, question inline with the H2.

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
    bubble_uri = data_uri(OUT / "dsl-bubbles.svg")
    key = (OUT / "dsl-key.html").read_text().rstrip("\n")

    section = f'''<section class="gs bg-slide">
  <div class="slide-header"><span class="rh-page"></span><span class="rh-mid">A Novel AI-Native GPU Kernel PL &middot; ATC&rsquo;26</span></div>

  <div class="bg-head">
    <h2>Background</h2>
    <p class="bg-question"><span class="q-tag">Question</span>Model architectures converged on encoder-only, decoder-only and diffusion, so why is operator work growing?</p>
  </div>

  <div class="panels">
    <div class="panel">
      <p class="panel-label">Operator optimization</p>
      <figure class="fig">
        <img src="{line_uri}" alt="Line chart of operator-optimization papers per year, 2013 to 2026, rising from 2 papers in 2013 to 81 in 2026.">
      </figure>

      <div class="dsl-key">
        <p class="dsl-key-label"><b>DSL index</b><span>numbers match the bubbles at right &middot; first release &middot; 46 entries</span></p>
        <div class="dsl-key-grid">
{key}
        </div>
      </div>
    </div>

    <div class="panel">
      <p class="panel-label">Operator programming DSLs</p>
      <figure class="fig">
        <img src="{bubble_uri}" alt="Bubble chart of 46 operator-programming DSLs by first release year and abstraction tier, from intrinsics and threads through C++ templates, tile DSLs and tensor/operator DSLs to agent-native; numbered bubbles match the DSL index at left.">
      </figure>
    </div>
  </div>

  <p class="source-note"><strong>Source</strong> &middot; group survey corpus &middot; <strong>276</strong> papers &middot; <strong>46</strong> DSLs</p>

  <aside class="notes">
    Two columns answer the question. On the left, operator-optimization papers by year in a 276-paper survey corpus: a handful a year through the 2010s, roughly a dozen through 2021, then twenty in 2022 and 2023, thirty-two in 2024, sixty-nine in 2025, and eighty-one in 2026 so far. Under it, the index of the 46 DSLs, numbered to match the bubbles at right.

    On the right, those 46 DSLs are placed by first release year and by the abstraction level of the interface they expose: intrinsics and threads, C++ templates and tile primitives, tile-level DSLs, tensor/operator DSLs, and agent-native. The upper dashed line is the cumulative abstraction frontier; it steps up in 2025 when the first agent-native DSL, CroqTile, appears. The placement is a qualitative taxonomy from the survey table, not a measured score. The count is the measured part: eleven DSLs landed in 2025 and eleven more in 2026.

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

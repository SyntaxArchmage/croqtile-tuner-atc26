#!/usr/bin/env python3
"""Generate the two Background-slide figures with matplotlib.

Left  : operator-optimization papers per year, 2013-2026 (line + area).
Right : DSLs first released per year, with that year's names stacked at the
        marker so the chart doubles as the index.

Data
  figures/data/corpus-trend.json  paper counts by year
  figures/data/dsl-timeline.json  first publication / public release year
  figures/data/dsl-tiers.json     qualitative abstraction tier + board order

The abstraction tier is a qualitative taxonomy, not a measured quantity:
  1 intrinsics/threads -> 2 C++ templates -> 3 tile DSLs
  -> 4 tensor/operator DSLs -> 5 agent-native
Within one year the names stack from tier 1 upward, so each column reads as
the abstraction ladder of that year; the tier key is printed under the left
panel in index.html.

Run:
    python3 figures/make_background_figures.py
"""

from __future__ import annotations

import json
import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm
from matplotlib import patheffects as pe

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = HERE / "out"
OUT.mkdir(parents=True, exist_ok=True)

# ── deck palette ────────────────────────────────────────────────────────────
PAPER = "#ffffff"
INK = "#18212a"
INK2 = "#66707a"
INK3 = "#8a949c"
GRID = "#eef1ef"
ACCENT = "#0b6b63"
ACCENT_DEEP = "#084e49"
ACCENT_TINT = "#e2f0ed"
ACCENT_SOFT = "#8fbcb2"

TIER_COLORS = {
    1: "#cfe3df",
    2: "#9cc6bd",
    3: "#3f837a",
    4: "#0b6b63",
    5: "#084e49",
}
TIER_TEXT = {1: INK, 2: INK, 3: PAPER, 4: PAPER, 5: PAPER}
TIER_LABELS = {
    1: "intrinsics",
    2: "templates",
    3: "tile DSL",
    4: "tensor / op",
    5: "agent",
}

# Font: aptitude-deck body stack is Aptos/Avenir Next; Lato is the closest
# locally installed humanist sans and keeps the charts in the same voice.
for name in ("Lato-Regular.ttf", "Lato-Bold.ttf", "Lato-Italic.ttf",
             "Lato-BoldItalic.ttf", "Lato-Medium.ttf"):
    p = pathlib.Path("/usr/share/fonts/truetype/lato") / name
    if p.exists():
        fm.fontManager.addfont(str(p))

plt.rcParams.update({
    "font.family": "Lato",
    "font.size": 9,
    "axes.unicode_minus": False,
    "svg.fonttype": "path",   # keep text as outlines: no font dependency
    "savefig.facecolor": PAPER,
    "figure.facecolor": PAPER,
})

def load_data():
    trend = json.loads((DATA / "corpus-trend.json").read_text())
    timeline = json.loads((DATA / "dsl-timeline.json").read_text())
    tiers = json.loads((DATA / "dsl-tiers.json").read_text())

    years = [int(y) for y in sorted(trend["by_year"]) if int(y) >= 2013]
    papers = [trend["by_year"][str(y)] for y in years]

    year_of = {}
    for year, names in timeline["by_year"].items():
        for name in names:
            year_of[name] = int(year)

    entries = []
    for item in tiers["dsls"]:
        name = item["name"]
        if name not in year_of:
            raise KeyError(f"{name!r} not in dsl-timeline.json")
        entries.append({**item, "year": year_of[name]})

    if len(entries) != timeline["total"]:
        raise ValueError(f"{len(entries)} entries, timeline says {timeline['total']}")
    if sorted(e["n"] for e in entries) != list(range(1, len(entries) + 1)):
        raise ValueError("numbers must be 1..N")
    return years, papers, trend, entries

# ═══════════════════════════════════════════════════════════════════════════
# Left figure — papers per year
# ═══════════════════════════════════════════════════════════════════════════

def make_papers_line(years, papers, total):
    # 600 x 150 source px, displayed at the bottom-right of the slide.
    W, H = 600, 150
    fig = plt.figure(figsize=(W / 72, H / 72), dpi=100)
    ax = fig.add_axes([0.07, 0.19, 0.91, 0.74])

    x = np.asarray(years)
    y = np.asarray(papers)

    # Highlight the surge window, but keep it quieter than the data.
    ax.axvspan(2023.5, 2026.5, color=ACCENT_TINT, alpha=0.55, lw=0, zorder=0)

    ax.fill_between(x, y, 0, color=ACCENT_TINT, alpha=0.90, lw=0, zorder=1)
    ax.plot(x, y, color=ACCENT, lw=2.4, solid_capstyle="round",
            solid_joinstyle="round", zorder=3)

    # Filled markers from 2024 on: the ramp's head, not just its tail.
    ramp = y >= 32
    ax.scatter(x[~ramp], y[~ramp], s=16, facecolor=PAPER, edgecolor=ACCENT,
               linewidth=1.15, zorder=4)
    ax.scatter(x[ramp], y[ramp], s=32, facecolor=ACCENT_DEEP,
               edgecolor=PAPER, linewidth=1.0, zorder=5)

    # Number every data point; ramp years carry the emphasis.
    for year, value, hot in zip(x, y, ramp):
        if hot:
            ax.annotate(f"{value}", (year, value), xytext=(0, 5),
                        textcoords="offset points", ha="center", va="bottom",
                        fontsize=13, fontweight="bold", color=INK, zorder=6)
        else:
            ax.annotate(f"{value}", (year, value), xytext=(0, 4),
                        textcoords="offset points", ha="center", va="bottom",
                        fontsize=10, color=INK2, zorder=6)

    ax.set_xlim(2012.55, 2026.45)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 20, 40, 60, 80])
    ax.set_xticks(years)

    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(INK3)
    ax.spines["bottom"].set_linewidth(0.9)
    ax.tick_params(axis="both", length=0, pad=4, labelsize=11.5, colors=INK2)
    for label in ax.get_xticklabels():
        if label.get_text() in ("2025", "2026"):
            label.set_color(INK)
            label.set_fontweight("bold")

    ax.text(2012.75, 98.0, "papers / year", fontsize=13, color=INK3,
            ha="left", va="top")
    ax.text(2026.42, 3.0, "2026 partial", fontsize=11.5, color=INK3,
            ha="right", va="bottom")

    fig.savefig(OUT / "papers-line.svg", format="svg", facecolor=PAPER)
    fig.savefig(OUT / "papers-line.png", dpi=300, facecolor=PAPER)
    plt.close(fig)

# ═══════════════════════════════════════════════════════════════════════════
# Right figure — DSLs per year, names stacked at each marker
# ═══════════════════════════════════════════════════════════════════════════

def make_dsl_line(entries):
    """Line chart of DSLs first released per year; names stack at each marker."""
    by_year = {}
    for e in entries:
        by_year.setdefault(e["year"], []).append(e)

    all_years = list(range(2013, 2027))
    counts = [len(by_year.get(y, [])) for y in all_years]

    W, H = 1176, 262
    fig = plt.figure(figsize=(W / 72, H / 72), dpi=100)
    ax = fig.add_axes([0.055, 0.10, 0.94, 0.88])

    x = np.array(all_years)
    y = np.array(counts)

    ax.axvspan(2024.5, 2027.95, color=ACCENT_TINT, alpha=0.55, lw=0, zorder=0)
    ax.fill_between(x, y, 0, color=ACCENT_TINT, alpha=0.90, lw=0, zorder=1)
    ax.plot(x, y, color=ACCENT, lw=2.4, solid_capstyle="round",
            solid_joinstyle="round", zorder=3)

    nonzero = y > 0
    ax.scatter(x[nonzero], y[nonzero], s=32, facecolor=ACCENT_DEEP,
               edgecolor=PAPER, linewidth=1.0, zorder=5)

    ax.set_xlim(2012.55, 2027.95)
    ax.set_xticks(all_years)
    ax.set_xticklabels([str(v) for v in all_years], fontsize=16, color=INK2)
    for label in ax.get_xticklabels():
        if label.get_text() in ("2025", "2026"):
            label.set_color(INK)
            label.set_fontweight("bold")

    ax.set_ylim(0, 12)
    ax.set_yticks([0, 2, 4, 6, 8, 10, 12])
    ax.set_yticklabels(["0", "2", "4", "6", "8", "10", "12"],
                       fontsize=16, color=INK2)

    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(INK3)
    ax.spines["bottom"].set_linewidth(0.9)
    ax.tick_params(axis="both", length=0, pad=3, labelsize=16, colors=INK2)

    ax.text(2012.75, 11.85, "DSLs first released / year",
            fontsize=15, color=INK3, ha="left", va="top")
    ax.text(2012.75, 11.0, "2026 partial", fontsize=12,
            color=INK3, ha="left", va="top")

    # A few columns sit a hair off-centre so adjacent-year names never touch.
    shift = {2017: -0.10, 2019: 0.16, 2023: -0.14}
    # The 2025–26 names are left-aligned in two index columns to the right of
    # their markers: centred, the steep 2024→25 segment would run through them.
    left = {2025: 0.02, 2026: 0.42}

    # Names stacked at each marker, ordered by tier then board number.
    # 2025–26 are the crowded columns: their names run below the marker.
    for year in all_years:
        if year not in by_year:
            continue
        names = sorted(by_year[year], key=lambda e: (e["tier"], e["n"]))
        count = len(names)
        below = year >= 2025
        # Only years whose line climbs straight out of the marker need the
        # paper halo: their names sit on top of the rising segment.
        halo = year in (2019, 2021, 2023, 2024)
        start = 6 if below else 4
        step = 12.5
        for i, e in enumerate(names):
            if below:
                offset, va = -(start + i * step), "top"
                xy = (year + left[year], count)
                ha = "left"
            else:
                offset, va = start + i * step, "bottom"
                xy = (year + shift.get(year, 0.0), count)
                ha = "center"
            ax.annotate(e["name"], xy=xy,
                        xytext=(0, offset), textcoords="offset points",
                        ha=ha, va=va, fontsize=12,
                        fontweight="bold" if e.get("milestone") else "normal",
                        color=ACCENT_DEEP if e.get("milestone") else INK,
                        path_effects=([pe.withStroke(linewidth=2.2,
                                                     foreground=PAPER)]
                                      if halo else None),
                        zorder=6)

    fig.savefig(OUT / "dsl-line.svg", format="svg", facecolor=PAPER)
    fig.savefig(OUT / "dsl-line.png", dpi=300, facecolor=PAPER)
    plt.close(fig)

def main():
    years, papers, trend, entries = load_data()
    make_papers_line(years, papers, trend["total"])
    make_dsl_line(entries)
    print("wrote")
    for p in sorted(OUT.iterdir()):
        print(" ", p.name, p.stat().st_size)

if __name__ == "__main__":
    main()

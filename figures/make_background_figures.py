#!/usr/bin/env python3
"""Generate the two Background-slide figures with matplotlib.

Left  : operator-optimization papers per year, 2013-2026 (line + area).
Right : the 46 DSLs on a time x abstraction-tier bubble chart, numbered to
        match the full index printed under the two panels.

Data
  figures/data/corpus-trend.json  paper counts by year
  figures/data/dsl-timeline.json  first publication / public release year
  figures/data/dsl-tiers.json     qualitative abstraction tier + board order

The abstraction axis is a qualitative taxonomy, not a measured quantity:
  1 intrinsics/threads -> 2 C++ templates -> 3 tile DSLs
  -> 4 tensor/operator DSLs -> 5 agent-native

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
from matplotlib.patches import FancyArrowPatch

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
    # 480 x 291 display px; 1 pt == 1 display px in this convention.
    W, H = 487, 225
    fig = plt.figure(figsize=(W / 72, H / 72), dpi=100)
    ax = fig.add_axes([0.085, 0.155, 0.89, 0.765])

    x = np.asarray(years)
    y = np.asarray(papers)

    # Highlight the surge window, but keep it quieter than the data.
    ax.axvspan(2023.5, 2026.5, color=ACCENT_TINT, alpha=0.55, lw=0, zorder=0)

    ax.fill_between(x, y, 0, color=ACCENT_TINT, alpha=0.90, lw=0, zorder=1)
    ax.plot(x, y, color=ACCENT, lw=2.4, solid_capstyle="round",
            solid_joinstyle="round", zorder=3)

    normal = y < 32
    ax.scatter(x[normal], y[normal], s=16, facecolor=PAPER, edgecolor=ACCENT,
               linewidth=1.15, zorder=4)
    hot = ~normal
    ax.scatter(x[hot], y[hot], s=32, facecolor=ACCENT_DEEP,
               edgecolor=PAPER, linewidth=1.0, zorder=5)

    # Selective direct labels: only the three surge years.
    for year, value in zip(x[-3:], y[-3:]):
        if year == 2024:
            ax.annotate(f"{value}", (year, value), xytext=(-6, 7),
                        textcoords="offset points", ha="right", va="bottom",
                        fontsize=10.0, fontweight="bold", color=INK2, zorder=6)
        else:
            ax.annotate(f"{value}", (year, value), xytext=(0, 6),
                        textcoords="offset points", ha="center", va="bottom",
                        fontsize=11.5, fontweight="bold", color=INK, zorder=6)

    ax.set_xlim(2012.55, 2026.45)
    ax.set_ylim(0, 92)
    ax.set_yticks([0, 20, 40, 60, 80])
    ax.set_xticks([2013, 2015, 2017, 2019, 2021, 2023, 2025, 2026])

    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(INK3)
    ax.spines["bottom"].set_linewidth(0.9)
    ax.tick_params(axis="both", length=0, pad=4, labelsize=9.2, colors=INK2)
    for label in ax.get_xticklabels():
        if label.get_text() in ("2025", "2026"):
            label.set_color(INK)
            label.set_fontweight("bold")

    ax.text(0.0, 1.035, "papers / year", transform=ax.transAxes,
            fontsize=8.4, color=INK3, ha="left", va="bottom")
    recent = sum(v for year, v in zip(years, papers) if year >= 2024)
    ax.text(2013.05, 89.0, f"2024–26: {recent} of {total} papers",
            fontsize=9.0, color=INK2, ha="left", va="top")
    ax.text(2026.42, 3.0, "2026 partial", fontsize=7.8, color=INK3,
            ha="right", va="bottom")

    fig.savefig(OUT / "papers-line.svg", format="svg", facecolor=PAPER)
    fig.savefig(OUT / "papers-line.png", dpi=300, facecolor=PAPER)
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# Right figure — DSL bubbles
# ═══════════════════════════════════════════════════════════════════════════

def _group_offsets(k, r):
    """Return pixel offsets for k bubbles in one (year, tier) cell."""
    d = 2 * r + 1.9
    if k == 1:
        return [(0.0, 0.0)]
    if k == 2:
        return [(-d / 2, 0.0), (d / 2, 0.0)]
    if k == 3:
        return [(-d, 0.0), (0.0, 0.0), (d, 0.0)]
    rows = 2 if k <= 4 else 3
    counts = [k // rows + (1 if i < k % rows else 0) for i in range(rows)]
    dy = 2 * r + 1.9
    out = []
    for ri, count in enumerate(counts):
        for ci in range(count):
            out.append(((ci - (count - 1) / 2) * d,
                        (ri - (rows - 1) / 2) * dy))
    return out


def _spring_layout(entries, ax, base_r_px):
    """Place bubbles near (year, tier); repel overlaps, keep tier bands."""
    fig = ax.figure
    fig.canvas.draw()

    year_px = {y: ax.transData.transform((y, 1))[0] for y in
               range(2013, 2027)}
    slot = np.median(np.diff([year_px[y] for y in range(2013, 2027)]))
    tier_px = {t: ax.transData.transform((2013, t))[1] for t in range(1, 6)}
    band = np.median(np.diff([tier_px[t] for t in range(1, 6)]))

    def _rmul(e):
        if e["name"] == "TileLang":
            return 1.0
        return 1.35 if e.get("milestone") else 1.0

    radii = np.array([base_r_px * _rmul(e) for e in entries])
    base = np.array([(year_px[e["year"]], tier_px[e["tier"]]) for e in entries])

    # Seed: a local honeycomb inside each (year, tier) cell.
    pos = base.copy()
    cells = {}
    for i, e in enumerate(entries):
        cells.setdefault((e["year"], e["tier"]), []).append(i)
    for (year, tier), idxs in cells.items():
        offs = _group_offsets(len(idxs), base_r_px)
        for i, (dx, dy) in zip(idxs, offs):
            pos[i] = (year_px[year] + dx, tier_px[tier] + dy)

    # Relax: repulsion + weak spring back to the cell centre.
    for _ in range(360):
        pos += 0.010 * (base - pos)
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                delta = pos[i] - pos[j]
                dist = float(np.hypot(*delta))
                min_dist = radii[i] + radii[j] + 1.0
                if dist < min_dist:
                    if dist < 1e-4:
                        delta = np.array([1.0, 0.0])
                        dist = 1.0
                    push = (min_dist - dist) / dist * 0.5
                    pos[i] += delta * push
                    pos[j] -= delta * push
        # Clamp: the year and the tier band remain readable.
        for i, e in enumerate(entries):
            pos[i, 0] = np.clip(pos[i, 0], year_px[e["year"]] - 0.95 * slot,
                                year_px[e["year"]] + 0.95 * slot)
            pos[i, 1] = np.clip(pos[i, 1], tier_px[e["tier"]] - 0.44 * band,
                                tier_px[e["tier"]] + 0.44 * band)

    inv = ax.transData.inverted()
    return np.array([inv.transform(p) for p in pos])


def make_dsl_bubbles(entries):
    # 624 x 291 display px.
    W, H = 617, 452
    fig = plt.figure(figsize=(W / 72, H / 72), dpi=100)
    ax = fig.add_axes([0.145, 0.155, 0.835, 0.765])

    ax.set_xlim(2012.45, 2026.55)
    ax.set_ylim(0.5, 5.5)

    # Surge window + tier hairlines.
    ax.axvspan(2024.5, 2026.5, color=ACCENT_TINT, alpha=0.55, lw=0, zorder=0)
    for t in (1.5, 2.5, 3.5, 4.5):
        ax.axhline(t, color=GRID, lw=0.8, zorder=0)

    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels([TIER_LABELS[t] for t in range(1, 6)],
                       fontsize=9.4, color=INK2)
    ax.set_xticks(range(2013, 2027))
    ax.set_xticklabels([str(y) for y in range(2013, 2027)],
                       fontsize=8.4, color=INK2)
    for label in ax.get_xticklabels():
        if label.get_text() in ("2025", "2026"):
            label.set_color(INK)
            label.set_fontweight("bold")

    ax.tick_params(axis="both", length=0, pad=3)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.set_ylabel("abstraction", fontsize=8.6, color=INK2, labelpad=2)
    ax.yaxis.set_label_coords(-0.108, 0.5)

    base_r = 7.6
    placed = _spring_layout(entries, ax, base_r)

    # Frontier: cumulative maximum tier; it steps up when agent-native lands.
    max_tier = 0
    frontier = {}
    for year in range(2013, 2027):
        max_tier = max([max_tier] + [e["tier"] for e in entries
                                     if e["year"] == year])
        frontier[year] = max_tier
    step_x, step_y = [], []
    prev = None
    for year in range(2013, 2027):
        level = frontier[year] + 0.42
        if prev is None:
            step_x.append(2012.75)
            step_y.append(level)
        elif level != prev:
            step_x += [year, year]
            step_y += [prev, level]
        prev = level
    step_x.append(2026.45)
    step_y.append(prev)
    ax.plot(step_x, step_y, color=ACCENT_TINT, lw=5.0, alpha=0.75,
            zorder=1.8, solid_capstyle="round")
    ax.plot(step_x, step_y, color=ACCENT_DEEP, lw=1.55, ls=(0, (3.6, 2.4)),
            zorder=2, solid_capstyle="round")
    ax.add_patch(FancyArrowPatch((2026.05, step_y[-1]), (2026.5, step_y[-1]),
                                 arrowstyle="-|>", mutation_scale=8,
                                 color=ACCENT_DEEP, lw=1.1, zorder=2))
    ax.annotate("abstraction frontier", (2016.3, step_y[0]),
                xytext=(0, 4.6), textcoords="offset points",
                fontsize=8.9, color=ACCENT_DEEP, ha="left", va="bottom",
                zorder=6)
    ax.text(2026.45, 5.56, "22 of 46 DSLs in 2025–26",
            fontsize=8.2, color=INK2, ha="right", va="bottom")

    # Bubbles: draw large milestones first so small ones sit on top.
    order = sorted(range(len(entries)),
                   key=lambda i: (entries[i].get("milestone", False),
                                  entries[i]["n"]))
    for i in order:
        e = entries[i]
        r = base_r * (1.0 if e["name"] == "TileLang"
                      else (1.35 if e.get("milestone") else 1.0))
        x, y = placed[i]
        ax.scatter([x], [y], s=(2 * r) ** 2,
                   facecolor=TIER_COLORS[e["tier"]],
                   edgecolor=PAPER if not e.get("milestone") else ACCENT_DEEP,
                   linewidth=0.55 if not e.get("milestone") else 1.2,
                   zorder=4 if not e.get("milestone") else 5)
        if e.get("milestone"):
            ax.scatter([x], [y], s=(2 * r + 6) ** 2, facecolor="none",
                       edgecolor=ACCENT_SOFT, linewidth=0.7, alpha=0.7,
                       zorder=3)
        ax.text(x, y, str(e["n"]), ha="center", va="center",
                fontsize=8.8 if e.get("milestone") else 7.2,
                fontweight="bold", color=TIER_TEXT[e["tier"]], zorder=6)

    # Four milestone names with hairline leaders.
    label_specs = {
        "CUTLASS/CuTe": ((2014.55, 1.42), "left"),
        "Triton": ((2019.55, 2.38), "left"),
        "TileLang": ((2024.85, 2.55), "right"),
        "CroqTile": ((2023.55, 4.82), "right"),
    }
    for e in entries:
        if e["name"] not in label_specs:
            continue
        i = entries.index(e)
        xy = placed[i]
        xytext, ha = label_specs[e["name"]]
        ax.annotate(e["name"], xy=xy, xytext=xytext, textcoords="data",
                    ha=ha, va="center", fontsize=8.4,
                    fontweight="bold" if e["name"] == "CroqTile" else "normal",
                    color=ACCENT_DEEP if e["name"] == "CroqTile" else INK,
                    arrowprops=dict(arrowstyle="-", color=ACCENT_SOFT,
                                    lw=0.6, shrinkA=2, shrinkB=3),
                    zorder=7)

    fig.savefig(OUT / "dsl-bubbles.svg", format="svg", facecolor=PAPER)
    fig.savefig(OUT / "dsl-bubbles.png", dpi=300, facecolor=PAPER)
    plt.close(fig)


def write_index_snippet(entries):
    lines = []
    for e in entries:
        name = (e["name"].replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;"))
        lines.append(
            f'        <span class="dsl-key-item t{e["tier"]}">'
            f'<i></i><b>{e["n"]:02d}</b>{name}</span>'
        )
    (OUT / "dsl-key.html").write_text("\n".join(lines) + "\n")


def main():
    years, papers, trend, entries = load_data()
    make_papers_line(years, papers, trend["total"])
    make_dsl_bubbles(entries)
    write_index_snippet(entries)
    print("wrote")
    for p in sorted(OUT.iterdir()):
        print(" ", p.name, p.stat().st_size)


if __name__ == "__main__":
    main()

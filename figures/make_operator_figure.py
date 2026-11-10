#!/usr/bin/env python3
"""GFLOPs-as-optimizations-stack chart for the operator-optimization page.

Horizontal bars, one row per cumulative optimization, deck palette and Lato.
The data is the seven-series sweep from the intro deck's figure.

Run:
    python3 figures/make_operator_figure.py
"""

from __future__ import annotations

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import numpy as np

OUT = pathlib.Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

PAPER = "#ffffff"
INK = "#18212a"
INK2 = "#66707a"
INK3 = "#8a949c"
GRID = "#eef1ef"
ACCENT = "#0b6b63"
ACCENT_DEEP = "#084e49"

for name in ("Lato-Regular.ttf", "Lato-Bold.ttf"):
    p = pathlib.Path("/usr/share/fonts/truetype/lato") / name
    if p.exists():
        fm.fontManager.addfont(str(p))

plt.rcParams.update({
    "font.family": "Lato",
    "axes.unicode_minus": False,
    "svg.fonttype": "path",
    "savefig.facecolor": PAPER,
    "figure.facecolor": PAPER,
})

SERIES = [
    ("scalar memrefs\n(no opts)", 0.558),
    ("vec", 1.53),
    ("vec + cache tile", 10.79),
    ("vec + cache tile\n+ pack", 15.57),
    ("vec + cache tile\n+ reg tile", 22.53),
    ("all opts", 61.94),
    ("absolute peak", 75.2),
]


def main() -> None:
    labels = [s[0] for s in SERIES]
    vals = np.array([s[1] for s in SERIES])

    W, H = 560, 430
    fig = plt.figure(figsize=(W / 72, H / 72), dpi=100)
    ax = fig.add_axes([0.315, 0.145, 0.655, 0.735])

    ypos = np.arange(len(vals))
    colors = ['#adc1b8'] * 5 + [ACCENT, '#ffffff']
    bars = ax.barh(ypos, vals, height=0.48, color=colors, zorder=3)
    bars[-1].set_edgecolor('#879e92')
    bars[-1].set_linewidth(1.1)
    bars[-1].set_linestyle((0, (4, 2)))
    ax.axhspan(4.58, 5.42, color='#edf5f0', zorder=0)
    ax.invert_yaxis()

    for y, v in zip(ypos, vals):
        ax.text(v + 1.6, y, f"{v:g}", va="center", ha="left",
                fontsize=14, fontweight="bold" if y == 5 else 'normal',
                color=ACCENT_DEEP if y == 5 else INK2, zorder=4)

    ax.set_xlim(0, 86)
    ax.set_ylim(len(vals) - 0.45, -0.55)
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels, fontsize=14, color=INK2, linespacing=1.25)
    ax.set_xticks([0, 20, 40, 60, 80])
    ax.tick_params(axis="x", length=0, pad=4, labelsize=12.5, colors=INK2)
    ax.tick_params(axis="y", length=0, pad=8)

    ax.grid(axis="x", color=GRID, lw=0.9)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_visible(False)

    ax.text(-0.44, 1.065, "Performance as optimizations combine",
            transform=ax.transAxes, fontsize=16, color=INK3,
            ha="left", va="bottom")
    ax.set_xlabel('GFLOPs', color=INK2, fontsize=12, labelpad=8)

    fig.savefig(OUT / "operator-gflops.svg", format="svg", facecolor=PAPER)
    fig.savefig(OUT / "operator-gflops.png", dpi=300, facecolor=PAPER)
    plt.close(fig)
    print("wrote operator-gflops.svg/png")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate the tuning search-space figure for the Ways-of-tuning trio.

The figure is a grid of tile size (BM) against pipeline stages. Each cell
counts how many of its N-tile / K-tile / swizzle variants fit the SMEM and
register limits, using the same seeded sweep as the paper's search-space
figure. Styling follows the deck palette.

Run:
    python3 figures/make_tuning_figures.py
"""

from __future__ import annotations

import pathlib

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(parents=True, exist_ok=True)

PAPER = "#ffffff"
INK = "#18212a"
INK2 = "#66707a"
INK3 = "#8a949c"
GRID = "#eef1ef"
ACCENT = "#0b6b63"
ACCENT_DEEP = "#084e49"
ACCENT_TINT = "#e2f0ed"

for name in ("Lato-Regular.ttf", "Lato-Bold.ttf", "Lato-Italic.ttf"):
    p = pathlib.Path("/usr/share/fonts/truetype/lato") / name
    if p.exists():
        fm.fontManager.addfont(str(p))

plt.rcParams.update({
    "font.family": "Lato",
    "font.size": 10,
    "axes.unicode_minus": False,
    "svg.fonttype": "path",
    "savefig.facecolor": PAPER,
    "figure.facecolor": PAPER,
})


def configs():
    """Seeded sweep over tile sizes, stages and swizzles; viability by limits."""
    seed = 77

    def rand():
        nonlocal seed
        seed ^= (seed << 13) & 0xFFFFFFFF
        seed ^= seed >> 17
        seed ^= (seed << 5) & 0xFFFFFFFF
        return (seed & 0xFFFFFFFF) / 4294967296

    rows = []
    for mt in (64, 128, 192, 256):
        for nt in (64, 128, 192, 256):
            for kt in (32, 64, 128):
                for st in (2, 3, 4, 5, 6):
                    for sw in (64, 128):
                        a = mt * kt / 2
                        b = nt * kt
                        e = mt * kt / 8
                        smem_kb = (st * (a + b + e) + 1024) / 1024
                        base = 32 + (mt * nt) / (128 * 4) * 8
                        regs = round(min(280, max(80, base + st * 12
                                                  + rand() * 40 - 20)))
                        ok = smem_kb <= 228 and regs <= 255
                        rows.append((mt, st, ok))
    return rows


def main() -> None:
    data = configs()
    xs = np.array([bm for bm, st, good in data], dtype=float)
    ys = np.array([st for bm, st, good in data], dtype=float)
    ok = np.array([good for bm, st, good in data])

    W, H = 680, 400
    fig = plt.figure(figsize=(W / 72, H / 72), dpi=100)
    ax = fig.add_axes([0.115, 0.185, 0.815, 0.665])

    ax.scatter(xs, ys, s=95, color=ACCENT, alpha=0.9,
               linewidths=0, zorder=3)

    ax.set_xlim(34, 286)
    ax.set_ylim(1.45, 6.55)
    ax.set_xticks([64, 128, 192, 256])
    ax.set_xticklabels(["64", "128", "192", "256"], fontsize=14, color=INK2)
    ax.set_yticks([2, 3, 4, 5, 6])
    ax.set_yticklabels(["2", "3", "4", "5", "6"], fontsize=14, color=INK2)
    ax.set_xlabel("tile size BM", fontsize=16, color=INK2, labelpad=6)
    ax.set_ylabel("stages", fontsize=16, color=INK2, labelpad=6)
    ax.tick_params(axis="both", length=0, pad=4)

    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(INK3)
    ax.spines["bottom"].set_linewidth(0.9)

    ax.set_title("search space · tile size × stages", loc="left",
                 fontsize=14.5, color=INK3, pad=10)

    fig.savefig(OUT / "search-space.svg", format="svg", facecolor=PAPER)
    fig.savefig(OUT / "search-space.png", dpi=300, facecolor=PAPER)
    plt.close(fig)
    print("wrote search-space.svg/png")


if __name__ == "__main__":
    main()

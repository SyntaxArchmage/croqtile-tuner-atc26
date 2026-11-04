#!/usr/bin/env python3
"""Draw the bottleneck-based tuning loop as an inline-SVG concept diagram.

A thin ring with five labelled steps around it: the deck's editorial idiom
(no pills, no paper figure). Colours and fonts come from index.html.

Run:
    python3 figures/make_expert_loop.py
"""

from __future__ import annotations

import math
import pathlib

OUT = pathlib.Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 700, 400
CX, CY, R = 350, 200, 125

# number, label, angle (deg, y-down), label x, label y, anchor
NODES = [
    ("01", "profile", -90, 350, 62, "middle"),
    ("02", "analyse", -18, 497, 164, "start"),
    ("03", "propose", 54, 444, 310, "start"),
    ("04", "implement", 126, 256, 310, "end"),
    ("05", "compile · measure", 198, 213, 164, "end"),
]


def pt(angle: float, r: float = R) -> tuple[float, float]:
    a = math.radians(angle)
    return CX + r * math.cos(a), CY + r * math.sin(a)


def tangent(angle: float) -> tuple[float, float]:
    a = math.radians(angle)
    return -math.sin(a), math.cos(a)


def main() -> None:
    parts = [
        f'<svg class="expert-loop" viewBox="0 0 {W} {H}" role="img" '
        'aria-label="Bottleneck tuning loop: profile, analyse, propose, '
        'implement, compile and measure, then decide; one round repeats.">',
        f'<circle class="ring" cx="{CX}" cy="{CY}" r="{R}"/>',
    ]

    for num, label, ang, lx, ly, anchor in NODES:
        x, y = pt(ang)
        parts.append(f'<circle class="dot" cx="{x:.1f}" cy="{y:.1f}" r="5"/>')
        mid = ang + 36
        mx, my = pt(mid)
        tx, ty = tangent(mid)
        nx, ny = -ty, tx
        tip = (mx + 10 * tx, my + 10 * ty)
        b1 = (mx - 4.5 * tx + 6 * nx, my - 4.5 * ty + 6 * ny)
        b2 = (mx - 4.5 * tx - 6 * nx, my - 4.5 * ty - 6 * ny)
        parts.append(
            f'<path class="head" d="M{tip[0]:.1f},{tip[1]:.1f} '
            f'L{b1[0]:.1f},{b1[1]:.1f} L{b2[0]:.1f},{b2[1]:.1f} Z"/>')
        parts.append(
            f'<g class="lbl"><text x="{lx}" y="{ly}" text-anchor="{anchor}">'
            f'<tspan class="num">{num}</tspan> {label}</text></g>')

    parts.append(f'<g class="center"><text x="{CX}" y="{CY + 6}" '
                 'class="round">one round</text></g>')
    parts.append("</svg>")
    (OUT / "expert-loop.svg").write_text("\n".join(parts) + "\n")
    print("wrote expert-loop.svg")


if __name__ == "__main__":
    main()

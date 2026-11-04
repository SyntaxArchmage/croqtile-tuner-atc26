#!/usr/bin/env python3
"""Visual QA helper: render one slide and report its layout metrics.

Usage:
    python3 tools/qa_slide.py 3 [--tag v1]

Writes /tmp/qa/slide03[_tag].png and prints a JSON-ish report: section
overflow, key element boxes, and any descendant that pokes outside the
slide's content box. The PNG is meant to be read back and judged visually.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import socket
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = 8899
BASE = f"http://localhost:{PORT}/index.html"

SELECTORS = [
    "h2", ".forces", ".force", ".force-n", ".force-title", ".force-eg",
    ".bg-stack", ".bg-bottom", ".trend-block", ".source-note",
]


def server_up() -> bool:
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", PORT)) == 0


def ensure_server() -> subprocess.Popen | None:
    if server_up():
        return None
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT), "--bind", "0.0.0.0"],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(40):
        if server_up():
            return proc
        time.sleep(0.1)
    raise RuntimeError("server did not start")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("slide", type=int, help="1-based slide number")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    proc = ensure_server()
    out_dir = pathlib.Path("/tmp/qa")
    out_dir.mkdir(parents=True, exist_ok=True)
    name = f"slide{args.slide:02d}" + (f"_{args.tag}" if args.tag else "")
    png = out_dir / f"{name}.png"

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(BASE, wait_until="load")
        page.evaluate("Reveal.configure({transition:'none'})")
        page.evaluate(f"Reveal.slide({args.slide - 1})")
        page.wait_for_timeout(500)
        page.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": 1280, "height": 720})

        report = page.evaluate(
            """(selectors) => {
              const s = Reveal.getCurrentSlide();
              const sr = s.getBoundingClientRect();
              const box = el => {
                const r = el.getBoundingClientRect();
                return [Math.round(r.left), Math.round(r.top),
                        Math.round(r.right), Math.round(r.bottom)];
              };
              const out = {slide: Reveal.getIndices().h + 1,
                           scroll: s.scrollHeight, height: Math.round(sr.height),
                           selectors: {}};
              for (const sel of selectors) {
                const els = [...s.querySelectorAll(sel)];
                if (els.length) out.selectors[sel] = els.map(box);
              }
              const pad = 0.5;
              const spill = [];
              for (const el of s.querySelectorAll('*')) {
                if (el.closest('aside.notes')) continue;
                const r = el.getBoundingClientRect();
                if (r.width < 1 || r.height < 1) continue;
                if (r.left < sr.left - pad || r.right > sr.right + pad ||
                    r.top < sr.top - pad || r.bottom > sr.bottom + pad) {
                  spill.push([el.tagName, (el.className || '').toString().slice(0, 40),
                              ...box(el)]);
                }
              }
              out.spill = spill;
              return out;
            }""", SELECTORS)
        browser.close()
    if proc:
        proc.terminate()

    print(f"png: {png}")
    print(json.dumps(report, indent=1)[:4000])


if __name__ == "__main__":
    main()

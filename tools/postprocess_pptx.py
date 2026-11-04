#!/usr/bin/env python3
"""Post-process the dom-to-pptx export for this deck.

dom-to-pptx sizes text boxes from the browser layout; PowerPoint's text
metrics differ slightly, so short labels wrap mid-word. Normalise the export:

  * zero text-frame insets (PowerPoint defaults eat ~0.1in per side)
  * disable autofit (spAutoFit recentres text when wrap is off)
  * turn wrapping off for short labels, captions and the source line

Usage:
    python3 tools/postprocess_pptx.py dist/slides.pptx
"""

from __future__ import annotations

import sys

from pptx import Presentation
from pptx.enum.text import MSO_AUTO_SIZE


def main(path: str) -> None:
    prs = Presentation(path)
    wrap_off = 0
    for slide in prs.slides:
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            tf = shape.text_frame
            text = tf.text.strip()
            if not text:
                continue
            tf.margin_left = 0
            tf.margin_right = 0
            tf.margin_top = 0
            tf.margin_bottom = 0
            tf.auto_size = MSO_AUTO_SIZE.NONE
            if len(text) <= 32 or text.upper().startswith("SOURCE"):
                tf.word_wrap = False
                wrap_off += 1
    prs.save(path)
    print(f"post-processed {path}: wrap off on {wrap_off} text frames")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "dist/slides.pptx")

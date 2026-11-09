#!/usr/bin/env python3
"""Refresh the background figures while preserving authored copy and notes."""
import base64
from pathlib import Path
from bs4 import BeautifulSoup


def main():
    root = Path(__file__).resolve().parent.parent
    index = root / 'index.html'
    html = index.read_text()
    start = html.index('<section class="gs bg-slide"')
    end = html.index('</section>', start) + len('</section>')
    section = BeautifulSoup(html[start:end], 'html.parser')
    images = section.select('img')
    for image, name in zip(images, ['dsl-line.svg', 'papers-line.svg']):
        image['src'] = 'data:image/svg+xml;base64,' + base64.b64encode(
            (root / 'figures/out' / name).read_bytes()).decode()
    index.write_text(html[:start] + str(section) + html[end:])
    print('Refreshed background figures; preserved slide text and notes')


if __name__ == '__main__':
    main()

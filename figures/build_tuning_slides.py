#!/usr/bin/env python3
"""Refresh tuning figures while preserving authored copy and notes."""
import base64
from pathlib import Path
from bs4 import BeautifulSoup


def main():
    root = Path(__file__).resolve().parent.parent
    index = root / 'index.html'
    html = index.read_text()
    for slide, filename, selector in [(5, 'expert-loop.svg', 'svg'),
                                       (6, 'search-space.svg', 'img')]:
        marker = f'id="slide-{slide:02}"'
        start = html.rfind('<section', 0, html.index(marker))
        end = html.index('</section>', start) + len('</section>')
        section = BeautifulSoup(html[start:end], 'html.parser')
        asset = root / 'figures/out' / filename
        if selector == 'svg':
            section.select_one('figure svg').replace_with(
                BeautifulSoup(asset.read_text(), 'html.parser').select_one('svg'))
        else:
            section.select_one('figure img')['src'] = (
                'data:image/svg+xml;base64,' + base64.b64encode(asset.read_bytes()).decode())
        html = html[:start] + str(section) + html[end:]
    index.write_text(html)
    print('Refreshed tuning figures; preserved slide text and notes')


if __name__ == '__main__':
    main()

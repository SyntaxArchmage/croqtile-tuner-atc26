"""Embed the authored presentation styles/figures; keep the HTML portable."""
from pathlib import Path
import base64
import re

ROOT = Path(__file__).resolve().parent.parent


def main():
    path = ROOT / "index.html"
    source = path.read_text()
    style = '<style id="presentation-polish">\n' + (ROOT / "polish.css").read_text() + '</style>'
    if 'id="presentation-polish"' in source:
        source = re.sub(r'<style id="presentation-polish">.*?</style>', lambda _: style, source, flags=re.S)
    else:
        source = source.replace('</head>', style + '\n</head>')

    def embed(match):
        tag = match.group()
        name = re.search(r'data-polish-asset="([^"]+)"', tag)[1]
        asset = ROOT / 'figures' / 'out' / (name + '.svg')
        uri = 'data:image/svg+xml;base64,' + base64.b64encode(asset.read_bytes()).decode()
        return re.sub(r'src="[^"]*"', lambda _: 'src="' + uri + '"', tag)

    source = re.sub(r'<img\b[^>]*data-polish-asset="[^"]+"[^>]*>', embed, source)
    path.write_text(source)
    (ROOT / 'dist').mkdir(exist_ok=True)
    (ROOT / 'dist' / 'slides.html').write_text(source)
    print('Embedded polish.css and presentation figures; refreshed dist/slides.html')


if __name__ == '__main__':
    main()

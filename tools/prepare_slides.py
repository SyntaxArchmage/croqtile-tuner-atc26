"""Embed presentation styles without altering the original paper figures."""
from pathlib import Path
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

    path.write_text(source)
    (ROOT / 'dist').mkdir(exist_ok=True)
    (ROOT / 'dist' / 'slides.html').write_text(source)
    print('Embedded polish.css; refreshed dist/slides.html with original figures')


if __name__ == '__main__':
    main()

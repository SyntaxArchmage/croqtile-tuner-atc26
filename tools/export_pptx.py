"""Export editable PowerPoint, browser PDF, and slide previews.

Native text preserves browser line breaks, fonts, emphasis and code indentation.
Charts are embedded at 2×; HTML tabs export their default view. Full presenter
notes remain in PowerPoint. The PDF preserves the browser's exact appearance.
"""
from pathlib import Path
import base64
import io
import re

import cairosvg
import fitz
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.util import Inches, Pt
from prepare_slides import main as prepare

ROOT = Path(__file__).resolve().parent.parent


def color(value):
    m = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)', value or '')
    if not m or (m[4] is not None and float(m[4]) == 0):
        return None
    return RGBColor(*map(int, m.group(1, 2, 3)))


def inch(px):
    return Inches(px / 100)


def shape(slide, item):
    x, y, w, h = [inch(item[k]) for k in ['x', 'y', 'w', 'h']]
    if item['type'] == 'rect':
        radius = min(item['radius'], item['w']/2, item['h']/2)
        kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
        sh = slide.shapes.add_shape(kind, x, y, w, h)
        if radius:
            sh.adjustments[0] = radius / min(item['w'], item['h'])
        bg = color(item['bg'])
        if bg:
            sh.fill.solid()
            sh.fill.fore_color.rgb = bg
        else:
            sh.fill.background()
        borders = item['borders']
        if all(b == borders[0] for b in borders) and borders[0]['width']:
            sh.line.color.rgb = color(borders[0]['color']) or RGBColor(200, 210, 205)
            sh.line.width = Pt(borders[0]['width']*.72)
        else:
            sh.line.fill.background()
            edges = [(x,y,x+w,y),(x+w,y,x+w,y+h),(x,y+h,x+w,y+h),(x,y,x,y+h)]
            for b, edge in zip(borders, edges):
                if b['width'] and color(b['color']):
                    line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, *edge)
                    line.line.color.rgb = color(b['color'])
                    line.line.width = Pt(b['width']*.72)
    elif item['type'] in ('svg', 'image'):
        if item['type'] == 'svg':
            blob, mime = item['src'].encode(), 'svg'
        else:
            header, payload = item['src'].split(',', 1)
            blob, mime = base64.b64decode(payload), header
        if 'svg' in mime:
            blob = cairosvg.svg2png(bytestring=blob,
                output_width=max(1, round(item['w']*2)),
                output_height=max(1, round(item['h']*2)))
        slide.shapes.add_picture(io.BytesIO(blob), x, y, w, h)
    else:
        sh = slide.shapes.add_textbox(x, y, w+inch(3), h+inch(2))
        tf = sh.text_frame
        tf.clear()
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.word_wrap = False
        tf.auto_size = MSO_AUTO_SIZE.NONE
        paragraph = tf.paragraphs[0]
        paragraph.space_before = paragraph.space_after = Pt(0)
        run = paragraph.add_run()
        run.text = item['text']
        run.font.name = item['font']
        run.font.size = Pt(item['size']*.72)
        run.font.bold = item['bold']
        run.font.italic = item['italic']
        run.font.color.rgb = color(item['color']) or RGBColor(24, 33, 42)


def main():
    prepare()
    preview = ROOT / 'dist/preview'
    preview.mkdir(exist_ok=True)
    pdf = fitz.open()
    slides = []
    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 720}, device_scale_factor=2)
        page.goto((ROOT / 'index.html').as_uri(), wait_until='load')
        page.wait_for_function('Reveal.isReady()')
        page.evaluate("Reveal.configure({transition:'none'});")
        page.evaluate('document.fonts.ready')
        page.add_style_tag(content='.reveal .controls,.reveal .progress{display:none!important}')
        page.emulate_media(media='screen')
        count = page.locator('.slides > section').count()
        extractor = (ROOT / 'tools/export_dom.js').read_text()
        for i in range(count):
            page.evaluate('(i)=>Reveal.slide(i)', i)
            page.wait_for_timeout(70)
            slides.append(page.evaluate(extractor))
            page.screenshot(path=str(preview / f'slide-{i+1:02}.png'))
            rendered = fitz.open(stream=page.pdf(width='1280px', height='720px',
                print_background=True, margin={k:'0' for k in ['top','right','bottom','left']}), filetype='pdf')
            if len(rendered) != 1:
                raise RuntimeError(f'Slide {i+1} printed as {len(rendered)} pages')
            pdf.insert_pdf(rendered)
            rendered.close()
        browser.close()
    pdf.save(ROOT / 'dist/slides.pdf', garbage=4, deflate=True)
    pdf.close()

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(12.8), Inches(7.2)
    for i, data in enumerate(slides):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = color(data['bg']) or RGBColor(247,247,243)
        slide.notes_slide.notes_text_frame.text = data['notes'].strip()
        for item in data['items']:
            if item['w'] >= .5 and item['h'] >= .5:
                shape(slide, item)
        print(f'Exported slide {i+1}/{len(slides)}', flush=True)
    prs.save(ROOT / 'dist/slides.pptx')

    contact = Image.new('RGB', (1600, ((len(slides)+3)//4)*248), '#e3eae5')
    draw = ImageDraw.Draw(contact)
    for i in range(len(slides)):
        with Image.open(preview / f'slide-{i+1:02}.png') as im:
            thumb = im.convert('RGB').resize((400,225), Image.Resampling.LANCZOS)
        x, y = i%4*400, i//4*248
        contact.paste(thumb, (x,y))
        draw.text((x+12,y+230),f'{i+1:02}',fill='#526a5c')
    contact.save(preview / 'all-slides.jpg', quality=92)
    print('Updated dist/slides.pptx, slides.pdf and preview/all-slides.jpg')


if __name__ == '__main__':
    main()

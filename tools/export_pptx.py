from pathlib import Path
from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_AUTO_SIZE
import json,re,io,base64,cairosvg
root=Path(__file__).resolve().parent.parent
with sync_playwright() as p:
 b=p.chromium.launch(args=['--no-sandbox']);page=b.new_page(viewport={'width':1280,'height':720})
 page.goto((root/'index.html').as_uri(),wait_until='domcontentloaded');page.wait_for_function('Reveal.isReady()');page.evaluate("Reveal.configure({transition:'none'});")
 allslides=[]
 for i in range(19):
  page.evaluate(f'Reveal.slide({i});');page.wait_for_timeout(50)
  allslides.append(page.evaluate('''() => {
 const s=Reveal.getCurrentSlide();const out={notes:s.querySelector('aside.notes')?.textContent||'',items:[],bg:getComputedStyle(document.body).backgroundColor};
 const box=r=>({x:r.left,y:r.top,w:r.width,h:r.height});
 const visible=e=> !e.closest('aside,script,style') && e.getBoundingClientRect().width>0;
 for(const e of s.querySelectorAll('*')){
 if(!visible(e) || e.closest('svg') && e.tagName.toLowerCase()!=='svg')continue;
 const r=e.getBoundingClientRect(),st=getComputedStyle(e);
 if(e.tagName==='IMG'){let ir=box(r); if(st.objectFit==='contain' && e.naturalWidth){const ratio=Math.min(ir.w/e.naturalWidth,ir.h/e.naturalHeight);const nw=e.naturalWidth*ratio,nh=e.naturalHeight*ratio;ir.x+=(ir.w-nw)/2;ir.y+=(ir.h-nh)/2;ir.w=nw;ir.h=nh;} out.items.push({type:'image',src:e.src,...ir});continue;}
 if(e.tagName.toLowerCase()==='svg'){const clone=e.cloneNode(true);const source=[e,...e.querySelectorAll('*')],dest=[clone,...clone.querySelectorAll('*')];source.forEach((node,i)=>{const cs=getComputedStyle(node);['fill','stroke','stroke-width','font-family','font-size','font-weight','color'].forEach(k=>dest[i].style.setProperty(k,cs.getPropertyValue(k)));});out.items.push({type:'svg',src:clone.outerHTML,...box(r)});continue;}
 if(st.backgroundColor!=='rgba(0, 0, 0, 0)' || parseFloat(st.borderTopWidth)>0)out.items.push({type:'rect',bg:st.backgroundColor,border:st.borderTopColor,bw:parseFloat(st.borderTopWidth),...box(r)});
 for(const n of e.childNodes){if(n.nodeType!==3 || !n.textContent.trim())continue;
 const range=document.createRange();range.selectNodeContents(n);const rr=range.getBoundingClientRect();if(!rr.width)continue;
 out.items.push({type:'text',text:n.textContent.replace(/\\s+/g,' ').trim(),color:st.color,size:parseFloat(st.fontSize),bold:parseInt(st.fontWeight)>=600,mono:st.fontFamily.toLowerCase().includes('mono'),...box(rr)});
 }
 }
 return out;
 }'''))
 b.close()
prs=Presentation();prs.slide_width=Inches(12.8);prs.slide_height=Inches(7.2)
def color(v):
 m=re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)',v or '')
 if not m or m[4]=='0':return None
 return RGBColor(*map(int,m.group(1,2,3)))
for data in allslides:
 sl=prs.slides.add_slide(prs.slide_layouts[6]);sl.background.fill.solid();sl.background.fill.fore_color.rgb=color(data['bg']) or RGBColor(255,255,255)
 sl.notes_slide.notes_text_frame.text=data['notes'].strip()
 for item in data['items']:
  if item['w']<1 or item['h']<1:continue
  x,y,w,h=[Inches(item[k]/100) for k in ['x','y','w','h']]
  if item['type']=='rect':
   sh=sl.shapes.add_shape(MSO_SHAPE.RECTANGLE,x,y,w,h);bg=color(item['bg']);bc=color(item['border'])
   if bg:sh.fill.solid();sh.fill.fore_color.rgb=bg
   else:sh.fill.background()
   if bc and item['bw']>0:sh.line.color.rgb=bc;sh.line.width=Pt(item['bw']*.72)
   else:sh.line.fill.background()
  elif item['type'] in ['svg','image']:
   if item['type']=='svg':blob=item['src'].encode();mime='svg'
   else:
    header,payload=item['src'].split(',',1);blob=base64.b64decode(payload);mime=header
   if 'svg' in mime:
    blob=cairosvg.svg2png(bytestring=blob,output_width=max(1,round(item['w']*2)),output_height=max(1,round(item['h']*2)))
   sl.shapes.add_picture(io.BytesIO(blob),x,y,w,h)
  else:
   sh=sl.shapes.add_textbox(x,y,w+Inches(.04),h+Inches(.035));tf=sh.text_frame;tf.clear();tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0;tf.word_wrap=False;tf.auto_size=MSO_AUTO_SIZE.NONE
   pp=tf.paragraphs[0];pp.space_before=pp.space_after=Pt(0);run=pp.add_run();run.text=item['text'];run.font.name='Consolas' if item['mono'] else 'Arial';run.font.size=Pt(item['size']*.72);run.font.bold=item['bold'];run.font.color.rgb=color(item['color']) or RGBColor(20,20,20)
prs.save(root/'dist/slides.pptx');print('Exported 19 slides with native text, figures, and speaker notes')

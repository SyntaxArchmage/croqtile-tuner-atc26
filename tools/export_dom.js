// Actual rendered geometry, including wrapped text, code indentation and bullets.
() => {
  const slide = Reveal.getCurrentSlide(), items = [];
  const box = r => ({x:r.left,y:r.top,w:r.width,h:r.height});
  const fill = (r,s) => {
    const borders=['Top','Right','Bottom','Left'].map(side=>({
      width:parseFloat(s['border'+side+'Width'])||0,color:s['border'+side+'Color']}));
    if(s.backgroundColor!=='rgba(0, 0, 0, 0)'||borders.some(b=>b.width))
      items.push({type:'rect',...r,bg:s.backgroundColor,radius:parseFloat(s.borderTopLeftRadius)||0,borders});
  };
  const textStyle = s => ({color:s.color,size:parseFloat(s.fontSize),
    font:s.fontFamily.split(',')[0].replace(/['"]/g,''),
    bold:parseInt(s.fontWeight)>=600,italic:s.fontStyle==='italic'});
  const before = e => {
    const s=getComputedStyle(e,'::before');
    if(['none','normal'].includes(s.content)||s.display==='none')return;
    const r=e.getBoundingClientRect(),left=parseFloat(s.left)||0,top=parseFloat(s.top)||0;
    const w=parseFloat(s.width)||(r.width-left-(parseFloat(s.right)||0));
    const h=parseFloat(s.height)||(r.height-top-(parseFloat(s.bottom)||0));
    fill({x:r.left+left,y:r.top+top,w,h},s);
    const content=s.content.replace(/^['"]|['"]$/g,'');
    if(content)items.push({type:'text',text:content,x:r.left+left,y:r.top+top,
      w:Math.max(w,parseFloat(s.fontSize)),h:parseFloat(s.fontSize)*1.3,...textStyle(s)});
  };
  const textNode = (n,s) => {
    const raw=n.textContent;
    if(!raw.trim())return;
    const start=raw.length-raw.trimStart().length,end=raw.trimEnd().length;
    const range=document.createRange(),lines=[];
    for(let i=start;i<end;i++) {
      range.setStart(n,i);range.setEnd(n,i+1);
      const r=range.getBoundingClientRect();
      if(!r.width||!r.height||raw[i]==='\n')continue;
      let line=lines[lines.length-1];
      if(!line||Math.abs(line.y-r.y)>1) {
        line={type:'text',text:'',...box(r),...textStyle(s)};lines.push(line);
      }
      line.text+=/\s/.test(raw[i])?' ':raw[i];
      line.w=r.right-line.x;line.h=Math.max(line.h,r.height);
    }
    items.push(...lines.filter(l=>l.text.trim()));
  };
  for(const e of slide.querySelectorAll('*')) {
    if(e.closest('aside,script,style,template')||(e.closest('svg')&&e.tagName.toLowerCase()!=='svg'))continue;
    const r=e.getBoundingClientRect(),s=getComputedStyle(e);
    if(!r.width||!r.height||s.visibility==='hidden'||s.display==='none')continue;
    if(e.tagName==='IMG') {
      let b=box(r);
      if(s.objectFit==='contain'&&e.naturalWidth) {
        const scale=Math.min(b.w/e.naturalWidth,b.h/e.naturalHeight);
        const w=e.naturalWidth*scale,h=e.naturalHeight*scale;
        b.x+=(b.w-w)/2;b.y+=(b.h-h)/2;b.w=w;b.h=h;
      }
      items.push({type:'image',src:e.src,...b});continue;
    }
    if(e.tagName.toLowerCase()==='svg') {
      const clone=e.cloneNode(true),a=[e,...e.querySelectorAll('*')],b=[clone,...clone.querySelectorAll('*')];
      a.forEach((node,i)=>{const cs=getComputedStyle(node);
        ['fill','stroke','stroke-width','font-family','font-size','font-weight','color'].forEach(k=>b[i].style.setProperty(k,cs.getPropertyValue(k)));
      });
      items.push({type:'svg',src:clone.outerHTML,...box(r)});continue;
    }
    fill(box(r),s);before(e);
    for(const n of e.childNodes)if(n.nodeType===3)textNode(n,s);
  }
  const merged=[];
  for(const item of items) {
    const prev=merged[merged.length-1];
    if(item.type==='text'&&prev?.type==='text'&&Math.abs(item.y-prev.y)<.6&&
       Math.abs(item.x-(prev.x+prev.w))<.75&&
       ['font','size','bold','italic','color'].every(k=>item[k]===prev[k])) {
      prev.text+=item.text;prev.w=item.x+item.w-prev.x;prev.h=Math.max(prev.h,item.h);
    } else merged.push(item);
  }
  return {notes:slide.querySelector('aside.notes')?.textContent||'',items:merged,
    bg:getComputedStyle(document.body).backgroundColor};
}

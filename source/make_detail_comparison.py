"""Lay out unaltered editor captures as a portable SVG and interactive HTML."""
from pathlib import Path
import base64
P=Path(__file__).resolve().parent.parent/'previews/detail_v1'
def uri(name): return 'data:image/png;base64,'+base64.b64encode((P/name).read_bytes()).decode()
images={n:uri(n+'.png') for n in ('before_full','after_full','before_detail','after_detail')}
svg=['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="2000" height="1140" viewBox="0 0 2000 1140">',
     '<rect width="2000" height="1140" fill="#15191e"/>',
     '<g fill="white" font-family="Arial,sans-serif"><text x="32" y="44" font-size="30">Actual box body upgrade — matching GIANTS Editor captures</text>',
     '<text x="32" y="91" font-size="24">BEFORE</text><text x="1016" y="91" font-size="24">AFTER</text></g>']
for name,x,y,w,h,crop in [('before_full',32,110,952,550,'350 220 1350 780'),('after_full',1016,110,952,550,'350 220 1350 780'),
                        ('before_detail',32,714,952,330,'180 690 1650 400'),('after_detail',1016,714,952,330,'180 690 1650 400')]:
    svg.append(f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{crop}" preserveAspectRatio="xMidYMid slice"><image width="2032" height="1096" xlink:href="{images[name]}"/></svg>')
svg+=['<g fill="#d8dfe7" font-family="Arial,sans-serif" font-size="23"><text x="32" y="696">Curtain and hardware close-up</text>',
      '<text x="32" y="1090">New cloth relief, welded hems, rounded buckle frames, rail trim, fasteners and door seals.</text>',
      '<text x="32" y="1122" font-size="19">Editor previews. In-game lighting may differ. No retouching or AI-generated truck imagery in this comparison.</text></g></svg>']
(P/'before_after.svg').write_text(''.join(svg),encoding='utf-8')
html='''<!doctype html><meta charset="utf-8"><title>Box body: before and after</title>
<style>body{margin:0;background:#15191e;color:#eef3f8;font:18px Arial}main{padding:24px}h1{font-size:26px}nav{display:flex;gap:16px;align-items:center;margin:20px 0}button{padding:10px 16px;cursor:pointer}section{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0;overflow:auto}figcaption{padding:12px;background:#252d37;font-weight:bold}img{display:block;width:100%;max-width:none}p{color:#c0c9d3}</style>
<main><h1>Box body: actual before and after</h1><p>Matching camera and editor lighting. Use Close-up to inspect the buckles and seams; zoom to see the original pixels.</p>
<nav><button onclick="show('full')">Whole truck</button><button onclick="show('detail')">Close-up</button><label>Zoom <input type="range" min="100" max="250" value="100" oninput="document.querySelectorAll('img').forEach(i=>i.style.width=this.value+'%')"></label></nav>
<section><figure><figcaption>BEFORE</figcaption><img id="before" src="before_full.png"></figure><figure><figcaption>AFTER</figcaption><img id="after" src="after_full.png"></figure></section>
<p>Upgraded curtain surface, fabric maps, rounded buckle hardware, rail trim, fasteners, and door seals. These are actual GIANTS Editor captures; in-game lighting may differ.</p></main>
<script>function show(view){for(const side of ['before','after'])document.getElementById(side).src=side+'_'+view+'.png'}</script>'''
(P/'before_after.html').write_text(html,encoding='utf-8')
print('Created before_after.svg and before_after.html')

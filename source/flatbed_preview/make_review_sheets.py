"""Arrange the unaltered GIANTS Editor captures for review."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops
import xml.etree.ElementTree as ET
import json

root=Path(__file__).resolve().parents[2]
out=root/'previews/flatbed_fitted_v1'
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25)
title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',36)
def framed(path):
    im=Image.open(path).convert('RGB')
    region=im.crop((0,30,im.width,im.height-55))
    bg=Image.new('RGB',region.size,region.getpixel((region.width-1,0)))
    mask=ImageChops.difference(region,bg).convert('L').point(lambda p:255 if p>24 else 0)
    bounds=mask.getbbox()
    if bounds:
        x0,y0,x1,y1=bounds
        region=region.crop((max(0,x0-45),max(0,y0-35),min(region.width,x1+45),min(region.height,y1+35)))
    region.thumbnail((1080,570))
    tile=Image.new('RGB',(1100,580),(163,163,163))
    tile.paste(region,((1100-region.width)//2,(580-region.height)//2))
    return tile

for kind in ['boards','stakes']:
    sheet=Image.new('RGB',(2240,1400),(28,35,44)); d=ImageDraw.Draw(sheet)
    heading='Folding side boards' if kind=='boards' else 'Sliding stakes'
    d.text((25,18),'FLATBED | '+heading,fill='white',font=title)
    d.text((25,65),'Fitted to the actual Volvo FH16 8x4 Tag | review model only | no roof spoiler',fill=(195,210,220),font=font)
    views=[('closed_side','Closed: boards raised' if kind=='boards' else 'Closed: six stakes per side'),
           ('open_side','Open: boards folded; fixed posts stay up' if kind=='boards' else 'Open: stakes 1, 3, 5 move forward into pairs'),
           ('closed_front34','Front three-quarter'),('open_rear34','Open: rear three-quarter')]
    for i,(key,label) in enumerate(views):
        x=20+(i%2)*1110; y=115+(i//2)*635
        d.text((x+8,y),label,fill='white',font=font)
        sheet.paste(framed(out/f'{kind}_{key}_v2_fitted.png'),(x,y+36))
    d.text((25,1370),'Geometry and poses shown in GIANTS Editor. Materials provisional; gameplay and clearances untested.',fill=(195,210,220),font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20))
    sheet.save(out/f'{kind}_fitted_review_v2.png')

i3d=ET.parse(out/'flatbedPreview.i3d').getroot()
nodes=list(i3d.find('Scene').iter())
hinges=[n for n in nodes if n.get('name','').startswith('Board hinge ') and 'barrel' not in n.get('name','')]
stakes=[n for n in nodes if n.tag=='TransformGroup' and n.get('name','').startswith('Stake ')]
assert len(hinges)==6,len(hinges)
assert len(stakes)==12,len(stakes)
for kind in ['boards','stakes']:
    for key in ['closed_side','open_side','open_rear34','closed_rear34','closed_front34','closed_rear']:
        with Image.open(out/f'{kind}_{key}_v2_fitted.png') as im:
            im.verify()
assert (out/'flatbedPreview.i3d.shapes').stat().st_size>0
result={'verification':'XML structure and screenshot files; poses visually inspected in GIANTS Editor',
        'preview_only':True,'board_hinges':6,'stakes':12,'deck_m':[2.55,6.85],
        'deck_top_root_m':1.62,'headboard_top_root_m':3.738,
        'gameplay':'UNTESTED','runtime_files_changed':False}
(out/'validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))

# Draws the sticker sheet for the inside of the right rear door (our own simple drawings, no brand marks):
# three orange warning triangles, a blue round info sticker, a white load-securing plate and a small parts list.
# -> boxTruckStickers_diffuse.dds (DXT5 with alpha, 512 x 1024, mipmaps). The decal quad (build_body.py
# decal_inside) maps the whole sheet onto 0.42 x 0.60 m.
# Usage: python -I make_sticker_texture.py <out folder>
import sys, os
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dds_util import save_dds_mips

out = sys.argv[1]
W, H = 512, 1024
img = Image.new('RGBA', (W, H), (255, 255, 255, 0))
d = ImageDraw.Draw(img)
bold = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 40)
small = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 15)
ORANGE, BLACK, BLUE, WHITE = (245, 150, 20, 255), (20, 20, 20, 255), (20, 70, 160, 255), (245, 245, 240, 255)
def triangle(cx, cy, s, mark):
    pts = [(cx, cy - s * 0.58), (cx - s / 2, cy + s * 0.29), (cx + s / 2, cy + s * 0.29)]
    d.polygon(pts, fill=BLACK)
    inner = [(cx, cy - s * 0.58 + 14), (cx - s / 2 + 12, cy + s * 0.29 - 7), (cx + s / 2 - 12, cy + s * 0.29 - 7)]
    d.polygon(inner, fill=ORANGE)
    d.text((cx, cy + 2), mark, font=bold, fill=BLACK, anchor='mm')
for i, mark in enumerate(('!', '\u2195', '\u21C4')):
    triangle(310, 120 + i * 190, 170, mark)
# blue round sticker
d.ellipse((40, 300, 190, 450), fill=WHITE); d.ellipse((50, 310, 180, 440), fill=BLUE)
d.text((115, 360), 'MAX', font=bold, fill=WHITE, anchor='mm'); d.text((115, 400), '24 t', font=small, fill=WHITE, anchor='mm')
# load securing plate
d.rounded_rectangle((60, 640, 450, 960), 12, fill=WHITE, outline=BLACK, width=4)
d.rectangle((60, 640, 450, 700), fill=BLUE)
d.text((255, 670), 'LOAD SECURING', font=ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', 28), fill=WHITE, anchor='mm')
for k in range(8):
    y = 725 + k * 28
    d.line((85, y, 85 + (330 if k % 3 else 220), y), fill=(90, 90, 90, 255), width=6)
# parts list
d.rounded_rectangle((40, 40, 200, 250), 8, fill=WHITE, outline=BLACK, width=3)
for k in range(9):
    d.line((55, 65 + k * 20, 185 - (k % 3) * 25, 65 + k * 20), fill=(60, 60, 60, 255), width=4)
n = save_dds_mips(img, os.path.join(out, 'boxTruckStickers_diffuse.dds'), 'DXT5')
img.save(os.path.join(out, 'boxTruckStickers_diffuse.png'))
print('stickers mips', n)

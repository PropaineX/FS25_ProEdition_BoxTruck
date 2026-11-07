import sys
from PIL import Image, ImageDraw, ImageFont
SHOT = r'C:\Users\groov\AppData\Local\Temp\claude\9f07c4f8ffeebdb3\a71d825e-0d5a-4ca0-a191-3c29b7576d65\images\3.png'
src = Image.open(SHOT).convert('RGB')
store = Image.open('store_boxTruck.png').convert('RGBA'); store = store.crop(store.getbbox())
def font(sz):
    for f in ('arialbd.ttf', 'arial.ttf'):
        try: return ImageFont.truetype(f, sz)
        except: pass
BG = (34, 34, 34); WHITE = (234, 237, 224); GREEN = (143, 190, 30)
# template: Winston's section (heading + tile row)
Y0, Y1 = 432, 844
sec = src.crop((0, Y0, src.width, Y1)).copy(); d = ImageDraw.Draw(sec)
# wipe the Winston logo: per column, blend between the clean card rows above and below it
TOP, BOT = 557 - Y0, 797 - Y0
for x in range(146, 440):
    a = sec.getpixel((x, TOP)); b = sec.getpixel((x, BOT))
    for y in range(TOP + 1, BOT):
        f = (y - TOP) / (BOT - TOP)
        sec.putpixel((x, y), tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3)))
# wipe heading and tile title
d.rectangle([130, 470 - Y0, 760, 515 - Y0], fill=BG)
for y in range(758 - Y0, 790 - Y0):
    c = sec.getpixel((420, y)); d.line([(150, y), (438, y)], fill=c)
# new heading + tile text
d.text((139, 478 - Y0), 'PROPAINEX PRO EDITION', font=font(27), fill=WHITE)
d.text((159, 740 - Y0), 'CATEGORY', font=font(17), fill=(122, 160, 22))
d.text((159, 762 - Y0), 'PRO EDITION TRUCKS', font=font(20), fill=WHITE)
# truck picture in the tile
bw, bh = 235, 168
s = min(bw / store.width, bh / store.height); im = store.resize((int(store.width * s), int(store.height * s)), Image.LANCZOS)
sec.paste(im, (292 - im.width // 2, 733 - Y0 - im.height), im)
# put it in right after DRIVABLES
CUT = 430
out = Image.new('RGB', (src.width, src.height + (Y1 - Y0)), BG)
out.paste(src.crop((0, 0, src.width, CUT)), (0, 0))
out.paste(sec, (0, CUT))
out.paste(src.crop((0, CUT, src.width, src.height)), (0, CUT + (Y1 - Y0)))
dd = ImageDraw.Draw(out)
dd.rectangle([0, out.height - 60, 1240, out.height], fill=(0, 0, 0))
dd.text((20, out.height - 46), 'MOCK-UP: new section added to your shop screenshot (its exact position among the mod sections depends on load order)', font=font(17), fill=(255, 210, 0))
out.save(sys.argv[1]); print(out.size)

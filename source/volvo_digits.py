"""Badge digits rendered from a font and fitted to the FH16 decal digits: 75 px tall, each digit as wide as the
game's own digit of the same shape class (0/6/8 ~ 94 px), which also gives the thick-upright / thin-bar contrast."""
from PIL import Image, ImageDraw, ImageFont
H = 75
TARGET_W = {'0': 94, '2': 90, '4': 92, '5': 90, '6': 94, '7': 87, '8': 93, '1': 34}

def render(font_path, ch, size=400):
    f = ImageFont.truetype(font_path, size)
    im = Image.new('L', (size * 2, size * 2), 0)
    ImageDraw.Draw(im).text((size // 4, size // 4), ch, fill=255, font=f)
    return im.crop(im.getbbox())

def fitted(font_path, ch, ref_h=None):
    g = render(font_path, ch)
    h = H
    if ch == '1':   # keep the 1's own proportions, just the height
        w = max(1, round(g.width * h / g.height))
    else:
        w = TARGET_W[ch]
    return g.resize((w, h), Image.LANCZOS)

def number(glyphs, s, gap=10):
    parts = [glyphs[c] for c in s]
    w = sum(p.width for p in parts) + gap * (len(parts) - 1)
    m = Image.new('L', (w, H), 0); x = 0
    for p in parts: m.paste(p, (x, 0)); x += p.width + gap
    return m

from PIL import ImageChops

def volvo_weight(font_path, ch, dx=5, dy=2):
    """Michroma digit with the FH16 badge contrast: uprights widened by dx px (sideways spread), bars thinned by dy px."""
    g = render(font_path, ch)
    w = (TARGET_W[ch] if ch != '1' else max(1, round(g.width * (H + dy) / g.height))) - dx
    g = g.resize((w, H + dy), Image.LANCZOS)
    wide = Image.new('L', (w + dx, H + dy), 0)
    for i in range(dx + 1):
        wide = ImageChops.lighter(wide, _shift(g, i, 0, w + dx, H + dy))
    thin = Image.new('L', (w + dx, H + dy), 255)
    for j in range(dy + 1):
        thin = ImageChops.darker(thin, _shift(wide, 0, -j, w + dx, H + dy, fill=0))
    return thin.crop((0, 0, w + dx, H))

def _shift(img, x, y, W, Hh, fill=0):
    c = Image.new('L', (W, Hh), fill); c.paste(img, (x, y)); return c

# Builds the engine badge textures (boxTruckBadges_diffuse.dds / _normal.dds, 512 x 256, DXT5 / DXT1 with mipmaps).
# Cells (top row, 101 x 76 like the FH16's own "0" cell): 4 2 5 1 8 in Michroma (SIL OFL 1.1, fonts/OFL.txt) at the
# FH16 badge weight; below: the EURO 6 plate copied from the game's fh16Decals texture.
# Usage: python -I make_badge_textures.py <game fh16 folder> <out folder>
import sys, os
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from volvo_digits import volvo_weight
from dds_util import save_dds_mips

game, out = sys.argv[1:3]
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'Michroma-Regular.ttf')
W, H = 512, 256
CELL_W, CELL_H = 101, 76
DIGITS = '42518'
EURO_SRC_D = (298, 295, 507, 341)   # in fh16Decals_diffuse (1024)
EURO_SRC_N = (296, 33, 508, 81)     # in fh16Decals_normal (512)
EURO_POS = (0, 100)

atlas = Image.open(os.path.join(game, 'fh16Decals_diffuse.dds')).convert('RGBA')
natlas = Image.open(os.path.join(game, 'fh16Decals_normal.dds')).convert('RGB')
# chrome letter colour = average RGB of the game's "0"
zero = atlas.crop((197, 269, 291, 344)); px = [p for p in zero.getdata() if p[3] > 200]
rgb = tuple(round(sum(c[i] for c in px) / len(px)) for i in range(3))

alpha = Image.new('L', (W, H), 0)
cells = {}
for i, ch in enumerate(DIGITS):
    g = volvo_weight(FONT, ch)
    x = i * CELL_W + (CELL_W - g.width) // 2; y = (CELL_H - g.height) // 2
    alpha.paste(g, (x, y))
    cells[ch] = (i * CELL_W, 0, (i + 1) * CELL_W, CELL_H)
diffuse = Image.new('RGBA', (W, H), rgb + (0,)); diffuse.putalpha(alpha)
euro = atlas.crop(EURO_SRC_D); diffuse.paste(euro, EURO_POS)
cells['EURO'] = (EURO_POS[0], EURO_POS[1], EURO_POS[0] + euro.width, EURO_POS[1] + euro.height)

# normal map: flat (127,132,255) + edge bevel from the letter alpha, same directions as the game's
# (left edge R low, right edge R high, top edge G high, bottom edge G low)
a = alpha.filter(ImageFilter.GaussianBlur(0.6)); ap = a.load()
normal = Image.new('RGB', (W, H), (127, 132, 255)); np_ = normal.load()
for y in range(1, CELL_H + 2):
    for x in range(1, W - 1):
        gx = (ap[x + 1, y] - ap[x - 1, y]) / 2.0; gy = (ap[x, y + 1] - ap[x, y - 1]) / 2.0
        if gx or gy:
            r = max(0, min(255, round(127 - 0.5 * gx))); gg = max(0, min(255, round(132 + 0.5 * gy)))
            np_[x, y] = (r, gg, 239 if abs(gx) + abs(gy) > 40 else 255)
neuro = natlas.crop(EURO_SRC_N).resize(euro.size, Image.LANCZOS); normal.paste(neuro, EURO_POS)

n1 = save_dds_mips(diffuse, os.path.join(out, 'boxTruckBadges_diffuse.dds'), 'DXT5')
n2 = save_dds_mips(normal.convert('RGBA'), os.path.join(out, 'boxTruckBadges_normal.dds'), 'DXT1')
diffuse.save(os.path.join(out, 'boxTruckBadges_diffuse_check.png')); normal.save(os.path.join(out, 'boxTruckBadges_normal_check.png'))
print('letter colour', rgb, '| mip levels', n1, n2)
print('CELLS', {k: v for k, v in cells.items()})

# Builds the "ProEdition" curtain decal: the PRO EDITION banner (Library\_ProEditionBanner\add_banner.py) with a gentle
# wave, on a transparent background -> boxTruckProEditionCurtain_diffuse.dds (DXT5, 4096 x 1024, mipmaps).
# The decal quads (build_body.py, curtainLeft/RightProEdition) map the whole texture onto BANNER_W x BANNER_H metres.
# Usage: python -I make_curtain_texture.py <_ProEditionBanner folder> <out folder>
import sys, os, math
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dds_util import save_dds_mips

banner_dir, out = sys.argv[1:3]
sys.path.insert(0, banner_dir)
from add_banner import make_banner

AMP, WAVES = 38, 1.6            # wave height (px at banner width 3700) and number of waves: approved 2026-10-22 (v2)
ban = make_banner(3700 / 432)
bw, bh = ban.size
pad = AMP * 2
wav = Image.new('RGBA', (bw, bh + 2 * pad), (0, 0, 0, 0))
src, dst = ban.load(), wav.load()
for x in range(bw):
    t = x / bw
    phase = 2 * math.pi * WAVES * t
    dy = AMP * math.sin(phase) * (0.6 + 0.4 * t)        # a little more movement towards the loose end
    shade = 1 + 0.10 * math.cos(phase)                    # slopes catch the light / fall in shade
    for y in range(bh + 2 * pad):
        sy = y - pad - dy
        y0 = int(math.floor(sy)); f = sy - y0
        if 0 <= y0 < bh - 1:
            a, b = src[x, y0], src[x, y0 + 1]
            c = [a[k] * (1 - f) + b[k] * f for k in range(4)]
            dst[x, y] = (min(255, int(c[0] * shade)), min(255, int(c[1] * shade)), min(255, int(c[2] * shade)), int(c[3]))
print('banner %d x %d px (aspect %.4f)' % (wav.width, wav.height, wav.width / wav.height))
tex = wav.resize((4096, 1024), Image.LANCZOS)
# transparent pixels keep the banner's edge colour, so mipmaps don't bleed black
rgb = Image.new('RGBA', tex.size, (206, 16, 24, 0)); rgb.alpha_composite(tex)
n = save_dds_mips(rgb, os.path.join(out, 'boxTruckProEditionCurtain_diffuse.dds'), 'DXT5')
print('mip levels', n)

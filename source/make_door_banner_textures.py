# Rear door PRO EDITION banner (user, 2026-10-24, preview previews\rear_banner_v2_preview.png): the same waving banner
# as the ProEdition curtain (make_curtain_texture.py), centred on the door seam, split in two: each door shows only its
# half and stops SEAM_GAP_M short of the seam, so the line where the doors meet stays visible through the banner.
# The door decals reuse the curtain decal quad (whole texture on it), so each texture is the whole banner with the
# other door's half transparent: boxTruckProEditionDoorLeft_diffuse.dds (truck left = +x = the reader's left from
# behind = "PRO ED") and boxTruckProEditionDoorRight_diffuse.dds. DXT5, 2048 x 512 (the door banner is 2.14 m wide).
# Usage: python -I make_door_banner_textures.py <_ProEditionBanner folder> <out folder>
import sys, os, math
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dds_util import save_dds_mips

banner_dir, out = sys.argv[1:3]
sys.path.insert(0, banner_dir)
from add_banner import make_banner

BANNER_W = 2.144          # metres on the doors: 85 % of the 2.523 m between the hinges
SEAM_GAP_M = 0.01         # each half stops 1 cm short of the seam
TEX_W, TEX_H = 2048, 512

# the curtain's waving banner, exactly as make_curtain_texture.py draws it
AMP, WAVES = 38, 1.6
ban = make_banner(3700 / 432)
bw, bh = ban.size
pad = AMP * 2
wav = Image.new('RGBA', (bw, bh + 2 * pad), (0, 0, 0, 0))
src, dst = ban.load(), wav.load()
for x in range(bw):
    t = x / bw
    phase = 2 * math.pi * WAVES * t
    dy = AMP * math.sin(phase) * (0.6 + 0.4 * t)
    shade = 1 + 0.10 * math.cos(phase)
    for y in range(bh + 2 * pad):
        sy = y - pad - dy
        y0 = int(math.floor(sy)); f = sy - y0
        if 0 <= y0 < bh - 1:
            a, b = src[x, y0], src[x, y0 + 1]
            c = [a[k] * (1 - f) + b[k] * f for k in range(4)]
            dst[x, y] = (min(255, int(c[0] * shade)), min(255, int(c[1] * shade)), min(255, int(c[2] * shade)), int(c[3]))
tex = wav.resize((TEX_W, TEX_H), Image.LANCZOS)

gap_px = round(SEAM_GAP_M / BANNER_W * TEX_W)
cut_left = TEX_W // 2 - gap_px          # left door keeps u < 0.5 - gap
cut_right = TEX_W // 2 + gap_px         # right door keeps u > 0.5 + gap
for name, keep in (('Left', (0, cut_left)), ('Right', (cut_right, TEX_W))):
    half = Image.new('RGBA', tex.size, (0, 0, 0, 0))
    half.paste(tex.crop((keep[0], 0, keep[1], TEX_H)), (keep[0], 0))
    # transparent pixels keep the banner's edge colour, so mipmaps don't bleed black
    rgb = Image.new('RGBA', half.size, (206, 16, 24, 0)); rgb.alpha_composite(half)
    path = os.path.join(out, 'boxTruckProEditionDoor%s_diffuse.dds' % name)
    n = save_dds_mips(rgb, path, 'DXT5')
    rgb.save(os.path.join(out, 'boxTruckProEditionDoor%s_check.png' % name))
    print(path, 'keeps x', keep, 'mips', n)
print('gap %d px each side of the seam' % gap_px)

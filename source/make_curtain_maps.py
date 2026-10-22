# Builds our own closed-curtain textures (no game or third-party art):
#   boxTruckCurtain_diffuse.dds  greyscale shading (folds, pull lines at the buckles), DXT1; the paint colour comes
#                                from the material's colorScale
#   boxTruckCurtain_normal.dds   matching normal map, DXT1
# Both 4096 x 1024 = the whole closed curtain (CURTAIN_LEN x CURTAIN_H, u from the front edge, v = 1 at the top).
# Usage: python -I make_curtain_maps.py <out folder> [preview.png]
import sys, os, math
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dds_util import save_dds_mips

out = sys.argv[1]
W, H = 4096, 1024
CURTAIN_LEN, CURTAIN_H = 6.72, 2.53          # metres, build_body.py curtain cloth (CURTAIN_FRONT_Z..REAR_Z, CLOTH_Y0..Y1)
BAND_V = 0.295                                # top of the dark band above the cloth's lower edge (BAND_Y + 0.045 - CLOTH_Y0)
BUCKLE_PITCH = 0.33                           # metres between the skirt buckles (build_body.py BUCKLE_PITCH)
rng = np.random.default_rng(1966)

u = (np.arange(W) + 0.5) / W * CURTAIN_LEN    # metres along the curtain
v = (np.arange(H) + 0.5) / H * CURTAIN_H      # metres up from the bottom edge (row 0 = top -> flip later)
U, V = np.meshgrid(u, v)
h = np.zeros_like(U)

# 1. gathered folds under the top rail: many narrow folds, deep at the top, fading out 0.6 m down
for k in range(60):
    period = rng.uniform(0.05, 0.14); phase = rng.uniform(0, 2 * math.pi); amp = rng.uniform(0.3, 1.0)
    depth = rng.uniform(0.25, 0.65)
    fade = np.clip((V - (CURTAIN_H - depth)) / depth, 0, 1) ** 1.6
    start, length = rng.uniform(0, CURTAIN_LEN), rng.uniform(0.3, 1.4)
    mask = np.clip(1 - np.abs(U - start) / (length / 2), 0, 1) ** 0.5
    h += amp * fade * mask * np.sin(2 * math.pi * U / period + phase)
# 2. long soft waves over the whole panel (the cloth never hangs perfectly flat)
for k in range(14):
    period = rng.uniform(0.35, 0.9); phase = rng.uniform(0, 2 * math.pi)
    tilt = rng.uniform(-0.08, 0.08)
    h += 0.35 * np.sin(2 * math.pi * (U + tilt * V) / period + phase) * (0.6 + 0.4 * V / CURTAIN_H)
# 3. pull lines: the buckle straps pull the hem down, V-shaped creases above each buckle
for bx in np.arange(BUCKLE_PITCH / 2, CURTAIN_LEN, BUCKLE_PITCH):
    reach = rng.uniform(0.25, 0.45)
    d = np.abs(U - bx) - 0.6 * np.clip(V - BAND_V, 0, None)
    crease = np.exp(-(d / 0.025) ** 2) * np.clip(1 - (V - BAND_V) / reach, 0, 1) * (V > BAND_V)
    h -= 0.9 * crease
# 4. fine fabric noise
h += 0.06 * rng.standard_normal(h.shape)

# smooth a little so the normal map has no pixel noise
def blur(a, sigma):
    r = int(3 * sigma) + 1
    k = np.exp(-(np.arange(-r, r + 1) / sigma) ** 2 / 2); k /= k.sum()
    a = np.apply_along_axis(lambda m: np.convolve(np.pad(m, r, mode='edge'), k, 'valid'), 1, a)
    return np.apply_along_axis(lambda m: np.convolve(np.pad(m, r, mode='edge'), k, 'valid'), 0, a)
h = (h - h.min()) / (h.max() - h.min()) * 255
h = blur(h, 1.2)
h = h[::-1]                                   # row 0 = top of the curtain

# normal map (OpenGL-style like the game's: R right, G up)
STRENGTH = 0.045
gy, gx = np.gradient(h)
nx, ny, nz = -gx * STRENGTH, gy * STRENGTH, np.ones_like(h)
n = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
normal = np.stack([(nx / n * 0.5 + 0.5), (ny / n * 0.5 + 0.5), (nz / n * 0.5 + 0.5)], -1)
normal_img = Image.fromarray((normal * 255).clip(0, 255).astype(np.uint8))

# shading: cavities (below the local average) darker, a soft shadow band under the top rail
blur10 = blur(h, 10)
cav = np.clip((h - blur10) / 40.0, -1, 1)
shade = 0.93 + 0.10 * cav
top = np.clip(1 - (np.arange(H) / H) / 0.06, 0, 1)[:, None]      # shadow of the top rail lip
shade *= 1 - 0.22 * top
shade = np.clip(shade, 0, 1)
diffuse_img = Image.fromarray((shade * 255).astype(np.uint8)).convert('RGB')

n1 = save_dds_mips(diffuse_img.convert('RGBA'), os.path.join(out, 'boxTruckCurtain_diffuse.dds'), 'DXT1')
n2 = save_dds_mips(normal_img.convert('RGBA'), os.path.join(out, 'boxTruckCurtain_normal.dds'), 'DXT1')
diffuse_img.save(os.path.join(out, 'boxTruckCurtain_diffuse.png')); normal_img.save(os.path.join(out, 'boxTruckCurtain_normal.png'))
print('curtain maps', W, H, 'mips', n1, n2)

"""Weathered flatbed deck planks, v4 (v3, a touch darker per user) (own procedural artwork, PropaineX 2026-11-06).

Atlas 2048 x 2048 = 8 plank strips of 2048 x 256 px. One strip = 3.40 m of plank (u) x 0.155 m (v),
so each 6.73 m plank shows a strip about twice. Features are drawn in metres, so nothing is stretched.
Outputs (diffuse + height-derived normal) into the folder given as argv[1].
Run: python -I weathered_deck_v1.py <out_dir>
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
W, H, N = 2048, 256, 8
LEN_M, WID_M = 3.40, 0.155
PXU, PXV = W / LEN_M, H / WID_M   # px per metre along / across the plank
rng = np.random.default_rng(20261106)

def noise(w, h, cells_u, cells_v, seed):
    """Smooth value noise in [0,1], cells counted along u and v."""
    r = np.random.default_rng(seed)
    g = r.random((max(2, int(cells_v)) + 1, max(2, int(cells_u)) + 1)).astype(np.float32)
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(im, np.float32) / 255.0

def fbm(w, h, cu, cv, seed, octaves=4):
    out = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        out += amp * noise(w, h, cu * 2 ** o, cv * 2 ** o, seed + o); tot += amp; amp *= 0.5
    return out / tot

def strip(k):
    s = 1000 * (k + 1)
    v = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    u = np.linspace(0, 1, W, dtype=np.float32)[None, :]
    # grain: long streaks along the plank, wavy
    warp = (fbm(W, H, 6, 2, s + 1) - 0.5) * 0.25
    grain_lines = np.sin((v + warp + 0.04 * fbm(W, H, 40, 6, s + 9)) * np.pi * 2 * rng.uniform(9, 15)) * 0.5 + 0.5
    grain_fine = fbm(W, H, 10, 110, s + 2, 3)   # long streaks: few cells along, many across
    grain = 0.35 * (1 - grain_lines ** 6) + 0.65 * grain_fine
    tone = fbm(W, H, 5, 1.5, s + 3)                     # slow tone change along the board
    # weathered grey-brown base, each plank a bit different
    base = np.array([0.315, 0.262, 0.205]) * rng.uniform(0.82, 1.06) + np.array([1.0, 0.7, 0.4]) * rng.normal(0, 0.012)
    col = np.ones((H, W, 3), np.float32) * base
    col *= (0.80 + 0.30 * tone)[..., None]
    col *= (0.74 + 0.36 * grain)[..., None]
    height = 0.5 + 0.35 * (grain - 0.5)
    # sun bleaching toward grey on the upper face
    bleach = np.clip(fbm(W, H, 8, 2, s + 4) * 1.4 - 0.45, 0, 1)[..., None] * 0.22
    col = col * (1 - bleach) + np.array([0.56, 0.55, 0.52]) * bleach
    # worn, darker edges along both long sides
    edge = np.clip(1 - np.minimum(v, 1 - v) / 0.09, 0, 1) ** 1.6
    edge = edge * (0.7 + 0.6 * fbm(W, H, 40, 2, s + 5))
    col *= (1 - 0.38 * edge)[..., None]
    height -= 0.25 * edge
    # dirt / oil stains: low frequency dark blotches
    stains = np.clip(fbm(W, H, 10, 3, s + 6) * 2.1 - 0.95, 0, 1)
    grime = np.clip(fbm(W, H, 60, 8, s + 8) * 1.6 - 0.6, 0, 1) * 0.25
    col *= (1 - 0.65 * stains - grime)[..., None]
    col = col * (1 - 0.25 * stains[..., None]) + np.array([0.16, 0.12, 0.08]) * 0.25 * stains[..., None]
    img = (np.clip(col, 0, 1) * 255).astype(np.uint8)
    hgt = height.copy()

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # knots (round in metres)
    for _ in range(rng.integers(1, 4)):
        cu, cv = rng.uniform(0, W), rng.uniform(0.25, 0.75) * H
        r = rng.uniform(0.010, 0.022)
        d = np.sqrt(((xx - cu) / (r * PXU * 1.6)) ** 2 + ((yy - cv) / (r * PXV)) ** 2)
        ring = (np.sin(d * 9) * 0.5 + 0.5) * np.exp(-d * 1.1)
        core = np.clip(1.2 - d, 0, 1)
        dark = np.clip(0.55 * core + 0.25 * ring, 0, 0.8)[..., None]
        img = (img * (1 - dark) + np.array([45, 32, 22]) * dark).astype(np.uint8)
        hgt -= 0.2 * core
    # cracks / splits along the grain
    for _ in range(rng.integers(3, 8)):
        x0 = rng.uniform(0, W); length = rng.uniform(0.15, 0.9) * PXU; y0 = rng.uniform(0.1, 0.9) * H
        t = np.clip((xx - x0) / length, 0, 1); inside = (xx >= x0) & (xx <= x0 + length)
        ypath = y0 + np.sin(t * rng.uniform(2, 5)) * rng.uniform(2, 8)
        width = (1 - np.abs(t * 2 - 1)) * rng.uniform(1.2, 3.0) + 0.3
        m = inside & (np.abs(yy - ypath) < width)
        img[m] = (img[m] * 0.25).astype(np.uint8); hgt[m] -= 0.6
    # scuffs and scrapes: short light marks, mostly across and diagonal (pallet forks, chains)
    for _ in range(rng.integers(10, 20)):
        cx, cy = rng.uniform(0, W), rng.uniform(0, H)
        ang = rng.choice([rng.uniform(-0.25, 0.25), rng.uniform(-1.2, 1.2)]); L = rng.uniform(0.02, 0.09)
        dx, dy = np.cos(ang) * L * PXU, np.sin(ang) * L * PXV
        tt = np.clip(((xx - cx) * dx + (yy - cy) * dy) / (dx * dx + dy * dy + 1e-6), 0, 1)
        dist = np.hypot(xx - (cx + tt * dx), yy - (cy + tt * dy))
        soft = np.clip(1 - dist / rng.uniform(2.0, 4.0), 0, 1)[..., None] * rng.uniform(0.10, 0.22)
        img = (img * (1 - soft) + np.array([176, 166, 150]) * soft).astype(np.uint8); hgt -= 0.15 * soft[..., 0]
    # rusty nail holes in pairs every ~0.85 m (crossmembers)
    for x in np.arange(rng.uniform(0.1, 0.4), LEN_M, 0.85) * PXU:
        for fy in (0.3, 0.7):
            d = np.hypot((xx - x) / PXU, (yy - fy * H) / PXV)
            rust = np.clip(1 - d / 0.012, 0, 1)[..., None] * 0.7
            img = (img * (1 - rust) + np.array([92, 52, 28]) * rust).astype(np.uint8)
            hole = d < 0.0025
            img[hole] = (20, 16, 14); hgt[hole] -= 0.5
    return img, hgt

def seamless(a):
    # fade both ends toward the shared column at the wrap so the strip tiles along the board (grain runs along u)
    n = int(W * 0.12); a = a.astype(np.float32)
    edge = (a[:, :1] + a[:, -1:]) / 2
    t = np.linspace(0, 1, n, dtype=np.float32) ** 2
    t = t.reshape((1, n) + (1,) * (a.ndim - 2))
    a[:, W - n:] = a[:, W - n:] * (1 - t) + edge * t
    a[:, :n] = a[:, :n] * (1 - t[:, ::-1]) + edge * t[:, ::-1]
    return a

imgs, hgts = zip(*[strip(k) for k in range(N)])
imgs = [np.clip(seamless(i), 0, 255).astype(np.uint8) for i in imgs]
hgts = [seamless(h) for h in hgts]
diff = Image.fromarray(np.concatenate(imgs, 0))
diff = diff.filter(ImageFilter.UnsharpMask(radius=1, percent=40))
diff.save(OUT / 'flatbedDeckWeathered_diffuse.png')

h = np.concatenate(hgts, 0)
gy, gx = np.gradient(h)
strength = 6.0
nx, ny, nz = -gx * strength, gy * strength, np.ones_like(h)
n = np.stack([nx, ny, nz], -1); n /= np.linalg.norm(n, axis=-1, keepdims=True)
Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8)).save(OUT / 'flatbedDeckWeathered_normal.png')
print('wrote', OUT / 'flatbedDeckWeathered_diffuse.png', diff.size)

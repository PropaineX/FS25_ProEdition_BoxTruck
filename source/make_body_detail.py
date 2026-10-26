"""Generate original, physically scaled curtain maps and stage the detail upgrade.

python source/make_body_detail.py <project> <staging directory>
Uses the installed GIANTS texture tool for BC7 RGB normals and full mip chains.
No source mod files are overwritten; install the reviewed staging result separately.
"""
from pathlib import Path
import sys, shutil, subprocess, xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

ROOT, OUT = map(Path, sys.argv[1:3])
OUT.mkdir(parents=True, exist_ok=True)
ART = OUT.parent / 'textures'
ART.mkdir(exist_ok=True)
TOOL = Path('C:/Program Files/GIANTS Software/GIANTS_Editor_10.0.14/tools/textureTool.exe')

def image(a):
    if a.ndim == 2:
        a = np.repeat(a[..., None], 3, axis=2)
    return Image.fromarray(np.uint8(np.clip(a, 0, 1) * 255 + .5))

def save(a, name, linear=False, normal=False):
    src = ART / (name + '.png')
    image(a).save(src)
    args = [str(TOOL), '-sourceFiles', str(src.resolve()), '-targetFile', str((OUT / (name + '.dds')).resolve()),
            '-format', 'bc7', '-arch', 'dds', '-quality', 'standard', '-numMipmaps', 'max',
            '-colorSpace', 'linear' if linear else 'srgb', '-disableCacheServer', '-silent', '-overwriteNonGenerated']
    if normal:
        args += ['-normalMapFormat', 'rgb', '-normalizeMipmaps', 'true']
    subprocess.run(args, check=True)
    print('TEXTURE', name, a.shape, flush=True)

def normals(h, dx, dy):
    gy, gx = np.gradient(h, dy, dx)
    n = np.stack((-gx, gy, np.ones_like(h)), -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return n * .5 + .5

# Actual closed curtain bounds: 6.72 x 2.53 m. Texture rows run top to bottom.
W, H = 4096, 2048
x = ((np.arange(W, dtype=np.float32) + .5) / W * 6.72)[None, :]
y = (2.53 - (np.arange(H, dtype=np.float32) + .5) / H * 2.53)[:, None]
rng = np.random.default_rng(1966)
h = np.zeros((H, W), np.float32)
# Relaxed fabric, strongest near the top suspension; millimetre relief.
for k in range(28):
    c = rng.uniform(0, 6.72)
    width = rng.uniform(.018, .060)
    drift = .014 * np.sin(y * rng.uniform(2, 7) + rng.uniform(0, 6.28))
    fade = np.exp(-(2.53 - y) / rng.uniform(.17, .48))
    h += rng.uniform(.0015, .0035) * np.exp(-((x - c + drift) / width) ** 2) * fade
for k in range(9):
    h += .00065 * np.sin(x * rng.uniform(6, 16) + y * rng.uniform(-1, 1) + k) * (.35 + .65 * y / 2.53)
# Tension creases grow diagonally from the real 0.33 m buckle spacing.
for bx in np.arange(.165, 6.72, .33):
    above = np.maximum(y - .295, 0)
    d = np.abs(x - bx) - .36 * above
    h -= .0018 * np.exp(-(d / .014) ** 2) * np.exp(-above / .23) * (y > .295)
# Heat-welded hems: low continuous raised edges, rather than painted black lines.
seams = np.zeros_like(h)
for sy in (.045, .075, .295, .325, 2.465, 2.49):
    ridge = np.exp(-((y - sy) / .0028) ** 2)
    h += .00025 * ridge
    seams += ridge
for sx in (.035, 6.685):
    ridge = np.exp(-((x - sx) / .003) ** 2)
    h += .0003 * ridge
    seams += ridge
diff = np.ones_like(h) * .965
diff -= .018 * seams
diff -= .025 * np.exp(-(2.53 - y) / .024)
diff += .006 * np.sin(x * 2.1 + y * 1.3)
save(diff, 'boxTruckCurtain_diffuse')
save(normals(h, 6.72 / W, 2.53 / H), 'boxTruckCurtain_normal', True, True)

# vehicleShader detail maps are projected in local metres: this tile covers 1 m.
# 512 threads/m, resolved at 4 samples per repeat. Seamless periodic weave.
N = 2048
u = np.arange(N, dtype=np.float32)[None, :] / N
v = np.arange(N, dtype=np.float32)[:, None] / N
warp, weft = np.cos(2*np.pi*512*u), np.cos(2*np.pi*512*v)
weave = (warp + weft) * .5
fine = .000018 * (warp + weft) + .000007 * warp * weft
save(.975 + .015 * weave, 'boxTruckFabric_detail_diffuse')
save(normals(fine, 1/N, 1/N), 'boxTruckFabric_detail_normal', True, True)
# vehicleShader detailSpecular RGB = smoothness, ambient occlusion, metalness.
spec = np.zeros((N, N, 3), np.float32)
spec[..., 0] = .31 + .025 * weave
spec[..., 1] = 1
save(spec, 'boxTruckFabric_detail_specular', True)

# Stage existing files; generated textures take precedence.
for f in ROOT.iterdir():
    if f.is_file() and f.suffix in ('.dds', '.i3d', '.shapes', '.xml') and not (OUT / f.name).exists():
        shutil.copy2(f, OUT / f.name)
tree = ET.parse(OUT / 'boxTruck.i3d')
r = tree.getroot()
files = r.find('Files')
paths = {f.get('filename'): f.get('fileId') for f in files}
def fid(path):
    if path not in paths:
        paths[path] = str(max(map(int, paths.values())) + 1)
        ET.SubElement(files, 'File', fileId=paths[path], filename=path)
    return paths[path]
def param(m, name, value):
    e = m.find(f"CustomParameter[@name='{name}']")
    if e is None: e = ET.SubElement(m, 'CustomParameter', name=name)
    e.set('value', value)
for m in r.find('Materials'):
    if m.get('name') == 'curtainCloth':
        for channel in ('Diffuse', 'Normal', 'Specular'):
            m.find(f"Custommap[@name='detail{channel}']").set('fileId', fid(f'boxTruckFabric_detail_{channel.lower()}.dds'))
        for name, value in [('smoothnessScale', '1'), ('metalnessScale', '0'), ('clearCoatIntensity', '0.025'), ('clearCoatSmoothness', '0.25')]:
            param(m, name, value)
ET.indent(tree, space='  ')
tree.write(OUT / 'boxTruck.i3d', encoding='iso-8859-1', xml_declaration=True)
print('STAGED', OUT, flush=True)

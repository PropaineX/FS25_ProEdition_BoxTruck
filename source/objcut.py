# Parse the GE OBJ export of profiLiner_vis, split into its 12 material blocks, keep the rear end.
# Usage (inside Blender): objcut.load(obj_path, zmax, ymin) -> list of (block, verts[m], uvs, faces) in GAME coords
import numpy as np
SLOTS = ['SHARED_BLACK2', 'chassis_color', 'metalPaintedBlack', 'silverScratched', 'rubberBlack',
         'plasticGraniteGrainSmallBlack', 'metalGalvanized', 'design_color', 'metalPainted', 'KRONE_BLUE5',
         'plasticGraniteGrainSmall', 'fabric2']
def parse(path, group='profiLiner_vis'):
    V, T, N, F = [], [], [], []
    cur = None
    for line in open(path):
        if line.startswith('g '): cur = line.split()[1]; continue
        c = line[:2]
        if c == 'v ': V.append(line.split()[1:4])
        elif c == 'vt': T.append(line.split()[1:3])
        elif c == 'vn': N.append(line.split()[1:4])
        elif c == 'f ' and cur == group:
            F.append([[int(x) - 1 for x in p.split('/')] for p in line.split()[1:4]])
    return (np.array(V, float) / 100.0, np.array(T, float), np.array(N, float), np.array(F, int))
def blocks(F, n=12):
    fv = F[:, :, 0]
    mx = np.maximum.accumulate(fv.max(1)); mn = np.minimum.accumulate(fv.min(1)[::-1])[::-1]
    b = [0] + [i + 1 for i in range(len(fv) - 1) if mx[i] < mn[i + 1]] + [len(fv)]
    blk = np.zeros(len(fv), int)
    for k in range(len(b) - 1): blk[b[k]:b[k + 1]] = k
    assert len(b) - 1 == n, len(b) - 1
    return blk

def components(V, fv):
    """connected pieces of the faces fv (vertices welded by position, 0.1 mm)"""
    key = np.round(V * 10000).astype(np.int64)
    _, weld = np.unique(key, axis=0, return_inverse=True)
    weld = weld.ravel()
    par = np.arange(weld.max() + 1)
    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for f in fv:
        a, b, c = (find(weld[i]) for i in f)
        par[b] = a; par[find(c)] = a
    return np.array([find(weld[f[0]]) for f in fv])

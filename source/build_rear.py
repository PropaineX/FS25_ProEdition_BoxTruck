# Builds the Box Truck rear frame from the game's Krone ProfiLiner body (GE OBJ export of profiLiner_vis):
# rear posts, header with door latches, sill with keepers; the lock levers go on the doors (they swing with them).
# Fitted to our box: z +DZ, y piecewise (sill +0.55, header +0.21, between = the doors' 0.875 squeeze).
# Run: blender -b -P build_rear.py -- <plvis.obj> <out.blend> <pl_curtainsTop.obj>
# The two OBJ files are GIANTS Editor exports (File > Export Selection..., Wavefront OBJ, one shape selected) of the
# game's data/vehicles/krone/profiLiner/profiLiner.i3d shapes profiLiner_vis and curtainsTop (game data: not kept here).
# Then export_rear.py; the doors are taken straight from the game's profiLiner.i3d in GIANTS Editor (merge script).
import bpy, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, objcut
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]
OBJ, OUT, TOP = a[0], a[1], a[2]

PL_HINGE_X, PL_HINGE_Z = 1.2614, -6.857286     # ProfiLiner door hinge line
REAR_Z = -5.35                                 # our rear (door hinge line), build_body.py
DZ = REAR_Z - PL_HINGE_Z
DOOR_Y0, DOOR_Y1 = 1.17, 3.89                  # ProfiLiner door bottom/top
NEW_Y0, NEW_Y1 = DOOR_Y0 + 0.55, DOOR_Y1 + 0.21  # ours: floor 1.75, roof 4.23
SY = (NEW_Y1 - NEW_Y0) / (DOOR_Y1 - DOOR_Y0)
LOCK_X = (0.109, 0.709)                        # ProfiLiner lock pivots (doorLeftLock01/02, mirrored on the right)

def map_y(y):
    return np.where(y < DOOR_Y0, y + 0.55, np.where(y > DOOR_Y1, y + 0.21, NEW_Y0 + (y - DOOR_Y0) * SY))
def map_n(n, y):
    n = n.copy(); mid = (y >= DOOR_Y0) & (y <= DOOR_Y1)
    n[mid, 1] /= SY
    return n / np.linalg.norm(n, axis=1, keepdims=True)

V, T, N, F = objcut.parse(OBJ); blk = objcut.blocks(F)
fv = F[:, :, 0]
P = V[fv]
keep = (P[:, :, 2].max(1) < -6.40) & (P[:, :, 1].min(1) > 0.93)
idx = np.where(keep)[0]

# lock levers: pieces on the door face (z < -6.83) at the lock pivots, not the slotted keeper plates
comp = objcut.components(V, fv[idx])
mover = np.zeros(len(idx), bool)
for c in np.unique(comp):
    sel = comp == c; f = idx[sel]; Q = V[np.unique(fv[f])]
    lo, hi = Q.min(0), Q.max(0); n = sel.sum(); cx = (lo[0] + hi[0]) / 2
    near = min(abs(abs(cx) - lx) for lx in LOCK_X)
    if hi[2] < -6.83 and lo[1] > 1.08 and hi[1] < 1.19 and near < 0.20 and n in (144, 30, 12, 40):
        mover[sel] = True
print('movers', mover.sum(), 'static', (~mover).sum())

bpy.ops.wm.read_factory_settings(use_empty=True)
mats = []
for s in objcut.SLOTS:
    m = bpy.data.materials.new('profiLiner_%s_mat' % s); mats.append(m)
    m.diffuse_color = (0.05 + 0.07 * len(mats), 0.5, 0.5, 1)   # the exporter merges materials with equal colours
    m.use_nodes = True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = m.diffuse_color
g2b = lambda x, y, z: (x, -z, y)

def make(name, faces, origin, V=V, T=T, N=N, F=F, blk=blk, mats=mats, names=objcut.SLOTS):
    corners = F[faces]                                  # (n,3,3) v/vt/vn
    vi = corners[:, :, 0].ravel()
    pos = V[vi].copy(); pos[:, 1] = map_y(pos[:, 1]); pos[:, 2] += DZ
    nrm = map_n(N[corners[:, :, 2].ravel()], V[vi][:, 1])
    # weld by original vertex index so shading stays as in the game mesh
    uniq, inv = np.unique(vi, return_inverse=True)
    first = np.zeros(len(uniq), int); first[inv[::-1]] = np.arange(len(vi))[::-1]
    verts = [g2b(*(pos[i] - origin)) for i in first]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], inv.reshape(-1, 3).tolist())
    used = sorted(set(blk[faces]))
    for k in used: me.materials.append(mats[k])
    slot = {k: i for i, k in enumerate(used)}
    for p, b in zip(me.polygons, blk[faces]): p.material_index = slot[b]
    uv = me.uv_layers.new(name='uv0')
    tex = T[corners[:, :, 1].ravel()]
    uv.data.foreach_set('uv', tex.ravel())
    me.normals_split_custom_set([g2b(*n) for n in nrm])
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    ob.location = g2b(*origin)
    ob['i3D_collision'] = False
    print(name, len(faces), 'faces, materials', [names[k] for k in used])
    return ob

make('rearFrame', idx[~mover], np.zeros(3))
mv = idx[mover]
cx = V[fv[mv]][:, :, 0].mean(1)
make('rearLocksLeft', mv[cx > 0], np.array([PL_HINGE_X, 0, REAR_Z]))
make('rearLocksRight', mv[cx < 0], np.array([-PL_HINGE_X, 0, REAR_Z]))
# top rail end (curtainsTop, the black band behind the latches); slots = its materialIds 39,38,37
TOP_MATS = ['profiLinerCurtains_plasticGraniteGrainSmallBlack_mat', 'profiLinerCurtains_cover_color_mat',
            'profiLinerCurtains_rubber_mat']
tm = []
for k, nme in enumerate(TOP_MATS):
    m = bpy.data.materials.new(nme); m.use_nodes = True
    m.diffuse_color = (0.9, 0.1 + 0.2 * k, 0.3, 1)
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = m.diffuse_color
    tm.append(m)
V2, T2, N2, F2 = objcut.parse(TOP, 'curtainsTop'); b2 = objcut.blocks(F2, 3)
k2 = np.where(V2[F2[:, :, 0]][:, :, 2].max(1) < -6.40)[0]
make('rearFrameTop', k2, np.zeros(3), V2, T2, N2, F2, b2, tm, TOP_MATS)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print('SAVED', OUT, 'SY', SY, 'DZ', DZ)

# Builds the Box Truck front wall from the game's Krone ProfiLiner body (GE OBJ export of profiLiner_vis, see
# build_rear.py): the corrugated front sheet, the grey band along the top, the fronts of the corner posts and the sill.
# Left out: the semitrailer's air/electric couplings and the electric box, and everything deeper than the sheet (the
# inside of its corner posts). Fitted to our box: the sheet's ribs where our front wall was (FRONT_Z); the sill +0.55,
# everything above it squeezed evenly up to TOP_Y (the front has no doors to keep in line), which leaves room for the
# white roof cap (from the band's top, 4.13, to ROOF_Y; own part in build_body.py); a few vertices low down are pushed back off the cab.
# The two round Krone logos at the ends of the band come from its body decals (visuals/alphaBlending_decals, OBJ +
# uv1/uv2 dumped with getShapeVertexTexCoords: same vertex order as the OBJ, needed by vmaskUV2_normalUV3).
# Run: blender -b -P build_front.py -- <plvis.obj> <out.blend> [<decals.obj> <decal uv .npz>]; then export_rear.py
import bpy, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, objcut
a = sys.argv[sys.argv.index('--') + 1:]
OBJ, OUT = a[0], a[1]
DECALS, DECAL_UV = (a[2], a[3]) if len(a) > 3 else (None, None)

FRONT_Z = 1.63                                  # build_body.py: outside face of the front wall
PL_RIB_Z = 6.88                                 # ProfiLiner: outside of the front sheet's ribs
DZ = FRONT_Z - PL_RIB_Z
ZMIN = 6.74                                     # ProfiLiner: inside face of the front sheet; deeper parts left out
PL_Y0, PL_TOP = 1.17, 4.018                     # ProfiLiner: sill top, top of the front band / rail end
NEW_Y0, TOP_Y = PL_Y0 + 0.55, 4.16              # ours: floor, top of the band (= bottom of the roof cap)
SY = (TOP_Y - NEW_Y0) / (PL_TOP - PL_Y0)
CAB = [(1.70, 1.68), (2.20, 1.72), (3.00, 1.81), (4.20, 2.04)]   # FH16 cab rear edge (y, z), knowledge index
CLEAR = 0.01

# the grey band (from PL_BAND_Y up) keeps the even squeeze but sits higher: its front face (top PL_BAND_TOP) ends right
# under the roof cap (CAP_Y), as on the ProfiLiner (user 2026-10-22); the sheet below is stretched to meet it
PL_BAND_Y, PL_BAND_TOP = 3.72, 3.870
CAP_Y, ROOF_TOP = 4.13, 4.225
BAND_Y = CAP_Y - (PL_BAND_TOP - PL_BAND_Y) * SY
SY_MID = (BAND_Y - NEW_Y0) / (PL_BAND_Y - PL_Y0)
def map_y(y):
    return np.where(y < PL_Y0, y + 0.55,
                    np.where(y < PL_BAND_Y, NEW_Y0 + (y - PL_Y0) * SY_MID,
                             np.minimum(BAND_Y + (y - PL_BAND_Y) * SY, ROOF_TOP)))
def map_n(n, y):
    n = n.copy()
    n[(y >= PL_Y0) & (y < PL_BAND_Y), 1] /= SY_MID
    n[y >= PL_BAND_Y, 1] /= SY
    return n / np.linalg.norm(n, axis=1, keepdims=True)
def cab_z(y):
    ys, zs = zip(*CAB)
    return np.interp(y, ys, zs)

bpy.ops.wm.read_factory_settings(use_empty=True)
g2b = lambda x, y, z: (x, -z, y)

def materials(names):
    out = []
    for k, nme in enumerate(names):
        m = bpy.data.materials.new(nme); m.use_nodes = True
        m.diffuse_color = (0.05 + 0.07 * k, 0.4, 0.7, 1)       # the exporter merges materials with equal colours
        m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = m.diffuse_color
        out.append(m)
    return out

def make(name, V, T, N, F, blk, faces, mats, names, extra_uv=()):
    corners = F[faces]
    vi = corners[:, :, 0].ravel()
    pos = V[vi].copy(); pos[:, 1] = map_y(pos[:, 1]); pos[:, 2] += DZ
    pushed = pos[:, 2] > cab_z(pos[:, 1]) - CLEAR
    pos[:, 2] = np.minimum(pos[:, 2], cab_z(pos[:, 1]) - CLEAR)
    nrm = map_n(N[corners[:, :, 2].ravel()], V[vi][:, 1])
    uniq, inv = np.unique(vi, return_inverse=True)
    first = np.zeros(len(uniq), int); first[inv[::-1]] = np.arange(len(vi))[::-1]
    me = bpy.data.meshes.new(name)
    me.from_pydata([g2b(*pos[i]) for i in first], [], inv.reshape(-1, 3).tolist())
    used = sorted(set(blk[faces]))
    for k in used: me.materials.append(mats[k])
    slot = {k: i for i, k in enumerate(used)}
    for p, b in zip(me.polygons, blk[faces]): p.material_index = slot[b]
    uv = me.uv_layers.new(name='uv0')
    uv.data.foreach_set('uv', T[corners[:, :, 1].ravel()].ravel())
    for k, arr in enumerate(extra_uv, 1):             # per vertex (same order as the OBJ's v)
        me.uv_layers.new(name='uv%d' % k).data.foreach_set('uv', arr[vi].ravel())
    me.normals_split_custom_set([g2b(*n) for n in nrm])
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    ob['i3D_collision'] = False
    print(name, len(faces), 'faces, materials', [names[k] for k in used], 'vertices pushed off the cab', int(pushed[first].sum()))
    return ob

# front sheet, band, post fronts, sill
V, T, N, F = objcut.parse(OBJ); blk = objcut.blocks(F)
P = V[F[:, :, 0]]; c = P.mean(1)
coupling = ((np.isin(blk, (2, 3, 4, 5, 6)) & (np.abs(c[:, 0]) < 1.0)) |
            ((P[:, :, 2].max(1) > PL_RIB_Z + 0.005) & (np.abs(c[:, 0]) < 0.8))) & (c[:, 1] < 2.4)
keep = (P[:, :, 2].min(1) > ZMIN) & (P[:, :, 1].min(1) > 1.0) & ~coupling
# the coupling bracket's mounting columns and small bits that lie flat on the sheet: narrow pieces low in the middle
low = np.where(keep & (np.abs(c[:, 0]) < 0.8) & (c[:, 1] < 2.4))[0]
pieces = objcut.components(V, F[low][:, :, 0])
for k in np.unique(pieces):
    f = low[pieces == k]; Q = V[np.unique(F[f][:, :, 0])]
    if Q[:, 0].max() - Q[:, 0].min() < 0.08 and len(f) < 60:
        keep[f] = False
frame = make('frontFrame', V, T, N, F, blk, np.where(keep)[0], materials(['profiLiner_%s_mat' % s for s in objcut.SLOTS]),
             objcut.SLOTS)

# the sheet's texture has the semitrailer couplings' shadows baked into its lower half (user 2026-10-22: "copy the top
# half over the bottom half"): cut the sheet at half height and give the lower half the UVs of the upper half
import bmesh
from mathutils import Vector
SHEET_SLOT = 'profiLiner_design_color_mat'
me = frame.data
slot = [m.name for m in me.materials].index(SHEET_SLOT)
sheet = [p for p in me.polygons if p.material_index == slot and p.normal.y < -0.7 and abs(p.center.x) < 1.15]
y_lo = min(me.vertices[v].co.z for p in sheet for v in p.vertices)
y_hi = max(me.vertices[v].co.z for p in sheet for v in p.vertices if me.vertices[v].co.z < BAND_Y + 0.01)
y_mid = (y_lo + y_hi) / 2
bm = bmesh.new(); bm.from_mesh(me)
faces = [f for f in bm.faces if f.material_index == slot and f.normal.y < -0.7 and abs(f.calc_center_median().x) < 1.15]
geom = list({e for f in faces for e in f.edges} | set(faces) | {v for f in faces for v in f.verts})
bmesh.ops.bisect_plane(bm, geom=geom, plane_co=Vector((0, 0, y_mid)), plane_no=Vector((0, 0, 1)))
uvl = bm.loops.layers.uv['uv0']
moved = 0
for f in bm.faces:
    if f.material_index != slot or f.normal.y > -0.7 or abs(f.calc_center_median().x) > 1.15:
        continue
    zs = [l.vert.co.z for l in f.loops]
    if max(zs) > y_mid + 1e-4 or min(zs) < y_lo - 1e-4:
        continue
    # uv as an affine function of (x, height) on this face, then read it one half-height higher
    A = np.array([[l.vert.co.x, l.vert.co.z, 1.0] for l in f.loops]); U = np.array([tuple(l[uvl].uv) for l in f.loops])
    coef, *_ = np.linalg.lstsq(A, U, rcond=None)
    if abs(coef[1]).max() < 1e-6:
        continue
    for l in f.loops:
        l[uvl].uv = tuple(np.array(tuple(l[uvl].uv)) + coef[1] * (y_mid - y_lo))
    moved += 1
bm.to_mesh(me); bm.free()
print('sheet: lower half %.3f..%.3f takes the texture of %.3f..%.3f, faces changed %d' % (y_lo, y_mid, y_mid, y_hi, moved))

# (the curtainsTop front end is not used: our white roof cap in build_body.py covers that place)

# the Krone logos at the ends of the band (user 2026-10-22: keep them)
if DECALS:
    uvs = np.load(DECAL_UV)
    V3, T3, N3, F3 = objcut.parse(DECALS, 'alphaBlending_decals')
    c3 = V3[F3[:, :, 0]].mean(1)
    k3 = np.where((np.abs(c3[:, 0]) > 1.1) & (c3[:, 1] > 3.7) & (c3[:, 2] > 6.7))[0]
    LOGO_MAT = ['profiLinerDecals_metalPainted_alphaBlending_mat']
    make('frontLogos', V3, T3, N3, F3, np.zeros(len(F3), int), k3, materials(LOGO_MAT), LOGO_MAT,
         extra_uv=(uvs['ch1'], uvs['ch2']))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print('SAVED', OUT, 'SY', SY, 'DZ', DZ)

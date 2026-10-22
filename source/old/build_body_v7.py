# Builds the curtain-sider body for the Box Truck Pro Edition in Blender (game-ready node structure) and renders
# preview pictures.
# Run: blender.exe -b -P build_body.py -- <out_dir> <preview_prefix> [norender]
# All sizes are written in GAME coordinates (x = left, y = up, z = forward, truck origin = FH16 origin)
# and converted to Blender (x, -z, y) when the objects are made. Measurements: ..\reference_fh16BoxTruck.md
#
# Node structure (exported by export_body.py, linked under fh16_main_component1 in GIANTS Editor):
#   boxBody
#     visuals                       fixed body parts (no collision)
#     middlePostLeft/Right          slide to the front with the curtain
#     curtainLeft/Right             origin at the curtain's front edge; scale z -> bunches at the front
#     rearDoorLeft/Right            origin on the outer hinge line; rotate about y to open (270 deg)
#     collisions                    invisible compound children (floor, front wall, roof)
#       colSideLeftPivot/Right      origin on the top rail; lifted 2.5 m (above the roof) while the curtain is open
#     tensionBelts                  beltStartNN (local z across the box) -> beltStartNNEnd
#     beltActivationTrigger
import bpy, bmesh, sys, os, math
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
OUT_DIR = args[0]
PREFIX = args[1] if len(args) > 1 else 'body_v1'
RENDER = not (len(args) > 2 and args[2] == 'norender')

# ---- main sizes (game coordinates, metres) ----
# LIFT raises the floor and everything under it (v3: 0; the tyres reach y 1.40, so the lowest body part, the side
# rail at 1.22 + LIFT, needs LIFT >= 0.25). ROOF_Y is the top of the body (4.23 = level with the FH16 Globetrotter XL
# roof). Both can be given on the command line: build_body.py <out> <prefix> [render|norender] [lift] [roofY]
LIFT = float(args[3]) if len(args) > 3 else 0.25
HALF_W = 1.275        # outside half width (2.55 m)
CHASSIS_TOP_Y = 1.18  # top of the FH16 chassis rails: the subframe stands on it whatever the lift
FLOOR_Y = 1.50 + LIFT # top of the load floor
BOTTOM_Y = 1.22 + LIFT  # lowest edge of the body sides (bottom side rail, posts, rear sill)
ROOF_Y = float(args[4]) if len(args) > 4 else 4.23   # level with the cab roof (user, 2026-10-22: no step above the cab)
SHIFT_Z = -0.37       # whole box moved back (v1-v3: 0). Cab rear edge measured (long-lens side shot, 2026-10-22):
                      # z 2.04 at y 4.2 (roof spoiler, rocks +-0.17 m), 1.81 at y 3.0, 1.72 at y 2.2, 1.68 at y 1.7.
                      # Front posts end at FRONT_Z + 0.02 = 1.65: ~3 cm clear at the lower corner. Same box length.
FRONT_Z = 2.00 + SHIFT_Z  # outside face of the front wall
REAR_Z = -4.98 + SHIFT_Z  # outside face of the rear doors
CURTAIN_FRONT_Z = FRONT_Z - 0.12
DOOR_HINGE_X = 1.29   # barn door hinge line (outside the rear post, so open doors lie along the sides)
BELT_COUNT = 9
# v7 (ProfiLiner-style, user 2026-10-22): the curtain gathers at the REAR when it opens; two sliding posts per side
CURTAIN_REAR_Z = REAR_Z + 0.14                 # rear end of the curtain (inside the rear posts)
CLOTH_Y0, CLOTH_Y1 = BOTTOM_Y + 0.06, ROOF_Y - 0.17   # the cloth reaches down over the bottom rail
CLOTH_X = 1.288                                # inner face of the cloth: outside the rails, the skirt hangs over the bottom rail
BAND_Y = FLOOR_Y + 0.03                        # dark reinforcement band; buckle straps hang below it
BUCKLE_PITCH = 0.33                            # make_curtain_maps.py uses the same pitch for the pull lines
GATHER_LEN = 0.50                              # length of the gathered (open) curtain at the rear
POST_Z = (CURTAIN_FRONT_Z - (CURTAIN_FRONT_Z - CURTAIN_REAR_Z) / 3, CURTAIN_FRONT_Z - 2 * (CURTAIN_FRONT_Z - CURTAIN_REAR_Z) / 3)
BOARD_Y = (0.30, 0.70, 1.10, 1.50)             # side boards, bottom edge above the floor
WHEEL_R = 0.535

# collision flags as used by the game's own vehicles (krone profiLiner, riedler timberFrameFH16)
COL_GROUP, COL_MASK = '0x10004', '0xfe3ffb83'
TRIGGER_GROUP, TRIGGER_MASK = '0x20000000', '0x100000'

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

def g2b(x, y, z):
    return Vector((x, -z, y))

MATS = {}
def mat(name, rgb):
    if name not in MATS:
        m = bpy.data.materials.new(name)
        m.diffuse_color = (*rgb, 1.0)
        MATS[name] = m
    return MATS[name]

def collection(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c

COLL = None  # collection new objects go into

def put(ob, parent):
    COLL.objects.link(ob) if ob.name not in COLL.objects else None
    if parent is not None:
        bpy.context.view_layer.update()
        mw = ob.matrix_world.copy()
        ob.parent = parent
        ob.matrix_world = mw
    return ob

def group(name, parent, x=0.0, y=0.0, z=0.0, rot_y_deg=0.0):
    """Transform group (Blender empty) at a game-space position, optional rotation about the game y axis."""
    ob = bpy.data.objects.new(name, None)
    ob.location = g2b(x, y, z)
    ob.rotation_euler = (0, 0, math.radians(rot_y_deg))  # game y axis = Blender z axis
    return put(ob, parent)

def box(name, parent, x0, x1, y0, y1, z0, z1, material):
    """Axis-aligned box from game-space min/max; object origin at the box centre."""
    sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * sx, v.co.y * sz, v.co.z * sy))  # blender x,y,z = game x,z,y sizes
    bm.to_mesh(me); bm.free()
    if material is not None:
        me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    ob.location = g2b((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    ob['i3D_collision'] = False
    return put(ob, parent)

def decal(name, parent, x, y0, y1, z_start, z_end, material):
    """Flat quad facing outwards (+x for x > 0) at x, the whole texture on it: u runs from z_start to z_end (the
    reading direction seen from outside), v = 1 at the top (the game's v runs bottom-up). uv1 = vmask (vmaskUV2)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv0 = bm.loops.layers.uv.new('uv0'); uv1 = bm.loops.layers.uv.new('uv1')
    corners = [(z_start, y1, (0, 1)), (z_start, y0, (0, 0)), (z_end, y0, (1, 0)), (z_end, y1, (1, 1))]
    verts = [bm.verts.new(g2b(x, y, z)) for z, y, _ in corners]
    face = bm.faces.new(verts)
    for loop, (_, _, uv) in zip(face.loops, corners):
        loop[uv0].uv = uv; loop[uv1].uv = uv
    face.normal_update()
    if (face.normal.x > 0) != (x > 0):
        face.normal_flip()
    bm.to_mesh(me); bm.free()
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    ob['i3D_collision'] = False
    ob['i3D_castsShadows'] = False
    return put(ob, parent)

def decal_inside(name, parent, x0, x1, y0, y1, z, material):
    """Flat quad at z facing game +z with the whole texture on it (u along x0 -> x1, v = 1 at the top). uv1 = vmask."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv0 = bm.loops.layers.uv.new('uv0'); uv1 = bm.loops.layers.uv.new('uv1')
    corners = [(x0, y1, (0, 1)), (x0, y0, (0, 0)), (x1, y0, (1, 0)), (x1, y1, (1, 1))]
    verts = [bm.verts.new(g2b(x, y, z)) for x, y, _ in corners]
    face = bm.faces.new(verts)
    for loop, (_, _, uv) in zip(face.loops, corners):
        loop[uv0].uv = uv; loop[uv1].uv = uv
    face.normal_update()
    if face.normal.y > 0:      # game +z = Blender -y
        face.normal_flip()
    bm.to_mesh(me); bm.free()
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    ob['i3D_collision'] = False
    ob['i3D_castsShadows'] = False
    return put(ob, parent)

def design_pieces(name, parent, sgn, pieces, tex_w, tex_h, x, material):
    """Curtain design made of pieces of a game ad sheet: each piece = (s0, s1, y0, y1, (px0, py0, px1, py1)) with s =
    metres from where reading starts (the front on the left side, the rear on the right side, so it reads left to
    right from outside on both sides) and a pixel rectangle of the sheet. One mesh, quads facing outwards at x."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv0 = bm.loops.layers.uv.new('uv0'); uv1 = bm.loops.layers.uv.new('uv1')
    origin = g2b(sgn * x, (CLOTH_Y0 + CLOTH_Y1) / 2, (CURTAIN_FRONT_Z + CURTAIN_REAR_Z) / 2)
    for k, (s0, s1, y0, y1, (px0, py0, px1, py1)) in enumerate(pieces):
        xk = x + 0.0006 * k      # later pieces lie on top of earlier ones
        za, zb = (CURTAIN_FRONT_Z - s0, CURTAIN_FRONT_Z - s1) if sgn > 0 else (CURTAIN_REAR_Z + s0, CURTAIN_REAR_Z + s1)
        u0, u1, vt, vb = px0 / tex_w, px1 / tex_w, 1 - py0 / tex_h, 1 - py1 / tex_h
        corners = [(za, y1, (u0, vt)), (za, y0, (u0, vb)), (zb, y0, (u1, vb)), (zb, y1, (u1, vt))]
        verts = [bm.verts.new(g2b(sgn * xk, y, z) - origin) for z, y, _ in corners]
        f = bm.faces.new(verts)
        for loop, (_, _, uv) in zip(f.loops, corners):
            loop[uv0].uv = uv; loop[uv1].uv = uv
        f.normal_update()
        if (f.normal.x > 0) != (sgn > 0):
            f.normal_flip()
    bm.to_mesh(me); bm.free()
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    ob.location = origin
    ob['i3D_collision'] = False
    ob['i3D_castsShadows'] = False
    return put(ob, parent)

# curtain designs from the Krone ProfiLiner's ad sheets (the game's own files, referenced by export_body.py):
# (s0, s1, y0, y1, pixel rect); our own layout for the 6.72 m curtain, pieces that are white on the sheet are left out
DESIGNS = {
    'Krone': (1, 2048, 512, [
        (1.06, 5.66, 3.695, 3.880, (0, 3, 1814, 73)),        # QUALITY | COMPETENCE | SERVICE
        (1.06, 5.66, 2.750, 3.615, (0, 91, 1426, 358)),      # Krone logo + KRONE
        (3.06, 5.66, 2.420, 2.665, (651, 398, 1481, 477)),   # We Deliver the Future
        (1.06, 2.36, 2.550, 2.674, (0, 374, 358, 407)),      # www.krone-trailer.com
    ]),
    'FSL': (2, 2048, 1024, [
        (0.50, 2.78, 1.950, 3.850, (1295, 0, 2044, 622)),    # Farming Simulator League shield
        (3.30, 6.20, 2.880, 3.850, (1299, 639, 1921, 842)),  # GIANTS SOFTWARE
        (3.30, 4.05, 1.950, 2.700, (0, 775, 205, 977)),      # DLG
        (4.20, 6.20, 2.000, 2.568, (212, 783, 849, 966)),    # KRONE The Power of Green
    ]),
    'GIANTS': (3, 4096, 4096, [
        (0.00, 6.72, 1.830, 4.030, (0, 486, 4096, 2032)),    # red triangle artwork (background, rear half red)
        (0.35, 2.470, 3.240, 3.950, (15, 2063, 2230, 2840)),  # Farming (stops before the white GIANTS beside it)
        (0.35, 2.786, 2.560, 3.240, (15, 2840, 2560, 3584)),  # Simulator
        (0.45, 2.10, 1.900, 2.443, (2589, 3526, 3833, 3934)),# GIANTS SOFTWARE
    ]),
}

def mirrored(name, parent, x0, x1, *rest):
    """Left box (positive x) plus its mirror on the right."""
    return [box(name + 'Left', parent, x0, x1, *rest), box(name + 'Right', parent, -x1, -x0, *rest)]

def rod(name, parent, x, z, y0, y1, r, material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=r, depth=y1 - y0, location=g2b(x, (y0 + y1) / 2, z))
    ob = bpy.context.object; ob.name = name
    ob.data.materials.append(material)
    for c in ob.users_collection: c.objects.unlink(ob)
    ob['i3D_collision'] = False
    return put(ob, parent)

def wheel(name, parent, x, y, z, radius, width, material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=width, location=g2b(x, y, z),
                                        rotation=(0, math.pi / 2, 0))
    ob = bpy.context.object; ob.name = name
    ob.data.materials.append(material)
    for c in ob.users_collection: c.objects.unlink(ob)
    return put(ob, parent)

def col(name, parent, *bounds):
    """Invisible collision box (compound child of the truck's main component)."""
    ob = box(name, parent, *bounds, colmat)
    ob['i3D_collision'] = True
    ob['i3D_compoundChild'] = True
    ob['i3D_density'] = 0.001
    ob['i3D_collisionFilterGroup'] = COL_GROUP
    ob['i3D_collisionFilterMask'] = COL_MASK
    ob['i3D_nonRenderable'] = True
    ob['i3D_castsShadows'] = False
    ob['i3D_receiveShadows'] = False
    ob.hide_render = True
    return ob

def merged_boxes(name, parent, boxes, material, origin=None):
    """Many axis-aligned boxes (game-space min/max tuples) in ONE mesh, origin at `origin` (game xyz) or the first
    box's centre. Keeps the node count low for small repeated parts (rivets, ribs, buckles)."""
    if origin is None:
        b = boxes[0]; origin = ((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2)
    o = g2b(*origin)
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for x0, x1, y0, y1, z0, z1 in boxes:
        res = bmesh.ops.create_cube(bm, size=1.0)
        c = g2b((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) - o
        for v in res['verts']:
            v.co = Vector((v.co.x * (x1 - x0), v.co.y * (z1 - z0), v.co.z * (y1 - y0))) + c
    bm.to_mesh(me); bm.free()
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    ob.location = o
    ob['i3D_collision'] = False
    return put(ob, parent)

def cloth_panel(name, parent, sgn, x_out, x_in, y0, y1, z_front, z_rear, material):
    """The closed curtain: a thin slab whose outer AND inner faces carry the whole curtain texture (u = 0 at the front
    edge, v = 1 at the top), so the folds line up with build_curtain_maps.py."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new('uv0')
    o = g2b(sgn * (x_out + x_in) / 2, (y0 + y1) / 2, (z_front + z_rear) / 2)
    def vert(x, y, z):
        return bm.verts.new(g2b(sgn * x, y, z) - o)
    corners = {}
    for xi, x in (('o', x_out), ('i', x_in)):
        for yi, y in (('b', y0), ('t', y1)):
            for zi, z in (('f', z_front), ('r', z_rear)):
                corners[xi + yi + zi] = (vert(x, y, z), (0.0 if zi == 'f' else 1.0, 0.0 if yi == 'b' else 1.0))
    def face(keys):
        f = bm.faces.new([corners[k][0] for k in keys])
        for loop, k in zip(f.loops, keys):
            loop[uv].uv = corners[k][1]
        return f
    faces = [face(k) for k in (('obf', 'obr', 'otr', 'otf'), ('ibf', 'itf', 'itr', 'ibr'), ('obf', 'otf', 'itf', 'ibf'),
                               ('obr', 'ibr', 'itr', 'otr'), ('otf', 'otr', 'itr', 'itf'), ('obf', 'ibf', 'ibr', 'obr'))]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    ob.location = o
    ob['i3D_collision'] = False
    return put(ob, parent)

def rounded_panels(name, parent, sgn_face, rects, x_face, depth, radius, material, segs=4):
    """Raised rounded-rectangle pressings on a vertical face that faces game +z (sgn_face = 1) or -z (-1).
    rects = (x0, x1, y0, y1) in game space; x_face = the z of the face. One mesh."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    b0 = rects[0]
    origin = g2b((b0[0] + b0[1]) / 2, (b0[2] + b0[3]) / 2, x_face)
    for x0, x1, y0, y1 in rects:
        pts = []
        for cx, cy, a0 in ((x1 - radius, y1 - radius, 0), (x0 + radius, y1 - radius, 90), (x0 + radius, y0 + radius, 180),
                           (x1 - radius, y0 + radius, 270)):
            for s in range(segs + 1):
                a = math.radians(a0 + 90 * s / segs)
                pts.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
        base = [bm.verts.new(g2b(x, y, x_face) - origin) for x, y in pts]
        inset = 0.012
        top = [bm.verts.new(g2b(cx_ + (inset if cx_ < (x0 + x1) / 2 else -inset), cy_ + (inset if cy_ < (y0 + y1) / 2 else -inset),
                                x_face + sgn_face * depth) - origin) for cx_, cy_ in pts]
        n = len(pts)
        for i in range(n):
            bm.faces.new([base[i], base[(i + 1) % n], top[(i + 1) % n], top[i]])
        bm.faces.new(top)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    ob.location = origin
    ob['i3D_collision'] = False
    return put(ob, parent)

def pleats(name, parent, sgn, x_in, depth_out, y0, y1, z_front, z_rear, folds, material, seed):
    """The open curtain gathered at the rear: a zig-zag sheet (folds x 2 faces) that bulges out a little more at the
    bottom, with a slight random lean per fold."""
    import random
    rnd = random.Random(seed)
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new('uv0')
    rows = 6
    origin = g2b(sgn * x_in, (y0 + y1) / 2, (z_front + z_rear) / 2)
    grid = []
    n = folds * 2
    leans = [rnd.uniform(-0.015, 0.015) for _ in range(n + 1)]
    for r in range(rows + 1):
        t = r / rows
        y = y0 + (y1 - y0) * t
        row = []
        for i in range(n + 1):
            z = z_front + (z_rear - z_front) * i / n + leans[i] * (1 - t)
            out = (depth_out * (1.25 - 0.45 * t)) if i % 2 else 0.0
            row.append(bm.verts.new(g2b(sgn * (x_in + out), y, z) - origin))
        grid.append(row)
    for r in range(rows):
        for i in range(n):
            f = bm.faces.new([grid[r][i], grid[r][i + 1], grid[r + 1][i + 1], grid[r + 1][i]])
            for loop, (rr, ii) in zip(f.loops, ((r, i), (r, i + 1), (r + 1, i + 1), (r + 1, i))):
                loop[uv].uv = (0.02 + 0.06 * ii / n, rr / rows)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.normal_update()
    if sum(f.normal.x for f in bm.faces) * sgn < 0:
        for f in bm.faces:
            f.normal_flip()
    # two-sided: copy the sheet with flipped normals so the inside shows too
    back = bmesh.ops.duplicate(bm, geom=list(bm.faces))['geom']
    for f in [g for g in back if isinstance(g, bmesh.types.BMFace)]:
        f.normal_flip()
    bm.to_mesh(me); bm.free()
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    ob.location = origin
    ob['i3D_collision'] = False
    return put(ob, parent)

# ---- materials (Blender colours = preview only; export_body.py gives the game materials) ----
alu = mat('alu', (0.62, 0.64, 0.66))                 # rails, frames (painted metal, not shiny)
postMat = mat('post', (0.55, 0.57, 0.59))            # sliding posts (matte, behind the curtain)
curtain = mat('curtain', (0.90, 0.90, 0.88))         # plain painted surfaces in the curtain white (roof)
curtainTex = mat('curtainCloth', (0.91, 0.90, 0.88)) # the curtain cloth with our fold textures
strap = mat('strap', (0.12, 0.12, 0.13))
wood = mat('floorWood', (0.20, 0.13, 0.10))          # dark load floor
antiSlip = mat('antiSlip', (0.24, 0.23, 0.21))
boardWood = mat('boardWood', (0.55, 0.40, 0.26))     # side boards
door = mat('door', (0.86, 0.86, 0.84))
kick = mat('kickPlate', (0.30, 0.04, 0.04))
proDecal = mat('proEditionDecal', (0.81, 0.06, 0.09))
# the GIANTS exporter merges materials with equal colours: every material needs its own preview colour
designMats = {n: mat('design%s' % n, (0.2, 0.3 + 0.05 * k, 0.6)) for k, n in enumerate(DESIGNS)}  # ProfiLiner sheets
steel = mat('steelDark', (0.16, 0.16, 0.17))
galv = mat('galvanized', (0.55, 0.56, 0.57))         # hinges, lock rods
stickerMat = mat('stickers', (0.95, 0.55, 0.05))
colmat = mat('collision', (0.9, 0.2, 0.2))
standin = mat('standIn', (0.35, 0.45, 0.62))
tyre = mat('tyre', (0.05, 0.05, 0.05))

COLL = collection('body')
root = group('boxBody', None)
visuals = group('visuals', root)

# ---- floor and subframe ----
mirrored('subframeRail', visuals, 0.38, 0.48, CHASSIS_TOP_Y, FLOOR_Y - 0.14, REAR_Z + 0.14, FRONT_Z - 0.05, steel)
cm = []
z = FRONT_Z - 0.10
while z > REAR_Z + 0.14:
    cm.append((-HALF_W, HALF_W, FLOOR_Y - 0.20, FLOOR_Y - 0.12, z - 0.03, z + 0.03)); z -= 0.60
merged_boxes('crossMembers', visuals, cm, steel)
box('floor', visuals, -HALF_W, HALF_W, FLOOR_Y - 0.12, FLOOR_Y, REAR_Z + 0.14, FRONT_Z - 0.08, wood)
# anti-slip strips and the centre line marks, 2 mm proud (visual only; the floor collision stays flat)
strips = [(sx * 0.70 - 0.13, sx * 0.70 + 0.13, FLOOR_Y, FLOOR_Y + 0.002, REAR_Z + 0.20, FRONT_Z - 0.15) for sx in (-1, 1)]
z = FRONT_Z - 0.40
while z > REAR_Z + 0.5:
    strips.append((-0.03, 0.03, FLOOR_Y, FLOOR_Y + 0.002, z - 0.35, z)); z -= 1.0
merged_boxes('floorStrips', visuals, strips, antiSlip)
# bottom side rail: outer profile with a rub strip and stake pockets
mirrored('sideRailBottom', visuals, 1.235, 1.285, BOTTOM_Y, FLOOR_Y + 0.02, REAR_Z + 0.14, FRONT_Z - 0.08, alu)
for side, sgn in (('Left', 1), ('Right', -1)):
    pockets = []
    z = FRONT_Z - 0.30
    while z > REAR_Z + 0.25:
        pockets.append((*sorted((sgn * 1.285, sgn * 1.295)), BOTTOM_Y + 0.02, BOTTOM_Y + 0.07, z - 0.025, z + 0.025)); z -= 0.40
    pockets.append((*sorted((sgn * 1.285, sgn * 1.292)), BOTTOM_Y + 0.11, BOTTOM_Y + 0.135, REAR_Z + 0.16, FRONT_Z - 0.10))
    merged_boxes('sideRail%sDetails' % side, visuals, pockets, steel)

# ---- front wall: plain outside, ribbed inside with a kick plate ----
box('frontWall', visuals, -HALF_W + 0.01, HALF_W - 0.01, FLOOR_Y, ROOF_Y - 0.06, FRONT_Z - 0.08, FRONT_Z, door)
mirrored('frontPost', visuals, 1.19, 1.285, BOTTOM_Y, ROOF_Y, FRONT_Z - 0.12, FRONT_Z + 0.02, alu)
ribs = []
x = -1.10
while x < 1.11:
    ribs.append((x - 0.02, x + 0.02, FLOOR_Y + 0.90, ROOF_Y - 0.25, FRONT_Z - 0.10, FRONT_Z - 0.08)); x += 0.14
merged_boxes('frontWallRibs', visuals, ribs, door)
box('frontKickPlate', visuals, -HALF_W + 0.02, HALF_W - 0.02, FLOOR_Y, FLOOR_Y + 0.90, FRONT_Z - 0.095, FRONT_Z - 0.08, kick)

# ---- roof, top rails, roof bows inside ----
box('roof', visuals, -HALF_W, HALF_W, ROOF_Y - 0.06, ROOF_Y, REAR_Z + 0.14, FRONT_Z, curtain)
mirrored('sideRailTop', visuals, 1.225, 1.285, ROOF_Y - 0.18, ROOF_Y, REAR_Z + 0.14, FRONT_Z, alu)
for side, sgn in (('Left', 1), ('Right', -1)):  # lip over the curtain and the curtain track
    merged_boxes('sideRailTop%sProfile' % side, visuals,
                 [(*sorted((sgn * 1.285, sgn * 1.300)), ROOF_Y - 0.16, ROOF_Y - 0.02, REAR_Z + 0.14, FRONT_Z),
                  (*sorted((sgn * 1.285, sgn * 1.312)), ROOF_Y - 0.21, ROOF_Y - 0.16, REAR_Z + 0.14, FRONT_Z)], alu)  # lip over the cloth
bows = []
z = FRONT_Z - 0.45
while z > REAR_Z + 0.3:
    bows.append((-1.22, 1.22, ROOF_Y - 0.11, ROOF_Y - 0.06, z - 0.025, z + 0.025)); z -= 0.55
for xs in (-0.6, 0.0, 0.6):
    bows.append((xs - 0.02, xs + 0.02, ROOF_Y - 0.08, ROOF_Y - 0.06, REAR_Z + 0.20, FRONT_Z - 0.10))
merged_boxes('roofBows', visuals, bows, alu)

# ---- rear portal: posts, header with hinge blocks, sill with door keepers ----
mirrored('rearPost', visuals, 1.18, 1.285, BOTTOM_Y, ROOF_Y, REAR_Z, REAR_Z + 0.14, alu)
box('rearHeader', visuals, -1.285, 1.285, ROOF_Y - 0.22, ROOF_Y, REAR_Z, REAR_Z + 0.14, alu)
box('rearSill', visuals, -1.285, 1.285, BOTTOM_Y, FLOOR_Y, REAR_Z, REAR_Z + 0.14, alu)
hdr = []
for xh in (-1.02, -0.36, 0.36, 1.02):           # lock-rod keepers on the header (rods of both doors)
    hdr += [(xh - 0.05, xh + 0.05, ROOF_Y - 0.05, ROOF_Y + 0.02, REAR_Z - 0.04, REAR_Z + 0.02),
            (xh - 0.012, xh + 0.012, ROOF_Y + 0.02, ROOF_Y + 0.06, REAR_Z - 0.03, REAR_Z - 0.006)]
merged_boxes('rearHeaderKeepers', visuals, hdr, galv)
sill = []
for xh in (-1.02, -0.36, 0.36, 1.02):
    sill.append((xh - 0.06, xh + 0.06, BOTTOM_Y + 0.08, BOTTOM_Y + 0.15, REAR_Z - 0.04, REAR_Z))
for sx in (-1, 1):
    sill.append((sx * 1.285 - 0.06, sx * 1.285 + 0.06, BOTTOM_Y + 0.02, BOTTOM_Y + 0.10, REAR_Z - 0.02, REAR_Z + 0.02))
merged_boxes('rearSillKeepers', visuals, sill, galv)

# ---- under-run protection ----
# rear under-run bar between the VOLVO mudflap lettering (top ~0.67) and the number plate (bottom ~0.80)
# fixed to the end of the FH16 chassis (z -4.88..-4.76), not to the box: seen from behind it then sits between the
# lettering and the plate (on the box end, 0.30 m further back, it lined up over the lettering)
# top edge just under the number plate: US plate 0.30 x 0.15 hangs from licensePlateBack (y 0.909), lowest edge with
# frame ~0.814 (placementArea top 0.07 shifts it 0.005 down)
box('rearUnderrun', visuals, -1.15, 1.15, 0.71, 0.81, -4.88, -4.76, steel)
mirrored('rearUnderrunBracket', visuals, 0.40, 0.48, 0.76, CHASSIS_TOP_Y, -4.84, -4.78, steel)
for k, yb in enumerate((0.55, 0.85)):
    mirrored('sideGuardBar%d' % (k + 1), visuals, 1.20, 1.24, yb, yb + 0.10, -0.10, 2.40, alu)
for k, zb in enumerate((2.30, 1.15, 0.00)):
    mirrored('sideGuardBracket%d' % (k + 1), visuals, 1.12, 1.20, 0.55, 1.22, zb - 0.03, zb + 0.03, steel)

# ---- sliding posts (2 per side, behind the curtain; slide to the rear when the curtain opens) ----
for side, sgn in (('Left', 1), ('Right', -1)):
    for k, pz in enumerate(POST_Z):
        g = group('post%s%d' % (side, k + 1), root, sgn * 1.22, FLOOR_Y, pz)
        merged_boxes('post%s%dBody' % (side, k + 1), g,
                     [(*sorted((sgn * 1.185, sgn * 1.255)), FLOOR_Y, ROOF_Y - 0.20, pz - 0.045, pz + 0.045),
                      (*sorted((sgn * 1.17, sgn * 1.26)), ROOF_Y - 0.24, ROOF_Y - 0.18, pz - 0.06, pz + 0.06),
                      (*sorted((sgn * 1.17, sgn * 1.26)), FLOOR_Y, FLOOR_Y + 0.05, pz - 0.06, pz + 0.06)],
                     postMat, origin=(sgn * 1.22, FLOOR_Y, pz))

# ---- side boards inside the curtain (one per bay and height; hidden one by one when the curtain opens) ----
bays = [(CURTAIN_FRONT_Z - 0.03, POST_Z[0] + 0.05), (POST_Z[0] - 0.05, POST_Z[1] + 0.05), (POST_Z[1] - 0.05, REAR_Z + 0.16)]
for side, sgn in (('Left', 1), ('Right', -1)):
    bg = group('boards' + side, root)
    k = 1
    for bz1, bz0 in bays:
        for yb in BOARD_Y:
            box('board%s%02d' % (side, k), bg, *sorted((sgn * 1.20, sgn * 1.225)), FLOOR_Y + yb, FLOOR_Y + yb + 0.14,
                bz0, bz1, boardWood)
            k += 1

# ---- curtains (group origin at the rear end, where the curtain gathers) ----
for side, sgn in (('Left', 1), ('Right', -1)):
    g = group('curtain' + side, root, 0, 0, CURTAIN_REAR_Z)
    closed = group('curtain%sClosed' % side, g, 0, 0, CURTAIN_REAR_Z)
    cloth_panel('curtain%sCloth' % side, closed, sgn, CLOTH_X + 0.008, CLOTH_X, CLOTH_Y0, CLOTH_Y1, CURTAIN_FRONT_Z,
                CURTAIN_REAR_Z, curtainTex)
    # dark reinforcement band at floor height, buckle straps below it, corner marks at the top corners
    X = CLOTH_X + 0.008                      # outer face of the cloth
    det = [(*sorted((sgn * X, sgn * (X + 0.004))), BAND_Y, BAND_Y + 0.045, CURTAIN_REAR_Z + 0.02, CURTAIN_FRONT_Z - 0.02)]
    for zf, dz in ((CURTAIN_FRONT_Z - 0.08, -1), (CURTAIN_REAR_Z + 0.08, 1)):
        det += [(*sorted((sgn * X, sgn * (X + 0.003))), CLOTH_Y1 - 0.30, CLOTH_Y1 - 0.08, *sorted((zf, zf + dz * 0.025))),
                (*sorted((sgn * X, sgn * (X + 0.003))), CLOTH_Y1 - 0.105, CLOTH_Y1 - 0.08, *sorted((zf, zf + dz * 0.20)))]
    merged_boxes('curtain%sBand' % side, closed, det, strap)
    buckles, straps_ = [], []
    z = CURTAIN_FRONT_Z - BUCKLE_PITCH / 2
    while z > CURTAIN_REAR_Z + 0.1:
        straps_.append((*sorted((sgn * X, sgn * (X + 0.005))), BOTTOM_Y + 0.06, BAND_Y + 0.02, z - 0.02, z + 0.02))
        buckles += [(*sorted((sgn * (X + 0.003), sgn * (X + 0.018))), BOTTOM_Y + 0.08, BOTTOM_Y + 0.15, z - 0.022, z + 0.022),
                    (*sorted((sgn * 1.24, sgn * (X + 0.010))), BOTTOM_Y - 0.015, BOTTOM_Y + 0.005, z - 0.012, z + 0.012)]  # hook under the rail
        z -= BUCKLE_PITCH
    merged_boxes('curtain%sStraps' % side, closed, straps_, strap)
    merged_boxes('curtain%sBuckles' % side, closed, buckles, galv)
    # "ProEdition" curtain design (shop option, hidden by default): the waving PRO EDITION banner,
    # boxTruckProEditionCurtain_diffuse.dds (make_curtain_texture.py, 3700 x 760 px banner -> 6.07 x 1.247 m).
    # Just outside the cloth, under the straps; reads front to back on the left, back to front on the right.
    # banner centre 1.092 m below the top of the cloth (as in the approved mock-up), starts 0.325 m behind its front
    bz0, bz1 = CURTAIN_FRONT_Z - 0.325, CURTAIN_FRONT_Z - 0.325 - 6.07
    by0, by1 = ROOF_Y - 0.17 - 1.092 - 1.247 / 2, ROOF_Y - 0.17 - 1.092 + 1.247 / 2
    decal('curtain' + side + 'ProEdition', closed, sgn * (X + 0.0015), by0, by1, *((bz0, bz1) if sgn > 0 else (bz1, bz0)), proDecal)
    for dn, (sheet, tw, th, pcs) in DESIGNS.items():   # shop options, hidden by default
        design_pieces('curtain%sDesign%s' % (side, dn), closed, sgn, pcs, tw, th, X + 0.0025, designMats[dn])
    # open: the curtain gathered at the rear (hidden until the curtain opens)
    opened = group('curtain%sOpen' % side, g, 0, 0, CURTAIN_REAR_Z)
    pleats('curtain%sGathered' % side, opened, sgn, CLOTH_X, 0.12, CLOTH_Y0, CLOTH_Y1, CURTAIN_REAR_Z + GATHER_LEN,
           CURTAIN_REAR_Z + 0.02, 9, curtainTex, seed=7 if sgn > 0 else 11)
    gs = []
    for k in range(4):
        zz = CURTAIN_REAR_Z + 0.06 + k * (GATHER_LEN - 0.08) / 3
        gs.append((*sorted((sgn * (CLOTH_X + 0.15), sgn * (CLOTH_X + 0.155))), BOTTOM_Y + 0.02, BAND_Y + 0.02, zz - 0.02, zz + 0.02))
    merged_boxes('curtain%sGatheredStraps' % side, opened, gs, strap)

# ---- rear barn doors (group origin on the hinge line) ----
for side, sgn in (('Left', 1), ('Right', -1)):
    g = group('rearDoor' + side, root, sgn * DOOR_HINGE_X, 0, REAR_Z)
    x_in, x_out = 0.005, 1.175
    box('door' + side + 'Panel', g, *sorted((sgn * x_in, sgn * x_out)), FLOOR_Y + 0.02, ROOF_Y - 0.23,
        REAR_Z + 0.02, REAR_Z + 0.06, door)
    # outside: frame border and rivets
    fr, rv = [], []
    y0d, y1d = FLOOR_Y + 0.02, ROOF_Y - 0.23
    fr += [(*sorted((sgn * x_in, sgn * x_out)), y0d, y0d + 0.05, REAR_Z + 0.015, REAR_Z + 0.02),
           (*sorted((sgn * x_in, sgn * x_out)), y1d - 0.05, y1d, REAR_Z + 0.015, REAR_Z + 0.02),
           (*sorted((sgn * x_in, sgn * (x_in + 0.05))), y0d, y1d, REAR_Z + 0.015, REAR_Z + 0.02),
           (*sorted((sgn * (x_out - 0.05), sgn * x_out)), y0d, y1d, REAR_Z + 0.015, REAR_Z + 0.02)]
    yy = y0d + 0.15
    while yy < y1d - 0.1:
        for xr in (x_in + 0.025, x_out - 0.025):
            rv.append((sgn * xr - 0.006, sgn * xr + 0.006, yy - 0.006, yy + 0.006, REAR_Z + 0.010, REAR_Z + 0.015))
        yy += 0.25
    xx = x_in + 0.15
    while xx < x_out - 0.1:
        for yr in (y0d + 0.025, y1d - 0.025):
            rv.append((sgn * xx - 0.006, sgn * xx + 0.006, yr - 0.006, yr + 0.006, REAR_Z + 0.010, REAR_Z + 0.015))
        xx += 0.25
    merged_boxes('door%sFrame' % side, g, fr, alu)
    merged_boxes('door%sRivets' % side, g, rv, galv)
    # lock bars with handles and cams
    lk = []
    for j, xb in enumerate((0.28, 0.88)):
        rod('door%sLockBar%d' % (side, j + 1), g, sgn * xb, REAR_Z + 0.002, FLOOR_Y - 0.10, ROOF_Y + 0.03, 0.017, galv)
        lk += [(*sorted((sgn * (xb - 0.02), sgn * (xb + 0.17))), FLOOR_Y + 0.70, FLOOR_Y + 0.74, REAR_Z - 0.03, REAR_Z - 0.005),
               (*sorted((sgn * (xb + 0.13), sgn * (xb + 0.19))), FLOOR_Y + 0.66, FLOOR_Y + 0.78, REAR_Z - 0.035, REAR_Z - 0.02)]
        for yg in (FLOOR_Y + 0.25, (FLOOR_Y + ROOF_Y) / 2, ROOF_Y - 0.45):
            lk.append((*sorted((sgn * (xb - 0.035), sgn * (xb + 0.035))), yg, yg + 0.05, REAR_Z - 0.005, REAR_Z + 0.015))
    merged_boxes('door%sLockParts' % side, g, lk, galv)
    hg = []
    for yh in (FLOOR_Y + 0.15, FLOOR_Y + 0.85, ROOF_Y - 0.90, ROOF_Y - 0.40):
        hg += [(*sorted((sgn * 0.98, sgn * 1.29)), yh, yh + 0.07, REAR_Z - 0.012, REAR_Z + 0.02),
               (*sorted((sgn * 1.275, sgn * 1.30)), yh - 0.02, yh + 0.09, REAR_Z - 0.02, REAR_Z + 0.02)]
    merged_boxes('door%sHinges' % side, g, hg, steel)
    # inside: pressed panels (3 rows x 2), the spare lock rod clipped on the left door, stickers on the right door
    rects = []
    for r in range(3):
        ry0 = y0d + 0.12 + r * (y1d - y0d - 0.20) / 3
        ry1 = ry0 + (y1d - y0d - 0.20) / 3 - 0.10
        for c in range(2):
            cx0 = x_in + 0.08 + c * (x_out - x_in - 0.14) / 2
            cx1 = cx0 + (x_out - x_in - 0.14) / 2 - 0.08
            rects.append(tuple(sorted((sgn * cx0, sgn * cx1))) + (ry0, ry1))
    rounded_panels('door%sPressings' % side, g, 1, rects, REAR_Z + 0.06, 0.012, 0.07, door)
    if sgn > 0:
        rod_ob = rod('doorLeftSpareRod', g, sgn * 0.45, REAR_Z + 0.085, FLOOR_Y + 0.20, ROOF_Y - 0.60, 0.012, galv)
        rod_ob.rotation_euler[1] = math.radians(14)
        merged_boxes('doorLeftRodClips', g, [(sgn * 0.20 - 0.02, sgn * 0.20 + 0.02, FLOOR_Y + 0.30, FLOOR_Y + 0.34, REAR_Z + 0.06, REAR_Z + 0.10),
                                             (sgn * 0.70 - 0.02, sgn * 0.70 + 0.02, ROOF_Y - 0.72, ROOF_Y - 0.68, REAR_Z + 0.06, REAR_Z + 0.10)], galv)
    else:
        decal_inside('doorRightStickers', g, sgn * 0.62, sgn * 0.20, FLOOR_Y + 0.25, FLOOR_Y + 1.09, REAR_Z + 0.0625, stickerMat)
    col('colDoor' + side, g, *sorted((sgn * x_in, sgn * x_out)), FLOOR_Y + 0.02, ROOF_Y - 0.23,
        REAR_Z + 0.02, REAR_Z + 0.06)

# ---- collisions ----
cols = group('collisions', root)
col('colFloor', cols, -HALF_W, HALF_W, FLOOR_Y - 0.12, FLOOR_Y, REAR_Z + 0.14, FRONT_Z - 0.08)
col('colFrontWall', cols, -HALF_W, HALF_W, FLOOR_Y, ROOF_Y - 0.06, FRONT_Z - 0.08, FRONT_Z)
col('colRoof', cols, -HALF_W, HALF_W, ROOF_Y - 0.10, ROOF_Y, REAR_Z + 0.14, FRONT_Z)
for side, sgn in (('Left', 1), ('Right', -1)):
    # side wall: lifted straight up above the roof while the curtain is open (moves only in its own plane)
    pivot = group('colSide%sPivot' % side, cols, sgn * 1.25, ROOF_Y - 0.20, 0)
    col('colSide' + side, pivot, *sorted((sgn * 1.23, sgn * 1.27)), FLOOR_Y, ROOF_Y - 0.20, REAR_Z + 0.14, FRONT_Z - 0.08)
    # the posts keep their own collision and slide back with them
    for k, pz in enumerate(POST_Z):
        col('colPost%s%d' % (side, k + 1), bpy.data.objects['post%s%d' % (side, k + 1)],
            *sorted((sgn * 1.185, sgn * 1.255)), FLOOR_Y, ROOF_Y - 0.20, pz - 0.045, pz + 0.045)

# ---- tension belts: start nodes on the left floor edge, local z across to the right edge ----
belts = group('tensionBelts', root)
belt_span = 2.478
for n in range(BELT_COUNT):
    bz = 1.55 + SHIFT_Z - n * 0.785
    s = group('beltStart%02d' % (n + 1), belts, 1.235, FLOOR_Y + 0.02, bz, rot_y_deg=-90)
    group('beltStart%02dEnd' % (n + 1), s, -1.243, FLOOR_Y + 0.02, bz, rot_y_deg=-90)

trig = box('beltActivationTrigger', root, -1.40, 1.40, FLOOR_Y, ROOF_Y - 0.10, REAR_Z + 0.03, FRONT_Z + 0.05, colmat)
trig['i3D_collision'] = True
trig['i3D_kinematic'] = True
trig['i3D_compound'] = True
trig['i3D_trigger'] = True
trig['i3D_collisionFilterGroup'] = TRIGGER_GROUP
trig['i3D_collisionFilterMask'] = TRIGGER_MASK
trig['i3D_nonRenderable'] = True
trig['i3D_castsShadows'] = False
trig['i3D_receiveShadows'] = False
trig.hide_render = True

# ---- stand-ins (NOT part of the mod: show where the game FH16 cab, chassis and wheels are) ----
COLL = collection('standIn_notExported')
box('standIn_cab', None, -1.24, 1.24, 0.75, 3.85, 2.15, 4.50, standin)
mirrored('standIn_chassisRail', None, 0.36, 0.48, 0.85, 1.18, -4.70, 4.40, steel)
for name, zc, single in (('front', 3.066, True), ('back01', -0.740, False), ('back02', -2.111, False),
                         ('back03', -3.492, True)):
    for side, sgn in (('L', 1), ('R', -1)):
        if single:
            wheel('standIn_wheel_%s%s' % (name, side), None, sgn * 1.06, WHEEL_R, zc, WHEEL_R, 0.385, tyre)
        else:
            wheel('standIn_wheel_%s%sIn' % (name, side), None, sgn * 0.77, WHEEL_R, zc, WHEEL_R, 0.315, tyre)
            wheel('standIn_wheel_%s%sOut' % (name, side), None, sgn * 1.10, WHEEL_R, zc, WHEEL_R, 0.315, tyre)

bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
ground = bpy.context.object; ground.name = 'standIn_ground'
ground.data.materials.append(mat('ground', (0.55, 0.57, 0.52)))
for c in ground.users_collection: c.objects.unlink(ground)
put(ground, None)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, PREFIX + '.blend'))

if RENDER:
    # ---- preview renders (Workbench, material colours) ----
    scene.render.engine = 'BLENDER_WORKBENCH'
    sh = scene.display.shading
    sh.light = 'STUDIO'
    sh.color_type = 'MATERIAL'
    sh.show_cavity = True
    sh.show_shadows = True
    sh.show_object_outline = True
    scene.render.resolution_x, scene.render.resolution_y = 1600, 900
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new('w')
    scene.world.color = (0.80, 0.84, 0.88)

    target = bpy.data.objects.new('camTarget', None)
    scene.collection.objects.link(target)
    cam_data = bpy.data.cameras.new('cam')
    cam = bpy.data.objects.new('cam', cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    trk = cam.constraints.new('TRACK_TO')
    trk.target = target; trk.track_axis = 'TRACK_NEGATIVE_Z'; trk.up_axis = 'UP_Y'

    views = [
        ('front_left', (9.0, 3.2, 9.5), (0, 1.9, -0.6), 'PERSP', 32),
        ('rear_right', (-8.0, 3.4, -13.5), (0, 1.9, -1.2), 'PERSP', 32),
        ('side_left', (25.0, 2.0, -0.4), (0, 2.0, -0.4), 'ORTHO', 11.5),
        ('rear', (0, 2.2, -20.0), (0, 2.1, 0), 'ORTHO', 5.2),
    ]
    for vname, cpos, tpos, ctype, lens in views:
        cam.location = g2b(*cpos)
        target.location = g2b(*tpos)
        cam_data.type = ctype
        if ctype == 'ORTHO':
            cam_data.ortho_scale = lens
        else:
            cam_data.lens = lens
        scene.render.filepath = os.path.join(OUT_DIR, '%s_%s.png' % (PREFIX, vname))
        bpy.ops.render.render(write_still=True)
        print('RENDERED', scene.render.filepath)

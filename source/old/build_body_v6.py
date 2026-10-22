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
MID_POST_Z = -1.45 + SHIFT_Z  # removable middle post on each side
CURTAIN_FRONT_Z = FRONT_Z - 0.12
DOOR_HINGE_X = 1.29   # barn door hinge line (outside the rear post, so open doors lie along the sides)
BELT_COUNT = 9
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

alu = mat('alu', (0.62, 0.64, 0.66))
curtain = mat('curtain', (0.90, 0.90, 0.88))
strap = mat('strap', (0.12, 0.12, 0.13))
wood = mat('floorWood', (0.42, 0.30, 0.20))
door = mat('door', (0.86, 0.86, 0.84))
proDecal = mat('proEditionDecal', (0.81, 0.06, 0.09))
steel = mat('steelDark', (0.16, 0.16, 0.17))
colmat = mat('collision', (0.9, 0.2, 0.2))
standin = mat('standIn', (0.35, 0.45, 0.62))
tyre = mat('tyre', (0.05, 0.05, 0.05))

COLL = collection('body')
root = group('boxBody', None)
visuals = group('visuals', root)

# ---- floor and subframe ----
mirrored('subframeRail', visuals, 0.38, 0.48, CHASSIS_TOP_Y, FLOOR_Y - 0.14, REAR_Z + 0.14, FRONT_Z - 0.05, steel)
z = FRONT_Z - 0.10
i = 1
while z > REAR_Z + 0.14:
    box('crossMember%02d' % i, visuals, -HALF_W, HALF_W, FLOOR_Y - 0.20, FLOOR_Y - 0.12, z - 0.03, z + 0.03, steel)
    z -= 0.60; i += 1
box('floor', visuals, -HALF_W, HALF_W, FLOOR_Y - 0.12, FLOOR_Y, REAR_Z + 0.14, FRONT_Z - 0.08, wood)
mirrored('sideRailBottom', visuals, 1.235, 1.285, BOTTOM_Y, FLOOR_Y + 0.02, REAR_Z + 0.14, FRONT_Z - 0.08, alu)

# ---- front wall ----
box('frontWall', visuals, -HALF_W + 0.01, HALF_W - 0.01, FLOOR_Y, ROOF_Y - 0.06, FRONT_Z - 0.08, FRONT_Z, door)
mirrored('frontPost', visuals, 1.19, 1.285, BOTTOM_Y, ROOF_Y, FRONT_Z - 0.12, FRONT_Z + 0.02, alu)

# ---- roof and top rails ----
box('roof', visuals, -HALF_W, HALF_W, ROOF_Y - 0.06, ROOF_Y, REAR_Z + 0.14, FRONT_Z, curtain)
mirrored('sideRailTop', visuals, 1.225, 1.285, ROOF_Y - 0.18, ROOF_Y, REAR_Z + 0.14, FRONT_Z, alu)

# ---- rear frame ----
mirrored('rearPost', visuals, 1.18, 1.285, BOTTOM_Y, ROOF_Y, REAR_Z, REAR_Z + 0.14, alu)
box('rearHeader', visuals, -1.285, 1.285, ROOF_Y - 0.22, ROOF_Y, REAR_Z, REAR_Z + 0.14, alu)
box('rearSill', visuals, -1.285, 1.285, BOTTOM_Y, FLOOR_Y, REAR_Z, REAR_Z + 0.14, alu)

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

# ---- middle posts (slide to the front with the curtain) ----
mirrored('middlePost', root, 1.235, 1.275, FLOOR_Y, ROOF_Y - 0.18, MID_POST_Z - 0.05, MID_POST_Z + 0.05, alu)

# ---- curtains with tension straps (group origin at the curtain's front edge) ----
for side, sgn in (('Left', 1), ('Right', -1)):
    g = group('curtain' + side, root, 0, 0, CURTAIN_FRONT_Z)
    box('curtain' + side + 'Cloth', g, *sorted((sgn * 1.262, sgn * 1.272)), FLOOR_Y - 0.06,
        ROOF_Y - 0.17, REAR_Z + 0.14, CURTAIN_FRONT_Z, curtain)
    # "ProEdition" curtain design (shop option, hidden by default): the waving PRO EDITION banner,
    # boxTruckProEditionCurtain_diffuse.dds (make_curtain_texture.py, 3700 x 760 px banner -> 6.07 x 1.247 m).
    # Just outside the cloth, under the straps; reads front to back on the left, back to front on the right.
    # banner centre 1.092 m below the top of the cloth (as in the approved mock-up), starts 0.325 m behind its front
    bz0, bz1 = CURTAIN_FRONT_Z - 0.325, CURTAIN_FRONT_Z - 0.325 - 6.07
    by0, by1 = ROOF_Y - 0.17 - 1.092 - 1.247 / 2, ROOF_Y - 0.17 - 1.092 + 1.247 / 2
    decal('curtain' + side + 'ProEdition', g, sgn * 1.2735, by0, by1, *((bz0, bz1) if sgn > 0 else (bz1, bz0)), proDecal)
    z = FRONT_Z - 0.40
    k = 1
    while z > REAR_Z + 0.28:
        box('curtain%sStrap%02d' % (side, k), g, *sorted((sgn * 1.272, sgn * 1.280)), BOTTOM_Y + 0.04,
            ROOF_Y - 0.17, z - 0.025, z + 0.025, strap)
        box('curtain%sBuckle%02d' % (side, k), g, *sorted((sgn * 1.272, sgn * 1.290)), BOTTOM_Y + 0.04, BOTTOM_Y + 0.14,
            z - 0.035, z + 0.035, steel)
        z -= 0.55; k += 1

# ---- rear barn doors (group origin on the hinge line) ----
for side, sgn in (('Left', 1), ('Right', -1)):
    g = group('rearDoor' + side, root, sgn * DOOR_HINGE_X, 0, REAR_Z)
    x_in, x_out = 0.005, 1.175
    box('door' + side + 'Panel', g, *sorted((sgn * x_in, sgn * x_out)), FLOOR_Y + 0.02, ROOF_Y - 0.23,
        REAR_Z + 0.02, REAR_Z + 0.06, door)
    for j, xb in enumerate((0.28, 0.88)):
        rod('door%sLockBar%d' % (side, j + 1), g, sgn * xb, REAR_Z + 0.005, FLOOR_Y + 0.05, ROOF_Y - 0.26,
            0.018, alu)
        box('door%sLockHandle%d' % (side, j + 1), g, *sorted((sgn * (xb - 0.02), sgn * (xb + 0.16))),
            FLOOR_Y + 0.70, FLOOR_Y + 0.74, REAR_Z - 0.015, REAR_Z + 0.005, alu)
    for j, yh in enumerate((FLOOR_Y + 0.30, (FLOOR_Y + ROOF_Y) / 2, ROOF_Y - 0.73)):
        box('door%sHinge%d' % (side, j + 1), g, *sorted((sgn * 1.10, sgn * 1.29)), yh, yh + 0.06,
            REAR_Z - 0.01, REAR_Z + 0.03, steel)
    col('colDoor' + side, g, *sorted((sgn * x_in, sgn * x_out)), FLOOR_Y + 0.02, ROOF_Y - 0.23,
        REAR_Z + 0.02, REAR_Z + 0.06)

# ---- collisions ----
cols = group('collisions', root)
col('colFloor', cols, -HALF_W, HALF_W, FLOOR_Y - 0.12, FLOOR_Y, REAR_Z + 0.14, FRONT_Z - 0.08)
col('colFrontWall', cols, -HALF_W, HALF_W, FLOOR_Y, ROOF_Y - 0.06, FRONT_Z - 0.08, FRONT_Z)
col('colRoof', cols, -HALF_W, HALF_W, ROOF_Y - 0.10, ROOF_Y, REAR_Z + 0.14, FRONT_Z)
for side, sgn in (('Left', 1), ('Right', -1)):
    pivot = group('colSide%sPivot' % side, cols, sgn * 1.25, ROOF_Y - 0.20, 0)
    col('colSide' + side, pivot, *sorted((sgn * 1.23, sgn * 1.27)), FLOOR_Y, ROOF_Y - 0.20, REAR_Z + 0.14, FRONT_Z - 0.08)

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

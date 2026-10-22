# Builds the curtain-sider body for the Box Truck Pro Edition in Blender and renders preview pictures.
# Run: blender.exe -b -P build_body.py -- <out_dir> <preview_prefix>
# All sizes are written in GAME coordinates (x = left, y = up, z = forward, truck origin = FH16 origin)
# and converted to Blender (x, -z, y) when the objects are made. Measurements: ..\reference_fh16BoxTruck.md
import bpy, bmesh, sys, os, math
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
OUT_DIR = args[0]
PREFIX = args[1] if len(args) > 1 else 'body_v1'

# ---- main sizes (game coordinates, metres) ----
HALF_W = 1.275        # outside half width (2.55 m)
FLOOR_Y = 1.50        # top of the load floor
ROOF_Y = 4.00         # top of the body
FRONT_Z = 2.00        # outside face of the front wall
REAR_Z = -4.98        # outside face of the rear doors
MID_POST_Z = -1.45    # removable middle post on each side
WHEEL_R = 0.535

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

def box(name, coll, x0, x1, y0, y1, z0, z1, material):
    """Axis-aligned box from game-space min/max; object origin at the box centre."""
    sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * sx, v.co.y * sz, v.co.z * sy))  # blender x,y,z = game x,z,y sizes
    bm.to_mesh(me); bm.free()
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    ob.location = g2b((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    coll.objects.link(ob)
    return ob

def mirrored(name, coll, x0, x1, *rest):
    """Left box (positive x) plus its mirror on the right."""
    return [box(name + 'Left', coll, x0, x1, *rest), box(name + 'Right', coll, -x1, -x0, *rest)]

def rod(name, coll, x, z, y0, y1, r, material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=r, depth=y1 - y0, location=g2b(x, (y0 + y1) / 2, z))
    ob = bpy.context.object; ob.name = name
    ob.data.materials.append(material)
    for c in ob.users_collection: c.objects.unlink(ob)
    coll.objects.link(ob)
    return ob

def wheel(name, coll, x, y, z, radius, width, material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=width, location=g2b(x, y, z),
                                        rotation=(0, math.pi / 2, 0))
    ob = bpy.context.object; ob.name = name
    ob.data.materials.append(material)
    for c in ob.users_collection: c.objects.unlink(ob)
    coll.objects.link(ob)
    return ob

alu = mat('alu', (0.62, 0.64, 0.66))
curtain = mat('curtain', (0.90, 0.90, 0.88))
strap = mat('strap', (0.12, 0.12, 0.13))
wood = mat('floorWood', (0.42, 0.30, 0.20))
door = mat('door', (0.86, 0.86, 0.84))
steel = mat('steelDark', (0.16, 0.16, 0.17))
standin = mat('standIn', (0.35, 0.45, 0.62))
tyre = mat('tyre', (0.05, 0.05, 0.05))

body = collection('body')
ref = collection('standIn_notExported')

# ---- floor and subframe ----
mirrored('subframeRail', body, 0.38, 0.48, 1.18, 1.36, -4.84, 1.95, steel)
z = 1.90
i = 1
while z > -4.84:
    box('crossMember%02d' % i, body, -HALF_W, HALF_W, 1.30, 1.38, z - 0.03, z + 0.03, steel)
    z -= 0.60; i += 1
box('floor', body, -HALF_W, HALF_W, 1.38, FLOOR_Y, -4.84, 1.92, wood)
mirrored('sideRailBottom', body, 1.235, 1.285, 1.22, FLOOR_Y + 0.02, -4.84, 1.92, alu)

# ---- front wall ----
box('frontWall', body, -HALF_W + 0.01, HALF_W - 0.01, FLOOR_Y, ROOF_Y - 0.06, FRONT_Z - 0.08, FRONT_Z, door)
mirrored('frontPost', body, 1.19, 1.285, 1.22, ROOF_Y, FRONT_Z - 0.12, FRONT_Z + 0.02, alu)

# ---- roof and top rails ----
box('roof', body, -HALF_W, HALF_W, ROOF_Y - 0.06, ROOF_Y, -4.84, FRONT_Z, curtain)
mirrored('sideRailTop', body, 1.225, 1.285, ROOF_Y - 0.18, ROOF_Y, -4.84, FRONT_Z, alu)

# ---- rear frame ----
mirrored('rearPost', body, 1.18, 1.285, 1.22, ROOF_Y, REAR_Z, REAR_Z + 0.14, alu)
box('rearHeader', body, -1.285, 1.285, ROOF_Y - 0.22, ROOF_Y, REAR_Z, REAR_Z + 0.14, alu)
box('rearSill', body, -1.285, 1.285, 1.22, FLOOR_Y, REAR_Z, REAR_Z + 0.14, alu)

# ---- rear barn doors (hinges on the outside edges) ----
doors = collection('rearDoors')
for side, sgn in (('Left', 1), ('Right', -1)):
    x_in, x_out = 0.005, 1.175
    d = box('door' + side, doors, *sorted((sgn * x_in, sgn * x_out)), FLOOR_Y + 0.02, ROOF_Y - 0.23,
            REAR_Z + 0.02, REAR_Z + 0.06, door)
    for j, xb in enumerate((0.28, 0.88)):
        rod('door%sLockBar%d' % (side, j + 1), doors, sgn * xb, REAR_Z + 0.005, FLOOR_Y + 0.05, ROOF_Y - 0.26,
            0.018, alu)
        box('door%sLockHandle%d' % (side, j + 1), doors, *sorted((sgn * (xb - 0.02), sgn * (xb + 0.16))),
            2.20, 2.24, REAR_Z - 0.015, REAR_Z + 0.005, alu)
    for j, yh in enumerate((1.80, 2.80, 3.50)):
        box('door%sHinge%d' % (side, j + 1), doors, *sorted((sgn * 1.10, sgn * 1.29)), yh, yh + 0.06,
            REAR_Z - 0.01, REAR_Z + 0.03, steel)

# ---- middle posts ----
mirrored('middlePost', body, 1.235, 1.275, FLOOR_Y, ROOF_Y - 0.18, MID_POST_Z - 0.05, MID_POST_Z + 0.05, alu)

# ---- curtains with tension straps ----
curtains = collection('curtains')
for side, sgn in (('Left', 1), ('Right', -1)):
    box('curtain' + side + '_closed', curtains, *sorted((sgn * 1.262, sgn * 1.272)), FLOOR_Y - 0.06,
        ROOF_Y - 0.17, -4.84, FRONT_Z - 0.12, curtain)
    z = FRONT_Z - 0.40
    k = 1
    while z > -4.70:
        box('curtain%sStrap%02d' % (side, k), curtains, *sorted((sgn * 1.272, sgn * 1.280)), 1.26,
            ROOF_Y - 0.17, z - 0.025, z + 0.025, strap)
        box('curtain%sBuckle%02d' % (side, k), curtains, *sorted((sgn * 1.272, sgn * 1.290)), 1.26, 1.36,
            z - 0.035, z + 0.035, steel)
        z -= 0.55; k += 1

# ---- under-run protection ----
box('rearUnderrun', body, -1.15, 1.15, 0.45, 0.60, -4.88, -4.76, steel)
mirrored('rearUnderrunBracket', body, 0.40, 0.48, 0.55, 1.22, -4.84, -4.78, steel)
for k, yb in enumerate((0.55, 0.85)):
    mirrored('sideGuardBar%d' % (k + 1), body, 1.20, 1.24, yb, yb + 0.10, -0.10, 2.40, alu)
for k, zb in enumerate((2.30, 1.15, 0.00)):
    mirrored('sideGuardBracket%d' % (k + 1), body, 1.12, 1.20, 0.55, 1.22, zb - 0.03, zb + 0.03, steel)

# ---- stand-ins (NOT part of the mod: show where the game FH16 cab, chassis and wheels are) ----
box('standIn_cab', ref, -1.24, 1.24, 0.75, 3.85, 2.15, 4.50, standin)
mirrored('standIn_chassisRail', ref, 0.36, 0.48, 0.85, 1.18, -4.70, 4.40, steel)
for name, zc, single in (('front', 3.066, True), ('back01', -0.740, False), ('back02', -2.111, False),
                         ('back03', -3.492, True)):
    for side, sgn in (('L', 1), ('R', -1)):
        if single:
            wheel('standIn_wheel_%s%s' % (name, side), ref, sgn * 1.06, WHEEL_R, zc, WHEEL_R, 0.385, tyre)
        else:
            wheel('standIn_wheel_%s%sIn' % (name, side), ref, sgn * 0.77, WHEEL_R, zc, WHEEL_R, 0.315, tyre)
            wheel('standIn_wheel_%s%sOut' % (name, side), ref, sgn * 1.10, WHEEL_R, zc, WHEEL_R, 0.315, tyre)

# ground
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
ground = bpy.context.object; ground.name = 'standIn_ground'
ground.data.materials.append(mat('ground', (0.55, 0.57, 0.52)))
for c in ground.users_collection: c.objects.unlink(ground)
ref.objects.link(ground)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, PREFIX + '.blend'))

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

# Preview renders of a build_body.py .blend (Eevee, textures from <tex dir>): closed, curtain open, doors open.
# Run: blender.exe -b <body.blend> -P preview_body.py -- <tex dir> <out prefix>
import bpy, sys, math, os
from mathutils import Vector
args = sys.argv[sys.argv.index('--') + 1:]
TEX, OUT = args[0], args[1]
SHEETS = args[2] if len(args) > 2 else TEX   # folder with profiLinerPaintjobN_diffuse.png (preview only)
scene = bpy.context.scene
g2b = lambda x, y, z: Vector((x, -z, y))

def img(name, noncolor=False):
    im = bpy.data.images.load(os.path.join(TEX, name))
    if noncolor: im.colorspace_settings.name = 'Non-Color'
    return im
def setup(m, tex=None, normal=None, alpha=False, rough=0.55, metal=0.0):
    m.use_nodes = True
    nt = m.node_tree; bsdf = nt.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = m.diffuse_color
    bsdf.inputs['Roughness'].default_value = rough; bsdf.inputs['Metallic'].default_value = metal
    uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'uv0'
    if tex:
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = img(tex); nt.links.new(uvn.outputs[0], t.inputs[0])
        if alpha:
            nt.links.new(t.outputs['Color'], bsdf.inputs['Base Color']); nt.links.new(t.outputs['Alpha'], bsdf.inputs['Alpha'])
            m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else None
        else:
            mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
            mix.inputs['Factor'].default_value = 1.0
            mix.inputs[6].default_value = m.diffuse_color
            nt.links.new(t.outputs['Color'], mix.inputs[7]); nt.links.new(mix.outputs[2], bsdf.inputs['Base Color'])
    if normal:
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = img(normal, True); nt.links.new(uvn.outputs[0], t.inputs[0])
        nm = nt.nodes.new('ShaderNodeNormalMap'); nm.uv_map = 'uv0'; nm.inputs['Strength'].default_value = 1.5
        nt.links.new(t.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs[0], bsdf.inputs['Normal'])

for m in bpy.data.materials:
    if m.name == 'curtainCloth': setup(m, 'boxTruckCurtain_diffuse.png', 'boxTruckCurtain_normal.png', rough=0.8)
    elif m.name == 'proEditionDecal': setup(m, 'boxTruckProEditionCurtain_diffuse.png', alpha=True, rough=0.7)
    elif m.name == 'stickers': setup(m, 'boxTruckStickers_diffuse.png', alpha=True)
    elif m.name.startswith('design'):
        sheet = {'designKrone': 1, 'designFSL': 2, 'designGIANTS': 3}[m.name]
        setup(m, os.path.join(SHEETS, 'profiLinerPaintjob%d_diffuse.png' % sheet), alpha=True, rough=0.7)
    elif m.name in ('galvanized',): setup(m, rough=0.35, metal=0.6)
    else: setup(m)

# show the ProEdition design on the left side only (to compare plain / printed in one picture)
for ob in bpy.data.objects:
    if ob.name == 'curtainRightProEdition': ob.hide_render = True
for ob in bpy.data.objects:
    if ob.name.startswith('standIn_cab'): ob.hide_render = False

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x, scene.render.resolution_y = 1600, 900
world = bpy.data.worlds.new('w'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.62, 0.70, 0.80, 1); world.node_tree.nodes['Background'].inputs[1].default_value = 0.9
sun_d = bpy.data.lights.new('sun', 'SUN'); sun_d.energy = 3.2; sun_d.angle = math.radians(3)
sun = bpy.data.objects.new('sun', sun_d); scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(140))
try:
    scene.view_settings.view_transform = 'AgX'
except Exception:
    pass
cam_d = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_d); scene.collection.objects.link(cam); scene.camera = cam
tgt = bpy.data.objects.new('tgt', None); scene.collection.objects.link(tgt)
c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'

O = {o.name: o for o in bpy.data.objects}
base = {n: (O[n].location.copy(), O[n].rotation_euler.copy()) for n in O}
def reset():
    for n, (l, r) in base.items():
        O[n].location = l.copy(); O[n].rotation_euler = r.copy()
    for side in ('Left', 'Right'):
        O['curtain%sClosed' % side].hide_render = False
        for ch in O['curtain%sClosed' % side].children_recursive: ch.hide_render = ch.name == 'curtainRightProEdition' or 'Design' in ch.name
        for ch in [O['curtain%sOpen' % side]] + list(O['curtain%sOpen' % side].children_recursive): ch.hide_render = True
        for ch in O['boards' + side].children: ch.hide_render = False
def open_curtain(side, rear_z):
    for ch in O['curtain%sClosed' % side].children_recursive: ch.hide_render = True
    for ch in [O['curtain%sOpen' % side]] + list(O['curtain%sOpen' % side].children_recursive): ch.hide_render = False
    for ch in O['boards' + side].children: ch.hide_render = True
    for k, z in ((1, rear_z + 0.30), (2, rear_z + 0.16)):     # posts parked at the rear, front post last
        p = O['post%s%d' % (side, k)]; p.location.y = -z
def open_doors(deg):
    O['rearDoorLeft'].rotation_euler[2] += math.radians(-deg); O['rearDoorRight'].rotation_euler[2] += math.radians(deg)
for n in O:
    if n.startswith('col') or n == 'beltActivationTrigger': O[n].hide_render = True

def shot(name, cpos, tpos, lens=35, ortho=None):
    cam.location = g2b(*cpos); tgt.location = g2b(*tpos)
    if ortho: cam_d.type = 'ORTHO'; cam_d.ortho_scale = ortho
    else: cam_d.type = 'PERSP'; cam_d.lens = lens
    scene.render.filepath = OUT + '_' + name + '.png'
    bpy.ops.render.render(write_still=True); print('RENDERED', scene.render.filepath)

REAR = -5.21
if len(args) > 3 and args[3] == 'designs':
    for dn in ('ProEdition', 'Krone', 'FSL', 'GIANTS'):
        reset()
        for side in ('Left', 'Right'):
            for ch in O['curtain%sClosed' % side].children_recursive:
                if 'Design' in ch.name or 'ProEdition' in ch.name:
                    ch.hide_render = not (ch.name.endswith(dn))
        shot('design%s_left' % dn, (24, 2.4, -1.6), (0, 2.4, -1.6), ortho=10.5)
        shot('design%s_right' % dn, (-24, 2.4, -1.6), (0, 2.4, -1.6), ortho=10.5)
    raise SystemExit
reset(); shot('side_closed', (24, 2.4, -1.6), (0, 2.4, -1.6), ortho=10.5)
reset(); shot('rear34_closed', (7.5, 3.6, -12.5), (0, 2.3, -3.0), lens=40)
reset(); open_curtain('Left', REAR); shot('side_open', (9.5, 3.4, 3.5), (0, 2.4, -2.2), lens=32)
reset(); open_doors(100); shot('rear_doorsOpen', (0.6, 2.9, -12.0), (0, 2.5, -4.0), lens=42)
reset(); shot('buckles_close', (3.2, 1.9, -3.2), (1.27, 1.7, -2.6), lens=50)

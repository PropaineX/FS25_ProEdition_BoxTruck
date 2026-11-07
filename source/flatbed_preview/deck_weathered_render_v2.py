"""Blender (background) mock-up of the weathered deck: before / after / close-up renders.
Never saves the blend. Run:
blender -b previews/flatbed_tailgate_v3/flatbed_tailgate_proposal_v3.blend --python source/flatbed_preview/deck_weathered_render_v1.py -- <out_dir> <texture_dir>
"""
import bpy, sys, math, random
from mathutils import Vector

out_dir, tex_dir = sys.argv[sys.argv.index('--') + 1:][:2]
GAME = 'G:/SteamLibrary/steamapps/common/Farming Simulator 25/data/shared/detailLibrary/nonMetallic/wood/'
STRIP_LEN, STRIPS = 3.40, 8

planks = sorted([o for o in bpy.data.objects if o.name.startswith('Deck plank')], key=lambda o: o.name)
assert len(planks) == 15

# hide loads / helpers / stakes so the bed is clear; keep boards up
for o in bpy.data.objects:
    n = o.name.lower()
    if any(k in n for k in ('milk', 'pallet', 'stake', 'belt', 'col', 'trigger')):
        o.hide_render = True

# --- UVs: planar along each board, each plank its own strip + offset ---------------------------------
random.seed(7)
for i, ob in enumerate(planks):
    me = ob.data
    if not me.uv_layers: me.uv_layers.new(name='UVMap')
    uv = me.uv_layers.active.data
    xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]
    x0, x1, y0 = min(xs), max(xs), min(ys)
    strip = i % STRIPS
    v_lo = 1 - (strip + 1) / STRIPS
    off = random.random()
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            u = (co.y - y0) / STRIP_LEN + off
            v = v_lo + (0.01 + 0.98 * (co.x - x0) / (x1 - x0)) / STRIPS
            uv[li].uv = (u, v)

def material(name, base_img, tint=None, normal_img=None, rough=0.85):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; bsdf = nt.nodes['Principled BSDF']
    img = nt.nodes.new('ShaderNodeTexImage'); img.image = bpy.data.images.load(base_img)
    color = img.outputs['Color']
    if tint:
        mix = nt.nodes.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'; mix.inputs['Fac'].default_value = 1
        mix.inputs['Color2'].default_value = (*tint, 1)
        nt.links.new(color, mix.inputs['Color1']); color = mix.outputs['Color']
    nt.links.new(color, bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = rough
    if normal_img:
        nimg = nt.nodes.new('ShaderNodeTexImage'); nimg.image = bpy.data.images.load(normal_img)
        nimg.image.colorspace_settings.name = 'Non-Color'
        nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 1.0
        nt.links.new(nimg.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    return m

# before = what the game shows now: oak detail, tinted with the deck's colorScale (0.231 0.161 0.102)
before = material('deck before', GAME + 'wood2Oak_diffuse.dds', tint=(0.231, 0.161, 0.102), rough=0.7)
after = material('deck after', tex_dir + '/flatbedDeckWeathered_diffuse.png',
                 normal_img=tex_dir + '/flatbedDeckWeathered_normal.png', rough=0.9)

# --- scene: sun + soft sky, camera from the rear corner --------------------------------------------
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.samples = 48; sc.cycles.device = 'CPU'
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
sc.view_settings.view_transform = 'AgX'
world = bpy.data.worlds.new('w'); sc.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.62, 0.66, 0.72, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.45
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sc.collection.objects.link(sun)
sun.data.energy = 2.2; sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))

pts = [p.matrix_world @ Vector(c) for p in planks for c in p.bound_box]
lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
mid = (lo + hi) / 2
tail = [o for o in bpy.data.objects if 'tailgate' in o.name.lower()]
head = [o for o in bpy.data.objects if 'headboard' in o.name.lower()]
rear_sign = -1 if head and (head[0].matrix_world.translation.y > mid.y) else 1
print('[DECK] headboard', [o.name for o in head][:2], 'rear_sign', rear_sign)
rear_y = hi.y if rear_sign > 0 else lo.y

cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
def shoot(pos, target, lens, path):
    cam.location = pos; cam.data.lens = lens
    cam.rotation_euler = (target - pos).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = path; bpy.ops.render.render(write_still=True)

wide_pos = Vector((hi.x + 2.6, rear_y + rear_sign * 3.2, hi.z + 2.6))
wide_tgt = Vector((mid.x, mid.y, hi.z))
close_pos = Vector((mid.x + 0.6, rear_y + rear_sign * 0.4, hi.z + 1.0))
close_tgt = Vector((mid.x - 0.1, rear_y - rear_sign * 1.4, hi.z))
for p in planks: p.data.materials.clear(); p.data.materials.append(before)
shoot(wide_pos, wide_tgt, 30, out_dir + '/01_before_wide_v3.png')
for p in planks: p.data.materials.clear(); p.data.materials.append(after)
shoot(wide_pos, wide_tgt, 30, out_dir + '/02_after_wide_v3.png')
for p in planks: p.data.materials.clear(); p.data.materials.append(before)
shoot(close_pos, close_tgt, 28, out_dir + '/04_before_close_v3.png')
for p in planks: p.data.materials.clear(); p.data.materials.append(after)
shoot(close_pos, close_tgt, 28, out_dir + '/03_after_close_v3.png')
print('[DECK] renders done')

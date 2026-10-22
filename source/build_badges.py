# Builds the cab engine badges engine425/515/585_decals in Blender: the same quads as the game's engine600_decals
# (corner positions and vmask uv1 dumped from fh16.i3d in GIANTS Editor), uv0 = uv2 = cells of our
# boxTruckBadges textures (make_badge_textures.py). Exported by export_badges.py.
# Run: blender.exe -b -P build_badges.py -- <out.blend>
import bpy, bmesh, sys
from mathutils import Vector

OUT = sys.argv[sys.argv.index('--') + 1:][0]
TEX_W, TEX_H = 512, 256
CELL_W, CELL_H = 101, 76
DIGIT_CELL = {c: i for i, c in enumerate('42518')}
FIRST_W = 95.5             # the game's first-digit quad is narrower: its texture rect is 95.5 px wide, not 101
EURO_RECT = (0, 100, 209, 146)
BADGES = {'engine425_decals': '425', 'engine515_decals': '515', 'engine585_decals': '585'}

# engine600_decals quads in game coordinates (shape local), corners: front-top, front-bottom, rear-top, rear-bottom
# ("front" = start of the text). Each corner: (x, y, z, vmask u, vmask v).
LEFT = [  # x > 0, text runs from z +0.017 back
    [(1.225559, 0.061525, 0.017009, 0.965821, 0.521432), (1.225559, 0.008688, 0.017009, 0.969305, 0.521399),
     (1.222607, 0.061525, -0.049678, 0.965851, 0.525815), (1.222608, 0.008688, -0.049678, 0.969328, 0.525792)],
    [(1.222607, 0.061525, -0.049678, 0.965851, 0.525815), (1.222608, 0.008688, -0.049678, 0.969328, 0.525792),
     (1.219293, 0.061525, -0.124582, 0.965877, 0.530759), (1.219293, 0.008688, -0.124582, 0.969353, 0.530739)],
    [(1.219293, 0.061525, -0.124582, 0.965877, 0.530759), (1.219293, 0.008688, -0.124582, 0.969353, 0.530739),
     (1.216047, 0.061525, -0.197931, 0.965902, 0.535600), (1.216047, 0.008688, -0.197931, 0.969380, 0.535585)],
    [(1.221503, -0.008110, -0.053395, 0.970432, 0.526036), (1.223163, -0.035580, -0.053395, 0.972248, 0.526018),
     (1.215149, -0.008494, -0.197231, 0.970511, 0.535538), (1.216809, -0.035963, -0.197231, 0.972328, 0.535528)],
]
RIGHT = [  # x < 0, text runs from z -0.200 forward
    [(-1.212685, 0.063537, -0.200116, 0.965758, 0.535754), (-1.215488, 0.006385, -0.200155, 0.969533, 0.535731),
     (-1.215527, 0.063629, -0.131006, 0.965731, 0.531192), (-1.218330, 0.006476, -0.131046, 0.969501, 0.531166)],
    [(-1.215527, 0.063629, -0.131006, 0.965731, 0.531192), (-1.218330, 0.006476, -0.131046, 0.969501, 0.531166),
     (-1.218593, 0.063728, -0.056422, 0.965698, 0.526270), (-1.221396, 0.006576, -0.056461, 0.969465, 0.526239)],
    [(-1.218593, 0.063728, -0.056422, 0.965698, 0.526270), (-1.221396, 0.006576, -0.056461, 0.969465, 0.526239),
     (-1.221704, 0.063828, 0.019233, 0.965657, 0.521289), (-1.224507, 0.006676, 0.019194, 0.969433, 0.521254)],
    [(-1.216118, -0.006085, -0.195977, 0.970356, 0.535451), (-1.216118, -0.037988, -0.195977, 0.972461, 0.535445),
     (-1.222540, -0.006085, -0.047755, 0.970299, 0.525659), (-1.222540, -0.037988, -0.047755, 0.972403, 0.525645)],
]

def rect_uv(x0, y0, x1, y1):
    """texture pixel rect -> (u0, u1, v_top, v_bottom); the game's v runs bottom-up (v = 1 - row / height)"""
    return x0 / TEX_W, x1 / TEX_W, 1 - y0 / TEX_H, 1 - y1 / TEX_H

def digit_uv(ch, first):
    i = DIGIT_CELL[ch]
    if first:
        cx = i * CELL_W + CELL_W / 2
        return rect_uv(cx - FIRST_W / 2, 0, cx + FIRST_W / 2, CELL_H)
    return rect_uv(i * CELL_W, 0, (i + 1) * CELL_W, CELL_H)

bpy.ops.wm.read_factory_settings(use_empty=True)
mat = bpy.data.materials.new('boxTruckBadges_mat')
for name, number in BADGES.items():
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv0 = bm.loops.layers.uv.new('uv0'); uv1 = bm.loops.layers.uv.new('uv1'); uv2 = bm.loops.layers.uv.new('uv2')
    for side, quads in (('L', LEFT), ('R', RIGHT)):
        for qi, quad in enumerate(quads):
            u0, u1, vt, vb = digit_uv(number[qi], qi == 0) if qi < 3 else rect_uv(*EURO_RECT)
            tex = [(u0, vt), (u0, vb), (u1, vt), (u1, vb)]
            verts = [bm.verts.new(Vector((c[0], -c[2], c[1]))) for c in quad]   # game (x, y, z) -> Blender (x, -z, y)
            order = [0, 1, 3, 2]                                                 # around the quad
            face = bm.faces.new([verts[k] for k in order])
            for loop, k in zip(face.loops, order):
                loop[uv0].uv = tex[k]; loop[uv2].uv = tex[k]; loop[uv1].uv = (quad[k][3], quad[k][4])
            face.normal_update()
            if (face.normal.x > 0) != (side == 'L'):   # face outwards
                face.normal_flip()
    bm.to_mesh(me); bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    ob['i3D_collision'] = False
    ob['i3D_castsShadows'] = False
    bpy.context.scene.collection.objects.link(ob)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print('BUILT', list(BADGES))

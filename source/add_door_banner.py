# Adds the rear door PRO EDITION banner to boxTruck.i3d (user, 2026-10-24; approved preview previews\rear_banner_v2_preview.png).
# No new geometry: each door gets an instance of the ProEdition curtain decal quad (shapeId of curtainLeftProEdition,
# whole banner texture on it), turned to face backwards and scaled to BANNER_W, with its own texture that shows only
# that door's half (make_door_banner_textures.py). Children of rearDoorLeft/Right, appended LAST so no sibling index
# or i3dMapping moves; hidden by default (the shop's ProEdition curtain design shows them, boxTruck.xml design8).
# Measured in GIANTS Editor 10 (bt\v17banner\measure*.lua), body coordinates:
#   curtain quad: x 1.2975, y 2.3445..3.5915, z 1.185 (u = 0) .. -4.885 (u = 1), facing +x
#   door faces z -5.3630, y 1.7121..4.1114; left face ends x +0.0022, right x -0.0058 -> seam centre x -0.0018
# Usage: python -I add_door_banner.py <boxTruck.i3d> [visible]
import re
import sys

I3D = sys.argv[1]
VISIBLE = len(sys.argv) > 2 and sys.argv[2] == 'visible'

SRC_X, SRC_Y0, SRC_Y1, SRC_Z0, SRC_Z1 = 1.2975, 2.3445, 3.5915, 1.185, -4.885
SRC_W, SRC_H = SRC_Z0 - SRC_Z1, SRC_Y1 - SRC_Y0
DOOR_FACE_Z, DOOR_TOP_Y, DOOR_BOTTOM_Y = -5.3630, 4.1114, 1.7121
SEAM_X = -0.0018
BANNER_W = 2.144                     # 85 % of the 2.523 m between the hinges (make_door_banner_textures.py)
TOP_SHARE = 0.10                     # gap above the banner / door height
OFFSET = 0.0015                      # off the door face, as the curtain decal sits off the cloth
HINGES = {'Left': (1.2614, 0.0, -5.35), 'Right': (-1.2614, 0.0, -5.35)}

s = BANNER_W / SRC_W
h = SRC_H * s
top = DOOR_TOP_Y - (DOOR_TOP_Y - DOOR_BOTTOM_Y) * TOP_SHARE
target = (SEAM_X, top - h / 2, DOOR_FACE_Z - OFFSET)
src_c = (SRC_X, (SRC_Y0 + SRC_Y1) / 2, (SRC_Z0 + SRC_Z1) / 2)
# rotation 0 90 0: (x, y, z) -> (z, y, -x): the quad's +x normal faces -z (backwards), its u (towards -z) runs to -x,
# i.e. left to right for someone standing behind the truck
rot = (src_c[2] * s, src_c[1] * s, -src_c[0] * s)
body_t = tuple(target[k] - rot[k] for k in range(3))

text = open(I3D, encoding='utf-8').read()
if 'doorLeftProEdition' in text:
    sys.exit('already has the door banner')

src_shape = re.search(r'<Shape name="curtainLeftProEdition"[^>]*shapeId="(\d+)"', text).group(1)
src_mat = re.search(r'<Material name="proEditionDecal" materialId="(\d+)".*?</Material>', text, re.S)
next_file = max(int(v) for v in re.findall(r'fileId="(\d+)"', text)) + 1
next_mat = max(int(v) for v in re.findall(r'materialId="(\d+)"', text)) + 1
next_node = max(int(v) for v in re.findall(r'nodeId="(\d+)"', text)) + 1

files, mats = [], []
ids = {}
for k, side in enumerate(('Left', 'Right')):
    fid, mid = next_file + k, next_mat + k
    files.append('    <File fileId="%d" filename="boxTruckProEditionDoor%s_diffuse.dds"/>\n' % (fid, side))
    m = src_mat.group(0)
    m = m.replace('name="proEditionDecal" materialId="%s"' % src_mat.group(1), 'name="proEditionDoor%sDecal" materialId="%d"' % (side, mid))
    m = re.sub(r'<Texture fileId="\d+"', '<Texture fileId="%d"' % fid, m, count=1)
    mats.append('    ' + m + '\n')
    ids[side] = (mid, next_node + k)

# Files: before </Files>; Materials: before </Materials>
text = text.replace('  </Files>', ''.join(files) + '  </Files>', 1)
text = text.replace('  </Materials>', ''.join(mats) + '  </Materials>', 1)

for side, (hx, hy, hz) in HINGES.items():
    mid, nid = ids[side]
    local = (body_t[0] - hx, body_t[1] - hy, body_t[2] - hz)
    node = ('<Shape name="door%sProEdition" translation="%.6f %.6f %.6f" rotation="0 90 0" scale="%.6f %.6f %.6f" '
            'shapeId="%s" clipDistance="150" nodeId="%d" castsShadows="false" receiveShadows="true" decalLayer="2" '
            'materialIds="%d"%s/>' % (side, local[0], local[1], local[2], s, s, s, src_shape, nid, mid,
                                      '' if VISIBLE else ' visibility="false"'))
    # last child of rearDoor<side>: right before its closing tag
    m = re.search(r'(<TransformGroup name="rearDoor%s"[^>]*>)(.*?)(\n(\s*)</TransformGroup>)' % side, text, re.S)
    # the door group holds nested groups (visuals); find ITS closing tag by indentation
    start = m.start()
    indent = re.match(r'\s*', text[text.rfind('\n', 0, start) + 1:start]).group(0)
    close = text.index('\n' + indent + '</TransformGroup>', start)
    text = text[:close] + '\n' + indent + '  ' + node + text[close:]
    print('door%sProEdition local t %.4f %.4f %.4f' % (side, *local))

open(I3D, 'w', encoding='utf-8').write(text)
print('scale %.6f, banner %.3f x %.3f m, centre body %.4f %.4f %.4f, shapeId %s, files %d-%d, materials %d-%d'
      % (s, BANNER_W, h, *target, src_shape, next_file, next_file + 1, next_mat, next_mat + 1))

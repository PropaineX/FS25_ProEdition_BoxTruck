# Exports rear_vN.blend (build_rear.py) to an i3d and gives every material the Krone ProfiLiner's own definition
# (shader, $data textures, parameters) copied from the game's profiLiner.i3d (by material name).
# Run: blender -b <rear.blend> -P export_rear.py -- <out.i3d> <game profiLiner.i3d>
import bpy, sys, copy, xml.etree.ElementTree as ET
OUT, SRC = sys.argv[sys.argv.index('--') + 1:][:2]
import addon_utils
addon_utils.enable('io_export_i3d', default_set=True)
from io_export_i3d import i3d_export
from io_export_i3d.dcc import dccBlender as d
import io_export_i3d.dcc as dccpkg
_vis = lambda n: bpy.data.objects[n].visible_get()
d.isNodeVisible = _vis; dccpkg.isNodeVisible = _vis
d.UISetAttrBool('i3D_exportUseSoftwareFileName', False)
d.UISetAttrBool('i3D_binaryFiles', True)
d.UISetAttrString('i3D_exportFileLocation', OUT)
i3d_export.I3DExportAll()

src = ET.parse(SRC).getroot()
sfiles = {f.get('fileId'): f.get('filename') for f in src.iter('File')}
smats = {m.get('name'): m for m in src.iter('Material')}
tree = ET.parse(OUT); root = tree.getroot()
files = root.find('Files')
if files is None:
    files = ET.Element('Files'); root.insert(list(root).index(root.find('Materials')), files)
for f in list(files): files.remove(f)
ids = {}
def fid(name):
    if name not in ids:
        ids[name] = str(len(ids) + 1); ET.SubElement(files, 'File', fileId=ids[name], filename=name)
    return ids[name]
for m in root.find('Materials'):
    s = smats[m.get('name')]
    for k in list(m.attrib):
        if k not in ('name', 'materialId'): del m.attrib[k]
    for c in list(m): m.remove(c)
    for k, v in s.attrib.items():
        if k not in ('name', 'materialId'): m.set(k, v)
    for c in s:
        c2 = copy.deepcopy(c)
        if c2.get('fileId'): c2.set('fileId', fid(sfiles[c.get('fileId')]))
        m.append(c2)
    if m.get('customShaderId'): m.set('customShaderId', fid(sfiles[s.get('customShaderId')]))
for sh in root.iter('Shape'):                       # decal pieces (Krone logos): drawn on the surface, no shadow
    if sh.get('name', '').endswith('Logos'):
        sh.set('decalLayer', '1'); sh.set('castsShadows', 'false')
tree.write(OUT, xml_declaration=True, encoding='iso-8859-1')
print('EXPORTED', OUT, len(ids), 'files')

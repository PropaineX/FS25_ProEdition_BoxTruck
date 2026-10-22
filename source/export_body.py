# Exports the body from a build_body.py .blend to an i3d (stand-ins, camera and renders left out).
# Run: blender.exe -b <body.blend> -P export_body.py -- <out.i3d> [ascii]
# The node structure (root "boxBody") comes from build_body.py.
import bpy, sys

args = sys.argv[sys.argv.index('--') + 1:]
OUT = args[0]
BINARY = not (len(args) > 1 and args[1] == 'ascii')

for ob in list(bpy.data.objects):
    if ob.name.startswith('standIn_') or ob.name == 'camTarget' or ob.type == 'CAMERA':
        bpy.data.objects.remove(ob)

# the exporter reads colours from the Principled BSDF node, build_body.py only sets the viewport colour
for m in bpy.data.materials:
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = m.diffuse_color

import addon_utils
addon_utils.enable('io_export_i3d', default_set=True)
from io_export_i3d import i3d_export
from io_export_i3d.dcc import dccBlender as d
import io_export_i3d.dcc as dccpkg
from io_export_i3d.util import logUtil

# background mode has no 3D view; the exporter's visibility check needs one
_vis = lambda n: bpy.data.objects[n].visible_get()
d.isNodeVisible = _vis
dccpkg.isNodeVisible = _vis

d.UISetAttrBool('i3D_exportVerbose', True)
d.UISetAttrBool('i3D_exportUseSoftwareFileName', False)
d.UISetAttrBool('i3D_binaryFiles', BINARY)
d.UISetAttrString('i3D_exportFileLocation', OUT)
i3d_export.I3DExportAll()
for t, msg in logUtil.ActionLog.message:
    print('LOG', t, msg)

# the exporter writes emissiveColor 1 1 1 (fully self-lit, flat white in GE); no glow wanted
i3d = OUT if OUT.endswith('.i3d') else OUT + '.i3d'
txt = open(i3d, encoding='iso-8859-1').read().replace('emissiveColor="1 1 1 1"', 'emissiveColor="0 0 0 1"')
open(i3d, 'w', encoding='iso-8859-1').write(txt)

# Plain Blender materials render with random dark parts in the game (in-game test 2026-10-22: one rear door dark).
# Replace them with the game's vehicleShader set-up, as the FH16's own materials use it: white_diffuse +
# default_normal + default_vmask, detail maps of a material template, linear colorScale.
# The white panels use exactly the "White (body)" paint option of the truck (calibratedPaint, 0.90 0.90 0.88).
import xml.etree.ElementTree as ET
D = '$data/shared/detailLibrary/'
TEMPLATES = {
    'calibratedPaint': (D + 'calibrated/calibratedPaint_diffuse.png', D + 'calibrated/calibratedPaint_normal.png',
                        D + 'calibrated/calibratedPaint_specular.png', {'clearCoatIntensity': '0.1000', 'clearCoatSmoothness': '0.2000', 'smoothnessScale': '0.8500'}),
    'metalPainted': (D + 'nonMetallic/metal/metalPainted_diffuse.png', D + 'flat_normal.png',
                     D + 'nonMetallic/metal/metalPainted_specular.png', {}),
    'plasticPainted': (D + 'nonMetallic/plastic/plasticPainted_diffuse.png', D + 'flat_normal.png',
                       D + 'nonMetallic/plastic/plasticPainted_specular.png', {}),
    'wood2Oak': (D + 'nonMetallic/wood/wood2Oak_diffuse.png', D + 'nonMetallic/wood/wood2_normal.png',
                 D + 'nonMetallic/wood/wood2_specular.png', {}),
    'metalGalvanized': (D + 'metallic/metalGalvanized_diffuse.png', D + 'metallic/metalGalvanized_normal.png',
                        D + 'metallic/metalGalvanized_specular.png', {}),
}
GAME_MATERIALS = {  # Blender material name -> (template, colorScale)
    'curtain':   ('calibratedPaint', '0.90 0.90 0.88'),
    'door':      ('calibratedPaint', '0.90 0.90 0.88'),
    'alu':       ('metalPainted',    '0.34 0.35 0.36'),
    'steelDark': ('metalPainted',    '0.02 0.02 0.02'),
    'strap':     ('plasticPainted',  '0.015 0.015 0.015'),
    'floorWood': ('wood2Oak',        '0.22 0.15 0.11'),   # v7: dark load floor
    'post':      ('plasticPainted',  '0.30 0.31 0.32'),   # sliding posts: matte, no glare
    'antiSlip':  ('plasticPainted',  '0.05 0.05 0.045'),
    'boardWood': ('wood2Oak',        '0.80 0.62 0.45'),
    'kickPlate': ('calibratedPaint', '0.20 0.012 0.012'),
    'galvanized': ('metalGalvanized', '1 1 1'),
    'curtainCloth': ('calibratedPaint', '0.90 0.90 0.88'),
}
# materials with their own diffuse / normal map (instead of white_diffuse / default_normal)
OWN_MAPS = {'curtainCloth': ('boxTruckCurtain_diffuse.dds', 'boxTruckCurtain_normal.dds')}
tree = ET.parse(i3d)
root_el = tree.getroot()
files = root_el.find('Files')
if files is None:
    files = ET.Element('Files')
    root_el.insert(list(root_el).index(root_el.find('Materials')), files)
next_id = max([int(f.get('fileId')) for f in files] + [0]) + 1
file_ids = {}
def fid(path):
    global next_id
    if path not in file_ids:
        ET.SubElement(files, 'File', fileId=str(next_id), filename=path)
        file_ids[path] = str(next_id); next_id += 1
    return file_ids[path]
for m in root_el.find('Materials'):
    name = m.get('name')
    if name not in GAME_MATERIALS:
        continue
    tpl, color = GAME_MATERIALS[name]
    dd, dn, ds, extra = TEMPLATES[tpl]
    for k in list(m.attrib):
        if k not in ('name', 'materialId'):
            del m.attrib[k]
    for child in list(m):
        m.remove(child)
    m.set('customShaderId', fid('$data/shaders/vehicleShader.xml'))
    params = {'colorScale': color, 'lightIds0': '1 1 1 1'}
    params.update(extra)
    for k in sorted(params):
        ET.SubElement(m, 'CustomParameter', name=k, value=params[k])
    ET.SubElement(m, 'Custommap', name='detailDiffuse', fileId=fid(dd))
    ET.SubElement(m, 'Custommap', name='detailNormal', fileId=fid(dn))
    ET.SubElement(m, 'Custommap', name='detailSpecular', fileId=fid(ds))
    tex, nrm = OWN_MAPS.get(name, ('$data/shared/white_diffuse.png', '$data/shared/default_normal.png'))
    ET.SubElement(m, 'Texture', fileId=fid(tex))
    ET.SubElement(m, 'Normalmap', fileId=fid(nrm))
    ET.SubElement(m, 'Glossmap', fileId=fid('$data/shared/default_vmask.png'))
    print('MATERIAL', name, '->', tpl, color)
# alpha-blended vehicleShader decals like the Krone ProfiLiner's paintjob decals: our ProEdition banner and door
# stickers, and the curtain designs that use the ProfiLiner's own ad sheets from the game
PL = '$data/vehicles/krone/profiLiner/'
DECALS = {'proEditionDecal': 'boxTruckProEditionCurtain_diffuse.dds', 'stickers': 'boxTruckStickers_diffuse.dds',
          'designKrone': PL + 'profiLinerPaintjob1_diffuse.png', 'designFSL': PL + 'profiLinerPaintjob2_diffuse.png',
          'designGIANTS': PL + 'profiLinerPaintjob3_diffuse.png'}
for m in root_el.find('Materials'):
    if m.get('name') not in DECALS:
        continue
    for k in list(m.attrib):
        if k not in ('name', 'materialId'):
            del m.attrib[k]
    for child in list(m):
        m.remove(child)
    m.set('customShaderId', fid('$data/shaders/vehicleShader.xml')); m.set('customShaderVariation', 'vmaskUV2')
    m.set('alphaBlending', 'true')
    ET.SubElement(m, 'CustomParameter', name='alphaBlendingClipThreshold', value='1')
    ET.SubElement(m, 'CustomParameter', name='lightIds0', value='1 1 1 1')
    ET.SubElement(m, 'Custommap', name='detailDiffuse', fileId=fid(D + 'nonMetallic/plastic/plasticPainted_diffuse.png'))
    ET.SubElement(m, 'Custommap', name='detailNormal', fileId=fid(D + 'flat_normal.png'))
    ET.SubElement(m, 'Custommap', name='detailSpecular', fileId=fid(D + 'nonMetallic/plastic/plasticPainted_specular.png'))
    ET.SubElement(m, 'Texture', fileId=fid(DECALS[m.get('name')]))
    ET.SubElement(m, 'Normalmap', fileId=fid('$data/shared/default_normal.png'))
    ET.SubElement(m, 'Glossmap', fileId=fid('$data/shared/default_vmask.png'))
    print('MATERIAL', m.get('name'), '-> alpha decal', DECALS[m.get('name')])
for n in root_el.iter():
    nm = n.get('name', '')
    if n.tag == 'Shape' and (nm.endswith('ProEdition') or 'Design' in nm):
        n.set('decalLayer', '2'); n.set('visibility', 'false')   # shown by the curtain design option
    if n.tag == 'Shape' and nm == 'doorRightStickers':
        n.set('decalLayer', '1')
    if nm in ('curtainLeftOpen', 'curtainRightOpen'):
        n.set('visibility', 'false')                             # the gathered curtain shows only while open
tree.write(i3d, xml_declaration=True, encoding='iso-8859-1')

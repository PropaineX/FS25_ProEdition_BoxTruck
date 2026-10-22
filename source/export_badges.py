# Exports the badges .blend from build_badges.py and gives them the FH16 badge material (vehicleShader
# vmaskUV2_normalUV3, chrome detail maps, the FH16 vmask) with our badge textures.
# Run: blender.exe -b <badges.blend> -P export_badges.py -- <out.i3d>
import bpy, sys, xml.etree.ElementTree as ET
OUT = sys.argv[sys.argv.index('--') + 1:][0]

import addon_utils
addon_utils.enable('io_export_i3d', default_set=True)
from io_export_i3d import i3d_export
from io_export_i3d.dcc import dccBlender as d
import io_export_i3d.dcc as dccpkg
_vis = lambda n: bpy.data.objects[n].visible_get()   # background mode has no 3D view
d.isNodeVisible = _vis; dccpkg.isNodeVisible = _vis
d.UISetAttrBool('i3D_exportUseSoftwareFileName', False)
d.UISetAttrBool('i3D_binaryFiles', True)
d.UISetAttrString('i3D_exportFileLocation', OUT)
i3d_export.I3DExportAll()

i3d = OUT if OUT.endswith('.i3d') else OUT + '.i3d'
tree = ET.parse(i3d); root = tree.getroot()
files = root.find('Files')
if files is None:
    files = ET.Element('Files'); root.insert(list(root).index(root.find('Materials')), files)
for f in list(files): files.remove(f)
FILES = ['$data/shaders/vehicleShader.xml', 'boxTruckBadges_diffuse.dds', 'boxTruckBadges_normal.dds',
         '$data/vehicles/volvo/fh16/fh16B_vmask.png', '$data/shared/detailLibrary/metallic/clear_diffuse.png',
         '$data/shared/detailLibrary/flat_normal.png', '$data/shared/detailLibrary/metallic/clear_specular.png']
for i, f in enumerate(FILES, 1):
    ET.SubElement(files, 'File', fileId=str(i), filename=f)
# exactly like the game's fh16Decals_chrome_mat (no alphaBlending: the decal alpha cuts the letters out as it does there)
for m in root.find('Materials'):
    for k in list(m.attrib):
        if k not in ('name', 'materialId'): del m.attrib[k]
    for c in list(m): m.remove(c)
    m.set('customShaderId', '1'); m.set('customShaderVariation', 'vmaskUV2_normalUV3')
    ET.SubElement(m, 'Texture', fileId='2'); ET.SubElement(m, 'Normalmap', fileId='3'); ET.SubElement(m, 'Glossmap', fileId='4')
    ET.SubElement(m, 'Custommap', name='detailSpecular', fileId='7')
    ET.SubElement(m, 'Custommap', name='detailNormal', fileId='6')
    ET.SubElement(m, 'Custommap', name='detailDiffuse', fileId='5')
tree.write(i3d, xml_declaration=True, encoding='iso-8859-1')
print('EXPORTED', i3d)

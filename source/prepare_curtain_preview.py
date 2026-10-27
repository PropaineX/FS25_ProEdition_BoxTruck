"""Prepare disposable GIANTS Editor preview assets from current runtime files."""
from pathlib import Path
import sys, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
straps='--straps' in sys.argv
folder='curtain_straps_motion_v2' if straps else 'curtain_shape_motion'
name='straps_v2.i3d' if straps else 'binary.i3d'
out=ROOT/'previews'/folder
out.mkdir(exist_ok=True)
tree=ET.parse(ROOT/'gatheredCurtains.i3d')
for entry in tree.getroot().find('Files'):
    filename=entry.get('filename')
    if not filename.startswith('$'):
        entry.set('filename',(ROOT/filename).as_posix())
shapes=name+'.shapes'
tree.getroot().find('Shapes').set('externalShapesFile',shapes)
(out/shapes).write_bytes((ROOT/'gatheredCurtains.i3d.shapes').read_bytes())
ET.SubElement(tree.getroot().find('Scene'),'Light',name='previewSun',type='directional',rotation='-35 -35 0',color='1 1 1',emitDiffuse='true',emitSpecular='true',nodeId='500')
tree.write(out/name,encoding='utf-8',xml_declaration=True)
print('Prepared',folder+'/'+name)

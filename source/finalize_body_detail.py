"""Validate and optionally install the reviewed detail build. Preserve a local backup.
python source/finalize_body_detail.py [--install]
"""
from pathlib import Path
import shutil, sys, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
STAGE=ROOT/'previews/detail_v1/work'
BASE=ROOT/'previews/detail_v1/before'
BASE.mkdir(exist_ok=True)
for name in ('boxTruck.i3d','boxTruck.i3d.shapes','boxTruckCurtain_diffuse.dds','boxTruckCurtain_normal.dds'):
    if not (BASE/name).exists(): shutil.copy2(ROOT/name,BASE/name)
original=ET.parse(BASE/'boxTruck.i3d').getroot()
tree=ET.parse(STAGE/'boxTruck.i3d'); upgraded=tree.getroot()
node_tags={'TransformGroup','Shape','Light','Camera','ReferenceNode'}
def paths(scene):
    out={}
    def visit(n,path):
        out[path]=n
        for i,c in enumerate(c for c in n if c.tag in node_tags): visit(c,path+(i,))
    visit(scene,())
    return out
old,new=paths(original.find('Scene')),paths(upgraded.find('Scene'))
hidden={'curtainLeftCloth','curtainRightCloth','curtainLeftBuckles','curtainRightBuckles'}
for path,node in old.items():
    other=new[path]
    assert other.tag==node.tag and other.get('name')==node.get('name'),f'Node mapping shifted: {path}'
    # Restore any editor-only preview changes to the original vehicle nodes.
    for key in ('visibility','translation','rotation','scale'):
        if key in node.attrib: other.set(key,node.get(key))
        else: other.attrib.pop(key,None)
    if node.get('name') in hidden: other.set('visibility','false')
    for key in ('compoundChild','collisionFilterGroup','collisionFilterMask','density','dynamic','kinematic'):
        assert other.get(key)==node.get(key),(path,key)
details=[n for n in upgraded.iter('Shape') if n.get('name','').startswith('bodyDetail')]
assert len(details)==10,len(details)
parents={c:n for n in upgraded.iter() for c in n}
for n in details:
    name=n.get('name')
    parent='boxBody' if 'Static' in name else ('rearDoor'+('Left' if 'Left' in name else 'Right') if 'Door' in name else 'curtain'+('Left' if 'Left' in name else 'Right')+'Closed')
    assert parents[n].get('name')==parent,(name,parent)
    assert n.get('compoundChild') is None,name
for n in upgraded.iter():
    assert not n.get('name','').startswith(('bodyDetailStudio','bodyDetailPreview','visualWheel')), 'Preview node in saved asset'
files={f.get('fileId'):f.get('filename') for f in upgraded.find('Files')}
for m in upgraded.find('Materials'):
    for c in m:
        if c.get('fileId'): assert c.get('fileId') in files,(m.get('name'),c.attrib)
for filename in files.values():
    if not filename.startswith('$'): assert (STAGE/filename).is_file(),filename
ET.indent(tree,space='  ')
tree.write(STAGE/'boxTruck.i3d',encoding='iso-8859-1',xml_declaration=True)
print(f'Validated {len(old)} original scene nodes, 10 new visual meshes, intact collision flags and texture references.')
if '--install' in sys.argv:
    names=['boxTruck.i3d','boxTruck.i3d.shapes','boxTruckCurtain_diffuse.dds','boxTruckCurtain_normal.dds',
           'boxTruckFabric_detail_diffuse.dds','boxTruckFabric_detail_normal.dds','boxTruckFabric_detail_specular.dds']
    for name in names: shutil.copy2(STAGE/name,ROOT/name)
    print('Installed 7 reviewed asset files. Original assets preserved in',BASE)

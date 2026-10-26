"""Give existing closed inner liners a white texture without shifting nodes."""
from pathlib import Path
import copy,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
p=ROOT/'boxTruck.i3d'; raw=p.read_text(encoding='iso-8859-1'); root=ET.fromstring(raw)
if root.find("Materials/Material[@name='boxTruckWhiteInnerLining']") is None:
    m=copy.deepcopy(root.find("Materials/Material[@name='curtainCloth']"))
    mid=str(max(int(n.get('materialId')) for n in root.find('Materials'))+1)
    m.set('name','boxTruckWhiteInnerLining'); m.set('materialId',mid)
    m.find('Texture').set('fileId','2'); m.find('Normalmap').set('fileId','31')
    m.find("CustomParameter[@name='colorScale']").set('value','1 1 1')
    backup=ROOT/'previews/gathered_integration/before'; backup.mkdir(exist_ok=True)
    if not (backup/p.name).exists(): (backup/p.name).write_text(raw,encoding='iso-8859-1')
    ET.indent(m,space='  ')
    raw=raw.replace('  </Materials>','    '+ET.tostring(m,encoding='unicode')+'\n  </Materials>')
    raw,count=re.subn(r'(<Shape name="curtain(?:Left|Right)InnerLining"[^>]*materialIds=")[^"]+',lambda match:match.group(1)+mid,raw)
    assert count==2,count
    p.write_text(raw,encoding='iso-8859-1')
    print('Both closed inner liners now use white texture, material',mid)

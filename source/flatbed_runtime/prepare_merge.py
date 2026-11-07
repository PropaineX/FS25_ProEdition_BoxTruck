"""Prepare a private Editor scratch scene; never point its save at production shapes."""
from pathlib import Path
import xml.etree.ElementTree as ET
import shutil,hashlib,json
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'source/flatbed_runtime/build';OUT.mkdir(exist_ok=True)
r=ET.parse(ROOT/'boxTruck.i3d')
for f in r.getroot().find('Files'):
 name=f.get('filename')
 if name and not name.startswith('$') and not Path(name).is_absolute():f.set('filename',(ROOT/name).as_posix())
r.getroot().find('Shapes').set('externalShapesFile','flatbedTruck_work.i3d.shapes')
r.write(OUT/'flatbedTruck_work.i3d',encoding='iso-8859-1',xml_declaration=True)
shutil.copyfile(ROOT/'boxTruck.i3d.shapes',OUT/'flatbedTruck_work.i3d.shapes')
(OUT/'boxtruck_before_hashes.json').write_text(json.dumps({n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['boxTruck.xml','boxTruck.i3d','boxTruck.i3d.shapes','scripts/BoxTruckBody.lua']},indent=2))
print('Private merge scratch prepared; production files not changed')

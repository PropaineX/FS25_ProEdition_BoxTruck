"""Build a runtime-only testing ZIP and verify every member against project assets."""
from pathlib import Path
import hashlib, json, zipfile, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
version=ET.parse(ROOT/'modDesc.xml').getroot().findtext('version')
out=ROOT.parent.parent/'Testing_local'
out.mkdir(parents=True,exist_ok=True)
files=[ROOT/n for n in ('modDesc.xml','boxTruck.xml','boxTruck.i3d','boxTruck.i3d.shapes','gatheredCurtains.i3d','gatheredCurtains.i3d.shapes')]
files+=sorted(ROOT.glob('*.dds'))
files+=sorted((ROOT/'scripts').rglob('*.lua'))
names={p.relative_to(ROOT).as_posix() for p in files}
for name in ('modDesc.xml','boxTruck.xml','boxTruck.i3d','gatheredCurtains.i3d'):
    root=ET.parse(ROOT/name).getroot()
    for e in root.iter():
        filename=e.get('filename')
        if filename and not filename.startswith('$'):
            assert filename.replace('\\','/') in names,(name,filename)
        if e.get('externalShapesFile'):
            assert e.get('externalShapesFile') in names,(name,e.get('externalShapesFile'))
assert all('detail_v1' not in n and not n.startswith(('source/','previews/')) for n in names)
dest=out/'FS25_BoxTruck_ProEdition.zip'
tmp=dest.with_suffix('.zip.tmp')
with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for f in files:z.write(f,f.relative_to(ROOT).as_posix())
with zipfile.ZipFile(tmp) as z:
    assert z.testzip() is None
    assert set(z.namelist())==names
    for f in files:assert z.read(f.relative_to(ROOT).as_posix())==f.read_bytes(),f
tmp.replace(dest)
result={'version':version,'filename':dest.name,'files':len(files),'bytes':dest.stat().st_size,
        'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'members':sorted(names)}
(out/'FS25_BoxTruck_ProEdition.manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='members'},indent=2))

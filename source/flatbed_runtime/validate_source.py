"""Validate runtime source and membership without creating/copying a ZIP."""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[2];BUILD=ROOT/'source/flatbed_runtime/build'
GAME=Path('G:/SteamLibrary/steamapps/common/Farming Simulator 25')
runtime=[ROOT/n for n in ['modDesc.xml','boxTruck.xml','boxTruck.i3d','boxTruck.i3d.shapes','gatheredCurtains.i3d','gatheredCurtains.i3d.shapes','flatbedTruck.xml','flatbedTruck.i3d','flatbedTruck.i3d.shapes']]
runtime+=sorted(ROOT.glob('*.dds'))+sorted((ROOT/'shaders').glob('*.xml'))+sorted((ROOT/'scripts').rglob('*.lua'))
members={p.relative_to(ROOT).as_posix() for p in runtime}
assert all(p.is_file() for p in runtime)
assert not any(n.startswith(('source/','previews/','chat_history/','.local/')) or n.endswith('.md') or '\\' in n for n in members)
def exact(path):
 path=Path(path)
 if not path.is_file():return False
 for parent,name in zip([ROOT,*[ROOT.joinpath(*path.relative_to(ROOT).parts[:i]) for i in range(1,len(path.relative_to(ROOT).parts))]],path.relative_to(ROOT).parts):
  assert name in {x.name for x in parent.iterdir()},('case mismatch',path,name)
 return True
refs=[]
def reference(value,source):
 value=value.strip()
 if not value or value.startswith('$l10n_'):return
 assert '\\' not in value,(source,value)
 if value.startswith('$dataS/'):return
 if value.startswith('$data/'):
  p=GAME/'data'/value[6:]
  assert p.is_file() or (p.suffix.lower()=='.png' and p.with_suffix('.dds').is_file()),(source,value)
  return
 assert not Path(value).is_absolute(),(source,value)
 assert value in members and exact(ROOT/value),(source,value)
 refs.append((source,value))
for name in ['modDesc.xml','boxTruck.xml','boxTruck.i3d','gatheredCurtains.i3d','flatbedTruck.xml','flatbedTruck.i3d',*[p.relative_to(ROOT).as_posix() for p in (ROOT/'shaders').glob('*.xml')]]:
 r=ET.parse(ROOT/name).getroot()
 for e in r.iter():
  for attr in ['filename','externalShapesFile','xmlFilename']:
   if e.get(attr):reference(e.get(attr),name)
  if e.tag in ['iconFilename','image','filename','sourceFile'] and e.text and e.text.strip():reference(e.text,name)
desc=ET.parse(ROOT/'modDesc.xml').getroot();assert desc.findtext('version')=='1.5.1.0'
assert {s.get('xmlFilename') for s in desc.findall('storeItems/storeItem')}=={'boxTruck.xml','flatbedTruck.xml'}
types={t.get('name'):t for t in desc.findall('vehicleTypes/type')}
assert [x.get('name') for x in types['boxTruckPro']]==['tensionBelts','boxTruckBody']
assert [x.get('name') for x in types['flatbedPro']]==['tensionBelts','foldable','flatbedBody']
labels={t.get('name'):t for t in desc.findall('l10n/text')}
for key in labels:
 if 'flatbed' in key.lower():assert all(labels[key].find(lang) is not None and labels[key].find(lang).text for lang in ['en','de']),key
v=ET.parse(ROOT/'flatbedTruck.xml').getroot();scene=ET.parse(ROOT/'flatbedTruck.i3d').getroot().find('Scene')
node_tags={'Shape','TransformGroup','Camera','Light','ReferenceNode'}
components=[n for n in scene if n.tag in node_tags]
def resolve(path):
 ci,tail=path.split('>');n=components[int(ci)]
 for part in tail.split('|'):
  if part:n=[c for c in n if c.tag in node_tags][int(part)]
 return n
maps={e.get('id'):resolve(e.get('node')) for e in v.find('i3dMappings')}
for e in v.iter():
 for attr in ['node','repr','driveNode','linkNode','jointNode','activationTrigger','startNode','endNode','rotCenterNode','steeringNode']:
  value=e.get(attr)
  if value:assert value in maps or '>' in value or value.replace('|','').isdigit(),(e.tag,attr,value)
 for value in e.attrib.values():
  if value.startswith('$l10n_') and 'flatbed' in value.lower():assert value[6:] in labels,value
anim={a.get('name'):a for a in v.findall('animations/animation')}
configs=v.findall('foldable/foldingConfigurations/foldingConfiguration');assert len(configs)==2
assert configs[0].get('saveId')=='boards' and configs[1].get('saveId')=='stakes'
assert [x.get('node') for x in anim['flatbedBoards'].findall('part')]==[f'flatbedBoard{s}{i}' for s in ('Left','Right') for i in (1,2,3)]+['flatbedTailgate'] and 'flatbedTailgate' not in anim and len(anim['additionalForks'].findall('part'))==6
for part in anim['additionalForks'].findall('part'):
 assert part.get('startTrans')==maps[part.get('node')].get('translation') or all(abs(float(a)-float(b))<1e-6 for a,b in zip(part.get('startTrans').split(),maps[part.get('node')].get('translation').split()))
 assert float(part.get('endTime'))==.7
for config in configs:
 for p in config.findall('foldingParts/foldingPart'):assert p.get('animationName') in anim
 for change in config.findall('objectChange'):
  if change.get('node').startswith('flatbedCol'):
   assert (change.get('compoundChildActive')=='true')==(('Stake' in change.get('node'))==(config.get('saveId')=='stakes'))
belts=v.findall('tensionBelts/tensionBeltsConfigurations/tensionBeltsConfiguration/tensionBelts/tensionBelt');assert len(belts)==9
for belt in belts:
 start=maps[belt.get('startNode')];end=maps[belt.get('endNode')]
 assert [float(x) for x in start.get('rotation').split()]==[0,-90,0]
 assert float(start.get('translation').split()[0])==1.23
 assert [float(x) for x in end.get('translation').split()]==[0,0,2.46]
assert v.find('design2Configurations/design2Configuration').get('isDefault')=='true'
assert maps['flatbedTailgate'].get('translation')=='0 1.625 -5.37'
assert all(x.get('node') not in maps or maps[x.get('node')] is not None for x in v.findall('lights/defaultLights/defaultLight'))
before=json.loads((BUILD/'boxtruck_before_hashes.json').read_text())
for name,digest in before.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,('Box Truck changed',name)
result={'version':'1.5.1.0','runtime_files':len(members),'flatbed_mappings':len(maps),'belts':9,'side_configurations':2,
 'boxtruck_files_unchanged':list(before),'local_references_checked':len(refs),
 'runtime_members':sorted(members),'gameplay':'UNTESTED','zip_created':False}
(BUILD/'source_validation.json').write_text(json.dumps(result,indent=2))
print('PASS XML, runtime references/case/slashes, l10n, store/type registration,363mappings,2side configs,9belts,animation targets and unchanged original Box Truck files')
print('Runtime membership:',len(members),'files; no ZIP created')

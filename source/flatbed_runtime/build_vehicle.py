"""Assemble the separate flatbed runtime files after the GIANTS Editor merge."""
from pathlib import Path
import xml.etree.ElementTree as ET
import copy,json,shutil,re
ROOT=Path(__file__).resolve().parents[2];BUILD=ROOT/'source/flatbed_runtime/build'
TAGS={'TransformGroup','Shape','Light','Camera','ReferenceNode'}
def chains(path):
 scene=ET.parse(path).getroot().find('Scene');by_path={};by_chain={};by_name={}
 def walk(n,path,chain):
  by_path[path]=chain;by_chain[chain]=path;by_name.setdefault(n.get('name'),[]).append(path)
  seen={}
  for i,c in enumerate(x for x in n if x.tag in TAGS):
   name=c.get('name');index=seen.get(name,0);seen[name]=index+1
   walk(c,path+('' if path.endswith('>') else '|')+str(i),chain+((name,index),))
 for i,n in enumerate(x for x in scene if x.tag in TAGS):walk(n,f'{i}>',((n.get('name'),0),))
 return by_path,by_chain,by_name
work=BUILD/'flatbedTruck_work.i3d'
tree=ET.parse(work);ir=tree.getroot()
assert any(n.get('name')=='flatbedBody' for n in ir.find('Scene').iter())
assert not any(n.get('name')=='boxBody' for n in ir.find('Scene').iter())
for f in ir.find('Files'):
 name=f.get('filename')
 if not name.startswith('$'):
  full=(work.parent/name).resolve();assert full.is_relative_to(ROOT),(name,full)
  f.set('filename',full.relative_to(ROOT).as_posix())
ir.find('Shapes').set('externalShapesFile','flatbedTruck.i3d.shapes')
# Use brushed silver detail rather than a perfect mirror for the approved metalwork.
files=ir.find('Files');fileids={f.get('filename'):f.get('fileId') for f in files}
def fid(path):
 if path not in fileids:
  fileids[path]=str(max([int(x) for x in fileids.values()]+[0])+1);ET.SubElement(files,'File',filename=path,fileId=fileids[path])
 return fileids[path]
for material in ir.find('Materials'):
 name=material.get('name','').lower()
 if name in ['flatbed aluminum','tailgate stainless steel','polished raised diamond tread']:
  for custom in material.findall('Custommap'):
   suffix={'detailDiffuse':'diffuse','detailNormal':'normal','detailSpecular':'specular'}.get(custom.get('name'))
   if suffix:custom.set('fileId',fid('$data/shared/detailLibrary/metallic/silverCircularBrushed_'+suffix+'.png'))
  param=next((p for p in material.findall('CustomParameter') if p.get('name')=='smoothnessScale'),None)
  if param is None:param=ET.SubElement(material,'CustomParameter',name='smoothnessScale')
  param.set('value','0.65')
# Match the proven FH16 body belt convention: start on +X, local +Z toward -X.
# Empty-node transforms can be normalized without changing compiled geometry.
for node in ir.find('Scene').iter():
 name=node.get('name','')
 if name.startswith('flatbedBeltStart'):
  index=int(name[-2:])-1;node.set('translation',f'1.23 1.64 {1.20-index*.775:.6f}');node.set('rotation','0 -90 0')
 elif name.startswith('flatbedBeltEnd'):
  node.set('translation','0 0 2.46');node.attrib.pop('rotation',None)
tree.write(ROOT/'flatbedTruck.i3d',encoding='iso-8859-1',xml_declaration=True)
shutil.copyfile(BUILD/'flatbedTruck_work.i3d.shapes',ROOT/'flatbedTruck.i3d.shapes')
old_paths,_,_=chains(ROOT/'boxTruck.i3d');new_paths,new_chains,names=chains(ROOT/'flatbedTruck.i3d')
v=ET.parse(ROOT/'boxTruck.xml').getroot();v.set('type','flatbedPro')
v.find('storeData/name').text='Flatbed Truck Pro Edition'
v.find('storeData/image').text='store_flatbedTruck.dds';v.find('storeData/price').text='155000'
v.find('storeData/category').text='PROEDITIONTRUCKS'
v.find('base/filename').text='flatbedTruck.i3d'
maps=v.find('i3dMappings');removed=[]
for m in list(maps):
 chain=old_paths.get(m.get('node'));new=new_chains.get(chain)
 if new is not None:m.set('node',new)
 else:
  assert chain is not None and any(step[0]=='boxBody' for step in chain),(m.attrib,chain)
  removed.append(m.get('id'));maps.remove(m)
mapping={m.get('id'):m for m in maps}
def mapnode(alias,name=None):
 name=name or alias;paths=names.get(name,[]);assert len(paths)==1,(alias,name,paths)
 if alias in mapping:mapping[alias].set('node',paths[0])
 else:mapping[alias]=ET.SubElement(maps,'i3dMapping',id=alias,node=paths[0])
 return alias
for name in names:
 if name and (name.startswith('flatbed') or name in ['OPTION_BOARDS','OPTION_STAKES']):mapnode(name)
# Original curtain design has no role on the flatbed; preserve all cab/aero options.
design8=v.find('design8Configurations')
if design8 is not None:v.remove(design8)
for option in v.findall('design2Configurations/design2Configuration'):option.attrib.pop('isDefault',None)
v.find('design2Configurations/design2Configuration').set('isDefault','true')
for change in v.findall('.//wheelConfiguration/objectChange'):
 if change.get('node')=='licensePlateBack':change.set('translationActive','0 0.985 -5.405')
 if change.get('node')=='backlights':change.set('translationActive','0 0 -3.994')
anims=v.find('animations')
for a in list(anims):
 if a.get('name','').startswith('box'):anims.remove(a)
fragment=ET.parse(ROOT/'source/flatbed_runtime/stake_folding.xml').getroot()
anims.append(copy.deepcopy(fragment.find('animations/animation')))
boards=ET.SubElement(anims,'animation',name='flatbedBoards')
for side,s in [('Left',-1),('Right',1)]:
 for i in range(1,4):ET.SubElement(boards,'part',node=f'flatbedBoard{side}{i}',startTime='0',endTime='1.5',startRot='0 0 0',endRot=f'0 0 {-180*s}')
# Tailgate moves with the side walls on X (user, 2026-11-06); no separate key.
ET.SubElement(boards,'part',node='flatbedTailgate',startTime='0',endTime='1.2',startRot='0 0 0',endRot='-180 0 0')
fold=ET.SubElement(v,'foldable');configs=ET.SubElement(fold,'foldingConfigurations',title='$l10n_configuration_flatbedSides')
manifest=json.loads((BUILD/'body_manifest.json').read_text())
for index,(title,anim,kind) in enumerate([('$l10n_configuration_flatbedBoards','flatbedBoards','boards'),('$l10n_configuration_flatbedStakes','additionalForks','stakes')],1):
 c=ET.SubElement(configs,'foldingConfiguration',name=title,price='0',saveId=kind)
 if index==1:c.set('isDefault','true')
 if kind=='stakes':parts=copy.deepcopy(fragment.find('foldable/foldingConfigurations/foldingConfiguration/foldingParts'));c.append(parts)
 else:
  parts=ET.SubElement(c,'foldingParts',posDirectionText='$l10n_action_flatbedLowerBoards',negDirectionText='$l10n_action_flatbedRaiseBoards',startAnimTime='0',foldInputButton='IMPLEMENT_EXTRA2')
  ET.SubElement(parts,'foldingPart',animationName=anim,speedScale='1')
 parts.set('allowUnfoldingByAI','false')
 for alias,show in [('OPTION_BOARDS',kind=='boards'),('OPTION_STAKES',kind=='stakes')]:
  ET.SubElement(c,'objectChange',node=alias,visibilityActive=str(show).lower(),visibilityInactive=str(not show).lower())
 for name,collkind in manifest['collisions']:
  if collkind!='always':ET.SubElement(c,'objectChange',node=name,compoundChildActive=str(collkind==kind).lower(),compoundChildInactive=str(collkind!=kind).lower())
belts=v.find('tensionBelts/tensionBeltsConfigurations/tensionBeltsConfiguration/tensionBelts')
belts.set('linkNode','flatbedBelts');belts.set('activationTrigger','flatbedBeltTrigger')
for i,b in enumerate(belts.findall('tensionBelt'),1):b.set('startNode',f'flatbedBeltStart{i:02d}');b.set('endNode',f'flatbedBeltEnd{i:02d}')
# Native static-light controls. The existing rear real-light helpers stay on the chassis.
lights=v.find('lights');default=ET.SubElement(lights,'defaultLights');brakes=ET.SubElement(lights,'brakeLights');turn=ET.SubElement(lights,'turnLights');reverse=ET.SubElement(lights,'reverseLights')
for number,(name,info) in enumerate(manifest['lamps'].items(),1):
 alias=f'flatbedLamp{number:02d}';mapnode(alias,name)
 if info['kind']=='red':
  ET.SubElement(default,'defaultLight',node=alias,lightTypes='0',intensity='1')
  ET.SubElement(brakes,'brakeLight',node=alias,intensity='4')
 elif info['kind']=='reverse':ET.SubElement(reverse,'reverseLight',node=alias,intensity='4')
 elif info['marker']:ET.SubElement(default,'defaultLight',node=alias,lightTypes='0',intensity='1')
 else:ET.SubElement(turn,'turnLight'+info['side'],node=alias,intensity='4')
# Every mapping referenced by this new vehicle resolves into its saved I3D.
for m in maps:assert m.get('node') in new_paths,m.attrib
ET.indent(v);ET.ElementTree(v).write(ROOT/'flatbedTruck.xml',encoding='utf-8',xml_declaration=True)
(BUILD/'vehicle_manifest.json').write_text(json.dumps({'mappings':len(maps),'removed_box_mappings':removed,'folding_configs':['boards','stakes'],'belts':9,'animations':[a.get('name') for a in anims]},indent=2))
print('FLATBED_VEHICLE_READY',len(maps),'resolved mappings;2side configs;9belts;3body animations')

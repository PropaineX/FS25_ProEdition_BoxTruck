from pathlib import Path
import xml.etree.ElementTree as ET
import shutil,json
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'source/flatbed_runtime/verify';OUT.mkdir(exist_ok=True)
r=ET.parse(ROOT/'flatbedTruck.i3d')
for f in r.getroot().find('Files'):
 name=f.get('filename')
 if not name.startswith('$'):f.set('filename',(ROOT/name).as_posix())
r.getroot().find('Shapes').set('externalShapesFile','flatbedTruck_check.i3d.shapes')
r.write(OUT/'flatbedTruck_check.i3d',encoding='iso-8859-1',xml_declaration=True)
shutil.copyfile(ROOT/'flatbedTruck.i3d.shapes',OUT/'flatbedTruck_check.i3d.shapes')
v=ET.parse(ROOT/'flatbedTruck.xml').getroot();maps={m.get('id'):m.get('node') for m in v.find('i3dMappings')}
lines=['local N={}', '''local function resolve(path)
 local c,p=string.match(path,'^(%d+)>(.*)$');local n=getChildAt(getRootNode(),tonumber(c))
 for i in string.gmatch(p,'%d+') do n=getChildAt(n,tonumber(i)) end
 return n
end''']
for name,path in maps.items():lines.append(f'N[{json.dumps(name)}]=resolve({json.dumps(path)});assert(N[{json.dumps(name)}]~=0,"mapping missing {name}")')
# The renderer receives the same default object changes as the actual XML.
for group in v.iter():
 if not group.tag.endswith('Configurations'):continue
 configs=[c for c in group if c.tag.endswith('Configuration')]
 if not configs:continue
 chosen=next((c for c in configs if c.get('isDefault')=='true'),configs[0])
 for active in [False,True]:
  for c in configs:
   if (c is chosen)!=active:continue
   for e in c.findall('objectChange'):
    name=e.get('node');suffix='Active' if active else 'Inactive'
    for attr,fn in [('visibility','setVisibility'),('translation','setTranslation'),('rotation','setRotation')]:
     value=e.get(attr+suffix)
     if value is not None:
      args=value if attr=='visibility' else ','.join(value.split())
      if attr=='rotation':args=','.join(f'math.rad({x})' for x in value.split())
      lines.append(f'{fn}(N[{json.dumps(name)}],{args})')
lines.append('print("[FLATBED_QA] all363 runtime vehicle mappings resolved; default configuration applied")')
manifest=json.loads((ROOT/'source/flatbed_runtime/build/body_manifest.json').read_text())
for i,(name,info) in enumerate(manifest['lamps'].items(),1):
 lines.append(f'do local count,values=getShapeVertexColors(N["flatbedLamp{i:02d}"]);assert(count and count>0,"missing lamp vertex colors {i}") end')
lines.append('print("[FLATBED_QA] all13 lamp lenses have vertex-color data for native staticLight_vertex")')
lines.append('''function runtimeView(px,py,pz,tx,ty,tz,fov)
 if RUNTIMECAM==nil then RUNTIMECAM=createCamera('RuntimeFlatbedReview',math.rad(38),.05,500);link(getRootNode(),RUNTIMECAM) end
 setTranslation(RUNTIMECAM,px,py,pz);setDirection(RUNTIMECAM,px-tx,py-ty,pz-tz,0,1,0);setFovY(RUNTIMECAM,math.rad(fov or 38));setCamera(RUNTIMECAM);clearSelection()
end''')
animdata={}
for a in v.findall('animations/animation'):
 if a.get('name') in ['flatbedBoards','additionalForks','flatbedTailgate']:
  parts=[]
  for p in a.findall('part'):
   attr='Rot' if p.get('startRot') else 'Trans'
   parts.append((p.get('node'),attr,[float(x) for x in p.get('start'+attr).split()],[float(x) for x in p.get('end'+attr).split()]))
  animdata[a.get('name')]=parts
for anim,parts in animdata.items():
 lines.append(f'local function pose_{anim}(t)')
 for name,attr,a,b in parts:
  values=[f'({x}+({y-x})*t)' for x,y in zip(a,b)]
  if attr=='Rot':values=[f'math.rad({x})' for x in values]
  lines.append(f'{"setRotation" if attr=="Rot" else "setTranslation"}(N["{name}"],{",".join(values)})')
 lines.append('end')
lines.append('''function runtimePose(stakes,t,tail)
 setVisibility(N.OPTION_STAKES,stakes);setVisibility(N.OPTION_BOARDS,not stakes)
 pose_flatbedBoards(stakes and 0 or t);pose_additionalForks(stakes and t or 0);pose_flatbedTailgate(tail or 0)
end''')
lines.append('source("'+(ROOT/'source/preview_body_wheels.lua').as_posix()+'")')
lines.append('runtimePose(false,0,0);runtimeView(8,4,-12,0,2,-.7,38)')
lines.append('print("[FLATBED_QA] runtime body and XML poses ready;9belt start/end node pairs resolved")')
(OUT/'check_runtime.lua').write_text('\n'.join(lines))
print('Runtime-only scratch copy and XML-driven Editor check ready')

"""Export the approved flatbed body, runtime pivots, collisions and belt nodes."""
import bpy,math,sys,runpy,json
from pathlib import Path
from mathutils import Vector
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'source/flatbed_runtime/build';OUT.mkdir(exist_ok=True)
g=lambda x,y,z:Vector((x,-z,y))
def reparent(ob,parent):
 bpy.context.view_layer.update();mw=ob.matrix_world.copy();ob.parent=parent;ob.matrix_world=mw;bpy.context.view_layer.update()
def empty(name,parent=None,pos=(0,0,0),ry=0):
 ob=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(ob);ob.location=g(*pos);ob.rotation_euler.z=math.radians(ry)
 if parent:reparent(ob,parent)
 return ob
def cube(name,parent,bounds):
 x0,x1,y0,y1,z0,z1=bounds
 bpy.ops.mesh.primitive_cube_add(size=1,location=g((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
 ob=bpy.context.object;ob.name=name;ob.dimensions=(x1-x0,z1-z0,y1-y0);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 reparent(ob,parent);return ob
fixed=bpy.data.objects['Flatbed_FIXED'];boards=bpy.data.objects['OPTION_BOARDS'];stakes=bpy.data.objects['OPTION_STAKES']
gate=bpy.data.objects['Tailgate_30cm_proposal'];gate.name='flatbedTailgate'
# Pivot about the bottom edge, preserving the approved shut geometry.
world={o:o.matrix_world.copy() for o in gate.children}
gate.location=g(0,1.625,-5.37);bpy.context.view_layer.update()
for ob,mw in world.items():ob.matrix_world=mw
reparent(gate,boards)
body=empty('flatbedBody')
for ob in [fixed,boards,stakes]:reparent(ob,body)
collisions=[]
def col(name,parent,bounds,kind='always'):
 ob=cube(name,parent,bounds);collisions.append((name,kind));return ob
col('flatbedColFloor',body,(-1.275,1.275,1.50,1.625,-5.35,1.50))
col('flatbedColHeadboard',body,(-1.275,1.275,1.625,3.738,1.48,1.56))
for side,s in [('Left',-1),('Right',1)]:
 for j in range(3):
  pivot=bpy.data.objects[f'Board hinge {s} {j}'];pivot.name=f'flatbedBoard{side}{j+1}'
  a=-5.35+j*6.85/3+.065;b=-5.35+(j+1)*6.85/3-.065
  col(f'flatbedColBoard{side}{j+1}',pivot,(s*1.25-.025,s*1.25+.025,1.65,2.22,a,b),'boards')
 for j in range(4):
  z=-5.35+j*6.85/3
  col(f'flatbedColPost{side}{j+1}',boards,(s*1.235-.045,s*1.235+.045,1.625,2.22,z-.045,z+.045),'boards')
 for j,z in enumerate([-5.10,-3.83,-2.56,-1.29,-.02,1.25],1):
  pivot=bpy.data.objects[f'Stake {s} {j}'];pivot.name=f'flatbedStake{side}{j}'
  col(f'flatbedColStake{side}{j}',pivot,(s*1.23-.035,s*1.23+.035,1.625,2.82,z-.045,z+.045),'stakes')
col('flatbedColTailgate',gate,(-1.185,1.185,1.625,1.925,-5.383,-5.358),'boards')
belts=empty('flatbedBelts',body)
for j in range(9):
 z=1.20-j*.775
 start=empty(f'flatbedBeltStart{j+1:02d}',belts,(1.23,1.64,z),-90)
 empty(f'flatbedBeltEnd{j+1:02d}',start,(-1.23,1.64,z),-90)
trigger=cube('flatbedBeltTrigger',body,(-1.45,1.45,1.625,4.15,-5.5,1.65))
# Add a separate reverse-light lens while retaining the approved light-bar layout.
lampwhite=bpy.data.materials.new('Flatbed reverse lens');lampwhite.diffuse_color=(.8,.8,.8,1)
reverse=cube('flatbedReverseLens',fixed,(-.39,-.30,.945,1.025,-5.402,-5.372));reverse.data.materials.append(lampwhite)
lamps={}
for ob in body.children_recursive:
 if ob.type!='MESH':continue
 if ob.name.startswith('Rear lamp red'):color=(1,.015,.015,1);kind='red'
 elif ob.name.startswith('Rear lamp amber') or ob.name.startswith('Amber side marker'):color=(1,.28,.012,1);kind='amber'
 elif ob.name=='flatbedReverseLens':color=(1,1,1,1);kind='reverse'
 else:continue
 # Each lamp gets its own material to avoid side-marker/indicator cross-talk.
 mat=bpy.data.materials.new('flatbedLamp_'+ob.name.replace(' ','_'));mat.diffuse_color=tuple(color)
 ob.data.materials.clear();ob.data.materials.append(mat)
 attr=ob.data.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
 for item in attr.data:item.color=color
 lamps[ob.name]={'kind':kind,'side':'Left' if ob.location.x<0 else 'Right','material':mat.name,'marker':ob.name.startswith('Amber side marker')}
keep={body,*body.children_recursive}
for ob in list(bpy.data.objects):
 if ob not in keep:bpy.data.objects.remove(ob,do_unlink=True)
for ob in keep:ob.hide_viewport=False;ob.hide_render=False
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'flatbed_runtime_body.blend'))
sys.argv=['export_body.py','--',str(OUT/'flatbedBody.i3d')]
runpy.run_path(str(ROOT/'source/export_body.py'),run_name='__main__')
tree=ET.parse(OUT/'flatbedBody.i3d');r=tree.getroot();files=r.find('Files')
if files is None:files=ET.SubElement(r,'Files')
ids={e.get('filename'):e.get('fileId') for e in files}
def fid(path):
 if path not in ids:
  ids[path]=str(max([int(i) for i in ids.values()]+[0])+1);ET.SubElement(files,'File',fileId=ids[path],filename=path)
 return ids[path]
D='$data/shared/detailLibrary/'
lampmats={v['material'] for v in lamps.values()}
for m in r.find('Materials'):
 name=m.get('name');color=m.get('diffuseColor','1 1 1 1').split()[:3]
 for k in list(m.attrib):
  if k not in ['name','materialId']:del m.attrib[k]
 for c in list(m):m.remove(c)
 m.set('customShaderId',fid('$data/shaders/vehicleShader.xml'))
 if name.startswith('Safety tape '):m.set('customShaderVariation','reflector')
 if name in lampmats:m.set('customShaderVariation','staticLight_vertex')
 if 'floor' in name.lower():dd,dn,ds=D+'nonMetallic/wood/wood2Oak_diffuse.png',D+'nonMetallic/wood/wood2_normal.png',D+'nonMetallic/wood/wood2_specular.png'
 elif 'stainless' in name.lower() or 'diamond' in name.lower() or 'aluminum' in name.lower():dd,dn,ds=D+'metallic/silverCircularBrushed_diffuse.png',D+'metallic/silverCircularBrushed_normal.png',D+'metallic/silverCircularBrushed_specular.png'
 else:dd,dn,ds=D+'nonMetallic/metal/metalPainted_diffuse.png',D+'flat_normal.png',D+'nonMetallic/metal/metalPainted_specular.png'
 params={'colorScale':' '.join(color)}
 if 'stainless' in name.lower() or 'diamond' in name.lower() or 'aluminum' in name.lower():params['smoothnessScale']='0.65'
 if name in lampmats:params.update(lightIds0='0 0 0 0')
 for k,v in params.items():ET.SubElement(m,'CustomParameter',name=k,value=v)
 for n,path in [('detailDiffuse',dd),('detailNormal',dn),('detailSpecular',ds)]:ET.SubElement(m,'Custommap',name=n,fileId=fid(path))
 ET.SubElement(m,'Texture',fileId=fid('$data/shared/white_diffuse.png'))
 ET.SubElement(m,'Normalmap',fileId=fid('$data/shared/default_normal.png'))
 ET.SubElement(m,'Glossmap',fileId=fid('$data/shared/default_vmask.png'))
collnames={name for name,_ in collisions}
for node in r.find('Scene').iter():
 name=node.get('name')
 if name in collnames:
  node.set('nonRenderable','true');node.set('compoundChild','true');node.set('collisionFilterGroup','0x10004');node.set('collisionFilterMask','0xfe3ffb83')
 if name=='flatbedBeltTrigger':
  node.set('nonRenderable','true');node.set('kinematic','true');node.set('compound','true');node.set('trigger','true');node.set('collisionFilterGroup','0x20000000');node.set('collisionFilterMask','0x100000')
 if name=='OPTION_STAKES':node.set('visibility','false')
tree.write(OUT/'flatbedBody.i3d',encoding='iso-8859-1',xml_declaration=True)
(OUT/'body_manifest.json').write_text(json.dumps({'collisions':collisions,'lamps':lamps,'body_root':'flatbedBody','floor':1.625,'tailgate_height':.30},indent=2))
print('RUNTIME_BODY_READY',len(collisions),'collision shapes;',len(lamps),'functional light lenses;9belts')

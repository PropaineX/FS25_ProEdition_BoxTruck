"""30 cm diamond-plate stainless tailgate, separate visual proposal."""
import bpy,math,sys,runpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
out=root/'previews/flatbed_tailgate_v1';out.mkdir(exist_ok=True)
steel=bpy.data.materials.new('Tailgate stainless steel');steel.diffuse_color=(.72,.75,.78,1);steel.use_nodes=True
bs=steel.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=steel.diffuse_color
bs.inputs['Metallic'].default_value=1;bs.inputs['Roughness'].default_value=.22
dark=bpy.data.materials.new('Tailgate latch steel');dark.diffuse_color=(.13,.15,.17,1)
gate=bpy.data.objects.new('Tailgate_30cm_proposal',None);bpy.context.scene.collection.objects.link(gate)
def box(name,x0,x1,y0,y1,z0,z1,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=((x0+x1)/2,-(z0+z1)/2,(y0+y1)/2))
 ob=bpy.context.object;ob.name=name;ob.dimensions=(x1-x0,z1-z0,y1-y0)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 ob.data.materials.append(mat);ob.parent=gate
 mod=ob.modifiers.new('Folded edge radius','BEVEL');mod.width=.002;mod.segments=2
 return ob
panel=box('Tailgate stainless panel',-1.185,1.185,1.625,1.925,-5.383,-5.358,steel)
box('Tailgate upper folded lip',-1.185,1.185,1.91,1.925,-5.391,-5.35,steel)
for x in [-.80,.80]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.017,depth=.12,location=(x,5.395,1.643),rotation=(0,math.pi/2,0))
 ob=bpy.context.object;ob.name='Tailgate hinge barrel';ob.data.materials.append(steel);ob.parent=gate
 for poly in ob.data.polygons:poly.use_smooth=len(poly.vertices)==4
for x in [-1.12,1.12]:
 box('Tailgate latch mounting',x-.023,x+.023,1.835,1.895,-5.397,-5.383,dark)
 box('Tailgate latch lever',x-.008,x+.008,1.84,1.89,-5.410,-5.397,steel)
# Raised diamond tread is real geometry on the rear-facing surface.
verts=[];faces=[]
for row in range(6):
 y=1.662+row*.043
 for col in range(39):
  x=-1.14+col*.060
  a=math.radians(45 if (row+col)%2==0 else -45)
  u=Vector((math.cos(a),math.sin(a)));v=Vector((-math.sin(a),math.cos(a)))
  corners=[u*.018,v*.0045,-u*.018,-v*.0045]
  start=len(verts)
  for depth in [5.3833,5.3848]:
   for c in corners:verts.append((x+c.x,depth,y+c.y))
  faces.append((start+4,start+7,start+6,start+5))
  for j in range(4):faces.append((start+j,start+(j+1)%4,start+4+(j+1)%4,start+4+j))
mesh=bpy.data.meshes.new('Raised stainless diamond tread');mesh.from_pydata(verts,[],faces);mesh.materials.append(steel)
ob=bpy.data.objects.new('Tailgate diamond pattern',mesh);bpy.context.scene.collection.objects.link(ob);ob.parent=gate
bpy.context.view_layer.update()
assert abs(panel.dimensions.z-.30)<1e-5
assert abs(panel.dimensions.x-2.37)<1e-5
bpy.ops.wm.save_as_mainfile(filepath=str(out/'flatbed_tailgate_proposal_v1.blend'))
(out/'validation.json').write_text(json.dumps({'height_m':.30,'width_m':2.37,'side_board_height_m':.60,'material':'diamond-pattern stainless steel','raised_diamonds':234,'both_configurations':True,'proposal_only':True,'runtime_changed':False},indent=2))
keep={gate,*gate.children_recursive}
for ob in list(bpy.data.objects):
 if ob not in keep:bpy.data.objects.remove(ob,do_unlink=True)
sys.argv=['export_body.py','--',str(out/'tailgatePreview.i3d')]
runpy.run_path(str(root/'source/export_body.py'),run_name='__main__')

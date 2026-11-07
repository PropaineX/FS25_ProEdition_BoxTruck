"""Separate review proposal: red/white diagonal tape around both tube ends."""
import bpy, math, sys, runpy, json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
out=root/'previews/flatbed_underrun_stripes_v1'; out.mkdir(exist_ok=True)
def mat(name,color):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1)
 bs.inputs['Metallic'].default_value=.3;bs.inputs['Roughness'].default_value=.2
 bs.inputs['Coat Weight'].default_value=.5
 return m
red=mat('Safety tape red preview',(.8,.012,.018))
white=mat('Safety tape white preview',(.95,.95,.92))
parent=bpy.data.objects['Flatbed_FIXED']; created=[]
for side in [-1,1]:
 x0,x1=(-1.12,-.64) if side<0 else (.64,1.12)
 verts=[]; faces=[]; mids=[]; nx=160; na=96; r=.066
 for i in range(nx+1):
  x=x0+(x1-x0)*i/nx
  for j in range(na):
   a=2*math.pi*j/na
   verts.append((x,5.255+r*math.cos(a),.615+r*math.sin(a)))
 for i in range(nx):
  for j in range(na):
   faces.append((i*na+j,(i+1)*na+j,(i+1)*na+(j+1)%na,i*na+(j+1)%na))
   x=x0+(x1-x0)*(i+.5)/nx; h=r*math.sin(2*math.pi*(j+.5)/na)
   mids.append(int(math.floor((side*x+h)/.065))%2)
 mesh=bpy.data.meshes.new('Diagonal tape sleeve mesh');mesh.from_pydata(verts,[],faces);mesh.materials.append(red);mesh.materials.append(white)
 ob=bpy.data.objects.new('Reflective safety band '+('left' if side<0 else 'right'),mesh)
 bpy.context.scene.collection.objects.link(ob);ob.parent=parent
 for face,mid in zip(mesh.polygons,mids):face.material_index=mid;face.use_smooth=True
 created.append(ob)
bpy.context.view_layer.update()
assert len(created)==2
for ob in created: assert abs(ob.dimensions.x-.48)<1e-5
bpy.ops.wm.save_as_mainfile(filepath=str(out/'flatbed_stripes_proposal_v1.blend'))
(out/'validation.json').write_text(json.dumps({'proposal_only':True,'bands':2,'band_width_m':.48,'end_margin_m':.04,'tube_diameter_m':.13,'stripe_width_m':.065,'retroreflection':'UNTESTED; visual mockup materials only','runtime_changes':False},indent=2))
for ob in created:
 mw=ob.matrix_world.copy();ob.parent=None;ob.matrix_world=mw
for ob in list(bpy.data.objects):
 if ob not in created:bpy.data.objects.remove(ob,do_unlink=True)
sys.argv=['export_body.py','--',str(out/'reflectiveBands.i3d')]
runpy.run_path(str(root/'source/export_body.py'),run_name='__main__')

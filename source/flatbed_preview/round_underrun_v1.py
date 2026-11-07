import bpy, math, sys, runpy, json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
out=root/'previews/flatbed_round_underrun_v1'; out.mkdir(exist_ok=True)
old=bpy.data.objects['Rear underrun beam']
material=old.data.materials[0]; parent=old.parent
before={o.name:(tuple(o.location),tuple(o.rotation_euler),tuple(o.scale),len(o.data.vertices) if o.type=='MESH' else None) for o in bpy.data.objects if o!=old}
bpy.data.objects.remove(old,do_unlink=True)
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.065,depth=2.32,end_fill_type='NGON',location=(0,5.255,.615),rotation=(0,math.pi/2,0))
tube=bpy.context.object; tube.name='Rear underrun round tube'; tube.data.materials.append(material)
bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
bpy.context.view_layer.update()
mw=tube.matrix_world.copy(); tube.parent=parent; tube.matrix_world=mw
bpy.context.view_layer.update()
print('TUBE_DIMENSIONS',tuple(tube.dimensions),flush=True)
for polygon in tube.data.polygons: polygon.use_smooth=len(polygon.vertices)==4
bevel=tube.modifiers.new('Soft tube end edges','BEVEL'); bevel.width=.003; bevel.segments=3
for name,expected in before.items():
    o=bpy.data.objects[name]
    assert (tuple(o.location),tuple(o.rotation_euler),tuple(o.scale),len(o.data.vertices) if o.type=='MESH' else None)==expected,name
assert all(abs(a-b)<1e-5 for a,b in zip(tube.dimensions,(2.32,.13,.13)))
bpy.ops.wm.save_as_mainfile(filepath=str(out/'flatbed_round_underrun_v1.blend'))
(out/'validation.json').write_text(json.dumps({'tube_length_m':2.32,'tube_diameter_m':.13,'center_game_m':[0,.615,-5.255],'other_objects_preserved':len(before),'runtime_changed':False},indent=2))
mw=tube.matrix_world.copy(); tube.parent=None; tube.matrix_world=mw
for ob in list(bpy.data.objects):
    if ob!=tube: bpy.data.objects.remove(ob,do_unlink=True)
tube.hide_render=False; tube.hide_viewport=False
sys.argv=['export_body.py','--',str(out/'roundTube.i3d')]
runpy.run_path(str(root/'source/export_body.py'),run_name='__main__')

import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
out=root/'previews/flatbed_stake_motion_v1'
report=json.loads((out/'validation.json').read_text())
bpy.context.preferences.edit.keyframe_new_interpolation_type='LINEAR'
scene=bpy.context.scene;scene.render.fps=20;scene.frame_start=1;scene.frame_end=15
for track in report['tracks']:
 ob=bpy.data.objects[track['body_node']]
 for frame,key in [(1,'start'),(15,'end')]:
  x,y,z=track[key];ob.location=(x,-z,y);ob.keyframe_insert(data_path='location',frame=frame,group='Fliegl native additionalForks')
 ob.animation_data.action.name=track['mapping']+'_additionalForks'
for parent,show in [('OPTION_STAKES',True),('OPTION_BOARDS',False),('Tailgate_30cm_proposal',False)]:
 ob=bpy.data.objects.get(parent)
 if ob:
  for item in [ob,*ob.children_recursive]:item.hide_render=not show;item.hide_viewport=not show
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'flatbed_stake_motion_v1.blend'))
print('SAVED six animated stakes; linear channels, 20fps frames1..15 =0.7s; stake configuration only')

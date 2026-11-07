import bpy, sys, runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
keep=set()
for name in ['Flatbed_FIXED','OPTION_BOARDS','OPTION_STAKES']:
    ob=bpy.data.objects[name]; keep.add(ob); keep.update(ob.children_recursive)
for ob in list(bpy.data.objects):
    if ob not in keep: bpy.data.objects.remove(ob,do_unlink=True)
for ob in keep: ob.hide_render=False; ob.hide_viewport=False
sys.argv=['export_body.py','--',str(root/'previews/flatbed_fitted_v1/flatbedPreview.i3d')]
runpy.run_path(str(root/'source/export_body.py'),run_name='__main__')

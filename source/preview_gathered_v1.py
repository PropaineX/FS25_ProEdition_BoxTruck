"""Preview only: compare existing pleats with a rounded, irregular gathered sheet."""
import bpy, sys, math, random
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT/'previews/gathered_v1'
OUT.mkdir(parents=True, exist_ok=True)
sys.argv = ['build_body.py','--',str(OUT),'body_reference','norender']
exec(compile((ROOT/'source/build_body.py').read_text(), 'build_body.py', 'exec'))
for ob in bpy.data.objects:
    if ob.name.startswith('col') or ob.name == 'beltActivationTrigger': ob.hide_render = True
for side in ('Left','Right'):
    for ob in bpy.data.objects['curtain'+side+'Closed'].children_recursive: ob.hide_render=True
    for ob in bpy.data.objects['curtain'+side+'Open'].children_recursive: ob.hide_render=False
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.studiolight_rotate_z=.5
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.show_shadows=True
scene.display.shading.show_object_outline=False
scene.world=bpy.data.worlds.new('previewWorld')
scene.world.color=(.16,.18,.22)
scene.render.resolution_x=1000; scene.render.resolution_y=1100
scene.render.resolution_percentage=100
camera=bpy.data.objects.new('gatherCamera',bpy.data.cameras.new('gatherCamera'))
scene.collection.objects.link(camera); scene.camera=camera
camera.location=g2b(5.4,3.25,-3.5)
target=g2b(1.32,2.85,-4.96)
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'; camera.data.ortho_scale=3.2
def shot(name):
    scene.render.filepath=str(OUT/(name+'.png')); bpy.ops.render.render(write_still=True)
shot('before')
for side,sgn,seed in [('Left',1,7),('Right',-1,11)]:
    ob=bpy.data.objects['curtain'+side+'Gathered']
    rnd=random.Random(seed)
    folds=7; cols=folds*24; rows=48
    widths=[rnd.uniform(.7,1.4) for _ in range(folds)]
    edges=[0]
    for w in widths: edges.append(edges[-1]+w/sum(widths))
    amps=[rnd.uniform(.12,.21) for _ in range(folds)]
    phases=[rnd.uniform(-1,1) for _ in range(folds)]
    verts=[]; faces=[]
    for r in range(rows+1):
        t=r/rows
        for c in range(cols+1):
            u=c/cols
            k=min(folds-1,next((i for i in range(folds) if u<=edges[i+1]),folds-1))
            f=(u-edges[k])/(edges[k+1]-edges[k])
            wave=math.sin(math.pi*f)**2
            depth=.018+amps[k]*wave*(.72+.34*(1-t)+.18*math.sin(t*7+phases[k]))
            depth+=.012*math.sin(t*14+u*22)*math.sin(math.pi*t)
            z=CURTAIN_REAR_Z+.02+.64*(1-u)
            z+=.026*math.sin(t*5+phases[k])*math.sin(math.pi*t)+.018*math.sin(u*17)*(1-t)
            y=CLOTH_Y0+(CLOTH_Y1-CLOTH_Y0)*t
            y+=(1-t)**5*(.035*math.sin(u*23)-.035*wave)
            verts.append(tuple(ob.matrix_world.inverted() @ g2b(sgn*(CLOTH_X+depth),y,z)))
    for r in range(rows):
        for c in range(cols):
            a=r*(cols+1)+c; faces.append((a,a+1,a+cols+2,a+cols+1))
    me=bpy.data.meshes.new('roundedGather'+side); me.from_pydata(verts,[],faces); me.materials.append(bpy.data.materials['curtainCloth'])
    for poly in me.polygons: poly.use_smooth=True
    ob.data=me
    # Old rigid hanging straps don't follow the preview fabric.
    bpy.data.objects['curtain'+side+'GatheredStraps'].hide_render=True
shot('proposed')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'gathered_proposal.blend'))

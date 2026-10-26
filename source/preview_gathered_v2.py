"""Preview only: compare existing pleats with a rounded, irregular gathered sheet."""
import bpy, sys, math, random
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT/'previews/gathered_v2'
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
    folds=5; cols=folds*48; rows=96
    widths=[.65,1.65,.85,1.45,.5]
    if side=='Right': widths.reverse()
    edges=[0]
    for w in widths: edges.append(edges[-1]+w/sum(widths))
    amps=[.22,.34,.18,.29,.23]
    phases=[rnd.uniform(-math.pi,math.pi) for _ in range(folds)]
    verts=[]; faces=[]
    for r in range(rows+1):
        t=r/rows
        for c in range(cols+1):
            u=c/cols
            # Continuous phase warping bends fold valleys sideways at different heights.
            warped=u+(.065*math.sin(t*6.5+u*8)+.035*math.sin(t*11-u*13))*math.sin(math.pi*u)*(1-.65*t)
            k=min(folds-1,next((i for i in range(folds) if warped<=edges[i+1]),folds-1))
            f=(warped-edges[k])/(edges[k+1]-edges[k])
            wave=(.5-.5*math.cos(2*math.pi*f))
            phase=phases[k]
            depth=.025+amps[k]*wave*(.80+.28*math.sin(t*5.8+phase)+.22*(1-t))
            depth+=.035*math.sin(t*12+u*19)*math.sin(math.pi*t)*math.sin(math.pi*u)
            # Fabric doubles back inside each fold rather than forming parallel flutes.
            z=CURTAIN_REAR_Z+.035+.57*(1-u)
            z+=.070*math.sin(2*math.pi*f)*math.sin(math.pi*u)
            z+=.085*math.sin(t*5.5+u*9)*(1-t)*math.sin(math.pi*u)
            y=CLOTH_Y0+(CLOTH_Y1-CLOTH_Y0)*t
            y+=(1-t)**4*(.065*math.sin(u*19+.5)+.025*math.sin(u*43)-.055*wave)
            y+=.026*math.sin(u*25+t*9)*math.sin(math.pi*t)**2
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

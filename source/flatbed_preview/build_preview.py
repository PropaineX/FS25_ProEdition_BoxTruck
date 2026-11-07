"""Review model only. Run with Blender -b -P this_script -- [stage|all]."""
import bpy, math, sys, json
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'previews/flatbed_fitted_v1'
MODE = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'all'
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

def material(name, rgb, metallic=0, rough=.45):
    m=bpy.data.materials.new(name); m.diffuse_color=(*rgb,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*rgb,1)
    bs.inputs['Metallic'].default_value=metallic; bs.inputs['Roughness'].default_value=rough
    return m

steel=material('Flatbed dark steel',(.055,.065,.075),.65)
alu=material('Flatbed aluminum',(.6,.65,.7),.7)
wood=material('Flatbed load floor',(.23,.16,.10),0,.85)
red=material('Rear red lenses',(.55,.012,.018),.15)
amber=material('Amber markers',(.95,.28,.015),.2)
white=material('Headboard paint',(.78,.81,.83),.3)

def g(x,y,z): return Vector((x,-z,y))
def box(name, x0,x1,y0,y1,z0,z1,mat,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=g((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
    ob=bpy.context.object; ob.name=name; ob.dimensions=(x1-x0,z1-z0,y1-y0)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(mat)
    bevel=ob.modifiers.new('Rounded fabrication edges','BEVEL'); bevel.width=.006; bevel.segments=2
    if parent:
        mw=ob.matrix_world.copy(); ob.parent=parent; ob.matrix_world=mw
    return ob

def empty(name,loc=(0,0,0)):
    ob=bpy.data.objects.new(name,None); scene.collection.objects.link(ob); ob.location=g(*loc); return ob

# Supported GIANTS Editor export, preview only. GE exports centimeters, Y up.
before=set(bpy.data.objects)
if (OUT/'volvo_preview.obj').exists():
    bpy.ops.wm.obj_import(filepath=str(OUT/'volvo_preview.obj'))
truck=[o for o in bpy.data.objects if o not in before]
for ob in truck:
    if ob.type=='MESH':
        ob.data.transform(Matrix.Scale(.01,4) @ ob.matrix_world)
        ob.matrix_world=Matrix.Identity(4)
    ob.name='VOLVO_REF_'+ob.name

fixed=empty('Flatbed_FIXED')
box('Structural deck',-1.275,1.275,1.50,1.62,-5.35,1.50,steel,fixed)
for i in range(15):
    x=-1.21+i*2.42/15
    box('Deck plank %02d'%i,x,x+2.42/15-.006,1.615,1.625,-5.29,1.44,wood,fixed)
for x in [-.42,.42]: box('Subframe rail',x-.055,x+.055,1.18,1.50,-5.18,1.46,steel,fixed)
for i in range(12):
    z=-5.1+i*.58; box('Deck crossmember',-1.23,1.23,1.36,1.50,z-.035,z+.035,steel,fixed)
for s in [-1,1]:
    x=s*1.24
    box('Deck edge aluminum rail',x-.035,x+.035,1.50,1.65,-5.35,1.50,alu,fixed)
    box('Headboard upright',x-.04,x+.04,1.62,3.738,1.48,1.56,steel,fixed)
    for z in [-4.8,-3,-1.2,.65]:
        box('Amber side marker',s*1.28-.015,s*1.28+.015,1.48,1.54,z-.065,z+.065,amber,fixed)
box('Headboard top',-1.275,1.275,3.65,3.738,1.48,1.56,steel,fixed)
box('Headboard lower protection',-1.20,1.20,1.64,2.37,1.49,1.54,white,fixed)
for y in [2.43,2.75,3.07,3.39]: box('Headboard horizontal rail',-1.20,1.20,y,y+.055,1.49,1.54,alu,fixed)
for x in [-.6,0,.6]: box('Headboard vertical bar',x-.025,x+.025,2.37,3.65,1.49,1.54,alu,fixed)
box('Rear light bar',-1.20,1.20,.87,1.10,-5.37,-5.24,steel,fixed)
box('Rear underrun beam',-1.16,1.16,.55,.68,-5.32,-5.19,alu,fixed)
for x in [-.85,.85]:
    box('Rear underrun bracket',x-.045,x+.045,.65,1.48,-5.25,-5.13,steel,fixed)
    box('Rear lamp red',x-.24,x+.06,.92,1.05,-5.40,-5.37,red,fixed)
    box('Rear lamp amber',x+.075,x+.23,.92,1.05,-5.40,-5.37,amber,fixed)

boards=empty('OPTION_BOARDS'); stakes=empty('OPTION_STAKES')
pivots=[]; sliders=[]
for s in [-1,1]:
    for j in range(4):
        z=-5.35+j*6.85/3
        box('Board fixed post',s*1.235-.045,s*1.235+.045,1.62,2.22,z-.045,z+.045,steel,boards)
    for j in range(3):
        z0=-5.35+j*6.85/3+.065; z1=-5.35+(j+1)*6.85/3-.065
        pivot=empty('Board hinge %s %d'%(s,j),(s*1.275,1.64,(z0+z1)/2)); pivot.parent=boards
        box('Drop side panel',s*1.25-.025,s*1.25+.025,1.65,2.22,z0,z1,alu,pivot)
        for y in [1.68,1.82,1.96,2.10,2.19]:
            box('Board extrusion',s*1.28-.008,s*1.28+.008,y,y+.013,z0,z1,steel,pivot)
        for z in [z0+.12,z1-.12]:
            box('Board latch',s*1.285-.015,s*1.285+.015,2.04,2.16,z-.035,z+.035,steel,pivot)
            box('Board hinge barrel',s*1.285-.025,s*1.285+.025,1.61,1.67,z-.065,z+.065,steel,pivot)
        pivots.append((pivot,s))
    for j,z in enumerate([-5.10,-3.83,-2.56,-1.29,-.02,1.25]):
        p=empty('Stake %s %d'%(s,j+1),(s*1.23,1.62,z)); p.parent=stakes
        box('Stake steel upright',s*1.23-.035,s*1.23+.035,1.62,2.82,z-.045,z+.045,steel,p)
        box('Stake sliding shoe',s*1.23-.065,s*1.23+.065,1.57,1.71,z-.085,z+.085,alu,p)
        sliders.append((p,j,z))

def show(parent,visible):
    for ob in [parent]+list(parent.children_recursive): ob.hide_render=not visible
def state(kind,opened=False):
    show(boards,kind=='boards'); show(stakes,kind=='stakes')
    for p,s in pivots: p.rotation_euler.y=math.radians(-180*s if opened else 0)
    for p,j,z in sliders:
        p.location.y=-(([-3.97,-3.83,-1.43,-1.29,1.11,1.25][j]) if opened else z)

ground=material('Studio ground',(.22,.25,.29),0,.85)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.30)); bpy.context.object.data.materials.append(ground)
scene.world=bpy.data.worlds.new('Studio world'); scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.65,.8,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for loc,power,size in [((5,-2,10),2200,8),((-5,-1,7),1800,7),((0,7,9),2500,6)]:
    data=bpy.data.lights.new('Softbox','AREA'); data.energy=power; data.shape='DISK'; data.size=size
    ob=bpy.data.objects.new('Softbox',data); scene.collection.objects.link(ob); ob.location=loc
    ob.rotation_euler=(Vector((0,0,1.5))-ob.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('Preview camera'); cam=bpy.data.objects.new('Preview camera',camd); scene.collection.objects.link(cam); scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.cycles.use_denoising=True
scene.render.resolution_x=1500; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
def shot(name,pos,target,scale):
    cam.location=g(*pos); cam.rotation_euler=(g(*target)-cam.location).to_track_quat('-Z','Y').to_euler()
    camd.type='ORTHO'; camd.ortho_scale=scale; scene.render.filepath=str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True); print('PREVIEW_RENDER',name,flush=True)

show(boards,False); show(stakes,False)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'flatbed_fitted_v1.blend'))
shot('01_deck_headboard',(11,7,12),(0,1.9,-.4),13)
if MODE!='stage':
    for kind in ['boards','stakes']:
        for opened in [False,True]:
            state(kind,opened); suffix=kind+('_open' if opened else '_closed')
            shot(suffix+'_side',(20,3,-.4),(0,2,-.4),11.5)
            shot(suffix+'_rear34',(10,6,-13),(0,1.9,-.6),12)
        state(kind,False)
        shot(kind+'_front34',(10,6,12),(0,1.9,-.4),13)
        shot(kind+'_rear',(0,3,-20),(0,2,-2),5.5)
    state('boards',False)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'flatbed_fitted_v1.blend'))
    (OUT/'validation.json').write_text(json.dumps({'preview_only':True,'deck_m':[2.55,6.85], 'deck_top_root':1.62,'headboard_top_root':3.738,'board_pivots':len(pivots),'stakes':len(sliders),'truck_meshes':len(truck)},indent=2))

"""Three preserved v7 studies with independently varied lower fabric only."""
import bpy, math, random, hashlib, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'previews/gathered_variants_v1'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'previews/gathered_v7/gathered_proposal.blend'))
scene=bpy.context.scene
objects=[bpy.data.objects['curtain'+side+'Gathered'] for side in ('Left','Right')]
original={ob.name:[v.co.copy() for v in ob.data.vertices] for ob in objects}
cols=240; rows=96
digests=[]
for variant in range(1,4):
    for side_index,ob in enumerate(objects):
        rng=random.Random(4100+variant*173+side_index*31)
        phases=[rng.uniform(-math.pi,math.pi) for _ in range(6)]
        strengths=[rng.uniform(.7,1.25) for _ in range(3)]
        inv=ob.matrix_world.inverted()
        sign=1 if side_index==0 else -1
        for v,base in zip(ob.data.vertices,original[ob.name]):
            r,c=divmod(v.index,cols+1); t=r/rows; u=c/cols
            # Keep the upper 60% exactly; release variation smoothly below it.
            q=max(0,min(1,(.40-t)/.40)); weight=q*q*(3-2*q)
            world=ob.matrix_world @ base
            edge=math.sin(math.pi*u)
            world.x+=sign*weight*edge*strengths[0]*(.060*math.sin(u*15+phases[0]+t*5)+.028*math.sin(u*31+phases[1]))
            world.y-=weight*strengths[1]*(.060*math.sin(u*13+phases[2])*edge+.022*math.sin(u*27+phases[3]))
            world.z+=weight*strengths[2]*(.065*math.sin(u*17+phases[4])+.023*math.sin(u*35+phases[5]))
            v.co=inv @ world
        ob.data.update()
        # Verify upper fabric is unchanged, and each mesh is reproducible.
        assert all((v.co-base).length<1e-5 for v,base in zip(ob.data.vertices,original[ob.name]) if v.index//(cols+1)/rows>=.4)
    digest=hashlib.sha256(b''.join(str([tuple(v.co) for v in ob.data.vertices]).encode() for ob in objects)).hexdigest()
    digests.append(digest)
    scene.render.filepath=str(OUT/f'version_{variant}.png')
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'version_{variant}.blend'))
assert len(set(digests))==3
(OUT/'validation.json').write_text(json.dumps({'different_mesh_hashes':digests,'upper_60_percent_unchanged':True},indent=2))

"""Export approved Blender studies as a standalone, visual-only I3D asset.
Coordinates are relative to the existing curtainOpen pivots; no original nodes change.
"""
import bpy, math, ast, copy, json, subprocess, shutil
from pathlib import Path
from mathutils import Vector
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
source=(ROOT/'source/build_body.py').read_text()
designs=ast.literal_eval(source[source.index('DESIGNS = ')+10:source.index('\n\ndef mirrored')])
base=ET.parse(ROOT/'boxTruck.i3d').getroot()
root=ET.Element('i3D',name='gatheredCurtains',version='1.6')
ET.SubElement(root,'Asset')
files=copy.deepcopy(base.find('Files')); root.append(files)
materials=ET.SubElement(root,'Materials')
names=['curtainCloth','proEditionDecal','designKrone','designFSL','designGIANTS','strap','galvanized']
matids={}
for name in names:
    m=copy.deepcopy(next(m for m in base.find('Materials') if m.get('name')==name))
    materials.append(m); matids[name]=m.get('materialId')
lining=copy.deepcopy(materials[0]); lining.set('name','gatheredWhiteLining'); lining.set('materialId','9000')
lining.find('Texture').set('fileId','2')
lining.find('Normalmap').set('fileId','31')
lining.find("CustomParameter[@name='colorScale']").set('value','1 1 1')
materials.append(lining); matids['gatheredWhiteLining']='9000'
for f in files:
    if f.get('filename')=='$data/shaders/vehicleShader.xml': f.set('filename','shaders/curtainShapeShader.xml')
for m in materials:
    ET.SubElement(m,'CustomParameter',name='curtainShape',value='0 0 0 0')
shapes=ET.SubElement(root,'Shapes'); scene=ET.SubElement(root,'Scene')
nodeid=1; shapeid=1; stats=[]
def node(parent,tag,**attrs):
    global nodeid
    n=ET.SubElement(parent,tag,nodeId=str(nodeid),**{k:str(v) for k,v in attrs.items()}); nodeid+=1
    return n
def fmt(seq): return ' '.join(f'{v:.7g}' for v in seq)
def emit(parent,name,verts,normals,uvs,faces,material,shadow=True,rest=None):
    global shapeid
    mesh=ET.SubElement(shapes,'IndexedTriangleSet',name=name,shapeId=str(shapeid),isOptimized='false')
    vv=ET.SubElement(mesh,'Vertices',count=str(len(verts)),normal='true',tangent='true',uv0='true',uv1='true',uv2='true',uv3='true')
    assert rest is not None and len(rest)==len(verts)
    # Base positions span the full shut curtain for conservative culling bounds.
    # UV2/3 store gathered targets without changing either texture UV set.
    for index,(p,n,uv,rp) in enumerate(zip(verts,normals,uvs,rest)):
        ET.SubElement(vv,'v',p=fmt(rp),n=fmt(n),t0=fmt(uv),t1=fmt(uv),t2=fmt((p.x,p.y)),t3=fmt((p.z,-sign if name=='whiteInnerLining' or (name=='cloth' and index>=len(verts)//2) else sign)))
    tt=ET.SubElement(mesh,'Triangles',count=str(len(faces)))
    for f in faces: ET.SubElement(tt,'t',vi=' '.join(map(str,f)))
    subsets=ET.SubElement(mesh,'Subsets',count='1')
    ET.SubElement(subsets,'Subset',firstVertex='0',numVertices=str(len(verts)),firstIndex='0',numIndices=str(len(faces)*3))
    node(parent,'Shape',name=name,shapeId=shapeid,materialIds=matids[material],castsShadows=str(shadow).lower(),receiveShadows='true',clipDistance='100')
    shapeid+=1
    stats.append({'name':name,'vertices':len(verts),'triangles':len(faces)})
for version in range(1,4):
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/f'previews/gathered_distinct_v1/version_{version}/gathered_proposal.blend'))
    for side,sign in [('Left',1),('Right',-1)]:
        ob=bpy.data.objects['curtain'+side+'Gathered']; me=ob.data
        cols=len(me.vertices)//97-1; rows=96
        positions=[ob.matrix_world @ v.co for v in me.vertices]
        normals=[(ob.matrix_world.to_3x3() @ v.normal).normalized() for v in me.vertices]
        def sample(u,t):
            cu=max(0,min(cols,u*cols)); rt=max(0,min(rows,t*rows))
            c=min(cols-1,int(cu)); r=min(rows-1,int(rt)); fu=cu-c; ft=rt-r
            ids=[r*(cols+1)+c,r*(cols+1)+c+1,(r+1)*(cols+1)+c,(r+1)*(cols+1)+c+1]
            weights=[(1-fu)*(1-ft),fu*(1-ft),(1-fu)*ft,fu*ft]
            p=sum((positions[i]*w for i,w in zip(ids,weights)),Vector())
            n=sum((normals[i]*w for i,w in zip(ids,weights)),Vector()).normalized()
            # Blender world -> game curtainOpen-local (pivot z=-5.21).
            return Vector((p.x,p.z,-p.y+5.21)),Vector((n.x,n.z,-n.y))
        group=node(scene,'TransformGroup',name=f'gathered{side}{version}')
        # Cloth uses the full original material-space UVs, both sides separately.
        verts=[]; norms=[]; uvs=[]; faces=[]
        nc=cols//3; nr=32
        for inside in (False,True):
            offset=len(verts)
            for r in range(nr+1):
                for c in range(nc+1):
                    u,t=c/nc,r/nr; p,n=sample(u,t)
                    verts.append(p-n*.001 if inside else p); norms.append(-n if inside else n); uvs.append((u,t))
            for r in range(nr):
                for c in range(nc):
                    a=offset+r*(nc+1)+c
                    fs=[(a,a+1,a+nc+2),(a,a+nc+2,a+nc+1)]
                    faces.extend(tuple(reversed(f)) if ((sign<0)!=inside) else f for f in fs)
        outer_count=(nc+1)*(nr+1)
        outer_verts=verts[:outer_count]; outer_norms=norms[:outer_count]
        outer_faces=faces[:2*nc*nr]
        outer_coords=[(6.72*(1-c/nc if sign<0 else c/nc),1.53+2.53*r/nr) for r in range(nr+1) for c in range(nc+1)]
        rest=[Vector((sign*(1.296 if i<outer_count else 1.295),1.53+2.53*uv[1],6.72*(1-uv[0]))) for i,uv in enumerate(uvs)]
        emit(group,'cloth',verts,norms,uvs,faces,'curtainCloth',rest=rest)
        def sample_cloth(u,t):
            # Match the rendered cloth triangles, rather than the denser Blender
            # study, so attachment points cannot intersect between grid vertices.
            cu=u*nc; rt=t*nr
            c=min(nc-1,int(cu)); r=min(nr-1,int(rt)); fu=cu-c; ft=rt-r
            a=r*(nc+1)+c
            if fu>=ft:
                ids=(a,a+1,a+nc+2); weights=(1-fu,fu-ft,ft)
            else:
                ids=(a,a+nc+2,a+nc+1); weights=(1-ft,fu,ft-fu)
            p=sum((outer_verts[i]*w for i,w in zip(ids,weights)),Vector())
            n=sum((outer_norms[i]*w for i,w in zip(ids,weights)),Vector()).normalized()
            return p,n
        # Carry the original reinforcement, straps and buckles on the same
        # material-space surface as the cloth, including the skirt below it.
        for suffix, material in [('Band','strap'),('Straps','strap'),('Buckles','galvanized')]:
            hardware=bpy.data.objects['curtain'+side+suffix]
            mesh=hardware.data
            mesh.calc_loop_triangles()
            rest=[]; verts=[]; norms=[]; uvs=[]; faces=[]
            def clip_attachment(poly, coordinate, bound, greater):
                result=[]
                if not poly: return result
                previous=poly[-1]; prev_value=coordinate(previous[0])
                for current in poly:
                    curr_value=coordinate(current[0])
                    prev_in=prev_value>=bound-1e-10 if greater else prev_value<=bound+1e-10
                    curr_in=curr_value>=bound-1e-10 if greater else curr_value<=bound+1e-10
                    if prev_in!=curr_in:
                        fraction=(bound-prev_value)/(curr_value-prev_value)
                        result.append(tuple(a+(b-a)*fraction for a,b in zip(previous,current)))
                    if curr_in: result.append(current)
                    previous=current; prev_value=curr_value
                return result
            def attach_vertex(closed):
                u=max(0,min(1,1-closed.z/6.72))
                t=max(0,min(1,(closed.y-1.53)/2.53))
                surface,normal=sample_cloth(u,t)
                target=surface+normal*(sign*closed.x-1.296)
                target.y+=closed.y-(1.53+2.53*t)
                return target
            for triangle in mesh.loop_triangles:
                original=[]
                for loop_index in triangle.loops:
                    vertex=mesh.vertices[mesh.loops[loop_index].vertex_index]
                    world=hardware.matrix_world @ vertex.co
                    closed=Vector((world.x,world.z,-world.y+5.21))
                    uv=Vector(mesh.uv_layers.active.data[loop_index].uv) if mesh.uv_layers.active else Vector((0,0))
                    original.append((closed,uv))
                ymin=min(p.y for p,uv in original); ymax=max(p.y for p,uv in original)
                # Slice on every rendered cloth grid edge, then its diagonal.
                # This makes the long reinforcement strip follow the folds too.
                ycuts=sorted(set([ymin,ymax]+[1.53+2.53*r/nr for r in range(nr+1) if ymin<1.53+2.53*r/nr<ymax]))
                if len(ycuts)==1: ycuts.append(ymax)
                for ylo,yhi in zip(ycuts,ycuts[1:]):
                    row=clip_attachment(original,lambda p:p.y,ylo,True)
                    row=clip_attachment(row,lambda p:p.y,yhi,False)
                    if not row: continue
                    umin=max(0,min(1,min(1-p.z/6.72 for p,uv in row)))
                    umax=max(0,min(1,max(1-p.z/6.72 for p,uv in row)))
                    cmin=min(nc-1,int(umin*nc)); cmax=min(nc-1,int(umax*nc))
                    for c in range(cmin,cmax+1):
                        cell=clip_attachment(row,lambda p:1-p.z/6.72,c/nc,True)
                        cell=clip_attachment(cell,lambda p:1-p.z/6.72,(c+1)/nc,False)
                        polygons=[cell]
                        if 1.53<=ylo and yhi<=4.06:
                            r=min(nr-1,int(((ylo+yhi)/2-1.53)/2.53*nr))
                            diagonal=lambda p:(1-p.z/6.72)*nc-c-((p.y-1.53)/2.53*nr-r)
                            polygons=[clip_attachment(cell,diagonal,0,True),clip_attachment(cell,diagonal,0,False)]
                        for poly in polygons:
                            for j in range(1,len(poly)-1):
                                tri=[poly[0],poly[j],poly[j+1]]
                                if (tri[1][0]-tri[0][0]).cross(tri[2][0]-tri[0][0]).length<1e-10: continue
                                gathered=[attach_vertex(p) for p,uv in tri]
                                normal=(gathered[1]-gathered[0]).cross(gathered[2]-gathered[0]).normalized()
                                if normal.length<.5: normal=Vector((sign,0,0))
                                offset=len(verts)
                                rest.extend(p for p,uv in tri); verts.extend(gathered); norms.extend([normal]*3); uvs.extend(tuple(uv) for p,uv in tri)
                                faces.append((offset,offset+1,offset+2))
            emit(group,'curtain'+suffix,verts,norms,uvs,faces,material,rest=rest)
        # Continuous opaque white inner liner hides exterior-facing fold returns
        # when looking across the load bay. No colored texture is assigned here.
        verts=[]; norms=[]; uvs=[]; faces=[]
        for r in range(33):
            t=r/32
            row=[sample(c/128,t)[0] for c in range(129)]
            lo=min(p.z for p in row)-.008; hi=max(p.z for p in row)+.008
            yy=min(p.y for p in row)
            for c in range(17):
                u=c/16
                verts.append(Vector((sign*1.267,yy,hi+(lo-hi)*u)))
                norms.append(Vector((-sign,0,0))); uvs.append((u,t))
        for r in range(32):
            for c in range(16):
                a=r*17+c
                fs=[(a,a+1,a+18),(a,a+18,a+17)]
                faces.extend(tuple(reversed(f)) if sign>0 else f for f in fs)
        rest=[Vector((sign*1.267,1.53+2.53*t,6.72*(1-u))) for u,t in uvs]
        emit(group,'whiteInnerLining',verts,norms,uvs,faces,'gatheredWhiteLining',rest=rest)
        # Decals follow the cloth surface and face outward only.
        specs=[('ProEdition',6.07,1.247,[(.325,6.395,2.3445,3.5915,(0,0,6.07,1.247))],'proEditionDecal')]
        specs += [(name,tw,th,pieces,'design'+name) for name,(_,tw,th,pieces) in designs.items()]
        for name,tw,th,pieces,material in specs:
            rest=[]
            verts=[]; norms=[]; uvs=[]; faces=[]
            for layer,(s0,s1,y0,y1,rect) in enumerate(pieces):
                px0,py0,px1,py1=rect
                # Clip the actual cloth triangles in material space. Independent
                # decal tessellation can intersect the deep folds and break print.
                for face in outer_faces:
                    poly=[(outer_verts[i],outer_norms[i],*outer_coords[i]) for i in face]
                    for axis,bound,greater in [(2,s0,True),(2,s1,False),(3,y0,True),(3,y1,False)]:
                        clipped=[]
                        if not poly: break
                        previous=poly[-1]
                        for current in poly:
                            prev_in=previous[axis]>=bound if greater else previous[axis]<=bound
                            curr_in=current[axis]>=bound if greater else current[axis]<=bound
                            if prev_in!=curr_in:
                                f=(bound-previous[axis])/(current[axis]-previous[axis])
                                clipped.append(tuple(a+(b-a)*f for a,b in zip(previous,current)))
                            if curr_in: clipped.append(current)
                            previous=current
                        poly=clipped
                    if len(poly)<3: continue
                    offset=len(verts)
                    for p,n,s,y in poly:
                        n=n.normalized()
                        verts.append(p+n*(.002+layer*.0006)); norms.append(n)
                        rest.append(Vector((sign*(1.298+layer*.0006),y,6.72-s if sign>0 else s)))
                        a=(s-s0)/(s1-s0); b=(y-y0)/(y1-y0)
                        uvs.append(((px0+(px1-px0)*a)/tw,1-(py1+(py0-py1)*b)/th))
                    for j in range(1,len(poly)-1): faces.append((offset,offset+j,offset+j+1))
            emit(group,name,verts,norms,uvs,faces,material,False,rest=rest)
# Only retain file references actually used by these materials.
used={m.get('customShaderId') for m in materials}
used.update(n.get('fileId') for m in materials for n in m if n.get('fileId'))
for f in list(files):
    if f.get('fileId') not in used: files.remove(f)
ET.indent(root,space='  ')
ET.ElementTree(root).write(ROOT/'gatheredCurtains.i3d',encoding='iso-8859-1',xml_declaration=True)
(ROOT/'previews/gathered_integration/mesh_manifest.json').write_text(json.dumps(stats,indent=2))
print('EXPORTED',len(stats),'meshes',sum(s['triangles'] for s in stats),'triangles')
shutil.copy2(ROOT/'gatheredCurtains.i3d',ROOT/'previews/gathered_integration/gatheredCurtains_ascii.i3d')
converter=Path.home()/'AppData/Roaming/Blender Foundation/Blender/5.2/scripts/addons/io_export_i3d/util/i3dConverter.exe'
subprocess.run([str(converter),'-in',str(ROOT/'gatheredCurtains.i3d'),'-out',str(ROOT/'gatheredCurtains.i3d'),'-gamePath','G:/SteamLibrary/steamapps/common/Farming Simulator 25/'],check=True)
assert (ROOT/'gatheredCurtains.i3d.shapes').is_file()

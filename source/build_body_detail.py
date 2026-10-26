"""Blender: additive visual detail meshes; no physics or animation replacement.
blender -b -P source/build_body_detail.py -- <stage directory>
"""
import bpy, bmesh, sys, math, copy
from pathlib import Path
import xml.etree.ElementTree as ET
from mathutils import Vector

OUT = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
bpy.ops.wm.read_factory_settings(use_empty=True)
materials = {}
for i, name in enumerate(('detailAluminium', 'detailSteel', 'detailWebbing', 'detailSeal', 'detailCurtain')):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (.2 + .1*i, .3, .4, 1)
    m.use_nodes = True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = m.diffuse_color
    materials[name] = m

def g(x, y, z): return Vector((x, -z, y))

def mesh(): return bmesh.new()

def box(bm, x, y, z, sx, sy, sz, bevel=0):
    result = bmesh.ops.create_cube(bm, size=1)
    for v in result['verts']:
        v.co = Vector((v.co.x*sx, v.co.y*sz, v.co.z*sy))
    if bevel:
        edges = {e for v in result['verts'] for e in v.link_edges}
        bmesh.ops.bevel(bm, geom=list(edges), offset=bevel, segments=2, affect='EDGES')
        # All vertices added in this operation are still around the origin;
        # caller uses a separate temporary mesh for each beveled component.
    for v in result['verts']:
        if v.is_valid: v.co += g(x,y,z)

def part(dest, x,y,z, sx,sy,sz, bevel=.0008):
    bm = mesh()
    bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x*sx, v.co.y*sz, v.co.z*sy))
    if bevel: bmesh.ops.bevel(bm, geom=list(bm.edges), offset=min(bevel, min(sx,sy,sz)*.22), segments=2, affect='EDGES')
    for v in bm.verts: v.co += g(x,y,z)
    temp = bpy.data.meshes.new('temp'); bm.to_mesh(temp); bm.free()
    dest.from_mesh(temp); bpy.data.meshes.remove(temp)

def pin(dest, x,y,z, radius=.004, depth=.003, side=1):
    bm = mesh()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=radius, radius2=radius*.82, depth=depth)
    # Cylinder local Blender z -> game x (Blender x), screw axis across the body.
    for v in bm.verts:
        a,b,c = v.co; v.co = Vector((side*c, a,b)) + g(x,y,z)
    temp = bpy.data.meshes.new('pin'); bm.to_mesh(temp); bm.free()
    dest.from_mesh(temp); bpy.data.meshes.remove(temp)

def finish(bm, name, material):
    me = bpy.data.meshes.new(name)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    me.materials.append(materials[material])
    # Exporter needs UV0 for vehicleShader, even though detail maps use local metres.
    uv = me.uv_layers.new(name='uv0')
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (-co.y, co.z)
    ob['i3D_collision'] = False
    ob['i3D_castsShadows'] = True
    ob['i3D_clipDistance'] = 65
    print('DETAIL_MESH',name,len(me.polygons),flush=True)
    return ob

rail = mesh(); screws = mesh()
for side in (1,-1):
    # Fine chamfered extrusion edges and darker recessed track beneath top rail.
    for yy in (4.205, 4.073, 1.495):
        part(rail, side*1.313, yy, -1.88, .008,.010,6.68,.0015)
    for zz in [1.35 - i*.33 for i in range(20)]:
        for yy in (4.17,1.505):
            pin(screws,side*1.319,yy,zz,.004,.003,side)
    for zz in (1.48,-5.23):
        for yy in (1.85,2.25,2.65,3.05,3.45,3.85):
            pin(screws,side*1.30,yy,zz,.004,.003,side)
finish(rail,'bodyDetailStaticRails','detailAluminium')
finish(screws,'bodyDetailStaticFasteners','detailSteel')

for side,name in ((1,'Left'),(-1,'Right')):
    metal=mesh(); webbing=mesh()
    for i in range(20):
        z=1.51-.165-i*.33
        # Open rectangular buckle frame, pivot roller and chamfered release tongue.
        x=side*1.321
        for dz in (-.021,.021): part(metal,x,1.585,z+dz,.016,.073,.006,.001)
        for yy in (1.550,1.620): part(metal,x,yy,z,.016,.006,.048,.001)
        part(metal,side*1.333,1.582,z,.010,.041,.027,.0018)
        part(metal,side*1.338,1.562,z,.005,.006,.030,.001)
        # Short strap keeper and top anchor; the existing full strap is preserved.
        part(webbing,side*1.314,1.683,z,.006,.018,.049,.001)
        part(metal,side*1.313,1.782,z,.011,.012,.044,.001)
        pin(metal,side*1.322,1.782,z,.0033,.003,side)
        part(metal,side*1.275,1.468,z,.06,.008,.026,.001)
    finish(metal,'bodyDetailCurtain'+name+'Hardware','detailSteel')
    finish(webbing,'bodyDetailCurtain'+name+'Keepers','detailWebbing')
    # A real tessellated cloth surface: shallow inward drape keeps existing decals
    # clear, and preserves the silhouette and all pallet/collision clearances.
    cloth=mesh(); grids=[]
    nu,nv=224,64
    for inside in (False,True):
        grid=[]
        for j in range(nv+1):
            row=[]; yy=1.53+2.53*j/nv
            for i in range(nu+1):
                s=6.72*i/nu; zz=1.51-s
                fade=math.sin(math.pi*i/nu)**.4 * math.sin(math.pi*j/nv)**.4
                sag=(.0035*(1+math.sin(s*11+.3*yy)) + .006*(1+math.sin(s*49+.5*math.sin(yy*4)))*math.exp(-(4.06-yy)/.33))*fade
                xx=side*(1.296-sag-(.003 if inside else 0))
                row.append(cloth.verts.new(g(xx,yy,zz)))
            grid.append(row)
        for j in range(nv):
            for i in range(nu):
                verts=[grid[j][i],grid[j][i+1],grid[j+1][i+1],grid[j+1][i]]
                if (side<0) != inside: verts.reverse()
                cloth.faces.new(verts)
        grids.append(grid)
    ob=finish(cloth,'bodyDetailCurtain'+name+'Cloth','detailCurtain')
    for poly in ob.data.polygons:
        poly.use_smooth=True
        for li in poly.loop_indices:
            co=ob.data.vertices[ob.data.loops[li].vertex_index].co
            ob.data.uv_layers[0].data[li].uv=((1.51+co.y)/6.72,(co.z-1.53)/2.53)

# Two separate door seal meshes follow the existing door pivots after integration.
for side,name in ((1,'Left'),(-1,'Right')):
    seal=mesh()
    # Inside edge of frame and center seam; narrow enough to preserve banner seam.
    for x in (side*1.235,side*.013): part(seal,x,2.91,-5.365,.009,2.37,.006,.001)
    for yy in (1.73,4.09): part(seal,side*.625,yy,-5.365,1.22,.010,.006,.001)
    finish(seal,'bodyDetailDoor'+name+'Seals','detailSeal')

bpy.ops.wm.save_as_mainfile(filepath=str(OUT.parent/'body_detail.blend'))
import addon_utils
addon_utils.enable('io_export_i3d', default_set=False)
from io_export_i3d import i3d_export
from io_export_i3d.dcc import dccBlender as d
import io_export_i3d.dcc as pkg
d.isNodeVisible=lambda n:bpy.data.objects[n].visible_get()
pkg.isNodeVisible=d.isNodeVisible
d.UISetAttrBool('i3D_exportUseSoftwareFileName',False)
d.UISetAttrBool('i3D_binaryFiles',False)
d.UISetAttrString('i3D_exportFileLocation',str(OUT/'bodyDetail.i3d'))
i3d_export.I3DExportAll()

# Use the truck's already working shader definitions for the new materials.
base=ET.parse(OUT/'boxTruck.i3d').getroot()
tree=ET.parse(OUT/'bodyDetail.i3d'); root=tree.getroot()
files=root.find('Files')
if files is None:
    files=ET.Element('Files')
    root.insert(1,files)
for c in list(files): files.remove(c)
for f in base.find('Files'): files.append(copy.deepcopy(f))
matdefs={m.get('name'):m for m in base.find('Materials')}
mapping={'detailAluminium':'alu','detailSteel':'galvanized','detailWebbing':'curtainCloth','detailSeal':'strap','detailCurtain':'curtainCloth'}
for m in root.find('Materials'):
    nm,mid=m.get('name'),m.get('materialId')
    orig=matdefs[mapping[nm]]
    m.attrib.clear();m.attrib.update(orig.attrib);m.set('name',nm);m.set('materialId',mid)
    for c in list(m):m.remove(c)
    for c in orig:m.append(copy.deepcopy(c))
    if nm in ('detailWebbing','detailSeal'):
        m.find('Texture').set('fileId','2');m.find('Normalmap').set('fileId','31')
        m.find("CustomParameter[@name='colorScale']").set('value','0.018 0.020 0.023')
ET.indent(tree,space='  ')
tree.write(OUT/'bodyDetail.i3d',encoding='iso-8859-1',xml_declaration=True)
print('DETAIL_EXPORT_COMPLETE',flush=True)

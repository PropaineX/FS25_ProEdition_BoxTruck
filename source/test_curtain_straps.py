"""Verify each strap attachment matches the actual rendered curtain triangles."""
from pathlib import Path
import math, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
root=ET.parse(ROOT/'previews/gathered_integration/gatheredCurtains_ascii.i3d').getroot()
meshes={m.get('shapeId'):m for m in root.find('Shapes')}
def vector(v,key): return tuple(map(float,v.get(key).split()))
def target(v): return (*vector(v,'t2'),vector(v,'t3')[0])
def blend(values,weights): return tuple(sum(v[i]*w for v,w in zip(values,weights)) for i in range(3))
def normalize(v):
    length=math.sqrt(sum(x*x for x in v)); return tuple(x/length for x in v)
counts=0; originals={}
for group in root.find('Scene'):
    sign=1 if 'Left' in group.get('name') else -1
    cloth=meshes[group.find("Shape[@name='cloth']").get('shapeId')].find('Vertices')
    nc=len({vector(v,'t0')[0] for v in cloth})-1
    nr=len({vector(v,'t0')[1] for v in cloth})-1
    for name in ('curtainBand','curtainStraps','curtainBuckles'):
        vertices=meshes[group.find("Shape[@name='"+name+"']").get('shapeId')].find('Vertices')
        key=(sign,name)
        closed=[v.get('p') for v in vertices]
        positions=[vector(v,'p') for v in vertices]
        bounds=tuple((min(p[i] for p in positions),max(p[i] for p in positions)) for i in range(3))
        if key in originals:
            assert all(abs(a-b)<.00001 for aa,bb in zip(originals[key],bounds) for a,b in zip(aa,bb))
        originals[key]=bounds
        hardware=meshes[group.find("Shape[@name='"+name+"']").get('shapeId')]
        for triangle in hardware.find('Triangles'):
            positions=[vector(vertices[int(i)],'p') for i in triangle.get('vi').split()]
            assert max(p[2] for p in positions)-min(p[2] for p in positions)<=6.72/nc+.00001
            assert max(p[1] for p in positions)-min(p[1] for p in positions)<=2.53/nr+.00001
        for v in vertices:
            rest=vector(v,'p')
            u=max(0,min(1,1-rest[2]/6.72)); t=max(0,min(1,(rest[1]-1.53)/2.53))
            cu=u*nc;rt=t*nr;c=min(nc-1,int(cu));r=min(nr-1,int(rt));fu=cu-c;ft=rt-r;a=r*(nc+1)+c
            if fu>=ft: ids=(a,a+1,a+nc+2);weights=(1-fu,fu-ft,ft)
            else: ids=(a,a+nc+2,a+nc+1);weights=(1-ft,fu,ft-fu)
            position=blend([target(cloth[i]) for i in ids],weights)
            normal=normalize(blend([vector(cloth[i],'n') for i in ids],weights))
            distance=sign*rest[0]-1.296
            expected=[p+n*distance for p,n in zip(position,normal)]
            expected[1]+=rest[1]-(1.53+2.53*t)
            actual=target(v)
            assert max(abs(a-b) for a,b in zip(expected,actual))<0.00003,(group.get('name'),name,rest,expected,actual)
            for fraction in (0,.25,.5,.75,1):
                attached=[a+(b-a)*fraction for a,b in zip(rest,expected)]
                rendered=[a+(b-a)*fraction for a,b in zip(rest,actual)]
                assert max(abs(a-b) for a,b in zip(attached,rendered))<0.00003
            counts+=1
print(f'PASS: {counts:,} hardware vertices follow the rendered fabric throughout travel; closed hardware extents are preserved across all variants.')

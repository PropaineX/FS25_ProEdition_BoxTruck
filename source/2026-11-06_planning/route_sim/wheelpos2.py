import sys, math, xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
scene = root.find('Scene')
TAGS=('TransformGroup','Shape','Light','Camera','Dynamic')
def kids(n): return [c for c in n if c.tag in TAGS]
def rot(rx,ry,rz):
    rx,ry,rz=[math.radians(v) for v in (rx,ry,rz)]
    cx,sx,cy,sy,cz,sz=math.cos(rx),math.sin(rx),math.cos(ry),math.sin(ry),math.cos(rz),math.sin(rz)
    X=[[1,0,0],[0,cx,-sx],[0,sx,cx]];Y=[[cy,0,sy],[0,1,0],[-sy,0,cy]];Z=[[cz,-sz,0],[sz,cz,0],[0,0,1]]
    mm=lambda a,b:[[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return mm(mm(X,Y),Z)
def world(chain):
    R=[[1,0,0],[0,1,0],[0,0,1]];t=[0,0,0]
    for c in chain:
        tr=[float(v) for v in c.get('translation','0 0 0').split()]
        t=[t[i]+sum(R[i][k]*tr[k] for k in range(3)) for i in range(3)]
        r=[float(v) for v in c.get('rotation','0 0 0').split()]
        Rl=rot(*r); R=[[sum(R[i][k]*Rl[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return t
comps=kids(scene)
for spec in sys.argv[2:]:
    name,m=spec.split('=')
    ci,path=m.split('>')
    n=comps[int(ci)];chain=[n]
    for i in path.split('|'):
        n=kids(n)[int(i)];chain.append(n)
    print('%-26s %-28s'%(name,n.get('name')), ' '.join('%.3f'%v for v in world(chain)))

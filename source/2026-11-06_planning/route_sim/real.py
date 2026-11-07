import sys, os, json, math; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim
chain=json.load(open('chain.json')); ids=[c[0] for c in chain]; s=ids.index(33783)
pts=[(x,-z) for _,x,z in chain[s:]]                 # sim y = -world z (north up)
SHED=(981.6,986.6,1087.3,1102.2)
P=-1.425
VEH={
 'box now (ideal)':  dict(LF=3.059,DC=math.atan(3.059/4.38),F=4.53,R=-5.35,MA=45,ST=45/38,node=0.0,la=4.0,md=4.94),
 'box now (scrub)':  dict(LF=3.059-P,DC=math.atan(3.059/4.38),F=4.53-P,R=-5.35-P,MA=45,ST=45/38,node=-P,la=4.0,md=4.94),
 'box +steerNode':   dict(LF=3.059-P,DC=math.atan(3.059/4.38),F=4.53-P,R=-5.35-P,MA=45,ST=45/38,node=-0.74-P,la=7.6,md=5.68),
 'milk':             dict(LF=3.918,DC=math.atan(3.918/6.44),F=5.55+2.387,R=-5.95+2.387,MA=35,ST=35/25,node=0.0,la=7.84,md=5.75+2.387),
}
def outline(x,y,h,F,R,W=1.275,step=0.1):
    c,s=math.cos(h),math.sin(h); out=[]
    def Q(f,l,tag): out.append((x+f*c-l*s, y+f*s+l*c, tag))
    n=int((F-R)/step)
    for i in range(n+1):
        f=R+(F-R)*i/n; Q(f,W,'left side %.1f m from front'%(F-f)); Q(f,-W,'right side')
    m=int(2*W/step)
    for i in range(m+1):
        l=-W+2*W*i/m; Q(F,l,'front'); Q(R,l,'rear')
    return out
def dist(px,py):
    x0,x1,y0,y1=SHED; dx=max(x0-px,0,px-x1); dy=max(y0-py,0,py-y1)
    if dx==0 and dy==0: return -min(px-x0,x1-px,py-y0,y1-py)
    return math.hypot(dx,dy)
end=pts.index((979.54,1089.43)) if (979.54,1089.43) in pts else len(pts)-1
out={}
for name,v in VEH.items():
    sim.LF,sim.DC_MAX,sim.FRONT,sim.REAR,sim.MAXANG,sim.STEER_T=v['LF'],v['DC'],v['F'],v['R'],v['MA'],v['ST']
    sim.LENGTH=2*(v['md']+v['node'])
    (x0,y0),(x1,y1)=pts[0],pts[1]; h=math.atan2(y1-y0,x1-x0)
    # put the AI node on the first waypoint
    st=(x0-v['node']*math.cos(h), y0-v['node']*math.sin(h), h)
    tr=sim.run(v['node'],v['la'],pts[:end+3],v=6/3.6,start=st,every=2)
    best=(9e9,None,None)
    for k,(x,y,hh,tgt,nd) in enumerate(tr):
        if nd[1]<1089.43 and hh<-math.pi/4: break       # passed the marker heading south
        for px,py,tag in outline(x,y,hh,v['F'],v['R']):
            d=dist(px,py)
            if d<best[0]: best=(d,tag,(px,-py),k)
    print('%-18s closest to shed edge: %+.2f m  (%s at x %.2f z %.2f)'%(name,best[0],best[1],best[2][0],best[2][1]))
    out[name]=dict(v=v,tr=tr,best=best)
json.dump({'pts':pts,'shed':SHED,'res':{k:{'tr':o['tr'],'v':o['v'],'best':o['best']} for k,o in out.items()}},open('real.json','w'))

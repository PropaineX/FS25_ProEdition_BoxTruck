import math, json, sys
# Box truck geometry (game units, z forward). Pivot = steeringCenterNode z 0.
LF = 3.059            # front axle ahead of pivot
DC_MAX = math.atan(3.059/4.38)   # centre steer angle at full lock (R 4.38)
FRONT, REAR, HALFW = 4.53, -5.35, 1.275
MAXANG = 45.0         # vehicle.maxRotation in deg -> AD steeringAngleLimit
STEER_T = 45/38       # s from straight to full lock
LENGTH = 9.88

def route(r=6.0, sp=2.0):
    pts=[(0.0,y) for y in [ -30+i*sp for i in range(int(30/sp)) ]]
    n=max(2,int(round(r*math.pi/2/sp)))
    for i in range(n+1):
        a=math.pi-(math.pi/2)*i/n          # centre (r,0), from (0,0) heading N to (r,r) heading E
        pts.append((r+r*math.cos(a), r*math.sin(a)))
    pts+= [(r+sp*i,r) for i in range(1,int(30/sp))]
    return pts

def run(node_z, lookahead, pts, v=8/3.6, dt=0.01, start=None, every=5):
    min_dist=max(LENGTH/2-node_z,0.1)
    x,y,h=start if start else (0.0,-24.0,math.pi/2)
    steer=0.0; wi=0; out=[]; t=0
    def node():
        return x+node_z*math.cos(h), y+node_z*math.sin(h)
    while t<120:
        nx,ny=node()
        # waypoint reached (current or next, maxSkip 1)
        for k in (0,1):
            if wi+k<len(pts) and math.hypot(nx-pts[wi+k][0],ny-pts[wi+k][1])<min_dist:
                wi=wi+k+1; break
        if wi>=len(pts)-1: break
        # look-ahead target (ADDrivePathModule:getLookAheadTarget)
        cur=pts[wi]; d=math.hypot(nx-cur[0],ny-cur[1]); rem=lookahead-d; j=0; ahead=cur; dn=0
        while rem>dn:
            rem-=dn; j+=1
            if wi+j>=len(pts): break
            cur,ahead=ahead,pts[wi+j]; dn=math.hypot(ahead[0]-cur[0],ahead[1]-cur[1])
        tx,ty=cur
        if rem>0.1 and dn>0.1:
            L=min(rem,dn); tx+= (ahead[0]-cur[0])/dn*L; ty+=(ahead[1]-cur[1])/dn*L
        # driveInDirection: steer fraction = angle/limit
        ang=math.atan2(ty-ny,tx-nx)-h; ang=(ang+math.pi)%(2*math.pi)-math.pi
        target=max(-1,min(1,math.degrees(ang)/MAXANG))
        ds=dt/STEER_T; steer+=max(-ds,min(ds,target-steer))
        dc=steer*DC_MAX
        h+=v*math.tan(dc)/LF*dt; x+=v*math.cos(h)*dt; y+=v*math.sin(h)*dt
        if int(round(t/dt))%every==0: out.append((x,y,h,(tx,ty),node()))
        t+=dt
    return out

def corners(x,y,h):
    c,s=math.cos(h),math.sin(h)
    return [(x+f*c-l*s, y+f*s+l*c) for f,l in ((FRONT,HALFW),(FRONT,-HALFW),(REAR,-HALFW),(REAR,HALFW))]

if __name__=='__main__':
    pts=route()
    res={}
    for name,nz,la in (('before',0.0,4.0),('after',-0.74,7.6)):
        tr=run(nz,la,pts)
        ys=[max(p[1] for p in corners(*s[:3])) for s in tr]
        xs=[min(p[0] for p in corners(*s[:3])) for s in tr]
        fl=[corners(*s[:3])[0] for s in tr]
        print(name,'max y %.2f  min x %.2f   frontLeft max y %.2f'%(max(ys),min(xs),max(p[1] for p in fl)))
        res[name]=tr
    json.dump({'pts':pts,'res':res},open(sys.argv[1] if len(sys.argv)>1 else 'sim.json','w'))

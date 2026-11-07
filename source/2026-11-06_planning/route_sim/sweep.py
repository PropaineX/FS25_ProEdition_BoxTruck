import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import math, sim
def setv(lf,dcmax,front,rear,maxang,steer_t,length):
    sim.LF,sim.DC_MAX,sim.FRONT,sim.REAR,sim.MAXANG,sim.STEER_T,sim.LENGTH=lf,dcmax,front,rear,maxang,steer_t,length
BOX=(3.059,math.atan(3.059/4.38),4.53,-5.35,45,45/38,9.88)
# milk: pivot at rear axle 1 (z -2.387); body z relative to pivot
MILK=(3.918,math.atan(3.918/6.44),5.55+2.387,-5.95+2.387,35,35/25,11.5)
cases=[('box before',BOX,0.0,4.0),('box after',BOX,-0.74,7.6),('milk',MILK,0.0,7.84)]
for r in (4,5,6,8):
  for sp in (1.0,2.0,3.0):
    pts=sim.route(r,sp); line=[]
    for n,veh,nz,la in cases:
        setv(*veh)
        if n=='milk': sim.LENGTH=11.5
        # AD min_distance uses node z vs component 1 origin; milk node is 2.387 behind comp origin
        tr=sim.run(nz,la,pts) if n!='milk' else run_milk(pts) if False else None
        if n=='milk':
            # node = pivot (rear axle 1); comp origin is 2.387 ahead -> min_dist = 5.75+2.387
            sim.LENGTH=2*(5.75+2.387); tr=sim.run(0.0,la,pts)
        my=max(max(p[1] for p in sim.corners(*s[:3])) for s in tr)
        line.append('%s %.2f'%(n,my-r))
    print('r=%d sp=%.0f  overshoot past route line (m): '%(r,sp)+' | '.join(line))

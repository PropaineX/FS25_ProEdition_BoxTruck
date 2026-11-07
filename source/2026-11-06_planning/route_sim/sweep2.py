import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import math, sim
P=-1.425  # midpoint of the two FIXED rear axles (-0.74, -2.11): where a real truck pivots
def setv(lf,dcmax,front,rear,maxang,steer_t,length):
    sim.LF,sim.DC_MAX,sim.FRONT,sim.REAR,sim.MAXANG,sim.STEER_T,sim.LENGTH=lf,dcmax,front,rear,maxang,steer_t,length
# all bodies given relative to the pivot used for motion; node_z relative to pivot; LENGTH tuned so AD min_dist = len/2 - nodeZ(vs comp origin)
cases={
 # ideal game kinematics (pivot z0) - what the earlier run assumed
 'box ideal now'   :((3.059,math.atan(3.059/4.38),4.53,-5.35,45,45/38,9.88),0.0,4.0,4.94),
 # scrub model: wheels angled for pivot z0 but truck really pivots between fixed axles
 'box real now'    :((3.059-P,math.atan(3.059/4.38),4.53-P,-5.35-P,45,45/38,0),0.0-P,4.0,4.94),
 'box real +steerNode':((3.059-P,math.atan(3.059/4.38),4.53-P,-5.35-P,45,45/38,0),-0.74-P,7.6,4.94+0.74),
 # rotCenterNode moved to P: wheel angles now match the fixed axles
 'box centre moved':((3.059-P,math.atan((3.059-P)/5.37),4.53-P,-5.35-P,45,45/38,0),0.0,2*(3.059-P),4.94-P),
 'milk'            :((3.918,math.atan(3.918/6.44),5.55+2.387,-5.95+2.387,35,35/25,0),0.0,7.84,5.75+2.387),
}
for r in (4,6,8):
  for sp in (1.0,2.0):
    pts=sim.route(r,sp); out=[]
    for n,(veh,nz,la,md) in cases.items():
        setv(*veh); sim.LENGTH=2*(md+nz) if False else 2*md+2*nz*0  # placeholder
        # run() uses min_dist = LENGTH/2 - node_z -> set LENGTH so result = md
        sim.LENGTH=2*(md+nz)
        tr=sim.run(nz,la,pts)
        my=max(max(p[1] for p in sim.corners(*s[:3])) for s in tr)
        out.append('%s %.2f'%(n,my-r))
    print('r=%d sp=%.0f: '%(r,sp)+' | '.join(out))

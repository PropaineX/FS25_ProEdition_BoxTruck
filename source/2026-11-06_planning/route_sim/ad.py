import sys, re, math, json, xml.etree.ElementTree as ET
r=ET.parse(sys.argv[1]).getroot(); w=r.find('waypoints')
ids=[int(v) for v in w.find('id').text.split(',')]
X=[float(v) for v in w.find('x').text.split(',')]; Y=[float(v) for v in w.find('y').text.split(',')]; Z=[float(v) for v in w.find('z').text.split(',')]
OUT=[[int(a) for a in s.split(',') if a and a!='-1'] for s in w.find('out').text.split(';')]
INC=[[int(a) for a in s.split(',') if a and a!='-1'] for s in w.find('incoming').text.split(';')]
FL=[int(v) for v in w.find('flags').text.split(',')]
idx={i:k for k,i in enumerate(ids)}
mk=None
for m in r.iter():
    if m.find('name') is not None and m.find('name').text==sys.argv[2]:
        mk=m; break
mid=int(float(mk.find('id').text)); k=idx[mid]
print('marker',mid,'at x %.2f z %.2f'%(X[k],Z[k]))
# walk back along incoming, list branches
def show(i,depth,seen,path):
    if depth==0 or i in seen: return
    seen.add(i); k=idx[i]
    print('  '*0+'wp %d x %.2f z %.2f out %s in %s flag %d'%(i,X[k],Z[k],OUT[k],INC[k],FL[k]))
for i in range(1): pass
cur=mid; chain=[cur]
for step in range(40):
    inc=INC[idx[cur]]
    if not inc: break
    cur=inc[0]; chain.append(cur)
for i in reversed(chain):
    k=idx[i]; print('wp %6d x %9.2f z %9.2f  out %-22s in %-22s flag %d'%(i,X[k],Z[k],OUT[k],INC[k],FL[k]))
json.dump([(i,X[idx[i]],Z[idx[i]]) for i in reversed(chain)],open('chain.json','w'))

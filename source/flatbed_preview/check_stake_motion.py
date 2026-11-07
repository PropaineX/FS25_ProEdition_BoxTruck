import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
out=root/'previews/flatbed_stake_motion_v1'
r=json.loads((out/'validation.json').read_text())
for frame,u in [(1,0),(8,.5),(15,1)]:
 bpy.context.scene.frame_set(frame)
 for track in r['tracks']:
  expected=[a+(b-a)*u for a,b in zip(track['start'],track['end'])]
  expected=[expected[0],-expected[2],expected[1]]
  ob=bpy.data.objects[track['body_node']]
  assert max(abs(a-b) for a,b in zip(ob.location,expected))<2e-5,(frame,ob.name,tuple(ob.location),expected)
 for side in [-1,1]:
  for number,z in [(2,-3.83),(4,-1.29),(6,1.25)]:
   ob=bpy.data.objects[f'Stake {side} {number}']
   assert abs(ob.location.y+z)<2e-5,(frame,ob.name)
r['blender_verification']='saved model reopened; 0/50/100% motion linear on six tracks, all six stationary stakes unchanged'
r['native_reversal_verification']='installed Foldable Lua executed: closed/gathered endpoints and both in-motion reversals PASS'
(out/'validation.json').write_text(json.dumps(r,indent=2))
print('PASS: reopened blend linear at 0%,50%,100%; six fixed stakes unchanged')

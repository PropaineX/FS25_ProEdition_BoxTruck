"""Adapt the user's installed Fliegl XML folding logic to our own stake nodes.

Writes an integration fragment and samples its actual linear animation parts for
an Editor review. Does not install or register an unfinished flatbed vehicle.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile,copy,json,hashlib

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'source/flatbed_runtime';OUT.mkdir(exist_ok=True)
PRE=ROOT/'previews/flatbed_stake_motion_v1';PRE.mkdir(exist_ok=True)
donor=ROOT.parent.parent/'mods/FS25_FlieglTimberRunnerAutoload.zip'
with zipfile.ZipFile(donor) as z:
    raw=z.read('timberRunner15.xml');reference=ET.fromstring(raw)
    second=ET.fromstring(z.read('timberRunner20.xml'))
fold=copy.deepcopy(reference.find('foldable'))
foldparts=fold.find('.//foldingParts')
foldparts.set('posDirectionText','$l10n_action_flatbedGatherStakes')
foldparts.set('negDirectionText','$l10n_action_flatbedSpreadStakes')
foldparts.set('startAnimTime','0')
foldparts.set('foldInputButton','IMPLEMENT_EXTRA2')
assert foldparts.find('foldingPart').get('animationName')=='additionalForks'
assert second.find('.//animation[@name="additionalForks"]/part').get('endTime')=='0.7'
root=ET.Element('vehicle')
root.append(ET.Comment('Integration fragment: use native Foldable + AnimatedVehicle. Paths are resolved against our body asset during integration.'))
root.append(fold)
animations=ET.SubElement(root,'animations')
anim=ET.SubElement(animations,'animation',name='additionalForks')
closed=[-5.10,-3.83,-2.56,-1.29,-.02,1.25]
paired=[-3.97,-3.83,-1.43,-1.29,1.11,1.25]
tracks=[]
for side,sgn in [('Left',-1),('Right',1)]:
    for number in [1,3,5]:
        name=f'flatbedStake{side}{number}'
        start=[sgn*1.23,1.62,closed[number-1]]
        end=[sgn*1.23,1.62,paired[number-1]]
        # Same native linear part and timing as Fliegl additionalForks.
        part=copy.deepcopy(reference.find('.//animation[@name="additionalForks"]/part'))
        part.set('node',name);part.set('startTrans',' '.join(map(str,start)));part.set('endTrans',' '.join(map(str,end)))
        anim.append(part)
        tracks.append({'mapping':name,'body_node':f'Stake {sgn} {number}','start':start,'end':end,'duration':float(part.get('endTime'))})
for sound in reference.findall('.//animation[@name="additionalForks"]/sound'):
    sound=copy.deepcopy(sound);sound.set('linkNode','flatbedStakeLeft3');anim.append(sound)
ET.indent(root)
ET.ElementTree(root).write(OUT/'stake_folding.xml',encoding='utf-8',xml_declaration=True)
# Node-name contract avoids assuming the body insertion index in the future truck I3D.
body=ET.parse(ROOT/'previews/flatbed_fitted_v1/flatbedPreview.i3d').getroot().find('Scene')
def walk(node,path):
    yield node,path
    for i,child in enumerate(node):yield from walk(child,path+'|'+str(i))
nodes={}
for i,node in enumerate(body):
    for n,path in walk(node,f'{i}>'):
        nodes[n.get('name')]=(n,path)
contract={}
for track in tracks:
    node,path=nodes[track['body_node']]
    assert [float(n) for n in node.get('translation').split()]==track['start']
    contract[track['mapping']]={'body_node':track['body_node'],'body_local_path':path.replace('>|','>'),'start':track['start'],'end':track['end']}
assert len(tracks)==6 and all(t['duration']==.7 for t in tracks)
assert all(abs(t['end'][2]-t['start'][2]-1.13)<1e-8 for t in tracks)
(OUT/'stake_node_contract.json').write_text(json.dumps(contract,indent=2))
# Bake identical channels into Blender later; preview Lua samples this definition.
for frame in range(15):
    u=frame/14
    lines=['local function find(n,name) if getName(n)==name then return n end for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name);if r then return r end end end']
    for track in tracks:
        xyz=[a+(b-a)*u for a,b in zip(track['start'],track['end'])]
        lines.append(f'local n=find(getRootNode(),"{track["body_node"]}"); assert(n,"stake missing"); setTranslation(n,{xyz[0]:.8f},{xyz[1]:.8f},{xyz[2]:.8f})')
    (PRE/f'frame_{frame:02d}.lua').write_text('\n'.join(lines))
report={'donor':donor.name,'donor_member':'timberRunner15.xml','also_verified':'timberRunner20.xml',
 'donor_member_sha256':hashlib.sha256(raw).hexdigest(),'native_system':'Foldable + AnimatedVehicle',
 'input_action':'IMPLEMENT_EXTRA2','duration_seconds':.7,'moving_stakes_each_side':[1,3,5],
 'travel_m':1.13,'tracks':tracks,'integration':'fragment and node contract; complete flatbed vehicle not registered',
 'gameplay':'UNTESTED'}
(PRE/'validation.json').write_text(json.dumps(report,indent=2))
print('PASS: copied native Foldable setup, six resolved stake channels, 0.7s linear travel, unchanged 1.13m travel on both sides')

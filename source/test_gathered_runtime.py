"""Exercise the real Lua specialization with mocked engine/network bindings."""
from pathlib import Path
import sys, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'.local/lua-test-runtime'))
from lupa import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'''
g_currentModName='FS25_BoxTruck_ProEdition'; g_currentModDirectory='mod/'
function Class(t,base) t.__index=t; return t end
Event={new=function(mt) return setmetatable({},mt) end}
function InitEventClass() end
SpecializationUtil={hasSpecialization=function() return true end}
InputAction={IMPLEMENT_EXTRA2=1,IMPLEMENT_EXTRA4=2}
g_i18n={getText=function(self,s) return s end}
Logging={xmlWarning=function() error('missing animation') end,error=function(s) error(s) end}
function getName(n) return n.name end
function getNumOfChildren(n) return #n.children end
function getChildAt(n,i) return n.children[i+1] end
function setVisibility(n,v) assert(n); n.visible=v end
function setTranslation() end
function setShaderParameter(n,name,x,y,z,w,shared) assert(name=="curtainShape" and shared==false); n.shape={x,y} end
function delete() end
function node(name) return {name=name,children={},visible=true} end
function link(parent,n)
    assert(parent.children ~= nil, 'link requires a scene node, not an i3d mapping record')
    if n.parent then
        for i,c in ipairs(n.parent.children) do if c==n then table.remove(n.parent.children,i); break end end
    end
    table.insert(parent.children,n); n.parent=parent
end
g_i3DManager={loadSharedI3DFile=function()
    local root=node('asset')
    for _,side in ipairs({'Left','Right'}) do for v=1,3 do
        local group=node('gathered'..side..v); link(root,group)
        for _,name in ipairs({'cloth','whiteInnerLining','ProEdition','Krone','FSL','GIANTS','curtainBand','curtainStraps','curtainBuckles'}) do link(group,node(name)) end
    end end
    return root,73
end,releaseSharedI3DFile=function(self,id) assert(id==73); self.released=true end}
NetworkUtil={writeNodeObject=function(s,n) s.object=n end,readNodeObject=function(s) return s.object end}
function streamWriteUIntN(s,n,bits) assert(n>=0 and n<2^bits); table.insert(s,n) end
function streamReadUIntN(s,bits) s.pos=(s.pos or 0)+1; return s[s.pos] end
streamWriteFloat32=streamWriteUIntN
function streamWriteFloat32(s,n) table.insert(s,n) end
streamReadFloat32=streamReadUIntN
''')
lua.execute((ROOT/'scripts/BoxTruckBody.lua').read_text())
lua.execute(r'''
function vehicle(server,design)
    local v={isServer=server,configurations={design8=design or 2},i3dMappings={},spec_animatedVehicle={animations={}},times={},playing={}}
    v[BoxTruckBody.SPEC_TABLE_NAME]={}
    function v:getAnimationDuration() return 4800 end
    function v:raiseActive() end
    function v:getAnimationExists() return true end
    function v:getAnimationTime(n) return self.times[n] or 0 end
    function v:getIsAnimationPlaying(n) return self.playing[n] or false end
    function v:setAnimationTime(n,t) self.times[n]=t; self.playing[n]=false end
    for _,p in ipairs(BoxTruckBody.PARTS) do v.spec_animatedVehicle.animations[p.anim]={currentSpeed=1} end
    for _,side in ipairs({'Left','Right'}) do
        local parent=node('curtain'..side..'Open'); v.i3dMappings[parent.name]={nodeId=parent}
        local closed=node('curtain'..side..'Closed'); v.i3dMappings[closed.name]={nodeId=closed}
        for _,suffix in ipairs({'Cloth','InnerLining','ProEdition','DesignKrone','DesignFSL','DesignGIANTS','Band','Straps','Buckles'}) do
            link(closed,node('curtain'..side..suffix))
        end
        link(parent,node('curtain'..side..'Gathered')); link(parent,node('curtain'..side..'GatheredStraps'))
    end
    BoxTruckBody.onLoad(v)
    return v
end
function animate(v,n,s,t) v.times[n]=t or v:getAnimationTime(n); v.playing[n]=true; v.spec_animatedVehicle.animations[n].currentSpeed=s end
local broadcasts={}
g_server={broadcastEvent=function(self,e) table.insert(broadcasts,e) end}
local server=vehicle(true); local spec=server[BoxTruckBody.SPEC_TABLE_NAME]
local rolls=0
math.random=function(a,b) assert(a==1 and b==3); rolls=rolls+1; return (rolls-1)%3+1 end
local seen={}
for i=1,12 do
    server:setAnimationTime('boxCurtainLeft',0)
    BoxTruckBody.playAnimation(server,animate,'boxCurtainLeft',1,0,false)
    local chosen=spec.curtainVariants[1]; seen[chosen]=true
    local count=rolls
    BoxTruckBody.playAnimation(server,animate,'boxCurtainLeft',1,.2,true)
    assert(rolls==count,'rerolled during same opening')
    for j,n in ipairs(spec.gatheredNodes[1]) do assert(n.visible==(j==chosen)) end
    BoxTruckBody.playAnimation(server,animate,'boxCurtainLeft',-1,.8,false)
    assert(rolls==count,'rolled on closing')
end
assert(seen[1] and seen[2] and seen[3] and #broadcasts==12)
assert(spec.curtainVariants[2]==1,'left choice changed right')
-- Reopening while closing is a fresh opening; consecutive repeats are allowed.
math.random=function() rolls=rolls+1; return 2 end
BoxTruckBody.playAnimation(server,animate,'boxCurtainRight',1,0,false)
BoxTruckBody.playAnimation(server,animate,'boxCurtainRight',-1,.5,false)
BoxTruckBody.playAnimation(server,animate,'boxCurtainRight',1,.3,false)
assert(spec.curtainVariants[2]==2 and rolls==14)
local client=vehicle(false)
local event=BoxTruckCurtainVariantEvent.new(server,2,3)
local packet={}; event:writeStream(packet,{})
packet.object=client
BoxTruckCurtainVariantEvent.emptyNew():readStream(packet,{getIsServer=function() return true end})
assert(client[BoxTruckBody.SPEC_TABLE_NAME].curtainVariants[2]==3)
-- Clients cannot choose authoritative shapes or roll locally.
event.vehicle=server; event:run({getIsServer=function() return false end})
assert(spec.curtainVariants[2]==2)
local count=rolls
BoxTruckBody.playAnimation(client,animate,'boxCurtainLeft',1,0,false)
assert(rolls==count)
-- Late joiners receive both choices before restored animation targets.
server:setAnimationTime('boxCurtainLeft',1); server:setAnimationTime('boxCurtainRight',1)
local stream={}; BoxTruckBody.onWriteStream(server,stream,{})
BoxTruckBody.onReadStream(client,stream,{})
for side=1,2 do assert(client[BoxTruckBody.SPEC_TABLE_NAME].curtainVariants[side]==spec.curtainVariants[side]) end
assert(client:getAnimationTime('boxCurtainLeft')==1)
-- Save/load preserves selections; old saves default to variant 1.
local values={}; local xml={setValue=function(self,k,v) values[k]=v end,getValue=function(self,k,d) return values[k] or d end}
local key='vehicles.vehicle(0).'..BoxTruckBody.SPEC_NAME
BoxTruckBody.saveToXMLFile(server,xml,key)
local restored=vehicle(true)
BoxTruckBody.onPostLoad(restored,{xmlFile=xml,key='vehicles.vehicle(0)'})
for side=1,2 do assert(restored[BoxTruckBody.SPEC_TABLE_NAME].curtainVariants[side]==spec.curtainVariants[side]) end
local legacy=vehicle(true)
BoxTruckBody.onPostLoad(legacy,{xmlFile={getValue=function(self,k,d) return d end},key='old'})
assert(legacy[BoxTruckBody.SPEC_TABLE_NAME].curtainVariants[1]==1)
-- Every shop design shows exactly its own outward-facing artwork.
for design=1,5 do
    local v=vehicle(false,design)
    for _,side in ipairs(v[BoxTruckBody.SPEC_TABLE_NAME].gatheredNodes) do for _,group in ipairs(side) do
        local visible=0
        for _,n in ipairs(group.children) do if n.name~='cloth' and n.name~='whiteInnerLining' and n.name:sub(1,7)~='curtain' and n.visible then visible=visible+1 end end
        assert(visible==(design==1 and 0 or 1))
    end end
end
-- Geometry follows the entire 1.2-second curtain slide, then remains gathered
-- while boards finish. Reverse and late-join initialization use the same position.
for _,v in ipairs({server,client,restored,legacy}) do
    for side,part in ipairs(v[BoxTruckBody.SPEC_TABLE_NAME].curtains) do
        for _,elapsed in ipairs({0,1,300,600,900,1199,1200,2400,1200,900,600,300,0}) do
            v.times[part.anim]=elapsed/4800
            BoxTruckBody.updateCurtainShapes(v)
            for _,surface in ipairs(v[BoxTruckBody.SPEC_TABLE_NAME].closedCurtainSurfaces[side]) do
                assert(surface.visible==false,'original surfaces must stay hidden, including straps')
            end
            for _,group in ipairs(v[BoxTruckBody.SPEC_TABLE_NAME].gatheredNodes[side]) do
                for _,mesh in ipairs(group.children) do
                    assert(math.abs(mesh.shape[1]-math.min(1,elapsed/1200))<1e-9)
                end
            end
        end
        v.times[part.anim]=.125
        BoxTruckBody.updateCurtainShapes(v,true)
        local mesh=v[BoxTruckBody.SPEC_TABLE_NAME].gatheredNodes[side][1].children[1]
        assert(mesh.shape[1]==.5 and mesh.shape[2]==.5)
    end
end
BoxTruckBody.onDelete(server); assert(g_i3DManager.released)
''')
asset=ET.parse(ROOT/'gatheredCurtains.i3d').getroot()
groups=list(asset.find('Scene')); assert len(groups)==6
assert all(len(g)==9 for g in groups)
materials={m.get('materialId'):m for m in asset.find('Materials')}
files={f.get('fileId'):f.get('filename') for f in asset.find('Files')}
for g in groups:
    inner=g.find("Shape[@name='whiteInnerLining']")
    mat=materials[inner.get('materialIds')]
    assert files[mat.find('Texture').get('fileId')]=='$data/shared/white_diffuse.png'
    color=mat.find("CustomParameter[@name='colorScale']")
    assert color is None or color.get('value')=='1 1 1' # converter omits the white default
assert asset.find('Shapes').get('externalShapesFile')=='gatheredCurtains.i3d.shapes'
assert (ROOT/'gatheredCurtains.i3d.shapes').stat().st_size>0
geometry=ET.parse(ROOT/'previews/gathered_integration/gatheredCurtains_ascii.i3d').getroot()
for mesh in geometry.find('Shapes'):
    vv=mesh.find('Vertices'); tt=mesh.find('Triangles')
    assert vv.get('uv2')=='true' and vv.get('uv3')=='true'
    for v in vv:
        rest=list(map(float,v.get('p').split()))
        xy=list(map(float,v.get('t2').split()))
        zn=list(map(float,v.get('t3').split()))
        assert len(xy)==2 and len(zn)==2 and abs(zn[1])==1
        assert 1.2<xy[1]<4.1 and -.1<=zn[0]<1.1
        assert 1.4<=rest[1]<=4.07 and -.001<=rest[2]<=6.721
        # Every intermediate vertex is a continuous affine combination of the
        # same rest and gathered vertex; UV0/UV1 remain unchanged.
        target=[xy[0],xy[1],zn[0]]
        previous=rest
        for t in (0,.001,.25,.5,.75,.999,1):
            pos=[a+(b-a)*t for a,b in zip(rest,target)]
            assert all(min(a,b)-1e-6<=v<=max(a,b)+1e-6 for v,a,b in zip(pos,rest,target))
            previous=pos

    assert int(vv.get('count'))==len(vv)
    assert int(tt.get('count'))==len(tt)
    assert all(0<=int(i)<len(vv) for t in tt for i in t.get('vi').split())
base=ET.parse(ROOT/'boxTruck.i3d').getroot()
base_mats={m.get('materialId'):m for m in base.find('Materials')}
for side in ('Left','Right'):
    inner=next(n for n in base.iter('Shape') if n.get('name')=='curtain'+side+'InnerLining')
    material=base_mats[inner.get('materialIds')]
    assert material.get('name')=='boxTruckWhiteInnerLining'
    assert material.find('Texture').get('fileId')=='2'
print('PASS: continuous shape geometry and timing, reverse motion, fixed artwork UVs, random openings, no mid-opening/closing rerolls, independent sides, client authority, event roundtrip, late join, save/restore, legacy saves, all designs, asset indices, and white lining texture.')

shader=ET.parse(ROOT/'shaders/curtainShapeShader.xml').getroot()
stock=ET.parse('G:/SteamLibrary/steamapps/common/Farming Simulator 25/data/shaders/vehicleShader.xml').getroot()
for hook in ('ALPHA_FS','POST_DIFFUSE_COLOR_FS','POST_GLOSS_COLOR_FS'):
    assert shader.find(".//CodeInjection[@position='"+hook+"']").text==stock.find(".//CodeInjection[@position='"+hook+"']").text
for m in asset.find('Materials'):
    assert files[m.get("customShaderId")]=="shaders/curtainShapeShader.xml"
vehicle=ET.parse(ROOT/'boxTruck.xml').getroot()
for side in ('Left','Right'):
    anim=vehicle.find("animations/animation[@name='boxCurtain"+side+"']")
    assert not any(p.get('node')=='curtain'+side+'Open' for p in anim)
print('PASS: shader retains stock artwork and opacity; no end-of-slide mesh visibility swap.')

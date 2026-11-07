"""Exercise actual FlatbedBody Lua state/event logic without running the game."""
from pathlib import Path
import sys,zipfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'.local/lua-test-runtime'))
from lupa import LuaRuntime
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('''
g_currentModName='FS25_BoxTruck_ProEdition'
Event={new=function(mt)return setmetatable({},mt)end}
function Class(c,p)return {__index=c}end
function InitEventClass(...)end
AnimatedVehicle={};XMLValueType={BOOL=1};InputAction={PROPAINEX_FLATBED_TAILGATE=42};GS_PRIO_NORMAL=1
Vehicle={xmlSchemaSavegame={register=function(...)end}}
SpecializationUtil={hasSpecialization=function(...)return true end,registerFunction=function(...)end,registerEventListener=function(...)end}
g_i18n={getText=function(self,key,context)return key end}
g_inputBinding={setActionEventText=function(self,id,text)self.text=text end,setActionEventTextPriority=function(...)end}
streams={}
local function w(id,v)streams[id]=streams[id]or{};table.insert(streams[id],v)end
local function r(id)return table.remove(streams[id],1)end
streamWriteBool=w;streamWriteFloat32=w;streamReadBool=r;streamReadFloat32=r
NetworkUtil={writeNodeObject=w,readNodeObject=r}
g_server={events={},broadcastEvent=function(self,event,...)table.insert(self.events,event)end}
local conn={requests={},sendEvent=function(self,event)table.insert(self.requests,event)end}
g_client={getServerConnection=function()return conn end};CLIENT_CONN=conn
FROM_SERVER={getIsServer=function()return true end};FROM_CLIENT={getIsServer=function()return false end}
function newVehicle(server,side)
 local v={isServer=server,isClient=true,configurations={folding=side or 1},time=0,playing=false,actions={}}
 function v:getAnimationExists(name)return name=='flatbedTailgate'end
 function v:getAnimationTime(name)return self.time end
 function v:setAnimationTime(name,time,...)self.time=time;self.playing=false end
 function v:getIsAnimationPlaying(name)return self.playing end
 function v:playAnimation(name,speed,time,noEvent)assert(noEvent==true);self.time=time;self.speed=speed;self.playing=true;self.plays=(self.plays or 0)+1 end
 function v:clearActionEventsTable(t)for k in pairs(t)do t[k]=nil end;self.actions={}end
 function v:addActionEvent(t,action,...)table.insert(self.actions,action);return true,100 end
 function v:setFlatbedTailgate(...)return FlatbedBody.setFlatbedTailgate(self,...)end
 return v
end
function xmlMemory(values)
 return {values=values or {},getValue=function(self,key,default)local v=self.values[key];if v==nil then return default end;return v end,
 setValue=function(self,key,v)self.values[key]=v end}
end
''')
lua.execute((ROOT/'scripts/FlatbedBody.lua').read_text(encoding='utf-8'))
lua.execute('''
-- 1.4.0.1: the tailgate moves with the side walls on X (native Foldable); the script binds no keys.
assert(FlatbedBody.onRegisterActionEvents==nil and FlatbedBody.setFlatbedTailgate==nil and FlatbedTailgateEvent==nil)
-- UAL: optional; fallback only on absent config group, preserving every option.
g_modsDirectory='C:/mods/'
local ual={ALL='ALL',VEHICLE_CONFIGURATIONS={},OPTIONS_DEFAULTS={{id='isCurtainTrailer',default=false},{id='autoCollectionMode',default=false}},LOADING_AREA_DEFAULTS={{id='height',default=1}}}
local v={configFileName='C:/mods/FS25_BoxTruck_ProEdition/flatbedTruck.xml',specializations={ual},specializationNames={'FS25_UniversalAutoload.universalAutoload'}}
FlatbedBody.onPreLoad(v)
local group=ual.VEHICLE_CONFIGURATIONS['FS25_BoxTruck_ProEdition/flatbedTruck.xml'];assert(group and group.ALL)
assert(group.ALL.loadArea[1].offset[2]==1.625 and group.ALL.loadArea[1].width==2.38)
assert(group.ALL.isCurtainTrailer==false and group.ALL.autoCollectionMode==false)
FlatbedBody.onPreLoad(v);assert(ual.VEHICLE_CONFIGURATIONS['FS25_BoxTruck_ProEdition/flatbedTruck.xml']==group)
local custom={myChoice={autoloadDisabled=true,loadArea={{width=1}}}}
ual.VEHICLE_CONFIGURATIONS['FS25_BoxTruck_ProEdition/flatbedTruck.xml']=custom
FlatbedBody.onPreLoad(v);assert(ual.VEHICLE_CONFIGURATIONS['FS25_BoxTruck_ProEdition/flatbedTruck.xml']==custom)
assert(custom.myChoice.loadArea[1].width==1 and custom.myChoice.autoloadDisabled)
FlatbedBody.onPreLoad({});assert(ual.OPTIONS_DEFAULTS[1].default==false)
''')
print('PASS no separate tailgate key: script registers no actions or events')
print('PASS UAL: optional dependency, exact default area, default option preservation, repeated load and custom/disabled config preservation')
with zipfile.ZipFile(ROOT.parent.parent/'debugger/gameSource.zip') as z:
 lua.execute(z.read('dataS/scripts/vehicles/specializations/Foldable.lua').decode())
for time,moving,direction in [(0,0,1),(1,0,-1),(.3,1,-1),(.7,-1,1)]:
 vehicle=lua.table_from({'spec_foldable':lua.table_from({'foldAnimTime':time,'foldMoveDirection':moving,'moveToMiddle':False})})
 assert lua.globals().Foldable.getToggledFoldDirection(vehicle)==direction
print('PASS installed native Foldable endpoint toggles and in-motion reversals')

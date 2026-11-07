local function find(n,name)
 if getName(n)==name then return n end
 for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name); if r then return r end end
end
local old=find(getRootNode(),'Rear underrun beam')
assert(old,'Original underrun beam not found')
local comp=find(getRootNode(),'fh16_main_component1')
local tube=loadI3DFile('C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/FS25_BoxTruck_ProEdition/previews/flatbed_round_underrun_v1/roundTube.i3d',false,false,false)
assert(tube~=0,'Tube asset not loaded')
link(comp,tube); setVisibility(old,false)
print('[FLATBED_TUBE] round tube fitted; old rectangular beam hidden')
